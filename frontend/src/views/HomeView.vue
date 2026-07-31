<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

// Effet machine à écrire pour le mockup du hero
const router = useRouter();
const typedText = ref("");
const fullText =
  "Le bailleur s'engage à restituer le dépôt de garantie dans un délai de deux mois";
let charIndex = 0;

function onRegister() {
  router.push("/register");
}

onMounted(() => {
  const interval = setInterval(() => {
    if (charIndex < fullText.length) {
      typedText.value += fullText[charIndex];
      charIndex++;
    } else {
      clearInterval(interval);
    }
  }, 35);
});

const features = [
  {
    title: "Rédaction assistée par IA",
    description:
      "Décrivez votre besoin en langage naturel, l'IA propose un premier brouillon structuré que vous affinez.",
  },
  {
    title: "Modèles de documents",
    description:
      "Contrats, courriers, mises en demeure : partez d'une base pensée pour votre cas plutôt que d'une page blanche.",
  },
  {
    title: "Sécurité & RGPD",
    description:
      "Vos données restent protégées de bout en bout, avec une infrastructure conforme aux exigences européennes.",
  },
];

const steps = [
  {
    number: "01",
    title: "Décrivez votre besoin",
    description:
      "Expliquez en quelques phrases le document que vous souhaitez rédiger.",
  },
  {
    number: "02",
    title: "L'IA génère un brouillon",
    description:
      "Un premier jet structuré apparaît, prêt à être relu et ajusté.",
  },
  {
    number: "03",
    title: "Éditez et exportez",
    description:
      "Peaufinez le texte directement dans l'éditeur, puis téléchargez votre document.",
  },
];
</script>

<template>
  <div class="bg-[#16233A] text-[#EFEAE0] font-body">
    <!-- HERO -->
    <section
      class="max-w-7xl mx-auto px-6 lg:px-12 pt-20 pb-24 grid lg:grid-cols-2 gap-16 items-center"
    >
      <div>
        <p
          class="font-mono text-xs tracking-[0.2em] uppercase text-[#C9A227] mb-6"
        >
          Rédaction de documents · assistée par IA
        </p>
        <h1 class="font-display text-5xl lg:text-6xl leading-[1.05] mb-6">
          Rédigez vos documents sans partir d'une page blanche.
        </h1>
        <p class="text-lg text-[#EFEAE0]/70 mb-10 max-w-md">
          HelpMeDraft transforme une idée exprimée simplement en un document
          structuré, que vous gardez la main pour relire et ajuster.
        </p>
        <div class="flex flex-wrap gap-4">
          <button
            class="btn bg-[#C9A227] hover:bg-[#B8930F] border-none text-[#16233A] font-semibold px-8"
          >
            Créer un document
          </button>
          <a
            href="#comment-ca-marche"
            class="btn btn-ghost text-[#EFEAE0] hover:bg-[#EFEAE0]/10 px-8"
          >
            Voir comment ça marche
          </a>
        </div>
      </div>

      <!-- Mockup document -->
      <div class="relative">
        <div
          class="bg-[#EFEAE0] text-[#16233A] rounded-lg shadow-2xl p-8 font-body relative overflow-hidden"
        >
          <div class="flex items-center gap-2 mb-6">
            <span class="w-2.5 h-2.5 rounded-full bg-[#D97757]/70"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-[#C9A227]/70"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-[#4C7A73]/70"></span>
            <span
              class="font-mono text-[10px] uppercase tracking-wider text-[#16233A]/40 ml-2"
            >
              contrat-location.docx
            </span>
          </div>

          <p class="text-sm leading-relaxed">
            <span class="font-semibold">Article 4 — Dépôt de garantie.</span>
            {{ typedText }}<span class="animate-blink">|</span>
          </p>

          <!-- Suggestion IA en marge -->
          <div
            class="mt-6 bg-[#4C7A73]/10 border-l-2 border-[#4C7A73] pl-3 py-2 text-xs text-[#4C7A73] font-mono"
          >
            Suggestion IA : préciser le mode de restitution (virement, chèque)
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="bg-[#EFEAE0] text-[#16233A] py-24">
      <div class="max-w-7xl mx-auto px-6 lg:px-12">
        <h2 class="font-display text-3xl lg:text-4xl mb-16 max-w-xl">
          Tout ce qu'il faut pour rédiger vite, sans rédiger seul.
        </h2>
        <div class="grid md:grid-cols-3 gap-10">
          <div v-for="feature in features" :key="feature.title">
            <div class="w-10 h-0.5 bg-[#C9A227] mb-5"></div>
            <h3 class="font-display text-xl mb-3">{{ feature.title }}</h3>
            <p class="text-[#16233A]/70 leading-relaxed">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- COMMENT ÇA MARCHE -->
    <section id="comment-ca-marche" class="py-24">
      <div class="max-w-7xl mx-auto px-6 lg:px-12">
        <h2 class="font-display text-3xl lg:text-4xl mb-16 max-w-xl">
          Comment ça marche
        </h2>
        <div class="grid md:grid-cols-3 gap-10">
          <div v-for="step in steps" :key="step.number">
            <p class="font-mono text-sm text-[#C9A227] mb-3">
              {{ step.number }}
            </p>
            <h3 class="font-display text-xl mb-3">{{ step.title }}</h3>
            <p class="text-[#EFEAE0]/70 leading-relaxed">
              {{ step.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA FINAL -->
    <section class="bg-[#EFEAE0] text-[#16233A] py-24">
      <div class="max-w-7xl mx-auto px-6 lg:px-12 text-center">
        <h2 class="font-display text-3xl lg:text-4xl mb-6">
          Prêt à rédiger votre premier document ?
        </h2>
        <p class="text-[#16233A]/70 mb-10 max-w-md mx-auto">
          Aucune carte bancaire nécessaire pour commencer.
        </p>
        <button
          class="btn bg-[#16233A] hover:bg-[#0F1826] border-none text-[#EFEAE0] font-semibold px-10"
          v-on:click="onRegister"
        >
          Inscrivez-vous gratuitement
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap");

.font-display {
  font-family: "Fraunces", serif;
  font-optical-sizing: auto;
}
.font-body {
  font-family: "Inter", sans-serif;
}
.font-mono {
  font-family: "JetBrains Mono", monospace;
}

.animate-blink {
  animation: blink 1s step-start infinite;
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
