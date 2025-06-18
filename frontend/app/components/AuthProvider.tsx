import { createContext, useContext, useState, useEffect } from "react";

export type AuthContextType = {
  user: string | null;
  token: string | null;
  login: (token: string, user: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (storedToken) setToken(storedToken);
    if (storedUser) setUser(storedUser);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("/auth/refresh", { method: "POST", credentials: "include" })
        .then((res) => res.ok && res.json())
        .then((data) => {
          if (data?.access_token) {
            setToken(data.access_token);
            localStorage.setItem("token", data.access_token);
          }
        })
        .catch(() => {});
    }, 5 * 60 * 1000); // co 5 minut

    return () => clearInterval(interval);
  }, []);

  const login = (newToken: string, newUser: string) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", newUser);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    // fetch("/auth/logout", { method: "POST", credentials: "include" });
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
