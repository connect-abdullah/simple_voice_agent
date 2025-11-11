'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Volume2, Loader2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/stream';

interface Voice {
  voice_id: string;
  name: string;
}

export default function VoiceAgent() {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState('Ready to talk');
  const [isLoading, setIsLoading] = useState(false);
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('21m00Tcm4TlvDq8ikWAM');
  const [transcribedText, setTranscribedText] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioQueueRef = useRef<Blob[]>([]);
  const isPlayingAudioRef = useRef(false);
  const wsRef = useRef<WebSocket | null>(null);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Fetch available voices
    fetch(`${API_URL}/voices`)
      .then(res => res.json())
      .then(data => {
        if (data.voices && Array.isArray(data.voices)) {
          setVoices(data.voices);
        } else {
          setVoices([
            { voice_id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel (Default)' }
          ]);
        }
      })
      .catch(err => {
        console.error('Failed to fetch voices:', err);
        setVoices([
          { voice_id: '21m00Tcm4TlvDq8ikWAM', name: 'Rachel (Default)' }
        ]);
      });

    return () => {
      stopAllAudio();
    };
  }, []);

  const stopAllAudio = () => {
    // Stop current audio playback
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current = null;
    }
    
    // Clear audio queue
    audioQueueRef.current = [];
    isPlayingAudioRef.current = false;
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const startRecording = async () => {
    try {
      // Stop any ongoing AI response immediately
      stopAllAudio();
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      // Try to use audio/webm;codecs=opus for better compression
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : 'audio/webm';
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        console.log(`📊 Recorded ${audioChunksRef.current.length} audio chunks`);
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        console.log(`📊 Final audio blob: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
        transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setStatus('🎤 Recording... Click to stop');
    } catch (error) {
      console.error('Error starting recording:', error);
      setStatus('❌ Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus('Processing audio...');
      setIsLoading(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      console.log(`📊 Audio blob size: ${audioBlob.size} bytes, type: ${audioBlob.type}`);
      
      // Check if audio blob is too small (likely empty)
      if (audioBlob.size < 1000) {
        console.warn('Audio blob too small, skipping transcription');
        setIsLoading(false);
        setStatus('❌ No audio recorded');
        return;
      }
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData,
        signal: AbortSignal.timeout(60000)
      });

      if (response.ok) {
        const result = await response.json();
        const text = result.text;

        if (!text || text === 'Transcription failed') {
          setIsLoading(false);
          setStatus('❌ No speech detected');
          return;
        }

        setTranscribedText(text);
        setStatus(`📝 You: "${text}"`);
        setIsLoading(false);

        // Send to AI immediately
        setTimeout(() => sendMessage(text), 500);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }
    } catch (error) {
      console.error('Transcription error:', error);
      const err = error as Error;
      setIsLoading(false);
      
      if (err.name === 'TimeoutError' || err.name === 'AbortError') {
        setStatus('⏱️ Timeout - try again');
      } else if (err.message.includes('Failed to fetch')) {
        setStatus('❌ Cannot connect to server');
      } else {
        setStatus(`❌ ${err.message}`);
      }
    }
  };

  const sendMessage = (message: string) => {
    setStatus('🤖 AI is responding...');
    setIsLoading(true);
    setAiResponse('');
    
    // Stop any existing audio/connections
    stopAllAudio();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    let fullResponse = '';

    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'text_input',
        text: message,
        voice_id: selectedVoice
      }));
    };

    ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'text_chunk') {
          fullResponse += data.content;
          setAiResponse(fullResponse);
        } else if (data.type === 'audio_chunk') {
          // Handle both 'audio' and 'audio_data' fields
          const audioBase64 = data.audio || data.audio_data;
          
          if (audioBase64) {
            try {
              // Decode base64 to binary
              const binaryString = atob(audioBase64);
              const bytes = new Uint8Array(binaryString.length);
              for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
              }
              
              const audioBlob = new Blob([bytes], { type: 'audio/mpeg' });
              audioQueueRef.current.push(audioBlob);
              
              if (!isPlayingAudioRef.current) {
                playNextAudio();
              }
            } catch (decodeError) {
              console.error('Error decoding audio:', decodeError);
            }
          }
        } else if (data.type === 'stream_complete') {
          setStatus('✅ Ready to talk');
          setIsLoading(false);
          ws.close();
        } else if (data.type === 'error') {
          setStatus(`❌ Error: ${data.message}`);
          setIsLoading(false);
          ws.close();
        }
      } catch (error) {
        console.error('Error processing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('❌ Connection error');
      setIsLoading(false);
    };

    ws.onclose = () => {
      setIsLoading(false);
    };
  };

  const playNextAudio = async () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingAudioRef.current = false;
      return;
    }

    isPlayingAudioRef.current = true;
    const audioBlob = audioQueueRef.current.shift()!;
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    currentAudioRef.current = audio;

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      currentAudioRef.current = null;
      playNextAudio();
    };

    audio.onerror = (error) => {
      console.error('Audio playback error:', error);
      URL.revokeObjectURL(audioUrl);
      currentAudioRef.current = null;
      playNextAudio();
    };

    try {
      await audio.play();
    } catch (error) {
      console.error('Failed to play audio:', error);
      URL.revokeObjectURL(audioUrl);
      currentAudioRef.current = null;
      playNextAudio();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 md:p-12 max-w-2xl w-full shadow-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2 bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
            🎤 Voice Agent
          </h1>
          <p className="text-purple-100 text-lg">
            Click to record your voice
          </p>
        </div>

        {/* Voice Selection */}
        <div className="mb-6">
          <label className="block text-white text-sm font-medium mb-2">
            Select AI Voice
          </label>
          <select
            value={selectedVoice}
            onChange={(e) => setSelectedVoice(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-purple-400 backdrop-blur-sm"
            disabled={isLoading}
          >
            {voices && voices.length > 0 ? (
              voices.map((voice) => (
                <option key={voice.voice_id} value={voice.voice_id} className="text-gray-900">
                  {voice.name}
                </option>
              ))
            ) : (
              <option value="21m00Tcm4TlvDq8ikWAM" className="text-gray-900">
                Loading voices...
              </option>
            )}
          </select>
        </div>

        {/* Recording Button */}
        <div className="flex justify-center mb-8">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading && !isRecording}
            className={`
              relative group
              w-32 h-32 rounded-full
              flex items-center justify-center
              transition-all duration-300 transform
              ${isRecording 
                ? 'bg-gradient-to-br from-orange-500 to-red-600 scale-110 shadow-xl shadow-orange-500/50 animate-pulse' 
                : isLoading
                ? 'bg-gradient-to-br from-gray-400 to-gray-500'
                : 'bg-gradient-to-br from-red-500 to-pink-600 hover:scale-110 hover:shadow-xl hover:shadow-red-500/50'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
            `}
          >
            {isLoading && !isRecording ? (
              <Loader2 className="w-12 h-12 text-white animate-spin" />
            ) : isRecording ? (
              <Square className="w-12 h-12 text-white" />
            ) : (
              <Mic className="w-12 h-12 text-white" />
            )}
          </button>
        </div>

        {/* Status */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/20 backdrop-blur-sm">
            {(isLoading || isRecording) && <Loader2 className="w-4 h-4 text-white animate-spin" />}
            <p className="text-white font-medium">{status}</p>
          </div>
        </div>

        {/* Transcribed Text */}
        {transcribedText && (
          <div className="mb-6 p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
            <div className="flex items-start gap-2">
              <Mic className="w-5 h-5 text-purple-300 flex-shrink-0 mt-1" />
              <div>
                <p className="text-purple-200 text-sm font-medium mb-1">You:</p>
                <p className="text-white">{transcribedText}</p>
              </div>
            </div>
          </div>
        )}

        {/* AI Response */}
        {aiResponse && (
          <div className="p-4 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
            <div className="flex items-start gap-2">
              <Volume2 className="w-5 h-5 text-green-300 flex-shrink-0 mt-1" />
              <div>
                <p className="text-green-200 text-sm font-medium mb-1">AI:</p>
                <p className="text-white whitespace-pre-wrap">{aiResponse}</p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 text-center">
          <p className="text-purple-200 text-sm">
            🎤 Click the microphone to start recording
          </p>
          <p className="text-purple-300 text-xs mt-2">
            Click again to stop and send your message
          </p>
        </div>
      </div>
    </div>
  );
}
