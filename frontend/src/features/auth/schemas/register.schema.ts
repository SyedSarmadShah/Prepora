import { z } from 'zod';

export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email address is required')
    .email('Please enter a valid email address')
    .max(255, 'Email address cannot exceed 255 characters'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters long'),
  first_name: z
    .string()
    .max(150, 'First name cannot exceed 150 characters')
    .optional(),
  last_name: z
    .string()
    .max(150, 'Last name cannot exceed 150 characters')
    .optional(),
});

export type RegisterFormData = z.infer<typeof registerSchema>;
