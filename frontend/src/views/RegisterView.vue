<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import authService from "../services/authService";

const email = ref("");
const mdp = ref("");
const confirmMdp = ref("");
const firstname = ref("");
const lastname = ref("");
const rgpdConsent = ref(false);

const router = useRouter();
const errorMessage = ref<string | null>(null);
const isSubmitting = ref(false);

async function handleSubmit() {
  errorMessage.value = null;
  isSubmitting.value = true;

  try {
    await authService.register({
      email: email.value,
      mdp: mdp.value,
      firstname: firstname.value,
      lastname: lastname.value,
      rgpd_consent: rgpdConsent.value,
    });
    router.push({ name: "login", query: { registered: "true" } });
  } catch (err: any) {
    if (err.response?.status === 409) {
      errorMessage.value = "Cet email est déjà utilisé.";
    } else if (err.response?.status === 400) {
      errorMessage.value =
        err.response.data.error ?? "Vérifiez les champs du formulaire.";
    } else {
      errorMessage.value = "Une erreur est survenue. Réessayez plus tard.";
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

const mdpValid = computed(() =>
  Object.values(mdpRules.value).every((rule) => rule === true),
);

const isFormValid = computed(
  () =>
    email.value.trim() !== "" &&
    firstname.value.trim() !== "" &&
    lastname.value.trim() !== "" &&
    mdpValid.value &&
    mdpsMatch.value &&
    rgpdConsent.value === true,
);
</script>

<template>
  <div className="flex justify-center items-center m-5">
    <div className="aura aura-rainbow">
      <div
        class="register-page"
        className="card bg-base-100 w-full max-w-sm shrink-0 shadow-xl card-body"
      >
        <h1>Inscription</h1>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <form className="fieldset" @submit.prevent="handleSubmit">
          <div>
            <label for="firstname" className="label">Prénom</label>
            <input
              id="firstname"
              v-model="firstname"
              type="text"
              className="input"
              placeholder="Prénom"
            />
          </div>

          <div>
            <label for="lastname" className="label">Nom</label>
            <input
              id="lastname"
              v-model="lastname"
              type="text"
              className="input"
              placeholder="Nom"
            />
          </div>

          <div>
            <label for="email" className="label">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              className="input"
              placeholder="Email"
            />
          </div>

          <div>
            <label for="mdp" className="label">Mot de passe</label>
            <input
              id="mdp"
              v-model="mdp"
              type="password"
              className="input"
              placeholder="Mot de passe"
            />
          </div>
          <ul class="password-rules">
            <li :class="{ valid: mdpRules.length }">
              <span>{{ mdpRules.length ? "✅" : "⬜" }}</span>
              Au moins 8 caractères
            </li>
            <li :class="{ valid: mdpRules.uppercase }">
              <span>{{ mdpRules.uppercase ? "✅" : "⬜" }}</span>
              Une majuscule
            </li>
            <li :class="{ valid: mdpRules.lowercase }">
              <span>{{ mdpRules.lowercase ? "✅" : "⬜" }}</span>
              Une minuscule
            </li>
            <li :class="{ valid: mdpRules.digit }">
              <span>{{ mdpRules.digit ? "✅" : "⬜" }}</span>
              Un chiffre
            </li>
          </ul>
          <div>
            <label for="confirmMdp" className="label"
              >Confirmer le mot de passe</label
            >
            <input
              id="confirmMdp"
              v-model="confirmMdp"
              type="password"
              className="input"
              placeholder="Confirmer le mot de passe"
            />
          </div>

          <div>
            <label className="label">
              <input v-model="rgpdConsent" type="checkbox" />
              J'accepte la politique de confidentialité (RGPD)
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-neutral mt-4"
            :disabled="!isFormValid || isSubmitting"
          >
            S'inscrire
          </button>
        </form>
        <router-link :to="{ name: 'login' }"
          >Déjà un compte ? Se connecter</router-link
        >
      </div>
    </div>
  </div>
</template>
