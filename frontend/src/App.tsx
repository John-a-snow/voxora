import { useEffect, useState } from "react";
import { Hero } from "./components/Hero";
import { Microphone } from "./components/Microphone";
import { Results } from "./components/Results";
import { Telemetry } from "./components/Telemetry";
import type {
  LatencySummary,
  VoiceQueryResponse,
} from "./types";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8001";

export default function App() {
  const [result, setResult] =
    useState<VoiceQueryResponse | null>(null);

  const [latencySummary, setLatencySummary] =
    useState<LatencySummary | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const fetchLatencySummary = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/latency/summary?sample_size=10`
      );

      if (!response.ok) {
        return;
      }

      const data =
        (await response.json()) as LatencySummary;

      setLatencySummary(data);
    } catch (error) {
      console.error(
        "Could not load latency summary",
        error
      );
    }
  };

  useEffect(() => {
    fetchLatencySummary();
  }, []);

  const handleResult = (
    newResult: VoiceQueryResponse
  ) => {
    setResult(newResult);
    setError(null);
    fetchLatencySummary();
  };

  const handleError = (message: string) => {
    setError(message);
    setResult(null);
  };

  const handleClear = () => {
    setResult(null);
    setError(null);
  };

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10 md:px-12">
      <div className="max-w-6xl mx-auto">
        <Hero />

        <Microphone
          onResult={handleResult}
          onError={handleError}
          onClear={handleClear}
        />

        {error && (
          <div className="mt-8 border-2 border-red-600 bg-red-50 p-5">
            <p className="text-xs uppercase tracking-widest font-bold text-red-600 mb-2">
              Error
            </p>

            <p className="text-red-800 font-medium">
              {error}
            </p>
          </div>
        )}

        {result && (
          <>
            <Results result={result} />

            <Telemetry
              timings={result.timings}
              latencySummary={latencySummary}
            />
          </>
        )}

        <footer className="mt-20 pb-6 text-xs font-bold uppercase tracking-widest text-gray-400">
          VOXORA • VOICE + RETRIEVAL + GROUNDED ANSWERS
        </footer>
      </div>
    </main>
  );
}