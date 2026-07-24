<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const mdp = ref("");
const firstname = ref("");
const errorMessage = ref("");

const authStore = useAuthStore();
const router = useRouter();

async function handleSubmit() {
  errorMessage.value = "";

  try {
    await authStore.login({
      email: email.value,
      mdp: mdp.value,
      firstname: firstname.value,
    });
    router.push("/dashboard");
  } catch (err) {
    errorMessage.value = "Email ou mot de passe incorrect";
  }
}
</script>

<template>
  <div className="flex justify-center items-center m-5">
    <div className="aura aura-rainbow">
      <div
        className="card bg-base-100 w-full max-w-sm shrink-0 shadow-xl card-body"
      >
        <h1>Connexion</h1>

        <form @submit.prevent="handleSubmit" className="fieldset">
          <div>
            <label for="email" className="label">Email</label>
            <input
              id="email"
              className="input"
              placeholder="Email"
              v-model="email"
              type="email"
              required
            />
          </div>

          <div>
            <label for="mdp" className="label">Mot de passe</label>
            <input
              id="mdp"
              className="input"
              placeholder="Mot de passe"
              v-model="mdp"
              type="password"
              required
            />
          </div>

          <div><a className="link link-hover">Forgot password?</a></div>
          <button type="submit" className="btn btn-neutral mt-4">
            Se connecter
          </button>

          <p v-if="errorMessage">{{ errorMessage }}</p>
        </form>
      </div>
    </div>
  </div>
</template>
