'use client'

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CameraCapture } from '@/components/camera/CameraCapture';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useRegisterUser } from '@/lib/hooks/useApi';
import { useToast } from '@/hooks/use-toast';
import { registerUserRequestSchema, type RegisterUserRequest } from '@/lib/schemas/user';
import { z } from 'zod';
import { CheckCircle2 } from 'lucide-react';

// Form schema without frames (frames are handled separately)
const registerFormSchema = registerUserRequestSchema.omit({ frames: true });

type RegisterFormData = z.infer<typeof registerFormSchema>;

export default function RegisterPage() {
  const [frame, setFrame] = useState<string | null>(null);
  const { toast } = useToast();
  
  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerFormSchema),
    defaultValues: {
      userId: '',
      userName: '',
      email: '',
      firstName: '',
      lastName: '',
    },
  });

  const { mutate: registerUser, isPending } = useRegisterUser({
    onSuccess: (response, variables) => {
      toast({
        title: 'Registration Successful!',
        description: response.data.message || `User ${variables.userName} has been registered successfully.`,
      });
      // Reset form
      form.reset();
      setFrame(null);
    },
    onError: (error) => {
      toast({
        title: 'Registration Failed',
        description: error instanceof Error ? error.message : 'Failed to register user. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const handleFrameCapture = (capturedFrame: string) => {
    setFrame(capturedFrame);
    toast({
      title: 'Photo Captured',
      description: 'Face photo captured successfully. Fill in the user details to complete registration.',
    });
  };

  const onSubmit = (data: RegisterFormData) => {
    if (!frame) {
      toast({
        title: 'Missing Photo',
        description: 'Please capture a face photo before submitting',
        variant: 'destructive',
      });
      return;
    }

    try {
      // Extract base64 data from data URL
      const base64Match = frame.match(/^data:image\/[a-z]+;base64,(.+)$/);
      const base64Frame = base64Match ? base64Match[1] : frame.split(',')[1] || frame;

      // Validate complete request with Zod (schema will handle empty strings -> undefined)
      const validatedData = registerUserRequestSchema.parse({
        ...data,
        frames: [base64Frame], // Backend only uses the first frame
      });

      registerUser(validatedData);
    } catch (error) {
      if (error instanceof z.ZodError) {
        toast({
          title: 'Validation Error',
          description: error.errors.map((e) => e.message).join(', '),
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Error',
          description: 'Failed to process registration. Please try again.',
          variant: 'destructive',
        });
      }
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-3xl font-bold text-foreground">Register New User</h1>
        <p className="text-muted-foreground">Capture a face photo and enter user details</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="animate-slide-up stagger-1">
          <div className="space-y-4">
            <CameraCapture
              onCapture={handleFrameCapture}
              autoStart
            />
            {frame && (
              <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                <CheckCircle2 className="h-4 w-4" />
                <span>Photo captured successfully</span>
              </div>
            )}
          </div>
        </div>

        <Card className="hover-lift transition-all duration-300 animate-slide-up stagger-2">
          <CardHeader>
            <CardTitle>User Information</CardTitle>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="userId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>User ID *</FormLabel>
                      <FormControl>
                        <Input placeholder="john.doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="userName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>User Name *</FormLabel>
                      <FormControl>
                        <Input placeholder="John Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input type="email" placeholder="john.doe@company.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="firstName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input placeholder="John" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="lastName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isPending || !frame}
                >
                  {isPending ? 'Registering...' : 'Register User'}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

