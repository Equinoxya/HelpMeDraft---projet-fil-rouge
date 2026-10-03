// ==============================================================================
// HelpMeDraft — configuration ESLint (format « plat », ESLint 9)
// ==============================================================================

import pluginVue from "eslint-plugin-vue";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";
import prettier from "eslint-config-prettier";

export default defineConfigWithVueTs(
  {
    name: "helpmedraft/fichiers",
    files: ["**/*.{ts,mts,tsx,vue}"],
  },
  {
    name: "helpmedraft/ignores",
    ignores: ["dist/**", "coverage/**", "node_modules/**", "*.config.ts"],
  },

  // Règles recommandées pour Vue 3 et TypeScript.
  pluginVue.configs["flat/recommended"],
  vueTsConfigs.recommended,

  // Prettier EN DERNIER : il neutralise les règles de mise en forme d'ESLint.
  // Sans cela, les deux outils se contredisent sur les mêmes lignes, et chaque
  // enregistrement défait le travail du précédent.
  prettier,

  {
    name: "helpmedraft/ajustements",
    rules: {
      // Les variables délibérément inutilisées se préfixent d'un souligné,
      // convention déjà retenue dans index.ts pour `_from`.
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },
);
