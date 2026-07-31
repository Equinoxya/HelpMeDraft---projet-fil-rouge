<!-- Nav.vue -->
<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { RouterLink } from "vue-router";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = async () => {
  await authStore.logout();
  router.push("/");
};
</script>

<template>
  <nav>
    <div class="navbar bg-[#16233A] shadow-sm">
      <div class="navbar-start">
        <div class="dropdown">
          <div tabIndex="{0}" role="button" class="btn btn-ghost btn-circle">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h7"
              />
            </svg>
          </div>

          <ul
            tabIndex="-1"
            class="menu-lg bg-base-200 w-56 dropdown-content rounded-box z-1 mt-3 p-2 shadow"
          >
            <li>
              <RouterLink to="/">Accueil</RouterLink>
            </li>

            <template v-if="authStore.isAuthenticated">
              <button @click="handleLogout">Déconnexion</button>
            </template>

            <template v-else>
              <li>
                <RouterLink to="/login">Connexion</RouterLink>
              </li>

              <li>
                <RouterLink to="/register">Inscription</RouterLink>
              </li>
            </template>
          </ul>
        </div>
      </div>

      <div class="navbar-center">
        <h1 class="btn btn-ghost text-xl">
          <RouterLink to="/">Help Me Draft</RouterLink>
        </h1>
      </div>
    </div>
  </nav>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

/* Barre principale */

nav {
  position: sticky;
  top: 0;
  z-index: 50;
  width: 100%;
  font-family: "Inter", sans-serif;
}

[class~="navbar"] {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 72px;
  padding: 0 2rem;
  background: rgba(22, 35, 58, 0.96);
  border-bottom: 1px solid rgba(239, 234, 224, 0.1);
  box-shadow: 0 10px 35px rgba(5, 12, 24, 0.2);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

/* Trait doré discret */

[class~="navbar"]::after {
  content: "";
  position: absolute;
  right: 0;
  bottom: -1px;
  left: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(201, 162, 39, 0.7) 50%,
    transparent 100%
  );
}

/* Partie gauche */

[class~="navbar-start"] {
  position: relative;
  z-index: 3;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: flex-start;
}

/* Centre de la navigation */

[class~="navbar-center"] {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate(-50%, -50%);
}

/* Nom du site */

[class~="navbar-center"] h1 {
  min-height: auto;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  box-shadow: none;
}

[class~="navbar-center"] h1 a {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0;
  font-family: "Fraunces", serif;
  font-size: clamp(1.35rem, 3vw, 1.65rem);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.025em;
  color: #efeae0;
  text-decoration: none;
  transition:
    color 180ms ease,
    transform 180ms ease;
}

[class~="navbar-center"] h1 a::after {
  content: "";
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  background: #c9a227;
  transform: scaleX(0);
  transform-origin: center;
  transition: transform 180ms ease;
}

[class~="navbar-center"] h1 a:hover {
  color: #c9a227;
  transform: translateY(-1px);
}

[class~="navbar-center"] h1 a:hover::after {
  transform: scaleX(1);
}

/* Menu déroulant */

[class~="dropdown"] {
  position: relative;
}

/* Bouton hamburger */

[class~="btn-circle"] {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  min-height: 44px;
  padding: 0;
  border: 1px solid rgba(239, 234, 224, 0.14);
  border-radius: 50%;
  outline: none;
  background: rgba(239, 234, 224, 0.04);
  color: #efeae0;
  cursor: pointer;
  box-shadow: none;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease;
}

[class~="btn-circle"]:hover {
  border-color: rgba(201, 162, 39, 0.65);
  background: rgba(201, 162, 39, 0.12);
  color: #c9a227;
  transform: translateY(-1px);
}

[class~="btn-circle"]:focus-visible {
  border-color: #c9a227;
  box-shadow: 0 0 0 3px rgba(201, 162, 39, 0.18);
}

[class~="btn-circle"] svg {
  width: 21px;
  height: 21px;
  transition: transform 220ms ease;
}

[class~="dropdown"]:focus-within [class~="btn-circle"] svg {
  transform: rotate(90deg);
}

/* Contenu déroulant */

[class~="dropdown-content"] {
  position: absolute;
  top: calc(100% + 0.75rem);
  left: 0;
  display: flex;
  flex-direction: column;
  width: 230px;
  margin: 0;
  padding: 0.65rem;
  overflow: hidden;
  border: 1px solid rgba(22, 35, 58, 0.12);
  border-radius: 8px;
  background: #efeae0;
  color: #16233a;
  list-style: none;
  box-shadow:
    0 24px 55px rgba(5, 12, 24, 0.35),
    0 1px 0 rgba(255, 255, 255, 0.7) inset;

  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transform-origin: top left;
  pointer-events: none;

  transition:
    opacity 180ms ease,
    visibility 180ms ease,
    transform 180ms ease;
}

/* Bord supérieur du menu */

[class~="dropdown-content"]::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(
    90deg,
    #c9a227 0%,
    #c9a227 55%,
    #4c7a73 55%,
    #4c7a73 100%
  );
}

/* Affichage du menu */

[class~="dropdown"]:focus-within [class~="dropdown-content"] {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}

/* Éléments du menu */

[class~="dropdown-content"] li {
  display: block;
  width: 100%;
}

[class~="dropdown-content"] li + li {
  margin-top: 0.2rem;
}

[class~="dropdown-content"] a,
[class~="dropdown-content"] button {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  min-height: 42px;
  padding: 0.7rem 0.85rem;
  border: none;
  border-radius: 5px;
  background: transparent;
  font-family: "Inter", sans-serif;
  font-size: 0.88rem;
  font-weight: 500;
  color: #16233a;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition:
    background-color 160ms ease,
    color 160ms ease,
    padding-left 160ms ease;
}

[class~="dropdown-content"] a::before,
[class~="dropdown-content"] button::before {
  content: "";
  width: 0;
  height: 1px;
  margin-right: 0;
  background: #c9a227;
  transition:
    width 160ms ease,
    margin-right 160ms ease;
}

[class~="dropdown-content"] a:hover,
[class~="dropdown-content"] button:hover {
  padding-left: 1rem;
  background: rgba(22, 35, 58, 0.07);
  color: #4c7a73;
}

[class~="dropdown-content"] a:hover::before,
[class~="dropdown-content"] button:hover::before {
  width: 14px;
  margin-right: 0.45rem;
}

/* Lien correspondant à la page active */

[class~="dropdown-content"] a.router-link-active {
  background: rgba(201, 162, 39, 0.13);
  color: #16233a;
}

[class~="dropdown-content"] a.router-link-active::after {
  content: "";
  position: absolute;
  top: 50%;
  right: 0.85rem;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #c9a227;
  transform: translateY(-50%);
}

/* Bouton déconnexion */

[class~="dropdown-content"] > button {
  margin-top: 0.2rem;
  color: #a34d37;
}

[class~="dropdown-content"] > button:hover {
  background: rgba(217, 119, 87, 0.11);
  color: #8b3c29;
}

/* Responsive */

@media (max-width: 640px) {
  [class~="navbar"] {
    min-height: 64px;
    padding: 0 1rem;
  }

  [class~="navbar-center"] h1 a {
    font-size: 1.25rem;
  }

  [class~="btn-circle"] {
    width: 40px;
    height: 40px;
    min-height: 40px;
  }

  [class~="dropdown-content"] {
    width: min(230px, calc(100vw - 2rem));
  }
}

/* Réduction des animations */

@media (prefers-reduced-motion: reduce) {
  [class~="btn-circle"],
  [class~="btn-circle"] svg,
  [class~="dropdown-content"],
  [class~="dropdown-content"] a,
  [class~="dropdown-content"] button,
  [class~="navbar-center"] h1 a {
    transition: none;
  }
}
</style>
