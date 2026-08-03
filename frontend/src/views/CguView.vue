<script setup lang="ts">
const lastUpdate = "Aujourd'hui";
</script>

<template>
  <main class="legal-page">
    <header class="legal-header">
      <span class="legal-tag">Règlement</span>
      <h1>Conditions Générales d'Utilisation</h1>
      <p class="subtitle">Dernière mise à jour : {{ lastUpdate }}</p>
    </header>

    <div class="legal-content">
      <section class="legal-card">
        <h2>1. Objet</h2>
        <p>
          Les présentes CGU ont pour objet de définir les modalités de mise à
          disposition des services de la plateforme
          <strong>HelpMeDraft</strong>, éditée par LexiCorp.
        </p>
      </section>

      <section class="legal-card">
        <h2>2. Services d'Assistance IA</h2>
        <p>
          HelpMeDraft met à disposition des outils de génération et
          d'amélioration de texte basés sur des modèles de langage (LLM).
          L'utilisateur demeure le seul responsable du contenu rédigé et de
          l'utilisation qu'il fait des suggestions apportées par l'IA.
        </p>
      </section>

      <section class="legal-card">
        <h2>3. Quotas et Utilisation Réseau</h2>
        <p>
          Afin de garantir un service équitable pour l'ensemble des
          utilisateurs, un système de quotas de requêtes quotidiennes (ex: 20
          requêtes IA par jour) est appliqué aux comptes standards.
        </p>
      </section>

      <section class="legal-card">
        <h2>4. Responsabilité</h2>
        <p>
          LexiCorp s'efforce d'assurer une disponibilité maximale du service,
          mais ne saurait être tenue pour responsable des interruptions
          temporaires liées à des maintenances ou à des pannes d'API tierces
          (OpenAI).
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
@import "../assets/legal-style.css";
</style>
