<script setup lang="ts">
const companyEmail = "contact@helpmedraft.fr";
const dpoContact = "rgpd@helpmedraft.fr";
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA] flex flex-col"
  >
    <!-- MAIN CONTENT -->
    <main
      class="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-16"
    >
      <!-- EN-TÊTE PAGE -->
      <header class="mb-10 pb-6 border-b border-[#111111]/20">
        <span
          class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
        >
          [ Protection des Données ]
        </span>
        <h1
          class="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#111111] mb-4"
        >
          Politique de Confidentialité
        </h1>
        <p
          class="font-mono text-xs text-[#111111]/70 leading-relaxed max-w-2xl"
        >
          Notre engagement pour la transparence et la sécurité de vos données
          personnelles, en pleine conformité avec le RGPD.
        </p>
      </header>

      <!-- PANNEAU PRINCIPAL -->
      <div class="space-y-8">
        <!-- 1. RESPONSABLE DU TRAITEMENT -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">01.</span>
            Responsable du Traitement
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            Les données à caractère personnel collectées sur l'application
            <strong>HelpMeDraft</strong> sont traitées par la société
            <strong>LexiCorp SAS</strong>.
          </p>
          <p class="text-sm sm:text-base leading-relaxed text-[#111111]/90">
            Pour toute question relative à la gestion de vos données
            personnelles ou pour exercer vos droits, vous pouvez contacter notre
            référent RGPD à l'adresse :
            <a
              :href="`mailto:${dpoContact}`"
              class="font-mono text-xs text-[#E0533C] underline underline-offset-4 hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors px-1 font-bold"
              >{{ dpoContact }}</a
            >
            ou par e-mail général à
            <a
              :href="`mailto:${companyEmail}`"
              class="font-mono text-xs text-[#E0533C] underline underline-offset-4 hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors px-1 font-bold"
              >{{ companyEmail }}</a
            >.
          </p>
        </section>

        <!-- 2. COLLECTE DES DONNÉES & COOKIES -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">02.</span> Collecte
            des Données & Cookies
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            Dans le cadre de l'utilisation du service, nous collectons les
            données strictly nécessaires :
          </p>

          <ul
            class="space-y-3 font-mono text-xs border-l-2 border-[#E0533C] pl-4 py-1 mb-6"
          >
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Compte utilisateur :</strong
              >
              <span class="text-[#111111]/80">
                Nom, prénom, adresse e-mail et mot de passe (haché de manière
                sécurisée).</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Utilisation du service :</strong
              >
              <span class="text-[#111111]/80">
                Historique des générations IA (textes avant/après, métriques
                d'utilisation).</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]">Consentements :</strong>
              <span class="text-[#111111]/80">
                Horodatage et traçabilité de vos choix RGPD.</span
              >
            </li>
          </ul>

          <!-- Encadré Cookies & Sessions -->
          <div
            class="p-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs leading-relaxed text-[#111111]"
          >
            <span class="font-bold text-[#E0533C] uppercase block mb-1"
              >[ Gestion des cookies et sessions ]</span
            >
            Ce site utilise uniquement des cookies et jetons de session (JWT /
            Refresh Tokens) strictement nécessaires à son bon fonctionnement et
            à votre authentification. Ils ne nécessitent pas votre consentement
            préalable.
          </div>
        </section>

        <!-- 3. IA & CONFIDENTIALITÉ -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">03.</span>
            Intelligence Artificielle & Confidentialité
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            HelpMeDraft intègre des modèles de langage pour vous assister dans
            la rédaction de vos documents professionnels.
          </p>
          <div
            class="p-4 bg-[#111111] text-[#F4F1EA] font-mono text-xs leading-relaxed border border-[#111111]"
          >
            <strong class="text-[#E0533C] uppercase block mb-1"
              >Garantie d'Anonymisation :</strong
            >
            Conformément à notre charte de sécurité, aucune donnée à caractère
            personnel n'est transmise aux API tierces (OpenAI) sans
            anonymisation préalable. De plus, vos données ne sont en aucun cas
            utilisées pour réentraîner les modèles publics d'IA.
          </div>
        </section>

        <!-- 4. DURÉE DE CONSERVATION -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">04.</span> Durée de
            Conservation des Données
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            Vos données sont conservées pour des durées strictement
            proportionnées aux finalités pour lesquelles elles ont été
            collectées :
          </p>

          <ul
            class="space-y-3 font-mono text-xs border-l-2 border-[#E0533C] pl-4 py-1"
          >
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Données de compte :</strong
              >
              <span class="text-[#111111]/80">
                Conservées pendant toute la durée d'activité de votre compte,
                puis supprimées définitivement dans un délai de 30 jours après
                sa clôture.</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Historique des requêtes IA :</strong
              >
              <span class="text-[#111111]/80">
                Conservé afin d'alimenter vos statistiques personnelles et vos
                quotas quotidiens.</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Logs de sécurité & sessions :</strong
              >
              <span class="text-[#111111]/80">
                Conservés pour une durée maximale de 12 mois.</span
              >
            </li>
          </ul>
        </section>

        <!-- 5. VOS DROITS -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">05.</span> Vos Droits
            Informatique et Libertés
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            Conformément au Règlement Général sur la Protection des Données
            (RGPD), vous disposez des droits suivants :
          </p>

          <ul
            class="space-y-3 font-mono text-xs border-l-2 border-[#E0533C] pl-4 py-1 mb-6"
          >
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Droit d'accès et de rectification :</strong
              >
              <span class="text-[#111111]/80">
                Vous pouvez consulter et modifier vos informations directement
                depuis votre profil.</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Droit à l'effacement (« Droit à l'oubli ») :</strong
              >
              <span class="text-[#111111]/80">
                Vous pouvez demander la suppression complète de votre compte et
                de vos documents.</span
              >
            </li>
            <li class="leading-relaxed">
              <strong class="uppercase text-[#111111]"
                >Droit à la limitation et à la portabilité :</strong
              >
              <span class="text-[#111111]/80">
                Vous pouvez demander une copie exportable de vos données
                documentaires.</span
              >
            </li>
          </ul>

          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 pt-4 border-t border-[#111111]/10"
          >
            Pour exercer l'un de ces droits, envoyez simplement votre demande à
            <a
              :href="`mailto:${companyEmail}`"
              class="font-mono text-xs text-[#E0533C] underline underline-offset-4 hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors px-1 font-bold"
              >{{ companyEmail }}</a
            >. Si vous estimez que vos droits ne sont pas respectés, vous
            disposez également du droit d'introduire une réclamation auprès de
            la CNIL (<strong>cnil.fr</strong>).
          </p>
        </section>
      </div>
    </main>

    <!-- FOOTER PAGE -->
    <footer
      class="border-t border-[#111111] px-6 lg:px-12 py-6 bg-[#F4F1EA] flex flex-col sm:flex-row justify-between items-center text-xs font-mono text-[#111111]/60 mt-auto"
    >
      <p>© 2026 HelpMeDraft Studio. Tous droits réservés.</p>
      <p class="mt-2 sm:mt-0">Souveraineté des Données · Protection RGPD</p>
    </footer>
  </div>
</template>
