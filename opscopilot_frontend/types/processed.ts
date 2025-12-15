// src/types/processed.ts
import { z } from "zod";

/* ========= Estados de revisión ========= */

export const ReviewStatusSchema = z.enum(["pending", "approved", "rejected"]);
export type ReviewStatus = z.infer<typeof ReviewStatusSchema> | null;

/* ========= Esquema tal como puede venir de la API (flexible) ========= */

export const ProcessedApiSchema = z
  .object({
    id: z.number(),
    item: z.string().nullable().optional(),
    amount: z.number().nullable().optional(),
    date_str: z.string().nullable().optional(),
    source_file: z.string().nullable().optional(),
    created_at: z.string().nullable().optional(), // ISO opcional en la API

    // 🔹 Campos relacionados con la IA / revisión (opcionales en la API)
    nlp_overall_confidence: z.number().nullable().optional(),
    needs_review: z.boolean().nullable().optional(),
    review_status: ReviewStatusSchema.nullable().optional(),
  })
  .passthrough();

export type ProcessedApi = z.infer<typeof ProcessedApiSchema>;
export const ProcessedListSchema = z.array(ProcessedApiSchema);

/* ========= Esquema/Tipo que usa el UI (created_at requerido) ========= */

export const ProcessedSchema = z.object({
  id: z.number(),
  item: z.string().nullable(),
  amount: z.number().nullable(),
  date_str: z.string().nullable(),
  source_file: z.string().nullable(),
  created_at: z.string(), // ISO

  // 🔹 Campos IA / revisión ya normalizados
  nlp_overall_confidence: z.number().nullable().optional(),
  needs_review: z.boolean().nullable().optional(),
  review_status: ReviewStatusSchema.nullable().optional(),
});

export type Processed = z.infer<typeof ProcessedSchema>;

/* ========= Payload para crear (POST /processed) ========= */

export const CreateProcessedSchema = z.object({
  item: z.string().nullable().optional(),
  amount: z
    .union([z.number(), z.string().regex(/^-?\d+(\.\d+)?$/)])
    .transform((v) => (typeof v === "string" ? Number(v) : v))
    .nullable()
    .optional(),
  date_str: z.string().nullable().optional(),
  source_file: z.string().nullable().optional(),

  // La IA puede mandar su confianza global al crear
  nlp_overall_confidence: z.number().nullable().optional(),
});

export type CreateProcessedInput = z.infer<typeof CreateProcessedSchema>;

/* ========= Normalización API -> UI ========= */

export function normalizeProcessed(row: ProcessedApi): Processed {
  return {
    id: row.id,
    item: row.item ?? null,
    amount: row.amount ?? null,
    date_str: row.date_str ?? null,
    source_file: row.source_file ?? null,
    created_at: row.created_at ?? row.date_str ?? new Date().toISOString(),

    nlp_overall_confidence: row.nlp_overall_confidence ?? null,
    needs_review: row.needs_review ?? null,
    review_status: row.review_status ?? null,
  };
}

/* ========= Alias usado en el UI (page.tsx, approvals, etc.) ========= */

export type ProcessedItem = {
  id: number;
  item: string | null;
  amount: number | null;
  date_str: string | null;
  source_file: string | null;
  created_at: string; // ISO

  // NUEVOS CAMPOS IA / REVISIÓN
  nlp_overall_confidence?: number | null;
  needs_review?: boolean | null;
  review_status?: ReviewStatus;
};
