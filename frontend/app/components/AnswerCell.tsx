import React, { useEffect, useState, useRef } from "react";
import { useApi } from "../hooks/useApi";

interface Props {
  answerMeta?: {
    id: number;
    question_id: number;
    file_id: number;
  };
}

interface PollAnswerStatus {
  status: "pending" | "done" | "error";
  answer_encoded?: string;
}

export interface AnswerContext {
  context: string;
  score: number;
}

export interface AnswerConversationItem {
  question: string;
  answer: string;
}

export interface RagasEvaluation {
  context_recall?: number;
  faithfulness?: number;
  semantic_similarity?: number;
  llm_context_precision_without_reference?: number;
  llm_context_precision_with_reference?: number;
  answer_relevancy?: number;
  answer_correctness?: number;
}

export interface DeepevalEvaluation {
  contextual_precision?: number;
  contextual_recall?: number;
  contextual_relevancy?: number;
  answer_relevancy?: number;
  faithfulness?: number;
}

export interface Evaluation {
  ragas?: Partial<RagasEvaluation>;
  deepeval?: Partial<DeepevalEvaluation>;
}

export interface AnswerDetail {
  filename: string;
  question_text: string;
  question_possible_options: string;
  answer_encoded: string;
  answer_text: string;
  answer_contexts: AnswerContext[];
  answer_conversation: AnswerConversationItem[];
  evaluation?: Evaluation; 
}



const AnswerCell: React.FC<Props> = ({ answerMeta }) => {
  const apiFetch = useApi();
  const [text, setText] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const [showOverlay, setShowOverlay] = useState(false);

  const [fullAnswer, setFullAnswer] = useState<AnswerDetail | null>(null);
  const [fullLoading, setFullLoading] = useState(false);
  const [fullError, setFullError] = useState(false);

  useEffect(() => {
    if (!answerMeta) return;

    const poll = async () => {
      try {
        const res = await apiFetch(`/answers/${answerMeta.id}`);
        if (!res.ok) return;

        const data: PollAnswerStatus = await res.json();
        if ((data.status === "done" || data.status === "error") && data.answer_encoded) {
          setText(data.answer_encoded);
          setLoading(false);
          if (pollingRef.current) clearInterval(pollingRef.current);
        } else {
          setLoading(true);
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    };

    poll();
    pollingRef.current = setInterval(poll, 10000);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [answerMeta, apiFetch]);

  useEffect(() => {
    if (!showOverlay || !answerMeta) return;

    setFullLoading(true);
    setFullError(false);
    setFullAnswer(null);

    const fetchDetails = async () => {
      try {
        const res = await apiFetch(`/answers/${answerMeta.id}/detail`);
        if (!res.ok) throw new Error("Fetch error");
        const data: AnswerDetail = await res.json();
        setFullAnswer(data);
      } catch (e) {
        setFullError(true);
      } finally {
        setFullLoading(false);
      }
    };

    fetchDetails();
  }, [showOverlay, answerMeta, apiFetch]);

  if (!answerMeta) {
    return (
      <div className="p-2 text-gray-400 italic text-center w-[250px] min-h-[60px]">
        brak odpowiedzi
      </div>
    );
  }

return (
  <>
    {/* Preview Box */}
    <div
      className="bg-gray-100 dark:bg-gray-800 text-black dark:text-white text-sm p-2 rounded cursor-pointer h-full w-full relative"
      onClick={() => setShowOverlay(true)}
    >
      {loading ? (
        <span className="text-gray-500 dark:text-gray-400 italic animate-pulse">Loading...</span>
      ) : (
        <>
          <div
            className="whitespace-pre-wrap overflow-hidden"
            style={{
              display: '-webkit-box',
              WebkitBoxOrient: 'vertical',
              WebkitLineClamp: 5,
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
          >
            {text}
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 rounded p-2 text-gray-500 dark:text-gray-400 text-xs mt-2 absolute bottom-1 left-2">
            Click for details
          </div>
        </>
      )}
    </div>

    {/* Overlay with Full Answer */}
    {showOverlay && text && fullAnswer && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[200]">
        <div className="bg-white dark:bg-gray-800 text-black dark:text-white rounded-2xl shadow-2xl max-w-5xl w-[95%] h-[85%] p-0 overflow-hidden relative flex flex-col">

          {/* Close Button */}
          <button
            className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded-full hover:bg-red-700 text-sm font-medium z-[201]"
            onClick={() => setShowOverlay(false)}
          >
            ✕
          </button>

          {/* Sticky Header */}
          <div className="bg-gray-100 dark:bg-gray-700 px-6 py-4 border-b border-gray-300 dark:border-gray-600 sticky top-0 z-10">
            <div className="font-semibold">📄 File: {fullAnswer.filename}</div>
            <div className="font-semibold">❓ Question: {fullAnswer.question_text}</div>
            <div className="font-semibold">
              🔢 Options: {fullAnswer.question_possible_options || "None"}
            </div>
          </div>

          {/* Scrollable Content */}
          <div className="overflow-y-auto px-6 py-4 space-y-6">
            
            {/* Encoded Answer */}
            <section>
              <h2 className="text-lg font-semibold">✅ Encoded Answer</h2>
              <div className="bg-gray-100 dark:bg-gray-700 text-sm p-3 rounded-lg whitespace-pre-wrap">
                {fullAnswer.answer_encoded}
              </div>
            </section>

            {/* Conversation */}
            {fullAnswer.answer_conversation?.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold">💬 Conversation</h2>
                <div className="space-y-4">
                  {fullAnswer.answer_conversation.map((conv, i) => (
                    <div key={i} className="flex flex-col space-y-2">
                      <div className="self-end bg-blue-600 text-white px-4 py-2 rounded-2xl max-w-[75%] text-sm">
                        <strong>Question:</strong> {conv.question}
                      </div>
                      <div className="self-start bg-gray-200 dark:bg-gray-600 px-4 py-2 rounded-2xl max-w-[75%] text-sm text-gray-800 dark:text-gray-100">
                        <strong>Answer:</strong> {conv.answer}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Full Answer */}
            <section>
              <h2 className="text-lg font-semibold">📝 Full Answer</h2>
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg text-sm whitespace-pre-wrap">
                {fullAnswer.answer_text || "No answer provided."}
              </div>
            </section>

            {/* Contexts */}
            {fullAnswer.answer_contexts?.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold">📚 Contexts</h2>
                <ul className="space-y-3">
                  {fullAnswer.answer_contexts.map((ctx, i) => (
                    <li key={i} className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg text-sm">
                      {/* <div className="text-xs text-gray-500 mb-1 italic">
                        Score: {ctx.score.toFixed(2)}
                      </div> */}
                      <div>{ctx.context}</div>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Evaluation */}
            {fullAnswer.evaluation?.ragas && (
              <section>
                <h2 className="text-lg font-semibold">📊 Evaluation</h2>
                
                {/* RAGAS */}
                {fullAnswer.evaluation.ragas && (
                  <div className="mt-2">
                    <h3 className="font-semibold mb-1 text-sm text-gray-600 dark:text-gray-300">
                      RAGAS Evaluation (
                      <a
                        href="https://docs.ragas.io"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline"
                      >
                        https://docs.ragas.io
                      </a>
                      )
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {Object.entries(fullAnswer.evaluation.ragas).map(([key, value]) => (
                        <div key={key} className="bg-gray-100 dark:bg-gray-700 p-2 rounded">
                          <strong>{key}:</strong> {value?.toFixed(3)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* DeepEval */}
                {fullAnswer.evaluation.deepeval && (
                  <div className="mt-4">
                    <h3 className="font-semibold mb-1 text-sm text-gray-600 dark:text-gray-300">
                      DeepEval (
                      <a
                        href="https://deepeval.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline"
                      >
                        https://deepeval.com/
                      </a>
                      )
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {Object.entries(fullAnswer.evaluation.deepeval).map(([key, value]) => (
                        <div key={key} className="bg-gray-100 dark:bg-gray-700 p-2 rounded">
                          <strong>{key}:</strong> {value?.toFixed(3)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </div>
    )}
  </>
);


};

export default AnswerCell;
