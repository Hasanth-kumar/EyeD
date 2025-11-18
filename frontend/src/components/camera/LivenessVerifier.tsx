'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useCamera } from '@/lib/hooks/useCamera';
import { useMediaPipe } from '@/lib/hooks/useMediaPipe';
import { useMarkAttendance } from '@/lib/hooks/useApi';
import {
  detectBlink,
  createBlinkDetector,
  type BlinkDetectorState,
  type Landmark,
} from '@/lib/utils/blinkDetection';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Check, X, Eye } from 'lucide-react';

/**
 * Props for LivenessVerifier component
 */
export interface LivenessVerifierProps {
  /** User information from Phase 1 recognition */
  user: {
    userId: string;
    userName: string;
    confidence: number;
    faceImage: string; // Base64 encoded frame from Phase 1
  };
  /** Callback when attendance is successfully marked */
  onComplete: () => void;
  /** Callback when an error occurs */
  onError: (error: string) => void;
  /** Minimum number of blinks required (default: 3) */
  minBlinks?: number;
}

/**
 * LivenessVerifier Component
 * 
 * Single Responsibility: Display UI for real-time blink detection and call API ONLY.
 * 
 * This component:
 * - Shows camera feed
 * - Detects blinks in real-time using blinkDetection utilities
 * - Displays blink count (e.g., "2/3 blinks")
 * - When 3+ blinks detected: Automatically calls `/api/attendance/mark` endpoint
 * - Shows success message when attendance marked
 * - Shows error message if <3 blinks: "Unable to verify Liveness and we detected less than 3 blinks"
 * - No business logic, just UI and API calls
 * 
 * Follows: @rules/ux_ui_principles.md, @rules/architecture.md
 */
export function LivenessVerifier({
  user,
  onComplete,
  onError,
  minBlinks = 3,
}: LivenessVerifierProps) {
  const [blinkCount, setBlinkCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<'detecting' | 'success' | 'error'>('detecting');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [collectedFrames, setCollectedFrames] = useState<string[]>([]);
  const [collectedLandmarks, setCollectedLandmarks] = useState<number[][][]>([]);
  const [faceDetected, setFaceDetected] = useState(false);
  const [debugInfo, setDebugInfo] = useState<{ earValue?: number; landmarksCount?: number }>({});
  
  const blinkDetectorStateRef = useRef<BlinkDetectorState>(
    createBlinkDetector()
  );
  const animationFrameRef = useRef<number | null>(null);
  const hasCalledApiRef = useRef(false);
  const lastFrameTimeRef = useRef<number>(0);
  const lastProcessedTimeRef = useRef<number>(0);

  // Initialize camera
  const { videoRef, isActive, error: cameraError, startCamera, stopCamera, captureFrame } = useCamera({
    width: 640,
    height: 480,
    facingMode: 'user',
  });

  // Initialize MediaPipe for landmark detection
  const { detectLandmarks, isReady: isMediaPipeReady, error: mediaPipeError } = useMediaPipe({
    minDetectionConfidence: 0.3,
    minTrackingConfidence: 0.3,
    numFaces: 1,
    runningMode: 'VIDEO',
  });

  // API hook for marking attendance
  const { mutate: markAttendance, isPending: isMarkingAttendance } = useMarkAttendance({
    onSuccess: (response) => {
      if (response.success) {
        setStatus('success');
        setIsProcessing(false);
        onComplete();
      } else {
        // Handle error from API response
        const errorMsg = response.message || 'Unable to verify Liveness and we detected less than 3 blinks';
        setErrorMessage(errorMsg);
        setStatus('error');
        setIsProcessing(false);
        onError(errorMsg);
      }
    },
    onError: (error) => {
      let errorMsg = 'Failed to mark attendance. Please try again.';
      
      // Handle ApiClientError with better error messages
      if (error instanceof Error) {
        // Check if it's an ApiClientError (has getUserMessage method)
        if ('getUserMessage' in error && typeof (error as any).getUserMessage === 'function') {
          errorMsg = (error as any).getUserMessage();
        } else if ('code' in error && (error as any).code === 'VALIDATION_ERROR') {
          // Handle validation errors specifically
          if ('details' in error && (error as any).details?.zodErrors) {
            const zodErrors = (error as any).details.zodErrors;
            const errorMessages = zodErrors.map((err: any) => {
              const path = err.path?.join('.') || 'field';
              return `${path}: ${err.message}`;
            });
            errorMsg = errorMessages.join('; ') || error.message;
          } else {
            errorMsg = error.message;
          }
        } else {
          errorMsg = error.message;
        }
      }
      
      console.error('[LivenessVerifier] API Error:', error);
      setErrorMessage(errorMsg);
      setStatus('error');
      setIsProcessing(false);
      onError(errorMsg);
    },
  });

  /**
   * Convert data URL to base64 string
   */
  const dataUrlToBase64 = useCallback((dataUrl: string): string => {
    const base64Match = dataUrl.match(/^data:image\/[a-z]+;base64,(.+)$/);
    return base64Match ? base64Match[1] : dataUrl.split(',')[1] || dataUrl;
  }, []);

  /**
   * Process video frame for blink detection
   */
  const processFrame = useCallback(async () => {
    if (!videoRef.current || !isActive || !isMediaPipeReady || isProcessing) {
      return;
    }

    // Throttle frame processing to avoid processing the same frame multiple times
    // Process at most once every 100ms (10 FPS for blink detection is sufficient)
    const now = performance.now();
    if (now - lastFrameTimeRef.current < 100) {
      return;
    }
    lastFrameTimeRef.current = now;

    // Check if video is actually playing and has data
    if (videoRef.current.readyState < 2) {
      // Video not ready yet
      return;
    }

    try {
      // Detect landmarks from video frame
      const landmarkResult = await detectLandmarks(videoRef.current);

      // Update face detection status
      setFaceDetected(landmarkResult.hasFace);

      if (landmarkResult.hasFace && landmarkResult.landmarks) {
        // Update debug info
        setDebugInfo({
          landmarksCount: landmarkResult.landmarks.length,
        });

        // Detect blink using blink detection utilities
        const blinkResult = detectBlink(
          landmarkResult.landmarks as Landmark[],
          blinkDetectorStateRef.current
        );

        // Update debug info with EAR value
        setDebugInfo(prev => ({
          ...prev,
          earValue: blinkResult.ear_value,
        }));

        // Update blink count
        setBlinkCount(blinkResult.blink_count);
        
        // Log debug info periodically (every 30 frames ~ 3 seconds)
        if (blinkResult.blink_count % 1 === 0 && Math.random() < 0.1) {
          console.log('[LivenessVerifier] Debug:', {
            blinkCount: blinkResult.blink_count,
            earValue: blinkResult.ear_value.toFixed(3),
            leftEAR: blinkResult.left_ear.toFixed(3),
            rightEAR: blinkResult.right_ear.toFixed(3),
            isBlinking: blinkResult.is_blinking,
            landmarksCount: landmarkResult.landmarks.length,
          });
        }

        // Capture frame for API call (collect frames during detection)
        // Continue collecting frames even after blinks are detected to ensure we have enough
        if (collectedFrames.length < 10) {
          // Collect frames periodically (every other frame to avoid too many)
          // Continue collecting until we have at least 3 frames or reach max
          if (collectedFrames.length === 0 || collectedFrames.length % 2 === 0 || collectedFrames.length < 3) {
            const frameDataUrl = captureFrame();
            if (frameDataUrl) {
              const base64Frame = dataUrlToBase64(frameDataUrl);
              setCollectedFrames((prev) => [...prev, base64Frame]);
              
              // Store landmarks for this frame
              if (landmarkResult.landmarks) {
                const landmarksArray = landmarkResult.landmarks.map((lm) => [lm[0], lm[1]]);
                setCollectedLandmarks((prev) => [...prev, landmarksArray]);
              }
            }
          }
        }

        // When 3+ blinks detected: Check if we have enough frames, then call API
        if (blinkResult.blink_count >= minBlinks && !hasCalledApiRef.current && !isMarkingAttendance) {
          // Ensure we have at least 3 frames before calling API
          // If not, collect more frames first
          if (collectedFrames.length < 3) {
            // Collect additional frames to reach minimum
            const framesNeeded = 3 - collectedFrames.length;
            let additionalFrames: string[] = [];
            let additionalLandmarks: number[][][] = [];
            
            for (let i = 0; i < framesNeeded; i++) {
              const frameDataUrl = captureFrame();
              if (frameDataUrl) {
                const base64Frame = dataUrlToBase64(frameDataUrl);
                additionalFrames.push(base64Frame);
                
                if (landmarkResult.landmarks) {
                  const landmarksArray = landmarkResult.landmarks.map((lm) => [lm[0], lm[1]]);
                  additionalLandmarks.push(landmarksArray);
                }
              }
            }
            
            // Add additional frames to collected frames
            const updatedFramesAfterCollection = [...collectedFrames, ...additionalFrames].slice(0, 10);
            const updatedLandmarksAfterCollection = [...collectedLandmarks, ...additionalLandmarks].slice(0, 10);
            
            // Update state and proceed with API call
            setCollectedFrames(updatedFramesAfterCollection);
            setCollectedLandmarks(updatedLandmarksAfterCollection);
            
            // Proceed with API call using the updated frames
            proceedWithApiCall(updatedFramesAfterCollection, updatedLandmarksAfterCollection, blinkResult.blink_count, landmarkResult.landmarks);
            return;
          }
          
          // We have enough frames, proceed immediately
          proceedWithApiCall(collectedFrames, collectedLandmarks, blinkResult.blink_count, landmarkResult.landmarks);
        }
        
        // Helper function to proceed with API call
        function proceedWithApiCall(
          currentFrames: string[],
          currentLandmarks: number[][][],
          currentBlinkCount: number,
          currentLandmarksData: Landmark[] | null
        ) {
          if (hasCalledApiRef.current) return; // Prevent duplicate calls
          
          hasCalledApiRef.current = true;
          setIsProcessing(true);

          // Capture final frame to ensure we have the latest
          const finalFrame = captureFrame();
          let updatedFrames = [...currentFrames];
          let updatedLandmarks = [...currentLandmarks];
          
          if (finalFrame) {
            const base64Frame = dataUrlToBase64(finalFrame);
            updatedFrames.push(base64Frame);
            if (updatedFrames.length > 10) {
              updatedFrames = updatedFrames.slice(-10);
            }
            
            if (currentLandmarksData) {
              const landmarksArray = currentLandmarksData.map((lm) => [lm[0], lm[1]]);
              updatedLandmarks.push(landmarksArray);
              if (updatedLandmarks.length > 10) {
                updatedLandmarks = updatedLandmarks.slice(-10);
              }
            }
          }

          // Ensure we have at least 3 frames by combining with Phase 1 frame if needed
          let framesToSend: string[] = [];
          let landmarksToSend: number[][][] = [];
          
          if (updatedFrames.length >= 3) {
            // We have enough frames, use them
            framesToSend = updatedFrames.slice(0, Math.min(10, updatedFrames.length));
            landmarksToSend = updatedLandmarks.length >= 3
              ? updatedLandmarks.slice(0, Math.min(10, updatedLandmarks.length))
              : [];
          } else {
            // Combine Phase 1 frame with collected frames to reach minimum 3
            framesToSend = [user.faceImage, ...updatedFrames].slice(0, Math.min(10, 3));
            
            // For landmarks, we may not have landmarks for Phase 1 frame
            // Use collected landmarks, pad with empty arrays if needed
            landmarksToSend = updatedLandmarks.length > 0
              ? updatedLandmarks.slice(0, Math.min(10, updatedLandmarks.length))
              : [];
            
            // Ensure we have at least 3 frames
            while (framesToSend.length < 3 && updatedFrames.length > 0) {
              // If we still don't have enough, duplicate the last frame
              framesToSend.push(updatedFrames[updatedFrames.length - 1]);
            }
          }

          console.log('[LivenessVerifier] Sending frames to API:', {
            frameCount: framesToSend.length,
            landmarkCount: landmarksToSend.length,
            blinkCount: currentBlinkCount,
          });

          // Call API - business logic is in backend
          markAttendance({
            frames: framesToSend,
            landmarks: landmarksToSend.length > 0 ? landmarksToSend : undefined,
            userId: user.userId,
            userName: user.userName,
            faceImage: user.faceImage,
            confidence: user.confidence,
            blinkCount: currentBlinkCount, // Send frontend blink count to backend
          });
        }
      } else {
        // No face detected - update debug info
        setDebugInfo({});
        // Log warning periodically if no face detected (using ref to avoid dependency)
        if (now - lastProcessedTimeRef.current > 2000) {
          console.warn('[LivenessVerifier] No face detected in frame');
          lastProcessedTimeRef.current = now;
        }
      }
    } catch (error) {
      console.error('[LivenessVerifier] Error processing frame:', error);
      // Don't stop processing on individual frame errors, but log them
      if (error instanceof Error) {
        console.error('[LivenessVerifier] Error details:', error.message, error.stack);
      }
    }
  }, [
    videoRef,
    isActive,
    isMediaPipeReady,
    isProcessing,
    detectLandmarks,
    captureFrame,
    dataUrlToBase64,
    collectedFrames,
    collectedLandmarks,
    minBlinks,
    isMarkingAttendance,
    markAttendance,
    user,
  ]);

  /**
   * Start camera and begin blink detection
   */
  useEffect(() => {
    if (isMediaPipeReady && !isActive) {
      startCamera();
    }
  }, [isMediaPipeReady, isActive, startCamera]);

  /**
   * Real-time frame processing loop
   */
  useEffect(() => {
    if (!isActive || !isMediaPipeReady || isProcessing || status !== 'detecting') {
      return;
    }

    const process = async () => {
      await processFrame();
      animationFrameRef.current = requestAnimationFrame(process);
    };

    animationFrameRef.current = requestAnimationFrame(process);

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isActive, isMediaPipeReady, isProcessing, status, processFrame]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      stopCamera();
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [stopCamera]);

  /**
   * Handle camera errors
   */
  useEffect(() => {
    if (cameraError) {
      setErrorMessage(`Camera error: ${cameraError}`);
      setStatus('error');
      onError(cameraError);
    }
  }, [cameraError, onError]);

  /**
   * Handle MediaPipe errors
   */
  useEffect(() => {
    if (mediaPipeError) {
      setErrorMessage(`MediaPipe error: ${mediaPipeError}`);
      setStatus('error');
      onError(mediaPipeError);
    }
  }, [mediaPipeError, onError]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Liveness Verification
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Camera Feed */}
          <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            {!isActive && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                <div className="text-center text-white">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
                  <p className="text-sm">Starting camera...</p>
                </div>
              </div>
            )}
          </div>

          {/* Face Detection Status */}
          {status === 'detecting' && (
            <div className="text-center space-y-2">
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-sm ${
                faceDetected 
                  ? 'bg-green-500/10 text-green-600 dark:text-green-400' 
                  : 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400'
              }`}>
                {faceDetected ? (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Face detected</span>
                  </>
                ) : (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Looking for face...</span>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Blink Count Display */}
          {status === 'detecting' && faceDetected && (
            <div className="text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-lg">
                <Eye className="h-5 w-5 text-primary" />
                <span className="text-lg font-semibold text-foreground">
                  {blinkCount} / {minBlinks} blinks
                </span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Blink naturally at least {minBlinks} times
              </p>
              {debugInfo.earValue !== undefined && (
                <p className="text-xs text-muted-foreground mt-1">
                  EAR: {debugInfo.earValue.toFixed(3)}
                </p>
              )}
            </div>
          )}

          {/* No Face Detected Warning */}
          {status === 'detecting' && !faceDetected && isActive && isMediaPipeReady && (
            <Alert>
              <AlertDescription>
                Please position your face in front of the camera with good lighting.
              </AlertDescription>
            </Alert>
          )}

          {/* Processing State */}
          {isProcessing && (
            <Alert>
              <Loader2 className="h-4 w-4 animate-spin" />
              <AlertDescription>
                Verifying liveness and marking attendance...
              </AlertDescription>
            </Alert>
          )}

          {/* Success State */}
          {status === 'success' && (
            <Alert className="border-accent bg-accent/10">
              <Check className="h-4 w-4 text-accent" />
              <AlertDescription className="text-accent">
                Attendance marked successfully!
              </AlertDescription>
            </Alert>
          )}

          {/* Error State */}
          {status === 'error' && errorMessage && (
            <Alert variant="destructive">
              <X className="h-4 w-4" />
              <AlertDescription>
                {errorMessage}
              </AlertDescription>
            </Alert>
          )}

          {/* User Info */}
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium text-foreground">
              User: {user.userName}
            </p>
            <p className="text-xs text-muted-foreground">
              Confidence: {(user.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

