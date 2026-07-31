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

    router.push({
      name: "login",
      query: { registered: "true" },
    });
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
  <main class="register-shell">
    <div class="register-aura">
      <section class="register-card">
        <div class="register-heading">
          <p class="register-eyebrow">Création de compte</p>
          <h1>Inscription</h1>
          <p>
            Créez votre espace HelpMeDraft et commencez à rédiger vos documents.
          </p>
        </div>

        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>

        <form class="register-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="firstname">Prénom</label>

            <input
              id="firstname"
              v-model="firstname"
              type="text"
              placeholder="Votre prénom"
              autocomplete="given-name"
              required
            />
          </div>

          <div class="form-group">
            <label for="lastname">Nom</label>

            <input
              id="lastname"
              v-model="lastname"
              type="text"
              placeholder="Votre nom"
              autocomplete="family-name"
              required
            />
          </div>

          <div class="form-group form-group-full">
            <label for="email">Adresse email</label>

            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="vous@exemple.fr"
              autocomplete="email"
              required
            />
          </div>

          <div class="form-group">
            <label for="mdp">Mot de passe</label>

            <input
              id="mdp"
              v-model="mdp"
              type="password"
              placeholder="Votre mot de passe"
              autocomplete="new-password"
              required
            />
          </div>

          <div class="password-panel">
            <p>Votre mot de passe doit contenir :</p>

            <ul class="password-rules">
              <li :class="{ valid: mdpRules.length }">
                <span>{{ mdpRules.length ? "✓" : "—" }}</span>
                Au moins 8 caractères
              </li>

              <li :class="{ valid: mdpRules.uppercase }">
                <span>{{ mdpRules.uppercase ? "✓" : "—" }}</span>
                Une majuscule
              </li>

              <li :class="{ valid: mdpRules.lowercase }">
                <span>{{ mdpRules.lowercase ? "✓" : "—" }}</span>
                Une minuscule
              </li>

              <li :class="{ valid: mdpRules.digit }">
                <span>{{ mdpRules.digit ? "✓" : "—" }}</span>
                Un chiffre
              </li>
            </ul>
          </div>

          <div class="form-group form-group-full">
            <label for="confirmMdp">Confirmer le mot de passe</label>

            <input
              id="confirmMdp"
              v-model="confirmMdp"
              type="password"
              placeholder="Saisissez à nouveau le mot de passe"
              autocomplete="new-password"
              required
              :class="{
                'input-valid': confirmMdp && mdpsMatch,
                'input-error': confirmMdp && !mdpsMatch,
              }"
            />

            <p v-if="confirmMdp && !mdpsMatch" class="field-error">
              Les mots de passe ne correspondent pas.
            </p>
          </div>

          <label class="rgpd-field form-group-full">
            <input v-model="rgpdConsent" type="checkbox" required />

            <span>
              J’accepte la politique de confidentialité et le traitement de mes
              données conformément au RGPD.
            </span>
          </label>

          <button
            type="submit"
            class="submit-button form-group-full"
            :disabled="!isFormValid || isSubmitting"
          >
            {{ isSubmitting ? "Création du compte…" : "Créer mon compte" }}
          </button>
        </form>

        <p class="login-link">
          Déjà un compte ?

          <RouterLink :to="{ name: 'login' }"> Se connecter </RouterLink>
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

.register-shell {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 72px);
  padding: 4rem 1.5rem;
  overflow: hidden;
  background:
    radial-gradient(
      circle at 15% 20%,
      rgba(76, 122, 115, 0.24),
      transparent 32%
    ),
    radial-gradient(
      circle at 85% 80%,
      rgba(201, 162, 39, 0.16),
      transparent 30%
    ),
    #16233a;
  font-family: "Inter", sans-serif;
}

.register-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.18;
  background-image:
    linear-gradient(rgba(239, 234, 224, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 234, 224, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
}

.register-aura {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 800px;
}

.register-aura::before {
  content: "";
  position: absolute;
  inset: -70px;
  z-index: -1;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(201, 162, 39, 0.14),
    transparent 68%
  );
  filter: blur(25px);
}

.register-card {
  position: relative;
  width: 100%;
  padding: 3rem;
  overflow: hidden;
  border: 1px solid rgba(239, 234, 224, 0.25);
  border-radius: 10px;
  background: #efeae0;
  color: #16233a;
  box-shadow:
    0 35px 90px rgba(5, 12, 24, 0.46),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.register-card::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 4px;
  background: linear-gradient(
    90deg,
    #c9a227 0%,
    #c9a227 58%,
    #4c7a73 58%,
    #4c7a73 100%
  );
}

.register-heading {
  max-width: 580px;
  margin-bottom: 2.5rem;
}

.register-eyebrow {
  margin: 0 0 0.9rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #4c7a73;
}

.register-heading h1 {
  position: relative;
  margin: 0 0 1.1rem;
  padding-bottom: 1.2rem;
  font-family: "Fraunces", serif;
  font-size: clamp(2.6rem, 7vw, 3.6rem);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.045em;
  color: #16233a;
}

.register-heading h1::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 58px;
  height: 3px;
  background: #c9a227;
}

.register-heading > p:last-child {
  margin: 0;
  max-width: 520px;
  font-size: 0.95rem;
  line-height: 1.7;
  color: rgba(22, 35, 58, 0.65);
}

.register-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.4rem 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group label,
.password-panel > p {
  margin: 0;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(22, 35, 58, 0.72);
}

.form-group input {
  width: 100%;
  height: 3.25rem;
  padding: 0 1rem;
  border: 1px solid rgba(22, 35, 58, 0.2);
  border-radius: 5px;
  outline: none;
  background: rgba(255, 255, 255, 0.5);
  font: inherit;
  color: #16233a;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.form-group input::placeholder {
  color: rgba(22, 35, 58, 0.36);
}

.form-group input:hover {
  border-color: rgba(22, 35, 58, 0.4);
  background: rgba(255, 255, 255, 0.68);
}

.form-group input:focus {
  border-color: #4c7a73;
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 0 0 3px rgba(76, 122, 115, 0.14);
  transform: translateY(-1px);
}

.form-group input.input-valid {
  border-color: #4c7a73;
}

.form-group input.input-error {
  border-color: #d97757;
}

.password-panel {
  align-self: end;
  min-height: 3.25rem;
  padding: 0.9rem 1rem;
  border-left: 2px solid rgba(201, 162, 39, 0.75);
  background: rgba(201, 162, 39, 0.08);
}

.password-panel > p {
  margin-bottom: 0.6rem;
  font-size: 0.6rem;
}

.password-rules {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.4rem 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.password-rules li {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.65rem;
  line-height: 1.4;
  color: rgba(22, 35, 58, 0.5);
}

.password-rules li span {
  width: 1rem;
  color: rgba(22, 35, 58, 0.35);
}

.password-rules li.valid {
  color: #4c7a73;
}

.password-rules li.valid span {
  color: #4c7a73;
}

.rgpd-field {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.2rem 0;
  cursor: pointer;
  font-size: 0.8rem;
  line-height: 1.55;
  color: rgba(22, 35, 58, 0.68);
}

.rgpd-field input {
  flex: 0 0 auto;
  width: 18px;
  height: 18px;
  margin-top: 0.1rem;
  accent-color: #4c7a73;
  cursor: pointer;
}

.submit-button {
  min-height: 3.35rem;
  margin-top: 0.25rem;
  border: 1px solid #16233a;
  border-radius: 5px;
  background: #16233a;
  font-family: "Inter", sans-serif;
  font-size: 0.92rem;
  font-weight: 600;
  color: #efeae0;
  cursor: pointer;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.submit-button:not(:disabled):hover {
  border-color: #c9a227;
  background: #c9a227;
  color: #16233a;
  box-shadow: 0 12px 28px rgba(201, 162, 39, 0.22);
  transform: translateY(-2px);
}

.submit-button:disabled {
  border-color: rgba(22, 35, 58, 0.15);
  background: rgba(22, 35, 58, 0.16);
  color: rgba(22, 35, 58, 0.42);
  cursor: not-allowed;
}

.error-message,
.field-error {
  font-family: "JetBrains Mono", monospace;
  color: #983f29;
}

.error-message {
  margin: 0 0 1.75rem;
  padding: 0.9rem 1rem;
  border-left: 3px solid #d97757;
  background: rgba(217, 119, 87, 0.1);
  font-size: 0.72rem;
}

.field-error {
  margin: 0;
  font-size: 0.65rem;
}

.login-link {
  margin: 1.8rem 0 0;
  font-size: 0.84rem;
  text-align: center;
  color: rgba(22, 35, 58, 0.6);
}

.login-link a {
  margin-left: 0.2rem;
  font-weight: 600;
  color: #4c7a73;
  text-decoration: none;
  text-underline-offset: 4px;
}

.login-link a:hover {
  color: #16233a;
  text-decoration: underline;
  text-decoration-color: #c9a227;
}

@media (max-width: 700px) {
  .register-shell {
    align-items: flex-start;
    padding: 2.5rem 1rem;
  }

  .register-card {
    padding: 2.5rem 1.5rem;
  }

  .register-form {
    grid-template-columns: 1fr;
  }

  .form-group,
  .form-group-full,
  .password-panel,
  .submit-button,
  .rgpd-field {
    grid-column: 1;
  }

  .password-rules {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .form-group input,
  .submit-button {
    transition: none;
  }
}
</style>
