'use client'

/**
 * Attendance Page - UI Coordination Only
 * 
 * Single Responsibility: Coordinate Phase 1 and Phase 2 UI flow ONLY.
 * 
 * This component:
 * - Shows Phase 1 (face recognition) first
 * - After Phase 1 success: Shows Phase 2 (LivenessVerifier component)
 * - Handles Phase 2 completion/errors
 * - NO business logic, just UI coordination
 * 
 * Follows: @rules/ux_ui_principles.md
 */

import { useState, useRef } from 'react';
import { LivenessVerifier } from '@/components/camera/LivenessVerifier';
import { CameraCapture } from '@/components/camera/CameraCapture';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Check, X, Loader2, Eye, UserPlus, RotateCcw, Upload, Users } from 'lucide-react';
import { useRecognizeFace, useMarkClassAttendance } from '@/lib/hooks/useApi';
import { useToast } from '@/hooks/use-toast';
import { type RecognizeFaceResponse } from '@/lib/schemas/attendance';
import { type MarkClassAttendanceResponse } from '@/types/attendance';
import { useRouter } from 'next/navigation';

type Phase = 'phase1' | 'phase2';
type AttendanceMode = 'individual' | 'class';

interface RecognizedUser {
  userId: string;
  userName: string;
  confidence: number;
  faceImage: string; // Base64 frame from Phase 1
}

export default function AttendancePage() {
  // UI state only - no business logic
  const [mode, setMode] = useState<AttendanceMode>('individual');
  const [phase, setPhase] = useState<Phase>('phase1');
  const [recognizedUser, setRecognizedUser] = useState<RecognizedUser | null>(null);
  const [recognitionResult, setRecognitionResult] = useState<RecognizeFaceResponse | null>(null);
  const [attendanceMarked, setAttendanceMarked] = useState(false);
  const [capturedFrame, setCapturedFrame] = useState<string>('');
  const [classAttendanceResult, setClassAttendanceResult] = useState<MarkClassAttendanceResponse | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { toast } = useToast();
  const router = useRouter();

  // API hook for class attendance
  const { mutate: markClassAttendance, isPending: isMarkingClass } = useMarkClassAttendance({
    onSuccess: (response) => {
      setClassAttendanceResult(response);
      if (response.success) {
        toast({
          title: 'Class Attendance Marked!',
          description: `Successfully marked attendance for ${response.totalMarked} student(s)`,
        });
      } else {
        toast({
          title: 'Error',
          description: response.message || 'Failed to mark class attendance',
          variant: 'destructive',
        });
      }
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to mark class attendance. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // API hook - business logic is in backend
  const { mutate: recognizeFace, isPending: isRecognizing } = useRecognizeFace({
    onSuccess: (response) => {
      setRecognitionResult(response);
      
      // Phase 1 success: Transition to Phase 2
      if (response.success && response.userId && response.userName && response.confidence !== undefined) {
        setRecognizedUser({
          userId: response.userId,
          userName: response.userName,
          confidence: response.confidence,
          faceImage: capturedFrame, // Store frame from Phase 1 for Phase 2
        });
        
        toast({
          title: 'Face Recognized!',
          description: `Welcome, ${response.userName}! Proceeding to liveness verification...`,
        });
        
        // UI coordination: Move to Phase 2
        setPhase('phase2');
      } else {
        // Phase 1 failure: Show error
        toast({
          title: 'Recognition Failed',
          description: response.message,
          variant: 'destructive',
        });
      }
    },
    onError: (error) => {
      // Error handling (UI only)
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to recognize face. Please try again.',
        variant: 'destructive',
      });
      setRecognitionResult({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to recognize face',
        dailyLimitReached: false,
      });
    },
  });

  /**
   * Handle Phase 1 capture - UI coordination only
   */
  const handlePhase1Capture = (frame: string) => {
    // Extract base64 data from data URL (UI formatting only)
    const base64Match = frame.match(/^data:image\/[a-z]+;base64,(.+)$/);
    const base64Frame = base64Match ? base64Match[1] : frame.split(',')[1] || frame;

    // Store frame for Phase 2 (UI state)
    setCapturedFrame(base64Frame);

    // Call API - business logic is in backend
    recognizeFace({ frame: base64Frame });
  };

  /**
   * Handle Phase 2 completion - UI coordination only
   */
  const handlePhase2Complete = () => {
    setAttendanceMarked(true);
    toast({
      title: 'Success!',
      description: 'Attendance marked successfully!',
    });
  };

  /**
   * Handle Phase 2 error - UI coordination only
   */
  const handlePhase2Error = (error: string) => {
    toast({
      title: 'Error',
      description: error,
      variant: 'destructive',
    });
  };

  /**
   * Handle retry - UI coordination only
   */
  const handleRetry = () => {
    setRecognitionResult(null);
    setRecognizedUser(null);
    setPhase('phase1');
    setCapturedFrame('');
  };

  /**
   * Handle register navigation - UI coordination only
   */
  const handleRegister = () => {
    router.push('/dashboard/users/register');
  };

  /**
   * Handle reset - UI coordination only
   */
  const handleReset = () => {
    setPhase('phase1');
    setRecognizedUser(null);
    setRecognitionResult(null);
    setAttendanceMarked(false);
    setCapturedFrame('');
  };

  /**
   * Handle file selection for class attendance
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: 'Invalid File',
        description: 'Please select an image file',
        variant: 'destructive',
      });
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: 'File Too Large',
        description: 'Please select an image smaller than 10MB',
        variant: 'destructive',
      });
      return;
    }

    // Read file as base64
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      // Extract base64 data (remove data URL prefix if present)
      const base64Match = result.match(/^data:image\/[a-z]+;base64,(.+)$/);
      const base64Data = base64Match ? base64Match[1] : result.split(',')[1] || result;
      setSelectedImage(result); // Store data URL for preview
      
      // Mark class attendance
      markClassAttendance({
        classImage: base64Data,
        location: undefined, // Can be added later if needed
      });
    };
    reader.onerror = () => {
      toast({
        title: 'Error',
        description: 'Failed to read file. Please try again.',
        variant: 'destructive',
      });
    };
    reader.readAsDataURL(file);
  };

  /**
   * Handle upload button click
   */
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  /**
   * Handle reset class attendance
   */
  const handleResetClassAttendance = () => {
    setClassAttendanceResult(null);
    setSelectedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-3xl font-bold text-foreground">Mark Attendance</h1>
        <p className="text-muted-foreground">
          Choose between individual or class attendance
        </p>
      </div>

      <Tabs value={mode} onValueChange={(value) => setMode(value as AttendanceMode)} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="individual" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Individual
          </TabsTrigger>
          <TabsTrigger value="class" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Class
          </TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-6 mt-6">
          <div className="text-sm text-muted-foreground">
            {phase === 'phase1' 
              ? 'Step 1: Recognize your face' 
              : 'Step 2: Verify liveness with blink detection'}
          </div>

          <div className="grid gap-6 md:grid-cols-2">
        <div>
          {phase === 'phase1' ? (
            <CameraCapture
              onCapture={handlePhase1Capture}
              autoStart={true}
            />
          ) : recognizedUser ? (
            <LivenessVerifier
              user={{
                userId: recognizedUser.userId,
                userName: recognizedUser.userName,
                confidence: recognizedUser.confidence,
                faceImage: recognizedUser.faceImage,
              }}
              onComplete={handlePhase2Complete}
              onError={handlePhase2Error}
              minBlinks={3}
            />
          ) : null}
        </div>

        <div className="space-y-4 animate-slide-up stagger-2">
          {phase === 'phase1' ? (
            <>
              <Card className="hover-lift transition-all duration-300">
                <CardHeader>
                  <CardTitle>Phase 1: Face Recognition</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3 animate-slide-up stagger-1">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 transition-transform duration-200 hover:scale-110">
                      <span className="text-primary font-semibold">1</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Position yourself</p>
                      <p className="text-sm text-muted-foreground">
                        Face the camera directly with good lighting
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">2</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Capture your face</p>
                      <p className="text-sm text-muted-foreground">
                        Click "Capture" to take a photo for recognition
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">3</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Wait for recognition</p>
                      <p className="text-sm text-muted-foreground">
                        The system will identify you and proceed to liveness verification
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {isRecognizing && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-4">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                      <div>
                        <p className="font-semibold text-foreground">Recognizing face...</p>
                        <p className="text-sm text-muted-foreground">
                          Please wait while we identify you
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {recognitionResult && !isRecognizing && (
                <Card className={recognitionResult.success ? 'border-accent' : 'border-destructive'}>
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-4">
                      {recognitionResult.success ? (
                        <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                          <Check className="h-6 w-6 text-accent" />
                        </div>
                      ) : (
                        <div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center">
                          <X className="h-6 w-6 text-destructive" />
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="font-semibold text-foreground">
                          {recognitionResult.success ? 'Face Recognized!' : 'Recognition Failed'}
                        </p>
                        <p className="text-sm text-muted-foreground">{recognitionResult.message}</p>
                        {recognitionResult.success && recognitionResult.confidence && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Confidence: {(recognitionResult.confidence * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    </div>
                    {!recognitionResult.success && (
                      <div className="flex gap-2 mt-4">
                        <Button onClick={handleRetry} variant="outline" className="flex-1">
                          <RotateCcw className="mr-2 h-4 w-4" />
                          Retry
                        </Button>
                        <Button onClick={handleRegister} className="flex-1">
                          <UserPlus className="mr-2 h-4 w-4" />
                          Register
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <>
              <Card className="hover-lift transition-all duration-300">
                <CardHeader>
                  <CardTitle>Phase 2: Liveness Verification</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {recognizedUser && (
                    <div className="mb-4 p-3 bg-accent/10 rounded-lg">
                      <p className="text-sm font-medium text-foreground">
                        Recognized: {recognizedUser.userName}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Confidence: {(recognizedUser.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                  <div className="flex items-start gap-3 animate-slide-up stagger-1">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 transition-transform duration-200 hover:scale-110">
                      <span className="text-primary font-semibold">1</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Position yourself</p>
                      <p className="text-sm text-muted-foreground">
                        Face the camera directly with good lighting
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">2</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Blink naturally</p>
                      <p className="text-sm text-muted-foreground">
                        Blink at least 3 times naturally. The system will detect blinks in real-time
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">3</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Automatic attendance</p>
                      <p className="text-sm text-muted-foreground">
                        Once 3+ blinks are detected, attendance will be marked automatically
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {attendanceMarked && (
                <Card className="border-accent">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                        <Check className="h-6 w-6 text-accent" />
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">Attendance Marked!</p>
                        <p className="text-sm text-muted-foreground">
                          Your attendance has been successfully recorded.
                        </p>
                        <div className="mt-2 space-y-1">
                          <div className="flex items-center gap-2 text-xs text-accent">
                            <Eye className="h-3 w-3" />
                            <span>Liveness verified</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <Button onClick={handleReset} variant="outline" className="w-full mt-4">
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Mark Another Attendance
                    </Button>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
        </TabsContent>

        <TabsContent value="class" className="space-y-6 mt-6">
          <div className="text-sm text-muted-foreground">
            Upload a photo of your class to mark attendance for all recognized students
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <Card className="hover-lift transition-all duration-300">
                <CardHeader>
                  <CardTitle>Upload Class Photo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  
                  {!selectedImage && !isMarkingClass && (
                    <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-muted-foreground/25 rounded-lg space-y-4">
                      <Upload className="h-12 w-12 text-muted-foreground" />
                      <div className="text-center">
                        <p className="font-medium text-foreground">Upload a class photo</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          Select an image file (JPG, PNG, etc.)
                        </p>
                      </div>
                      <Button onClick={handleUploadClick} className="w-full">
                        <Upload className="mr-2 h-4 w-4" />
                        Choose Photo
                      </Button>
                    </div>
                  )}

                  {selectedImage && !isMarkingClass && (
                    <div className="space-y-4">
                      <div className="relative rounded-lg overflow-hidden border-2 border-muted">
                        <img
                          src={selectedImage}
                          alt="Class photo preview"
                          className="w-full h-auto"
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button onClick={handleUploadClick} variant="outline" className="flex-1">
                          <Upload className="mr-2 h-4 w-4" />
                          Change Photo
                        </Button>
                        <Button onClick={handleResetClassAttendance} variant="outline" className="flex-1">
                          <RotateCcw className="mr-2 h-4 w-4" />
                          Reset
                        </Button>
                      </div>
                    </div>
                  )}

                  {isMarkingClass && (
                    <div className="flex flex-col items-center justify-center p-8 space-y-4">
                      <Loader2 className="h-12 w-12 animate-spin text-primary" />
                      <div className="text-center">
                        <p className="font-semibold text-foreground">Processing class photo...</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          Detecting faces and marking attendance
                        </p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4 animate-slide-up stagger-2">
              <Card className="hover-lift transition-all duration-300">
                <CardHeader>
                  <CardTitle>How It Works</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">1</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Upload class photo</p>
                      <p className="text-sm text-muted-foreground">
                        Take or upload a photo of your entire class
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">2</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Automatic detection</p>
                      <p className="text-sm text-muted-foreground">
                        The system detects all faces and recognizes students
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-primary font-semibold">3</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Attendance marked</p>
                      <p className="text-sm text-muted-foreground">
                        All recognized students get attendance marked automatically
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {classAttendanceResult && (
                <Card className={classAttendanceResult.success ? 'border-accent' : 'border-destructive'}>
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-4">
                        {classAttendanceResult.success ? (
                          <div className="h-12 w-12 rounded-full bg-accent/10 flex items-center justify-center">
                            <Check className="h-6 w-6 text-accent" />
                          </div>
                        ) : (
                          <div className="h-12 w-12 rounded-full bg-destructive/10 flex items-center justify-center">
                            <X className="h-6 w-6 text-destructive" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="font-semibold text-foreground">
                            {classAttendanceResult.success ? 'Attendance Marked!' : 'Processing Failed'}
                          </p>
                          <p className="text-sm text-muted-foreground">{classAttendanceResult.message}</p>
                        </div>
                      </div>

                      {classAttendanceResult.success && (
                        <div className="mt-4 p-4 bg-muted/50 rounded-lg space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Faces Detected:</span>
                            <span className="font-medium">{classAttendanceResult.totalDetected}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Students Recognized:</span>
                            <span className="font-medium">{classAttendanceResult.totalRecognized}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Attendance Marked:</span>
                            <span className="font-medium text-accent">{classAttendanceResult.totalMarked}</span>
                          </div>
                        </div>
                      )}

                      {classAttendanceResult.results.length > 0 && (
                        <div className="mt-4 space-y-2">
                          <p className="text-sm font-medium text-foreground">Results:</p>
                          <div className="max-h-48 overflow-y-auto space-y-1">
                            {classAttendanceResult.results.map((result, index) => (
                              <div
                                key={index}
                                className={`p-2 rounded text-sm ${
                                  result.success
                                    ? 'bg-accent/10 text-accent-foreground'
                                    : 'bg-destructive/10 text-destructive-foreground'
                                }`}
                              >
                                <div className="flex items-center justify-between">
                                  <span className="font-medium">{result.userName}</span>
                                  {result.success ? (
                                    <Check className="h-4 w-4" />
                                  ) : (
                                    <X className="h-4 w-4" />
                                  )}
                                </div>
                                {result.error && (
                                  <p className="text-xs mt-1 text-muted-foreground">{result.error}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <Button onClick={handleResetClassAttendance} variant="outline" className="w-full mt-4">
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Mark Another Class
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
