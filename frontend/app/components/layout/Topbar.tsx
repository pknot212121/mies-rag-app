import React, { useState, useEffect } from "react";
import { LogOut } from "lucide-react";
import { useAuth } from "../AuthProvider";
import { useNavigate } from "react-router";
import { useApi } from "../../hooks/useApi";

const Topbar: React.FC = () => {
  const auth = useAuth();
  const navigate = useNavigate();
  const apiFetch = useApi();

  const [message, setMessage] = useState<string | null>(null);
  const [name, setName] = useState("");

  useEffect(() => {
    async function fetchProfile() {
      try {
        const res = await apiFetch("/auth/me");
        if (res.ok) {
          const data = await res.json();
          setName(data.name);
        }
      } catch {
        // handle error silently or show message
      }
    }
    fetchProfile();
  }, [apiFetch]);

  const handleLogout = async () => {
    try {
      const res = await apiFetch("/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      if (res.ok) {
        setMessage("Logged out successfully");
        navigate("/");
        auth.logout();
      } else {
        setMessage("Logout failed");
      }
    } catch (error) {
      setMessage("Logout failed: " + error);
    }
  };

  return (
    <>
      <div className="w-full flex justify-between items-center bg-gray-200 dark:bg-gray-800 p-4 shadow-sm border-b border-gray-300 dark:border-gray-700">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Welcome, {name}!
        </h1>
        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 text-red-600 dark:text-red-400 px-3 py-2 rounded hover:bg-red-100 dark:hover:bg-red-700 transition"
          aria-label="Logout"
        >
          <LogOut className="h-4 w-4" />
          <span>Logout</span>
        </button>
      </div>

      {message && (
        <div className="fixed top-4 right-4 bg-gray-800 text-white p-3 rounded shadow-lg flex items-center">
          <span>{message}</span>
          <button
            onClick={() => setMessage(null)}
            className="ml-4 text-red-400 font-bold hover:text-red-600 transition"
            aria-label="Close message"
          >
            ×
          </button>
        </div>
      )}
    </>
  );
};

export default Topbar;
