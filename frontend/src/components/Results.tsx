import type { VoiceQueryResponse } from "../types";

interface ResultsProps {
  result: VoiceQueryResponse;
}

export function Results({ result }: ResultsProps) {
  const refused = result.status === "refused_insufficient";

  return (
    <section className="mt-12 space-y-10">
      <div>
        <p className="text-xs uppercase tracking-widest font-bold text-gray-500 mb-3">
          You said
        </p>

        <h2 className="text-3xl md:text-5xl font-black leading-tight">
          "{result.transcript}"
        </h2>

        <p className="mt-3 text-sm font-medium text-gray-500">
          Language: {result.language}
        </p>
      </div>

      <div className="border-4 border-neutral-900 bg-white p-8 shadow-[8px_8px_0px_0px_rgba(23,23,23,1)]">
        <div className="flex justify-between items-center gap-4 border-b-2 border-neutral-900 pb-4 mb-8">
          <h3 className="text-2xl font-black">
            Answer
          </h3>

          <span
            className={
              refused
                ? "text-red-600 font-bold text-sm"
                : result.grounded
                ? "text-green-600 font-bold text-sm"
                : "text-yellow-600 font-bold text-sm"
            }
          >
            {refused
              ? "NO RELEVANT CONTEXT"
              : result.grounded
              ? "GROUNDED"
              : "NOT VERIFIED"}
          </span>
        </div>

        <p className="text-xl md:text-3xl leading-relaxed">
          {result.answer ||
            "The system could not generate an answer from the available evidence."}
        </p>

        {result.citations.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-300">
            <p className="text-xs uppercase tracking-widest font-bold text-gray-500 mb-3">
              Citations
            </p>

            <div className="flex flex-wrap gap-2">
              {result.citations.map((citation, index) => (
                <span
                  key={`${citation}-${index}`}
                  className="bg-gray-100 border border-gray-300 px-3 py-1 text-sm"
                >
                  {citation}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {result.retrieved_documents.length > 0 && (
        <div>
          <h3 className="text-2xl font-black uppercase mb-6">
            Evidence
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.retrieved_documents
              .slice(0, 5)
              .map((doc, index) => (
                <div
                  key={`${doc.document_id}-${index}`}
                  className="border-2 border-neutral-900 bg-white p-6"
                >
                  <div className="flex justify-between gap-4 mb-4">
                    <span className="text-2xl font-black">
                      {(index + 1)
                        .toString()
                        .padStart(2, "0")}
                    </span>

                    <div className="text-right">
                      <p className="text-xs font-mono">
                        {doc.document_id}
                      </p>

                      {doc.score !== undefined && (
                        <p className="text-xs text-gray-500 mt-1">
                          Score: {doc.score.toFixed(4)}
                        </p>
                      )}
                    </div>
                  </div>

                  <p className="text-sm leading-relaxed text-gray-700">
                    {doc.text || "No text available."}
                  </p>

                  <p className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
                    {doc.source || "Knowledge Base"}
                    {" • "}
                    {doc.language || "Unknown"}
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}
    </section>
  );
}