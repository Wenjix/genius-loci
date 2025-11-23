from .base_factory import load_skill_prompt, build_agent

def create():
    sp = load_skill_prompt("vibe")
    return build_agent("loci_vibe", sp)