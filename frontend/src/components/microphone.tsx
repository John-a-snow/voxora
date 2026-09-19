import { useState, useref } from 'react';
import axios from 'axios';
import { Mic, Loader2, StopCircle } from 'lucide-react';
import { VoiceQueryResponse } from '../types';

const API_BASE_URL = 
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8001';

interface MicrophoneProps {
    onResult: (result: VoiceQueryResponse) => void;
    onError: (error: string) => void;
    onClear: () => void;
}

export const Microphone: React.FC<MicrophoneProps> = ({ onResult, onError, onClear }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProsessing, setIsProcessing] = useState(false);
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
              const audioBlob = new Blob(chunksRef.currect, { type: 'audio/wav' });
              await processAudio(audioBlob);


              stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        }  catch (err) {
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
    }  catch (err: any) {
        console.error(err);
        if (err.response && err.response.)
    }  
    }
}