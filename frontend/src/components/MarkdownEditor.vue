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
const showPreview = ref(true);
const internalValue = ref(props.modelValue || "");

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
  nextTick(() => {
    initEditor();
  });
});

// Nettoie à la fermeture
onBeforeUnmount(() => {
  if (editorView.value) {
    editorView.value.destroy();
    editorView.value = null;
  }
});

// Expose la fonction focus
defineExpose({ focus });
</script>

<template>
  <div
    class="border border-[#111111] bg-[#F4F1EA] rounded-none overflow-hidden flex flex-col min-h-90"
    :class="{ 'opacity-50 pointer-events-none': disabled }"
  >
    <!-- Barre d'outils -->
    <div
      class="bg-[#FAF8F5] border-b border-[#111111] p-2 flex flex-wrap items-center gap-1"
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
      <button
        type="button"
        title="Aperçu"
        :class="[
          'h-9 px-3 font-mono text-xs font-bold transition-colors',
          showPreview
            ? 'bg-[#111111] text-[#F4F1EA]'
            : 'text-[#111111] hover:bg-[#111111]/10',
        ]"
        @click="showPreview = !showPreview"
      >
        {{ showPreview ? "✓ Aperçu" : "× Aperçu" }}
      </button>
    </div>

    <!-- Zone d'édition et d'aperçu -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Éditeur -->
      <div class="flex-1 overflow-auto p-6">
        <div ref="editorContainer" class="h-full"></div>
      </div>

      <!-- Aperçu -->
      <div
        v-if="showPreview"
        class="w-1/2 border-l border-[#111111] bg-[#FAF8F5] overflow-auto p-6"
      >
        <div class="prose max-w-none" v-html="previewHtml"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Styles pour l'aperçu Markdown */
.prose :deep(h1) {
  font-family: Georgia, serif;
  font-size: 2em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #111111;
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
