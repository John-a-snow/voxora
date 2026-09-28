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

function Navbar({ toggleDarkMode, isDarkMode, currentView, setCurrentView }: { toggleDarkMode: () => void, isDarkMode: boolean, currentView: string, setCurrentView: (view: 'landing' | 'app' | 'features') => void }) {
  return (
    <nav className="flex justify-between items-stretch bg-brand-panel brutal-border brutal-shadow mb-12 hidden md:flex">
      <div 
        className="border-r-3 border-brand-border p-4 flex items-center bg-brand-bg cursor-pointer"
        onClick={() => setCurrentView('landing')}
      >
        <h1 className="text-xl font-black tracking-tighter uppercase text-brand-text">Voxora RAG</h1>
      </div>
      <div className="flex-1 flex justify-center items-center gap-8 font-mono text-sm font-bold uppercase text-brand-text">
        <button 
          onClick={() => setCurrentView('landing')} 
          className={`hover:text-brand-primary transition-colors ${currentView === 'landing' ? 'border-b-2 border-brand-primary text-brand-primary' : ''}`}
        >
          Home
        </button>
        <button 
          onClick={() => setCurrentView('features')}
          className={`hover:text-brand-primary transition-colors ${currentView === 'features' ? 'border-b-2 border-brand-primary text-brand-primary' : ''}`}
          >
            Features
          </button>  
      </div> 
      <div className="border-l-3 border-brand-border flex items-stretch">
        <button onClick={toggleDarkMode} className="px-4 border-r-3 border-brand-border hover:bg-brand-bg flex items-center justify-center text-brand-text">
          {isDarkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.293 13.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </button>
                <button 
          onClick={() => setCurrentView('app')}
          className="px-6 bg-brand-primary text-white font-black uppercase tracking-widest hover:bg-brand-primary-hover"
        >
          Voice Query
        </button>
      </div>
    </nav>
  );
}

function LandingPage({ onStart }: { onStart: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center z-10 relative px-4">
      <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-panel brutal-border text-brand-text text-sm font-bold tracking-widest font-mono uppercase brutal-shadow mb-8">
        <span className="w-3 h-3 bg-brand-primary brutal-border animate-bounce" />
        V1.0 RELEASE
      </div>
      <h1 className="text-6xl md:text-8xl font-black tracking-tighter uppercase leading-none mb-6 text-brand-text drop-shadow-[4px_4px_0_rgba(205,19,55,1)]">
        Voxora <br /> Intelligence
      </h1>
      <p className="text-xl md:text-2xl font-bold max-w-2xl mx-auto text-brand-text leading-relaxed brutal-border bg-brand-panel p-6 brutal-shadow mb-12">
        The most advanced voice-activated Retrieval-Augmented Generation system. Speak naturally. Retrieve instantly.
      </p>
      <button 
        onClick={onStart}
        className="bg-brand-primary text-white brutal-border brutal-shadow brutal-shadow-hover px-10 py-5 text-xl font-black uppercase tracking-widest flex items-center gap-4 transition-transform"
      >
        Enter Workspace
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </div>
  );
}

function FeaturesPage() {
  const features = [
    {
      title: "Retrieval-Augmented Generation",
      desc: "Automatically extracts dense embeddings from the knowledge base to ensure the AI's answer is deeply grounded in factual evidence, effectively reducing hallucinations.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
      color: "bg-yellow-300"
    },
    {
      title: "Live Audio Visualizer",
      desc: "Intercepts the browser's Web Audio API stream and renders the exact frequencies of your voice directly onto a dynamic HTML5 canvas.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      ),
      color: "bg-blue-300"
    },
    {
      title: "Real-time Telemetry",
      desc: "Collects precise execution latency (P50, P70, P100 metrics) for Speech-to-Text, Embedding generation, and LLM inference across your sessions.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: "bg-red-300"
    },
    {
      title: "Session History Drawer",
      desc: "Maintains a full log of your current workspace session. Instantly retrieve past voice queries, exact transcripts, and their corresponding AI answers.",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
      ),
      color: "bg-green-300"
    }
  ];

  return (
    <div className="animate-in fade-in zoom-in duration-300 relative z-10 px-4 pb-20">
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter text-brand-text mb-4">
          Core <span className="text-brand-primary">Features</span>
        </h1>
        <p className="text-xl font-bold font-mono text-brand-muted max-w-2xl mx-auto uppercase">
          The technical architecture powering Voxora Intelligence.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {features.map((f, idx) => (
          <div key={idx} className="bg-brand-panel brutal-border brutal-shadow p-8 flex flex-col hover:-translate-y-2 transition-transform">
            <div className={`w-16 h-16 ${f.color} brutal-border flex items-center justify-center text-3xl mb-6 text-black`}>
              {f.icon}
            </div>
            <h3 className="text-2xl font-black uppercase tracking-tight text-brand-text mb-4">
              {f.title}
            </h3>
            <p className="text-lg font-medium text-brand-muted leading-relaxed">
              {f.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [result, setResult] = useState<VoiceQueryResponse | null>(null);
  const [history, setHistory] = useState<VoiceQueryResponse[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [latencySummary, setLatencySummary] = useState<LatencySummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<'landing' | 'app' | 'features'>('landing');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => setIsDarkMode(!isDarkMode);

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
    setHistory((prev) => [data, ...prev]);
    setError(null);
    fetchLatencySummary();
  };

  const handleError = (message: string) => {
    setError(message);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-8 lg:px-16 max-w-[1400px] mx-auto bg-brand-bg relative overflow-hidden selection:bg-brand-primary selection:text-white transition-colors duration-300">
      {/* Decorative background elements */}
      <div className="absolute top-40 left-10 w-24 h-24 bg-brand-primary brutal-border brutal-shadow rotate-12 opacity-10 pointer-events-none hidden md:block" />
      <div className="absolute bottom-40 right-10 w-32 h-32 bg-brand-panel brutal-border brutal-shadow -rotate-6 opacity-20 pointer-events-none hidden md:block" />
      
      <main className="space-y-16 relative z-10">
        <Navbar 
          toggleDarkMode={toggleDarkMode} 
          isDarkMode={isDarkMode} 
          currentView={currentView}
          setCurrentView={setCurrentView}
        />
        
        {currentView === 'landing' && (
          <LandingPage onStart={() => setCurrentView('app')} />
        )}

        {currentView === 'features' && (
          <FeaturesPage />
        )}
        
        {currentView === 'app' && (
          <>
            <Hero />

            <div className="flex justify-center mt-12 w-full">
              <Microphone
                onResult={handleResult}
                onError={handleError}
                onClear={() => {
                  setError(null);
                  setResult(null);
                }}
              />
            </div>

            {error && (
              <div className="bg-red-100 brutal-border brutal-shadow text-red-600 p-6 flex items-center justify-center font-bold font-mono">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span className="uppercase tracking-widest">{error}</span>
              </div>
            )}

            {result && <Results result={result} />}

            {result && <Telemetry
              latencySummary={latencySummary}
              timings={result.timings}
            />}
          </>
        )}
      </main>

      {/* History Drawer (Only show when in the app) */}
      <div 
        className={`fixed top-0 right-0 h-full w-80 bg-brand-panel border-l-4 border-brand-border transform transition-transform duration-300 z-50 brutal-shadow ${isHistoryOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        <div className="flex flex-col h-full relative">
          <button 
            onClick={() => setIsHistoryOpen(false)}
            className="absolute -left-12 top-4 bg-brand-panel border-y-4 border-l-4 border-brand-border w-12 h-12 flex items-center justify-center hover:bg-brand-bg z-50 text-brand-text"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <div className="p-6 border-b-4 border-brand-border bg-brand-bg text-brand-text">
            <h2 className="text-xl font-black uppercase tracking-widest font-mono">Session History</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-brand-panel">
            {history.length === 0 ? (
              <p className="text-brand-muted font-bold font-mono text-sm uppercase text-center mt-10">No history yet</p>
            ) : (
              history.map((item, idx) => (
                <div 
                  key={idx} 
                  onClick={() => setResult(item)}
                  className="bg-brand-bg brutal-border p-4 cursor-pointer hover:-translate-y-1 transition-transform brutal-shadow-hover"
                >
                  <p className="text-xs font-black font-mono text-brand-muted uppercase mb-2">Q{history.length - idx}</p>
                  <p className="text-sm font-bold text-brand-text line-clamp-2">"{item.transcript}"</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      {/* History Floating Action Button */}
      {currentView === 'app' && !isHistoryOpen && (
        <button 
          onClick={() => setIsHistoryOpen(true)}
          className="fixed bottom-8 right-8 bg-brand-primary text-white brutal-border brutal-shadow brutal-shadow-hover p-4 z-40 group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      )}
    </div>
  );