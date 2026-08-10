import { z } from 'zod';

export const updateProfileSchema = z.object({
  first_name: z
    .string()
    .max(150, 'First name cannot exceed 150 characters')
    .optional(),
  last_name: z
    .string()
    .max(150, 'Last name cannot exceed 150 characters')
    .optional(),
  target_exam: z
    .string()
    .max(100, 'Target exam cannot exceed 100 characters')
    .nullable()
    .optional(),
  phone_number: z
    .string()
    .max(20, 'Phone number cannot exceed 20 characters')
    .nullable()
    .optional(),
});

export type UpdateProfileFormData = z.infer<typeof updateProfileSchema>;
