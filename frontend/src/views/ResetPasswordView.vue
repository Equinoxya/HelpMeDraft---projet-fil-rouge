<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter, RouterLink } from "vue-router";
import authService from "../services/authService";

const route = useRoute();
const router = useRouter();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
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
    errorMessage.value = "Les deux champs sont requis";
    return;
  }

  if (!passwordsMatch.value) {
    errorMessage.value = "Les mots de passe ne correspondent pas";
    return;
  }

  isLoading.value = true;
  try {
    await authService.resetPassword(token.value, newPassword.value);
    isSuccess.value = true;
    setTimeout(() => {
      router.push({ name: "login" });
    }, 3000);
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error ?? "Le lien est invalide ou a expiré";
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
        <span class="auth-tag">Sécurité</span>
        <h1>Nouveau mot de passe</h1>
      </div>

      <!-- Erreur Token manquant dans l'URL -->
      <div v-if="tokenMissing" class="status-box">
        <div class="alert alert-error">
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
          <span>Lien invalide : aucun jeton trouvé dans l'URL.</span>
        </div>
      </div>

      <!-- Écran de succès après réinitialisation -->
      <div v-else-if="isSuccess" class="status-box">
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
          <span>Mot de passe réinitialisé avec succès !</span>
        </div>
        <p class="status-subtext">
          Redirection automatique vers la page de connexion...
        </p>
      </div>

      <!-- Formulaire principal -->
      <form v-else @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label for="newPassword" class="form-label"
            >Nouveau mot de passe</label
          >
          <input
            id="newPassword"
            v-model="newPassword"
            type="password"
            placeholder="••••••••••••"
            class="form-input"
            :disabled="isLoading"
            required
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label"
            >Confirmer le mot de passe</label
          >
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="••••••••••••"
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

        <button type="submit" class="btn-submit" :disabled="isLoading">
          <span v-if="isLoading" class="spinner"></span>
          <span>{{ isLoading ? "Mise à jour..." : "Réinitialiser" }}</span>
        </button>
      </form>

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

.status-box {
  text-align: center;
}

.status-subtext {
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
  transition: color 180ms ease;
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
