<script setup lang="ts">
const companyInfo = {
  name: "LexiCorp SAS",
  capital: "10 000 €",
  address: "123 Avenue des Développeurs, 57000 Metz",
  siret: "123 456 789 00012",
  rcs: "Metz B 123 456 789",
  email: "contact@helpmedraft.fr",
  director: "L'équipe LexiCorp",
  host: "Vercel Inc. - 440 N Barranca Ave #4133 Covina, CA 91723, USA",
};
</script>

<template>
  <main class="legal-page">
    <header class="legal-header">
      <span class="legal-tag">Informations Légales</span>
      <h1>Mentions Légales</h1>
      <p class="subtitle">
        Conformément aux dispositions de la loi n° 2004-575 du 21 juin 2004 pour
        la confiance dans l'économie numérique.
      </p>
    </header>

    <div class="legal-content">
      <section class="legal-card">
        <h2>1. Éditeur du site</h2>
        <p>
          Le site <strong>HelpMeDraft</strong> est édité par la société
          <strong>{{ companyInfo.name }}</strong
          >, société par actions simplifiée au capital de
          {{ companyInfo.capital }}.
        </p>

        <ul class="info-list">
          <li><strong>Siège social :</strong> {{ companyInfo.address }}</li>
          <li><strong>RCS :</strong> {{ companyInfo.rcs }}</li>
          <li><strong>N° SIRET :</strong> {{ companyInfo.siret }}</li>
          <li>
            <strong>Directeur de la publication :</strong>
            {{ companyInfo.director }}
          </li>
          <li>
            <strong>Email :</strong>
            <a :href="`mailto:${companyInfo.email}`">{{ companyInfo.email }}</a>
          </li>
        </ul>
      </section>

      <section class="legal-card">
        <h2>2. Hébergement</h2>
        <p>Le site est hébergé par la société <strong>Vercel Inc.</strong></p>
        <p class="address-text">{{ companyInfo.host }}</p>
      </section>

      <section class="legal-card">
        <h2>3. Propriété intellectuelle</h2>
        <p>
          L'ensemble de ce site (structure, textes, logos, éléments graphiques)
          est la propriété exclusive de LexiCorp. Toute reproduction ou
          représentation totale ou partielle sans autorisation expresse est
          strictement interdite.
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
@import "../assets/legal-style.css";
</style>
