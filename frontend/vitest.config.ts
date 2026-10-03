import { fileURLToPath } from "node:url";
import { defineConfig, mergeConfig } from "vitest/config";
import viteConfig from "./vite.config.ts";

// La configuration de test réutilise celle de Vite : mêmes alias, même
// transformation TypeScript, même plugin Vue. C'est l'argument qui a fait
// retenir Vitest plutôt que Jest, qui aurait demandé une seconde chaîne.
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: "jsdom",
      globals: true,
      root: fileURLToPath(new URL("./", import.meta.url)),
      include: ["src/**/__tests__/**/*.spec.ts"],
      coverage: {
        provider: "v8",
        reporter: ["text", "html"],
        include: ["src/utils/**", "src/services/**", "src/stores/**"],
      },
    },
  }),
);
