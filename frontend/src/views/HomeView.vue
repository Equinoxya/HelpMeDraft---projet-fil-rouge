<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const typedText = ref("");
const fullText =
  "Le bailleur s'engage à restituer le dépôt de garantie dans un délai de deux mois...";
let charIndex = 0;
let typingInterval: ReturnType<typeof setInterval> | null = null;

function onRegister() {
  router.push("/register");
}

onMounted(() => {
  typingInterval = setInterval(() => {
    if (charIndex < fullText.length) {
      typedText.value += fullText[charIndex];
      charIndex++;
    } else if (typingInterval) {
      clearInterval(typingInterval);
    }
  }, 35);
});

onUnmounted(() => {
  if (typingInterval) clearInterval(typingInterval);
});

const features = [
  {
    code: "[ 01 ]",
    title: "Intelligence Contextuelle",
    description:
      "Expliquez la situation en français courant. L'IA extrait les faits clés et structure un document juridiquement cohérent.",
  },
  {
    code: "[ 02 ]",
    title: "Bibliothèque de Modèles",
    description:
      "Des bases solides pour vos baux, contrats et mises en demeure. Finie la hantise de la page blanche.",
  },
  {
    code: "[ 03 ]",
    title: "Souveraineté des Données",
    description:
      "Vos écrits restent les vôtres. Hébergement européen, aucun entraînement public sur vos données confidentielles.",
  },
];

const steps = [
  {
    step: "Étape I",
    title: "L'Intention",
    description:
      "Décrivez en 2 ou 3 phrases ce que vous souhaitez obtenir ou formaliser.",
  },
  {
    step: "Étape II",
    title: "La Structure",
    description:
      "L'algorithme génère un premier jet organisé en articles et clauses claires.",
  },
  {
    step: "Étape III",
    title: "L'Édition",
    description:
      "Affinez chaque terme directement dans l'éditeur puis exportez en PDF ou Word.",
  },
];
</script>

<template>
  <div
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased selection:bg-[#E0533C] selection:text-[#F4F1EA]"
  >
    <!-- HERO SECTION : STYLE ÉDITORIAL MONUMENTAL -->
    <header class="border-b border-[#111111] pt-16 pb-20 lg:pt-24 lg:pb-28">
      <div class="max-w-7xl mx-auto px-6 lg:px-12">
        <div class="inline-block border-l-2 border-[#E0533C] pl-4 mb-8">
          <p
            class="font-mono text-xs uppercase tracking-[0.25em] text-[#111111]/70"
          >
            Assistant de Rédaction Juridique & Administrative
          </p>
        </div>

        <h1
          class="text-5xl sm:text-7xl lg:text-8xl font-black tracking-tight leading-[0.95] text-[#111111] uppercase mb-12"
        >
          Le mot juste.<br />
          <span class="text-[#E0533C] underline decoration-4 underline-offset-8"
            >Sans l'effort</span
          >
          du premier jet.
        </h1>

        <div class="grid lg:grid-cols-12 gap-12 items-end pt-4">
          <div class="lg:col-span-6 space-y-8">
            <p
              class="text-xl sm:text-2xl font-serif text-[#111111]/80 leading-relaxed"
            >
              HelpMeDraft transforme une intention orale en un acte écrit
              rigoureux. Gardez la totale maîtrise sur le fond, gagnez du temps
              sur la forme.
            </p>

            <div class="flex flex-col sm:flex-row gap-4 pt-2">
              <button
                @click="onRegister"
                class="btn rounded-none bg-[#111111] hover:bg-[#E0533C] text-[#F4F1EA] font-mono text-xs uppercase tracking-widest h-14 px-8 border-none transition-colors"
              >
                Générer un document
              </button>
              <a
                href="#methode"
                class="btn rounded-none btn-ghost text-[#111111] hover:bg-[#111111]/10 font-mono text-xs uppercase tracking-widest h-14 px-8 border border-[#111111]"
              >
                La Méthode ↓
              </a>
            </div>
          </div>

          <!-- MOCKUP STYLE FEUILLE DE PAPIER / MANUSCRIT -->
          <div class="lg:col-span-6">
            <div
              class="bg-[#FAF8F5] border-2 border-[#111111] p-6 sm:p-8 shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
            >
              <div
                class="flex justify-between items-center border-b border-[#111111]/20 pb-4 mb-6"
              >
                <span
                  class="font-mono text-xs uppercase tracking-widest text-[#111111]/50"
                  >[ Brouillon Actif ]</span
                >
                <span class="font-mono text-xs text-[#E0533C] font-bold"
                  >MODE ÉDITION</span
                >
              </div>

              <div
                class="font-serif text-base sm:text-lg text-[#111111] min-h-[96px] leading-relaxed"
              >
                <span
                  class="font-sans font-bold text-xs uppercase tracking-wider block mb-2 text-[#E0533C]"
                  >Article 4 — Restitution</span
                >
                « {{ typedText
                }}<span
                  class="inline-block w-2 h-5 bg-[#111111] animate-blink align-middle ml-1"
                ></span>
                »
              </div>

              <div
                class="mt-8 pt-4 border-t-2 border-dashed border-[#111111]/20 bg-[#111111]/5 p-4 font-mono text-xs text-[#111111]/80"
              >
                <span class="font-bold text-[#E0533C]">NOTE D'ANALYSE :</span>
                Vérifier si le bien se situe en zone tendue pour ajuster le
                délai légal à 1 mois.
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- CARACTÉRISTIQUES (GRILLE BRUTALISTE) -->
    <section class="border-b border-[#111111] bg-[#FAF8F5]">
      <div class="max-w-7xl mx-auto">
        <div
          class="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-[#111111]"
        >
          <article
            v-for="item in features"
            :key="item.code"
            class="p-8 sm:p-12 hover:bg-[#F4F1EA] transition-colors"
          >
            <span
              class="font-mono text-xs text-[#E0533C] font-bold block mb-6"
              >{{ item.code }}</span
            >
            <h2
              class="text-2xl font-bold uppercase tracking-tight text-[#111111] mb-4"
            >
              {{ item.title }}
            </h2>
            <p class="text-[#111111]/70 leading-relaxed font-serif text-lg">
              {{ item.description }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <!-- PROCESSUS (MÉTHODE) -->
    <section id="methode" class="py-24 border-b border-[#111111]">
      <div class="max-w-7xl mx-auto px-6 lg:px-12">
        <div
          class="flex flex-col md:flex-row md:items-end justify-between mb-16 pb-6 border-b border-[#111111]"
        >
          <div>
            <span
              class="font-mono text-xs uppercase tracking-widest text-[#E0533C] font-bold"
              >Protocole</span
            >
            <h2
              class="text-4xl sm:text-5xl font-black uppercase tracking-tight text-[#111111] mt-2"
            >
              Comment ça fonctionne
            </h2>
          </div>
          <p class="font-serif italic text-lg text-[#111111]/60 mt-4 md:mt-0">
            Trois temps, sans friction.
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-12">
          <div v-for="s in steps" :key="s.step" class="space-y-4">
            <span
              class="font-mono text-xs uppercase tracking-widest text-[#111111]/40 border-b border-[#111111] pb-1 inline-block"
              >{{ s.step }}</span
            >
            <h3 class="text-2xl font-bold uppercase text-[#111111]">
              {{ s.title }}
            </h3>
            <p class="text-[#111111]/70 font-serif text-lg leading-relaxed">
              {{ s.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA FINAL BANNER -->
    <section class="bg-[#111111] text-[#F4F1EA] py-24 px-6 lg:px-12">
      <div class="max-w-5xl mx-auto text-center space-y-8">
        <span
          class="font-mono text-xs uppercase tracking-[0.3em] text-[#E0533C] font-bold"
          >Prêt à démarrer ?</span
        >
        <h2
          class="text-4xl sm:text-6xl font-black uppercase tracking-tight leading-none"
        >
          Passez de l'idée au document formel.
        </h2>
        <p class="font-serif text-xl text-[#F4F1EA]/70 max-w-xl mx-auto">
          Sans engagement. Sans carte bancaire requise pour tester.
        </p>
        <div class="pt-4">
          <button
            @click="onRegister"
            class="btn rounded-none bg-[#E0533C] hover:bg-[#c8442e] text-[#F4F1EA] font-mono text-xs uppercase tracking-widest h-14 px-10 border-none transition-colors"
          >
            Créer mon premier acte
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.animate-blink {
  animation: blink 0.9s step-start infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .animate-blink {
    animation: none;
  }
}
</style>
