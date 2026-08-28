<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
import { RouterLink, useRouter } from "vue-router";
import { storeToRefs } from "pinia";

const authStore = useAuthStore();
const router = useRouter();

const { isAuthenticated } = storeToRefs(authStore);

const handleLogout = async () => {
  await authStore.logout();
  router.push("/");
};
</script>

<template>
  <header
    class="sticky top-0 z-50 bg-[#F4F1EA] border-b-2 border-[#111111] font-sans antialiased"
  >
    <div
      class="max-w-7xl mx-auto px-6 lg:px-12 h-20 flex items-center justify-between"
    >
      <!-- LOGO / MARQUE -->
      <div class="flex items-center gap-6">
        <RouterLink
          to="/"
          class="flex items-center gap-3 group focus-visible:outline-2 focus-visible:outline-black"
        >
          <div
            class="w-8 h-8 bg-[#111111] text-[#F4F1EA] flex items-center justify-center font-mono font-black text-sm group-hover:bg-[#E0533C] transition-colors"
          >
            H
          </div>
          <span
            class="font-mono text-sm uppercase tracking-widest font-black text-[#111111]"
          >
            HelpMeDraft <span class="text-[#E0533C]">/</span> Studio
          </span>
        </RouterLink>

        <!-- BADGE ÉTAT CONNECTÉ (Desktop) -->
        <span
          v-if="isAuthenticated"
          class="hidden md:inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider bg-[#111111]/5 border border-[#111111]/20 px-2.5 py-1 text-[#111111]"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
          Session Active
        </span>
      </div>

      <!-- LIENS DESKTOP -->
      <nav
        class="hidden md:flex items-center gap-8 font-mono text-xs uppercase tracking-wider text-[#111111]"
      >
        <RouterLink
          to="/"
          class="!text-[#111111] hover:!text-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black py-2"
        >
          Accueil
        </RouterLink>

        <!-- SANS LOGIN : Connexion / Inscription -->
        <template v-if="!isAuthenticated">
          <RouterLink
            to="/login"
            class="!text-[#111111] hover:!text-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black py-2"
          >
            Connexion
          </RouterLink>
          <RouterLink
            to="/register"
            class="bg-[#111111] !text-[#F4F1EA] px-5 py-2.5 hover:bg-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black"
          >
            Espace Rédaction
          </RouterLink>
        </template>

        <!-- AVEC LOGIN : Accueil, Dashboard, Documents, Déconnexion -->
        <template v-else>
          <RouterLink
            to="/dashboard"
            class="!text-[#111111] hover:!text-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black py-2"
          >
            Tableau de bord
          </RouterLink>
          <RouterLink
            v-if="authStore.user?.role === 'admin'"
            to="/admin"
            class="!text-[#111111] hover:!text-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black py-2"
          >
            Administration
          </RouterLink>
          <RouterLink
            to="/documents"
            class="!text-[#111111] hover:!text-[#E0533C] transition-colors focus-visible:outline-2 focus-visible:outline-black py-2"
          >
            Mes documents
          </RouterLink>
          <button
            @click="handleLogout"
            class="!text-[#111111] border border-[#111111] px-4 py-2 hover:bg-[#E0533C] hover:border-[#E0533C] hover:!text-[#F4F1EA] transition-colors focus-visible:outline-2 focus-visible:outline-black cursor-pointer"
          >
            Déconnexion
          </button>
        </template>
      </nav>

      <!-- MENU MOBILE -->
      <div class="md:hidden dropdown dropdown-end">
        <button
          tabindex="0"
          aria-label="Menu de navigation"
          class="w-10 h-10 border border-[#111111] bg-[#FAF8F5] text-[#111111] flex items-center justify-center hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors focus-visible:outline-2 focus-visible:outline-black"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <ul
          tabindex="0"
          class="dropdown-content mt-2 w-64 border-2 border-[#111111] bg-[#FAF8F5] shadow-[6px_6px_0px_0px_rgba(17,17,17,1)] p-4 font-mono text-xs uppercase tracking-wider space-y-3 z-50 text-[#111111]"
        >
          <li>
            <RouterLink
              to="/"
              class="block py-2 !text-[#111111] hover:!text-[#E0533C]"
            >
              → Accueil
            </RouterLink>
          </li>

          <!-- MOBILE SANS LOGIN -->
          <template v-if="!isAuthenticated">
            <li class="pt-2 border-t border-[#111111]/20">
              <RouterLink
                to="/login"
                class="block py-2 !text-[#111111] hover:!text-[#E0533C]"
              >
                Connexion
              </RouterLink>
            </li>
            <li>
              <RouterLink
                to="/register"
                class="block text-center bg-[#111111] !text-[#F4F1EA] py-2.5 mt-2 hover:bg-[#E0533C]"
              >
                S'inscrire
              </RouterLink>
            </li>
          </template>

          <!-- MOBILE AVEC LOGIN -->
          <template v-else>
            <li>
              <RouterLink
                to="/dashboard"
                class="block py-2 !text-[#111111] hover:!text-[#E0533C]"
              >
                → Tableau de bord
              </RouterLink>
            </li>
            <li>
              <RouterLink
                to="/documents"
                class="block py-2 !text-[#111111] hover:!text-[#E0533C]"
              >
                → Mes documents
              </RouterLink>
            </li>
            <li class="pt-2 border-t border-[#111111]/20">
              <button
                @click="handleLogout"
                class="w-full text-left py-2 text-[#E0533C] font-bold cursor-pointer"
              >
                [ Déconnexion ]
              </button>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </header>
</template>
