import React from "react";

interface Props {
  question: {
    id: number;
    text: string;
  };
}

const QuestionHeader: React.FC<Props> = ({ question }) => (
  <div
    className="bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-serif font-medium p-3 rounded h-full w-full leading-snug text-ellipsis overflow-hidden break-words line-clamp-[6] shadow-sm"
    title={question.text}
  >
    {question.text}
  </div>
);

export default QuestionHeader;