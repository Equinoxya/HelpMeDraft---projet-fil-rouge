<script setup lang="ts">
import { ref } from "vue";
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
    // On affiche toujours le même message, que l'email existe ou non
    // (cohérent avec la logique anti-énumération du backend)
    isSubmitted.value = true;
  } catch (err) {
    errorMessage.value = "Une erreur est survenue, réessayez plus tard";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[#16233A]">
    <div class="card w-full max-w-md bg-base-100 shadow-xl">
      <div class="card-body">
        <h1 class="card-title text-2xl mb-4">Mot de passe oublié</h1>

        <div v-if="!isSubmitted">
          <p class="text-sm text-base-content/70 mb-4">
            Entrez votre email, vous recevrez un lien pour réinitialiser votre
            mot de passe.
          </p>

          <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text">Email</span>
              </label>
              <input
                v-model="email"
                type="email"
                placeholder="vous@exemple.com"
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
              Envoyer le lien
            </button>
          </form>
        </div>

        <div v-else class="text-center">
          <div class="alert alert-success mb-4">
            Si cet email existe, un lien de réinitialisation a été envoyé.
          </div>
          <p class="text-sm text-base-content/70">
            Vérifiez votre boîte mail (et vos spams).
          </p>
        </div>

        <div class="text-center mt-4">
          <RouterLink to="/login" class="link link-primary text-sm">
            Retour à la connexion
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
