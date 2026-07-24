<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
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
      router.push({ name: "Login" });
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
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="card w-full max-w-md bg-base-100 shadow-xl">
      <div class="card-body">
        <h1 class="card-title text-2xl mb-4">Réinitialiser le mot de passe</h1>

        <div v-if="tokenMissing" class="alert alert-error">
          Lien invalide : aucun token trouvé dans l'URL.
        </div>

        <div v-else-if="isSuccess" class="text-center">
          <div class="alert alert-success mb-4">
            Mot de passe réinitialisé avec succès !
          </div>
          <p class="text-sm text-base-content/70">
            Redirection vers la connexion...
          </p>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="flex flex-col gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Nouveau mot de passe</span>
            </label>
            <input
              v-model="newPassword"
              type="password"
              class="input input-bordered w-full"
              :disabled="isLoading"
            />
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text">Confirmer le mot de passe</span>
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              class="input input-bordered w-full"
              :disabled="isLoading"
            />
          </div>

          <div v-if="errorMessage" class="alert alert-error text-sm">
            {{ errorMessage }}
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="loading loading-spinner"></span>
            Réinitialiser
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
