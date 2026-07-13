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
    await authStore.login({ email: email.value, mdp: mdp.value });
    router.push("/dashboard");
  } catch (err) {
    errorMessage.value = "Email ou mot de passe incorrect";
  }
}
</script>

<template>
  <div>
    <h1>Connexion</h1>

    <form @submit.prevent="handleSubmit">
      <div>
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" required />
      </div>

      <div>
        <label for="mdp">Mot de passe</label>
        <input id="mdp" v-model="mdp" type="password" required />
      </div>

      <button type="submit">Se connecter</button>

      <p v-if="errorMessage">{{ errorMessage }}</p>
    </form>
  </div>
</template>
