export type UserRole = "user" | "admin";

export interface AdminUser {
  id: string;
  email: string;
  firstname: string;
  lastname: string;
  role: UserRole;
  quota_daily_limit: number;
  created_at: string;
  nb_documents: number;
  nb_appels_ia: number;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  page: number;
  per_page: number;
  total: number;
}

export interface UpdateUserPayload {
  role?: UserRole;
  quota_daily_limit?: number;
}

export interface AdminStats {
  total_users: number;
  total_documents: number;
  total_ia_calls_today: number;
  total_ia_calls_7j: number;
  documents_by_status: {
    brouillon: number;
    a_relire: number;
    termine: number;
  };
}
