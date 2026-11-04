import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
        // Pendant du `proxy_cookie_path` de nginx.conf. Le backend pose le
        // cookie de refresh sur « Path=/auth », le chemin qu'il voit après
        // retrait du préfixe. Le navigateur, lui, appelle /api/auth/refresh et
        // ne renverrait donc jamais le cookie : la session ne survivrait pas à
        // un rechargement, et un lien direct vers /admin ou /dashboard
        // retomberait sur /login.
        cookiePathRewrite: { "/auth": "/api/auth" },
      },
    },
  },
});