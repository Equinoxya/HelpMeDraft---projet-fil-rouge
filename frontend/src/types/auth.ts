export interface LoginPayload {
  email: string;
  mdp: string;
}

export interface RegisterPayload {
  email: string;
  mdp: string;
  firstname: string;
  lastname: string;
  rgpd_consent: boolean;
}

export interface AuthUser {
  id: string;
  email: string;
  firstname: string;
  lastname: string;
}

export interface AuthResponse {
  access_token: string;
  user: AuthUser;
}

export interface RegisterResponse {
  message: string;
  user_id: string;
  email: string;
}

export interface RefreshResponse {
  access_token: string;
}
export interface MeResponse {
  id: string;
  email: string;
  firstname: string;
  lastname: string;
}
