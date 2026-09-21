import { useEffect, useState } from "react";
import { Hero } from "./components/hero";
import { Microphone } from "./components/microphone";
import { Results } from "./components/Results";
import { Telemetry } from "./components/telemetry";

import type {
  LatencySummary,
  VoiceQueryResponse,
} from "./types";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8001";

export default function App() {
  const [result, setResult] = useState<VoiceQueryResponse | null>(null);
  const [latencySummary, setLatencySummary] =
    useState<LatencySummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchLatencySummary = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/latency/summary?sample_size=10`
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();
      setLatencySummary(data);
    } catch {
      return;
    }
  };

  useEffect(() => {
    fetchLatencySummary();
  }, []);

  const handleResult = (data: VoiceQueryResponse) => {
    setResult(data);
    setError(null);
    fetchLatencySummary();
  };

  const handleError = (message: string) => {
    setError(message);
  };

  return (
    <main>
      <Hero />

      <Microphone
        onResult={handleResult}
        onError={handleError}
      />

      {error && (
        <div>
          {error}
        </div>
      )}

      <Results result={result} />

      <Telemetry
        latencySummary={latencySummary}
        result={result}
      />
    </main>
  );
}