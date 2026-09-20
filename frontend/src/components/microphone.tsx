import { useRef, useState } from "react";
import type { VoiceQueryResponse } from "../types";

interface MicrophoneProps {
  onResult: (result: VoiceQueryResponse) => void;
  onError: (error: string) => void;
  onClear: () => void;
}

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8001";

export function Microphone({
  onResult,
  onError,
  onClear,
}: MicrophoneProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const startRecording = async () => {
    try {
      onClear();

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      streamRef.current = stream;

      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
      ];

      const supportedType = mimeTypes.find((type) =>
        MediaRecorder.isTypeSupported(type)
      );

      const recorder = supportedType
        ? new MediaRecorder(stream, { mimeType: supportedType })
        : new MediaRecorder(stream);

      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const mimeType = recorder.mimeType || "audio/webm";
        const extension = mimeType.includes("ogg") ? "ogg" : "webm";

        const audioBlob = new Blob(chunksRef.current, {
          type: mimeType,
        });

        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;

        if (audioBlob.size === 0) {
          onError("No audio was recorded. Please try again.");
          return;
        }

        await processAudio(audioBlob, extension);
      };

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error(error);
      onError("Microphone permission denied or unavailable.");
    }
  };

  const stopRecording = () => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob, extension: string) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();

      formData.append(
        "audio",
        audioBlob,
        `recording.${extension}`
      );

      const response = await fetch(
        `${API_BASE_URL}/api/voice-query`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Voice query failed."
        );
      }

      onResult(data as VoiceQueryResponse);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        onError(error.message);
      } else {
        onError("Backend offline or request failed.");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <section className="my-12">
      <div className="flex flex-col items-start gap-4">
        {!isRecording && !isProcessing && (
          <button
            onClick={startRecording}
            className="bg-neutral-900 text-white px-8 py-5 font-bold text-lg uppercase tracking-wide hover:bg-neutral-700 transition"
          >
            Start Voice Query
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="bg-red-600 text-white px-8 py-5 font-bold text-lg uppercase tracking-wide hover:bg-red-700 transition"
          >
            Stop Recording
          </button>
        )}

        {isProcessing && (
          <button
            disabled
            className="bg-gray-200 text-gray-500 px-8 py-5 font-bold text-lg uppercase tracking-wide cursor-not-allowed"
          >
            Processing...
          </button>
        )}

        <p className="text-sm text-gray-500">
          Speak in English or Hindi. Keep the question under 30 seconds.
        </p>
      </div>

      {isProcessing && (
        <div className="mt-8 border-2 border-gray-900 p-5 bg-white">
          <p className="font-bold uppercase tracking-wide mb-3">
            Processing Query
          </p>

          <div className="text-sm font-medium">
            Voice → STT → Retrieval → Generation → Grounding
          </div>
        </div>
      )}
    </section>
  );
}