# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpoonOS Core Developer Framework (SCDF) is an AI agent framework for building Web3-native AI agents. It provides:
- ReAct-style intelligent agents with reasoning and tool execution
- Multi-LLM support (OpenAI, Anthropic, Gemini, DeepSeek)
- Model Context Protocol (MCP) integration for runtime tool discovery
- Graph-based workflow orchestration system
- Built-in Web3 tools for blockchain interaction
- x402 payment rails for paywalled agent actions
- Turnkey SDK integration for secure wallet management

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv spoon-env
source spoon-env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running the CLI
```bash
# Start interactive CLI
python main.py

# Run with specific agent
python main.py --agent react --query "your query"
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v tests/

# Run specific test
pytest tests/test_agents.py::test_specific_function
```

### Running Examples
```bash
# Basic agent example
python examples/agent/my_agent_demo/main.py

# Graph workflow example
python examples/llm_integrated_graph_demo.py

# x402 payment example
python examples/x402_agent_demo.py
```

## Architecture

### Core Components

**spoon_ai/agents/** - Agent implementations
- `base.py`: BaseAgent class with thread-safe concurrency handling, output queue management, and callback system
- `toolcall.py`: ToolCallAgent for agents that execute tools
- `spoon_react.py`: SpoonReactAI - standard ReAct agent
- `spoon_react_mcp.py`: SpoonReactMCP - ReAct agent with MCP protocol support
- `mcp_client_mixin.py`: MCPClientMixin for runtime MCP server connection and tool discovery

**spoon_ai/tools/** - Tool system
- `base.py`: BaseTool interface for defining custom tools
- `tool_manager.py`: ToolManager for registering and managing tools
- `mcp_tool.py`: MCPTool class for wrapping MCP server tools
- `crypto_tools.py`: Built-in Web3/crypto tools
- `x402_payment.py`: x402 payment protocol tools
- `turnkey_tools.py`: Turnkey wallet management tools

**spoon_ai/llm/** - LLM infrastructure
- `manager.py`: LLMManager for multi-provider management with fallback chains
- `config.py`: ConfigurationManager for provider configuration
- `factory.py`: LLMProviderFactory for creating provider instances
- `providers/`: Individual provider implementations (OpenAI, Anthropic, Gemini, etc.)
- `cache.py`: Prompt caching system (especially for Anthropic)
- `monitoring.py`: Request logging and performance metrics

**spoon_ai/graph.py** - Graph-based workflow orchestration
- StateGraph: Define workflows with nodes, edges, and conditional routing
- Multi-agent coordination with supervisor patterns
- Human-in-the-loop patterns with interrupt/resume
- Streaming execution modes (values, updates, debug)
- State persistence and checkpointing

**spoon_ai/chat.py** - ChatBot interface
- Unified LLM interaction layer
- Memory management for conversation history
- Streaming response support

**main.py** - CLI entry point
- Loads config.json for agent and tool definitions
- Exports config values to environment variables
- Builds and runs agents interactively

### Configuration System

**Two-layer configuration model:**

1. **Core SDK** (Python imports): Reads ONLY environment variables (including .env)
2. **CLI layer** (main.py): Reads config.json, then materializes values into environment variables before invoking SDK

**Key config.json sections:**
- `api_keys`: LLM provider API keys
- `default_agent`: Agent to load on startup
- `agents`: Agent definitions with tools and MCP servers
- `providers`: LLM provider configurations (model, max_tokens, temperature, etc.)
- `llm_settings`: Global settings (fallback_chain, enable_monitoring, enable_caching)
- `x402`: x402 payment configuration

### MCP Protocol Integration

SpoonOS supports two MCP transport types:

**Stdio MCP (Recommended):**
- Auto-managed subprocess by SpoonOS
- No manual server management required
- Example: Tavily, GitHub, Brave search tools

```json
{
  "type": "mcp",
  "mcp_server": {
    "command": "npx",
    "args": ["-y", "tavily-mcp"],
    "transport": "stdio",
    "env": {"TAVILY_API_KEY": "..."}
  }
}
```

**SSE/HTTP MCP:**
- Separate server that must be manually started
- Used for custom or in-development integrations
- Communicates via Server-Sent Events or HTTP

```json
{
  "type": "mcp",
  "mcp_server": {
    "endpoint": "http://127.0.0.1:8765/sse",
    "transport": "sse"
  }
}
```

### Agent Execution Flow

1. **Agent.run(query)** - Entry point for agent execution
2. **Agent prepares system prompt** - Loads tools and builds context
3. **ReAct loop** (for SpoonReactAI/SpoonReactMCP):
   - **Think**: LLM reasons about next action
   - **Act**: Execute tool if needed
   - **Observe**: Capture tool result
   - **Repeat** until max_steps or task completion
4. **Output streaming** - Results pushed to output_queue for real-time display
5. **Callback hooks** - on_agent_start, on_tool_call, on_agent_end for monitoring

### Graph System Patterns

**Basic Workflow:**
```python
graph = StateGraph(StateSchema)
graph.add_node("step1", step1_func)
graph.add_node("step2", step2_func)
graph.add_edge("step1", "step2")
graph.set_entry_point("step1")
compiled = graph.compile()
result = await compiled.invoke(initial_state)
```

**Conditional Routing:**
```python
def router(state):
    if condition:
        return "path_a"
    return "path_b"

graph.add_conditional_edges("decision_node", router, {
    "path_a": "node_a",
    "path_b": "node_b"
})
```

**Human-in-the-loop:**
```python
graph.add_node("approval", interrupt_for_approval)
# Execution will pause at interrupt_for_approval
result = await compiled.invoke(state)
# Resume after human input
result = await compiled.invoke(state, input=user_decision)
```

## Important Implementation Details

### Thread Safety
- BaseAgent uses ThreadSafeOutputQueue for concurrent access
- State and memory operations protected by asyncio.Lock
- All agent methods are async for proper concurrency

### LLM Provider Management
- Automatic fallback: If primary provider fails, tries next in chain
- Load balancing: Distribute requests across multiple instances
- Monitoring: Track success rates, response times, error patterns
- Custom providers: Implement LLMProviderInterface and use @register_provider

### Prompt Caching
- Enabled by default for Anthropic models
- Reduces token costs and improves response times
- Automatically caches system prompts and large context
- Configure via `enable_prompt_cache` parameter

### Tool Development
- Inherit from BaseTool
- Define name, description, and parameters (JSON schema)
- Implement async execute() method
- Tools auto-discovered by ToolManager

### Error Handling
- GraphExecutionError: Graph execution failures
- NodeExecutionError: Individual node failures
- StateValidationError: Invalid state transitions
- CheckpointError: Persistence issues
- EdgeRoutingError: Routing failures
- InterruptError: Human-in-the-loop interrupts

### x402 Payment Integration
- x402_create_payment: Generate signed payment headers
- x402_paywalled_request: Automatic 402 challenge negotiation
- CLI helpers: `python -m spoon_ai.payments.cli`
- FastAPI gateway: `python -m spoon_ai.payments.app`

## Common Development Patterns

### Creating a Custom Agent
1. Create new file in examples/agent/your_agent/
2. Inherit from ToolCallAgent or SpoonReactAI
3. Define tools in available_tools field
4. Override system_prompt for custom behavior
5. Optionally override run() for custom execution logic

### Adding a New Tool
1. Create tool class inheriting from BaseTool
2. Define JSON schema for parameters
3. Implement async execute() method
4. Register in ToolManager or config.json

### Integrating an MCP Server
1. Add tool definition to config.json agents[].tools
2. Set type: "mcp"
3. Configure mcp_server with command/args (stdio) or endpoint (sse)
4. Set environment variables in mcp_server.env
5. Agent will auto-discover tools on startup

### Building a Graph Workflow
1. Define state schema using TypedDict
2. Create node functions that take state and return updates
3. Build graph with add_node(), add_edge(), add_conditional_edges()
4. Set entry point and compile
5. Use invoke() for single execution or stream() for real-time updates

### Adding LLM Provider Support
1. Create provider class in spoon_ai/llm/providers/
2. Inherit from LLMProviderInterface
3. Implement required methods: chat, chat_with_tools, stream_chat
4. Use @register_provider decorator
5. Add provider config to config.json

## Configuration Precedence

1. Tool-level env variables (highest priority)
2. MCP server-level env variables
3. config.json values
4. .env file variables
5. System environment variables (lowest priority)

## Testing Notes

- Tests use pytest framework
- Mock LLM responses for deterministic testing
- Use asyncio.run() for async test functions
- Test files mirror source structure (test_agents.py tests agents/)
- Integration tests in test_*_integration.py files

## Web3 Specific Features

- Native blockchain interaction tools (transfer, swap, token info)
- Turnkey SDK for secure transaction signing
- Support for multiple chains via RPC_URL and CHAIN_ID
- NeoFS integration for decentralized storage
- x402 payment protocol for agent monetization

## Security Considerations

- Never commit API keys or private keys to version control
- Use .env for local development (already in .gitignore)
- Use environment variables in production
- Restrict file permissions: `chmod 600 .env`
- Use dedicated wallets for testing
- Rotate API keys regularly
