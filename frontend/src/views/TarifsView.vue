<script setup lang="ts">
import { RouterLink } from "vue-router";

const pricingPlans = [
  {
    name: "Gratuit",
    price: "0 €",
    period: "/mois",
    description: "Pour tester la plateforme",
    features: [
      "Jusqu'à 5 documents",
      "20 requêtes IA/jour",
      "Export en Markdown",
      "Support par email",
    ],
    cta: "Créer un compte",
    ctaTo: "/register",
    isPopular: false,
  },
  {
    name: "Professionnel",
    price: "19,99 €",
    period: "/mois",
    description: "Pour les utilisateurs réguliers",
    features: [
      "Documents illimités",
      "100 requêtes IA/jour",
      "Export PDF + Word",
      "Support prioritaire",
      "Historique des versions",
    ],
    cta: "Choisir ce plan",
    ctaTo: "/register",
    isPopular: true,
  },
  {
    name: "Entreprise",
    price: "49,99 €",
    period: "/mois",
    description: "Pour les équipes et cabinets",
    features: [
      "Tout en illimité",
      "500 requêtes IA/jour",
      "Gestion d'équipe",
      "Modèles personnalisés",
      "Support dédié",
      "Intégration API",
    ],
    cta: "Nous contacter",
    ctaTo: "mailto:contact@helpmedraft.fr",
    isPopular: false,
  },
];

const includedFeatures = [
  "Aucune carte bancaire requise pour l'essai",
  "Annulation à tout moment",
  "Données 100% sécurisées (RGPD)",
  "Hébergement en France",
];
</script>

<template>
  <main class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased">
    <div class="max-w-7xl mx-auto px-6 lg:px-12 pt-12 md:pt-16 pb-24">
      <!-- En-tête -->
      <header class="mb-16 text-center">
        <p
          class="font-mono text-xs uppercase tracking-widest text-[#E0533C] font-bold mb-3"
        >
          // TARIFS
        </p>
        <h1
          class="font-serif text-4xl sm:text-5xl font-normal tracking-tight mb-4"
        >
          Des formules adaptées à vos besoins
        </h1>
        <p class="text-lg text-[#111111]/70 max-w-2xl mx-auto">
          Choisissez le plan qui correspond à votre usage. Tous nos plans
          incluent l'accès complet à l'assistant IA.
        </p>
      </header>

      <!-- Grille des tarifs -->
      <section class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <article
          v-for="plan in pricingPlans"
          :key="plan.name"
          class="bg-[#FAF8F5] border-2 border-[#111111] p-8 flex flex-col"
          :class="{
            'border-[#E0533C] shadow-[6px_6px_0px_0px_#E0533C]': plan.isPopular,
          }"
        >
          <div class="mb-6">
            <h2 class="font-serif text-2xl font-normal mb-2">
              {{ plan.name }}
            </h2>
            <p class="font-mono text-sm text-[#111111]/60">
              {{ plan.description }}
            </p>
          </div>

          <div class="mb-6">
            <span class="font-serif text-5xl font-normal">{{
              plan.price
            }}</span>
            <span class="font-mono text-lg text-[#111111]/60">{{
              plan.period
            }}</span>
          </div>

          <ul class="flex-1 space-y-3 mb-8">
            <li
              v-for="feature in plan.features"
              :key="feature"
              class="flex items-center gap-3 font-mono text-sm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                class="w-4 h-4 text-[#E0533C]"
              >
                <path
                  d="M20 6L9 17l-5-5"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  fill="none"
                />
              </svg>
              <span>{{ feature }}</span>
            </li>
          </ul>

          <RouterLink
            :to="plan.ctaTo.startsWith('mailto:') ? plan.ctaTo : plan.ctaTo"
            class="w-full text-center block py-3 px-6 border-2 border-[#111111] font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors"
            :class="{
              'bg-[#111111] text-[#F4F1EA] hover:bg-[#E0533C] border-[#111111]':
                plan.isPopular,
            }"
          >
            {{ plan.cta }}
          </RouterLink>
        </article>
      </section>

      <!-- Fonctionnalités incluses -->
      <section class="mt-16 bg-[#FAF8F5] border-2 border-[#111111] p-8">
        <h2 class="font-serif text-2xl font-normal mb-6 text-center">
          Inclus dans tous les plans
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="feature in includedFeatures"
            :key="feature"
            class="flex items-center gap-3"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              class="w-5 h-5 text-[#E0533C] flex-shrink-0"
            >
              <path
                d="M20 6L9 17l-5-5"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                fill="none"
              />
            </svg>
            <span class="font-mono text-sm">{{ feature }}</span>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="mt-16 text-center">
        <p class="font-serif text-xl mb-6">Besoin d'une formule sur mesure ?</p>
        <a
          href="mailto:contact@helpmedraft.fr"
          class="inline-flex items-center justify-center gap-3 bg-[#111111] text-[#F4F1EA] px-8 py-4 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#E0533C] transition-colors"
        >
          Nous contacter
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
        </a>
      </section>
    </div>
  </main>
</template>
