"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
};

type AuthContextValue = {
  user: CurrentUser | null;
  isLoading: boolean;
  logout: () => void;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isLoading: true,
  logout: () => {},
  refresh: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function refresh() {
    const token = typeof window !== "undefined" ? window.localStorage.getItem("pdf360_access_token") : null;
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const { data } = await apiClient.get<CurrentUser>("/auth/me");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  function logout() {
    window.localStorage.removeItem("pdf360_access_token");
    window.localStorage.removeItem("pdf360_refresh_token");
    setUser(null);
    window.location.href = "/login";
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
