import axios from "axios";

function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (envUrl) {
    // Ensure it ends with /api/v1 if the user entered only the origin or omitted the version
    if (!envUrl.includes("/api/v1")) {
      return envUrl.replace(/\/+$/, "") + "/api/v1";
    }
    return envUrl.replace(/\/+$/, "");
  }
  return "http://localhost:8000/api/v1";
}

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
});

// Attaches the access token to every outgoing request, once auth storage
// (Phase 6 frontend integration) writes it to localStorage/cookies.
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem("pdf360_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
