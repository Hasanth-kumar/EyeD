'use client';

import { useCamera } from '@/lib/hooks/useCamera';
import { useMediaPipe, type Landmark } from '@/lib/hooks/useMediaPipe';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Camera, Check, Eye } from 'lucide-react';
import { useEffect, useState, useCallback, useRef } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  detectBlink,
  createBlinkDetector,
  resetBlinkDetector,
  type BlinkDetectorState,
} from '@/lib/utils/blinkDetection';

interface FrameCollectorProps {
  targetFrames?: number;
  durationSeconds?: number; // Duration in seconds for frame collection
  frameIntervalMs?: number; // Interval between frames in milliseconds
  onComplete: (frames: string[], landmarks: Landmark[][]) => void;
  autoStart?: boolean;
  minBlinks?: number;
}

export const FrameCollector = ({
  targetFrames, // Deprecated: use durationSeconds instead
  durationSeconds = 30, // Default 30 seconds to match backend LIVENESS_VERIFICATION_DURATION_SECONDS
  frameIntervalMs = 1000, // Default 1 second interval (30 frames over 30 seconds)
  onComplete,
  autoStart = false,
  minBlinks = 3,
}: FrameCollectorProps) => {
  const { videoRef, isActive, error, startCamera, stopCamera, captureFrame } = useCamera();
  const { detectLandmarks, isReady: isMediaPipeReady, error: mediaPipeError } = useMediaPipe({
    runningMode: 'VIDEO',
  });

  const [frames, setFrames] = useState<string[]>([]);
  const [isCollecting, setIsCollecting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [blinkCount, setBlinkCount] = useState(0);
  const [currentEar, setCurrentEar] = useState<number | null>(null);
  const [isBlinking, setIsBlinking] = useState(false);
  
  // Calculate target frames based on duration (for backward compatibility)
  const calculatedTargetFrames = targetFrames ?? Math.ceil(durationSeconds * 1000 / frameIntervalMs);

  const blinkDetectorStateRef = useRef<BlinkDetectorState | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Initialize blink detector
  useEffect(() => {
    blinkDetectorStateRef.current = createBlinkDetector();
    return () => {
      if (blinkDetectorStateRef.current) {
        resetBlinkDetector(blinkDetectorStateRef.current);
      }
    };
  }, []);

  // Real-time blink detection loop (runs continuously when camera is active)
  useEffect(() => {
    if (!isActive || !isMediaPipeReady || !videoRef.current) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      return;
    }

    const processFrame = async () => {
      if (!videoRef.current || !blinkDetectorStateRef.current) return;

      try {
        // Detect landmarks from video
        const result = await detectLandmarks(videoRef.current);

        if (result.landmarks && result.hasFace) {
          // Detect blink
          const blinkResult = detectBlink(result.landmarks, blinkDetectorStateRef.current);
          
          setBlinkCount(blinkResult.blinkCount);
          setCurrentEar(blinkResult.earValue);
          setIsBlinking(blinkResult.isBlinking);
        } else {
          setCurrentEar(null);
          setIsBlinking(false);
        }
      } catch (err) {
        console.error('Error processing frame:', err);
      }

      // Continue processing
      animationFrameRef.current = requestAnimationFrame(processFrame);
    };

    animationFrameRef.current = requestAnimationFrame(processFrame);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isActive, isMediaPipeReady, detectLandmarks, videoRef]);

  useEffect(() => {
    if (autoStart) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
  }, [autoStart, startCamera, stopCamera]);

  const reset = useCallback(() => {
    setFrames([]);
    setIsCollecting(false);
    setProgress(0);
    setElapsedSeconds(0);
    setBlinkCount(0);
    setCurrentEar(null);
    setIsBlinking(false);
    if (blinkDetectorStateRef.current) {
      resetBlinkDetector(blinkDetectorStateRef.current);
    }
  }, []);

  const handleCollect = async () => {
    reset();
    setIsCollecting(true);
    setFrames([]);
    setProgress(0);
    setElapsedSeconds(0);

    const collectedFrames: string[] = [];
    const collectedLandmarks: Landmark[][] = [];
    const startTime = Date.now();
    const endTime = startTime + (durationSeconds * 1000);
    
    // Reset blink detector for this collection session
    // Note: Backend will also reset, but we need consistent counting during collection
    if (blinkDetectorStateRef.current) {
      resetBlinkDetector(blinkDetectorStateRef.current);
    }

    while (Date.now() < endTime) {
      const currentTime = Date.now();
      const elapsed = Math.floor((currentTime - startTime) / 1000);
      setElapsedSeconds(elapsed);
      setProgress(((currentTime - startTime) / (durationSeconds * 1000)) * 100);

      // Capture frame
      const frame = captureFrame();
      if (frame && videoRef.current) {
        // Detect landmarks for this frame
        const landmarkResult = await detectLandmarks(videoRef.current);
        
        if (landmarkResult.landmarks && landmarkResult.hasFace) {
          collectedFrames.push(frame);
          collectedLandmarks.push(landmarkResult.landmarks);
          
          // Detect blink and update state
          if (blinkDetectorStateRef.current) {
            const blinkResult = detectBlink(landmarkResult.landmarks, blinkDetectorStateRef.current);
            setBlinkCount(blinkResult.blinkCount);
            setCurrentEar(blinkResult.earValue);
            setIsBlinking(blinkResult.isBlinking);
          }
        }

        setFrames([...collectedFrames]);
      }

      // Wait for frame interval before next capture
      await new Promise((resolve) => setTimeout(resolve, frameIntervalMs));
    }

    setIsCollecting(false);
    setProgress(100);
    setElapsedSeconds(durationSeconds);

    // Get final blink count from state
    const finalBlinkCount = blinkDetectorStateRef.current?.blinkCounter ?? 0;

    // Only proceed if we have frames and at least minBlinks
    if (collectedFrames.length > 0 && finalBlinkCount >= minBlinks) {
      onComplete(collectedFrames, collectedLandmarks);
    } else if (collectedFrames.length > 0) {
      // Show error if not enough blinks
      console.warn(`Only ${finalBlinkCount} blinks detected. Need at least ${minBlinks}.`);
      // Reset to allow user to try again
      reset();
    }
  };

  // Check if collection is complete (duration-based or frame-based)
  const isComplete = (!isCollecting && frames.length > 0 && (elapsedSeconds >= durationSeconds || frames.length >= calculatedTargetFrames));
  const hasEnoughBlinks = blinkCount >= minBlinks;
  const canProceed = isComplete && hasEnoughBlinks;

  const displayError = error || mediaPipeError;

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
          {canProceed && (
            <div className="absolute inset-0 flex items-center justify-center bg-accent/90 animate-scale-in">
              <div className="text-center text-accent-foreground">
                <Check className="h-16 w-16 mx-auto mb-2 animate-bounce" />
                <p className="font-semibold">Ready to Mark Attendance!</p>
                <p className="text-sm mt-1">{blinkCount} blinks detected</p>
              </div>
            </div>
          )}
        </div>

        {displayError && (
          <Alert variant="destructive">
            <AlertDescription>{displayError}</AlertDescription>
          </Alert>
        )}

        {!isMediaPipeReady && isActive && (
          <Alert>
            <AlertDescription>Initializing face detection...</AlertDescription>
          </Alert>
        )}

        {/* Blink Detection Status */}
        {isActive && isMediaPipeReady && (
          <div className="space-y-2 p-4 bg-muted/50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Eye className={`h-4 w-4 ${isBlinking ? 'text-primary animate-pulse' : 'text-muted-foreground'}`} />
                <span className="text-sm font-medium">
                  {isBlinking ? 'Blinking...' : 'Eyes Open'}
                </span>
              </div>
              {currentEar !== null && (
                <span className="text-xs text-muted-foreground">
                  EAR: {currentEar.toFixed(3)}
                </span>
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Blinks Detected:</span>
              <span className={`text-lg font-bold ${hasEnoughBlinks ? 'text-accent' : 'text-foreground'}`}>
                {blinkCount} / {minBlinks}
              </span>
            </div>
            {!hasEnoughBlinks && isCollecting && (
              <p className="text-xs text-muted-foreground">
                Blink naturally {minBlinks - blinkCount} more time(s) to proceed
              </p>
            )}
            {hasEnoughBlinks && (
              <p className="text-xs text-accent font-medium">
                ✓ Liveness verification complete!
              </p>
            )}
          </div>
        )}

        {isCollecting && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Collecting frames...</span>
              <span>{elapsedSeconds}s / {durationSeconds}s ({frames.length} frames)</span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        <div className="flex gap-2">
          {!isActive ? (
            <Button onClick={startCamera} className="flex-1" disabled={!isMediaPipeReady}>
              <Camera className="mr-2 h-4 w-4" />
              Start Camera
            </Button>
          ) : (
            <>
              <Button
                onClick={handleCollect}
                disabled={isCollecting || canProceed || !isMediaPipeReady}
                className="flex-1"
              >
                {canProceed ? (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    Ready
                  </>
                ) : isCollecting ? (
                  <>
                    <Camera className="mr-2 h-4 w-4 animate-pulse" />
                    Collecting...
                  </>
                ) : (
                  <>
                    <Camera className="mr-2 h-4 w-4" />
                    Collect Frames
                  </>
                )}
              </Button>
              {canProceed && (
                <Button onClick={reset} variant="outline">
                  Reset
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </Card>
  );
};
