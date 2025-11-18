'use client';

import { useEffect } from 'react';
import { useCamera } from '@/lib/hooks/useCamera';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Camera, CameraOff } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface CameraCaptureProps {
  onCapture?: (frame: string) => void;
  autoStart?: boolean;
  captureButtonText?: string;
}

export const CameraCapture = ({ onCapture, autoStart = false, captureButtonText = 'Capture Photo' }: CameraCaptureProps) => {
  const { videoRef, isActive, error, startCamera, stopCamera, captureFrame } = useCamera();

  useEffect(() => {
    if (autoStart) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
  }, [autoStart, startCamera, stopCamera]);

  const handleCapture = () => {
    const frame = captureFrame();
    if (frame && onCapture) {
      onCapture(frame);
    }
  };

  return (
    <Card className="p-6 transition-all duration-300 hover:shadow-lg">
      <div className="space-y-4">
        <div className="relative bg-muted rounded-lg overflow-hidden aspect-video transition-all duration-300">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          {!isActive && (
            <div className="absolute inset-0 flex items-center justify-center bg-muted animate-fade-in">
              <CameraOff className="h-16 w-16 text-muted-foreground animate-pulse" />
            </div>
          )}
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex gap-2">
          {!isActive ? (
            <Button onClick={startCamera} className="flex-1">
              <Camera className="mr-2 h-4 w-4" />
              Start Camera
            </Button>
          ) : (
            <>
              <Button onClick={stopCamera} variant="outline" className="flex-1">
                <CameraOff className="mr-2 h-4 w-4" />
                Stop Camera
              </Button>
              {onCapture && (
                <Button onClick={handleCapture} className="flex-1">
                  <Camera className="mr-2 h-4 w-4" />
                  {captureButtonText}
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </Card>
  );
};
