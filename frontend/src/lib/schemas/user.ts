import { z } from 'zod';

export const registerUserRequestSchema = z.object({
  userId: z.string().min(1, 'User ID is required'),
  userName: z.string().min(1, 'User name is required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  firstName: z.string().optional().or(z.literal('')),
  lastName: z.string().optional().or(z.literal('')),
  frames: z.array(z.string()).min(1, 'At least one frame is required'),
});

export type RegisterUserRequest = z.infer<typeof registerUserRequestSchema>;
