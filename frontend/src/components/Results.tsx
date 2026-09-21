import type { VoiceQueryResponse } from "../types";

interface ResultsProps {
  result: VoiceQueryResponse | null;
}

export function Results({ result }: ResultsProps) {
  if (!result) {
    return null;
  }

  const refused = result.status === "refused_insufficient";

  return (
    <section className="results">
      <div className="result-card">
        <h2>Result</h2>

        <div className="result-item">
          <strong>Transcript</strong>
          <p>{result.transcript}</p>
        </div>

        <div className="result-item">
          <strong>Language</strong>
          <p>{result.language}</p>
        </div>

        <div className="result-item">
          <strong>Answer</strong>
          <p>{result.answer}</p>
        </div>

        <div className="result-item">
          <strong>Status</strong>
          <p>{refused ? "Insufficient information" : result.status}</p>
        </div>

        <div className="result-item">
          <strong>Grounded</strong>
          <p>{result.grounded ? "Yes" : "No"}</p>
        </div>

        {result.citations && result.citations.length > 0 && (
          <div className="result-item">
            <strong>Citations</strong>
            <ul>
              {result.citations.map((citation) => (
                <li key={citation}>{citation}</li>
              ))}
            </ul>
          </div>
        )}

        {result.retrieved_documents &&
          result.retrieved_documents.length > 0 && (
            <div className="result-item">
              <strong>Retrieved Documents</strong>

              <div className="documents">
                {result.retrieved_documents.map((document, index) => (
                  <div
                    className="document-card"
                    key={document.document_id ?? index}
                  >
                    <p>{document.text}</p>

                    {document.score !== undefined && (
                      <small>Score: {document.score.toFixed(3)}</small>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
      </div>
    </section>
  );
}