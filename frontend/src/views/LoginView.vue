<script setup lang="ts">
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
</script>

<template>
  <div>
    <h1>Login</h1>
    <p>Authentifié : {{ authStore.isAuthenticated }}</p>
  </div>
</template>
