<script setup lang="ts">
import {
  ref,
  watch,
  onMounted,
  onBeforeUnmount,
  computed,
  nextTick,
} from "vue";
import { EditorView, keymap } from "@codemirror/view";
import { EditorState } from "@codemirror/state";
import { markdown, markdownLanguage } from "@codemirror/lang-markdown";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { marked } from "marked";
import DOMPurify from "dompurify";

// Props (modelValue optionnel avec valeur par défaut)
const props = defineProps<{
  modelValue?: string;
  disabled?: boolean;
}>();

// Emits
const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
  (e: "input"): void;
  (e: "openIaPanel"): void;
}>();

// State
const editorContainer = ref<HTMLElement | null>(null);
const editorView = ref<EditorView | null>(null);
const internalValue = ref(props.modelValue || "");

// ── Disposition : trois modes, et non un aperçu qu'on allume ou qu'on éteint
//
// Le bouton « Aperçu » basculait un booléen : soit l'éditeur seul, soit deux
// panneaux côte à côte. Relire un document long dans une demi-colonne est
// inconfortable, et rien ne permettait de donner toute la largeur au rendu.
// Trois modes explicites remplacent le va-et-vient : écrire, partagé, lire.
type ModeAffichage = "ecrire" | "partage" | "apercu";

const MODES: { valeur: ModeAffichage; libelle: string; titre: string }[] = [
  { valeur: "ecrire", libelle: "Écrire", titre: "Éditeur seul" },
  { valeur: "partage", libelle: "Partagé", titre: "Éditeur et aperçu" },
  { valeur: "apercu", libelle: "Lire", titre: "Aperçu seul" },
];

const mode = ref<ModeAffichage>("partage");

// ── Le mode partagé n'a pas cours sur un téléphone ──────────────────────────
//
// Mesuré sur un écran de 390 px : la barre d'outils s'enroule sur trois lignes
// et occupe 178 px des 465 px disponibles. Partager le reste en deux laisse
// 111 px pour écrire, sous une colonne de lecture de 272 px — ni l'un ni
// l'autre n'est utilisable. En dessous du point de rupture, le mode partagé se
// comporte donc comme « Écrire », et son bouton est retiré : mieux vaut ne pas
// proposer une disposition qu'on ne peut pas tenir.
const PARTAGE_MIN = "(min-width: 768px)"; // md de Tailwind
const estLarge = ref(true);
let mediaPartage: MediaQueryList | null = null;

function suivreLargeur(evenement: MediaQueryListEvent | MediaQueryList) {
  estLarge.value = evenement.matches;
}

/**
 * Le mode réellement appliqué, qui peut différer du mode choisi : sur petit
 * écran, « partagé » retombe sur l'éditeur seul.
 */
const modeEffectif = computed<ModeAffichage>(() =>
  mode.value === "partage" && !estLarge.value ? "ecrire" : mode.value,
);

const afficheEditeur = computed(() => modeEffectif.value !== "apercu");
const afficheApercu = computed(() => modeEffectif.value !== "ecrire");
const modesVisibles = computed(() =>
  estLarge.value ? MODES : MODES.filter((m) => m.valeur !== "partage"),
);

const apercuElement = ref<HTMLElement | null>(null);

// ── Défilement synchronisé ──────────────────────────────────────────────────
//
// En mode partagé, les deux panneaux défilaient chacun de leur côté : on
// corrigeait un paragraphe à gauche en cherchant son rendu à droite. La
// position est reportée en PROPORTION et non en pixels — les deux colonnes
// n'ont ni la même typographie ni la même hauteur, un report en pixels
// dériverait dès le premier titre.
//
// Le verrou évite l'aller-retour : sans lui, le défilement reporté sur le
// panneau opposé déclencherait son propre écouteur, qui corrigerait le
// premier, et les deux s'entraîneraient mutuellement.
let synchronisationEnCours = false;

function reporterDefilement(source: HTMLElement, cible: HTMLElement) {
  if (synchronisationEnCours || modeEffectif.value !== "partage") return;

  const amplitudeSource = source.scrollHeight - source.clientHeight;
  const amplitudeCible = cible.scrollHeight - cible.clientHeight;
  // Un panneau qui tient entièrement à l'écran n'a rien à faire défiler, et la
  // division donnerait NaN.
  if (amplitudeSource <= 0 || amplitudeCible <= 0) return;

  synchronisationEnCours = true;
  cible.scrollTop = (source.scrollTop / amplitudeSource) * amplitudeCible;
  // Relâché au cadre suivant : l'affectation ci-dessus provoque un événement
  // `scroll` qui n'est émis qu'après le présent appel.
  requestAnimationFrame(() => {
    synchronisationEnCours = false;
  });
}

/** Le conteneur que CodeMirror fait défiler, à distinguer de son hôte. */
function zoneDefilementEditeur(): HTMLElement | null {
  return editorContainer.value?.querySelector(".cm-scroller") ?? null;
}

function auDefilementEditeur() {
  const source = zoneDefilementEditeur();
  if (source && apercuElement.value)
    reporterDefilement(source, apercuElement.value);
}

function auDefilementApercu() {
  const cible = zoneDefilementEditeur();
  if (cible && apercuElement.value)
    reporterDefilement(apercuElement.value, cible);
}

// Thème personnalisé pour ton design
const customTheme = EditorView.theme({
  "&": {
    height: "100%",
    backgroundColor: "#F4F1EA",
    color: "#111111",
    fontFamily: "system-ui, -apple-system, sans-serif",
    fontSize: "16px",
    lineHeight: "1.6",
  },
  ".cm-content": {
    caretColor: "#C4341C",
    fontFamily: "inherit",
    fontSize: "inherit",
    lineHeight: "inherit",
    padding: "16px",
  },
  ".cm-gutters": {
    backgroundColor: "#F4F1EA",
    color: "#111111",
    borderRight: "1px solid #111111",
  },
  ".cm-selectionBackground": {
    backgroundColor: "#C4341C",
    color: "#F4F1EA",
  },
  ".cm-cursor": {
    borderLeftColor: "#C4341C",
  },
  "&.cm-focused": {
    outline: "2px solid #C4341C",
  },
});

// Configuration de marked
const markedOptions = {
  gfm: true,
  breaks: true,
  headerIds: false,
  mangle: false,
};

// Contenu pour l'aperçu
// SÉCURITÉ — XSS stocké (OWASP A03:2021 Injection).
// marked convertit le Markdown en HTML mais ne filtre PAS le HTML brut qu'il
// rencontre : un document contenant <img src=x onerror="alert(1)"> produit
// cette balise telle quelle, et v-html l'injecte sans échappement, donc le
// gestionnaire onerror s'exécute. Comme l'éditeur enregistre automatiquement
// le contenu, la charge est persistée en base et rejouée à chaque ouverture
// du document (XSS stocké, et non simplement réfléchi).
// DOMPurify supprime les balises et attributs dangereux (script, on*, iframe,
// javascript: ...) après la conversion Markdown et avant l'injection.
const previewHtml = computed(() => {
  try {
    const rawHtml = marked.parse(
      internalValue.value || "",
      markedOptions,
    ) as string;
    return DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } });
  } catch {
    return "<p>Erreur de rendu</p>";
  }
});

// Initialisation de l'éditeur
function initEditor() {
  if (!editorContainer.value) return false;

  const extensions = [
    markdown({ base: markdownLanguage }),
    customTheme,
    // SANS CECI, LE TEXTE SORT DU CHAMP VISIBLE. CodeMirror ne replie pas les
    // lignes par défaut : un titre, une URL ou une ligne de tableau plus large
    // que le panneau partait vers la droite, hors du cadre, et seul un
    // défilement horizontal permettait d'en lire la fin. Sur un document
    // administratif, où les lignes de tableau sont longues par nature, la
    // moitié du texte était invisible.
    EditorView.lineWrapping,
    // CodeMirror rend une zone d'édition en `contenteditable`, que les
    // technologies d'assistance annoncent comme un champ de saisie sans nom :
    // axe-core la signale en « aria-input-field-name », gravité « serious ».
    // Aucune <label> ne peut la désigner, puisque ce n'est pas un <input> —
    // le nom accessible doit donc être porté par la zone elle-même.
    EditorView.contentAttributes.of({
      "aria-label": "Éditeur de document, format Markdown",
    }),
    keymap.of([...defaultKeymap, ...historyKeymap]),
    history(),
    EditorView.updateListener.of((update) => {
      if (update.docChanged) {
        const newValue = update.state.doc.toString();
        if (newValue !== internalValue.value) {
          internalValue.value = newValue;
          emit("update:modelValue", newValue);
          emit("input");
        }
      }
    }),
  ];

  const state = EditorState.create({
    doc: internalValue.value || "",
    extensions,
  });

  const view = new EditorView({
    state,
    parent: editorContainer.value,
  });

  editorView.value = view;
  return true;
}

// Fonction pour insérer du Markdown
function insertMarkdown(prefix: string, suffix: string = "") {
  if (!editorView.value) return;

  const { state } = editorView.value;
  const { selection } = state;
  const from = selection.main.from;
  const to = selection.main.to;
  const selectedText = state.doc.sliceString(from, to);

  let insertText = prefix + selectedText + suffix;
  if (!selectedText) {
    insertText = prefix + "texte" + suffix;
  }

  editorView.value.dispatch({
    changes: { from, to, insert: insertText },
    selection: {
      anchor: from + insertText.length,
      head: from + insertText.length,
    },
  });

  editorView.value.focus();
  internalValue.value = editorView.value.state.doc.toString();
  emit("update:modelValue", internalValue.value);
  emit("input");
}

// Boutons de la barre d'outils
const toolbarActions = {
  bold: () => insertMarkdown("**", "**"),
  italic: () => insertMarkdown("*", "*"),
  underline: () => insertMarkdown("<u>", "</u>"),
  h1: () => insertMarkdown("# "),
  h2: () => insertMarkdown("## "),
  h3: () => insertMarkdown("### "),
  p: () => insertMarkdown("\n\n"),
  ul: () => insertMarkdown("- "),
  ol: () => insertMarkdown("1. "),
  link: () => {
    const url = prompt("URL du lien (https://...)");
    if (url) {
      const text = prompt("Texte du lien", "texte du lien");
      insertMarkdown(`[${text || "texte du lien"}]`, `](${url})`);
    }
  },
  code: () => insertMarkdown("```\n", "\n```"),
  inlineCode: () => insertMarkdown("`", "`"),
  quote: () => insertMarkdown("> "),
  hr: () => insertMarkdown("---"),
  ia: () => emit("openIaPanel"),
};

// Focus l'éditeur
function focus() {
  editorView.value?.focus();
}

// Met à jour le contenu si le parent le change
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== internalValue.value) {
      internalValue.value = newValue || "";
      if (editorView.value) {
        editorView.value.dispatch({
          changes: {
            from: 0,
            to: editorView.value.state.doc.length,
            insert: internalValue.value,
          },
        });
      }
    }
  },
);

// Initialise à l'affichage
onMounted(() => {
  // `matchMedia` manque dans certains environnements de test : le composant
  // doit se monter quand même, en supposant un grand écran.
  if (typeof window !== "undefined" && window.matchMedia) {
    mediaPartage = window.matchMedia(PARTAGE_MIN);
    suivreLargeur(mediaPartage);
    mediaPartage.addEventListener("change", suivreLargeur);
  }

  nextTick(() => {
    initEditor();
    zoneDefilementEditeur()?.addEventListener("scroll", auDefilementEditeur, {
      passive: true,
    });
  });
});

// Passer de « lire » à un mode qui montre l'éditeur le remonte dans le DOM :
// l'écouteur posé sur l'ancien conteneur est parti avec lui, et CodeMirror
// doit remesurer, sans quoi la zone de saisie garde la hauteur qu'elle avait
// au moment où elle a été masquée.
watch(modeEffectif, () => {
  nextTick(() => {
    if (!afficheEditeur.value) return;
    const zone = zoneDefilementEditeur();
    zone?.removeEventListener("scroll", auDefilementEditeur);
    zone?.addEventListener("scroll", auDefilementEditeur, { passive: true });
    editorView.value?.requestMeasure();
  });
});

// Nettoie à la fermeture
onBeforeUnmount(() => {
  mediaPartage?.removeEventListener("change", suivreLargeur);
  zoneDefilementEditeur()?.removeEventListener("scroll", auDefilementEditeur);
  if (editorView.value) {
    editorView.value.destroy();
    editorView.value = null;
  }
});

// Expose la fonction focus
defineExpose({ focus });
</script>

<template>
  <!--
    LA HAUTEUR DE TRAVAIL EST PORTÉE ICI, sur la racine, et non sur la zone des
    panneaux. Celle-ci est un élément flexible : son `flex-basis` l'emporte sur
    toute hauteur qu'on lui déclarerait, et elle s'étire donc à la taille que
    lui laisse son parent. Tant que ce parent n'avait qu'un `min-h`, il
    grandissait avec le document — mesuré à plus de dix mille pixels sur un
    document d'essai — et c'est la page entière qui défilait au lieu des
    panneaux.
  -->
  <div
    class="border border-[#111111] bg-[#F4F1EA] rounded-none overflow-hidden flex flex-col h-[min(70vh,44rem)] min-h-[22rem]"
    :class="{ 'opacity-50 pointer-events-none': disabled }"
  >
    <!-- Barre d'outils -->
    <div
      class="bg-[#FAF8F5] border-b border-[#111111] p-2 flex flex-wrap items-center gap-x-1 gap-y-2"
      role="toolbar"
      aria-label="Mise en forme Markdown"
    >
      <button
        type="button"
        title="Gras"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.bold()"
      >
        G
      </button>
      <button
        type="button"
        title="Italique"
        class="h-9 px-3 font-mono text-xs font-bold italic text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.italic()"
      >
        I
      </button>
      <button
        type="button"
        title="Souligné"
        class="h-9 px-3 font-mono text-xs font-bold underline text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.underline()"
      >
        S
      </button>

      <span class="w-px h-6 bg-[#111111]/20 mx-1" aria-hidden="true"></span>

      <button
        type="button"
        title="Titre 1"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.h1()"
      >
        H1
      </button>
      <button
        type="button"
        title="Titre 2"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.h2()"
      >
        H2
      </button>
      <button
        type="button"
        title="Titre 3"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.h3()"
      >
        H3
      </button>

      <span class="w-px h-6 bg-[#111111]/20 mx-1" aria-hidden="true"></span>

      <button
        type="button"
        title="Liste à puces"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.ul()"
      >
        • Liste
      </button>
      <button
        type="button"
        title="Liste numérotée"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.ol()"
      >
        1. Liste
      </button>

      <span class="w-px h-6 bg-[#111111]/20 mx-1" aria-hidden="true"></span>

      <button
        type="button"
        title="Lien"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.link()"
      >
        Lien
      </button>
      <button
        type="button"
        title="Code"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.code()"
      >
        Code
      </button>
      <button
        type="button"
        title="Citation"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.quote()"
      >
        " Citation
      </button>

      <span class="w-px h-6 bg-[#111111]/20 mx-1" aria-hidden="true"></span>

      <button
        type="button"
        title="Assistant IA"
        class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
        @click="toolbarActions.ia()"
      >
        ✨ IA
      </button>
      <!--
        Sélecteur de mode. `aria-pressed` et non trois liens : ce sont bien
        trois états d'un même réglage, et le lecteur d'écran annonce lequel est
        actif. `ml-auto` le pousse à droite, séparé des outils d'écriture.
      -->
      <div
        class="flex items-center border border-[#111111] ml-auto"
        role="group"
        aria-label="Disposition de l'éditeur"
      >
        <button
          v-for="(option, index) in modesVisibles"
          :key="option.valeur"
          type="button"
          :title="option.titre"
          :aria-pressed="modeEffectif === option.valeur"
          :class="[
            'h-9 px-3 font-mono text-xs font-bold transition-colors cursor-pointer',
            index > 0 ? 'border-l border-[#111111]' : '',
            modeEffectif === option.valeur
              ? 'bg-[#111111] text-[#F4F1EA]'
              : 'text-[#111111] hover:bg-[#111111]/10',
          ]"
          @click="mode = option.valeur"
        >
          {{ option.libelle }}
        </button>
      </div>
    </div>

    <!--
      Zone d'édition et d'aperçu.

      `min-h-0` est indispensable : un élément flexible refuse par défaut de
      descendre sous la hauteur de son contenu, ce qui ferait déborder la zone
      hors de la hauteur fixée par la racine et rendrait inopérant le
      `overflow` des panneaux.

      EMPILÉS SOUS `md`. Deux colonnes de quelques centimètres sur un téléphone
      ne se lisent ni l'une ni l'autre : en dessous du point de rupture, les
      panneaux passent l'un au-dessus de l'autre.
    -->
    <div class="flex flex-col md:flex-row flex-1 min-h-0 overflow-hidden">
      <!--
        Éditeur. `min-w-0` et `min-h-0` SONT NÉCESSAIRES : un élément flexible
        refuse par défaut de descendre sous la largeur de son contenu
        (`min-width: auto`). Un titre long ou un bloc de code le faisait donc
        déborder du cadre au lieu d'y défiler. Même raisonnement en hauteur une
        fois les panneaux empilés.

        Le défilement est laissé à CodeMirror, qui gère déjà le sien : le
        `overflow-auto` qui enveloppait la zone en ajoutait un second,
        imbriqué, et l'on pouvait faire défiler le cadre jusqu'à n'avoir plus
        que du vide sous les yeux, texte toujours présent mais hors champ.
      -->
      <div
        v-show="afficheEditeur"
        class="relative flex-1 min-w-0 min-h-0 overflow-hidden"
        :class="afficheApercu ? 'md:w-1/2' : 'w-full'"
      >
        <!--
          POSITIONNEMENT ABSOLU, et c'est ce qui donne enfin sa hauteur à
          l'éditeur. CodeMirror se dimensionne par « height: 100% » (voir
          customTheme), règle qui ne résout rien tant que l'ancêtre n'a pas de
          hauteur DÉCLARÉE : un élément flexible en reçoit une à la mise en
          page, mais sa propriété `height` reste `auto`, et le pourcentage
          retombe alors sur la hauteur du contenu. La zone de saisie prenait
          donc la taille du document — près de trois mille pixels pour celui
          d'essai — et c'est la page qui défilait.

          `inset-0` dans un parent `relative` fournit les quatre côtés, donc
          une hauteur résolue, et CodeMirror retrouve son propre défilement.
        -->
        <div ref="editorContainer" class="absolute inset-0"></div>
      </div>

      <!-- Aperçu -->
      <div
        v-if="afficheApercu"
        ref="apercuElement"
        class="flex-1 min-w-0 min-h-0 overflow-auto bg-[#FAF8F5] px-4 py-8 sm:px-8"
        :class="
          afficheEditeur
            ? 'border-t md:border-t-0 md:border-l border-[#111111] md:w-1/2'
            : 'w-full'
        "
        @scroll="auDefilementApercu"
      >
        <!--
          C'est LE v-html à risque du projet : previewHtml vient du texte de
          l'utilisateur. Il est assaini par DOMPurify avant d'arriver ici, et
          cette parade est couverte par 13 tests de non-régression
          (markdown-sanitization.spec.ts). Toute modification de la chaîne de
          rendu doit les faire passer avant d'être retenue.
        -->
        <!-- eslint-disable vue/no-v-html -->
        <div
          class="prose mx-auto w-full max-w-[72ch] bg-white border border-[#111111]/15 shadow-[3px_3px_0px_0px_rgba(17,17,17,0.08)] px-6 py-8 sm:px-10 sm:py-12"
          v-html="previewHtml"
        ></div>
        <!-- eslint-enable vue/no-v-html -->
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
  RIEN NE DOIT DÉPASSER LA COLONNE. Les règles ci-dessous traitent la cause
  constatée du débordement : un contenu plus large que son conteneur. Une URL
  sans espace, un tableau à six colonnes ou une ligne de code longue
  élargissaient le panneau, qui sortait alors du cadre de l'éditeur et
  provoquait un défilement horizontal de toute la page.

  `overflow-wrap: anywhere` sur le texte, une largeur plafonnée sur les blocs
  qui ne se coupent pas, et un défilement PROPRE au tableau et au bloc de code
  — ces deux-là doivent garder leurs colonnes et leur indentation, les couper
  les rendrait illisibles.
*/
.prose {
  overflow-wrap: anywhere;
}
.prose :deep(img),
.prose :deep(video),
.prose :deep(svg) {
  max-width: 100%;
  height: auto;
}
.prose :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}
.prose :deep(th),
.prose :deep(td) {
  border: 1px solid #11111133;
  padding: 0.4em 0.6em;
  /* Dans un tableau, couper au milieu d'un mot est pire que défiler. */
  overflow-wrap: normal;
}

/* Styles pour l'aperçu Markdown */
.prose :deep(h1) {
  font-family: Georgia, serif;
  font-size: 2em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #111111;
}
/* Le premier bloc rendu ne doit pas ouvrir sur une marge haute en double. */
.prose :deep(> :first-child) {
  margin-top: 0;
}
.prose :deep(h2) {
  font-family: Georgia, serif;
  font-size: 1.5em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #111111;
}
.prose :deep(h3) {
  font-family: Georgia, serif;
  font-size: 1.3em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #111111;
}
.prose :deep(p) {
  margin: 0.5em 0;
  line-height: 1.6;
  color: #111111;
}
.prose :deep(ul) {
  list-style-type: disc;
  padding-left: 2em;
  margin: 0.5em 0;
}
.prose :deep(ol) {
  list-style-type: decimal;
  padding-left: 2em;
  margin: 0.5em 0;
}
.prose :deep(li) {
  margin: 0.25em 0;
}
.prose :deep(a) {
  color: #c4341c;
  text-decoration: underline;
}
.prose :deep(a:hover) {
  color: #a72c18;
}
.prose :deep(strong) {
  font-weight: bold;
  color: #111111;
}
.prose :deep(em) {
  font-style: italic;
  color: #111111;
}
.prose :deep(u) {
  text-decoration: underline;
}
.prose :deep(code) {
  background-color: #11111110;
  padding: 0 4px;
  border-radius: 2px;
  font-family: monospace;
  font-size: 0.9em;
}
.prose :deep(pre) {
  background-color: #11111110;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
  max-width: 100%;
  /* Le code garde son indentation : il défile plutôt qu'il ne se coupe. */
  overflow-wrap: normal;
  font-family: monospace;
  font-size: 0.9em;
}
.prose :deep(pre code) {
  background-color: transparent;
  padding: 0;
}
.prose :deep(blockquote) {
  border-left: 3px solid #c4341c;
  padding-left: 1em;
  margin-left: 0;
  color: #11111180;
  font-style: italic;
}
.prose :deep(hr) {
  border: none;
  border-top: 1px solid #111111;
  margin: 1em 0;
}
</style>
