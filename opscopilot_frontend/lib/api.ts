// src/lib/api.ts
import axios, { AxiosError } from "axios";
import type { ProcessedItem } from "@/types/processed";
import type { NLPExtraction, NLPHistoryItem, NLPConfidenceRule, NLPRuleAction } from "@/types/nlp";


/* ========= Detección entorno & bases ========= */

const isServer = typeof window === "undefined";

/**
 * Base pública de la API que usa el frontend (CSR y SSR).
 * Lo ideal es definirla en .env.local:
 *
 *   NEXT_PUBLIC_API_URL="http://127.0.0.1:8000/api/v1"
 *
 * Si no está definida, usamos ese valor por defecto.
 */
const RAW_PUBLIC_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1"
).trim();

/**
 * Base interna para llamadas desde el servidor (SSR/ISR) si tienes
 * un hostname distinto para el backend desde el contenedor de Next.
 * Si no la usas, puede quedarse vacía.
 *
 *   INTERNAL_API_URL="http://backend:8000/api/v1"
 */
const RAW_INTERNAL_BASE = (process.env.INTERNAL_API_URL ?? "").trim();

// En servidor: preferimos INTERNAL_API_URL (absoluta). En cliente: NEXT_PUBLIC_API_URL.
const EFFECTIVE_BASE = isServer ? (RAW_INTERNAL_BASE || RAW_PUBLIC_BASE) : RAW_PUBLIC_BASE;
// Normaliza (quita barras finales)
const BASE_URL = EFFECTIVE_BASE.replace(/\/+$/, "");

/** Une base + path y valida absoluta en servidor */
function joinUrl(base: string, path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!base) return p; // sólo válido en cliente con base relativa
  if (isServer && !/^https?:\/\//i.test(base)) {
    throw new Error(
      `INTERNAL_API_URL debe ser ABSOLUTA en servidor. Valor: "${base}". ` +
        `Ejemplo: INTERNAL_API_URL="http://127.0.0.1:8000/api/v1"`
    );
  }
  return `${base}${p}`;
}

/* ========= Error tipado ========= */

export class ApiError extends Error {
  status?: number;
  payload?: unknown;
  constructor(message: string, opts?: { status?: number; payload?: unknown }) {
    super(message);
    this.name = "ApiError";
    this.status = opts?.status;
    this.payload = opts?.payload;
  }
}

/* ========= Helpers de headers (normalizados a objeto plano) ========= */

// Normaliza cualquier HeadersInit a objeto plano { [k]: v }
function normalizeHeaders(h?: HeadersInit): Record<string, string> {
  if (!h) return {};

  // Caso: array de tuplas [string, string][]
  if (Array.isArray(h)) return Object.fromEntries(h);

  // Caso: objeto Headers nativo (tanto en Node 18+ como en navegador)
  const maybeHeaders = h as any;
  if (maybeHeaders && typeof maybeHeaders.entries === "function") {
    return Object.fromEntries(maybeHeaders.entries());
  }

  // Caso: objeto plano Record<string, string>
  return { ...(h as Record<string, string>) };
}

// Devuelve SIEMPRE objeto plano (válido para fetch y axios)
function withJsonHeaders(headers?: HeadersInit): Record<string, string> {
  return { "Content-Type": "application/json", ...normalizeHeaders(headers) };
}

function withAuthHeader(
  headers: HeadersInit | undefined,
  token?: string | null
): Record<string, string> {
  const base = normalizeHeaders(headers);
  return token ? { ...base, Authorization: `Bearer ${token}` } : base;
}

/* ========= Helper de auth (SSR/ISR) ========= */

/** Carga la sesión sólo en servidor y devuelve accessToken si existe */
async function getServerAccessToken(): Promise<string | null> {
  if (!isServer) return null;
  try {
    const { getServerSession } = await import("next-auth");
    const { authOptions } = await import("@/lib/auth");
    const session: any = await getServerSession(authOptions);
    return session?.accessToken ?? null;
  } catch {
    // No bloquear peticiones si aún no está configurada la auth
    return null;
  }
}

/* ========= fetch helpers (SSR/ISR + Cliente) ========= */

type FetchInit = RequestInit & { cache?: RequestCache };

/** ==== SSR/ISR: usa token de NextAuth automáticamente ==== */
export async function apiGet<T>(path: string, init?: FetchInit): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const token = await getServerAccessToken();
  const res = await fetch(url, {
    method: "GET",
    cache: "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), token),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`GET ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiPost<T, B = unknown>(
  path: string,
  body: B,
  init?: FetchInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const token = await getServerAccessToken();
  const res = await fetch(url, {
    method: "POST",
    cache: "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), token),
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`POST ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiPut<T, B = unknown>(
  path: string,
  body: B,
  init?: FetchInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const token = await getServerAccessToken();
  const res = await fetch(url, {
    method: "PUT",
    cache: "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), token),
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`PUT ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiDelete<T = unknown>(
  path: string,
  init?: FetchInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const token = await getServerAccessToken();
  const res = await fetch(url, {
    method: "DELETE",
    cache: "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), token),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`DELETE ${path} ${res.status}`, { status: res.status, payload: text });
  }
  try {
    return (await res.json()) as T;
  } catch {
    return undefined as unknown as T;
  }
}

/** ==== Cliente (CSR): pasa el token desde useSession() si quieres ====
 *
 * const { data: session } = useSession();
 * const data = await apiClientGet<MyType>('/processed?limit=20', { token: session?.accessToken });
 *
 **/
type ClientInit = Omit<FetchInit, "headers"> & {
  headers?: HeadersInit;
  token?: string | null;
};

export async function apiClientGet<T>(
  path: string,
  init?: ClientInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const res = await fetch(url, {
    method: "GET",
    cache: init?.cache ?? "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), init?.token ?? null),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`GET ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiClientPost<T, B = unknown>(
  path: string,
  body: B,
  init?: ClientInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const res = await fetch(url, {
    method: "POST",
    cache: init?.cache ?? "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), init?.token ?? null),
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`POST ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiClientPut<T, B = unknown>(
  path: string,
  body: B,
  init?: ClientInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const res = await fetch(url, {
    method: "PUT",
    cache: init?.cache ?? "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), init?.token ?? null),
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`PUT ${path} ${res.status}`, { status: res.status, payload: text });
  }
  return (await res.json()) as T;
}

export async function apiClientDelete<T = unknown>(
  path: string,
  init?: ClientInit
): Promise<T> {
  const url = joinUrl(BASE_URL, path);
  const res = await fetch(url, {
    method: "DELETE",
    cache: init?.cache ?? "no-store",
    headers: withAuthHeader(withJsonHeaders(init?.headers || {}), init?.token ?? null),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(`DELETE ${path} ${res.status}`, { status: res.status, payload: text });
  }
  try {
    return (await res.json()) as T;
  } catch {
    return undefined as unknown as T;
  }
}

/* ========= axios (opcional) ========= */

/** Instancia axios genérica (sin token) – mantiene compatibilidad */
export const api = axios.create({
  baseURL: BASE_URL || undefined,
  timeout: 10000,
  headers: withJsonHeaders(),
});

/** Crea una instancia axios con Bearer ya añadido (útil por-request) */
export function createAxios(token?: string | null) {
  const instance = axios.create({
    baseURL: BASE_URL || undefined,
    timeout: 10000,
    headers: withAuthHeader(withJsonHeaders(), token ?? undefined),
  });

  // Interceptor de respuesta con ApiError tipado
  instance.interceptors.response.use(
    (res) => res,
    (error: AxiosError) => {
      const status = error.response?.status;
      const payload = error.response?.data;
      const method = (error.config?.method || "").toString().toUpperCase();
      const url = error.config?.url;
      const msg = `Axios ${method} ${url} ${status ?? ""}`;
      return Promise.reject(new ApiError(msg, { status, payload }));
    }
  );

  return instance;
}

/** Helpers estilo axios para compatibilidad con tu código existente */
export async function apiGetAxios<T>(url: string, params?: any): Promise<T> {
  const { data } = await api.get<T>(url, { params });
  return data;
}

export async function apiPostAxios<T, B = unknown>(
  url: string,
  body: B
): Promise<T> {
  const { data } = await api.post<T>(url, body);
  return data;
}

/* ========= Helpers específicos de OpsCopilot ========= */

/** Procesed pendientes de aprobación */
export async function getPendingProcessed(): Promise<ProcessedItem[]> {
  return apiGet<ProcessedItem[]>("/processed/pending");
}

export async function approveProcessed(id: number): Promise<ProcessedItem> {
  return apiPost<ProcessedItem>(`/processed/${id}/approve`, {});
}

export async function rejectProcessed(id: number): Promise<ProcessedItem> {
  return apiPost<ProcessedItem>(`/processed/${id}/reject`, {});
}

/** NLP: llamar al endpoint de extracción de IA */
export async function extractNlp(text: string): Promise<NLPExtraction> {
  // Esto termina siendo: BASE_URL + "/nlp/extract"
  // Con la config por defecto:
  //   http://127.0.0.1:8000/api/v1/nlp/extract
  return apiPost<NLPExtraction>("/nlp/extract", { text });
}

/** Crear un gasto procesado manual/IA */
export async function createProcessed(body: {
  item: string | null;
  amount: number | null;
  date_str: string | null;
  source_file: string | null;
  nlp_overall_confidence?: number | null;
}): Promise<ProcessedItem> {
  return apiPost<ProcessedItem>("/processed", body);
}
// Histórico de extracciones NLP (para panel de calidad)
export async function getNlpExtractions(
  limit = 50
): Promise<NLPHistoryItem[]> {
  // coincide con app/api/endpoints/nlp.py → @router.get("/extractions", ...)
  return apiGet<NLPHistoryItem[]>(`/nlp/extractions?limit=${limit}`);
}

// Payload para crear/editar reglas NLP
export type NlpRulePayload = {
  min_confidence: number;
  max_confidence: number;
  action: NLPRuleAction;
  is_active?: boolean;
};

// Reglas NLP: listar
export async function getNlpRules(): Promise<NLPConfidenceRule[]> {
  return apiGet<NLPConfidenceRule[]>("/nlp/rules");
}

// Reglas NLP: crear
export async function createNlpRule(
  body: NlpRulePayload
): Promise<NLPConfidenceRule> {
  return apiPost<NLPConfidenceRule, NlpRulePayload>("/nlp/rules", body);
}

// Reglas NLP: actualizar
export async function updateNlpRule(
  id: number,
  body: Partial<NlpRulePayload>
): Promise<NLPConfidenceRule> {
  return apiPut<NLPConfidenceRule, Partial<NlpRulePayload>>(
    `/nlp/rules/${id}`,
    body
  );
}

// Reglas NLP: eliminar
export async function deleteNlpRule(id: number): Promise<void> {
  await apiDelete<void>(`/nlp/rules/${id}`);
}
// lib/api.ts

export type ProcessedStats = {
  total_count: number;
  ia_count: number;
  pending_review: number;
  approved_count: number;
  rejected_count: number;
  avg_confidence: number | null;
};

export async function getProcessedStats(): Promise<ProcessedStats> {
  return apiGet<ProcessedStats>("/processed/stats");
}
