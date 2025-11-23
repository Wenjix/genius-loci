## Overview
- Deliver an end-to-end demo that shows platform utility (Feed) and a live “Judge Photo” stunt.
- Implement a simple state graph with vision → historian → vibe → treasurer → payout using existing `genius-loci/main.py`.
- Add a mock wallet for deterministic “cha-ching” behavior and wire the frontend to show a green banner with the fake hash.

## Phase 1 – Brain & Fake Bank (Hours 0–3)
- Add `spoon/mock_wallet.py`: a `MockEVMWallet` that simulates latency (sleep), prints realistic logs (e.g., `⚡ [GAS] 0.00032 ETH burned`), and returns a dict `{success: True, tx_hash: '0xMOCK...', block: 849201, amount_usdc: 1.0}`.
- Extend `LociState` in `genius-loci/main.py:35` to include `photo_desc: str`, `vibe_score: int`, `tx_hash: str` while keeping existing keys. Use `photo_desc` as a synonym for `vision` in responses.
- Mock Vision: update `_describe_image` in `genius-loci/main.py:45-66` to return fixed text when no API keys are present: `"I see a delicious bowl of ramen."`.
- Treasurer Node Integration: add a lightweight adapter in `payout_node` (`genius-loci/main.py:128-147`) to prefer `MockEVMWallet` when env vars are missing; on success, set `tx_hash` and `payout`.
- Logs/Sample Output: adjust `StateGraph._log` (`genius-loci/main.py:194-211`) to print exactly:
  - `👁️ GPT-5.1: Analysis complete.` after vision node (even in mock mode)
  - `💸 TREASURER: Value confirmed.` when `payout_approved` is true
  - `✅ [CONFIRMED] Block #849201. Sent 1.0 USDC.` when payout succeeds via mock wallet
- Ensure `run_argue_demo()` keeps default `image` and `wallet` fields and prints final `tx_hash`.

## Phase 2 – Real GPT-5.1 Upgrade (Hours 3–6)
- Dependencies: add `openai` and `python-dotenv` to `genius-loci/requirements.txt` and document `pip install openai python-dotenv`.
- Env: require `.env` with `OPENAI_API_KEY` set; keep `GEMINI_API_KEY` as fallback.
- Vision Node: replace `_describe_image` to use OpenAI SDK with `model="gpt-5.1"` and the system prompt:
  - `"You are the Genius Loci of this venue. Be highly opinionated. Analyze the image for aesthetic quality, lighting, and vibes. Output a concise, character-rich description."`
  - Send the image bytes and system message; handle errors by falling back to Gemini (`genius-loci/main.py:83-104` helper) or the mock response.
- Vibe Agent: implement simple scoring in `vibe_node` (`genius-loci/main.py:112-117`):
  - If description contains `cinematic lighting` or `rich texture` → `vibe_score = 98`
  - If contains `blurry` or `bland` → `vibe_score = 35`
  - Else → `vibe_score = 72`
  - Persist score in `state` and include one-paragraph analysis via LLM fallback.

## Phase 3 – Platform Feed (Hours 6–9)
- Assets: create `genius-loci/static/assets/ramen_good.jpg`, `genius-loci/static/assets/starbucks_closed.jpg`, `genius-loci/static/assets/pothole.jpg`.
- Frontend Summoning Circle UI: enhance `genius-loci/static/index.html` to visually theme the form as a “summoning circle” (glow, ring accents around submit) and show an image preview when the user selects a file.
- Global Spirit Activity: append a static section at the bottom with three items:
  - Item 1: `Spirit: Ramen_Bar_Tokyo. Bounty: 'Verify Broth Clarity'. Status: PAID 1.5 USDC (Vibe Score: 98/100).`
  - Item 2: `Spirit: Starbucks_Sutter. Bounty: 'Check Status'. Status: PAID 0.5 USDC.`
  - Item 3: `Spirit: Civic_Works_SF. Bounty: 'Report Damage'. Status: PAID 1.0 USDC.`
- Style: add a section header and card-list; keep typography consistent with current CSS variables.

## Phase 4 – Money Shot Polish (Hours 9–12)
- Cha-Ching UI: update the banner behavior in `index.html:141-168` to include the fake hash from API (`json.payout` or `json.tx_hash`), e.g., `PAYMENT RECEIVED · TX 0xMOCK...`.
- Banner Styling: make `.banner.success` larger and greener (already exists at `index.html:102-108`); ensure prominent display.
- API Response: ensure `/api/argue` returns `tx_hash` and `payout_approved` along with `vision/vibe/treasurer/payout` (`genius-loci/main.py:257-283`).
- Rehearsal Script:
  - Step 1 – Utility Pitch: scroll to the bottom feed and narrate the three items.
  - Step 2 – Live Stunt: upload the judges’ photo via the Summoning Circle.
  - Step 3 – Reveal: watch server logs print `GPT-5.1: Analysis...`, `TREASURER: Value confirmed`, and the green `PAYMENT RECEIVED · TX` banner.

## Verification
- Server: run `uvicorn genius-loci.main:app --port 8000 --reload` and confirm static mount works.
- Mock Mode: with no env keys, upload `ramen_good.jpg`; verify terminal prints the three lines and the banner shows the mock TX.
- Real GPT-5.1: set `OPENAI_API_KEY`; repeat upload and check that descriptions feel opinionated; confirm scoring thresholds produce 98 or 35 when keywords present.
- UI: confirm image preview and feed items render; banner toggles success/fail based on `payout_approved`.

## Notes & Risks
- OpenAI image handling requires proper SDK usage and attachment of bytes; we include robust fallback to Gemini or mock text.
- If `spoon_ai` providers aren’t image-capable via the manager, we call OpenAI SDK directly in `_describe_image` to ensure demo reliability.
- No secrets logged; `.env` is required only locally; fallback remains deterministic for onstage scenarios.
