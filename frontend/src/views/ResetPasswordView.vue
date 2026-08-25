<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import axios from "axios";
import authService from "../services/authService";

const route = useRoute();
const router = useRouter();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const isLoading = ref(false);
const isSuccess = ref(false);
const errorMessage = ref("");
const tokenMissing = ref(false);

onMounted(() => {
  const queryToken = route.query.token;
  if (typeof queryToken === "string" && queryToken.length > 0) {
    token.value = queryToken;
  } else {
    tokenMissing.value = true;
  }
});

const passwordsMatch = computed(
  () => newPassword.value === confirmPassword.value,
);

async function handleSubmit() {
  errorMessage.value = "";

  if (!newPassword.value || !confirmPassword.value) {
    errorMessage.value = "Les deux champs sont requis.";
    return;
  }

  if (!passwordsMatch.value) {
    errorMessage.value = "Les mots de passe ne correspondent pas.";
    return;
  }

  isLoading.value = true;
  try {
    await authService.resetPassword(token.value, newPassword.value);
    isSuccess.value = true;
    setTimeout(() => {
      router.push({ name: "login" });
    }, 3000);
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      errorMessage.value =
        err.response?.data?.error ?? "Le lien est invalide ou a expiré.";
    } else {
      errorMessage.value = "Une erreur inattendue est survenue.";
    }
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
            [ Sécurité ]
          </span>
          <h1
            class="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#111111]"
          >
            Nouveau mot de passe
          </h1>
          <p class="font-serif text-[#111111]/70 text-base mt-2">
            Définissez un nouveau secret d'accès pour votre compte.
          </p>
        </div>

        <!-- ERREUR TOKEN MANQUANT -->
        <div
          v-if="tokenMissing"
          class="p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold flex items-center gap-3"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5 shrink-0"
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
          <span
            >LIEN INVALIDE : Aucun jeton de sécurité trouvé dans l'URL.</span
          >
        </div>

        <!-- SUCCÈS RÉINITIALISATION -->
        <div v-else-if="isSuccess" class="space-y-4">
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
            <span>Mot de passe réinitialisé avec succès !</span>
          </div>
          <p class="font-serif text-[#111111]/70 text-sm leading-relaxed">
            Redirection automatique vers la page de connexion dans quelques
            instants...
          </p>
        </div>

        <!-- FORMULAIRE PRINCIPAL -->
        <form v-else class="space-y-6" @submit.prevent="handleSubmit">
          <!-- NOUVEAU MOT DE PASSE -->
          <div class="space-y-2">
            <label
              for="newPassword"
              class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
            >
              Nouveau mot de passe
            </label>
            <div class="relative flex items-center">
              <input
                id="newPassword"
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="••••••••••••"
                autocomplete="new-password"
                :disabled="isLoading"
                required
                class="w-full h-12 pl-4 pr-12 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C] disabled:opacity-50"
              />
              <button
                type="button"
                class="absolute right-3 p-1 text-[#111111]/60 hover:text-[#111111] transition-colors focus:outline-none"
                :aria-label="
                  showNewPassword
                    ? 'Masquer le mot de passe'
                    : 'Afficher le mot de passe'
                "
                @click="showNewPassword = !showNewPassword"
              >
                <svg
                  v-if="showNewPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                  ></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
            </div>
          </div>

          <!-- CONFIRMER MOT DE PASSE -->
          <div class="space-y-2">
            <label
              for="confirmPassword"
              class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
            >
              Confirmer le mot de passe
            </label>
            <div class="relative flex items-center">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="••••••••••••"
                autocomplete="new-password"
                :disabled="isLoading"
                required
                class="w-full h-12 pl-4 pr-12 bg-[#F4F1EA] border text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C] disabled:opacity-50"
                :class="
                  confirmPassword && !passwordsMatch
                    ? 'border-[#E0533C]'
                    : 'border-[#111111]'
                "
              />
              <button
                type="button"
                class="absolute right-3 p-1 text-[#111111]/60 hover:text-[#111111] transition-colors focus:outline-none"
                :aria-label="
                  showConfirmPassword
                    ? 'Masquer la confirmation'
                    : 'Afficher la confirmation'
                "
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <svg
                  v-if="showConfirmPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path
                    d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"
                  ></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
            </div>
            <p
              v-if="confirmPassword && !passwordsMatch"
              class="font-mono text-xs text-[#E0533C] mt-1"
            >
              Les mots de passe ne correspondent pas.
            </p>
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

          <!-- BOUTON SUBMIT -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full h-14 bg-[#111111] hover:bg-[#E0533C] disabled:bg-[#111111]/30 disabled:cursor-not-allowed text-[#F4F1EA] font-mono text-xs uppercase tracking-widest transition-colors border-none flex items-center justify-center gap-2 mt-4"
          >
            <span
              v-if="isLoading"
              class="w-4 h-4 border-2 border-[#F4F1EA]/30 border-t-[#F4F1EA] rounded-full animate-spin"
            ></span>
            <span>{{ isLoading ? "Mise à jour..." : "Réinitialiser" }}</span>
          </button>
        </form>

        <!-- FOOTER DE LA CARTE -->
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
