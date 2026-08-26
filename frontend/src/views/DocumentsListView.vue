<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import documentService from "../services/documentService";
import type { DocumentItem } from "../types/document";
import { statusLabels, getStatusStyle } from "../utils/documentStatus";
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
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN CONTENT -->
    <main
      class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16"
    >
      <!-- EN-TÊTE PAGE -->
      <section
        class="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10 pb-6 border-b border-[#111111]/20"
      >
        <div>
          <span
            class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
          >
            [ Espace Personnel ]
          </span>
          <h1
            class="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#111111]"
          >
            Mes documents
          </h1>
        </div>

        <RouterLink
          to="/documents/nouveau"
          class="inline-flex items-center justify-center gap-2 h-12 px-6 bg-[#111111] hover:bg-[#E0533C] text-[#F4F1EA] font-mono text-xs uppercase tracking-widest transition-colors shadow-[4px_4px_0px_0px_rgba(224,83,60,1)] hover:shadow-none border border-[#111111]"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Nouveau document
        </RouterLink>
      </section>

      <!-- PANNEAU PRINCIPAL AVEC OMBRE NÉO-BRUTALISTE -->
      <section
        class="bg-[#FAF8F5] border-2 border-[#111111] shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
      >
        <!-- BARRE D'OUTILS ET RECHERCHE -->
        <div
          class="p-4 sm:p-6 border-b border-[#111111]/20 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-[#F4F1EA]/50"
        >
          <label class="relative flex-1 max-w-md flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4 absolute left-3.5 text-[#111111]/50 pointer-events-none"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Rechercher dans cette page..."
              aria-label="Rechercher un document"
              class="w-full h-11 pl-10 pr-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
            />
          </label>

          <p
            class="font-mono text-xs uppercase text-[#111111]/70 self-end sm:self-center"
          >
            {{ filteredItems.length }} / {{ total }} document(s)
          </p>
        </div>

        <!-- ALERTE ERREUR -->
        <div
          v-if="errorMessage"
          class="p-4 border-b border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold flex items-center gap-2"
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

        <!-- ÉTAT DE CHARGEMENT -->
        <div
          v-if="isLoading"
          class="p-12 text-center font-mono text-xs uppercase tracking-widest text-[#111111]/60 flex flex-col items-center gap-3"
        >
          <span
            class="w-6 h-6 border-2 border-[#111111]/20 border-t-[#E0533C] rounded-full animate-spin"
          ></span>
          Chargement de vos documents…
        </div>

        <template v-else>
          <!-- LISTE DES DOCUMENTS -->
          <div v-if="filteredItems.length" class="divide-y divide-[#111111]/10">
            <div
              v-for="document in filteredItems"
              :key="document.id_document"
              class="group flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 sm:p-6 hover:bg-[#F4F1EA] transition-colors"
            >
              <RouterLink
                :to="`/documents/${document.id_document}`"
                class="flex items-start gap-4 flex-1 w-full sm:w-auto mb-4 sm:mb-0"
              >
                <div
                  class="w-10 h-10 border border-[#111111] bg-[#FAF8F5] group-hover:bg-[#E0533C] group-hover:text-[#F4F1EA] flex items-center justify-center shrink-0 transition-colors"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="1.8"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M14 2v6h6"
                    />
                  </svg>
                </div>

                <div class="space-y-1">
                  <h3
                    class="font-bold text-base sm:text-lg text-[#111111] group-hover:text-[#E0533C] transition-colors"
                  >
                    {{ document.titre }}
                  </h3>
                  <div
                    class="font-mono text-xs text-[#111111]/60 flex flex-wrap items-center gap-2"
                  >
                    <span
                      class="font-mono text-[10px] uppercase font-bold px-2 py-0.5 tracking-wider"
                      :class="getStatusStyle(document.status)"
                    >
                      {{ statusLabels[document.status] }}
                    </span>
                    <span
                      class="uppercase tracking-wider font-semibold text-[#111111]/80"
                    >
                      [{{ formatLabels[document.format] ?? document.format }}]
                    </span>
                    <span>·</span>
                    <span
                      >Modifié le {{ formatDate(document.updated_at) }}</span
                    >
                  </div>
                </div>
              </RouterLink>

              <!-- BOUTON SUPPRIMER -->
              <button
                type="button"
                :disabled="deletingId === document.id_document"
                class="self-end sm:self-center font-mono text-xs uppercase tracking-wider px-3 py-1.5 border border-[#E0533C] text-[#E0533C] hover:bg-[#E0533C] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors shrink-0"
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

          <!-- ÉTAT VIDE -->
          <div v-else class="p-12 text-center space-y-4">
            <p class="font-serif text-lg text-[#111111]/80">
              {{
                searchQuery
                  ? "Aucun document ne correspond à cette recherche."
                  : "Vous n'avez pas encore de document."
              }}
            </p>
            <RouterLink
              v-if="!searchQuery"
              to="/documents/nouveau"
              class="inline-block font-mono text-xs uppercase tracking-widest text-[#E0533C] hover:underline underline-offset-4 font-bold"
            >
              Créer votre premier document →
            </RouterLink>
          </div>

          <!-- PAGINATION -->
          <div
            v-if="totalPages > 1"
            class="p-4 sm:p-6 border-t border-[#111111]/20 flex items-center justify-between bg-[#F4F1EA]/50"
          >
            <button
              type="button"
              :disabled="page === 1"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-[#111111] transition-colors"
              @click="goToPage(page - 1)"
            >
              ← Précédent
            </button>

            <span class="font-mono text-xs uppercase text-[#111111]/70">
              Page {{ page }} / {{ totalPages }}
            </span>

            <button
              type="button"
              :disabled="page === totalPages"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-[#111111] transition-colors"
              @click="goToPage(page + 1)"
            >
              Suivant →
            </button>
          </div>
        </template>
      </section>
    </main>
  </div>
</template>
