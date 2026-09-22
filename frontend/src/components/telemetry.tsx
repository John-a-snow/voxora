import type { LatencySummary, VoiceQueryResponse } from "../types";

interface TelemetryProps {
  result: VoiceQueryResponse | null;
  latencySummary: LatencySummary | null;
}

export function Telemetry({
  result,
  latencySummary,
}: TelemetryProps) {
  if (!result || !result.timings) {
    return null;
  }

  const timings = result.timings as any;
  const summary = latencySummary as any;

  return (
    <section className="telemetry">
      <div className="telemetry-card">
        <h2>Latency</h2>

        <div className="timing-grid">
          <div>
            <strong>Speech to Text</strong>
            <p>{timings.stt_ms ?? 0} ms</p>
          </div>           

          <div>
            <strong>Retrieval</strong>
            <p>{timings.retrieval_ms ?? 0} ms</p>
          </div>

          <div>
            <strong>Generation</strong>
            <p>{timings.generation_ms ?? 0} ms</p>
          </div>

          <div>
            <strong>Total</strong>
            <p>{timings.total_ms ?? 0} ms</p>
          </div>
        </div>

        {summary && (
          <div className="latency-summary">
            <h3>Latency Summary</h3>

            <table>
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Value</th>
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td>P50</td>
                  <td>
                    {summary.p50_ms ??
                      summary.p50 ??
                      "—"}{" "}
                    {summary.p50_ms || summary.p50 ? "ms" : ""}
                  </td>
                </tr>

                <tr>
                  <td>P70</td>
                  <td>
                    {summary.p70_ms ??
                      summary.p70 ??
                      "—"}{" "}
                    {summary.p70_ms || summary.p70 ? "ms" : ""}
                  </td>
                </tr>

                <tr>
                  <td>P100</td>
                  <td>
                    {summary.p100_ms ??
                      summary.p100 ??
                      "—"}{" "}
                    {summary.p100_ms || summary.p100 ? "ms" : ""}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}