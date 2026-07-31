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
  <div class="flex justify-center bg-[#16233A] items-center p-5">
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

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap");

/* Page */

.flex.justify-center {
  position: relative;
  min-height: calc(100vh - 64px);
  padding: 4rem 1.5rem;
  overflow: hidden;
  background:
    radial-gradient(
      circle at 15% 15%,
      rgba(76, 122, 115, 0.25),
      transparent 32%
    ),
    radial-gradient(
      circle at 85% 80%,
      rgba(201, 162, 39, 0.17),
      transparent 30%
    ),
    #16233a;
  font-family: "Inter", sans-serif;
}

/* Motif de fond */

.flex.justify-center::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.12;
  background-image:
    linear-gradient(rgba(239, 234, 224, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239, 234, 224, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
}

/* Halo de la carte */

.aura {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
}

.aura::before {
  content: "";
  position: absolute;
  inset: -70px;
  z-index: -1;
  border-radius: 999px;
  background: radial-gradient(
    circle,
    rgba(201, 162, 39, 0.15),
    transparent 68%
  );
  filter: blur(20px);
}

/* Carte */

.card {
  position: relative;
  width: 100%;
  max-width: none;
  padding: 2.75rem;
  overflow: hidden;
  border: 1px solid rgba(239, 234, 224, 0.25);
  border-radius: 10px;
  background: #efeae0;
  color: #16233a;
  box-shadow:
    0 30px 80px rgba(5, 12, 24, 0.42),
    0 1px 0 rgba(255, 255, 255, 0.65) inset;
}

/* Trait décoratif supérieur */

.card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(
    90deg,
    #c9a227 0%,
    #c9a227 48%,
    #4c7a73 48%,
    #4c7a73 100%
  );
}

/* Petit détail façon document */

.card::after {
  content: "ACCÈS SÉCURISÉ";
  position: absolute;
  top: 1.5rem;
  right: 1.75rem;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.6rem;
  font-weight: 500;
  letter-spacing: 0.15em;
  color: rgba(22, 35, 58, 0.38);
}

/* Titre */

h1 {
  position: relative;
  margin: 0 0 2.5rem;
  padding-bottom: 1.25rem;
  font-family: "Fraunces", serif;
  font-size: clamp(2.5rem, 7vw, 3.4rem);
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.04em;
  color: #16233a;
}

h1::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 55px;
  height: 3px;
  background: #c9a227;
}

/* Formulaire */

.fieldset {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
  padding: 0;
  margin: 0;
  border: 0;
}

.fieldset > div {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

/* Labels */

.label {
  display: block;
  padding: 0;
  min-height: auto;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: rgba(22, 35, 58, 0.7);
}

/* Champs */

.input {
  width: 100%;
  height: 3.25rem;
  padding: 0 1rem;
  border: 1px solid rgba(22, 35, 58, 0.2);
  border-radius: 5px;
  outline: none;
  background: rgba(255, 255, 255, 0.45);
  font-family: "Inter", sans-serif;
  font-size: 0.95rem;
  color: #16233a;
  box-shadow: none;
  transition:
    border-color 180ms ease,
    background-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.input::placeholder {
  color: rgba(22, 35, 58, 0.38);
}

.input:hover {
  border-color: rgba(22, 35, 58, 0.4);
  background: rgba(255, 255, 255, 0.6);
}

.input:focus {
  border-color: #4c7a73;
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 0 0 3px rgba(76, 122, 115, 0.14);
  transform: translateY(-1px);
}

/* Lien mot de passe oublié */

.link {
  width: fit-content;
  font-family: "Inter", sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4c7a73;
  text-decoration: none;
  text-underline-offset: 4px;
  transition:
    color 180ms ease,
    text-decoration-color 180ms ease;
}

.link:hover {
  color: #16233a;
  text-decoration: underline;
  text-decoration-color: #c9a227;
}

/* Bouton */

.btn {
  width: 100%;
  min-height: 3.25rem;
  margin-top: 0.4rem;
  border: 1px solid #16233a;
  border-radius: 5px;
  background: #16233a;
  font-family: "Inter", sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: #efeae0;
  box-shadow: none;
  text-transform: none;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    transform 180ms ease,
    box-shadow 180ms ease;
}

.btn:hover {
  border-color: #c9a227;
  background: #c9a227;
  color: #16233a;
  box-shadow: 0 10px 24px rgba(201, 162, 39, 0.2);
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}

/* Message d'erreur */

.fieldset > p {
  margin: 0;
  padding: 0.8rem 1rem;
  border-left: 3px solid #d97757;
  background: rgba(217, 119, 87, 0.1);
  font-family: "JetBrains Mono", monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  color: #9d422a;
}

/* Responsive */

@media (max-width: 520px) {
  .flex.justify-center {
    align-items: flex-start;
    min-height: 100vh;
    padding: 2.5rem 1rem;
  }

  .card {
    padding: 2.25rem 1.5rem;
  }

  .card::after {
    top: 1.2rem;
    right: 1.25rem;
    font-size: 0.52rem;
  }

  h1 {
    margin-bottom: 2rem;
    font-size: 2.5rem;
  }
}

/* Accessibilité */

@media (prefers-reduced-motion: reduce) {
  .input,
  .btn,
  .link {
    transition: none;
  }
}
</style>
