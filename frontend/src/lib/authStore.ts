"use client";

import { create } from "zustand";

interface AuthState {
  isAuthenticated: boolean;
  setAuthenticated: (authenticated: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated:
    typeof window !== "undefined"
      ? !!localStorage.getItem("access_token")
      : false,

  setAuthenticated: (authenticated) =>
    set({ isAuthenticated: authenticated }),
}));