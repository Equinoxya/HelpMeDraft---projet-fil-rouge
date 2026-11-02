import api from "./api";
import type {
  ActionAdmin,
  AdminUser,
  AdminUserListResponse,
  UpdateUserPayload,
  AdminStats,
  JournalResponse,
} from "../types/admin";

async function listUsers(
  page = 1,
  per_page = 20,
  recherche = "",
): Promise<AdminUserListResponse> {
  const response = await api.get<AdminUserListResponse>("/admin/users", {
    // La recherche vide n'est PAS envoyée : le serveur la traiterait comme une
    // chaîne vide, ce qui revient au même, mais l'URL resterait inutilement
    // encombrée dans les journaux d'accès.
    params: recherche ? { page, per_page, recherche } : { page, per_page },
  });
  return response.data;
}

async function updateUser(
  userId: string,
  payload: UpdateUserPayload,
): Promise<AdminUser> {
  const response = await api.patch<AdminUser>(
    `/admin/users/${userId}`,
    payload,
  );
  return response.data;
}

/**
 * Supprime un compte. `confirmation` doit valoir son email : le serveur le
 * compare en base et refuse sinon. La garde n'est donc pas seulement dans
 * l'interface — un appel direct à l'API sur le mauvais identifiant échoue aussi.
 */
async function removeUser(userId: string, confirmation: string): Promise<void> {
  await api.delete(`/admin/users/${userId}`, { params: { confirmation } });
}

async function journal(
  page = 1,
  per_page = 20,
  action: ActionAdmin | null = null,
): Promise<JournalResponse> {
  const response = await api.get<JournalResponse>("/admin/journal", {
    params: action ? { page, per_page, action } : { page, per_page },
  });
  return response.data;
}

async function stats(): Promise<AdminStats> {
  const response = await api.get<AdminStats>("/admin/stats");
  return response.data;
}

export default { listUsers, updateUser, removeUser, stats, journal };
