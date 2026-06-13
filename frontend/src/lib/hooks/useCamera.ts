'use client';

import { useCallback, useRef, useState } from 'react';

interface UseCameraOptions {
  width?: number;
  height?: number;
  facingMode?: 'user' | 'environment';
}

function isBenignPlayError(err: unknown): boolean {
  if (!(err instanceof Error)) return false;
  return (
    err.name === 'AbortError' ||
    err.message.includes('interrupted') ||
    err.message.includes('The play() request was interrupted')
  );
}

async function safePlay(video: HTMLVideoElement): Promise<void> {
  try {
    await video.play();
  } catch (err) {
    if (!isBenignPlayError(err)) throw err;
  }
}

export function useCamera(options: UseCameraOptions = {}) {
  const { width = 640, height = 480, facingMode = 'user' } = options;
  const optionsRef = useRef({ width, height, facingMode });
  optionsRef.current = { width, height, facingMode };

  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sessionRef = useRef(0);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stopCamera = useCallback(() => {
    sessionRef.current += 1;

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsActive(false);
  }, []);

  const startCamera = useCallback(async () => {
    const session = sessionRef.current + 1;
    sessionRef.current = session;
    setError(null);

    try {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;

      const { width: w, height: h, facingMode: mode } = optionsRef.current;
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: w, height: h, facingMode: mode },
        audio: false,
      });

      if (session !== sessionRef.current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }

      streamRef.current = stream;

      const video = videoRef.current;
      if (!video) {
        setIsActive(true);
        return;
      }

      video.srcObject = stream;

      if (video.readyState >= HTMLMediaElement.HAVE_METADATA) {
        await safePlay(video);
      } else {
        await new Promise<void>((resolve, reject) => {
          const onLoaded = () => {
            video.removeEventListener('loadedmetadata', onLoaded);
            safePlay(video).then(resolve).catch(reject);
          };
          video.addEventListener('loadedmetadata', onLoaded);
        });
      }

      if (session !== sessionRef.current) return;

      setIsActive(true);
    } catch (err) {
      if (session !== sessionRef.current || isBenignPlayError(err)) return;

      const message = err instanceof Error ? err.message : 'Failed to access camera';
      setError(message);
      setIsActive(false);
    }
  }, []);

  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;
    if (!video || video.readyState < 2) return null;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || optionsRef.current.width;
    canvas.height = video.videoHeight || optionsRef.current.height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.92);
  }, []);

  return {
    videoRef,
    isActive,
    error,
    startCamera,
    stopCamera,
    captureFrame,
  };
}
