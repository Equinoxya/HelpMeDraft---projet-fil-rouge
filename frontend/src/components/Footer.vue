<script setup lang="ts">
import { RouterLink } from "vue-router";

const currentYear = new Date().getFullYear();

const navLinks = [
  { label: "Accueil", to: "/" },
  { label: "Fonctionnalités", to: "/fonctionnalites" },
  { label: "Tarifs", to: "/tarifs" },
];

const legalLinks = [
  { label: "Mentions légales", to: "/mentions-legales" },
  { label: "CGU", to: "/cgu" },
  { label: "Politique de confidentialité", to: "/confidentialite" },
];

const contactEmail = "contact@helpmedraft.fr";
</script>

<template>
  <footer
    class="bg-[#F4F1EA] text-[#111111] border-t-2 border-[#111111] mt-auto font-sans antialiased"
  >
    <!-- BANDEAU SUPERIEUR / GRILLE PRINCIPALE -->
    <div
      class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-12 divide-y md:divide-y-0 md:divide-x divide-[#111111]"
    >
      <!-- BLOC MARQUE (4 cols) -->
      <aside
        class="md:col-span-4 p-8 lg:p-12 flex flex-col justify-between space-y-8"
      >
        <div class="space-y-4">
          <!-- Logo Studio -->
          <div class="flex items-center gap-3">
            <div
              class="w-8 h-8 bg-[#111111] text-[#F4F1EA] flex items-center justify-center font-mono font-black text-sm"
            >
              H
            </div>
            <span
              class="font-mono text-sm uppercase tracking-widest font-black text-[#111111]"
            >
              HelpMeDraft
            </span>
          </div>

          <p
            class="font-serif text-base text-[#111111]/80 leading-relaxed max-w-sm"
          >
            Plateforme d'assistance à la rédaction administrative et juridique.
            Passez de l'intention à l'acte écrit sans friction.
          </p>
        </div>

        <!-- Indicator de statut système (touche pro/studio) -->
        <div
          class="inline-flex items-center gap-2 font-mono text-xs text-[#111111]/70 bg-[#111111]/5 px-3 py-1.5 border border-[#111111]/20 w-fit"
        >
          <span
            class="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"
            aria-hidden="true"
          ></span>
          <span>Systèmes opérationnels · RGPD ok</span>
        </div>
      </aside>

      <!-- BLOC NAVIGATION (3 cols) -->
      <nav class="md:col-span-3 p-8 lg:p-12 space-y-6">
        <h3
          class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#E0533C]"
        >
          [ Navigation ]
        </h3>

        <ul class="space-y-3 font-mono text-xs uppercase tracking-wider">
          <li v-for="link in navLinks" :key="link.to">
            <RouterLink
              :to="link.to"
              class="hover:text-[#E0533C] hover:underline underline-offset-4 transition-colors block py-1 focus-visible:outline-2 focus-visible:outline-black"
            >
              → {{ link.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>

      <!-- BLOC LÉGAL (3 cols) -->
      <nav class="md:col-span-3 p-8 lg:p-12 space-y-6">
        <h3
          class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#E0533C]"
        >
          [ Juridique ]
        </h3>

        <ul class="space-y-3 font-mono text-xs uppercase tracking-wider">
          <li v-for="link in legalLinks" :key="link.to">
            <RouterLink
              :to="link.to"
              class="hover:text-[#E0533C] hover:underline underline-offset-4 transition-colors block py-1 focus-visible:outline-2 focus-visible:outline-black"
            >
              {{ link.label }}
            </RouterLink>
          </li>
        </ul>
      </nav>

      <!-- BLOC CONTACT & RESEAUX (2 cols) -->
      <nav
        class="md:col-span-2 p-8 lg:p-12 space-y-6 flex flex-col justify-between"
      >
        <div class="space-y-6">
          <h3
            class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#E0533C]"
          >
            [ Contact ]
          </h3>

          <a
            :href="`mailto:${contactEmail}`"
            class="font-mono text-xs break-all hover:text-[#E0533C] underline underline-offset-4 transition-colors focus-visible:outline-2 focus-visible:outline-black"
          >
            {{ contactEmail }}
          </a>
        </div>

        <!-- Réseaux Sociaux (Boutons style badge) -->
        <div class="pt-4 space-y-2">
          <span
            class="font-mono text-[10px] uppercase text-[#111111]/50 block mb-2"
            >Réseaux</span
          >
          <div class="flex gap-2">
            <a
              href="https://www.linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="LinkedIn"
              class="w-9 h-9 border border-[#111111] bg-[#FAF8F5] flex items-center justify-center hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors focus-visible:outline-2 focus-visible:outline-black"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                class="w-4 h-4 fill-current"
              >
                <path
                  d="M19 0h-14c-2.76 0-5 2.24-5 5v14c0 2.76 2.24 5 5 5h14c2.76 0 5-2.24 5-5v-14c0-2.76-2.24-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.27c-.966 0-1.75-.79-1.75-1.76s.784-1.76 1.75-1.76 1.75.79 1.75 1.76-.783 1.76-1.75 1.76zm13.5 12.27h-3v-5.6c0-1.34-.026-3.06-1.87-3.06-1.87 0-2.16 1.46-2.16 2.97v5.69h-3v-11h2.88v1.5h.04c.4-.76 1.38-1.56 2.84-1.56 3.04 0 3.6 2 3.6 4.59v6.47z"
                />
              </svg>
            </a>

            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              class="w-9 h-9 border border-[#111111] bg-[#FAF8F5] flex items-center justify-center hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors focus-visible:outline-2 focus-visible:outline-black"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                class="w-4 h-4 fill-current"
              >
                <path
                  d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
                />
              </svg>
            </a>
          </div>
        </div>
      </nav>
    </div>

    <!-- BANDEAU INFERIEUR / COPYRIGHT -->
    <div
      class="border-t border-[#111111] bg-[#111111] text-[#F4F1EA] py-4 px-6 lg:px-12 flex flex-col sm:flex-row justify-between items-center text-xs font-mono"
    >
      <p>© {{ currentYear }} LexiCorp / HelpMeDraft. Tous droits réservés.</p>
      <p class="mt-2 sm:mt-0 text-[#F4F1EA]/60">Édition & Rédaction Assistée</p>
    </div>
  </footer>
</template>

<style scoped>
/* Suppression de l'import CSS scoped qui causait des warnings */
</style>
