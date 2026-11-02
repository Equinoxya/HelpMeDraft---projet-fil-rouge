<script setup lang="ts">
import {
  ref,
  computed,
  nextTick,
  onMounted,
  onBeforeUnmount,
  onUnmounted,
} from "vue";
import adminService from "../services/adminService";
import type {
  ActionAdmin,
  AdminUser,
  AdminStats,
  EntreeJournal,
  UserRole,
} from "../types/admin";
import { useAuthStore } from "../stores/auth";
import { messageErreur } from "../utils/erreurs";

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

// ── Recherche de comptes ────────────────────────────────────────────────────
const recherche = ref("");
let minuterieRecherche: ReturnType<typeof setTimeout> | undefined;

/**
 * Temporisation : sans elle, chaque frappe déclenche une requête, et les
 * réponses peuvent revenir dans le désordre — la liste affiche alors le
 * résultat d'une recherche plus ancienne que ce qui est tapé.
 */
function rechercheModifiee(valeur: string) {
  recherche.value = valeur;
  clearTimeout(minuterieRecherche);
  minuterieRecherche = setTimeout(() => {
    page.value = 1; // sinon on reste sur une page qui n'existe plus après filtrage
    fetchAll();
  }, 300);
}

onUnmounted(() => clearTimeout(minuterieRecherche));

// ── Journal d'administration ────────────────────────────────────────────────
const journal = ref<EntreeJournal[]>([]);
const journalTotal = ref(0);
const journalPage = ref(1);
const journalAction = ref<ActionAdmin | null>(null);
const journalRetention = ref(0);
const JOURNAL_PER_PAGE = 10;

const journalTotalPages = computed(() =>
  Math.max(1, Math.ceil(journalTotal.value / JOURNAL_PER_PAGE)),
);

const LIBELLES_ACTION: Record<ActionAdmin, string> = {
  role: "rôle",
  quota: "quota",
  suppression: "suppression",
};

async function fetchJournal() {
  try {
    const reponse = await adminService.journal(
      journalPage.value,
      JOURNAL_PER_PAGE,
      journalAction.value,
    );
    journal.value = reponse.items;
    journalTotal.value = reponse.total;
    journalRetention.value = reponse.retention_jours;
  } catch (err) {
    // L'échec du journal ne doit pas masquer la liste des comptes, qui est
    // l'outil principal de cet écran.
    errorMessage.value = messageErreur(
      err,
      "Le journal d'administration n'a pas pu être chargé.",
    );
  }
}

function allerPageJournal(cible: number) {
  if (cible < 1 || cible > journalTotalPages.value) return;
  journalPage.value = cible;
  fetchJournal();
}

function filtrerJournal(action: ActionAdmin | null) {
  journalAction.value = action;
  journalPage.value = 1;
  fetchJournal();
}

function formaterDate(iso: string): string {
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ── Confirmation de suppression ─────────────────────────────────────────────
const compteASupprimer = ref<AdminUser | null>(null);
const confirmationSaisie = ref("");
const champConfirmation = ref<HTMLInputElement | null>(null);

// Le bouton qui a ouvert la boîte, pour y ramener le focus en sortant. Sans
// cela, fermer la boîte renvoie le focus au début du document, et il faut
// retraverser tout l'écran pour revenir à la ligne qu'on regardait.
let declencheur: HTMLElement | null = null;

/**
 * Le bouton ne s'active que si l'email est recopié. La comparaison ignore la
 * casse, comme celle du serveur : exiger la casse exacte ferait échouer une
 * confirmation pourtant juste.
 */
const confirmationValide = computed(
  () =>
    compteASupprimer.value !== null &&
    confirmationSaisie.value.trim().toLowerCase() ===
      compteASupprimer.value.email.toLowerCase(),
);

function demanderSuppression(user: AdminUser) {
  declencheur = document.activeElement as HTMLElement | null;
  compteASupprimer.value = user;
  confirmationSaisie.value = "";

  // Le focus DOIT entrer dans la boîte. Vérifié au navigateur : sans cette
  // ligne, il reste sur le bouton « Supprimer » de la ligne du tableau — un
  // lecteur d'écran n'annonce donc pas l'ouverture, et il faut tabuler tout
  // l'écran pour atteindre le champ. axe-core ne détecte pas ce défaut.
  nextTick(() => champConfirmation.value?.focus());
}

function annulerSuppression() {
  compteASupprimer.value = null;
  confirmationSaisie.value = "";
  nextTick(() => declencheur?.focus());
}

/**
 * Échap ferme la boîte.
 *
 * L'écoute est posée sur le DOCUMENT et non sur le conteneur de la boîte :
 * un `@keydown.esc` sur un `div` n'est déclenché que si ce div a le focus, ce
 * qui n'est jamais garanti. Même mécanique que la fermeture du menu mobile
 * dans Nav.vue.
 */
function auClavier(evenement: KeyboardEvent) {
  if (evenement.key === "Escape" && compteASupprimer.value !== null) {
    annulerSuppression();
  }
}

onMounted(() => document.addEventListener("keydown", auClavier));
onBeforeUnmount(() => document.removeEventListener("keydown", auClavier));

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / PER_PAGE)),
);

async function fetchAll() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const [statsResponse, usersResponse] = await Promise.all([
      adminService.stats(),
      adminService.listUsers(page.value, PER_PAGE, recherche.value),
      fetchJournal(),
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
  } catch (err) {
    errorMessage.value = messageErreur(err, "La mise à jour du rôle a échoué.");
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
  } catch (err) {
    errorMessage.value = messageErreur(
      err,
      "La mise à jour du quota a échoué.",
    );
  } finally {
    savingUserId.value = null;
  }
}

/**
 * Supprime le compte retenu dans la boîte de confirmation.
 *
 * `window.confirm` a été remplacé par une boîte où il faut RECOPIER l'email :
 * une alerte où « OK » est la réponse par défaut ne protège de rien, on la
 * valide par réflexe. L'email recopié est aussi envoyé au serveur, qui le
 * compare en base — la garde ne vit donc pas seulement dans le navigateur.
 */
async function confirmerSuppression() {
  const user = compteASupprimer.value;
  if (user === null || !confirmationValide.value) return;

  deletingUserId.value = user.id;
  errorMessage.value = "";
  try {
    await adminService.removeUser(user.id, confirmationSaisie.value.trim());
    annulerSuppression();
    await fetchAll();
  } catch (err) {
    errorMessage.value = messageErreur(err, "La suppression a échoué.");
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
          class="font-mono text-xs uppercase tracking-[0.2em] text-[#C4341C] font-bold block mb-2"
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
        class="mb-6 p-4 border border-[#C4341C] bg-[#C4341C]/10 font-mono text-xs text-[#C4341C] font-bold"
        role="alert"
      >
        {{ errorMessage }}
      </div>

      <div
        v-if="isLoading"
        class="p-12 text-center font-mono text-xs uppercase tracking-widest text-[#111111]/60 flex flex-col items-center gap-3"
      >
        <span
          class="w-6 h-6 border-2 border-[#111111]/20 border-t-[#C4341C] rounded-full animate-spin"
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
          <div
            class="p-4 sm:p-6 border-b border-[#111111]/20 flex flex-col sm:flex-row sm:items-end gap-3"
          >
            <div class="flex-1">
              <!-- Étiquette VISIBLE et non un simple placeholder : celui-ci
                   disparaît à la saisie, et n'est pas une étiquette (RGAA 11.1). -->
              <label
                for="recherche-comptes"
                class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60 block mb-2"
              >
                Rechercher un compte
              </label>
              <input
                id="recherche-comptes"
                type="search"
                :value="recherche"
                maxlength="128"
                placeholder="email, prénom ou nom"
                class="w-full sm:max-w-md h-10 px-3 bg-[#F4F1EA] border border-[#111111] font-mono text-xs"
                @input="
                  rechercheModifiee(($event.target as HTMLInputElement).value)
                "
              />
            </div>
            <p
              class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60"
              aria-live="polite"
            >
              {{ total }} compte{{ total > 1 ? "s" : "" }}
              {{ recherche ? "trouvé" + (total > 1 ? "s" : "") : "" }}
            </p>
          </div>
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
                    class="font-mono text-[10px] uppercase font-bold px-3 py-2 tracking-wider transition-colors disabled:opacity-50"
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
                  <!--
                    Le libellé est porté par aria-label plutôt que par une
                    <label> visible : la colonne du tableau annonce déjà
                    « Quota » pour qui voit l'écran, mais le champ reste sans
                    nom pour un lecteur d'écran, qui le rencontre hors de ce
                    contexte. Le nom cite l'utilisateur concerné, car la page
                    en affiche autant que de lignes.
                  -->
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    :aria-label="`Quota IA quotidien de ${user.email}`"
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
                    class="font-mono text-xs uppercase tracking-wider px-3 py-1.5 border border-[#C4341C] text-[#C4341C] hover:bg-[#C4341C] hover:text-[#F4F1EA] disabled:opacity-50 transition-colors"
                    @click="demanderSuppression(user)"
                  >
                    {{ deletingUserId === user.id ? "…" : "Supprimer" }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <p
            v-if="users.length === 0"
            class="p-8 text-center font-mono text-xs uppercase tracking-wider text-[#111111]/60"
          >
            Aucun compte ne correspond à « {{ recherche }} ».
          </p>

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

        <!-- JOURNAL D'ADMINISTRATION -->
        <section
          class="mt-12 bg-[#FAF8F5] border-2 border-[#111111] shadow-[8px_8px_0px_0px_rgba(17,17,17,1)]"
        >
          <div
            class="p-4 sm:p-6 border-b-2 border-[#111111] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
          >
            <div>
              <h2
                class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#C4341C]"
              >
                [ Journal d'administration ]
              </h2>
              <p class="font-mono text-[10px] text-[#111111]/60 mt-1">
                Lecture seule · conservé {{ journalRetention }} jours
              </p>
            </div>

            <!-- Filtre en boutons et non en <select> : trois valeurs, et l'état
                 courant reste visible sans ouvrir la liste. -->
            <div
              class="flex flex-wrap gap-2"
              role="group"
              aria-label="Filtrer le journal par type d'action"
            >
              <button
                type="button"
                :aria-pressed="journalAction === null"
                class="font-mono text-[10px] uppercase tracking-wider px-3 py-2 border border-[#111111] transition-colors"
                :class="
                  journalAction === null
                    ? 'bg-[#111111] text-[#F4F1EA]'
                    : 'hover:bg-[#111111]/10'
                "
                @click="filtrerJournal(null)"
              >
                Tout
              </button>
              <button
                v-for="(libelle, action) in LIBELLES_ACTION"
                :key="action"
                type="button"
                :aria-pressed="journalAction === action"
                class="font-mono text-[10px] uppercase tracking-wider px-3 py-2 border border-[#111111] transition-colors"
                :class="
                  journalAction === action
                    ? 'bg-[#111111] text-[#F4F1EA]'
                    : 'hover:bg-[#111111]/10'
                "
                @click="filtrerJournal(action)"
              >
                {{ libelle }}
              </button>
            </div>
          </div>

          <ul v-if="journal.length" class="divide-y divide-[#111111]/10">
            <li
              v-for="entree in journal"
              :key="entree.id_action"
              class="p-4 sm:px-6 flex flex-col sm:flex-row sm:items-baseline gap-1 sm:gap-4 font-mono text-xs"
            >
              <time
                :datetime="entree.created_at"
                class="text-[#111111]/60 shrink-0 w-28"
              >
                {{ formaterDate(entree.created_at) }}
              </time>
              <span class="flex-1">
                <strong class="font-bold">{{ entree.acteur_email }}</strong>
                <span class="text-[#C4341C] font-bold mx-1">
                  {{ LIBELLES_ACTION[entree.action] }}
                </span>
                <!-- La cible est affichée depuis la COPIE de son email : elle
                     reste lisible après la suppression du compte, ce qui est
                     précisément le cas où cette ligne sert. -->
                <span>{{ entree.cible_email }}</span>
                <span
                  v-if="entree.avant !== null && entree.apres !== null"
                  class="text-[#111111]/60"
                >
                  · {{ entree.avant }} → {{ entree.apres }}
                </span>
              </span>
            </li>
          </ul>

          <p
            v-else
            class="p-8 text-center font-mono text-xs uppercase tracking-wider text-[#111111]/60"
          >
            Aucune action enregistrée.
          </p>

          <div
            v-if="journalTotalPages > 1"
            class="p-4 sm:p-6 border-t border-[#111111]/20 flex items-center justify-between"
          >
            <button
              type="button"
              :disabled="journalPage === 1"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 transition-colors"
              @click="allerPageJournal(journalPage - 1)"
            >
              ← Précédent
            </button>
            <span class="font-mono text-xs uppercase text-[#111111]/70">
              Page {{ journalPage }} / {{ journalTotalPages }}
            </span>
            <button
              type="button"
              :disabled="journalPage === journalTotalPages"
              class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] disabled:opacity-30 transition-colors"
              @click="allerPageJournal(journalPage + 1)"
            >
              Suivant →
            </button>
          </div>
        </section>
      </template>
    </div>

    <!-- CONFIRMATION DE SUPPRESSION -->
    <!-- Remplace un window.confirm, où « OK » est la réponse par défaut et se
         valide par réflexe. Ici, il faut recopier l'email, et cet email part
         aussi au serveur, qui le compare en base. -->
    <div
      v-if="compteASupprimer"
      class="fixed inset-0 z-50 flex items-center justify-center bg-[#111111]/70 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="titre-suppression"
    >
      <div
        class="w-full max-w-lg bg-[#FAF8F5] border-2 border-[#111111] shadow-[8px_8px_0px_0px_rgba(17,17,17,1)] p-6 sm:p-8"
      >
        <h2
          id="titre-suppression"
          class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#C4341C] mb-4"
        >
          [ Supprimer définitivement ce compte ]
        </h2>

        <p class="font-serif text-base mb-4">
          <strong>{{ compteASupprimer.email }}</strong>
          — {{ compteASupprimer.firstname }} {{ compteASupprimer.lastname }}
        </p>

        <p class="font-mono text-xs text-[#111111]/80 mb-6 leading-relaxed">
          Partiront avec ce compte :
          <strong>{{ compteASupprimer.nb_documents }} document(s)</strong>, ses
          dossiers,
          <strong>{{ compteASupprimer.nb_appels_ia }} appel(s) IA</strong>, ses
          consentements et ses sessions. <strong>Irréversible.</strong>
        </p>

        <label
          for="confirmation-email"
          class="font-mono text-[10px] uppercase tracking-wider text-[#111111]/60 block mb-2"
        >
          Taper l'email du compte pour confirmer
        </label>
        <input
          id="confirmation-email"
          ref="champConfirmation"
          v-model="confirmationSaisie"
          type="text"
          autocomplete="off"
          class="w-full h-10 px-3 bg-[#F4F1EA] border border-[#111111] font-mono text-xs mb-6"
          @keydown.enter="confirmerSuppression"
        />

        <div class="flex flex-wrap justify-end gap-3">
          <button
            type="button"
            class="font-mono text-xs uppercase tracking-wider border border-[#111111] px-4 py-2 hover:bg-[#111111] hover:text-[#F4F1EA] transition-colors"
            @click="annulerSuppression"
          >
            Annuler
          </button>
          <button
            type="button"
            :disabled="!confirmationValide || deletingUserId !== null"
            class="font-mono text-xs uppercase tracking-wider px-4 py-2 border border-[#C4341C] bg-[#C4341C] text-[#F4F1EA] hover:bg-[#A72C18] disabled:opacity-40 transition-colors"
            @click="confirmerSuppression"
          >
            {{ deletingUserId !== null ? "Suppression…" : "Supprimer" }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
