<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import authService from "../services/authService";

const email = ref("");
const isLoading = ref(false);
const isSubmitted = ref(false);
const errorMessage = ref("");

async function handleSubmit() {
  errorMessage.value = "";

  if (!email.value) {
    errorMessage.value = "L'email est requis";
    return;
  }

  isLoading.value = true;
  try {
    await authService.forgotPassword(email.value.trim());
    // Message générique anti-énumération d'utilisateurs
    isSubmitted.value = true;
  } catch (err: unknown) {
    errorMessage.value = "Une erreur est survenue, réessayez plus tard";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN CARD SECTION -->
    <main class="flex-1 flex items-center justify-center px-4 py-12 lg:py-20">
      <div
        class="w-full max-w-lg bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-10 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
      >
        <!-- HEADER DE LA CARTE -->
        <div class="border-b border-[#111111]/20 pb-6 mb-8">
          <span
            class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
          >
            [ Récupération ]
          </span>
          <h1
            class="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#111111]"
          >
            Mot de passe
          </h1>
          <p class="font-serif text-[#111111]/70 text-base mt-2">
            Rétablissez l'accès sécurisé à votre espace de rédaction.
          </p>
        </div>

        <!-- FORMULAIRE PRINCIPAL -->
        <div v-if="!isSubmitted">
          <p class="font-serif text-[#111111]/80 text-sm mb-6 leading-relaxed">
            Entrez votre adresse email ci-dessous. Nous vous enverrons un lien
            sécurisé pour réinitialiser votre mot de passe.
          </p>

          <form class="space-y-6" @submit.prevent="handleSubmit">
            <!-- CHAMP EMAIL -->
            <div class="space-y-2">
              <label
                for="email"
                class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
              >
                Adresse email
              </label>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="vous@exemple.com"
                autocomplete="email"
                :disabled="isLoading"
                required
                class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C] disabled:opacity-50"
              />
            </div>

            <!-- ALERTE ERREUR -->
            <div
              v-if="errorMessage"
              class="p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold flex items-center gap-2"
              role="alert"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-4 h-4 shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <span>{{ errorMessage }}</span>
            </div>

            <!-- BOUTON DE SOUMISSION -->
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full h-14 bg-[#111111] hover:bg-[#E0533C] disabled:bg-[#111111]/30 disabled:cursor-not-allowed text-[#F4F1EA] font-mono text-xs uppercase tracking-widest transition-colors border-none flex items-center justify-center gap-2"
            >
              <span
                v-if="isLoading"
                class="w-4 h-4 border-2 border-[#F4F1EA]/30 border-t-[#F4F1EA] rounded-full animate-spin"
              ></span>
              <span>{{
                isLoading ? "Envoi en cours..." : "Envoyer le lien"
              }}</span>
            </button>
          </form>
        </div>

        <!-- CONFIRMATION APRÈS ENVOI -->
        <div v-else class="space-y-4">
          <div
            class="p-4 border border-[#111111] bg-[#111111]/5 font-mono text-xs text-[#111111] font-bold flex items-start gap-3"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-[#E0533C] shrink-0 mt-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span
              >Si cet email existe dans nos registres, un lien de
              réinitialisation vous a été envoyé.</span
            >
          </div>

          <p class="font-serif text-[#111111]/70 text-sm leading-relaxed">
            Pensez à vérifier votre boîte de réception ainsi que votre dossier
            de courriers indésirables (spams).
          </p>
        </div>

        <!-- FOOTER DE LA CARTE / LIEN RETOUR -->
        <div class="mt-8 pt-6 border-t border-[#111111]/20 text-center">
          <RouterLink
            to="/login"
            class="font-mono text-xs uppercase tracking-wider text-[#111111] hover:text-[#E0533C] transition-colors underline decoration-1 underline-offset-4"
          >
            ← Retour à la connexion
          </RouterLink>
        </div>
      </div>
    </main>
  </div>
</template>
