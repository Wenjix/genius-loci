import asyncio
import os
import sys
from dotenv import load_dotenv
from spoon_ai.chat import ChatBot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from examples.agent.basic_spoonos_project.agent import MyInfoAgent

def build_agent():
    llm = ChatBot(
        llm_provider="gemini",
        model_name="gemini-2.5-pro"
    )
    agent = MyInfoAgent(llm=llm)
    agent.clear()
    return agent

async def main():
    load_dotenv(override=True)
    agent = build_agent()
    response = await agent.run("What is the weather like in Hong Kong today?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())