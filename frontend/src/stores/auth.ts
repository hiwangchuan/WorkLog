import { defineStore } from "pinia";
import { apiGet, apiPost } from "@/api/http";

export interface User {
  id: number;
  username: string;
  email?: string;
  nickname?: string;
}

interface AuthState {
  token: string;
  user: User | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: localStorage.getItem("worklog_token") || "",
    user: JSON.parse(localStorage.getItem("worklog_user") || "null")
  }),
  actions: {
    async login(username: string, password: string) {
      const data = await apiPost<{ access_token: string; user: User }>("/auth/login", { username, password });
      this.token = data.access_token;
      this.user = data.user;
      localStorage.setItem("worklog_token", this.token);
      localStorage.setItem("worklog_user", JSON.stringify(this.user));
    },
    async register(payload: { username: string; password: string; email?: string; nickname?: string }) {
      const requestPayload = {
        username: payload.username.trim(),
        password: payload.password,
        email: payload.email?.trim() || undefined,
        nickname: payload.nickname?.trim() || undefined
      };
      const data = await apiPost<{ access_token: string; user: User }>("/auth/register", requestPayload);
      this.token = data.access_token;
      this.user = data.user;
      localStorage.setItem("worklog_token", this.token);
      localStorage.setItem("worklog_user", JSON.stringify(this.user));
    },
    async loadMe() {
      if (!this.token) return;
      this.user = await apiGet<User>("/auth/me");
      localStorage.setItem("worklog_user", JSON.stringify(this.user));
    },
    logout() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("worklog_token");
      localStorage.removeItem("worklog_user");
    }
  }
});
