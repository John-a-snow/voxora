import type { Timings, LatencySummary } from '../types';

interface TelemetryProps {
    timings: Timings;
    latencySummary?: LatencySummary | null;
}

export const Telemetry: React.FC<TelemetryProps> = ({ timings, latencySummary }) => {
    const localMs = timings.retrieval_ms + timings.grounding_ms;
    const remoteMs = timings.stt_ms + timings.generation_ms;
}