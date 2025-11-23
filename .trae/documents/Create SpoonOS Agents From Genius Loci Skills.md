## Goal
- Add an expandable toggle in the frontend to choose execution mode: default “Skills” (existing prompts), alternative “Spoons” (SpoonOS agents).
- Enforce provider policy: Vision uses OpenAI GPT‑5.1; Historian/Vibe/Treasurer use Anthropic Claude Sonnet 4.5.

## UI Changes
- Add a compact toggle button (expandable dropdown or segmented control) labeled “Mode: Skills ▾”. Options:
  - Skills (default)
  - Spoons
- Persist selection in JS (localStorage) and include it in submissions:
  - Summoning Circle: add hidden input `mode` to the form
  - Map UI: include `mode` when posting to upload endpoints
- Visual affordance: neon styling consistent with current theme; hover expands to show options.

## API Contract
- Update endpoints to accept `mode`:
  - `/api/argue`: multipart form with `wallet`, `file`, `mode`
  - Optional: create `/api/skill/{name}` and `/api/spoons/{name}` for targeted calls later
- Response unchanged except for adding `mode_used` for debugging.

## Backend Execution Modes
### Skills Mode (default)
- Use current Genius Loci pipeline:
  - Vision: OpenAI SDK Responses API with `model="gpt-5.1"` (keep existing fallback/mock)
  - Historian/Vibe/Treasurer: use `_llm_chat` but force provider `anthropic` and `model="claude-sonnet-4.5"` for consistent behavior
- Preserve current scoring and payout logic.

### Spoons Mode
- Create SkillAgent factory (no tools required initially):
  - Read `genius-loci/skills/<name>/prompt.md`
  - Instantiate `CustomAgent` with `system_prompt` set to the prompt
  - Configure ChatBot/LLM to use Anthropic provider, model `claude-sonnet-4.5`
- Composite flow:
  - Vision node remains direct OpenAI Responses call with GPT‑5.1
  - Historian/Vibe/Treasurer nodes call their respective `CustomAgent.run(input)` with the vision description as the main input
  - Vibe node still calculates `vibe_score` using keyword rules (Spoons agent output used for display only)
- Payout unchanged; continue to mock wallet in non‑RPC scenarios

## Config Integration (Optional)
- Add agent entries in `config.json` so they can be loaded via CLI:
  - `loci_historian`, `loci_vibe`, `loci_treasurer` with class `SpoonReactAI` or `CustomAgent` and aliases; provider set to Anthropic
  - Maintain `loci_vision` as an SDK call rather than a config agent due to image input nuances

## Logging & UX
- Tag logs with mode: e.g., `🧭 MODE: Spoons` at start
- Keep success metric prints intact; show TX banner as before; include amount and hash

## Verification
- Toggle defaults to Skills; submit a real image:
  - Confirm vision prints “GPT‑5.1: Analysis complete.”
  - Confirm Historian/Vibe/Treasurer use Anthropic (log provider/model in debug mode)
- Switch to Spoons; verify SkillAgents run and produce outputs, score still computed, payout/tx banner unchanged
- Manual tests: upload civic/ramen/starbucks samples; ensure amounts and balances update correctly

## Risks & Mitigations
- OpenAI image content schema variance: keep current working payload and fallback
- Anthropic rate limits: `_llm_chat` uses manager; can reuse fallback chain if needed
- Agent lifecycle: `CustomAgent` instances are ephemeral per request to avoid state bleed; later can enable preserve_state if desired
