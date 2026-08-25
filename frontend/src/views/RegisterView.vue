<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import authService from "../services/authService";

const email = ref("");
const mdp = ref("");
const confirmMdp = ref("");
const firstname = ref("");
const lastname = ref("");
const rgpdConsent = ref(false);

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const router = useRouter();
const errorMessage = ref<string | null>(null);
const isSubmitting = ref(false);

async function handleSubmit() {
  errorMessage.value = null;
  isSubmitting.value = true;

  try {
    await authService.register({
      email: email.value.trim(),
      mdp: mdp.value,
      firstname: firstname.value.trim(),
      lastname: lastname.value.trim(),
      rgpd_consent: rgpdConsent.value,
    });

    router.push({
      name: "login",
      query: { registered: "true" },
    });
  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      if (err.response?.status === 409) {
        errorMessage.value = "Cet email est déjà utilisé.";
      } else if (err.response?.status === 400) {
        errorMessage.value =
          err.response.data?.error ?? "Vérifiez les champs du formulaire.";
      } else {
        errorMessage.value = "Une erreur est survenue. Réessayez plus tard.";
      }
    } else {
      errorMessage.value = "Une erreur inattendue est survenue.";
    }
  } finally {
    isSubmitting.value = false;
  }
}

const mdpsMatch = computed(() => mdp.value === confirmMdp.value);

const mdpRules = computed(() => ({
  length: mdp.value.length >= 8,
  uppercase: /[A-Z]/.test(mdp.value),
  lowercase: /[a-z]/.test(mdp.value),
  digit: /[0-9]/.test(mdp.value),
}));

const mdpValid = computed(() => Object.values(mdpRules.value).every(Boolean));

const isFormValid = computed(
  () =>
    email.value.trim() !== "" &&
    firstname.value.trim() !== "" &&
    lastname.value.trim() !== "" &&
    mdpValid.value &&
    mdpsMatch.value &&
    rgpdConsent.value,
);
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- FORM SECTION -->
    <main class="flex-1 flex items-center justify-center px-4 py-12 lg:py-20">
      <div
        class="w-full max-w-xl bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-10 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
      >
        <div class="border-b border-[#111111]/20 pb-6 mb-8">
          <span
            class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
          >
            [ Inscription Studio ]
          </span>
          <h1
            class="text-3xl sm:text-4xl font-black uppercase tracking-tight text-[#111111]"
          >
            Créer un compte
          </h1>
          <p class="font-serif text-[#111111]/70 text-base mt-2">
            Accédez à votre espace pour structurer vos premiers actes.
          </p>
        </div>

        <div
          v-if="errorMessage"
          class="mb-6 p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold"
          role="alert"
        >
          ANNULATION : {{ errorMessage }}
        </div>

        <form class="space-y-6" @submit.prevent="handleSubmit">
          <!-- Nom & Prénom -->
          <div class="grid sm:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label
                for="firstname"
                class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
              >
                Prénom
              </label>
              <input
                id="firstname"
                v-model="firstname"
                type="text"
                placeholder="Jean"
                autocomplete="given-name"
                required
                class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
              />
            </div>

            <div class="space-y-2">
              <label
                for="lastname"
                class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
              >
                Nom
              </label>
              <input
                id="lastname"
                v-model="lastname"
                type="text"
                placeholder="Dupont"
                autocomplete="family-name"
                required
                class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
              />
            </div>
          </div>

          <!-- Email -->
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
              placeholder="jean.dupont@exemple.fr"
              autocomplete="email"
              required
              class="w-full h-12 px-4 bg-[#F4F1EA] border border-[#111111] text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
            />
          </div>

          <!-- Mot de passe -->
          <div class="space-y-2">
            <label
              for="mdp"
              class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
            >
              Mot de passe
            </label>
            <div class="relative flex items-center">
              <input
                id="mdp"
                v-model="mdp"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="new-password"
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

          <!-- Exigences Mot de passe -->
          <div
            class="border-l-2 border-[#E0533C] bg-[#111111]/5 p-4 font-mono text-xs"
          >
            <span class="font-bold text-[#E0533C] uppercase block mb-2"
              >Exigences de sécurité :</span
            >
            <ul class="grid sm:grid-cols-2 gap-2 text-[#111111]/70">
              <li :class="{ 'text-[#111111] font-bold': mdpRules.length }">
                [{{ mdpRules.length ? "✓" : " " }}] 8 caractères min.
              </li>
              <li :class="{ 'text-[#111111] font-bold': mdpRules.uppercase }">
                [{{ mdpRules.uppercase ? "✓" : " " }}] Une majuscule
              </li>
              <li :class="{ 'text-[#111111] font-bold': mdpRules.lowercase }">
                [{{ mdpRules.lowercase ? "✓" : " " }}] Une minuscule
              </li>
              <li :class="{ 'text-[#111111] font-bold': mdpRules.digit }">
                [{{ mdpRules.digit ? "✓" : " " }}] Un chiffre
              </li>
            </ul>
          </div>

          <!-- Confirmation Mot de passe -->
          <div class="space-y-2">
            <label
              for="confirmMdp"
              class="block font-mono text-xs uppercase tracking-wider text-[#111111]"
            >
              Confirmer le mot de passe
            </label>
            <div class="relative flex items-center">
              <input
                id="confirmMdp"
                v-model="confirmMdp"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="••••••••"
                autocomplete="new-password"
                required
                class="w-full h-12 pl-4 pr-12 bg-[#F4F1EA] border text-sm text-[#111111] placeholder-[#111111]/40 focus:outline-none focus:ring-2 focus:ring-[#E0533C]"
                :class="
                  confirmMdp && !mdpsMatch
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
              v-if="confirmMdp && !mdpsMatch"
              class="font-mono text-xs text-[#E0533C] mt-1"
            >
              Les mots de passe ne correspondent pas.
            </p>
          </div>

          <!-- RGPD -->
          <label class="flex items-start gap-3 cursor-pointer pt-2">
            <input
              v-model="rgpdConsent"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 rounded-none border-[#111111] accent-[#E0533C]"
            />
            <span class="font-serif text-sm text-[#111111]/80 leading-snug">
              J’accepte la politique de confidentialité et le traitement de mes
              données conformément au RGPD.
            </span>
          </label>

          <!-- Bouton Submit -->
          <button
            type="submit"
            :disabled="!isFormValid || isSubmitting"
            class="w-full h-14 bg-[#111111] hover:bg-[#E0533C] disabled:bg-[#111111]/30 disabled:cursor-not-allowed text-[#F4F1EA] font-mono text-xs uppercase tracking-widest transition-colors border-none"
          >
            {{ isSubmitting ? "Création en cours..." : "Créer mon compte" }}
          </button>
        </form>

        <p
          class="mt-8 pt-6 border-t border-[#111111]/20 font-serif text-center text-sm text-[#111111]/70"
        >
          Déjà un compte ?
          <RouterLink
            :to="{ name: 'login' }"
            class="font-sans font-bold text-[#111111] hover:text-[#E0533C] underline ml-1"
          >
            Se connecter
          </RouterLink>
        </p>
      </div>
    </main>
  </div>
</template>
