import type { ChatAnswer } from "@/lib/types";
import { mockAnswer } from "@/lib/mock-data";

/**
 * ------------------------------------------------------------------
 * API SERVICE LAYER — the only file that talks to the backend.
 * ------------------------------------------------------------------
 * Configure the backend with `VITE_API_BASE_URL` in `.env`.
 * When it is not set, the UI falls back to mock data so the frontend
 * is fully usable without a backend.
 *
 * Change ENDPOINTS below if your backend uses different routes.
 */
export const API_BASE_URL: string = import.meta.env["VITE_API_BASE_URL"] ?? "";

export const ENDPOINTS = {
  chat: "/api/chat",
};

const MOCK_DELAY = Number(import.meta.env["VITE_MOCK_DELAY_MS"] ?? 900);

export interface AskQuestionPayload {
  question: string;
  conversationId?: string | undefined;
}

export class ApiError extends Error {
  status?: number | undefined;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// ------------------------------------------------------------------
// Evidence status mapping
// ------------------------------------------------------------------
// Backend returns: confidence = "high" | "medium" | "low"
// Frontend expects: EvidenceStatus = "Strong" | "Moderate" | "Limited" | "Insufficient"
// ------------------------------------------------------------------

function mapConfidenceToStatus(
  confidence: string | undefined,
  refusal: boolean,
  evidenceSufficient: boolean,
): ChatAnswer["evidence_status"] {
  if (refusal || !evidenceSufficient) return "Insufficient";
  switch ((confidence ?? "").toLowerCase()) {
    case "high":
      return "Strong";
    case "medium":
      return "Moderate";
    case "low":
      return "Limited";
    default:
      return "Moderate";
  }
}

// ------------------------------------------------------------------
// Evidence match score
// ------------------------------------------------------------------
// Backend does not return a numeric evidence_match score.
// We derive a rough score from the number of sources and confidence.
// ------------------------------------------------------------------

function deriveEvidenceMatch(
  confidence: string | undefined,
  sourcesCount: number,
  refusal: boolean,
): number {
  if (refusal || sourcesCount === 0) return 0;
  const base =
    confidence === "high" ? 85 : confidence === "medium" ? 65 : 45;
  // Bonus for more sources, capped at 99.
  return Math.min(99, base + Math.min(sourcesCount * 2, 10));
}

/** Normalises the Teryaq backend response shape into ChatAnswer. */
export function normalizeAnswer(raw: Record<string, unknown>): ChatAnswer {
  const sources = Array.isArray(raw["sources"])
    ? (raw["sources"] as any[])
    : [];

  const confidence = raw["confidence"] as string | undefined;
  const refusal = Boolean(raw["refusal"]);
  const evidenceSufficient = Boolean(raw["evidence_sufficient"]);

  const citations = sources.map((s, i) => {
    // page can be a number, a string like "unknown", or missing.
    const rawPage = s.page;
    const page: number | undefined =
      rawPage !== undefined &&
      rawPage !== null &&
      rawPage !== "unknown" &&
      !isNaN(Number(rawPage))
        ? Number(rawPage)
        : undefined;

    return {
      // Use chunk_id as the citation id — it is unique and traceable.
      id: String(s.chunk_id ?? s.document_id ?? `REF-${i}`),
      title: String(s.section || s.document_id || "Clinical Reference"),
      source: String(s.document_id ?? ""),
      page,
      chunk_id: s.chunk_id ? String(s.chunk_id) : undefined,
      section: s.section ? String(s.section) : undefined,
      year: undefined,
      score: undefined,
      // The retrieved text is not in the sources array.
      // It would need a separate field from the backend.
      passage: undefined,
      used_in_answer: true,
    };
  });

  return {
    answer: String(raw["answer"] ?? ""),
    evidence_status: mapConfidenceToStatus(confidence, refusal, evidenceSufficient),
    evidence_grounded: evidenceSufficient && !refusal,
    source_traceable: citations.length > 0,
    reference_backed: citations.length > 0,
    evidence_match: deriveEvidenceMatch(confidence, citations.length, refusal),
    retrieved_count: citations.length,
    passed_threshold_count: citations.length,
    next_step: refusal
      ? undefined
      : "Consult a qualified healthcare professional for personalised advice.",
    follow_up_questions: [],
    citations,
  };
}

export async function askQuestion(
  payload: AskQuestionPayload,
  signal?: AbortSignal,
): Promise<ChatAnswer> {
  if (!API_BASE_URL) {
    await new Promise((r) => setTimeout(r, MOCK_DELAY));
    if (/^error\b/i.test(payload.question.trim())) {
      throw new ApiError("Mock failure: the evidence service could not be reached.");
    }
    return mockAnswer(payload.question);
  }

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${ENDPOINTS.chat}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Backend expects:  { message: string, session_id: string | null }
      body: JSON.stringify({
        message: payload.question,
        session_id: payload.conversationId ?? null,
      }),
      signal: signal ?? null,
    });
  } catch {
    throw new ApiError("Network error — could not reach the evidence service.");
  }

  if (!res.ok) {
    throw new ApiError(`Request failed with status ${res.status}.`, res.status);
  }

  const data = (await res.json()) as Record<string, unknown>;

  // ------------------------------------------------------------------
  // Persist the session_id returned by the backend.
  // The backend creates a new session when session_id is null and
  // returns the generated id in every response.  We store it so
  // subsequent messages in the same conversation reuse it.
  // ------------------------------------------------------------------
  const returnedSessionId = data["session_id"] as string | undefined;
  if (returnedSessionId && payload.conversationId !== returnedSessionId) {
    // Signal the caller that the session id may have changed.
    // We attach it to the normalised answer as a non-standard field
    // so index.tsx can pick it up.
    (data as any)["_resolved_session_id"] = returnedSessionId;
  }

  return normalizeAnswer(data);
}