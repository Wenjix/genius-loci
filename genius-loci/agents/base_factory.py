from pathlib import Path
from spoon_ai.agents.custom_agent import CustomAgent
from spoon_ai.chat import ChatBot

def load_skill_prompt(name: str) -> str:
    p = Path(__file__).resolve().parent.parent / "skills" / name / "prompt.md"
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""

def build_agent(name: str, system_prompt: str) -> CustomAgent:
    return CustomAgent(name=name, description=name, system_prompt=system_prompt, llm=ChatBot())