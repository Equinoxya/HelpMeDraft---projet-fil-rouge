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
    await authService.forgotPassword(email.value);
    // Message générique anti-énumération d'utilisateurs
    isSubmitted.value = true;
  } catch (err) {
    errorMessage.value = "Une erreur est survenue, réessayez plus tard";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- En-tête -->
      <div class="auth-header">
        <span class="auth-tag">Récupération</span>
        <h1>Mot de passe oublié</h1>
      </div>

      <!-- Formulaire principal -->
      <div v-if="!isSubmitted">
        <p class="auth-description">
          Entrez votre adresse email. Nous vous enverrons un lien sécurisé pour
          réinitialiser votre mot de passe.
        </p>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="email" class="form-label">Adresse email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="vous@exemple.com"
              class="form-input"
              :disabled="isLoading"
              required
            />
          </div>

          <!-- Alerte Erreur -->
          <div v-if="errorMessage" class="alert alert-error">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="alert-icon"
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

          <!-- Bouton de soumission -->
          <button type="submit" class="btn-submit" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{
              isLoading ? "Envoi en cours..." : "Envoyer le lien"
            }}</span>
          </button>
        </form>
      </div>

      <!-- Écran de confirmation après envoi -->
      <div v-else class="confirmation-box">
        <div class="alert alert-success">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="alert-icon"
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
            >Si cet email existe, un lien de réinitialisation a été
            envoyé.</span
          >
        </div>
        <p class="confirmation-subtext">
          Pensez à vérifier votre boîte de réception ainsi que votre dossier de
          courriers indésirables (spams).
        </p>
      </div>

      <!-- Lien vers la connexion -->
      <div class="auth-footer">
        <RouterLink to="/login" class="back-link">
          ← Retour à la connexion
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
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

.auth-card {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem 2rem;
  border: 1px solid rgba(239, 234, 224, 0.1);
  border-radius: 16px;
  background: rgba(239, 234, 224, 0.03);
  backdrop-filter: blur(12px);
  box-shadow: 0 20px 40px rgba(5, 12, 24, 0.4);
}

.auth-header {
  margin-bottom: 1.75rem;
  text-align: center;
}

.auth-tag {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #c9a227;
}

.auth-header h1 {
  margin: 0.4rem 0 0;
  font-family: "Fraunces", serif;
  font-size: 1.85rem;
  font-weight: 600;
  color: #efeae0;
}

.auth-description {
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(239, 234, 224, 0.7);
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgba(239, 234, 224, 0.8);
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(239, 234, 224, 0.15);
  border-radius: 8px;
  background: rgba(22, 35, 58, 0.6);
  color: #efeae0;
  font-size: 0.95rem;
  outline: none;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.form-input:focus {
  border-color: #c9a227;
  box-shadow: 0 0 0 3px rgba(201, 162, 39, 0.2);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Alertes */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  line-height: 1.4;
}

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.alert-error {
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.12);
  color: #fca5a5;
}

.alert-success {
  border: 1px solid rgba(76, 122, 115, 0.4);
  background: rgba(76, 122, 115, 0.18);
  color: #a7f3d0;
}

/* Boutons & Liens */
.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.85rem 1.5rem;
  border: 1px solid rgba(201, 162, 39, 0.5);
  border-radius: 8px;
  background: #c9a227;
  color: #16233a;
  font-family: "Inter", sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    background-color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.btn-submit:hover:not(:disabled) {
  background: #dabc36;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(201, 162, 39, 0.25);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.confirmation-box {
  text-align: center;
}

.confirmation-subtext {
  margin-top: 1rem;
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(239, 234, 224, 0.65);
}

.auth-footer {
  margin-top: 1.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(239, 234, 224, 0.08);
  text-align: center;
}

.back-link {
  font-size: 0.88rem;
  color: #c9a227;
  text-decoration: none;
  transition:
    color 180ms ease,
    transform 180ms ease;
}

.back-link:hover {
  color: #efeae0;
  text-decoration: underline;
  text-underline-offset: 4px;
}

/* Spinner de chargement */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(22, 35, 58, 0.25);
  border-top-color: #16233a;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
