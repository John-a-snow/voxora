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
    const 2useRef<BlobPart[]>([]);
     
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const animationRef = useRef<number | null>(null);

    const startRecording = async () => {
        try {
            onClear();

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });

            streamRef.current = stream;

            const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 128;
            const source = audioCtx.createMediaStreamSource(stream);
            source.connect(analyser);

            audioContextRef.current = audioCtx;
            analyserRef.current = analyser;

            const drawWaveform = () => {
              if (!canvasRef.current || !analyserRef.current) return;
              const canvas = canvasRef.current;
              const canvasCtx = canvas.getContext("2d");
              if (!canvasCtx) return;
              
              const bufferLength = analyserRef.current.frequencyBinCount;
              const dataArray = new Uint8Array(bufferLength);
              analyserRef.current.getByteFrequencyData(dataArray);

              canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

              const barWidth = (canvas.width / bufferLength) * 2.5;
              let x = 0;
              
              for (let i =0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * canvas.height;
                canvasCtx.fillStyle = "rgb(239, 68, 68)";
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
              }

              animationRef.current = requestAnimationFrame(drawWaveform);
            };


            setTimeout(() => drawWaveform(), 100);

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
            const extention = mimeType.includes("ogg") ? "ogg" : "webm";

            const audioBlob = new Blob(chunksRef.current, {
                type: mimeType,
            });

            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
                audioContextRef.current.close();
            }

            stream.getTracks().forEach((track) => track.stop());
            streamRef.current = null;

            if (audioBlob.size === 0) {
                onError("No audio was recorded. Please try again.");
                return;
            }

            await processAudio(audioBlob, extention);
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
        }  catch (error) {
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
        <section className="my-12 flex flex-col items-center justify-center relative w-full">
            <div className="flex flex-col items-center gap-8 relative z-10 w-full max-w-md mx-auto">
                {!isRecording && !isProcessing && (
                    <button 
                    onClick={startRecording}
                    className="group relative flex flex-col items-center justify-center gap-4 transition-transform hover:-translate-y-1 active:translate-y-2 w-full bg-brand-panel brutal-border brutal-shadow p-8 cursor-pointer"
                    >
                        <div className="w-20 h-20 bg-brand-primary brutal-border flex items-center justify-center group-hover:bg-brand-primary-hover transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-white" fil="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeWidth={3} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                            </svg>
                        </div>
                        <span className="font-black text-2xl uppercase tracking-widest text-brand-text">
                         Tap to speak
                        </span>
                    </button>
                )}

                {isRecording && (
                    <div 
                    className="group relative flex flex-col items-center justify-center gap-4 w-full bg-red-100 brutal-border brutal-shadow p-8 cursor-pointer overflow-hidden"
                    onClick={stopRecording}
                    >
                        <div className="absolute top-2 right-2 flex gap-2">
                            <span className="relative flex h-3 w-3">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500 brutal-border"></span>
                            </span>
                        </div>

                        <canvas
                          ref={canvasRef}
                          width={200}
                          height={80}
                          className="w-full max-w-[200px] h-20" 
                          />

                          <span className="font-black text-2xl uppercase tracking-widest text-red-600 mt-2">
                            Stop Recording
                          </span>
                        </div>  
                )}

                {isProcessing && (
                    <div className="flex flex-col items-center justify-center gap-4 w-full bg-ble-100 brutal-border brutal-shadow p-8">
                        <div className="w-20 h-20 bg-blue-500 brutal-border flex items-center justify-center animate-spin">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M4 4v5h.582m15.356 2A8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                        </div>
                        <span className="font-black text-2xl uppercase tracking-widest text-blue-700">
                            Processing...
                        </span>
                      </div>  
                )}

                <div className="bg-brand-panel brutal-border p-4 w-full text-center">
                    <p className="text-sm font-bold font-mono text-brand-text uppercase tracking-wider">
                        Speak in English or Hindi. Max 30s.
                    </p>
                </div>
            </div>
        </section>
    );
    }
  


