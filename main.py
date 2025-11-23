import os
import sys
import json
import asyncio
import argparse
from importlib import import_module
from dotenv import load_dotenv
from spoon_ai.chat import ChatBot

def load_config():
    path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(path, "r") as f:
        return json.load(f)

def build_agent(config, agent_name):
    agent_cfg = config["agents"][agent_name]
    module = import_module(agent_cfg["module"])
    AgentClass = getattr(module, agent_cfg["class"])
    llm = ChatBot(
        llm_provider=agent_cfg.get("llm_provider"),
        model_name=agent_cfg.get("llm_model")
    )
    agent = AgentClass(llm=llm)
    agent.clear()
    return agent

async def run_once(agent, query):
    return await agent.run(query)

def main():
    load_dotenv(override=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", default=None)
    parser.add_argument("--query", default=None)
    args = parser.parse_args()
    cfg = load_config()
    agent_name = args.agent or cfg.get("default_agent")
    agent = build_agent(cfg, agent_name)
    if args.query:
        result = asyncio.run(run_once(agent, args.query))
        print(result)
        return
    try:
        while True:
            prompt = input("> ")
            if not prompt or prompt.strip().lower() in {"exit", "quit", "q"}:
                break
            result = asyncio.run(run_once(agent, prompt))
            print(result)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()