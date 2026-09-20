import type { LatencySummary, Timings } from "../types";

interface TelemetryProps {
  timings: Timings;
  latencySummary?: LatencySummary | null;
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="border-2 border-neutral-900 bg-white p-5">
      <p className="text-xs uppercase tracking-widest font-bold text-gray-500">
        {label}
      </p>

      <p className="text-3xl font-black mt-2">
        {value.toFixed(0)} ms
      </p>
    </div>
  );
}

export function Telemetry({
  timings,
  latencySummary,
}: TelemetryProps) {
  return (
    <section className="mt-16 mb-10">
      <h3 className="text-3xl font-black uppercase mb-6">
        Pipeline Telemetry
      </h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Metric
          label="STT"
          value={timings.stt_ms}
        />

        <Metric
          label="Retrieval"
          value={timings.retrieval_ms}
        />

        <Metric
          label="Generation"
          value={timings.generation_ms}
        />

        <Metric
          label="Grounding"
          value={timings.grounding_ms}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <Metric
          label="Total RAG"
          value={timings.total_rag_ms}
        />

        <Metric
          label="End to End"
          value={timings.total_e2e_ms}
        />
      </div>

      {latencySummary && latencySummary.sample_count > 0 && (
        <div className="mt-12 border-t-2 border-neutral-900 pt-8">
          <div className="flex justify-between items-end mb-5">
            <h4 className="text-2xl font-black uppercase">
              Latency Analytics
            </h4>

            <p className="text-xs font-bold text-gray-500">
              Samples: {latencySummary.sample_count}
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b-2 border-neutral-900 text-left">
                  <th className="py-3">Metric</th>
                  <th className="py-3 text-right">P50</th>
                  <th className="py-3 text-right">P70</th>
                  <th className="py-3 text-right">P100</th>
                </tr>
              </thead>

              <tbody>
                <LatencyRow
                  label="STT"
                  metric={latencySummary.stt_ms}
                />

                <LatencyRow
                  label="Retrieval"
                  metric={latencySummary.retrieval_ms}
                />

                <LatencyRow
                  label="Generation"
                  metric={latencySummary.generation_ms}
                />

                <LatencyRow
                  label="Grounding"
                  metric={latencySummary.grounding_ms}
                />

                <LatencyRow
                  label="Total RAG"
                  metric={latencySummary.total_rag_ms}
                />

                <LatencyRow
                  label="Total End to End"
                  metric={latencySummary.total_e2e_ms}
                />
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}

function LatencyRow({
  label,
  metric,
}: {
  label: string;
  metric: {
    p50: number;
    p70: number;
    p100: number;
  };
}) {
  return (
    <tr className="border-b border-gray-200">
      <td className="py-3 font-bold">
        {label}
      </td>

      <td className="py-3 text-right">
        {metric.p50.toFixed(1)} ms
      </td>

      <td className="py-3 text-right">
        {metric.p70.toFixed(1)} ms
      </td>

      <td className="py-3 text-right font-black">
        {metric.p100.toFixed(1)} ms
      </td>
    </tr>
  );
}