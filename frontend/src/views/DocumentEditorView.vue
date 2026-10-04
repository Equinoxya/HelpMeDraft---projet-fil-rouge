<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import documentService from "../services/documentService";
import type { DocumentStatus } from "../types/document";
import dossierService from "../services/dossierService";
import type { DossierItem } from "../types/dossier";
import iaService from "../services/iaService";
import {
  type IaTypeAction,
  type IaScope,
  type IaHistoriqueEntry,
} from "../types/ia";
import {
  estimerDureeGeneration,
  formaterDuree,
  avancementEstime,
} from "../utils/iaEstimation";
import MarkdownEditor from "../components/MarkdownEditor.vue";
import { messageErreur, estAnnulation, estStatut } from "../utils/erreurs";

// Type pour le ref de l'éditeur
interface MarkdownEditorExposed {
  focus: () => void;
}

const route = useRoute();
const router = useRouter();

const documentId = computed(() =>
  typeof route.params.id === "string" ? route.params.id : null,
);
const isEditMode = computed(() => documentId.value !== null);

const titre = ref("");
const status = ref<DocumentStatus>("brouillon");
const idDossier = ref<string>("");
const content = ref<string>("");
const dossiers = ref<DossierItem[]>([]);

const isLoading = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const errorMessage = ref("");
const savedNotice = ref(false);
let savedNoticeTimeout: ReturnType<typeof setTimeout> | null = null;

type AutoSaveStatus = "idle" | "saving" | "saved" | "error";
const autoSaveStatus = ref<AutoSaveStatus>("idle");
let autoSaveTimeout: ReturnType<typeof setTimeout> | null = null;
const AUTOSAVE_DELAY_MS = 2500;

const isTitreValid = computed(() => {
  const trimmed = titre.value.trim();
  return trimmed.length > 0 && trimmed.length <= 255;
});

// Référence pour l'éditeur Markdown
const markdownEditorRef = ref<MarkdownEditorExposed | null>(null);

// Panel IA
const showIaPanel = ref(false);
const iaTypeAction = ref<IaTypeAction>("reformuler");
const iaScope = ref<IaScope>("document");
const iaInstructions = ref("");
const iaLoading = ref(false);
const iaError = ref("");
const iaResult = ref<string | null>(null);
// Identifiant de l'interaction en base. Nécessaire pour marquer l'insertion
// (AI Act) : sans lui, on saurait qu'un texte a été inséré mais pas de quelle
// génération il provient.
const iaResultId = ref<string | null>(null);
// Texte réellement soumis au modèle, figé au moment de la génération. La
// sélection du navigateur peut changer pendant l'attente ; appliquer la
// proposition à un autre passage que celui qu'on a soumis donnerait un
// résultat silencieusement faux.
const iaSourceText = ref<string | null>(null);

// Historique des interactions IA du document, et traçabilité des passages
// effectivement versés au document.
const iaHistorique = ref<IaHistoriqueEntry[]>([]);
const afficherHistoriqueIa = ref(false);

// Compteur de progression de la génération.
//
// Le backend n'interrompt plus l'inférence (voir OLLAMA_CONNECT_TIMEOUT dans
// backend/app/config.py) : une génération peut légitimement durer plus d'une
// minute sur une machine sans carte graphique. Un bouton figé pendant tout ce
// temps ne dit pas si quelque chose avance ou si l'application est bloquée.
// On affiche donc le temps écoulé et le temps estimé.
const iaSecondesEcoulees = ref(0);
const iaSecondesEstimees = ref(0);
let iaCompteurInterval: ReturnType<typeof setInterval> | null = null;

// Permet d'abandonner une génération en cours. Indispensable depuis que plus
// aucun délai ne borne l'inférence : sans ce bouton, une génération lente
// laisse l'utilisateur sans aucune porte de sortie.
let iaAbort: AbortController | null = null;

const iaAttenteDepassee = computed(
  () =>
    iaSecondesEstimees.value > 0 &&
    iaSecondesEcoulees.value > iaSecondesEstimees.value,
);

const iaAvancement = computed(() =>
  avancementEstime(iaSecondesEcoulees.value, iaSecondesEstimees.value),
);

const iaTexteProgression = computed(() => {
  const ecoule = formaterDuree(iaSecondesEcoulees.value);
  if (iaAttenteDepassee.value) {
    // L'estimation n'est qu'un ordre de grandeur : la dépasser est normal et
    // ne doit pas ressembler à une panne. On arrête de l'afficher plutôt que
    // de montrer un temps restant négatif.
    return `${ecoule} écoulées — plus long que prévu, la génération continue`;
  }
  return `${ecoule} / ~${formaterDuree(iaSecondesEstimees.value)} estimées`;
});

function demarrerCompteurIa(contenu: string) {
  iaSecondesEcoulees.value = 0;
  iaSecondesEstimees.value = estimerDureeGeneration(
    contenu,
    iaTypeAction.value,
  );
  // On repart du temps de départ réel à chaque tick plutôt que d'incrémenter :
  // les intervalles de l'onglet en arrière-plan sont ralentis par le
  // navigateur, et un compteur incrémenté dériverait du temps réellement
  // écoulé.
  const debut = Date.now();
  arreterCompteurIa();
  iaCompteurInterval = setInterval(() => {
    iaSecondesEcoulees.value = (Date.now() - debut) / 1000;
  }, 1000);
}

function arreterCompteurIa() {
  if (iaCompteurInterval) {
    clearInterval(iaCompteurInterval);
    iaCompteurInterval = null;
  }
}

function annulerGenerationIa() {
  iaAbort?.abort();
}

function openIaPanel() {
  const selection = window.getSelection();
  if (selection && !selection.isCollapsed) {
    const selectedText = selection.toString();
    if (selectedText) {
      iaScope.value = "selection";
    }
  } else {
    iaScope.value = "document";
  }
  iaResult.value = null;
  iaResultId.value = null;
  iaError.value = "";
  showIaPanel.value = true;
}

function closeIaPanel() {
  showIaPanel.value = false;
  iaResult.value = null;
  iaResultId.value = null;
  iaError.value = "";
  // Fermer le panneau vaut abandon : sans cela, la génération continuerait
  // d'occuper le serveur pour un résultat que plus personne n'attend.
  annulerGenerationIa();
}

function getIaSourceText(): string | null {
  if (iaScope.value === "selection") {
    const selection = window.getSelection();
    if (selection && !selection.isCollapsed) {
      const selectedText = selection.toString();
      if (selectedText) return selectedText;
    }
    iaError.value = "Sélectionnez d'abord du texte dans le document.";
    return null;
  }
  return content.value;
}

async function handleGenerateIa() {
  if (!documentId.value) {
    iaError.value = "Enregistrez d'abord le document avant d'utiliser l'IA.";
    return;
  }

  const contenu = getIaSourceText();
  if (!contenu || !contenu.trim()) {
    iaError.value = "Le texte à traiter est vide.";
    return;
  }

  iaLoading.value = true;
  iaError.value = "";
  iaResult.value = null;
  iaResultId.value = null;
  demarrerCompteurIa(contenu);
  iaAbort = new AbortController();

  try {
    const result = await iaService.generer(
      documentId.value,
      {
        type_action: iaTypeAction.value,
        scope: iaScope.value,
        contenu,
        instructions: iaInstructions.value.trim() || undefined,
      },
      iaAbort.signal,
    );
    iaResult.value = result.content_after;
    iaResultId.value = result.id_ia;
  } catch (err) {
    // Une annulation n'est pas une erreur : l'utilisateur sait ce qu'il a
    // fait, et lui afficher « L'assistant IA n'a pas pu répondre » le
    // laisserait croire à une panne.
    if (estAnnulation(err)) {
      iaError.value = "";
    } else {
      iaError.value = messageErreur(err, "L'assistant IA n'a pas pu répondre.");
    }
  } finally {
    iaLoading.value = false;
    arreterCompteurIa();
    iaAbort = null;
  }
}

/**
 * Applique la proposition au document.
 *
 * Deux modes, exigés par le cahier des charges : « le résultat doit pouvoir
 * être inséré ou venir remplacer le texte d'origine ». Remplacer écrase la
 * source ; insérer la conserve et ajoute la proposition juste après. Dans les
 * deux cas, c'est l'utilisateur qui décide — la génération seule ne touche
 * jamais au document.
 *
 * Le repérage se fait par recherche de chaîne dans le Markdown, et non par les
 * décalages de la sélection du navigateur. `Range.startOffset` compte les
 * caractères DANS LE NŒUD DOM sélectionné, pas depuis le début du document :
 * utilisé tel quel sur `content`, il désigne une position arbitraire et
 * tronquait le texte à un endroit sans rapport avec la sélection. Chercher le
 * texte source dans la chaîne donne la bonne position, ou aucune — auquel cas
 * on ajoute en fin plutôt que d'écrire au hasard.
 *
 * @returns le décalage de la proposition dans le nouveau contenu, ou null si
 *          rien n'a été appliqué.
 */
interface ImpactProposition {
  /** Décalage de la proposition dans le nouveau contenu. */
  position: number;
  /** Message à montrer quand le passage visé n'a pas pu être retrouvé. */
  avertissement?: string;
}

function appliquerProposition(
  mode: "inserer" | "remplacer",
): ImpactProposition | null {
  const proposition = iaResult.value;
  if (!proposition) return null;

  if (iaScope.value === "document") {
    if (mode === "remplacer") {
      content.value = proposition;
      return { position: 0 };
    }
    const position = content.value.length;
    content.value = `${content.value}\n\n${proposition}`;
    return { position: position + 2 };
  }

  // Portée « sélection » : on retrouve le texte soumis au modèle dans le
  // Markdown. iaSourceText est figé au moment de la génération, et non relu
  // ici : la sélection du navigateur a pu changer pendant l'attente, et
  // appliquer la proposition à un autre passage que celui qu'on a soumis
  // serait un résultat silencieusement faux.
  const source = iaSourceText.value;
  const debut = source ? content.value.indexOf(source) : -1;

  if (!source || debut === -1) {
    // La sélection ne correspond plus à rien dans le texte — elle venait de
    // l'aperçu rendu, ou le document a été modifié depuis. On n'écrase rien :
    // on ajoute en fin, et on le dit plutôt que de laisser croire au
    // remplacement demandé.
    const position = content.value.length;
    content.value = `${content.value}\n\n${proposition}`;
    return {
      position: position + 2,
      avertissement:
        "Le passage d'origine n'a pas été retrouvé : la proposition a été ajoutée en fin de document.",
    };
  }

  const avant = content.value.slice(0, debut);
  const apres = content.value.slice(debut + source.length);
  content.value =
    mode === "remplacer"
      ? avant + proposition + apres
      : `${avant}${source}\n\n${proposition}${apres}`;

  return {
    position: mode === "remplacer" ? debut : debut + source.length + 2,
  };
}

/**
 * Applique la proposition, puis enregistre la trace exigée par l'AI Act.
 *
 * L'ordre compte : on marque APRÈS avoir modifié le contenu, jamais avant.
 * Une trace enregistrée pour une insertion qui n'aurait pas eu lieu serait
 * fausse, et une trace fausse est pire qu'une trace absente — elle ferait
 * croire à une vérification qui n'a pas eu lieu.
 *
 * Symétriquement, un échec du marquage n'annule pas l'insertion : l'utilisateur
 * a demandé à insérer son texte, et lui retirer son travail parce qu'un appel
 * de journalisation a échoué serait une régression bien pire que l'écart de
 * traçabilité. L'échec est signalé, pas masqué.
 */
async function appliquerIaResult(mode: "inserer" | "remplacer") {
  const idIa = iaResultId.value;
  const impact = appliquerProposition(mode);
  if (impact === null) return;

  nextTick(() => {
    markdownEditorRef.value?.focus();
  });
  scheduleAutoSave();

  let message = impact.avertissement ?? "";

  if (idIa && documentId.value) {
    try {
      await iaService.marquerInsertion(documentId.value, idIa, impact.position);
      await chargerHistoriqueIa();
    } catch {
      message =
        "Le texte a bien été inséré, mais la trace de génération n'a pas pu être enregistrée.";
    }
  }

  if (message) {
    // Le panneau reste ouvert : fermer effacerait le message avec lui, et
    // l'utilisateur n'apprendrait jamais que le résultat diffère de ce qu'il a
    // demandé.
    iaResult.value = null;
    iaResultId.value = null;
    iaError.value = message;
    return;
  }

  closeIaPanel();
}

/**
 * Charge l'historique des interactions IA du document.
 *
 * Silencieux en cas d'échec : l'historique est une information secondaire, et
 * un message d'erreur en haut de l'éditeur pour une liste qui ne s'affiche pas
 * coûterait plus à l'utilisateur qu'il ne lui apporte.
 */
/**
 * Passages du document issus d'une génération (AI Act, art. 50).
 *
 * La réconciliation se fait par recherche du texte généré dans le contenu
 * courant, et non par les décalages enregistrés. Un décalage devient faux dès
 * la première frappe en amont du passage : le maintenir exigerait de suivre
 * chaque édition, pour répondre à une question — « ce passage vient-il d'une
 * génération ? » — à laquelle une recherche de chaîne répond directement.
 *
 * Trois états, et le troisième est le plus utile : un passage « modifié
 * depuis » dit que l'utilisateur s'est approprié le texte, ce qui est
 * exactement le comportement que l'outil vise.
 */
const passagesGeneres = computed(() =>
  iaHistorique.value
    .filter((entree) => entree.insere)
    .map((entree) => ({
      ...entree,
      present: Boolean(
        entree.content_after && content.value.includes(entree.content_after),
      ),
    })),
);

function formaterHorodatage(iso: string | null): string {
  if (!iso) return "";
  const date = new Date(iso);
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

async function chargerHistoriqueIa() {
  if (!documentId.value) return;
  try {
    iaHistorique.value = await iaService.historique(documentId.value);
  } catch {
    iaHistorique.value = [];
  }
}

async function loadDocument(id: string) {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const document = await documentService.get(id);
    titre.value = document.titre;
    status.value = document.status;
    idDossier.value = document.id_dossier ?? "";
    content.value = document.content ?? "";
    isLoading.value = false;
    // Chargé après le document : la réconciliation des passages générés a
    // besoin du contenu courant pour dire lesquels y sont encore.
    void chargerHistoriqueIa();
    return;
  } catch (err) {
    if (estStatut(err, 404)) {
      errorMessage.value = "Ce document est introuvable.";
    } else {
      errorMessage.value =
        "Impossible de charger ce document. Réessayez plus tard.";
    }
  }

  isLoading.value = false;
}

onMounted(() => {
  if (documentId.value) {
    loadDocument(documentId.value);
  }
  dossierService
    .list()
    .then((list) => {
      dossiers.value = list;
    })
    .catch(() => {});
});

onBeforeUnmount(() => {
  if (savedNoticeTimeout) clearTimeout(savedNoticeTimeout);
  if (autoSaveTimeout) clearTimeout(autoSaveTimeout);
  arreterCompteurIa();
  annulerGenerationIa();
});

function buildPayload() {
  return {
    titre: titre.value.trim(),
    content: content.value,
    format: "markdown" as const,
    status: status.value,
    id_dossier: idDossier.value || undefined,
  };
}

async function persistDocument() {
  const payload = buildPayload();

  if (isEditMode.value && documentId.value) {
    await documentService.update(documentId.value, payload);
  } else {
    const created = await documentService.create(payload);
    router.replace(`/documents/${created.id_document}`);
  }
}

function scheduleAutoSave() {
  if (!isTitreValid.value) return;
  if (isLoading.value || isSaving.value) return;

  if (autoSaveTimeout) clearTimeout(autoSaveTimeout);
  autoSaveTimeout = setTimeout(performAutoSave, AUTOSAVE_DELAY_MS);
}

async function performAutoSave() {
  if (!isTitreValid.value || isSaving.value) return;

  autoSaveStatus.value = "saving";

  try {
    await persistDocument();
    autoSaveStatus.value = "saved";
  } catch {
    autoSaveStatus.value = "error";
  }
}

function handleEditorInput() {
  scheduleAutoSave();
}

async function handleSave() {
  errorMessage.value = "";

  if (!isTitreValid.value) {
    errorMessage.value = "Le titre est requis (255 caractères maximum).";
    return;
  }

  if (autoSaveTimeout) clearTimeout(autoSaveTimeout);
  isSaving.value = true;

  try {
    await persistDocument();

    savedNotice.value = true;
    autoSaveStatus.value = "saved";
    if (savedNoticeTimeout) clearTimeout(savedNoticeTimeout);
    savedNoticeTimeout = setTimeout(() => {
      savedNotice.value = false;
    }, 2500);
  } catch (err) {
    errorMessage.value = messageErreur(
      err,
      "Une erreur est survenue lors de l'enregistrement.",
    );
  } finally {
    isSaving.value = false;
  }
}

async function handleDelete() {
  if (!documentId.value) return;

  const confirmed = window.confirm(
    "Supprimer définitivement ce document ? Cette action est irréversible.",
  );
  if (!confirmed) return;

  isDeleting.value = true;
  errorMessage.value = "";

  try {
    await documentService.remove(documentId.value);
    router.push("/documents");
  } catch {
    errorMessage.value = "La suppression a échoué. Réessayez plus tard.";
    isDeleting.value = false;
  }
}

function handleCancel() {
  router.push("/documents");
}
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#C4341C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN CONTENT -->
    <main
      class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16"
    >
      <!-- BARRE SUPÉRIEURE -->
      <div class="flex items-center justify-between gap-4 mb-8">
        <RouterLink
          to="/documents"
          class="font-mono text-xs uppercase tracking-wider text-[#111111] hover:text-[#C4341C] transition-colors font-bold inline-flex items-center gap-2"
        >
          ← Retour aux documents
        </RouterLink>

        <button
          v-if="isEditMode"
          type="button"
          :disabled="isDeleting || isLoading"
          class="font-mono text-xs uppercase tracking-wider px-4 py-2 border border-[#C4341C] text-[#C4341C] hover:bg-[#C4341C] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors"
          @click="handleDelete"
        >
          {{ isDeleting ? "Suppression…" : "Supprimer le document" }}
        </button>
      </div>

      <!-- CARTE ÉDITEUR -->
      <div
        class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-10 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
      >
        <span
          class="font-mono text-xs uppercase tracking-[0.2em] text-[#C4341C] font-bold block mb-4"
        >
          [ {{ isEditMode ? "Mode Édition" : "Nouveau Brouillon" }} ]
        </span>

        <!-- CHARGEMENT -->
        <div
          v-if="isLoading"
          class="p-12 text-center font-mono text-xs uppercase tracking-widest text-[#111111]/60 flex flex-col items-center gap-3"
        >
          <span
            class="w-6 h-6 border-2 border-[#111111]/20 border-t-[#C4341C] rounded-full animate-spin"
          ></span>
          Chargement du document…
        </div>

        <template v-else>
          <!-- ALERTE ERREUR -->
          <div
            v-if="errorMessage"
            class="mb-6 p-4 border border-[#C4341C] bg-[#C4341C]/10 font-mono text-xs text-[#C4341C] font-bold flex items-center gap-2"
            role="alert"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4 shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span>{{ errorMessage }}</span>
          </div>

          <!-- NOTIFICATION SUCCÈS -->
          <div
            v-if="savedNotice"
            class="mb-6 p-4 border border-[#111111] bg-[#111111] text-[#F4F1EA] font-mono text-xs font-bold flex items-center gap-2"
            role="status"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4 text-[#C4341C] shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2.5"
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span>Document enregistré avec succès.</span>
          </div>

          <!-- CHAMP TITRE + STATUT + DOSSIER -->
          <div class="mb-6 grid sm:grid-cols-[1fr_auto_auto] gap-4 items-end">
            <div class="space-y-2">
              <label
                for="titre"
                class="font-mono text-xs uppercase tracking-wider text-[#111111] font-bold block"
              >
                Titre du document
              </label>
              <input
                id="titre"
                v-model="titre"
                type="text"
                placeholder="Ex. Compte rendu de réunion du 12 mars"
                maxlength="255"
                class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-serif text-lg text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#C4341C] transition-shadow"
              />
            </div>

            <div class="space-y-2">
              <label
                for="status"
                class="font-mono text-xs uppercase tracking-wider text-[#111111] font-bold block"
              >
                Statut
              </label>
              <select
                id="status"
                v-model="status"
                class="h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs uppercase tracking-wider text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#C4341C]"
              >
                <option value="brouillon">Brouillon</option>
                <option value="a_relire">À relire</option>
                <option value="termine">Terminé</option>
              </select>
            </div>
            <div class="space-y-2">
              <label
                for="dossier"
                class="font-mono text-xs uppercase tracking-wider text-[#111111] font-bold block"
              >
                Dossier
              </label>
              <select
                id="dossier"
                v-model="idDossier"
                class="h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs uppercase tracking-wider text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#C4341C]"
              >
                <option value="">Aucun dossier</option>
                <option
                  v-for="d in dossiers"
                  :key="d.id_dossier"
                  :value="d.id_dossier"
                >
                  {{ d.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- INDICATEUR D'AUTOSAVE -->
          <div class="mb-2 h-4 flex items-center">
            <span
              v-if="autoSaveStatus === 'saving'"
              class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/50 flex items-center gap-1.5"
            >
              <span
                class="w-2 h-2 border border-[#111111]/30 border-t-[#111111]/70 rounded-full animate-spin"
              ></span>
              Enregistrement…
            </span>
            <span
              v-else-if="autoSaveStatus === 'saved'"
              class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/50"
            >
              ✓ Enregistré automatiquement
            </span>
            <span
              v-else-if="autoSaveStatus === 'error'"
              class="font-mono text-[10px] uppercase tracking-wider text-[#C4341C] font-bold"
            >
              ⚠ Échec de l'enregistrement auto — pensez à enregistrer
              manuellement
            </span>
          </div>

          <!-- PANEL IA -->
          <div
            v-if="showIaPanel"
            class="mb-4 p-5 border-2 border-[#111111] bg-[#F4F1EA] space-y-4"
          >
            <div class="flex items-center justify-between">
              <span
                class="font-mono text-xs uppercase tracking-widest font-bold text-[#C4341C]"
              >
                [ Assistant IA — Ollama ]
              </span>
              <button
                type="button"
                class="font-mono text-xs text-[#111111]/60 hover:text-[#C4341C]"
                @click="closeIaPanel"
              >
                ✕ Fermer
              </button>
            </div>

            <!--
              MENTION D'INFORMATION — AI Act (règlement UE 2024/1689, art. 50),
              applicable depuis le 2 août 2026.

              Permanente, et non « affichée au premier usage puis mémorisée ».
              Un état « déjà vue » vivrait dans le localStorage : il disparaît
              en navigation privée et ne suit pas l'utilisateur d'un poste à
              l'autre, de sorte que l'information serait donnée ou non selon le
              navigateur — invérifiable. Une mention permanente satisfait
              l'obligation sans état à maintenir.

              Le titre du panneau nomme un outil ; cette mention dit que le
              texte proposé est produit par un modèle et peut être faux. Ce
              n'est pas la même information.
            -->
            <p
              class="flex gap-2 p-3 bg-[#FAF8F5] border border-[#111111]/30 text-xs leading-relaxed text-[#111111]/80"
              role="note"
            >
              <span aria-hidden="true" class="font-mono text-[#C4341C]">ⓘ</span>
              <span>
                Les propositions ci-dessous sont
                <strong>générées par un modèle de langage</strong> exécuté
                localement. Elles peuvent contenir des erreurs ou des
                affirmations fausses :
                <strong>relisez avant d'insérer</strong>. Vous restez
                responsable du contenu final de votre document
                (<RouterLink to="/cgu" class="underline hover:text-[#C4341C]"
                  >CGU</RouterLink
                >).
              </span>
            </p>

            <div class="flex flex-wrap gap-4">
              <div class="space-y-1">
                <label
                  class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/70 block"
                >
                  Action
                </label>
                <select
                  v-model="iaTypeAction"
                  class="h-9 px-3 bg-[#FAF8F5] border border-[#111111] font-mono text-xs uppercase"
                >
                  <option value="reformuler">Reformuler</option>
                  <option value="corriger">Corriger</option>
                  <option value="completer">Compléter</option>
                </select>
              </div>

              <div class="space-y-1">
                <label
                  class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/70 block"
                >
                  Portée
                </label>
                <select
                  v-model="iaScope"
                  class="h-9 px-3 bg-[#FAF8F5] border border-[#111111] font-mono text-xs uppercase"
                >
                  <option value="selection">Sélection</option>
                  <option value="document">Document entier</option>
                </select>
              </div>
            </div>

            <div class="space-y-1">
              <label
                class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/70 block"
              >
                Instructions particulières (optionnel)
              </label>
              <input
                v-model="iaInstructions"
                type="text"
                maxlength="500"
                placeholder="Ex. ton plus formel, plus concis..."
                class="w-full h-9 px-3 bg-[#FAF8F5] border border-[#111111] font-mono text-xs"
              />
            </div>

            <div
              v-if="iaError"
              class="font-mono text-xs text-[#C4341C] font-bold"
            >
              {{ iaError }}
            </div>

            <button
              type="button"
              :disabled="iaLoading"
              class="h-10 px-5 bg-[#111111] text-[#F4F1EA] font-mono text-xs uppercase tracking-wider hover:bg-[#C4341C] disabled:opacity-50 transition-colors"
              @click="handleGenerateIa"
            >
              {{ iaLoading ? "Génération en cours…" : "Générer" }}
            </button>

            <!--
              Compteur de génération. L'inférence n'est plus interrompue par un
              délai maximum : elle peut durer plus d'une minute sur une machine
              sans carte graphique. Sans ce compteur, l'utilisateur n'a aucun
              moyen de distinguer une attente normale d'un blocage.
            -->
            <div v-if="iaLoading" class="space-y-2" role="status">
              <div
                class="h-1 w-full bg-[#111111]/10 overflow-hidden"
                aria-hidden="true"
              >
                <div
                  class="h-full bg-[#C4341C] transition-[width] duration-1000 ease-linear"
                  :style="{ width: `${iaAvancement * 100}%` }"
                ></div>
              </div>
              <div class="flex items-center justify-between gap-3">
                <p
                  class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60"
                >
                  {{ iaTexteProgression }}
                </p>
                <button
                  type="button"
                  class="shrink-0 font-mono text-[10px] uppercase tracking-wider underline hover:text-[#C4341C] transition-colors"
                  @click="annulerGenerationIa"
                >
                  Annuler
                </button>
              </div>
            </div>

            <div
              v-if="iaResult"
              class="pt-3 border-t border-[#111111]/20 space-y-3"
            >
              <p
                class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60"
              >
                Résultat proposé :
              </p>
              <div
                class="p-3 bg-[#FAF8F5] border border-[#111111]/30 text-sm font-serif whitespace-pre-wrap"
              >
                {{ iaResult }}
              </div>
              <!--
                Deux actions distinctes, exigées par le cahier des charges :
                « le résultat doit pouvoir être inséré ou venir remplacer le
                texte d'origine ». Insérer conserve la source et ajoute la
                proposition après ; remplacer écrase la source. Aucune des deux
                n'est appliquée sans ce clic — la génération ne touche jamais au
                document d'elle-même.
              -->
              <div class="flex flex-wrap gap-3">
                <button
                  type="button"
                  class="h-9 px-4 bg-[#111111] text-[#F4F1EA] font-mono text-xs uppercase hover:bg-[#C4341C] transition-colors"
                  @click="appliquerIaResult('inserer')"
                >
                  Insérer
                </button>
                <button
                  type="button"
                  class="h-9 px-4 bg-[#111111] text-[#F4F1EA] font-mono text-xs uppercase hover:bg-[#C4341C] transition-colors"
                  @click="appliquerIaResult('remplacer')"
                >
                  Remplacer
                </button>
                <button
                  type="button"
                  class="h-9 px-4 border border-[#111111] font-mono text-xs uppercase hover:bg-[#111111]/10 transition-colors"
                  @click="iaResult = null"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>

          <!--
            TRAÇABILITÉ DES CONTENUS GÉNÉRÉS — AI Act (art. 50).

            La table `ia` conserve chaque proposition produite ; `insere`
            distingue celles que l'utilisateur a versées au document. La
            présence du passage est recalculée à l'affichage en cherchant le
            texte généré dans le contenu courant : un décalage enregistré
            deviendrait faux à la première frappe en amont.

            « Modifié depuis » n'est pas un échec de traçabilité, c'est
            l'information la plus utile de la liste : elle dit que
            l'utilisateur s'est approprié le texte.
          -->
          <section
            v-if="passagesGeneres.length > 0"
            class="mt-6 border border-[#111111] bg-[#FAF8F5]"
          >
            <h2 class="m-0">
              <button
                type="button"
                class="w-full flex items-center justify-between gap-3 px-4 py-3 font-mono text-[10px] uppercase tracking-wider text-[#111111]/70 hover:text-[#C4341C] transition-colors"
                :aria-expanded="afficherHistoriqueIa"
                aria-controls="passages-generes"
                @click="afficherHistoriqueIa = !afficherHistoriqueIa"
              >
                <span>
                  Passages issus d'une génération ({{ passagesGeneres.length }})
                </span>
                <span aria-hidden="true">{{
                  afficherHistoriqueIa ? "▴" : "▾"
                }}</span>
              </button>
            </h2>

            <ul
              v-show="afficherHistoriqueIa"
              id="passages-generes"
              class="px-4 pb-4 space-y-3 list-none"
            >
              <li
                v-for="passage in passagesGeneres"
                :key="passage.id_ia"
                class="pt-3 border-t border-[#111111]/15 space-y-1"
              >
                <p
                  class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60"
                >
                  {{ passage.type_action }} ·
                  {{ formaterHorodatage(passage.insere_at) }} ·
                  {{ passage.tokens_used }} tokens
                </p>
                <p class="text-sm font-serif text-[#111111]/90 line-clamp-2">
                  {{ passage.content_after }}
                </p>
                <p class="font-mono text-[10px] uppercase tracking-wider">
                  <span v-if="passage.present" class="text-[#C4341C] font-bold">
                    Présent tel quel dans le document
                  </span>
                  <span v-else class="text-[#111111]/50">
                    Modifié depuis l'insertion
                  </span>
                </p>
              </li>
            </ul>
          </section>

          <!-- ÉDITEUR MARKDOWN -->
          <MarkdownEditor
            ref="markdownEditorRef"
            v-model="content"
            @input="handleEditorInput"
            @open-ia-panel="openIaPanel"
          />

          <!-- BOUTONS EN BAS -->
          <div
            class="mt-8 flex flex-col-reverse sm:flex-row justify-end items-stretch sm:items-center gap-4"
          >
            <button
              type="button"
              :disabled="isSaving"
              class="h-12 px-6 font-mono text-xs uppercase tracking-widest border border-[#111111] text-[#111111] hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors"
              @click="handleCancel"
            >
              Annuler
            </button>
            <button
              type="button"
              :disabled="isSaving || !isTitreValid"
              class="h-12 px-6 font-mono text-xs uppercase tracking-widest bg-[#111111] text-[#F4F1EA] border border-[#111111] hover:bg-[#C4341C] disabled:opacity-50 transition-colors shadow-[4px_4px_0px_0px_rgba(224,83,60,1)] hover:shadow-none"
              @click="handleSave"
            >
              {{ isSaving ? "Enregistrement…" : "Enregistrer" }}
            </button>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>
