import { useState, useEffect } from 'react';
import { Hero } from './components/Hero';
import { Microphone } from './components/microphone';
import { Telemetry } from './components/telemetry';
import { Result } from './components/result';
import type { VoiceQueryResponse, LatencySummary } from './types';
import axios from 'axios';

const API_BASE_URL = 
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8001';


  function App() {
    const [result, setResult] = useState<VoiceQueryResponse | null>(null);
    const [latencySummary, setLatencySummary] = useState<LatencySummary | null>(null);
    const [error, setError] = useState<string | null>(null);

    const fetchLatencySummary = async () => {
      try {
        const response = await axios.get<LatencySummary>(`${API_BASE_URL}/api/latency/summary?sample_size=10`);
        setLatencySummary(response.data);
      }  catch (err) {
        console.error("Failed to fetch latency summary", err);
      }
    };

    useEffect(() => {
        fetchLatencySummary();
    }, []);

    const handleResult = (newResult: VoiceQueryResponse) => {
        setResult(newResult);
        setError(null);
        fetchLatencySummary();
    };

    const handleError = (errorMessage: string) => {
        setError(errorMessage);
        setResult(null);
    };

    const handleClear = () => {
        setResult(null);
        setError(null);
    };
  }