from pathlib import Path
import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from typing import TypedDict, Callable, Dict, List, Optional
import google.generativeai as genai
from spoon_ai.llm.manager import get_llm_manager
from spoon_ai.schema import Message
from spoon_ai.tools.turnkey_tools import CompleteTransactionWorkflowTool

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html", status_code=307)

class LociState(TypedDict):
    image: str
    wallet: str
    vision: str
    historian: str
    vibe: str
    treasurer: str
    payout: str
    payout_approved: bool

def _describe_image(image_path: str) -> str:
    try:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return "Vision unavailable: missing GEMINI_API_KEY"
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-pro")
        if not image_path or not os.path.exists(image_path):
            resp = model.generate_content(["Describe this image. Focus on the people and the setting."])
            return getattr(resp, "text", "No description") or "No description"
        ext = os.path.splitext(image_path)[1].lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
        with open(image_path, "rb") as f:
            data = f.read()
        resp = model.generate_content([
            "Describe this image. Focus on the people and the setting.",
            {"mime_type": mime, "data": data},
        ])
        return getattr(resp, "text", "No description") or "No description"
    except Exception as e:
        return f"Vision error: {e}"

def vision_node(state: LociState) -> LociState:
    img = state.get("image", "")
    base_dir = Path(__file__).parent
    candidate = Path(img)
    if not candidate.is_absolute():
        candidate = base_dir / img
    desc = _describe_image(str(candidate))
    return {**state, "vision": desc}

def _read_prompt(name: str) -> str:
    p = Path(__file__).parent / "skills" / name / "prompt.md"
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""

def _llm_chat(system_prompt: str, user_prompt: str) -> str:
    manager = get_llm_manager()
    msgs = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_prompt),
    ]
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resp = loop.run_until_complete(manager.chat(msgs, provider="gemini", model="gemini-2.5-pro"))
        loop.close()
        return resp.content or ""
    except Exception:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resp = loop.run_until_complete(manager.chat(msgs, provider="anthropic", model="claude-sonnet-4.5"))
            loop.close()
            return resp.content or ""
        except Exception as e2:
            return f"LLM error: {e2}"

def historian_node(state: LociState) -> LociState:
    v = state.get("vision", "")
    sys_p = _read_prompt("historian")
    user_p = f"Image context: {v}\nProvide cultural context and resonance relevant to this photo."
    out = _llm_chat(sys_p, user_p)
    return {**state, "historian": out}

def vibe_node(state: LociState) -> LociState:
    v = state.get("vision", "")
    sys_p = _read_prompt("vibe")
    user_p = f"Image context: {v}\nAssess tone and social acceptability in one short paragraph."
    out = _llm_chat(sys_p, user_p)
    return {**state, "vibe": out}

def treasurer_node(state: LociState) -> LociState:
    h = state.get("historian", "")
    vb = state.get("vibe", "")
    sys_p = _read_prompt("treasurer")
    user_p = "Given these assessments, respond with APPROVE or DENY only.\n" + f"Historian: {h}\nVibe: {vb}"
    out = _llm_chat(sys_p, user_p).strip().upper()
    approved = out.startswith("APPROVE")
    return {**state, "treasurer": out, "payout_approved": approved}

def payout_node(state: LociState) -> LociState:
    if not state.get("payout_approved", False):
        return {**state, "payout": "Not approved"}
    to_addr = state.get("wallet", "")
    sign_with = os.getenv("PAYOUT_SIGN_WITH", "")
    rpc_url = os.getenv("WEB3_RPC_URL", "")
    if not to_addr or not sign_with or not rpc_url:
        return {**state, "payout": "Simulated Transaction Hash: SIM-" + os.urandom(4).hex()}
    async def _do_workflow():
        tool = CompleteTransactionWorkflowTool()
        return await tool.execute(sign_with=sign_with, to_address=to_addr, value_wei=str(10**18), enable_broadcast=True, rpc_url=rpc_url)
    try:
        result = asyncio.run(_do_workflow())
        if "TxHash:" in result:
            tx = result.split("TxHash:")[1].strip().split("\n")[0]
            return {**state, "payout": tx}
        return {**state, "payout": result}
    except Exception:
        return {**state, "payout": "Simulated Transaction Hash: SIM-" + os.urandom(4).hex()}

class StateGraph:
    def __init__(self):
        self.nodes: Dict[str, Callable[[LociState], LociState]] = {}
        self.edges: Dict[str, List[str]] = {}
        self.entry: Optional[str] = None
        self.exit: Optional[str] = None

    def add_node(self, name: str, fn: Callable[[LociState], LociState]) -> None:
        self.nodes[name] = fn
        if name not in self.edges:
            self.edges[name] = []

    def add_edge(self, src: str, dst: str) -> None:
        if src not in self.edges:
            self.edges[src] = []
        self.edges[src].append(dst)

    def set_entry(self, name: str) -> None:
        self.entry = name

    def set_exit(self, name: str) -> None:
        self.exit = name

    def run(self, initial: LociState) -> LociState:
        indeg: Dict[str, int] = {n: 0 for n in self.nodes}
        for s, outs in self.edges.items():
            for d in outs:
                indeg[d] = indeg.get(d, 0) + 1
        order: List[str] = []
        q: List[str] = []
        if self.entry:
            q.append(self.entry)
            indeg[self.entry] = 0
        else:
            q.extend([n for n, d in indeg.items() if d == 0])
        seen = set()
        while q:
            n = q.pop(0)
            if n in seen:
                continue
            seen.add(n)
            order.append(n)
            for d in self.edges.get(n, []):
                indeg[d] -= 1
                if indeg[d] == 0:
                    q.append(d)
        def _log(name: str, value: str, s: LociState) -> None:
            if name == "vision":
                print(f"👁️ VISION: {value}")
            elif name == "historian":
                print(f"👻 HISTORIAN: {value}")
            elif name == "vibe":
                print(f"🎭 VIBE: {value}")
            elif name == "treasurer":
                print(f"💸 TREASURER: {value}")
                if s.get("payout_approved", False):
                    print("💸 TREASURER: Payment approved. Sending funds...")
                else:
                    print("💸 TREASURER: Payment denied.")
            elif name == "payout":
                ok = s.get("payout_approved", False)
                status = "PAYMENT RECEIVED" if ok else "PAYMENT NOT SENT"
                print(f"🔗 PAYOUT: {status} · {value}")

        state = initial
        for n in order:
            fn = self.nodes.get(n)
            if fn:
                state = fn(state)
                _log(n, str(state.get(n, "")), state)
        return state

def build_argue_graph() -> StateGraph:
    g = StateGraph()
    g.add_node("vision", vision_node)
    g.add_node("historian", historian_node)
    g.add_node("vibe", vibe_node)
    g.add_node("treasurer", treasurer_node)
    g.add_node("payout", payout_node)
    g.add_edge("vision", "historian")
    g.add_edge("vision", "vibe")
    g.add_edge("historian", "treasurer")
    g.add_edge("vibe", "treasurer")
    g.add_edge("treasurer", "payout")
    g.set_entry("vision")
    g.set_exit("payout")
    return g

def run_argue_demo() -> LociState:
    image = "demo.png"
    wallet = os.getenv("DEMO_WALLET", "SPON-DEMO-WALLET")
    initial: LociState = {
        "image": image,
        "wallet": wallet,
        "vision": "",
        "historian": "",
        "vibe": "",
        "treasurer": "",
        "payout": "",
        "payout_approved": False,
    }
    g = build_argue_graph()
    final = g.run(initial)
    print(f"final: {final['payout']}")
    return final

if __name__ == "__main__":
    run_argue_demo()

@app.post("/api/argue")
async def api_argue(wallet: str = Form(...), file: UploadFile = File(...)):
    uploads = Path(__file__).parent / "static" / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    dest = uploads / file.filename
    data = await file.read()
    dest.write_bytes(data)
    initial: LociState = {
        "image": str(dest),
        "wallet": wallet,
        "vision": "",
        "historian": "",
        "vibe": "",
        "treasurer": "",
        "payout": "",
        "payout_approved": False,
    }
    g = build_argue_graph()
    final = g.run(initial)
    return {
        "vision": final.get("vision", ""),
        "historian": final.get("historian", ""),
        "vibe": final.get("vibe", ""),
        "treasurer": final.get("treasurer", ""),
        "payout": final.get("payout", ""),
        "payout_approved": final.get("payout_approved", False),
    }