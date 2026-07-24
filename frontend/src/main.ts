import { createApp } from "vue";
import { createPinia } from "pinia";
import "./style.css";
import App from "./App.vue";
import router from "./index.ts";
import { useAuthStore } from "./stores/auth.ts";

const app = createApp(App);
app.use(createPinia());
const authStore = useAuthStore();

authStore.initialize().finally(() => {
  app.use(router);
  app.mount("#app");
});
