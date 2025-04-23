import React, { useRef, useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { useWebSocket } from "./WebSocketProvider";
import { Base64 } from "js-base64";
import Chat from "./Chat";

const ScreenShare: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
  const captureIntervalRef = useRef<NodeJS.Timeout>();
  const [isSharing, setIsSharing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const { sendMessage, sendMediaChunk, isConnected, playbackAudioLevel } = useWebSocket();

  const startSharing = async () => {
    if (isSharing) return;
    try {
      // Add session start command
      sendMessage({ action: "start_sharing" });

      const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      const audioStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1, sampleRate: 16000 } });

      audioContextRef.current = new AudioContext({ sampleRate: 16000, latencyHint: "interactive" });
      const ctx = audioContextRef.current;
      await ctx.audioWorklet.addModule("/worklets/audio-processor.js");
      const source = ctx.createMediaStreamSource(audioStream);
      audioWorkletNodeRef.current = new AudioWorkletNode(ctx, "audio-processor", { processorOptions: { sampleRate: 16000, bufferSize: 4096 } });
      audioWorkletNodeRef.current.port.onmessage = ({ data: { pcmData, level } }) => {
        setAudioLevel(level as number);
        if (pcmData) {
          const b64 = Base64.fromUint8Array(new Uint8Array(pcmData as ArrayBuffer));
          sendMediaChunk({ mime_type: "audio/pcm", data: b64 });
        }
      };
      source.connect(audioWorkletNodeRef.current);
      audioStreamRef.current = audioStream;

      if (videoRef.current) {
        videoRef.current.srcObject = screenStream;
        captureIntervalRef.current = setInterval(() => {
          const v = videoRef.current!;
          const canvas = document.createElement("canvas");
          canvas.width = v.videoWidth;
          canvas.height = v.videoHeight;
          const ctx2 = canvas.getContext("2d");
          if (!ctx2) return;
          ctx2.drawImage(v, 0, 0);
          const imgB64 = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
          sendMediaChunk({ mime_type: "image/jpeg", data: imgB64 });
        }, 3000);
      }

      // sendMessage({ setup: {} });
      setIsSharing(true);
    } catch (err) {
      console.error("startSharing error", err);
      stopSharing();
    }
  };

  const stopSharing = () => {
    // Cleanup first
    if (captureIntervalRef.current) clearInterval(captureIntervalRef.current);
    if (audioWorkletNodeRef.current) audioWorkletNodeRef.current.disconnect();

    // Add session start command
    sendMessage({ action: "stop_sharing" });

    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((t) => t.stop());
      audioStreamRef.current = null;
    }
    if (captureIntervalRef.current) clearInterval(captureIntervalRef.current);
    if (audioWorkletNodeRef.current) audioWorkletNodeRef.current.disconnect();
    if (audioContextRef.current) {
      void audioContextRef.current.close();
    }
    setIsSharing(false);
    setAudioLevel(0);
  };

  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-6 max-w-5xl">
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight mb-4 sm:mb-8">Gemini Learning Assistant with Memory</h1>
        <p className="text-base sm:text-lg text-muted-foreground">Share your screen and talk to me</p>
      </div>
      <div className="flex flex-col lg:flex-row gap-6 justify-center items-start h-full min-h-[400px] sm:min-h-[600px]">
        <Card className="w-full lg:w-1/2 overflow-hidden">
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">Screen Preview</CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 space-y-4">
            <div className="relative w-full aspect-video">
              <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 w-full h-full object-cover rounded-md border bg-muted" />
            </div>
            {isSharing && <Progress value={Math.max(audioLevel, playbackAudioLevel)} className="h-1 sm:h-2 bg-white" indicatorClassName="bg-black" />}
            <div className="flex flex-col gap-2 w-full">
              {!isSharing ? (
                <Button size="lg" onClick={startSharing} disabled={!isConnected} variant={isConnected ? "default" : "outline"} className={`w-full ${!isConnected ? "border-red-300 text-red-700" : ""}`}>
                  {isConnected ? "Start Screen Share" : "Connecting..."}
                </Button>
              ) : (
                <Button size="lg" variant="destructive" onClick={stopSharing} className="w-full">
                  Stop Sharing
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Chat />
      </div>
    </div>
  );
};

export default ScreenShare;
