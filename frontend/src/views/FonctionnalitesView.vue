<script setup lang="ts">
import { RouterLink } from "vue-router";

const features = [
  {
    title: "Rédaction Assistée par IA",
    description:
      "Laissez notre assistant Ollama vous aider à rédiger, reformuler ou corriger vos documents administratifs et juridiques.",
    icon: "brain",
    items: [
      "Reformulation de textes",
      "Correction orthographique",
      "Complétion automatique",
    ],
  },
  {
    title: "Éditeur Markdown Sécurisé",
    description:
      "Un éditeur moderne avec aperçu en temps réel, sans risque d'injection XSS.",
    icon: "edit",
    items: ["Syntaxe Markdown", "Aperçu instantané", "Barre d'outils complète"],
  },
  {
    title: "Gestion de Documents",
    description:
      "Organisez vos documents par dossiers, statuts et dates de modification.",
    icon: "folder",
    items: [
      "Classement par dossiers",
      "Statuts personnalisables",
      "Recherche avancée",
    ],
  },
  {
    title: "Export Multi-Formats",
    description: "Exportez vos documents dans le format de votre choix.",
    icon: "export",
    items: ["PDF", "Word (.docx)", "Markdown brut"],
  },
];

const iconMap: Record<string, string> = {
  brain: `<path d="M12 2a3 3 0 0 1 3 3v1a3 3 0 0 1-3 3 3 3 0 0 1-3-3V5a3 3 0 0 1 3-3z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <path d="M19 11a7 7 0 0 0-7-7H6a7 7 0 0 0 0 14h6z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <path d="M12 18v-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  edit: `<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  folder: `<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  export: `<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
           <polyline points="7 10 12 15 17 10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
           <line x1="12" y1="15" x2="12" y2="3" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
};
</script>

<template>
  <main class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased">
    <div class="max-w-7xl mx-auto px-6 lg:px-12 pt-12 md:pt-16 pb-24">
      <!-- En-tête -->
      <header class="mb-16">
        <p
          class="font-mono text-xs uppercase tracking-widest text-[#E0533C] font-bold mb-3"
        >
          // FONCTIONNALITÉS
        </p>
        <h1
          class="font-serif text-4xl sm:text-5xl font-normal tracking-tight mb-4"
        >
          Tout ce dont vous avez besoin pour rédiger sans effort
        </h1>
        <p class="text-lg text-[#111111]/70 max-w-3xl">
          HelpMeDraft vous accompagne à chaque étape de la rédaction
          administrative et juridique.
        </p>
      </header>

      <!-- Grille des fonctionnalités -->
      <section class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <article
          v-for="feature in features"
          :key="feature.title"
          class="bg-[#FAF8F5] border-2 border-[#111111] p-8 shadow-[4px_4px_0px_0px_#111111]"
        >
          <div class="flex items-start gap-6">
            <div
              class="flex-shrink-0 w-16 h-16 border-2 border-[#111111] bg-[#F4F1EA] flex items-center justify-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                class="w-8 h-8 text-[#111111]"
                v-html="iconMap[feature.icon]"
              ></svg>
            </div>
            <div>
              <h2 class="font-serif text-2xl font-normal mb-2">
                {{ feature.title }}
              </h2>
              <p class="text-[#111111]/70 mb-4">{{ feature.description }}</p>
              <ul class="space-y-1">
                <li
                  v-for="item in feature.items"
                  :key="item"
                  class="flex items-center gap-2 font-mono text-sm"
                >
                  <span class="text-[#E0533C]">▹</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </article>
      </section>

      <!-- CTA -->
      <section class="mt-16 text-center">
        <RouterLink
          to="/documents/nouveau"
          class="inline-flex items-center justify-center gap-3 bg-[#111111] text-[#F4F1EA] px-8 py-4 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#E0533C] transition-colors"
        >
          Commencer à rédiger
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            class="w-4 h-4"
          >
            <path
              d="M5 12h14M12 5l7 7-7 7"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
            />
          </svg>
        </RouterLink>
      </section>
    </div>
  </main>
</template>
