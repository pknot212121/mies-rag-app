import { useAuth } from "../components/AuthProvider";
import { useNavigate } from "react-router";
import { useCallback } from "react";

export function useApi() {
  const auth = useAuth();
  const navigate = useNavigate();

  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const res = await fetch("/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (!res.ok) return null;

      const data = await res.json();
      if (data?.access_token) {
        auth.login(data.access_token, auth.user || "");
        return data.access_token;
      }
    } catch {
      return null;
    }

    return null;
  }, [auth]);

  const apiFetch = useCallback(async (input: RequestInfo, init: RequestInit = {}) => {
    const headers = new Headers(init.headers || {});
    if (auth.token) {
      headers.set("Authorization", `Bearer ${auth.token}`);
    }

    let response = await fetch(input, {
      ...init,
      headers,
      credentials: "include",
    });

    if (response.status === 401) {
      const refreshed = await refreshToken();
      if (refreshed) {
        const newHeaders = new Headers(init.headers || {});
        newHeaders.set("Authorization", `Bearer ${refreshed}`);
        response = await fetch(input, {
          ...init,
          headers: newHeaders,
          credentials: "include",
        });
      } else {
        auth.logout();
        navigate("/");
      }
    }

    return response;
  }, [auth, navigate, refreshToken]);

  return apiFetch;
}
