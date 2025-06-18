import React, { useState } from "react";
import { useNavigate } from "react-router";
import { useApi } from "../hooks/useApi";
import { useAuth } from "../components/AuthProvider";

const JobCreate: React.FC = () => {
  const [name, setName] = useState("");
  const [questions, setQuestions] = useState([
    { text: "", options: [] as string[], showOptions: false },
  ]);
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const apiFetch = useApi();
  const auth = useAuth();
  const navigate = useNavigate();

  const handleQuestionChange = (index: number, value: string) => {
    const newQuestions = [...questions];
    newQuestions[index].text = value;
    setQuestions(newQuestions);
  };

  const addQuestion = () => {
    setQuestions([...questions, { text: "", options: [], showOptions: false }]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const toggleOptions = (index: number) => {
    const newQuestions = [...questions];
    newQuestions[index].showOptions = !newQuestions[index].showOptions;
    setQuestions(newQuestions);
  };

  const addOptionToQuestion = (index: number, option: string) => {
    if (!option.trim()) return;
    const newQuestions = [...questions];
    newQuestions[index].options.push(option);
    setQuestions(newQuestions);
  };

  const removeOptionFromQuestion = (qIdx: number, oIdx: number) => {
    const newQuestions = [...questions];
    newQuestions[qIdx].options.splice(oIdx, 1);
    setQuestions(newQuestions);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const allFiles = Array.from(e.target.files);
      const pdfFiles = allFiles.filter((file) => file.type === "application/pdf");

      if (pdfFiles.length !== allFiles.length) {
        alert("Only PDF files are allowed.");
        return;
      }

      setFiles(pdfFiles);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };


  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      const pdfFiles = droppedFiles.filter((file) => file.type === "application/pdf");

      if (pdfFiles.length !== droppedFiles.length) {
        alert("Only PDF files are allowed.");
        return;
      }

      setFiles((prev) => [...prev, ...pdfFiles]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      alert("Job name is required.");
      return;
    }

    const emptyQuestion = questions.find((q) => !q.text.trim());
    if (emptyQuestion) {
      alert("All questions must have text.");
      return;
    }

    if (files.length === 0) {
      alert("At least one PDF file is required.");
      return;
    }

    const formData = new FormData();
    formData.append("name", name);
    questions.forEach((q) => {
      formData.append(
        "questions",
        JSON.stringify({
          text: q.text,
          possible_options: q.options.length > 0 ? q.options.join(", ") : "None",
        })
      );
    });
    files.forEach((file) => formData.append("files", file));

    try {
      const res = await apiFetch("/jobs", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        navigate(`/dashboard/job/${data.id}`);
      } else {
        console.error("Server error:", res.status);
      }
    } catch (err: any) {
      console.error("Network error:", err.message);
    }
  };

  return (
    <div className="h-full w-full overflow-y-auto p-6 bg-gray-100 dark:bg-gray-900">
      <form
        onSubmit={handleSubmit}
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={() => setDragActive(true)}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        className="max-w-3xl mx-auto bg-white dark:bg-gray-800 p-6 rounded shadow space-y-6"
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Create New Job</h2>

        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Job Name"
          className="w-full p-3 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          required
        />

        {questions.map((q, i) => (
          <div
            key={i}
            className="border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 rounded p-4 space-y-4"
          >
            <div className="flex space-x-2 items-center">
              <input
                type="text"
                value={q.text}
                onChange={(e) => handleQuestionChange(i, e.target.value)}
                placeholder={`Question ${i + 1}`}
                className="flex-grow p-3 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                required
              />
              <button
                type="button"
                onClick={() => removeQuestion(i)}
                className="text-red-600 font-bold text-lg px-3"
              >
                ✕
              </button>
            </div>

            <button
              type="button"
              onClick={() => toggleOptions(i)}
              className="text-sm text-blue-600 hover:underline"
            >
              {q.showOptions ? "Hide Options" : "Add/View Options"}
            </button>

            {q.showOptions && (
              <OptionInput
                index={i}
                onAdd={addOptionToQuestion}
                options={q.options}
                onRemove={removeOptionFromQuestion}
              />
            )}
          </div>
        ))}

        <button
          type="button"
          onClick={addQuestion}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded"
        >
          + Add Question
        </button>

        <label
          htmlFor="file-upload"
          className={`block border-2 border-dashed p-6 rounded cursor-pointer text-center transition ${
            dragActive ? "border-blue-400 bg-blue-50" : "border-gray-300"
          }`}
        >
          <p className="text-gray-700 dark:text-gray-300">
            Drag & Drop PDF files here or click to upload
          </p>
          <input
            id="file-upload"
            type="file"
            multiple
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>

        <ul className="mt-2 text-sm text-gray-600 dark:text-gray-400 space-y-1">
          {files.map((file, idx) => (
            <li
              key={idx}
              className="flex items-center justify-between bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 p-2 rounded"
            >
              <span className="truncate">{file.name}</span>
              <button
                type="button"
                onClick={() => removeFile(idx)}
                className="ml-3 text-red-500 hover:text-red-700 font-bold"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>


        <button
          type="submit"
          className="w-full py-3 bg-blue-600 text-white font-semibold rounded hover:bg-blue-700"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

const OptionInput = ({
  index,
  onAdd,
  options,
  onRemove,
}: {
  index: number;
  onAdd: (index: number, option: string) => void;
  options: string[];
  onRemove: (qIdx: number, oIdx: number) => void;
}) => {
  const [value, setValue] = useState("");

  return (
    <div className="space-y-2">
      <div className="flex space-x-2">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Enter option"
          className="flex-grow p-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100"
        />
        <button
          type="button"
          onClick={() => {
            onAdd(index, value);
            setValue("");
          }}
          className="px-4 py-2 bg-green-500 text-white rounded"
        >
          Add
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {options.map((opt, oIdx) => (
          <span
            key={oIdx}
            className="bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-white px-3 py-1 rounded-full flex items-center"
          >
            {opt}
            <button
              type="button"
              onClick={() => onRemove(index, oIdx)}
              className="ml-2 text-red-500 hover:text-red-700"
            >
              &times;
            </button>
          </span>
        ))}
      </div>
    </div>
  );
};

export default JobCreate;
