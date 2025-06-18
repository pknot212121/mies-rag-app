import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { Menu, Plus, Play  } from "lucide-react";
import { useAuth } from "../AuthProvider";
import { useApi } from "../../hooks/useApi";

interface SidebarProps {
  open: boolean;
  toggle: () => void;
}

interface Job {
  id: number;
  name: string;
}

const Sidebar: React.FC<SidebarProps> = ({ open, toggle }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const auth = useAuth();
  const navigate = useNavigate();
  const apiFetch = useApi();

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await apiFetch("/jobs");
        if (res.ok) {
          const data = await res.json();
          setJobs(data);
        }
      } catch (err) {
        // Możesz tu obsłużyć błąd np. toast
      }
    }
    fetchJobs();
  }, [apiFetch]);

  return (
    <div
      className={`transition-all duration-300 bg-gray-200 dark:bg-gray-800 border-r border-gray-300 dark:border-gray-700 shadow-sm flex flex-col ${
        open ? "w-64 min-w-[16rem] max-w-[16rem]" : "w-16 min-w-[6rem] max-w-[6rem]"
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-300 dark:border-gray-700">
        <button
          onClick={toggle}
          className="text-gray-900 dark:text-gray-100 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
          aria-label="Toggle sidebar"
        >
          <Menu />
        </button>
        {open && (
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            Jobs
          </span>
        )}
      </div>

      <div className="p-4 space-y-3 flex-grow overflow-auto">
        <button
          onClick={() => navigate("/dashboard")}
          className="w-full flex items-center justify-center space-x-2 border border-gray-400 dark:border-gray-600 rounded py-2 text-gray-900 dark:text-gray-100 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        >
          <Plus className="h-4 w-4" />
          {open && <span>New Job</span>}
        </button>

        <button
          onClick={() => navigate("/dashboard/job/demo")}
          className="w-full flex items-center justify-center space-x-2 rounded py-2 bg-blue-600 text-white font-semibold hover:bg-blue-700 transition"
        >
          <Play className="h-4 w-4" />
          {open && <span>Demo</span>}
        </button>

        <div className="mt-4 space-y-2">
          {jobs.length === 0 ? (
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
              No jobs yet. Click "New Job" to create one.
            </div>
          ) : (
            jobs.map((job) => (
              <button
                key={job.id}
                onClick={() => navigate(`/dashboard/job/${job.id}`)}
                className="w-full flex items-center px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 transition whitespace-nowrap overflow-hidden text-ellipsis"
                title={open ? `#${job.id}_${job.name}` : `#${job.id}`}
              >
                {open ? `#${job.id}_${job.name}` : (
                  <span className="truncate w-full text-center">#{job.id}</span>
                )}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );

};

export default Sidebar;
