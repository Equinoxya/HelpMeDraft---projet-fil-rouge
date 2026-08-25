<script setup lang="ts">
const lastUpdate = "Aujourd'hui";
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
          [ Règlement Intérieur ]
        </span>
        <h1
          class="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#111111] mb-4"
        >
          Conditions Générales d'Utilisation
        </h1>
        <p
          class="font-mono text-xs text-[#111111]/70 leading-relaxed max-w-2xl"
        >
          Dernière mise à jour :
          <span class="font-bold text-[#111111]">{{ lastUpdate }}</span>
        </p>
      </header>

      <!-- PANNEAU PRINCIPAL -->
      <div class="space-y-8">
        <!-- 1. OBJET -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">01.</span> Objet
          </h2>
          <p class="text-sm sm:text-base leading-relaxed text-[#111111]/90">
            Les présentes CGU ont pour objet de définir les modalités de mise à
            disposition des services de la plateforme
            <strong>HelpMeDraft</strong>, éditée par <strong>LexiCorp</strong>.
          </p>
        </section>

        <!-- 2. SERVICES D'ASSISTANCE IA -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">02.</span> Services
            d'Assistance IA
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            HelpMeDraft met à disposition des outils de génération et
            d'amélioration de texte basés sur des modèles de langage (LLM).
          </p>
          <div
            class="p-4 bg-[#F4F1EA] border border-[#111111] font-mono text-xs leading-relaxed text-[#111111]"
          >
            <strong class="text-[#E0533C] uppercase block mb-1"
              >[ Responsabilité Éditoriale ]</strong
            >
            L'utilisateur demeure le seul responsable du contenu rédigé et de
            l'utilisation qu'il fait des suggestions apportées par l'IA.
          </div>
        </section>

        <!-- 3. QUOTAS ET UTILISATION RÉSEAU -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">03.</span> Quotas et
            Utilisation Réseau
          </h2>
          <p
            class="text-sm sm:text-base leading-relaxed text-[#111111]/90 mb-4"
          >
            Afin de garantir un service équitable pour l'ensemble des
            utilisateurs, un système de quotas de requêtes quotidiennes est
            appliqué aux comptes standards.
          </p>
          <div
            class="p-3 bg-[#111111] text-[#F4F1EA] font-mono text-xs border border-[#111111] inline-block"
          >
            <span class="text-[#E0533C] font-bold">Quota standard :</span> 20
            requêtes IA / jour
          </div>
        </section>

        <!-- 4. RESPONSABILITÉ -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <h2
            class="font-serif text-xl sm:text-2xl font-bold text-[#111111] mb-4 pb-3 border-b border-[#111111]/10 flex items-center gap-2"
          >
            <span class="font-mono text-sm text-[#E0533C]">04.</span>
            Responsabilité
          </h2>
          <p class="text-sm sm:text-base leading-relaxed text-[#111111]/90">
            LexiCorp s'efforce d'assurer une disponibilité maximale du service,
            mais ne saurait être tenue pour responsable des interruptions
            temporaires liées à des maintenances ou à des pannes d'API tierces
            (OpenAI).
          </p>
        </section>
      </div>
    </main>
  </div>
</template>
