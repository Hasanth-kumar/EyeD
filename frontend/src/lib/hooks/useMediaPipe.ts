'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';
import type { Landmark } from '@/lib/utils/blinkDetection';

export type { Landmark };

interface UseMediaPipeOptions {
  minDetectionConfidence?: number;
  minTrackingConfidence?: number;
  numFaces?: number;
  runningMode?: 'IMAGE' | 'VIDEO';
}

export function useMediaPipe(options: UseMediaPipeOptions = {}) {
  const {
    minDetectionConfidence = 0.3,
    minTrackingConfidence = 0.3,
    numFaces = 1,
    runningMode = 'VIDEO',
  } = options;

  const landmarkerRef = useRef<FaceLandmarker | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/wasm'
        );
        const landmarker = await FaceLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
            delegate: 'GPU',
          },
          runningMode,
          numFaces,
          minFaceDetectionConfidence: minDetectionConfidence,
          minFacePresenceConfidence: minTrackingConfidence,
          minTrackingConfidence: minTrackingConfidence,
          outputFaceBlendshapes: false,
          outputFacialTransformationMatrixes: false,
        });

        if (!cancelled) {
          landmarkerRef.current = landmarker;
          setIsReady(true);
        }
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to initialize MediaPipe';
          setError(message);
        }
      }
    }

    init();

    return () => {
      cancelled = true;
      landmarkerRef.current?.close();
      landmarkerRef.current = null;
    };
  }, [minDetectionConfidence, minTrackingConfidence, numFaces, runningMode]);

  const detectLandmarks = useCallback(
    async (video: HTMLVideoElement) => {
      const landmarker = landmarkerRef.current;
      if (!landmarker || video.readyState < 2) {
        return { landmarks: null as Landmark[] | null, hasFace: false };
      }

      const result = landmarker.detectForVideo(video, performance.now());
      const faceLandmarks = result.faceLandmarks?.[0];

      if (!faceLandmarks?.length) {
        return { landmarks: null, hasFace: false };
      }

      const landmarks: Landmark[] = faceLandmarks.map((point) => [point.x, point.y]);
      return { landmarks, hasFace: true };
    },
    []
  );

  return {
    detectLandmarks,
    isReady,
    error,
  };
}
