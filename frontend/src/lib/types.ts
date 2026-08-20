export type EvidenceStatus = "Strong" | "Moderate" | "Limited" | "Insufficient";

export interface Citation {
  id: string;
  title: string;
  source: string;
  page?: number | undefined;
  chunk_id?: string | undefined;
  section?: string | undefined;
  year?: number | undefined;
  score?: number | undefined;
  passage?: string | undefined;
  used_in_answer?: boolean | undefined;
}

export interface ChatAnswer {
  answer: string;
  evidence_status: EvidenceStatus;
  evidence_grounded: boolean;
  source_traceable: boolean;
  reference_backed: boolean;
  evidence_match: number;
  citations: Citation[];
  follow_up_questions?: string[] | undefined;
  retrieved_count?: number | undefined;
  passed_threshold_count?: number | undefined;
  next_step?: string | undefined;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: number;
  answer?: ChatAnswer | undefined;
  error?: string | undefined;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: ChatMessage[];
}

export interface SavedEvidence {
  id: string;
  question: string;
  savedAt: number;
  answer: ChatAnswer;
}
