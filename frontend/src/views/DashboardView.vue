<script setup lang="ts">
import { useAuthStore } from "../stores/auth";
const authStore = useAuthStore();
</script>

<template>
  <div>
    <h1>Dashboard</h1>
    <p>Bonjour {{ authStore.user?.firstname }}</p>
  </div>
</template>
