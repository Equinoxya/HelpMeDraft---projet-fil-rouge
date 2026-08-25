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

    // La zone contenteditable ne s'affiche (v-else) qu'une fois isLoading
    // repassé à false : il faut le faire AVANT le nextTick, sinon
    // editorRef.value est encore null et l'injection échoue en silence.
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
    // hors contexte d'édition ; on ignore silencieusement dans ce cas.
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
  <main class="editor-page">
    <div class="editor-shell">
      <!-- En-tête -->
      <div class="editor-topbar">
        <RouterLink to="/documents" class="back-link">
          ← Retour aux documents
        </RouterLink>

        <button
          v-if="isEditMode"
          type="button"
          class="delete-button"
          :disabled="isDeleting || isLoading"
          @click="handleDelete"
        >
          {{ isDeleting ? "Suppression…" : "Supprimer" }}
        </button>
      </div>

      <div class="editor-card">
        <p class="editor-eyebrow">
          {{ isEditMode ? "Édition du document" : "Nouveau document" }}
        </p>

        <div v-if="isLoading" class="loading-state">
          Chargement du document…
        </div>

        <template v-else>
          <div v-if="errorMessage" class="alert-error" role="alert">
            {{ errorMessage }}
          </div>

          <div v-if="savedNotice" class="alert-success" role="status">
            Document enregistré.
          </div>

          <!-- Titre -->
          <div class="form-group">
            <label for="titre" class="form-label">Titre du document</label>
            <input
              id="titre"
              v-model="titre"
              type="text"
              class="titre-input"
              placeholder="Ex. Contrat de location meublée"
              maxlength="255"
            />
          </div>

          <!-- Barre d'outils -->
          <div class="toolbar" role="toolbar" aria-label="Mise en forme">
            <button
              type="button"
              class="toolbar-btn"
              :class="{ active: activeFormats.bold }"
              title="Gras"
              @click="exec('bold')"
            >
              G
            </button>
            <button
              type="button"
              class="toolbar-btn italic"
              :class="{ active: activeFormats.italic }"
              title="Italique"
              @click="exec('italic')"
            >
              I
            </button>
            <button
              type="button"
              class="toolbar-btn underline"
              :class="{ active: activeFormats.underline }"
              title="Souligné"
              @click="exec('underline')"
            >
              S
            </button>

            <span class="toolbar-separator" aria-hidden="true"></span>

            <button
              type="button"
              class="toolbar-btn"
              title="Titre 1"
              @click="exec('formatBlock', '<h1>')"
            >
              H1
            </button>
            <button
              type="button"
              class="toolbar-btn"
              title="Titre 2"
              @click="exec('formatBlock', '<h2>')"
            >
              H2
            </button>
            <button
              type="button"
              class="toolbar-btn"
              title="Paragraphe"
              @click="exec('formatBlock', '<p>')"
            >
              P
            </button>

            <span class="toolbar-separator" aria-hidden="true"></span>

            <button
              type="button"
              class="toolbar-btn"
              title="Liste à puces"
              @click="exec('insertUnorderedList')"
            >
              • Liste
            </button>
            <button
              type="button"
              class="toolbar-btn"
              title="Liste numérotée"
              @click="exec('insertOrderedList')"
            >
              1. Liste
            </button>
            <button
              type="button"
              class="toolbar-btn"
              title="Insérer un lien"
              @click="insertLink"
            >
              Lien
            </button>

            <span class="toolbar-separator" aria-hidden="true"></span>

            <button
              type="button"
              class="toolbar-btn"
              title="Annuler"
              @click="exec('undo')"
            >
              ↺
            </button>
            <button
              type="button"
              class="toolbar-btn"
              title="Rétablir"
              @click="exec('redo')"
            >
              ↻
            </button>
          </div>

          <!-- Zone d'édition -->
          <div
            ref="editorRef"
            class="editor-zone"
            contenteditable="true"
            role="textbox"
            aria-multiline="true"
            aria-label="Contenu du document"
            @keyup="updateActiveFormats"
            @mouseup="updateActiveFormats"
          ></div>

          <!-- Actions -->
          <div class="editor-actions">
            <button
              type="button"
              class="cancel-button"
              :disabled="isSaving"
              @click="handleCancel"
            >
              Annuler
            </button>
            <button
              type="button"
              class="save-button"
              :disabled="isSaving || !isTitreValid"
              @click="handleSave"
            >
              {{ isSaving ? "Enregistrement…" : "Enregistrer" }}
            </button>
          </div>
        </template>
      </div>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

.editor-page {
  min-height: calc(100vh - 72px);
  padding: 3rem max(1.5rem, calc((100vw - 1000px) / 2)) 5rem;
  background:
    radial-gradient(
      circle at 12% 100%,
      rgba(76, 122, 115, 0.2),
      transparent 30%
    ),
    radial-gradient(
      circle at 88% 0%,
      rgba(201, 162, 39, 0.12),
      transparent 28%
    ),
    #16233a;
  color: #efeae0;
  font-family: "Inter", sans-serif;
}

.editor-shell {
  max-width: 900px;
  margin: 0 auto;
}

.editor-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.back-link {
  font-size: 0.86rem;
  font-weight: 500;
  color: #c9a227;
  text-decoration: none;
}

.back-link:hover {
  color: #efeae0;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.delete-button {
  padding: 0.55rem 1rem;
  border: 1px solid rgba(217, 119, 87, 0.5);
  border-radius: 5px;
  background: rgba(217, 119, 87, 0.1);
  color: #d97757;
  font-family: "Inter", sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.delete-button:hover:not(:disabled) {
  background: rgba(217, 119, 87, 0.2);
  border-color: #d97757;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.editor-card {
  padding: 2.5rem;
  border: 1px solid rgba(239, 234, 224, 0.25);
  border-radius: 10px;
  background: #efeae0;
  color: #16233a;
  box-shadow:
    0 35px 90px rgba(5, 12, 24, 0.46),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.editor-eyebrow {
  margin: 0 0 1.5rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #4c7a73;
}

.loading-state {
  padding: 3rem 0;
  text-align: center;
  color: rgba(22, 35, 58, 0.6);
  font-size: 0.9rem;
}

.alert-error,
.alert-success {
  margin-bottom: 1.5rem;
  padding: 0.85rem 1rem;
  border-left: 3px solid;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  line-height: 1.5;
}

.alert-error {
  border-color: #d97757;
  background: rgba(217, 119, 87, 0.1);
  color: #983f29;
}

.alert-success {
  border-color: #4c7a73;
  background: rgba(76, 122, 115, 0.1);
  color: #2f5a53;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  margin-bottom: 1.75rem;
}

.form-label {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(22, 35, 58, 0.72);
}

.titre-input {
  width: 100%;
  height: 3.1rem;
  padding: 0 1rem;
  border: 1px solid rgba(22, 35, 58, 0.2);
  border-radius: 5px;
  outline: none;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Fraunces", serif;
  font-size: 1.15rem;
  color: #16233a;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.titre-input:focus {
  border-color: #4c7a73;
  box-shadow: 0 0 0 3px rgba(76, 122, 115, 0.14);
}

/* Barre d'outils */

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem;
  margin-bottom: 0;
  border: 1px solid rgba(22, 35, 58, 0.15);
  border-bottom: none;
  border-radius: 5px 5px 0 0;
  background: rgba(22, 35, 58, 0.04);
}

.toolbar-btn {
  min-width: 2.1rem;
  height: 2.1rem;
  padding: 0 0.6rem;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: #16233a;
  cursor: pointer;
  transition:
    background-color 150ms ease,
    border-color 150ms ease;
}

.toolbar-btn.italic {
  font-style: italic;
}

.toolbar-btn.underline {
  text-decoration: underline;
}

.toolbar-btn:hover {
  background: rgba(76, 122, 115, 0.12);
}

.toolbar-btn.active {
  border-color: #4c7a73;
  background: rgba(76, 122, 115, 0.18);
  color: #2f5a53;
}

.toolbar-separator {
  width: 1px;
  height: 1.4rem;
  background: rgba(22, 35, 58, 0.15);
}

/* Zone d'édition */

.editor-zone {
  min-height: 360px;
  padding: 1.5rem;
  border: 1px solid rgba(22, 35, 58, 0.2);
  border-radius: 0 0 5px 5px;
  background: rgba(255, 255, 255, 0.6);
  font-family: "Inter", sans-serif;
  font-size: 0.98rem;
  line-height: 1.75;
  color: #16233a;
  outline: none;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.editor-zone:focus {
  border-color: #4c7a73;
  box-shadow: 0 0 0 3px rgba(76, 122, 115, 0.14);
}

.editor-zone :deep(h1) {
  margin: 0 0 0.75rem;
  font-family: "Fraunces", serif;
  font-size: 1.75rem;
  font-weight: 600;
}

.editor-zone :deep(h2) {
  margin: 0 0 0.6rem;
  font-family: "Fraunces", serif;
  font-size: 1.4rem;
  font-weight: 600;
}

.editor-zone :deep(p) {
  margin: 0 0 0.9rem;
}

.editor-zone :deep(ul),
.editor-zone :deep(ol) {
  margin: 0 0 0.9rem;
  padding-left: 1.5rem;
}

.editor-zone :deep(a) {
  color: #4c7a73;
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* Actions */

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-button,
.save-button {
  min-height: 3rem;
  padding: 0 1.6rem;
  border-radius: 5px;
  font-family: "Inter", sans-serif;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    transform 180ms ease;
}

.cancel-button {
  border: 1px solid rgba(22, 35, 58, 0.2);
  background: transparent;
  color: rgba(22, 35, 58, 0.7);
}

.cancel-button:hover:not(:disabled) {
  border-color: rgba(22, 35, 58, 0.4);
  background: rgba(22, 35, 58, 0.05);
}

.save-button {
  border: 1px solid #16233a;
  background: #16233a;
  color: #efeae0;
}

.save-button:hover:not(:disabled) {
  border-color: #c9a227;
  background: #c9a227;
  color: #16233a;
  transform: translateY(-2px);
}

.save-button:disabled,
.cancel-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 640px) {
  .editor-card {
    padding: 1.75rem 1.25rem;
  }

  .editor-actions {
    flex-direction: column-reverse;
  }

  .cancel-button,
  .save-button {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .save-button,
  .toolbar-btn,
  .titre-input,
  .editor-zone {
    transition: none;
  }
}
</style>
