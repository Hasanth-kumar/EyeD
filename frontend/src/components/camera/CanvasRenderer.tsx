'use client';

import { useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface CanvasRendererProps {
  videoElement: HTMLVideoElement | null;
  width?: number;
  height?: number;
  className?: string;
  onFrameCapture?: (blob: Blob) => void;
  captureInterval?: number;
  enabled?: boolean;
}

/**
 * CanvasRenderer - Renders video frames to a canvas element
 * 
 * This component is used for processing video frames from a camera stream.
 * It continuously draws video frames to a hidden canvas, which can be used
 * for frame capture and processing.
 * 
 * @param videoElement - The video element to render from
 * @param width - Canvas width (default: 640)
 * @param height - Canvas height (default: 480)
 * @param className - Additional CSS classes
 * @param onFrameCapture - Callback when a frame is captured (optional)
 * @param captureInterval - Interval between frame captures in ms (default: 100)
 * @param enabled - Whether rendering is enabled (default: true)
 */
export function CanvasRenderer({
  videoElement,
  width = 640,
  height = 480,
  className,
  onFrameCapture,
  captureInterval = 100,
  enabled = true,
}: CanvasRendererProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!videoElement || !canvasRef.current || !enabled) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const drawFrame = () => {
      if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
        // Draw video frame to canvas
        ctx.drawImage(videoElement, 0, 0, width, height);
        
        // Optionally capture frame as blob
        if (onFrameCapture) {
          canvas.toBlob((blob) => {
            if (blob) onFrameCapture(blob);
          }, 'image/jpeg', 0.8);
        }
      }
    };

    // Draw frames at specified interval
    const interval = setInterval(drawFrame, captureInterval);
    
    return () => clearInterval(interval);
  }, [videoElement, width, height, onFrameCapture, captureInterval, enabled]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className={cn('hidden', className)}
      aria-hidden="true"
    />
  );
}





