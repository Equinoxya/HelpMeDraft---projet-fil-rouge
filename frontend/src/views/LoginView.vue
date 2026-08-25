<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const mdp = ref("");
const errorMessage = ref("");
const isSubmitting = ref(false);
const showPassword = ref(false);

const authStore = useAuthStore();
const router = useRouter();

async function handleSubmit() {
  errorMessage.value = "";
  isSubmitting.value = true;

  try {
    await authStore.login({
      email: email.value.trim(),
      mdp: mdp.value,
    });

    router.push("/dashboard");
  } catch (err: unknown) {
    errorMessage.value =
      "Identifiants invalides. Vérifiez votre email et mot de passe.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN LOGIN CARD -->
    <main class="flex-1 flex items-center justify-center px-4 py-12 lg:py-20">
      <div
        class="w-full max-w-lg bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-10 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
      >
        <!-- HEADER DE LA CARTE -->
        <div class="border-b border-[#111111]/20 pb-6 mb-8">
          <span
            class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
          >
            [ Authentification ]
          </span>
          <h1
            class="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#111111]"
          >
            Connexion
          </h1>
          <p class="font-serif text-[#111111]/70 text-base mt-2">
            Accédez à vos dossiers juridiques et modèles d'actes.
          </p>
        </div>

        <!-- MESSAGE D'ERREUR -->
        <div
          v-if="errorMessage"
          class="mb-6 p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold"
          role="alert"
        >
          ERREUR : {{ errorMessage }}
        </div>

        <!-- FORMULAIRE -->
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <!-- EMAIL -->
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
              placeholder="votre.email@exemple.fr"
              autocomplete="email"
              required
              class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
            />
          </div>

          <!-- MOT DE PASSE -->
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <label
                for="mdp"
                class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
              >
                Mot de passe
              </label>
              <RouterLink
                to="/forgot-password"
                class="font-mono text-xs text-[#111111]/60 hover:text-[#E0533C] underline decoration-1 underline-offset-4"
              >
                Oublié ?
              </RouterLink>
            </div>

            <div class="relative flex items-center">
              <input
                id="mdp"
                v-model="mdp"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="current-password"
                required
                class="w-full h-12 pl-4 pr-12 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
              />
              <button
                type="button"
                class="absolute right-3 p-1 text-[#111111]/60 hover:text-[#111111] transition-colors focus:outline-none"
                :aria-label="
                  showPassword
                    ? 'Masquer le mot de passe'
                    : 'Afficher le mot de passe'
                "
                @click="showPassword = !showPassword"
              >
                <svg
                  v-if="showPassword"
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

          <!-- BOUTON DE SOUMISSION -->
          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full h-14 bg-[#111111] hover:bg-[#E0533C] disabled:bg-[#111111]/30 disabled:cursor-not-allowed text-[#F4F1EA] font-mono text-xs uppercase tracking-widest transition-colors border-none mt-4"
          >
            {{ isSubmitting ? "Connexion en cours..." : "Se connecter" }}
          </button>
        </form>

        <!-- FOOTER DE LA CARTE -->
        <p
          class="mt-8 pt-6 border-t border-[#111111]/20 font-serif text-center text-sm text-[#111111]/70"
        >
          Pas encore de compte Studio ?
          <RouterLink
            :to="{ name: 'register' }"
            class="font-sans font-bold text-[#111111] hover:text-[#E0533C] underline ml-1"
          >
            Créer un compte
          </RouterLink>
        </p>
      </div>
    </main>
  </div>
</template>
