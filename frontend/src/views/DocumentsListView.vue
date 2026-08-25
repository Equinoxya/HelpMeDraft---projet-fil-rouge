<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import documentService from "../services/documentService";
import type { DocumentItem } from "../types/document";

const PER_PAGE = 10;

const items = ref<DocumentItem[]>([]);
const total = ref(0);
const page = ref(1);

const searchQuery = ref("");
const isLoading = ref(false);
const errorMessage = ref("");
const deletingId = ref<string | null>(null);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / PER_PAGE)),
);

const filteredItems = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return items.value;

  return items.value.filter((document) =>
    document.titre.toLowerCase().includes(query),
  );
});

const formatLabels: Record<string, string> = {
  markdown: "Markdown",
  wysiwyg: "Riche",
};

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function fetchDocuments() {
  isLoading.value = true;
  errorMessage.value = "";

  try {
    const response = await documentService.list({
      page: page.value,
      per_page: PER_PAGE,
    });
    items.value = response.items;
    total.value = response.total;
  } catch {
    errorMessage.value =
      "Impossible de charger vos documents. Réessayez plus tard.";
  } finally {
    isLoading.value = false;
  }
}

function goToPage(targetPage: number) {
  if (targetPage < 1 || targetPage > totalPages.value) return;
  page.value = targetPage;
  searchQuery.value = "";
  fetchDocuments();
}

async function handleDelete(document: DocumentItem) {
  const confirmed = window.confirm(
    `Supprimer définitivement « ${document.titre} » ? Cette action est irréversible.`,
  );
  if (!confirmed) return;

  deletingId.value = document.id_document;
  errorMessage.value = "";

  try {
    await documentService.remove(document.id_document);

    // Décrément intelligent : si on supprime le dernier document d'une page
    // (hors première page), on recule d'une page plutôt que d'afficher une
    // page vide.
    if (items.value.length === 1 && page.value > 1) {
      page.value -= 1;
    }

    await fetchDocuments();
  } catch {
    errorMessage.value = "La suppression a échoué. Réessayez plus tard.";
  } finally {
    deletingId.value = null;
  }
}

onMounted(fetchDocuments);
</script>

<template>
  <main class="documents-page">
    <div class="documents-shell">
      <!-- En-tête -->
      <section class="page-header">
        <div>
          <p class="page-eyebrow">Espace personnel</p>
          <h1>Mes documents</h1>
        </div>

        <RouterLink to="/documents/nouveau" class="primary-action">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              d="M12 5v14M5 12h14"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
          </svg>
          Nouveau document
        </RouterLink>
      </section>

      <!-- Panneau liste -->
      <section class="documents-panel">
        <div class="documents-toolbar">
          <label class="search-field">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              aria-hidden="true"
            >
              <circle cx="11" cy="11" r="7" stroke-width="1.8" />
              <path
                d="m20 20-3.5-3.5"
                stroke-linecap="round"
                stroke-width="1.8"
              />
            </svg>

            <input
              v-model="searchQuery"
              type="search"
              placeholder="Rechercher dans cette page"
              aria-label="Rechercher un document"
            />
          </label>

          <p class="results-count">
            {{ filteredItems.length }} / {{ total }} document(s)
          </p>
        </div>

        <div v-if="errorMessage" class="alert-error" role="alert">
          {{ errorMessage }}
        </div>

        <div v-if="isLoading" class="loading-state">
          Chargement de vos documents…
        </div>

        <template v-else>
          <div v-if="filteredItems.length" class="documents-list">
            <div
              v-for="document in filteredItems"
              :key="document.id_document"
              class="document-row"
            >
              <RouterLink
                :to="`/documents/${document.id_document}`"
                class="document-link"
              >
                <div class="document-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.8"
                    />
                    <path
                      d="M14 2v6h6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.8"
                    />
                  </svg>
                </div>

                <div class="document-main">
                  <h3>{{ document.titre }}</h3>

                  <div class="document-meta">
                    <span>{{
                      formatLabels[document.format] ?? document.format
                    }}</span>
                    <span aria-hidden="true">·</span>
                    <span
                      >Modifié le {{ formatDate(document.updated_at) }}</span
                    >
                  </div>
                </div>
              </RouterLink>

              <button
                type="button"
                class="delete-button"
                :disabled="deletingId === document.id_document"
                @click="handleDelete(document)"
              >
                {{
                  deletingId === document.id_document
                    ? "Suppression…"
                    : "Supprimer"
                }}
              </button>
            </div>
          </div>

          <div v-else class="empty-state">
            <p class="empty-title">
              {{
                searchQuery
                  ? "Aucun document ne correspond à cette recherche."
                  : "Vous n'avez pas encore de document."
              }}
            </p>
            <RouterLink
              v-if="!searchQuery"
              to="/documents/nouveau"
              class="empty-action"
            >
              Créer votre premier document →
            </RouterLink>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button
              type="button"
              class="page-button"
              :disabled="page === 1"
              @click="goToPage(page - 1)"
            >
              ← Précédent
            </button>

            <span class="page-indicator">
              Page {{ page }} / {{ totalPages }}
            </span>

            <button
              type="button"
              class="page-button"
              :disabled="page === totalPages"
              @click="goToPage(page + 1)"
            >
              Suivant →
            </button>
          </div>
        </template>
      </section>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

.documents-page {
  min-height: calc(100vh - 72px);
  padding: 4rem max(1.5rem, calc((100vw - 1100px) / 2)) 6rem;
  background:
    radial-gradient(
      circle at 10% 5%,
      rgba(76, 122, 115, 0.2),
      transparent 25rem
    ),
    #16233a;
  color: #efeae0;
  font-family: "Inter", sans-serif;
}

.documents-shell {
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 2.5rem;
}

.page-eyebrow {
  margin: 0 0 0.75rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #c9a227;
}

.page-header h1 {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: clamp(2.2rem, 5vw, 3.4rem);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.04em;
}

.primary-action {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  min-height: 3.1rem;
  padding: 0 1.3rem;
  border: 1px solid #c9a227;
  border-radius: 5px;
  background: #c9a227;
  color: #16233a;
  font-size: 0.86rem;
  font-weight: 600;
  text-decoration: none;
  transition:
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.primary-action svg {
  width: 18px;
  height: 18px;
}

.primary-action:hover {
  background: #efeae0;
  box-shadow: 0 14px 30px rgba(5, 12, 24, 0.25);
  transform: translateY(-2px);
}

.documents-panel {
  overflow: hidden;
  border: 1px solid rgba(22, 35, 58, 0.12);
  border-radius: 8px;
  background: #efeae0;
  color: #16233a;
  box-shadow: 0 30px 70px rgba(5, 12, 24, 0.2);
}

.documents-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(22, 35, 58, 0.1);
}

.results-count {
  margin: 0;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.66rem;
  color: rgba(22, 35, 58, 0.45);
  white-space: nowrap;
}

.search-field {
  display: flex;
  align-items: center;
  width: min(100%, 360px);
  padding: 0 0.9rem;
  border: 1px solid rgba(22, 35, 58, 0.16);
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.4);
}

.search-field:focus-within {
  border-color: #4c7a73;
  box-shadow: 0 0 0 3px rgba(76, 122, 115, 0.12);
}

.search-field svg {
  width: 18px;
  height: 18px;
  color: rgba(22, 35, 58, 0.42);
  flex-shrink: 0;
}

.search-field input {
  width: 100%;
  height: 2.8rem;
  padding: 0 0.7rem;
  border: none;
  outline: none;
  background: transparent;
  font: inherit;
  color: #16233a;
}

.search-field input::placeholder {
  color: rgba(22, 35, 58, 0.38);
}

.alert-error {
  margin: 1.25rem 1.5rem 0;
  padding: 0.85rem 1rem;
  border-left: 3px solid #d97757;
  background: rgba(217, 119, 87, 0.1);
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  color: #983f29;
}

.loading-state {
  padding: 4rem 1.5rem;
  text-align: center;
  color: rgba(22, 35, 58, 0.55);
  font-size: 0.9rem;
}

.documents-list {
  display: flex;
  flex-direction: column;
}

.document-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(22, 35, 58, 0.08);
}

.document-row:last-child {
  border-bottom: none;
}

.document-link {
  display: grid;
  flex: 1;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 1rem;
  min-height: 92px;
  padding: 1.2rem 0 1.2rem 1.5rem;
  color: #16233a;
  text-decoration: none;
  transition: background-color 160ms ease;
}

.document-row:hover .document-link {
  background: rgba(76, 122, 115, 0.07);
}

.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 5px;
  background: rgba(22, 35, 58, 0.07);
  color: #4c7a73;
}

.document-icon svg {
  width: 20px;
  height: 20px;
}

.document-main h3 {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: 1rem;
  font-weight: 600;
}

.document-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.35rem;
  font-size: 0.72rem;
  color: rgba(22, 35, 58, 0.48);
}

.delete-button {
  flex: 0 0 auto;
  margin-right: 1.5rem;
  padding: 0.55rem 0.9rem;
  border: 1px solid rgba(217, 119, 87, 0.4);
  border-radius: 5px;
  background: transparent;
  color: #a34d37;
  font-family: "Inter", sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition:
    background-color 160ms ease,
    border-color 160ms ease;
}

.delete-button:hover:not(:disabled) {
  background: rgba(217, 119, 87, 0.11);
  border-color: #d97757;
}

.delete-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.empty-state {
  padding: 4rem 1.5rem;
  text-align: center;
}

.empty-title {
  margin: 0 0 1rem;
  font-family: "Fraunces", serif;
  font-size: 1.35rem;
  color: #16233a;
}

.empty-action {
  color: #4c7a73;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
}

.empty-action:hover {
  text-decoration: underline;
  text-underline-offset: 4px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(22, 35, 58, 0.1);
}

.page-button {
  padding: 0.55rem 1rem;
  border: 1px solid rgba(22, 35, 58, 0.2);
  border-radius: 5px;
  background: transparent;
  color: #16233a;
  font-family: "Inter", sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 160ms ease;
}

.page-button:hover:not(:disabled) {
  background: rgba(76, 122, 115, 0.1);
}

.page-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.72rem;
  color: rgba(22, 35, 58, 0.55);
}

@media (max-width: 640px) {
  .documents-page {
    padding: 2.8rem 1rem 4rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }

  .primary-action {
    width: 100%;
  }

  .documents-toolbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-field {
    width: 100%;
  }

  .document-row {
    flex-direction: column;
    align-items: stretch;
  }

  .document-link {
    padding: 1.2rem 1.5rem;
  }

  .delete-button {
    margin: 0 1.5rem 1.2rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .primary-action,
  .document-link,
  .delete-button,
  .page-button {
    transition: none;
  }
}
</style>
