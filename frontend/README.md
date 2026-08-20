# TERYaq — Clinical Evidence Assistant (Frontend)

A responsive, backend-ready chatbot UI for breast-cancer clinical questions. Every answer is
presented with an evidence status, evidence-match score, and traceable source citations.

## Features

- New Conversation / Chat / History / Saved Evidence
- Dark & light mode (persisted)
- Evidence status, evidence-match ring, evidence-grounded / source-traceable / reference-backed flags
- Clickable source citations with an evidence-details panel (section, page, chunk ID, retrieved passage)
- Quick actions: Explore Chat, Copy Answer, Save Evidence
- Question composer with voice input (Web Speech API) and send button
- Loading, error, empty, and no-results states
- Medical disclaimer throughout

## Tech stack

React 19 · TypeScript · TanStack Start/Router · Tailwind CSS v4 · shadcn/ui · lucide-react · sonner

## Project structure

```
src/
  routes/
    __root.tsx          # providers (theme, store, toasts), fonts, meta
    index.tsx           # Chat page
    history.tsx         # Conversation history (search + evidence-level filter)
    saved.tsx           # Saved evidence
  components/app/
    AppShell.tsx        # sidebar + header layout (responsive, mobile drawer)
    AppSidebar.tsx      # navigation, new conversation, theme toggle
    AnswerCard.tsx      # answer + evidence badges + citations + quick actions
    EvidenceDetails.tsx # evidence detail side panel
    EvidenceBadge.tsx   # status badge + evidence-match ring
    ChatComposer.tsx    # textarea, voice input, send
  services/
    chatApi.ts          # >>> THE ONLY FILE THAT TALKS TO THE BACKEND <<<
  lib/
    types.ts            # shared domain types
    store.tsx           # conversations + saved evidence (localStorage)
    theme.tsx           # dark/light mode
    mock-data.ts        # mock answers/conversations (delete once live)
  styles.css            # design tokens (colors, fonts, radii)
```

## Install & run

```bash
npm install       # or: bun install
cp .env.example .env
npm run dev       # http://localhost:8080
npm run build     # production build
```

## Environment variables

| Variable             | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| `VITE_API_BASE_URL`  | Base URL of your backend. Empty → the UI runs on mock data.        |
| `VITE_MOCK_DELAY_MS` | Simulated latency for mock answers.                                |

Only `VITE_*` variables reach the browser — never put API keys or secrets here. Authenticated
calls should be proxied by your backend.

## Connecting your backend

1. Set `VITE_API_BASE_URL` in `.env`.
2. Change routes in `src/services/chatApi.ts`:

```ts
export const ENDPOINTS = {
  chat: "/api/chat", // <-- change to your route, e.g. "/v1/ask"
};
```

3. If your response shape differs, adapt `normalizeAnswer()` in the same file — it is the single
   mapping point between your API payload and the UI model (`ChatAnswer` in `src/lib/types.ts`).
   No component changes are required.

### Expected request

`POST {VITE_API_BASE_URL}/api/chat`

```json
{ "question": "What are the common symptoms of breast cancer?", "conversation_id": "abc123" }
```

### Expected response

```json
{
  "answer": "....",
  "evidence_status": "Strong",
  "evidence_grounded": true,
  "source_traceable": true,
  "reference_backed": true,
  "evidence_match": 87,
  "retrieved_count": 4,
  "passed_threshold_count": 3,
  "next_step": "Consult a qualified healthcare professional.",
  "follow_up_questions": ["..."],
  "citations": [
    {
      "id": "IARC-HANDB-2016",
      "title": "IARC Handbooks of Cancer Prevention",
      "source": "IARC",
      "page": 117,
      "section": "Harms of mammography screening",
      "chunk_id": "IARC-HANDB-2016-CH-0188",
      "year": 2016,
      "score": 0.81,
      "passage": "....",
      "used_in_answer": true
    }
  ]
}
```

Only `answer`, `evidence_status`, `evidence_match`, and `citations` are required; everything else
is optional and degrades gracefully.

## Mock mode

With `VITE_API_BASE_URL` empty the app answers from `src/lib/mock-data.ts` and seeds a few sample
conversations. Type a question starting with `error` to exercise the error state. Once your API is
live, set the env var — mock data is bypassed automatically.

## Disclaimer

Educational information only — not a diagnosis or medical advice.
