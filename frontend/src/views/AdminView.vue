<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import adminService from "../services/adminService";
import type { AdminUser, AdminStats, UserRole } from "../types/admin";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();

const isLoading = ref(false);
const errorMessage = ref("");

const stats = ref<AdminStats | null>(null);
const users = ref<AdminUser[]>([]);
const total = ref(0);
const page = ref(1);
const PER_PAGE = 20;

const savingUserId = ref<string | null>(null);
const deletingUserId = ref<string | null>(null);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / PER_PAGE)),
);

async function fetchAll() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const [statsResponse, usersResponse] = await Promise.all([
      adminService.stats(),
      adminService.listUsers(page.value, PER_PAGE),
    ]);
    stats.value = statsResponse;
    users.value = usersResponse.items;
    total.value = usersResponse.total;
  } catch {
    errorMessage.value = "Impossible de charger les données d'administration.";
  } finally {
    isLoading.value = false;
  }
}

function goToPage(target: number) {
  if (target < 1 || target > totalPages.value) return;
  page.value = target;
  fetchAll();
}

async function toggleRole(user: AdminUser) {
  const newRole: UserRole = user.role === "admin" ? "user" : "admin";
  savingUserId.value = user.id;
  errorMessage.value = "";
  try {
    const updated = await adminService.updateUser(user.id, { role: newRole });
    user.role = updated.role;
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error ?? "La mise à jour du rôle a échoué.";
  } finally {
    savingUserId.value = null;
  }
}

async function updateQuota(user: AdminUser, value: number) {
  if (!Number.isInteger(value) || value < 1 || value > 1000) {
    errorMessage.value = "Le quota doit être un entier entre 1 et 1000.";
    return;
  }
  savingUserId.value = user.id;
  errorMessage.value = "";
  try {
    const updated = await adminService.updateUser(user.id, {
      quota_daily_limit: value,
    });
    user.quota_daily_limit = updated.quota_daily_limit;
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error ?? "La mise à jour du quota a échoué.";
  } finally {
    savingUserId.value = null;
  }
}

async function handleDelete(user: AdminUser) {
  const confirmed = window.confirm(
    `Supprimer définitivement le compte de ${user.firstname} ${user.lastname} (${user.email}) ? Cette action est irréversible.`,
  );
  if (!confirmed) return;

  deletingUserId.value = user.id;
  errorMessage.value = "";
  try {
    await adminService.removeUser(user.id);
    await fetchAll();
  } catch (err: any) {
    errorMessage.value =
      err.response?.data?.error ?? "La suppression a échoué.";
  } finally {
    deletingUserId.value = null;
  }
}

onMounted(fetchAll);
</script>

<template>
  <main
    class="min-h-screen bg-[#F4F1EA] text-[#111111] font-sans antialiased pb-24"
  >
    <div class="max-w-7xl mx-auto px-6 lg:px-12 pt-12 md:pt-16">
      <header class="mb-10 pb-6 border-b-2 border-[#111111]">
        <span
          class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold block mb-2"
        >
          [ Back-office ]
        </span>
        <h1
          class="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#111111]"
        >
          Administration
        </h1>
      </header>

      <div
        v-if="errorMessage"
        class="mb-6 p-4 border border-[#E0533C] bg-[#E0533C]/10 font-mono text-xs text-[#E0533C] font-bold"
        role="alert"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="isLoading"
        class="p-12 text-center font-mono text-xs uppercase tracking-widest text-[#111111]/60 flex flex-col items-center gap-3"
      >
        <span
          class="w-6 h-6 border-2 border-[#111111]/20 border-t-[#E0533C] rounded-full animate-spin"
        ></span>
        Chargement…
      </div>

      <template v-else>
        <!-- STATS -->
        <section
          v-if="stats"
          class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12"
        >
          <article
            class="p-6 bg-[#FAF8F5] border-2 border-[#111111] shadow-[4px_4px_0px_0px_#111111]"
          >
            <p
              class="font-mono text-[11px] uppercase tracking-widest text-[#111111]/60 mb-2"
            >
              Utilisateurs
            </p>
            <p class="font-serif text-4xl text-[#111111]">
              {{ stats.total_users }}
            </p>
          </article>
          <article
            class="p-6 bg-[#FAF8F5] border-2 border-[#111111] shadow-[4px_4px_0px_0px_#111111]"
          >
            <p
              class="font-mono text-[11px] uppercase tracking-widest text-[#111111]/60 mb-2"
            >
              Documents
            </p>
            <p class="font-serif text-4xl text-[#111111]">
              {{ stats.total_documents }}
            </p>
          </article>
          <article
            class="p-6 bg-[#FAF8F5] border-2 border-[#111111] shadow-[4px_4px_0px_0px_#111111]"
          >
            <p
              class="font-mono text-[11px] uppercase tracking-widest text-[#111111]/60 mb-2"
            >
              Appels IA (24h)
            </p>
            <p class="font-serif text-4xl text-[#111111]">
              {{ stats.total_ia_calls_today }}
            </p>
          </article>
          <article
            class="p-6 bg-[#FAF8F5] border-2 border-[#111111] shadow-[4px_4px_0px_0px_#111111]"
          >
            <p
              class="font-mono text-[11px] uppercase tracking-widest text-[#111111]/60 mb-2"
            >
              Appels IA (7j)
            </p>
            <p class="font-serif text-4xl text-[#111111]">
              {{ stats.total_ia_calls_7j }}
            </p>
          </article>
        </section>

        <!-- TABLE UTILISATEURS -->
        <section
          class="bg-[#FAF8F5] border-2 border-[#111111] shadow-[8px_8px_0px_0px_rgba(17,17,17,1)] overflow-x-auto"
        >
          <table class="w-full text-sm">
            <thead>
              <tr
                class="border-b-2 border-[#111111] font-mono text-[10px] uppercase tracking-wider text-[#111111]/60"
              >
                <th class="text-left p-4">Utilisateur</th>
                <th class="text-left p-4">Rôle</th>
                <th class="text-left p-4">Quota IA / 24h</th>
                <th class="text-left p-4">Docs</th>
                <th class="text-left p-4">Appels IA</th>
                <th class="text-right p-4">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#111111]/10">
              <tr v-for="user in users" :key="user.id">
                <td class="p-4">
                  <p class="font-bold">
                    {{ user.firstname }} {{ user.lastname }}
                  </p>
                  <p class="font-mono text-xs text-[#111111]/60">
                    {{ user.email }}
                  </p>
                </td>
                <td class="p-4">
                  <button
                    type="button"
                    :disabled="
                      savingUserId === user.id || user.id === authStore.user?.id
                    "
                    class="font-mono text-[10px] uppercase font-bold px-3 py-1 tracking-wider transition-colors disabled:opacity-50"
                    :class="
                      user.role === 'admin'
                        ? 'bg-[#111111] text-[#F4F1EA]'
                        : 'border border-[#111111] text-[#111111] hover:bg-[#111111]/10'
                    "
                    :title="
                      user.id === authStore.user?.id
                        ? 'Vous ne pouvez pas modifier votre propre rôle'
                        : ''
                    "
                    @click="toggleRole(user)"
                  >
                    {{ user.role === "admin" ? "Admin" : "Utilisateur" }}
                  </button>
                </td>
                <td class="p-4">
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    :value="user.quota_daily_limit"
                    :disabled="savingUserId === user.id"
                    class="w-20 h-9 px-2 bg-[#F4F1EA] border border-[#111111] font-mono text-xs disabled:opacity-50"
                    @change="
                      updateQuota(
                        user,
                        Number(($event.target as HTMLInputElement).value),
                      )
                    "
                  />
                </td>
                <td class="p-4 font-mono text-xs">{{ user.nb_documents }}</td>
                <td class="p-4 font-mono text-xs">{{ user.nb_appels_ia }}</td>
                <td class="p-4 text-right">
                  <button
                    type="button"
                    :disabled="
                      deletingUserId === user.id ||
                      user.id === authStore.user?.id
                    "
                    class="font-mono text-xs uppercase tracking-wider px-3 py-1.5 border border-[#E0533C] text-[#E0533C] hover:bg-[#E0533C] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors"
                    @click="handleDelete(user)"
                  >
                    {{ deletingUserId === user.id ? "…" : "Supprimer" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div
            v-if="totalPages > 1"
            class="p-4 sm:p-6 border-t border-[#111111]/20 flex items-center justify-between"
          >
            <button
              type="button"
              :disabled="page === 1"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 transition-colors"
              @click="goToPage(page - 1)"
            >
              ← Précédent
            </button>
            <span class="font-mono text-xs uppercase text-[#111111]/70">
              Page {{ page }} / {{ totalPages }}
            </span>
            <button
              type="button"
              :disabled="page === totalPages"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 transition-colors"
              @click="goToPage(page + 1)"
            >
              Suivant →
            </button>
          </div>
        </section>
      </template>
    </div>
  </main>
</template>
