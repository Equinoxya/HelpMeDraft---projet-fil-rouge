import api from "./api";
import type {
  LoginPayload,
  RegisterPayload,
  AuthResponse,
  RegisterResponse,
  RefreshResponse,
} from "../types/auth";

async function register(payload: RegisterPayload): Promise<RegisterResponse> {
  const response = await api.post<RegisterResponse>("/register", payload);
  return response.data;
}

async function login(payload: LoginPayload): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>("/login", payload);
  return response.data;
}

async function refresh(): Promise<RefreshResponse> {
  const response = await api.post<RefreshResponse>("/refresh");
  return response.data;
}

async function logout(): Promise<void> {
  await api.post("/logout");
}

export default {
  register,
  login,
  refresh,
  logout,
};
