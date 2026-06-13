import { z } from 'zod';

export const reportParamsSchema = z.object({
  startDate: z.string(),
  endDate: z.string(),
  format: z.enum(['pdf', 'csv', 'excel']),
  type: z.enum(['summary', 'detailed', 'user']),
  userId: z.string().optional(),
});

export type ReportParams = z.infer<typeof reportParamsSchema>;
