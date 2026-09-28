import { useState } from "react";
import type { VoiceQueryResponse } from "../types";

interface TextInputProps {
  onResult: (result: VoiceQueryResponse) => void;
  onError: (error: string) => void;
  onClear: () => void;
}

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8001";

export function TextInput({ onResult, onError, onClear }: TextInputProps) {
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const SUGGESTED_QUESTIONS = [
    "What is Hack Club?",
    "What is GitHub?",
    "What is Docker?",
    "What is FastAPI?",
    "What is Python?",
  ];

  const handleSubmit = async (textToSubmit: string) => {
    if (!textToSubmit.trim()) return;
    
    setIsProcessing(true);
    onClear();
    setQuery(textToSubmit);

    try {
      const response = await fetch(`${API_BASE_URL}/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: textToSubmit,
          language: "English",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || "Text query failed.");
      }

      onResult(data as VoiceQueryResponse);
    } catch (error) {
      console.error(error);
      if (error instanceof Error) {
        onError(error.message);
      } else {
        onError("Unable to connect to the Voxora backend. Please try again.");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col gap-4 mt-8 relative z-10">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit(query)}
          placeholder="Type a question and search..."
          disabled={isProcessing}
          className="flex-1 bg-brand-panel brutal-border brutal-shadow p-4 text-xl font-bold font-mono text-brand-text placeholder-brand-muted focus:outline-none focus:ring-4 focus:ring-brand-primary disabled:opacity-50"
        />
        <button
          onClick={() => handleSubmit(query)}
          disabled={isProcessing || !query.trim()}
          className="bg-brand-primary text-white brutal-border brutal-shadow brutal-shadow-hover px-8 py-4 font-black uppercase tracking-widest disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? "Processing..." : "Search"}
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        <span className="text-sm font-bold font-mono text-brand-muted uppercase tracking-wider mr-2 self-center">
          Try asking:
        </span>
        {SUGGESTED_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => handleSubmit(q)}
            disabled={isProcessing}
            className="text-xs bg-brand-bg brutal-border brutal-shadow-hover px-3 py-1 font-bold font-mono text-brand-text hover:bg-yellow-200 transition-colors disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
