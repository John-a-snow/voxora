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
        }
    }
 }