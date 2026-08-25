<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";
import { useAuthStore } from "../stores/auth";

type DocumentStatus = "Brouillon" | "Terminé" | "À relire";

interface RecentDocument {
  id: number;
  title: string;
  type: string;
  updatedAt: string;
  status: DocumentStatus;
}

const authStore = useAuthStore();
const searchQuery = ref("");

const userFirstname = computed(() => {
  return authStore.user?.firstname || "Ophélie";
});

const stats = [
  {
    label: "Documents créés",
    value: "12",
    detail: "+3 ce mois-ci",
  },
  {
    label: "Brouillons",
    value: "04",
    detail: "À terminer",
  },
  {
    label: "Documents finalisés",
    value: "08",
    detail: "Prêts à être exportés",
  },
];

const quickActions = [
  {
    title: "Créer un document",
    description:
      "Décrivez votre besoin et laissez l'IA préparer un premier brouillon.",
    to: "/documents/nouveau",
    icon: "document",
  },
  {
    title: "Utiliser un modèle",
    description: "Partez d'une structure existante adaptée à votre situation.",
    to: "/modeles",
    icon: "template",
  },
  {
    title: "Importer un document",
    description:
      "Ajoutez un document existant pour le modifier ou l'améliorer.",
    to: "/documents/importer",
    icon: "import",
  },
];

const recentDocuments = ref<RecentDocument[]>([
  {
    id: 1,
    title: "Contrat de location meublée",
    type: "Contrat",
    updatedAt: "Aujourd'hui à 14:32",
    status: "Brouillon",
  },
  {
    id: 2,
    title: "Mise en demeure pour facture impayée",
    type: "Courrier",
    updatedAt: "29 juillet 2026",
    status: "À relire",
  },
  {
    id: 3,
    title: "Attestation d'hébergement",
    type: "Attestation",
    updatedAt: "26 juillet 2026",
    status: "Terminé",
  },
  {
    id: 4,
    title: "Lettre de résiliation",
    type: "Courrier",
    updatedAt: "22 juillet 2026",
    status: "Terminé",
  },
]);

const filteredDocuments = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();

  if (!query) {
    return recentDocuments.value;
  }

  return recentDocuments.value.filter((document) => {
    return (
      document.title.toLowerCase().includes(query) ||
      document.type.toLowerCase().includes(query) ||
      document.status.toLowerCase().includes(query)
    );
  });
});

function getStatusStyle(status: DocumentStatus) {
  switch (status) {
    case "Brouillon":
      return "bg-[#111111] text-[#F4F1EA]";
    case "À relire":
      return "bg-[#E0533C] text-[#F4F1EA]";
    case "Terminé":
      return "bg-[#F4F1EA] text-[#111111] border border-[#111111]";
  }
}
</script>

<template>
  <main
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased pb-24"
  >
    <div class="max-w-7xl mx-auto px-6 lg:px-12 pt-12 md:pt-16">
      <!-- EN-TÊTE DASHBOARD -->
      <header
        class="flex flex-col md:flex-row md:items-end justify-between gap-8 pb-12 border-b-2 border-[#111111]"
      >
        <div>
          <p
            class="font-mono text-xs uppercase tracking-widest text-[#E0533C] font-bold mb-3"
          >
            // ESPACE PERSONNEL
          </p>
          <h1
            class="font-serif text-4xl sm:text-6xl font-normal tracking-tight"
          >
            Bonjour, {{ userFirstname }}.
          </h1>
          <p
            class="mt-4 text-base md:text-lg text-[#111111]/70 max-w-2xl leading-relaxed"
          >
            Retrouvez vos documents, reprenez vos brouillons en cours et amorcez
            vos nouvelles rédactions.
          </p>
        </div>

        <RouterLink
          to="/documents/nouveau"
          class="inline-flex items-center justify-center gap-3 bg-[#111111] text-[#F4F1EA] px-6 py-4 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            class="w-4 h-4"
            aria-hidden="true"
          >
            <path
              d="M12 5v14M5 12h14"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
            />
          </svg>
          Nouveau document
        </RouterLink>
      </header>

      <!-- STATISTIQUES (GRILLE BRUTALISTE) -->
      <section
        class="grid grid-cols-1 md:grid-cols-3 gap-6 my-12"
        aria-label="Résumé du compte"
      >
        <article
          v-for="stat in stats"
          :key="stat.label"
          class="p-6 bg-[#FAF8F5] border-2 border-[#111111] shadow-[4px_4px_0px_0px_#111111]"
        >
          <p
            class="font-mono text-[11px] uppercase tracking-widest text-[#111111]/60 mb-2"
          >
            {{ stat.label }}
          </p>
          <p class="font-serif text-5xl font-normal text-[#111111] my-1">
            {{ stat.value }}
          </p>
          <p class="font-mono text-xs text-[#E0533C] font-bold mt-3">
            ↑ {{ stat.detail }}
          </p>
        </article>
      </section>

      <!-- SECTION 01 : ACTIONS RAPIDES -->
      <section class="mt-16">
        <div class="flex items-center gap-4 mb-8">
          <span
            class="font-mono text-xs font-bold bg-[#111111] text-[#F4F1EA] px-2.5 py-1"
            >01</span
          >
          <h2 class="font-serif text-2xl md:text-3xl font-normal">
            Que souhaitez-vous faire ?
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <RouterLink
            v-for="action in quickActions"
            :key="action.title"
            :to="action.to"
            class="group relative flex flex-col justify-between p-8 bg-[#FAF8F5] border-2 border-[#111111] shadow-[6px_6px_0px_0px_#111111] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_#111111] transition-all focus-visible:outline-2 focus-visible:outline-black"
          >
            <div>
              <div
                class="w-12 h-12 border-2 border-[#111111] bg-[#F4F1EA] flex items-center justify-center text-[#111111] group-hover:bg-[#E0533C] group-hover:text-[#F4F1EA] transition-colors mb-6"
              >
                <svg
                  v-if="action.icon === 'document'"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  class="w-6 h-6"
                  aria-hidden="true"
                >
                  <path
                    d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                  <path
                    d="M14 2v6h6M9 13h6M9 17h6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                </svg>

                <svg
                  v-else-if="action.icon === 'template'"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  class="w-6 h-6"
                  aria-hidden="true"
                >
                  <rect
                    x="3"
                    y="3"
                    width="18"
                    height="18"
                    rx="1"
                    stroke-width="2"
                  />
                  <path
                    d="M3 9h18M9 21V9"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                </svg>

                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  class="w-6 h-6"
                  aria-hidden="true"
                >
                  <path
                    d="M12 3v12M7 8l5-5 5 5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                  <path
                    d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                </svg>
              </div>

              <h3 class="font-serif text-xl font-normal mb-3 text-[#111111]">
                {{ action.title }}
              </h3>
              <p class="text-sm text-[#111111]/70 leading-relaxed">
                {{ action.description }}
              </p>
            </div>

            <div
              class="mt-8 flex justify-end font-mono text-lg font-bold text-[#111111] group-hover:text-[#E0533C] transition-colors"
            >
              →
            </div>
          </RouterLink>
        </div>
      </section>

      <!-- SECTION 02 : DOCUMENTS RÉCENTS -->
      <section class="mt-20">
        <div
          class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8"
        >
          <div class="flex items-center gap-4">
            <span
              class="font-mono text-xs font-bold bg-[#111111] text-[#F4F1EA] px-2.5 py-1"
              >02</span
            >
            <h2 class="font-serif text-2xl md:text-3xl font-normal">
              Documents récents
            </h2>
          </div>

          <RouterLink
            to="/documents"
            class="font-mono text-xs uppercase tracking-wider font-bold text-[#E0533C] hover:underline underline-offset-4"
          >
            Voir tous les documents →
          </RouterLink>
        </div>

        <!-- PANNEAU DES DOCUMENTS -->
        <div
          class="bg-[#FAF8F5] border-2 border-[#111111] shadow-[6px_6px_0px_0px_#111111]"
        >
          <!-- BARRE DE RECHERCHE -->
          <div
            class="p-4 sm:p-6 border-b-2 border-[#111111] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4"
          >
            <div class="relative flex-1 max-w-md">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#111111]/50"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="7" stroke-width="2" />
                <path
                  d="m20 20-3.5-3.5"
                  stroke-linecap="round"
                  stroke-width="2"
                />
              </svg>

              <input
                v-model="searchQuery"
                type="search"
                placeholder="Rechercher par titre, type ou statut..."
                aria-label="Rechercher un document"
                class="w-full bg-[#F4F1EA] border border-[#111111] pl-10 pr-4 py-2.5 font-mono text-xs text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
              />
            </div>

            <span
              class="font-mono text-xs uppercase tracking-wider text-[#111111]/60 self-end sm:self-center"
            >
              {{ filteredDocuments.length }} document(s)
            </span>
          </div>

          <!-- LISTE DES DOCUMENTS -->
          <div
            v-if="filteredDocuments.length"
            class="divide-y-2 divide-[#111111]"
          >
            <RouterLink
              v-for="doc in filteredDocuments"
              :key="doc.id"
              :to="`/documents/${doc.id}`"
              class="group flex flex-col sm:flex-row sm:items-center justify-between p-5 sm:p-6 hover:bg-[#F4F1EA] transition-colors focus-visible:outline-2 focus-visible:outline-black gap-4"
            >
              <div class="flex items-start gap-4">
                <div
                  class="w-10 h-10 border border-[#111111] bg-[#F4F1EA] flex-shrink-0 flex items-center justify-center text-[#111111] group-hover:bg-[#111111] group-hover:text-[#F4F1EA] transition-colors mt-0.5"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    class="w-5 h-5"
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

                <div>
                  <h3
                    class="font-serif text-lg font-normal text-[#111111] group-hover:text-[#E0533C] transition-colors"
                  >
                    {{ doc.title }}
                  </h3>
                  <div
                    class="flex items-center gap-2 mt-1 font-mono text-[11px] text-[#111111]/60"
                  >
                    <span class="uppercase font-bold">{{ doc.type }}</span>
                    <span>•</span>
                    <span>{{ doc.updatedAt }}</span>
                  </div>
                </div>
              </div>

              <div
                class="flex items-center justify-between sm:justify-end gap-6 border-t sm:border-t-0 border-[#111111]/10 pt-3 sm:pt-0"
              >
                <span
                  class="font-mono text-[10px] uppercase font-bold px-3 py-1 tracking-wider"
                  :class="getStatusStyle(doc.status)"
                >
                  {{ doc.status }}
                </span>

                <span
                  class="font-mono text-base font-bold text-[#111111] group-hover:translate-x-1 group-hover:text-[#E0533C] transition-transform"
                >
                  →
                </span>
              </div>
            </RouterLink>
          </div>

          <!-- ÉTAT VIDE -->
          <div v-else class="p-12 text-center">
            <p class="font-serif text-2xl font-normal text-[#111111] mb-2">
              Aucun document trouvé.
            </p>
            <p class="font-mono text-xs text-[#111111]/60">
              Essayez de modifier votre terme de recherche.
            </p>
          </div>
        </div>
      </section>

      <!-- BANNIÈRE ASSISTANCE -->
      <section
        class="mt-20 p-8 sm:p-12 bg-[#111111] text-[#F4F1EA] border-2 border-[#111111] shadow-[6px_6px_0px_0px_#E0533C] flex flex-col md:flex-row items-start md:items-center justify-between gap-8"
      >
        <div class="max-w-2xl">
          <p
            class="font-mono text-xs uppercase tracking-widest text-[#E0533C] font-bold mb-3"
          >
            // ASSISTANCE RÉDACTIONNEL
          </p>
          <h2 class="font-serif text-2xl sm:text-4xl font-normal leading-tight">
            Vous hésitez sur le bon type de document ?
          </h2>
          <p
            class="mt-3 text-sm sm:text-base text-[#F4F1EA]/70 leading-relaxed"
          >
            Exposez brièvement votre contexte à notre assistant guidé. Il
            sélectionnera le modèle juridique ou administratif idéal.
          </p>
        </div>

        <RouterLink
          to="/assistant"
          class="inline-flex items-center gap-3 bg-[#E0533C] text-[#F4F1EA] px-6 py-4 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#F4F1EA] hover:text-[#111111] transition-colors focus-visible:outline-2 focus-visible:outline-white whitespace-nowrap"
        >
          Consulter l'assistant
          <span aria-hidden="true">→</span>
        </RouterLink>
      </section>
    </div>
  </main>
</template>

<style scoped>
/* Les styles spécifiques ont été entièrement remplacés par les utilitaires Tailwind */
</style>
