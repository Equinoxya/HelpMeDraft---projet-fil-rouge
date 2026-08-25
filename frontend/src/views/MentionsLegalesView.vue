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
          [ Cadre Réglementaire ]
        </span>
        <h1
          class="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#111111] mb-4"
        >
          Mentions Légales
        </h1>
        <p
          class="font-mono text-xs text-[#111111]/70 leading-relaxed max-w-2xl"
        >
          Conformément aux dispositions de la loi n° 2004-575 du 21 juin 2004
          pour la confiance dans l'économie numérique.
        </p>
      </header>

      <!-- PANNEAU PRINCIPAL LÉGAL -->
      <div class="space-y-8">
        <!-- 1. ÉDITEUR -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">01.</span> Éditeur du
            site
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-6"
          >
            Le site <strong>HelpMeDraft</strong> est édité par la société
            <strong>{{ companyInfo.name }}</strong
            >, société par actions simplifiée au capital de
            <strong>{{ companyInfo.capital }}</strong
            >.
          </p>

          <ul
            class="space-y-3 font-mono text-xs border-l-2 border-[#E0533C] pl-4 py-1"
          >
            <li
              class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2"
            >
              <span class="font-bold uppercase tracking-wider text-[#111111]/60"
                >Siège social :</span
              >
              <span class="text-[#111111] font-semibold">{{
                companyInfo.address
              }}</span>
            </li>
            <li
              class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2"
            >
              <span class="font-bold uppercase tracking-wider text-[#111111]/60"
                >RCS :</span
              >
              <span class="text-[#111111] font-semibold">{{
                companyInfo.rcs
              }}</span>
            </li>
            <li
              class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2"
            >
              <span class="font-bold uppercase tracking-wider text-[#111111]/60"
                >N° SIRET :</span
              >
              <span class="text-[#111111] font-semibold">{{
                companyInfo.siret
              }}</span>
            </li>
            <li
              class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2"
            >
              <span class="font-bold uppercase tracking-wider text-[#111111]/60"
                >Directeur de la publication :</span
              >
              <span class="text-[#111111] font-semibold">{{
                companyInfo.director
              }}</span>
            </li>
            <li
              class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2"
            >
              <span class="font-bold uppercase tracking-wider text-[#111111]/60"
                >Email :</span
              >
              <a
                :href="`mailto:${companyInfo.email}`"
                class="text-[#E0533C] underline underline-offset-4 hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors px-1"
              >
                {{ companyInfo.email }}
              </a>
            </li>
          </ul>
        </section>

        <!-- 2. HÉBERGEMENT -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">02.</span>
            Hébergement
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-3"
          >
            Le site est hébergé par la société <strong>Vercel Inc.</strong>
          </p>
          <div
            class="p-3 bg-[#F4F1EA] border border-[#111111] font-mono text-xs text-[#111111]/80 inline-block"
          >
            {{ companyInfo.host }}
          </div>
        </section>

        <!-- 3. PROPRIÉTÉ INTELLECTUELLE -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">03.</span> Propriété
            intellectuelle
          </h2>
          <p class="text-sm sm:text-base leading-relaxed text-[#111111]/90">
            L'ensemble de ce site (structure, textes, logos, éléments
            graphiques) est la propriété exclusive de <strong>LexiCorp</strong>.
            Toute reproduction ou représentation totale ou partielle sans
            autorisation expresse est strictement interdite.
          </p>
        </section>
      </div>
    </main>
  </div>
</template>
