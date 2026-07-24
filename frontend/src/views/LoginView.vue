<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const mdp = ref("");
const errorMessage = ref("");

const authStore = useAuthStore();
const router = useRouter();

async function handleSubmit() {
  errorMessage.value = "";

  try {
    await authStore.login({
      email: email.value,
      mdp: mdp.value,
    });
    router.push("/dashboard");
  } catch (err) {
    errorMessage.value = "Email ou mot de passe incorrect";
  }
}
</script>

<template>
  <div class="flex justify-center items-center m-5">
    <div class="aura aura-rainbow">
      <div
        class="card bg-base-100 w-full max-w-sm shrink-0 shadow-xl card-body"
      >
        <h1>Connexion</h1>

        <form @submit.prevent="handleSubmit" class="fieldset">
          <div>
            <label for="email" class="label">Email</label>
            <input
              id="email"
              class="input"
              placeholder="Email"
              v-model="email"
              type="email"
              required
            />
          </div>

          <div>
            <label for="mdp" class="label">Mot de passe</label>
            <input
              id="mdp"
              class="input"
              placeholder="Mot de passe"
              v-model="mdp"
              type="password"
              required
            />
          </div>

          <div>
            <RouterLink to="/forgot-password" class="link link-hover">
              Mot de passe oublié ?
            </RouterLink>
          </div>

          <button type="submit" class="btn btn-neutral mt-4">
            Se connecter
          </button>

          <p v-if="errorMessage">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>
