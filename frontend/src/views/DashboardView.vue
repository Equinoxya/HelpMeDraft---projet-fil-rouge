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
    value: "4",
    detail: "À terminer",
  },
  {
    label: "Documents finalisés",
    value: "8",
    detail: "Prêts à être exportés",
  },
];

const quickActions = [
  {
    title: "Créer un document",
    description:
      "Décrivez votre besoin et laissez l’IA préparer un premier brouillon.",
    to: "/documents/nouveau",
    icon: "document",
  },
  {
    title: "Utiliser un modèle",
    description:
      "Partez d’une structure existante adaptée à votre situation.",
    to: "/modeles",
    icon: "template",
  },
  {
    title: "Importer un document",
    description:
      "Ajoutez un document existant pour le modifier ou l’améliorer.",
    to: "/documents/importer",
    icon: "import",
  },
];

const recentDocuments = ref<RecentDocument[]>([
  {
    id: 1,
    title: "Contrat de location meublée",
    type: "Contrat",
    updatedAt: "Modifié aujourd’hui à 14:32",
    status: "Brouillon",
  },
  {
    id: 2,
    title: "Mise en demeure pour facture impayée",
    type: "Courrier",
    updatedAt: "Modifié le 29 juillet 2026",
    status: "À relire",
  },
  {
    id: 3,
    title: "Attestation d’hébergement",
    type: "Attestation",
    updatedAt: "Modifié le 26 juillet 2026",
    status: "Terminé",
  },
  {
    id: 4,
    title: "Lettre de résiliation",
    type: "Courrier",
    updatedAt: "Modifié le 22 juillet 2026",
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

function getStatusClass(status: DocumentStatus) {
  return {
    "status-draft": status === "Brouillon",
    "status-review": status === "À relire",
    "status-finished": status === "Terminé",
  };
}
</script>

<template>
  <main class="dashboard-page">
    <section class="dashboard-header">
      <div>
        <p class="dashboard-eyebrow">Espace personnel</p>

        <h1>Bonjour {{ userFirstname }}.</h1>

        <p class="dashboard-introduction">
          Retrouvez vos documents, reprenez vos brouillons et démarrez une
          nouvelle rédaction.
        </p>
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

    <section class="stats-grid" aria-label="Résumé du compte">
      <article v-for="stat in stats" :key="stat.label" class="stat-card">
        <p class="stat-label">{{ stat.label }}</p>
        <p class="stat-value">{{ stat.value }}</p>
        <p class="stat-detail">{{ stat.detail }}</p>
      </article>
    </section>

    <section class="dashboard-section">
      <div class="section-heading">
        <div>
          <p class="section-number">01</p>
          <h2>Que souhaitez-vous faire ?</h2>
        </div>
      </div>

      <div class="actions-grid">
        <RouterLink
          v-for="action in quickActions"
          :key="action.title"
          :to="action.to"
          class="action-card"
        >
          <div class="action-icon">
            <svg
              v-if="action.icon === 'document'"
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
                d="M14 2v6h6M9 13h6M9 17h6"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
              />
            </svg>

            <svg
              v-else-if="action.icon === 'template'"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              aria-hidden="true"
            >
              <rect
                x="3"
                y="3"
                width="18"
                height="18"
                rx="2"
                stroke-width="1.8"
              />
              <path
                d="M3 9h18M9 21V9"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
              />
            </svg>

            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                d="M12 3v12M7 8l5-5 5 5"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
              />
              <path
                d="M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
              />
            </svg>
          </div>

          <div class="action-content">
            <h3>{{ action.title }}</h3>
            <p>{{ action.description }}</p>
          </div>

          <span class="action-arrow" aria-hidden="true">→</span>
        </RouterLink>
      </div>
    </section>

    <section class="dashboard-section recent-section">
      <div class="section-heading recent-heading">
        <div>
          <p class="section-number">02</p>
          <h2>Documents récents</h2>
        </div>

        <RouterLink to="/documents" class="secondary-link">
          Voir tous les documents
        </RouterLink>
      </div>

      <div class="documents-panel">
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
              placeholder="Rechercher un document"
              aria-label="Rechercher un document"
            />
          </label>

          <p>{{ filteredDocuments.length }} document(s)</p>
        </div>

        <div v-if="filteredDocuments.length" class="documents-list">
          <RouterLink
            v-for="document in filteredDocuments"
            :key="document.id"
            :to="`/documents/${document.id}`"
            class="document-row"
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
              <h3>{{ document.title }}</h3>

              <div class="document-meta">
                <span>{{ document.type }}</span>
                <span aria-hidden="true">·</span>
                <span>{{ document.updatedAt }}</span>
              </div>
            </div>

            <span
              class="document-status"
              :class="getStatusClass(document.status)"
            >
              {{ document.status }}
            </span>

            <span class="document-arrow" aria-hidden="true">→</span>
          </RouterLink>
        </div>

        <div v-else class="empty-state">
          <p class="empty-title">Aucun document trouvé.</p>
          <p>
            Le document recherché semble avoir pris une pause café prolongée.
          </p>
        </div>
      </div>
    </section>

    <section class="assistance-banner">
      <div>
        <p class="assistance-label">Besoin d’aide ?</p>
        <h2>Vous ne savez pas quel document choisir ?</h2>
        <p>
          Décrivez simplement votre situation et HelpMeDraft vous orientera vers
          le bon modèle.
        </p>
      </div>

      <RouterLink to="/assistant" class="assistance-link">
        Demander à l’assistant
        <span aria-hidden="true">→</span>
      </RouterLink>
    </section>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

.dashboard-page {
  min-height: 100vh;
  padding: 4rem max(1.5rem, calc((100vw - 1280px) / 2)) 6rem;
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

.dashboard-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 3rem;
}

.dashboard-eyebrow,
.section-number,
.assistance-label {
  margin: 0 0 0.75rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #c9a227;
}

.dashboard-header h1 {
  margin: 0;
  max-width: 800px;
  font-family: "Fraunces", serif;
  font-size: clamp(2.8rem, 6vw, 4.8rem);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.045em;
}

.dashboard-introduction {
  max-width: 620px;
  margin: 1.2rem 0 0;
  font-size: 1rem;
  line-height: 1.7;
  color: rgba(239, 234, 224, 0.68);
}

.primary-action {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  min-height: 3.25rem;
  padding: 0 1.35rem;
  border: 1px solid #c9a227;
  border-radius: 5px;
  background: #c9a227;
  color: #16233a;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  transition:
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.primary-action svg {
  width: 19px;
  height: 19px;
}

.primary-action:hover {
  background: #efeae0;
  color: #16233a;
  box-shadow: 0 14px 30px rgba(5, 12, 24, 0.25);
  transform: translateY(-2px);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  margin-bottom: 5rem;
  overflow: hidden;
  border: 1px solid rgba(239, 234, 224, 0.12);
  border-radius: 8px;
  background: rgba(239, 234, 224, 0.12);
}

.stat-card {
  padding: 1.8rem;
  background: rgba(15, 24, 38, 0.82);
}

.stat-label {
  margin: 0 0 1rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(239, 234, 224, 0.5);
}

.stat-value {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: 2.6rem;
  line-height: 1;
  color: #efeae0;
}

.stat-detail {
  margin: 0.8rem 0 0;
  font-size: 0.78rem;
  color: #4c7a73;
}

.dashboard-section {
  margin-top: 5rem;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 2rem;
}

.section-heading h2,
.assistance-banner h2 {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.035em;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

.action-card {
  position: relative;
  display: flex;
  min-height: 230px;
  padding: 1.8rem;
  border: 1px solid rgba(239, 234, 224, 0.12);
  border-radius: 8px;
  background: rgba(239, 234, 224, 0.045);
  color: #efeae0;
  text-decoration: none;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.action-card:hover {
  border-color: rgba(201, 162, 39, 0.65);
  background: rgba(239, 234, 224, 0.075);
  box-shadow: 0 22px 50px rgba(5, 12, 24, 0.22);
  transform: translateY(-4px);
}

.action-icon {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  margin-right: 1.2rem;
  border: 1px solid rgba(201, 162, 39, 0.35);
  border-radius: 50%;
  background: rgba(201, 162, 39, 0.08);
  color: #c9a227;
}

.action-icon svg {
  width: 22px;
  height: 22px;
}

.action-content h3 {
  margin: 0 0 0.75rem;
  font-family: "Fraunces", serif;
  font-size: 1.35rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.7;
  color: rgba(239, 234, 224, 0.62);
}

.action-arrow {
  position: absolute;
  right: 1.5rem;
  bottom: 1.3rem;
  color: #c9a227;
  font-size: 1.3rem;
  transition: transform 180ms ease;
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
}

.secondary-link {
  color: #c9a227;
  font-size: 0.82rem;
  font-weight: 500;
  text-decoration: none;
}

.secondary-link:hover {
  text-decoration: underline;
  text-underline-offset: 5px;
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

.documents-toolbar > p {
  margin: 0;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.66rem;
  color: rgba(22, 35, 58, 0.45);
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

.documents-list {
  display: flex;
  flex-direction: column;
}

.document-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 1rem;
  min-height: 92px;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid rgba(22, 35, 58, 0.08);
  color: #16233a;
  text-decoration: none;
  transition:
    background-color 160ms ease,
    padding-left 160ms ease;
}

.document-row:last-child {
  border-bottom: none;
}

.document-row:hover {
  padding-left: 1.8rem;
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

.document-status {
  padding: 0.4rem 0.65rem;
  border-radius: 999px;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.6rem;
  font-weight: 500;
  white-space: nowrap;
}

.status-draft {
  background: rgba(201, 162, 39, 0.14);
  color: #7e6510;
}

.status-review {
  background: rgba(217, 119, 87, 0.14);
  color: #9b472f;
}

.status-finished {
  background: rgba(76, 122, 115, 0.14);
  color: #35675f;
}

.document-arrow {
  color: rgba(22, 35, 58, 0.4);
  transition: transform 160ms ease;
}

.document-row:hover .document-arrow {
  transform: translateX(4px);
}

.empty-state {
  padding: 4rem 1.5rem;
  text-align: center;
}

.empty-state p {
  margin: 0.4rem 0;
  color: rgba(22, 35, 58, 0.55);
}

.empty-state .empty-title {
  font-family: "Fraunces", serif;
  font-size: 1.5rem;
  color: #16233a;
}

.assistance-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  margin-top: 5rem;
  padding: 2.5rem;
  border-left: 4px solid #c9a227;
  background: #efeae0;
  color: #16233a;
}

.assistance-banner > div {
  max-width: 720px;
}

.assistance-banner > div > p:last-child {
  margin: 0.9rem 0 0;
  line-height: 1.7;
  color: rgba(22, 35, 58, 0.65);
}

.assistance-link {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 0.8rem;
  color: #4c7a73;
  font-size: 0.86rem;
  font-weight: 600;
  text-decoration: none;
}

.assistance-link span {
  transition: transform 180ms ease;
}

.assistance-link:hover span {
  transform: translateX(4px);
}

@media (max-width: 900px) {
  .dashboard-header,
  .assistance-banner {
    align-items: flex-start;
    flex-direction: column;
  }

  .stats-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }

  .action-card {
    min-height: 180px;
  }
}

@media (max-width: 640px) {
  .dashboard-page {
    padding: 2.8rem 1rem 4rem;
  }

  .dashboard-header {
    margin-bottom: 2.5rem;
  }

  .primary-action {
    width: 100%;
  }

  .stats-grid {
    margin-bottom: 4rem;
  }

  .section-heading,
  .documents-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .search-field {
    width: 100%;
  }

  .document-row {
    grid-template-columns: auto minmax(0, 1fr) auto;
  }

  .document-status {
    grid-column: 2;
    justify-self: start;
  }

  .document-arrow {
    grid-column: 3;
    grid-row: 1 / span 2;
  }

  .assistance-banner {
    padding: 2rem 1.5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .primary-action,
  .action-card,
  .action-arrow,
  .document-row,
  .document-arrow,
  .assistance-link span {
    transition: none;
  }
}
</style>