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
    <div className="navbar bg-base-100 shadow-sm">
      <div className="navbar-start">
        <div className="dropdown">
          <div
            tabIndex="{0}"
            role="button"
            className="btn btn-ghost btn-circle"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
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
            className="menu-lg  bg-base-200 w-56 dropdown-content rounded-box z-1 mt-3 p-2 shadow"
          >
            <li><RouterLink to="/">Accueil</RouterLink></li>
            <template v-if="authStore.isAuthenticated">
              <button @click="handleLogout">Déconnexion</button>
            </template>
            <template v-else>
              <li><RouterLink to="/login">Connexion</RouterLink></li>
              <li><RouterLink to="/register">Inscription</RouterLink></li>
            </template>
          </ul>
        </div>
      </div>
      <div className="navbar-center">
        <h1 className="btn btn-ghost text-xl">
          <RouterLink to="/">Help Me Draft</RouterLink>
        </h1>
      </div>
    </div>
  </nav>
</template>

<style></style>
