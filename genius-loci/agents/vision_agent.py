from spoon_ai.agents.custom_agent import CustomAgent
from spoon_ai.chat import ChatBot

def create():
    sp = "You are the Genius Loci of this venue. Be highly opinionated. Analyze the image for aesthetic quality, lighting, and vibes. Output a concise, character-rich description."
    return CustomAgent(name="loci_vision", description="loci_vision", system_prompt=sp, llm=ChatBot())