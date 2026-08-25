<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import documentService from "../services/documentService";

const route = useRoute();
const router = useRouter();

const documentId = computed(() =>
  typeof route.params.id === "string" ? route.params.id : null,
);
const isEditMode = computed(() => documentId.value !== null);

const titre = ref("");
const editorRef = ref<HTMLDivElement | null>(null);

const isLoading = ref(false);
const isSaving = ref(false);
const isDeleting = ref(false);
const errorMessage = ref("");
const savedNotice = ref(false);
let savedNoticeTimeout: ReturnType<typeof setTimeout> | null = null;

const activeFormats = ref({
  bold: false,
  italic: false,
  underline: false,
});

const isTitreValid = computed(() => {
  const trimmed = titre.value.trim();
  return trimmed.length > 0 && trimmed.length <= 255;
});

async function loadDocument(id: string) {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const document = await documentService.get(id);
    titre.value = document.titre;

    isLoading.value = false;
    await nextTick();
    if (editorRef.value) {
      editorRef.value.innerHTML = document.content ?? "";
    }
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
  document.addEventListener("selectionchange", updateActiveFormats);
});

onBeforeUnmount(() => {
  document.removeEventListener("selectionchange", updateActiveFormats);
  if (savedNoticeTimeout) clearTimeout(savedNoticeTimeout);
});

function updateActiveFormats() {
  if (!editorRef.value || document.activeElement !== editorRef.value) return;

  try {
    activeFormats.value = {
      bold: document.queryCommandState("bold"),
      italic: document.queryCommandState("italic"),
      underline: document.queryCommandState("underline"),
    };
  } catch {
    // queryCommandState peut lever une exception sur certains navigateurs
  }
}

function exec(command: string, value?: string) {
  editorRef.value?.focus();
  document.execCommand(command, false, value);
  updateActiveFormats();
}

function insertLink() {
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) {
    errorMessage.value =
      "Sélectionnez d'abord le texte auquel ajouter un lien.";
    return;
  }

  const url = window.prompt("Adresse du lien (https://...)");
  if (!url) return;

  exec("createLink", url);
}

async function handleSave() {
  errorMessage.value = "";

  if (!isTitreValid.value) {
    errorMessage.value = "Le titre est requis (255 caractères maximum).";
    return;
  }

  isSaving.value = true;

  const payload = {
    titre: titre.value.trim(),
    content: editorRef.value?.innerHTML ?? "",
    format: "wysiwyg" as const,
  };

  try {
    if (isEditMode.value && documentId.value) {
      await documentService.update(documentId.value, payload);
    } else {
      const created = await documentService.create(payload);
      router.replace(`/documents/${created.id_document}`);
    }

    savedNotice.value = true;
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
      <!-- BARRE SUPÉRIEURE DE NAVIGATION ET SUPPRESSION -->
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

      <!-- CARTE ÉDITEUR NÉO-BRUTALISTE -->
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

          <!-- CHAMP TITRE -->
          <div class="mb-6 space-y-2">
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

          <!-- BARRE D'OUTILS DE MISE EN FORME -->
          <div
            class="bg-[#F4F1EA] border border-[#111111] border-b-0 p-2 flex flex-wrap items-center gap-1"
            role="toolbar"
            aria-label="Mise en forme"
          >
            <button
              type="button"
              title="Gras"
              :class="[
                'h-9 px-3 font-mono text-xs font-bold border border-transparent transition-colors',
                activeFormats.bold
                  ? 'bg-[#111111] text-[#F4F1EA]'
                  : 'text-[#111111] hover:bg-[#111111]/10',
              ]"
              @click="exec('bold')"
            >
              G
            </button>
            <button
              type="button"
              title="Italique"
              :class="[
                'h-9 px-3 font-mono text-xs font-bold italic border border-transparent transition-colors',
                activeFormats.italic
                  ? 'bg-[#111111] text-[#F4F1EA]'
                  : 'text-[#111111] hover:bg-[#111111]/10',
              ]"
              @click="exec('italic')"
            >
              I
            </button>
            <button
              type="button"
              title="Souligné"
              :class="[
                'h-9 px-3 font-mono text-xs font-bold underline border border-transparent transition-colors',
                activeFormats.underline
                  ? 'bg-[#111111] text-[#F4F1EA]'
                  : 'text-[#111111] hover:bg-[#111111]/10',
              ]"
              @click="exec('underline')"
            >
              S
            </button>

            <span
              class="w-[1px] h-6 bg-[#111111]/20 mx-1"
              aria-hidden="true"
            ></span>

            <button
              type="button"
              title="Titre 1"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('formatBlock', '<h1>')"
            >
              H1
            </button>
            <button
              type="button"
              title="Titre 2"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('formatBlock', '<h2>')"
            >
              H2
            </button>
            <button
              type="button"
              title="Paragraphe"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('formatBlock', '<p>')"
            >
              P
            </button>

            <span
              class="w-[1px] h-6 bg-[#111111]/20 mx-1"
              aria-hidden="true"
            ></span>

            <button
              type="button"
              title="Liste à puces"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('insertUnorderedList')"
            >
              • Liste
            </button>
            <button
              type="button"
              title="Liste numérotée"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('insertOrderedList')"
            >
              1. Liste
            </button>
            <button
              type="button"
              title="Insérer un lien"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="insertLink"
            >
              Lien
            </button>

            <span
              class="w-[1px] h-6 bg-[#111111]/20 mx-1"
              aria-hidden="true"
            ></span>

            <button
              type="button"
              title="Annuler"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('undo')"
            >
              ↺
            </button>
            <button
              type="button"
              title="Rétablir"
              class="h-9 px-3 font-mono text-xs font-bold text-[#111111] hover:bg-[#111111]/10 transition-colors"
              @click="exec('redo')"
            >
              ↻
            </button>
          </div>

          <!-- ZONE D'ÉDITION RICHE (WYSIWYG) -->
          <div
            ref="editorRef"
            contenteditable="true"
            role="textbox"
            aria-multiline="true"
            aria-label="Contenu du document"
            class="min-h-[360px] p-6 bg-[#F4F1EA] border border-[#111111] text-[#111111] font-sans text-base leading-relaxed focus:outline-none focus:ring-2 focus:ring-[#E0533C] [&_h1]:font-serif [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:mb-4 [&_h2]:font-serif [&_h2]:text-xl [&_h2]:font-bold [&_h2]:mb-3 [&_p]:mb-4 [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:mb-4 [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:mb-4 [&_a]:text-[#E0533C] [&_a]:underline"
            @keyup="updateActiveFormats"
            @mouseup="updateActiveFormats"
          ></div>

          <!-- ACTIONS EN BAS -->
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
