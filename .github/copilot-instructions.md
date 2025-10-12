<!--
Guidance for AI coding agents working in the LogiMAS repo.
Keep this short (20–50 lines) and code-focused. Reference files and examples.
-->
# LogiMAS — Quick instructions for AI coding agents

Purpose: help an AI agent be immediately productive in this repository by
documenting the architecture, key files, run/debug commands, and coding
patterns that are specific to LogiMAS.

1) Big picture
- This repo implements a Retrieval-Augmented Multi-Agent System for logistics.
  - Frontend: `apps/web` (Next.js; dev server runs on localhost:3000).
  - Agent backend: `packages/agents/logimas_agents` (FastAPI app in `main.py`, exposes `/agent/invoke`).
  - Agent logic: `packages/agents/logimas_agents/agents` (per-agent files) + `chains/graph.py` (LangGraph StateGraph routing).
  - Tools & infra: `packages/agents/logimas_agents/tools` (DB, routing, vector store) and `supabase/` for schema and local Supabase config.

2) How to run (developer workflow)
- Backend (agents): from the repo root run the Python dev server with the working dir at `packages/agents`:
  - cd packages/agents; uvicorn logimas_agents.main:app --reload --port 8000
  - Ensure env vars from `.env.example` are set (SUPABASE keys, GROQ_API_KEY, LLM names). The code loads `.env` relative to `packages/agents/logimas_agents`.
- Frontend: cd `apps/web`; npm run dev (Next.js runs on localhost:3000). The UI POSTs to `http://127.0.0.1:8000/agent/invoke` (see `AgentChat.tsx`).

3) Key integration points & conventions
- Agent invocation: single entrypoint POST /agent/invoke (FastAPI) — payload shape: { "query": "..." } (see `main.py`).
- Agent graph routing: `chains/graph.py` implements `route_logic(state)` with keyword lists (e.g., `mobility_keywords`, `warehouse_keywords`) — update these lists if you change routing behavior.
- Agent implementations:
  - RAG-style chains: agents often expose `..._rag_chain.invoke(query)` and return a string.
  - Tool-calling agents use an executor with `.invoke({"input": query})` and return dicts (e.g., tracking/warehouse/cost executors).
- Tools: use `@tool` decorated functions in `tools/` with Pydantic input schemas. Tools rely on `supabase_client` from `tools/database.py` for DB access and audit logging.`log_agent_decision(...)` writes to the `agent_audit_logs` table.

4) Data & secrets
- Environment template: `.env.example` — must fill SUPABASE URLs/keys and model keys (GROQ_API_KEY, LLM_MODEL_NAME, EMBEDDING_MODEL_NAME).
- DB schema: `supabase/migrations/0001_initial_schema.sql` includes `agent_audit_logs`, documents, shipments, etc.

5) Small, actionable coding conventions (from the codebase)
- When adding a new agent node, register it in `chains/graph.py` and call `log_agent_decision(agent_name, query, decision)` after invocation.
- Tools should return plain dicts (with `error` keys on failures) so the graph nodes can format/append outputs. Examples: `find_best_packaging(...)`, `calculate_route_fuel_cost(...)` in `tools/*.py`.
- Frontend expects the agent API to return JSON { response: string } (see `apps/web/components/ui/AgentChat.tsx`). Keep that contract stable.

6) Useful file pointers (examples)
- Entrypoint: `packages/agents/logimas_agents/main.py` (FastAPI + /agent/invoke)
- Graph router: `packages/agents/logimas_agents/chains/graph.py` (routing logic + node wiring)
- Tools & DB: `packages/agents/logimas_agents/tools/database.py` (supabase client, `log_agent_decision`)
- Executor examples: `packages/agents/logimas_agents/agents/tracking.py`, `warehouse.py`, `cost.py` (use `AgentExecutor` / tool-calling patterns)
- Frontend integration: `apps/web/components/ui/AgentChat.tsx` (fetch URL, UI contract)

7) When editing or extending
- Keep the `/agent/invoke` contract stable. If changing response shapes, update the frontend's `AgentChat.tsx` and the logging schema.
- Add Pydantic schemas for new tools and include them in `tools/` so other agents can call them consistently.
- If adding new environment variables, update `.env.example` and `packages/agents`'s dotenv loading path.

If anything above is unclear or you'd like more detail (run scripts, build steps, or more code examples), tell me which section to expand.
