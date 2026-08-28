import api from "./api";
import type {
  AdminUser,
  AdminUserListResponse,
  UpdateUserPayload,
  AdminStats,
} from "../types/admin";

async function listUsers(
  page = 1,
  per_page = 20,
): Promise<AdminUserListResponse> {
  const response = await api.get<AdminUserListResponse>("/admin/users", {
    params: { page, per_page },
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

async function removeUser(userId: string): Promise<void> {
  await api.delete(`/admin/users/${userId}`);
}

async function stats(): Promise<AdminStats> {
  const response = await api.get<AdminStats>("/admin/stats");
  return response.data;
}

export default { listUsers, updateUser, removeUser, stats };
