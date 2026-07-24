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
    class="flex flex-col sm:flex-row flex-wrap justify-between items-center sm:items-start gap-10 bg-base-200 text-base-content p-10 mt-auto"
  >
    <!-- Bloc Marque -->
    <aside class="flex flex-col items-center sm:items-start gap-2">
      <div class="flex items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          class="w-8 h-8 fill-current text-primary"
        >
          <path d="M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        <p class="text-lg font-bold">HelpMeDraft</p>
      </div>
      <p class="text-sm opacity-70 max-w-xs">
        Rédigez vos documents plus vite grâce à l'assistance de l'IA.
      </p>
      <p class="text-xs opacity-50">
        Copyright © {{ currentYear }} - LexiCorp. Tous droits réservés.
      </p>
    </aside>

    <!-- Bloc Navigation -->
    <nav class="flex flex-col items-center sm:items-start">
      <h6 class="footer-title">Navigation</h6>
      <RouterLink
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="link link-hover"
      >
        {{ link.label }}
      </RouterLink>
    </nav>

    <!-- Bloc Légal -->
    <nav class="flex flex-col items-center sm:items-start">
      <h6 class="footer-title">Informations légales</h6>
      <RouterLink
        v-for="link in legalLinks"
        :key="link.to"
        :to="link.to"
        class="link link-hover"
      >
        {{ link.label }}
      </RouterLink>
    </nav>

    <!-- Bloc Contact -->
    <nav class="flex flex-col items-center sm:items-start">
      <h6 class="footer-title">Contact</h6>
      <a :href="`mailto:${contactEmail}`" class="link link-hover">
        {{ contactEmail }}
      </a>
      <div class="flex gap-4 mt-2">
        <a
          href="https://www.linkedin.com"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="LinkedIn"
          class="hover:text-primary transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="w-6 h-6 fill-current"
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
          class="hover:text-primary transition-colors"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            class="w-6 h-6 fill-current"
          >
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
            />
          </svg>
        </a>
      </div>
    </nav>
  </footer>
</template>
