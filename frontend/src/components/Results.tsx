import type { VoiceQueryResponse } from "../types";

interface ResultsProps {
  result: VoiceQueryResponse;
}

export function Results({ result }: ResultsProps) {
  const refused = result.status === "refused_insufficient";

  return (
    <section className="mt-16 space-y-12">
      <div className="text-center mb-12 bg-brand-panel brutal-border brutal-shadow p-8 relative">
        <div className="absolute -top-4 -left-4 bg-brand-primary text-white brutal-border px-3 py-1 text-xs font-black font-mono uppercase tracking-widest">
          Recognized Speech
        </div>
        <h2 className="text-3xl md:text-5xl font-black leading-tight text-brand-text mb-6 mt-4">
          "{result.transcript}"
        </h2>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-200 brutal-border font-mono font-bold text-sm uppercase text-black">
          <span>Language:</span>
          <span>{result.language}</span>
        </div>
      </div>

      <div className="bg-brand-panel brutal-border brutal-shadow p-8 md:p-10 relative">
        <div className="absolute -top-4 -right-4 bg-brand-panel brutal-border p-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-brand-text" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b-4 border-brand-border pb-6 mb-6">
          <h3 className="text-4xl font-black text-brand-text uppercase tracking-tighter">
            AI Answer
          </h3>

          <span
            className={`px-4 py-2 text-sm font-black font-mono brutal-border uppercase ${
              refused
                ? "bg-red-500 text-white"
                : result.grounded
                ? "bg-green-400 text-black"
                : "bg-yellow-400 text-black"
            }`}
          >
            {refused                                                                   
              ? "NO RELEVANT CONTEXT"
              : result.grounded
              ? "GROUNDED RESPONSE"
              : "UNVERIFIED"}
          </span>
        </div>

        <p className="text-2xl md:text-3xl leading-relaxed text-brand-text font-medium">
          {result.answer ||
            "The system could not generate an answer from the available evidence."}
        </p>

        {result.citations.length > 0 && (
          <div className="mt-10 pt-8 border-t-4 border-brand-border">
            <p className="text-sm uppercase tracking-widest font-black text-brand-text mb-4 flex items-center gap-2 font-mono">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              Citations
            </p>

            <div className="flex flex-wrap gap-3">
              {result.citations.map((citation, index) => (
                <span
                  key={`${citation}-${index}`}
                  className="bg-brand-primary text-white brutal-border px-3 py-1 text-sm font-bold font-mono"
                >
                  {citation}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {result.retrieved_documents.length > 0 && (
        <div className="pt-8">
          <h3 className="text-3xl font-black text-brand-text uppercase mb-8 border-b-4 border-brand-border pb-4 inline-block tracking-tighter">
            Retrieved Evidence
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {result.retrieved_documents
              .slice(0, 4)
              .map((doc, index) => (
                <div
                  key={`${doc.document_id}-${index}`}
                  className="bg-brand-panel brutal-border brutal-shadow p-6 flex flex-col hover:-translate-y-2 transition-transform cursor-crosshair"
                >
                  <div className="flex justify-between items-start gap-4 mb-6">
                    <div className="w-12 h-12 brutal-border bg-yellow-300 flex items-center justify-center text-xl font-black text-black">
                      {index + 1}
                    </div>

                    <div className="text-right">
                      <p className="text-xs font-mono font-bold text-brand-text bg-brand-bg brutal-border px-2 py-1 uppercase">
                        {doc.document_id}
                      </p>

                      {doc.score !== undefined && (
                        <p className="text-xs font-mono font-bold text-brand-muted mt-2 uppercase">
                          Score: <span className="text-brand-text">{doc.score.toFixed(4)}</span>
                        </p>
                      )}
                    </div>
                  </div>

                  <p className="text-lg font-medium leading-relaxed text-brand-text flex-1 line-clamp-5">
                    {doc.text || "No text available."}
                  </p>

                  <div className="mt-6 pt-4 border-t-4 border-brand-border flex items-center justify-between text-xs font-black font-mono text-brand-text uppercase">
                    <span className="flex items-center gap-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      {doc.source || "Knowledge Base"}
                    </span>
                    <span className="px-3 py-1 bg-brand-primary text-white brutal-border">
                      {doc.language || "Unknown"}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </section>
  );
}