<script setup lang="ts">
const companyEmail = "contact@helpmedraft.fr";
const dpoContact = "rgpd@helpmedraft.fr";
</script>

<template>
  <main class="legal-page">
    <!-- En-tête de la page -->
    <header class="legal-header">
      <span class="legal-tag">Protection des Données</span>
      <h1>Politique de Confidentialité</h1>
      <p class="subtitle">
        Notre engagement pour la transparence et la sécurité de vos données
        personnelles, en pleine conformité avec le RGPD.
      </p>
    </header>

    <!-- Contenu principal -->
    <div class="legal-content">
      <!-- 1. Responsable de traitement -->
      <section class="legal-card">
        <h2>1. Responsable du Traitement</h2>
        <p>
          Les données à caractère personnel collectées sur l'application
          <strong>HelpMeDraft</strong> sont traitées par la société
          <strong>LexiCorp SAS</strong>.
        </p>
        <p>
          Pour toute question relative à la gestion de vos données personnelles
          ou pour exercer vos droits, vous pouvez contacter notre référent RGPD
          à l'adresse :
          <a :href="`mailto:${dpoContact}`">{{ dpoContact }}</a> ou par mail
          général à <a :href="`mailto:${companyEmail}`">{{ companyEmail }}</a
          >.
        </p>
      </section>

      <!-- 2. Collecte & Cookies -->
      <section class="legal-card">
        <h2>2. Collecte des Données & Cookies</h2>
        <p>
          Dans le cadre de l'utilisation du service, nous collectons les données
          strictement nécessaires :
        </p>

        <ul class="info-list">
          <li>
            <strong>Compte utilisateur :</strong> Nom, prénom, adresse e-mail et
            mot de passe (haché de manière sécurisée).
          </li>
          <li>
            <strong>Utilisation du service :</strong> Historique des générations
            IA (textes avant/après, métriques d'utilisation).
          </li>
          <li>
            <strong>Consentements :</strong> Horodatage et traçabilité de vos
            choix RGPD.
          </li>
        </ul>

        <!-- Encadré Cookies & Sessions -->
        <div class="cookie-notice">
          <p>
            <strong>Gestion des cookies et sessions :</strong> Ce site utilise
            uniquement des cookies et jetons de session (JWT / Refresh Tokens)
            strictement nécessaires à son bon fonctionnement et à votre
            authentification. Ils ne nécessitent pas votre consentement
            préalable.
          </p>
        </div>
      </section>

      <!-- 3. Utilisation des Services IA (OpenAI) -->
      <section class="legal-card">
        <h2>3. Utilisation de l'Intelligence Artificielle & Confidencialité</h2>
        <p>
          HelpMeDraft intègre des modèles de langage pour vous assister dans la
          rédaction de vos documents professionnels.
        </p>
        <p>
          <strong>Garantie d'Anonymisation :</strong> Conformément à notre
          charte de sécurité, aucune donnée à caractère personnel n'est
          transmise aux API tierces (OpenAI) sans anonymisation préalable. De
          plus, vos données ne sont en aucun cas utilisées pour réentraîner les
          modèles publics d'IA.
        </p>
      </section>

      <!-- 4. Durée de conservation -->
      <section class="legal-card">
        <h2>4. Durée de Conservation des Données</h2>
        <p>
          Vos données sont conservées pour des durées strictement proportionnées
          aux finalités pour lesquelles elles ont été collectées :
        </p>

        <ul class="info-list">
          <li>
            <strong>Données de compte :</strong> Conservées pendant toute la
            durée d'activité de votre compte, puis supprimées définitivement
            dans un délai de 30 jours après sa clôture.
          </li>
          <li>
            <strong>Historique des requêtes IA :</strong> Conservé afin
            d'alimenter vos statistiques personnelles et vos quotas quotidiens.
          </li>
          <li>
            <strong>Logs de sécurité & sessions :</strong> Conservés pour une
            durée maximale de 12 mois.
          </li>
        </ul>
      </section>

      <!-- 5. Vos Droits (RGPD) -->
      <section class="legal-card">
        <h2>5. Vos Droits Informatique et Libertés</h2>
        <p>
          Conformément au Règlement Général sur la Protection des Données
          (RGPD), vous disposez des droits suivants :
        </p>

        <ul class="info-list">
          <li>
            <strong>Droit d'accès et de rectification :</strong> Vous pouvez
            consulter et modifier vos informations directement depuis votre
            profil.
          </li>
          <li>
            <strong>Droit à l'effacement (« Droit à l'oubli ») :</strong> Vous
            pouvez demander la suppression complète de votre compte et de vos
            documents.
          </li>
          <li>
            <strong>Droit à la limitation et à la portabilité :</strong> Vous
            pouvez demander une copie exportable de vos données documentaires.
          </li>
        </ul>

        <p class="mt-4">
          Pour exercer l'un de ces droits, envoyez simplement votre demande à
          <a :href="`mailto:${companyEmail}`">{{ companyEmail }}</a
          >. Si vous estimez que vos droits ne sont pas respectés, vous disposez
          également du droit d'introduire une réclamation auprès de la CNIL
          (cnil.fr).
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
@import "../assets/legal-style.css";
</style>
