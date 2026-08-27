<script setup lang="ts">
import { RouterLink } from "vue-router";

const categories = [
  {
    name: "Contrats",
    description: "Contrats de travail, location, prestation de services...",
    templates: [
      {
        name: "Contrat de travail CDI",
        description: "Modèle conforme au code du travail français",
        icon: "file-text",
      },
      {
        name: "Contrat de location",
        description: "Bail type pour location meublée ou non meublée",
        icon: "home",
      },
      {
        name: "Contrat de prestation",
        description: "Pour prestataires de services indépendants",
        icon: "briefcase",
      },
      {
        name: "CGV/CGU",
        description: "Conditions générales de vente et d'utilisation",
        icon: "file",
      },
    ],
  },
  {
    name: "Courriers",
    description: "Lettres et courriers administratifs...",
    templates: [
      {
        name: "Lettre de résiliation",
        description: "Modèle de lettre de résiliation type",
        icon: "x",
      },
      {
        name: "Mise en demeure",
        description: "Lettre formelle avec accusé de réception",
        icon: "alert-triangle",
      },
      {
        name: "Réclamation",
        description: "Modèle pour réclamation client/fournisseur",
        icon: "mail",
      },
      {
        name: "Accusé de réception",
        description: "Pour confirmer la réception d'un document",
        icon: "check-square",
      },
    ],
  },
  {
    name: "Administratif",
    description: "Documents administratifs divers...",
    templates: [
      {
        name: "Procès-verbal",
        description: "PV de réunion ou d'assemblée générale",
        icon: "clipboard",
      },
      {
        name: "Compte-rendu",
        description: "Modèle structuré pour comptes-rendus",
        icon: "edit-3",
      },
      {
        name: "Devis",
        description: "Devis professionnel avec TVA",
        icon: "dollar-sign",
      },
      {
        name: "Facture",
        description: "Facture conforme à la réglementation",
        icon: "file-invoice",
      },
    ],
  },
];

const iconMap: Record<string, string> = {
  "file-text": `<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                 <path d="M14 2v6h6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                 <path d="M16 13H8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                 <path d="M16 17H8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  home: `<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <polyline points="9 22 9 12 15 12 15 22" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  briefcase: `<rect x="2" y="7" width="20" height="15" rx="2" ry="2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                <path d="M12 12h.01" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  file: `<path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <path d="M13 2v7h7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  x: `<line x1="18" y1="6" x2="6" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
        <line x1="6" y1="6" x2="18" y2="18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  "alert-triangle": `<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                     <line x1="12" y1="9" x2="12" y2="13" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                     <line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  mail: `<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          <polyline points="22,6 12,13 2,6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  "check-square": `<polyline points="9 11 12 14 22 4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  clipboard: `<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                 <rect x="8" y="2" width="8" height="4" rx="1" ry="1" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  "edit-3": `<path d="M12 20h9" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
             <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  "dollar-sign": `<line x1="12" y1="1" x2="12" y2="23" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
  "file-invoice": `<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  <path d="M14 2v6h6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  <path d="M16 13H8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  <path d="M16 17H8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                  <path d="M10 9H8" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>`,
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
          // MODÈLES DE DOCUMENTS
        </p>
        <h1
          class="font-serif text-4xl sm:text-5xl font-normal tracking-tight mb-4"
        >
          Partez d'un modèle pour gagner du temps
        </h1>
        <p class="text-lg text-[#111111]/70 max-w-3xl">
          Choisissez parmi nos modèles pré-remplis et adaptez-les à vos besoins
          spécifiques.
        </p>
      </header>

      <!-- Catégories de modèles -->
      <section class="space-y-12">
        <div v-for="category in categories" :key="category.name">
          <div class="flex items-center gap-4 mb-6">
            <span
              class="font-mono text-xs font-bold bg-[#111111] text-[#F4F1EA] px-2.5 py-1"
            >
              {{ category.name }}
            </span>
            <p class="font-mono text-sm text-[#111111]/60">
              {{ category.description }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <RouterLink
              v-for="template in category.templates"
              :key="template.name"
              :to="`/documents/nouveau?template=${encodeURIComponent(template.name)}`"
              class="group bg-[#FAF8F5] border-2 border-[#111111] p-6 hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_#111111] transition-all"
            >
              <div class="flex items-start gap-4">
                <div
                  class="w-10 h-10 border border-[#111111] bg-[#F4F1EA] flex-shrink-0 flex items-center justify-center"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    class="w-5 h-5 text-[#111111]"
                    v-html="iconMap[template.icon]"
                  ></svg>
                </div>
                <div>
                  <h3
                    class="font-serif text-lg font-normal mb-1 group-hover:text-[#E0533C] transition-colors"
                  >
                    {{ template.name }}
                  </h3>
                  <p class="font-mono text-xs text-[#111111]/60">
                    {{ template.description }}
                  </p>
                </div>
              </div>
              <div class="mt-4 flex justify-end">
                <span
                  class="font-mono text-lg font-bold text-[#111111] group-hover:text-[#E0533C] transition-colors"
                >
                  →
                </span>
              </div>
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section
        class="mt-16 text-center bg-[#FAF8F5] border-2 border-[#111111] p-12"
      >
        <h2 class="font-serif text-2xl font-normal mb-4">
          Besoin d'un modèle personnalisé ?
        </h2>
        <p class="text-[#111111]/70 mb-8 max-w-xl mx-auto">
          Nous pouvons créer des modèles sur mesure pour votre activité ou votre
          organisation.
        </p>
        <a
          href="mailto:contact@helpmedraft.fr"
          class="inline-flex items-center justify-center gap-3 bg-[#111111] text-[#F4F1EA] px-8 py-4 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#E0533C] transition-colors"
        >
          Nous contacter
        </a>
      </section>
    </div>
  </main>
</template>
