<script setup lang="ts">
import Footer from "./components/Footer.vue";
import Nav from "./components/Nav.vue";
</script>

<template>
  <!--
    Lien d'évitement — RGAA 12.7.
    Premier élément focalisable du document, invisible jusqu'à ce qu'il reçoive
    le focus. Sans lui, un utilisateur au clavier traverse les 24 à 25 éléments
    de l'en-tête avant d'atteindre le contenu, et il le refait à chaque page.
  -->
  <a
    href="#contenu"
    class="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:bg-[#111111] focus:text-[#F4F1EA] focus:px-4 focus:py-3 focus:font-mono focus:text-xs focus:uppercase focus:tracking-wider focus:font-bold"
  >
    Aller au contenu principal
  </a>

  <Nav />

  <!--
    La cible du lien d'évitement est posée ici et non dans chaque vue : un
    `id` oublié dans une vue rendrait le lien muet sur cet écran, sans que
    rien ne le signale. `tabindex="-1"` est nécessaire pour qu'un conteneur
    non focalisable puisse recevoir le focus au suivi du lien ; le contour par
    défaut est conservé, c'est lui qui indique où le focus a atterri.
  -->
  <div id="contenu" tabindex="-1">
    <router-view />
  </div>

  <Footer />
</template>
