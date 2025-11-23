## Environment Setup
- Python 3.12+, virtualenv per `README.md`:
  - `python -m venv spoon-env`
  - `source spoon-env/bin/activate`
  - `pip install -r requirements.txt`
- Alternative installs: `pip install spoon-ai-sdk` or `uv pip install -r requirements.txt && uv pip install -e .` (docs/installation.md).

## Runtime Configuration (Gemini)
- Copy env template and set keys:
  - `cp .env.example .env`
  - Ensure `GEMINI_API_KEY` is set; keep `ANTHROPIC_API_KEY` available for fallback later.
- Load `.env` in entry:
  - `from dotenv import load_dotenv; load_dotenv(override=True)`.
- Provider choice:
  - Use Gemini first: `llm_provider="gemini"`, model `"gemini-2.5-pro"` (README.md:375–379).
  - ChatBot validates provider/key families; Gemini keys typically start with `AIza` (spoon_ai/chat.py:373–381).

## Project Scaffold (One Agent)
- Location: `examples/agent/basic_spoonos_project/`.
- Files to add:
  - `agent.py`: `MyInfoAgent(ToolCallAgent)` with one built-in tool (`SmartWeatherTool`).
  - `main.py`: loads `.env`, constructs `ChatBot(llm_provider="gemini", model_name="gemini-2.5-pro")`, runs the agent.
- References:
  - Agent base and tool wiring: `spoon_ai/agents/toolcall.py:23–41`.
  - Example patterns: `examples/agent/my_agent_demo.py:11–110`.
  - Chat layer behavior: `spoon_ai/chat.py:100–171`.

## Agent Implementation Details
- `agent.py`:
  - Implement `SmartWeatherTool(BaseTool)` that returns weather and outfit guidance (pure HTTP, no extra API keys; follows `examples/agent/my_agent_demo.py:11–75`).
  - Implement `MyInfoAgent(ToolCallAgent)` with `available_tools = ToolManager([SmartWeatherTool()])`, `name = "my_info_agent"`, `max_steps = 5`.
- `main.py`:
  - `load_dotenv(override=True)`.
  - Instantiate `MyInfoAgent(llm=ChatBot(llm_provider="gemini", model_name="gemini-2.5-pro"))`.
  - Clear state and run on a sample prompt; print the result.

## Run & Verify
- Commands:
  - `source spoon-env/bin/activate`
  - `python examples/agent/basic_spoonos_project/main.py`
- Behavior:
  - The agent should select and call `smart_weather`; Gemini returns final response; Anthropic key can be configured later for fallback chains via `LLMManager` if desired.

## Optional MCP Variant (Later)
- Add Tavily MCP tool via stdio when needed (requires Node and `npx`): see `doc/configuration.md` and `doc/agent.md:160–172` for `MCPTool` patterns.
- Set `TAVILY_API_KEY` in `.env`.

## Next Steps (upon approval)
- Add `examples/agent/basic_spoonos_project/agent.py` and `main.py` with the described content.
- Run locally with Gemini to validate.
- Optionally configure fallback chain to Anthropic in `LLMManager` once Gemini is confirmed stable.