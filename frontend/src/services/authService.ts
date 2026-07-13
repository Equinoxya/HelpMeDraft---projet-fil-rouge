import api from "./api";

export interface LoginPayload {
  email: string;
  mdp: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: {
    user_id: string;
    email: string;
    firstname: string;
    lastname: string;
  };
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/auth/login", payload);
  return response.data;
}
