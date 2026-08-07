import api from "./api";
import type {
  LoginPayload,
  RegisterPayload,
  AuthResponse,
  RegisterResponse,
  RefreshResponse,
  MeResponse,
} from "../types/auth";

async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>("/auth/register", payload);
  return response.data;
}

async function login(payload: LoginPayload): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>("/auth/login", payload);
  return response.data;
}

async function refresh(): Promise<RefreshResponse> {
  const response = await api.post<RefreshResponse>("/auth/refresh");
  return response.data;
}

async function logout(): Promise<void> {
  await api.post("/auth/logout");
}

async function forgotPassword(email: string): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>(
    "/auth/forgot-password",
    {
      email,
    },
  );
  return response.data;
}

async function resetPassword(
  token: string,
  mdp: string,
): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/auth/reset-password", {
    token,
    mdp,
  });
  return response.data;
}

async function me(token: string): Promise<MeResponse> {
  const response = await api.get<MeResponse>("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export default {
  register,
  login,
  refresh,
  logout,
  forgotPassword,
  resetPassword,
  me,
};
