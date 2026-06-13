export type Landmark = [number, number];

export interface BlinkDetectorState {
  blinkCount: number;
  frameCounter: number;
  closedFrames: number;
  wasClosed: boolean;
}

const LEFT_EYE = [33, 160, 158, 133, 153, 144];
const RIGHT_EYE = [362, 385, 387, 263, 373, 380];
const EAR_THRESHOLD = 0.21;
const CONSECUTIVE_CLOSED_FRAMES = 2;

function euclidean(a: Landmark, b: Landmark): number {
  return Math.hypot(a[0] - b[0], a[1] - b[1]);
}

function eyeAspectRatio(landmarks: Landmark[], indices: number[]): number {
  const p = indices.map((i) => landmarks[i]).filter(Boolean) as Landmark[];
  if (p.length < 6) return 1;

  const vertical1 = euclidean(p[1], p[5]);
  const vertical2 = euclidean(p[2], p[4]);
  const horizontal = euclidean(p[0], p[3]);
  if (horizontal === 0) return 1;

  return (vertical1 + vertical2) / (2 * horizontal);
}

export function createBlinkDetector(): BlinkDetectorState {
  return {
    blinkCount: 0,
    frameCounter: 0,
    closedFrames: 0,
    wasClosed: false,
  };
}

export function resetBlinkDetector(state: BlinkDetectorState): void {
  state.blinkCount = 0;
  state.frameCounter = 0;
  state.closedFrames = 0;
  state.wasClosed = false;
}

export function detectBlink(
  landmarks: Landmark[],
  state: BlinkDetectorState
): { blinkCount: number; earValue: number; isBlinking: boolean } {
  if (landmarks.length < 468) {
    return { blinkCount: state.blinkCount, earValue: 1, isBlinking: false };
  }

  const leftEar = eyeAspectRatio(landmarks, LEFT_EYE);
  const rightEar = eyeAspectRatio(landmarks, RIGHT_EYE);
  const earValue = (leftEar + rightEar) / 2;
  const isClosed = earValue < EAR_THRESHOLD;

  state.frameCounter += 1;

  if (isClosed) {
    state.closedFrames += 1;
    state.wasClosed = true;
  } else if (state.wasClosed && state.closedFrames >= CONSECUTIVE_CLOSED_FRAMES) {
    state.blinkCount += 1;
    state.wasClosed = false;
    state.closedFrames = 0;
  } else {
    state.wasClosed = false;
    state.closedFrames = 0;
  }

  return {
    blinkCount: state.blinkCount,
    earValue,
    isBlinking: isClosed,
  };
}
