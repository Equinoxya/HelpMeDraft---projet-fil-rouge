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
    class="flex flex-col sm:flex-row flex-wrap justify-between items-center sm:items-start gap-10 bg-base-300 text-base-content p-10 mt-auto"
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

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

/* Conteneur principal */

footer {
  position: relative;
  display: grid;
  grid-template-columns: minmax(260px, 1.5fr) repeat(3, minmax(150px, 1fr));
  align-items: start;
  width: 100%;
  padding: 4.5rem max(2rem, calc((100vw - 1280px) / 2));
  gap: 3rem;
  overflow: hidden;
  border-top: 1px solid rgba(239, 234, 224, 0.1);
  background:
    radial-gradient(
      circle at 12% 100%,
      rgba(76, 122, 115, 0.22),
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

/* Ligne décorative supérieure */

footer::before {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  width: min(1280px, calc(100% - 4rem));
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(201, 162, 39, 0.75),
    rgba(76, 122, 115, 0.75),
    transparent
  );
  transform: translateX(-50%);
}

/* Texture discrète */

footer::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.22;
  background-image:
    linear-gradient(rgba(239, 234, 224, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 234, 224, 0.025) 1px, transparent 1px);
  background-size: 52px 52px;
}

/* Tous les blocs au-dessus du décor */

footer > * {
  position: relative;
  z-index: 1;
}

/* Bloc marque */

aside {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 360px;
}

/* Logo et nom */

aside > div:first-child {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.45rem;
}

aside svg {
  width: 2rem;
  height: 2rem;
  color: #c9a227;
  filter: drop-shadow(0 4px 12px rgba(201, 162, 39, 0.18));
}

aside > div:first-child p {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: 1.6rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.035em;
  color: #efeae0;
}

/* Description */

aside > p:nth-of-type(1) {
  max-width: 310px;
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.75;
  color: rgba(239, 234, 224, 0.67);
}

/* Copyright */

aside > p:nth-of-type(2) {
  margin: 1.1rem 0 0;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.65rem;
  line-height: 1.6;
  letter-spacing: 0.03em;
  color: rgba(239, 234, 224, 0.38);
}

/* Colonnes de navigation */

footer nav {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
}

/* Titres */

.footer-title {
  position: relative;
  margin: 0 0 1.25rem;
  padding-bottom: 0.75rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: #c9a227;
}

.footer-title::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 28px;
  height: 1px;
  background: rgba(201, 162, 39, 0.75);
}

/* Liens */

.link {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: fit-content;
  min-height: 34px;
  padding: 0.3rem 0;
  font-size: 0.84rem;
  font-weight: 400;
  line-height: 1.4;
  color: rgba(239, 234, 224, 0.68);
  text-decoration: none;
  transition:
    color 180ms ease,
    transform 180ms ease;
}

.link::before {
  content: "";
  width: 0;
  height: 1px;
  margin-right: 0;
  background: #c9a227;
  transition:
    width 180ms ease,
    margin-right 180ms ease;
}

.link:hover {
  color: #efeae0;
  transform: translateX(2px);
}

.link:hover::before {
  width: 12px;
  margin-right: 0.45rem;
}

/* Lien actif */

.link.router-link-active {
  color: #efeae0;
}

.link.router-link-active::after {
  content: "";
  position: absolute;
  right: -0.8rem;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #c9a227;
}

/* Réseaux sociaux */

footer nav:last-child > div {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 1rem;
}

footer nav:last-child > div a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(239, 234, 224, 0.14);
  border-radius: 50%;
  background: rgba(239, 234, 224, 0.04);
  color: rgba(239, 234, 224, 0.68);
  text-decoration: none;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

footer nav:last-child > div a:hover {
  border-color: rgba(201, 162, 39, 0.7);
  background: rgba(201, 162, 39, 0.12);
  color: #c9a227;
  box-shadow: 0 10px 25px rgba(5, 12, 24, 0.25);
  transform: translateY(-3px);
}

footer nav:last-child > div svg {
  width: 18px;
  height: 18px;
}

/* Tablette */

@media (max-width: 1000px) {
  footer {
    grid-template-columns: repeat(2, minmax(220px, 1fr));
    padding: 4rem 2rem;
    gap: 3rem 4rem;
  }

  aside {
    max-width: 400px;
  }
}

/* Mobile */

@media (max-width: 640px) {
  footer {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3.5rem 1.5rem;
    gap: 2.75rem;
    text-align: center;
  }

  footer::before {
    width: calc(100% - 3rem);
  }

  aside,
  footer nav {
    align-items: center;
    width: 100%;
  }

  aside {
    max-width: 340px;
  }

  aside > div:first-child {
    justify-content: center;
  }

  aside > p:nth-of-type(1) {
    max-width: 320px;
  }

  .footer-title::after {
    left: 50%;
    transform: translateX(-50%);
  }

  .link {
    justify-content: center;
  }

  .link:hover {
    transform: translateY(-1px);
  }

  .link:hover::before {
    width: 0;
    margin-right: 0;
  }

  .link.router-link-active::after {
    right: -0.7rem;
  }
}

/* Accessibilité */

@media (prefers-reduced-motion: reduce) {
  .link,
  .link::before,
  footer nav:last-child > div a {
    transition: none;
  }
}
</style>
