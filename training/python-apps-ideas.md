Awesome—here are 5 **two-hour** interview build prompts, all LLM-centric and mapped to the JD’s emphasis on AI-first delivery, microservices/APIs, tool evaluation (LangChain/LangGraph/HF), and observability.

---

# 1) “RAG++” with Feedback & Live Re-Rank

“Build a retrieval-augmented generation service over 20–50 short docs; capture user feedback and improve ranking online.” (Hits LLMs + microservice + eval/monitoring.)

* Index: chunk 20–50 markdown files → HF embeddings → FAISS/Chroma.
* Query pipeline: hybrid recall (BM25 + vectors) → cross-encoder/LLM re-rank → answer with cited spans.
* Feedback: `POST /feedback` stores 👍/👎 per (query, doc, rank) for online re-weighting.
  **Endpoints**
* `POST /ask {q}` → `{answer, sources[], lat_ms, token_usage}`
* `POST /feedback {q, doc_id, label}` → `{ok:true}`
* `GET /metrics` → `{p50,p95,hit_rate@3,avg_rerank_ms}`
  **Success**
* Cited answers; measurable **hit\_rate\@k**; latency + token counters surfaced. (End-to-end + ops.)
  **Stretch**
* Simple “learning to re-rank” weight tweak from feedback (e.g., doc prior boosts).

---

# 2) Function-Calling Agent over Admin APIs (Guardrailed)

**What they might ask:** “Create an LLM agent that can **read** account health and **open** a support task via function calls—safely.” (Agentic LLM + system integration + safety.)
**120-min scope**

* Define tool schema: `get_account_health(id)`, `open_ticket(account_id, title)`.
* Orchestrate with LangChain/LangGraph style planner → tool → validator → final answer.
* Safety: allow-list tools; dry-run mode; require model to output rationale + chosen tool in JSON.
  **Endpoints**
* `POST /assist {goal, account_id}` → `{steps[], tool_calls[], result}`
* `GET /health` → tool versions + rate limits
  **Success**
* Deterministic JSON traces; blocked unknown tools; clear audit log of tool calls. (Microservice + guardrails.)
  **Stretch**
* Add human-in-the-loop: `X-Require-Confirm: true` to require confirmation before side-effects.

---

# 3) Spec-to-Tests Generator (LLM → Executable Checks)

**What they might ask:** “Given a short product spec, generate table-driven tests (e.g., pytest) plus a structured checklist summary.” (User-facing AI feature + integration to dev workflow.)
**120-min scope**

* Prompt LLM with few-shot examples → produce: (a) JSON checklist, (b) pytest file skeleton.
* Validate JSON against Pydantic schema; ensure code block extraction; write to `/out/tests/test_spec.py`.
* Score quality with simple rubric: #cases, presence of edge cases, lint pass.
  **Endpoints**
* `POST /generate {spec_text}` → `{checklist:[], files:[{path, content}]}`
* `GET /eval` → `{cases, edge_cases, flake8_ok}`
  **Success**
* Runnable test file; schema-valid checklist; basic quality metrics surfaced (ops mindset).
  **Stretch**
* Add “regenerate only failing sections” via `PATCH /generate`.

---

# 4) Smart Reply/Tone Controller with Policy Filters

**What they might ask:** “Draft safe, on-brand replies to customer emails; enforce tone, redact PII, and block policy violations.” (LLM generation + compliance + operationalization.)
**120-min scope**

* Pipeline: PII redaction → LLM reply draft (style system prompt) → policy classifier (LLM or zero-shot) → JSON safety report.
* Add temperature/length caps; return two variants (formal/friendly).
  **Endpoints**
* `POST /reply {email_text, persona}` → `{drafts:[...], redactions[], policy:{labels[],severity}}`
* `GET /metrics` → volume, redaction\_rate, block\_rate, avg\_tokens
  **Success**
* No PII in outputs; blocked drafts flagged with reasons; reproducible persona prompts. (Tool evaluation + monitoring.)
  **Stretch**
* Few-shot memory of brand phrases; glossary enforcement.

---

# 5) PromptOps Dashboard: Versioned Prompts & Canary Runs

**What they might ask:** “Ship a tiny prompt management service that runs **A/B** prompts across models and reports quality metrics.” (Evaluation + reporting to stakeholders.)
**120-min scope**

* Store prompts (id, text, tags), models, and test cases.
* Runner executes (prompt × model) → collects latency, token use, rubric scores (JSON validity, keyword hits).
* Canary: route `X-Exp: A|B` to prompt versions; log outcomes.
  **Endpoints**
* `POST /prompts`, `POST /cases`, `POST /run`
* `GET /results?model=...` → table of win-rate, p95, cost est
  **Success**
* Clear best prompt by **win-rate**; basic cost/latency surfaced; easy to justify tool/model choice to leadership.
  **Stretch**
* Export CSV; minimal HTML view of leaderboards.

---

## A reliable 120-minute plan (use for any of the above)

* **0–15 min**: Align scope, sketch API + data flow, pick baseline models/tools. (Own research → deployment.)
* **15–85 min**: Build the vertical slice (happy path) with FastAPI + one LLM; add schema validation & error handling.
* **85–110 min**: Add metrics (`/metrics`), sample tests/cURL, log token/latency; wire minimal evaluation. (Observability.)
* **110–120 min**: Demo + tradeoffs + “next steps” (CI/CD, model versioning, alerts, cost/latency budgets).

If you tell me which two you want to rehearse, I’ll craft a tight command-by-command build script and example payloads you can reuse live.
