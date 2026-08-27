<script setup lang="ts">
import {
  ref,
  computed,
  watch,
  onMounted,
  onBeforeUnmount,
  nextTick,
} from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import documentService from "../services/documentService";
import type { DocumentStatus } from "../types/document";
import dossierService from "../services/dossierService";
import type { DossierItem } from "../types/dossier";
import iaService from "../services/iaService";
import { type IaTypeAction, type IaScope } from "../types/ia";
import MarkdownEditor from "../components/MarkdownEditor.vue";

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
  iaError.value = "";
  showIaPanel.value = true;
}

function closeIaPanel() {
  showIaPanel.value = false;
  iaResult.value = null;
  iaError.value = "";
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

  try {
    const result = await iaService.generer(documentId.value, {
      type_action: iaTypeAction.value,
      scope: iaScope.value,
      contenu,
      instructions: iaInstructions.value.trim() || undefined,
    });
    iaResult.value = result.content_after;
  } catch (err: any) {
    iaError.value =
      err.response?.data?.error ?? "L'assistant IA n'a pas pu répondre.";
  } finally {
    iaLoading.value = false;
  }
}

function applyIaResult() {
  if (!iaResult.value) return;

  if (iaScope.value === "selection") {
    const selection = window.getSelection();
    if (selection && !selection.isCollapsed) {
      const range = selection.getRangeAt(0);
      const start = content.value.substring(0, range.startOffset);
      const end = content.value.substring(range.endOffset);
      content.value = start + iaResult.value + end;
    }
  } else {
    content.value = iaResult.value;
  }

  nextTick(() => {
    markdownEditorRef.value?.focus();
  });
  scheduleAutoSave();
  closeIaPanel();
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
    return;
  } catch (err: any) {
    if (err.response?.status === 404) {
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
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error ??
      "Une erreur est survenue lors de l'enregistrement.";
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
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN CONTENT -->
    <main
      class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16"
    >
      <!-- BARRE SUPÉRIEURE -->
      <div class="flex items-center justify-between gap-4 mb-8">
        <RouterLink
          to="/documents"
          class="font-mono text-xs uppercase tracking-wider text-[#111111] hover:text-[#E0533C] transition-colors font-bold inline-flex items-center gap-2"
        >
          ← Retour aux documents
        </RouterLink>

        <button
          v-if="isEditMode"
          type="button"
          :disabled="isDeleting || isLoading"
          class="font-mono text-xs uppercase tracking-wider px-4 py-2 border border-[#E0533C] text-[#E0533C] hover:bg-[#E0533C] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors"
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
          class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-4"
        >
          [ {{ isEditMode ? "Mode Édition" : "Nouveau Brouillon" }} ]
        </span>

        <!-- CHARGEMENT -->
        <div
          v-if="isLoading"
          class="p-12 text-center font-mono text-xs uppercase tracking-widest text-[#111111]/60 flex flex-col items-center gap-3"
        >
          <span
            class="w-6 h-6 border-2 border-[#111111]/20 border-t-[#E0533C] rounded-full animate-spin"
          ></span>
          Chargement du document…
        </div>

        <template v-else>
          <!-- ALERTE ERREUR -->
          <div
            v-if="errorMessage"
            class="mb-6 p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold flex items-center gap-2"
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
              class="w-4 h-4 text-[#E0533C] shrink-0"
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
                placeholder="Ex. Contrat de location meublée"
                maxlength="255"
                class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-serif text-lg text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C] transition-shadow"
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
                class="h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs uppercase tracking-wider text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
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
                class="h-12 px-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs uppercase tracking-wider text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
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
              class="font-mono text-[10px] uppercase tracking-wider text-[#E0533C] font-bold"
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
                class="font-mono text-xs uppercase tracking-widest font-bold text-[#E0533C]"
              >
                [ Assistant IA — Ollama ]
              </span>
              <button
                type="button"
                class="font-mono text-xs text-[#111111]/60 hover:text-[#E0533C]"
                @click="closeIaPanel"
              >
                ✕ Fermer
              </button>
            </div>

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
              class="font-mono text-xs text-[#E0533C] font-bold"
            >
              {{ iaError }}
            </div>

            <button
              type="button"
              :disabled="iaLoading"
              class="h-10 px-5 bg-[#111111] text-[#F4F1EA] font-mono text-xs uppercase tracking-wider hover:bg-[#E0533C] disabled:opacity-50 transition-colors"
              @click="handleGenerateIa"
            >
              {{ iaLoading ? "Génération en cours…" : "Générer" }}
            </button>

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
              <div class="flex gap-3">
                <button
                  type="button"
                  class="h-9 px-4 bg-[#111111] text-[#F4F1EA] font-mono text-xs uppercase hover:bg-[#E0533C] transition-colors"
                  @click="applyIaResult"
                >
                  Insérer
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

          <!-- ÉDITEUR MARKDOWN -->
          <MarkdownEditor
            ref="markdownEditorRef"
            v-model="content"
            @input="handleEditorInput"
            @openIaPanel="openIaPanel"
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
              class="h-12 px-6 font-mono text-xs uppercase tracking-widest bg-[#111111] text-[#F4F1EA] border border-[#111111] hover:bg-[#E0533C] disabled:opacity-50 transition-colors shadow-[4px_4px_0px_0px_rgba(224,83,60,1)] hover:shadow-none"
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
