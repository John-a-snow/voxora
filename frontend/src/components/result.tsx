import type { VoiceQueryResponse } from '../types';
import { CheckCircle, XCircle } from 'lucide-react';

interface resultsProps {
    result: VoiceQueryResponse;
}

export const Results: React.FC<ResultsProps> = ({ result }) => {
    const isRefused = result.status === 'refused_insufficient';

    return (
        <div className="flex flex-col gap-12 mt-12">

            <section>
                <div className="text-xs uppercase font-bold tracking-widest text-brand-primary mb-4 flex items-center gap-4">
                    YOU SAID 
                    <span className="bg-brand-border text-brand-bg px-2 py-1 text-[10px]">
                        {result.language === 'en-IN' ? 'ENGLISH' : result.language === 'hi-IN' ? 'HINDI' : result.language} 
                    </span>
                </div>
                <h2 className="text-3xl md:text-5xl font-black tracking-tight leading-tight">
                    "{result.transcript}"
                </h2>
            </section>


            <section className="border-4 border-brand-border bg-white p-8 md:p-12 shadow-[8px_8px_0px_0px_rgba(23,23,23,1)]">
                <div className="text-xs uppercase font-bold tracking-widest mb-8 border-b-2 border-brand-border pb-4 flex justify-between items-end">
                    <span className="text-2xl">ANSWER</span>
                    {isRefused ? (
                        <div className="flex flex-col items-end">
                            <span className="text-red-600 flex items-center gap-2"><XCircle size={16} /> NO RELEVANT CONTEXT</span>
                            <span className="text-gray-500 mt-1"></span>
                    )}
                </div>
            </section>
        </div>
    )
}



import { useState, useRef } from 'react';
import axios from 'axios';
import { Mic, Loader2, StopCircle } from 'lucide-react';
import type { VOiceQueryResponse } from '../types';

const API_BASE_URL =
 (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8001';

 interface MicrophoneProps {
    onResult: (result: VOiceQueryResponse) => void;
    onError: (error: string) => void;
    onClear: () => void;
 }

 export const Microphone: React.FC<MicrophoneProps> = ({ onResult, onError, onClear }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<BlobPart[]>([]);

    const startRecording = async () => {
        try {
            onClear();
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
                await processAudio(audioBlob);


                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error(err);
            onError("Microphone permission denied or unavailable.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const processAudio = async (audioBlob: Blob) => {
        setIsProcessing(true);
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            const response = await axios.post<VoiceQueryResponse>(`${API_BASE_URL}/api/voice-query`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            onResult(response.data);
        } catch (err: any) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.details) {
                onError(err.response.data.details);
            } else {
                onError("Backend offline or request failed.");
            }
        } finally {
          setIsProcessing(false);
        }
    };

    return (
        <div className="my-12">
            <div className="flex flex-col items-start gap-4">
                {!isRecording && !isProcessing ? (
                    <button 
                    onClick={startRecording}
                    className="group relative flex items-center justify-center gap-4 bg-brand-border text-brand-bg hover:bg-brand-primary transition-colors duration-300 px-8 py-6 rounded-none font-bold text-xl uppercase tracking-wider shadow-[4px_4px_0px_0px_rgba(234,88,12,1)]"
                    >
                        <Mic size={32} />
                        <span>Talk to the Corpus</span>
                    </button>  
                ) : isRecording ? (
                    <button 
                      onClick={stopRecording}
                      className="group relative flex items-center justify-center gap-4 bg-red-600 text-white hover:bg-red-700 transition-colors duration-300 px-8 py-6 rounded-none font-bold text-xl uppercase tracking-wider shadow-[4px_4px_0px_0px_0px_rgba(23,23,23,1)] animate-pulse"
                    >
                        <StopCircle size={32} />
                        <span>Listening... (Click to Stop)</span>
                    </button>      
                ) : (
                  <button 
                    disabled
                    className="group relative flex items-center justify-center gap-4 by-gray-200 text-gray-500 px-8 py-6 rounded-none font-bold text-xl uppercase tracking-wider cursor-not-allowed border-2 border-gray-300"
                   >
                    <Loader2 size={32} className="animate-spin" />
                    <span>Processing</span>
                   </button>