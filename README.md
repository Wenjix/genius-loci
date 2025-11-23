# 👻 Genius Loci (The Spirit of Place)
"The Map is a Lie. We wake it up."

Genius Loci is a decentralized operating system for physical locations. It transforms static places into autonomous economic agents that pay humans to keep their digital twins alive.

Using SpoonOS State Graphs and GPT-5.1 Vision, every location spawns a "Spirit" with a crypto wallet and a personality. These Spirits post bounties for sensory data (e.g., "Show me the queue length," "Verify the menu"), verify the results with an AI swarm, and instantly pay users via the x402 protocol.

## 🎥 The Demo
(Insert your 2-minute YouTube video link here)

## 🧠 The Architecture: "The Inverted Economy"
Most maps sell user data. We invert the model: Locations pay users.

Input: A physical location (The Spirit) posts a bounty.

Sensor: A human uploads a photo.

The Swarm (SpoonOS Graph):
- 👁️ Vision Node (GPT-5.1): Semantically analyzes the scene ("I see a long line").
- 📜 Historian Node: Verifies context ("This matches the known location").
- ✨ Vibe Node: Scores quality ("Blurry photo. Rejected.").
- 💰 Treasurer Node: Executes the payout logic.

Settlement: The user receives instant USDC via x402.

## 🛠️ Tech Stack
- Framework: SpoonOS Core (Python SDK)
- Agent Logic: SpoonGraph (State Machine)
- Vision Model: OpenAI gpt-5.1-vision-preview
- Payments: x402 Protocol (Mocked for Demo Speed / Base Sepolia Ready)
- Frontend: Vanilla JS + CSS Grid (No React overhead)

## 🚀 Quick Start (Run the Spirit)

Prerequisites
- Python 3.10+
- An OpenAI API Key (with GPT-5.1 access)

1. Clone & Install
```bash
git clone https://github.com/yourusername/genius-loci.git
cd genius-loci
pip install -r requirements.txt
```

2. Configure Environment

Create a `.env` file:
```bash
OPENAI_API_KEY=sk-proj-...
# Optional: Set DEMO_MODE=True to force approval during loud/dark demos
DEMO_MODE=False
```

3. Summon the Spirit
```bash
uvicorn main:app --reload
```
Open `http://localhost:8000` to see the Spirit Map.

## 📂 Project Structure
```plaintext
/genius-loci
├── main.py              # The Brain: FastAPI + SpoonOS Graph
├── spoon/               # The Tools
│   └── mock_wallet.py   # Simulates x402 latency/gas for smooth demos
├── skills/              # The Swarm Personalities
│   ├── historian/       # Verifies facts
│   ├── vibe/            # Judges aesthetics
│   └── treasurer/       # Controls the money
└── static/              # The Frontend
    ├── index.html       # The "Summoning Circle" UI
    └── assets/          # Mock data images (Ramen, Potholes)
```

## 🏆 Hackathon Tracks
- Open Innovation: Novel use of "Inverted Economic Models" for AI agents.
- AI4Science: Decentralized data collection for physical infrastructure (DePIN).

## 🔮 Future Roadmap
- Mainnet Launch: Deploy Treasury contracts to Base Mainnet.
- AR Integration: View "Spirit Bounties" through camera overlay.
- Memory Persistence: Spirits "remember" daily patterns (e.g., "It is usually busy at 2 PM").

(Built with 👻 at the SpoonOS Hackathon 2025)