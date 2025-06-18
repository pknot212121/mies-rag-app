import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { useAuth } from "../components/AuthProvider";
import { useApi } from "../hooks/useApi";
import QuestionHeader from "../components/QuestionHeader";
import AnswerCell from "../components/AnswerCell";
import FileCell from "../components/FileCell";

interface Question {
  id: number;
  text: string;
}
interface File {
  id: number;
  filename: string;
}
interface Answer {
  id: number;
  file_id: number;
  question_id: number;
}

const JobDetails = () => {
  const { id } = useParams<{ id: string }>();
  const auth = useAuth();
  const apiFetch = useApi();

  const [jobName, setJobName] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [answersMeta, setAnswersMeta] = useState<Answer[]>([]);
  const [jobStatus, setJobStatus] = useState<string>("pending");
  const [loadingReport, setLoadingReport] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setJobName("");
      setQuestions([]);
      setFiles([]);
      setAnswersMeta([]);
      try {
        const res = await apiFetch(`/jobs/${id}`);
        const data = await res.json();
        setJobName(data.name);
        setQuestions(data.questions);
        setFiles(data.files);
        setAnswersMeta(data.answers);
      } catch (e) {
        console.error("Failed to load job details:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, apiFetch]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const checkStatus = async () => {
      try {
        const res = await apiFetch(`/jobs/${id}/status`);
        const data = await res.json();
        setJobStatus(data.status);

        if (data.status === "done" && interval) {
          clearInterval(interval);
        }
      } catch (e) {
        console.error("Failed to fetch job status:", e);
      }
    };

    checkStatus();
    interval = setInterval(checkStatus, 5000);

    return () => clearInterval(interval);
  }, [id, apiFetch]);

  const handleDownloadReport = async (type: "encoded" | "detailed") => {
    setLoadingReport(true);
    try {
      const job_id = id === "demo" ? 1 : id;
      const response = await apiFetch(`/files/main_${type}_raport/${job_id}`, {
        method: "GET",
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `main_${type}_raport_#${id}_${jobName}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Błąd podczas pobierania raportu:", error);
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div className="p-2 w-full h-full bg-gray-100 dark:bg-gray-950 flex flex-col rounded">
      <div className="max-w-full mx-auto bg-white dark:bg-gray-900 p-6 rounded-xl shadow-lg space-y-4 h-full flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-serif font-bold text-gray-900 dark:text-white">
            {loading ? "Loading..." : jobName}
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => handleDownloadReport("encoded")}
              disabled={jobStatus !== "done" || loadingReport}
              title="Contains only encoded answers"
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                jobStatus === "done" && !loadingReport
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : "bg-gray-400 dark:bg-gray-700 text-gray-200 cursor-not-allowed"
              }`}
            >
              {loadingReport ? "Generating..." : "Download Encoded Report"}
            </button>

            <button
              onClick={() => handleDownloadReport("detailed")}
              disabled={jobStatus !== "done" || loadingReport}
              title="Includes encoded, full text, and contextual citations"
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                jobStatus === "done" && !loadingReport
                  ? "bg-green-600 hover:bg-green-700 text-white"
                  : "bg-gray-400 dark:bg-gray-700 text-gray-200 cursor-not-allowed"
              }`}
            >
              {loadingReport ? "Generating..." : "Download Detailed Report"}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-full">
            <div className="text-gray-500 dark:text-gray-300 animate-pulse">Loading data...</div>
          </div>
        ) : (
          <div
            role="region"
            aria-labelledby="tableCaption"
            tabIndex={0}
            className="w-full max-h-[98vh] overflow-auto"
          >
            <table className="table-fixed w-full text-[1rem] font-serif border-separate border-spacing-0">
              <thead>
                <tr>
                  <th className="sticky top-0 left-0 z-20 bg-white dark:bg-gray-900 p-1 w-[200px] h-[150px] text-gray-800 dark:text-gray-200">
                    <div className="bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-serif font-medium p-3 rounded h-full w-full leading-snug text-ellipsis overflow-hidden break-words line-clamp-[6] shadow-sm"></div>
                  </th>
                  {questions.map((q) => (
                    <th
                      key={q.id}
                      className="sticky top-0 z-10 bg-white dark:bg-gray-900 p-1 text-left w-[250px] h-[150px] text-gray-800 dark:text-gray-200"
                    >
                      <QuestionHeader question={q} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr key={file.id} className="h-[150px]">
                    <th className="sticky left-0 z-10 bg-white dark:bg-gray-900 p-1 font-light italic text-left w-[250px] h-[150px] text-gray-800 dark:text-gray-200">
                      <FileCell file={file} jobId={id} />
                    </th>
                    {questions.map((q) => {
                      const answerMeta = answersMeta.find(
                        (a) => a.question_id === q.id && a.file_id === file.id
                      );
                      return (
                        <td
                          key={`${file.id}_${q.id}`}
                          className="p-1 text-center align-top w-[250px] h-[150px] text-gray-800 dark:text-gray-100 bg-white dark:bg-gray-900"
                        >
                          <AnswerCell answerMeta={answerMeta} />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobDetails;
