// src/types/nlp.ts

export type NLPExtraction = {
  // Texto original analizado por la IA
  raw_text: string;

  // Campos extraídos
  item: string | null;
  amount: number | null;
  date_str: string | null;

  // Alias conceptual (en backend lo rellenamos igual que item)
  concept?: string | null;

  // Confianza por campo (las que ya usas en el formulario)
  item_conf: number | null;
  amount_conf: number | null;
  date_conf: number | null;

  // Confianza global
  overall_confidence: number | null;

  // Info adicional que envía el backend
  confidences?: Record<string, number>; // ej. { item: 0.7, amount: 0.9, date_str: 0.9 }
  language?: string | null;

  // Para flujo de revisiones / approvals
  needs_review?: boolean;
  review_status?: "pending" | "approved" | "rejected";
};
// 🔹 Tipo para el histórico guardado en BD (GET /nlp/extractions)
export type NLPHistoryItem = {
  id: number;
  raw_text: string;
  item: string | null;
  amount: number | null;
  date_str: string | null;
  item_conf: number | null;
  amount_conf: number | null;
  date_conf: number | null;
  created_at: string;        // ISO
  language?: string | null;  // por si lo tienes en el modelo/schema
};
// 🔹 Acciones posibles de las reglas de confianza
export type NLPRuleAction = "AUTO_ACCEPT" | "REVIEW" | "IGNORE_OR_SUGGEST";

// 🔹 Regla de confianza NLP (GET /nlp/rules)
export type NLPConfidenceRule = {
  id: number;
  min_confidence: number;
  max_confidence: number;
  action: NLPRuleAction;
  is_active: boolean;
};