import React, { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi";

interface Props {
  file: {
    id: number;
    filename: string;
  };
  jobId: string | undefined;
}

const FileCell: React.FC<Props> = ({ file, jobId }) => {
  const [loadingReport, setLoadingReport] = useState(false);
  const [jobStatus, setJobStatus] = useState<string>("pending");
  const apiFetch = useApi();

  useEffect(() => {
    const fetchJobStatus = async () => {
      try {
        const res = await apiFetch(`/jobs/${jobId}/status`);
        const data = await res.json();
        setJobStatus(data.status);
        if (data.status === "done" && interval) {
          clearInterval(interval);
        }
      } catch (e) {
        console.error("Failed to fetch job status:", e);
      }
    };

    fetchJobStatus();
    const interval = setInterval(fetchJobStatus, 5000);
    return () => clearInterval(interval);
  }, [jobId, apiFetch]);

  const handleDownloadReport = async (type: "file" | "json" | "md") => {
    setLoadingReport(true);
    try {
      let endpoint = "";
      let filename = "";

      switch (type) {
        case "file":
          endpoint = `/files/${file.id}`;
          filename = file.filename;
          break;
        case "json":
          endpoint = `/files/partial_report/${file.id}/json`;
          filename = file.filename.replace(".pdf", "") + "_report.json";
          break;
        case "md":
          endpoint = `/files/partial_report/${file.id}/md`;
          filename = file.filename.replace(".pdf", "") + "_report.md";
          break;
        default:
          throw new Error("Invalid report type");
      }

      const response = await apiFetch(endpoint, { method: "GET" });
      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Błąd podczas pobierania raportu:", error);
    } finally {
      setLoadingReport(false);
    }
  };

  const isDisabled = jobStatus !== "done" || loadingReport;

  return (
    <div className="bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 p-3 rounded h-full flex flex-col justify-between shadow-sm">
      <div
        className="font-serif font-medium break-words overflow-hidden text-ellipsis line-clamp-4 mb-3"
        title={file.filename}
      >
        {file.filename}
      </div>

      <div className="flex flex-col gap-2">
        <button
          onClick={() => handleDownloadReport("file")}
          className={`text-xs py-1 px-2 rounded font-semibold transition ${
            isDisabled
              ? "bg-gray-400 dark:bg-gray-600 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white"
          }`}
          disabled={isDisabled}
          title="Download the source file"
        >
          {loadingReport ? "Loading..." : "Download File"}
        </button>

        <button
          onClick={() => handleDownloadReport("json")}
          className={`text-xs py-1 px-2 rounded font-semibold transition ${
            isDisabled
              ? "bg-gray-400 dark:bg-gray-600 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700 text-white"
          }`}
          disabled={isDisabled}
          title="Download partial JSON report for this file"
        >
          {loadingReport ? "Loading..." : "Download JSON Report"}
        </button>

        <button
          onClick={() => handleDownloadReport("md")}
          className={`text-xs py-1 px-2 rounded font-semibold transition ${
            isDisabled
              ? "bg-gray-400 dark:bg-gray-600 cursor-not-allowed"
              : "bg-purple-600 hover:bg-purple-700 text-white"
          }`}
          disabled={isDisabled}
          title="Download partial Markdown report for this file"
        >
          {loadingReport ? "Loading..." : "Download MD Report"}
        </button>
      </div>
    </div>
  );
}

export default FileCell;
