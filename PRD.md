# 📄 Product Requirements Document (PRD)

## Project Name: Genius Loci (The Spirit of the Venue)

**Hackathon Track:** Open Innovation / AI4Science (Decentralized Intelligence)

**Core Concept:** An autonomous "Location Spirit" that uses an inverted economic model. Instead of users paying for data, the Agent uses its own crypto treasury to pay users for sensory input (photos).

---

## 1. The User Flow (The "Happy Path")

### Discovery
User visits a simple web page representing the "Spirit of the Venue."

### The Ask
The Spirit displays a **"Bounty"**:
> "I am blind. Show me the Judges. Reward: 1.0 USDC."

### Action
User inputs their wallet address and uploads a photo.

### Processing (The Black Box)
The user sees a terminal log of three sub-agents arguing:
- **Visual Agent:** Identifies the content.
- **Vibe Agent:** Rates the aesthetic/mood.
- **Treasurer Agent:** Approves the transaction.

### Reward
If approved, the user receives a real transaction hash and funds.

---

## 2. Technical Architecture (SpoonOS Graph)

The backend must use a **State Graph** where data flows between specific agent nodes.

### State Schema (LociState)

```python
class LociState(TypedDict):
    user_wallet: str          # Address to pay
    image_data: bytes         # The uploaded file
    vision_analysis: str      # Output of the Vision model
    vibe_score: int          # 0-100 score
    payout_approved: bool    # Final decision
    transaction_hash: str    # Payment confirmation
```

### Nodes (Agents)

1. **VisionNode**
   - Input: Image data
   - Output: Text description of image content
   - Model: Gemini 2.5 Pro (primary) / Claude 4.5 Sonnet (fallback)

2. **HistorianNode**
   - Input: Vision analysis + venue context
   - Output: Relevance assessment
   - Logic: "Is this actually the venue? Is this the right subject?"

3. **VibeNode**
   - Input: Vision analysis + image quality metrics
   - Output: Quality score (0-100)
   - Logic: "Is it blurry? Is it cool? Does it capture the moment?"

4. **TreasurerNode**
   - Input: Vibe score + relevance check
   - Output: Approval decision (bool)
   - Logic: `If Score > threshold AND relevant -> Approve`

5. **PayoutNode**
   - Input: Approval decision + user wallet
   - Output: Transaction hash
   - Action: Execute x402 payment via SpoonOS wallet

### Graph Flow

```
START
  ↓
VisionNode (analyze image)
  ↓
HistorianNode (check relevance) ──→ [REJECT if not relevant]
  ↓
VibeNode (rate quality) ──→ [REJECT if score < threshold]
  ↓
TreasurerNode (approve/reject decision)
  ↓
PayoutNode (execute payment) ──→ [SUCCESS with tx hash]
  ↓
END
```

---

## 3. System Personality (The "Swarm")

The agents must not sound robotic. They use **Skill Folders** to load distinct personas:

### Historian Agent
- **Personality:** Obsessed with accuracy and historical authenticity
- **Voice:** Scholarly, pedantic, concerned with temporal accuracy
- **Example Output:**
  > "Analyzing temporal markers... The judges' table configuration matches archival references from 14:32 UTC. Authenticity: VERIFIED."

### Vibe Checker Agent
- **Personality:** Gen Z aesthetic critic, street photographer mindset
- **Voice:** Casual, uses slang, focused on vibes and energy
- **Example Output:**
  > "okay lowkey this goes hard ngl 🔥 lighting is chef's kiss, composition ate and left no crumbs. vibe score: 87/100"

### Treasurer Agent
- **Personality:** Stingy bureaucrat, demands value for money
- **Voice:** Corporate, risk-averse, skeptical
- **Example Output:**
  > "BUDGET IMPACT ANALYSIS: Relevance score sufficient. Quality threshold MET. Treasury deduction: 1.0 USDC. APPROVAL GRANTED with FISCAL RESERVATION."

---

## 4. Technical Requirements

### Frontend
- **Technology:** Simple web page (HTML/JS or Next.js)
- **Features:**
  - Wallet address input field
  - Image upload (drag & drop or file picker)
  - Real-time terminal log display of agent conversations
  - Transaction confirmation display

### Backend
- **Framework:** SpoonOS Core with StateGraph
- **Components:**
  - Graph orchestration (spoon_ai.graph)
  - Vision model integration (GPT-4V or Claude 3.5 Sonnet)
  - x402 payment system (spoon_ai.payments)
  - Agent personality system (custom prompts)

### Payment System
- **Protocol:** x402 payment rails
- **Currency:** USDC on Base Sepolia (testnet for demo)
- **Treasury:** Pre-funded agent wallet
- **Amount:** 1.0 USDC per approved submission

### Vision Models
- **Primary:** Gemini 2.5 Pro (vision capabilities)
- **Fallback:** Claude 4.5 Sonnet (vision capabilities)
- **Input:** Base64 encoded image or image URL
- **Output:** Structured text analysis

---

## 5. Success Criteria

### Must Have (MVP)
- [ ] User can submit photo with wallet address
- [ ] Vision agent analyzes image content
- [ ] At least 2 personality agents provide commentary
- [ ] Payment executes on approval
- [ ] User receives transaction hash

### Should Have
- [ ] All 3 agents (Vision, Vibe, Treasurer) with distinct personalities
- [ ] Terminal log shows agent "arguments"
- [ ] Relevance checking (Historian agent)
- [ ] Quality scoring (Vibe agent)
- [ ] Rejection flow with explanation

### Nice to Have
- [ ] Agent avatars/icons
- [ ] Animated terminal output
- [ ] Historical submissions gallery
- [ ] Leaderboard of highest vibe scores
- [ ] Multiple venues/spirits

---

## 6. Data Flow Example

### Input
```json
{
  "user_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "image_data": "<base64_encoded_image>"
}
```

### Vision Analysis
```
"Three people seated at a judges' table with laptops.
Indoor venue, conference setting. Time appears to be afternoon.
Lighting: fluorescent overhead. Quality: Sharp, well-framed."
```

### Historian Check
```
VERIFIED: Matches known venue layout.
Judges' table configuration consistent with event setup.
Timestamp analysis: Plausible for event day 2.
```

### Vibe Score
```
Composition: 8/10
Lighting: 7/10
Energy capture: 9/10
Technical quality: 9/10
FINAL VIBE SCORE: 82/100
```

### Treasurer Decision
```
Threshold: 70/100
Current Score: 82/100
Relevance: VERIFIED
Decision: APPROVED
Authorization Code: GEN-LO-2024-001
```

### Output
```json
{
  "approved": true,
  "vibe_score": 82,
  "transaction_hash": "0x8f3e2d...",
  "payout_amount": "1.0 USDC",
  "agent_log": [
    "[Vision] Three judges at table, conference setting",
    "[Historian] VERIFIED venue match, plausible timestamp",
    "[Vibe] okay this actually slaps, score: 82/100 🔥",
    "[Treasurer] APPROVED. Treasury impact: -1.0 USDC"
  ]
}
```

---

## 7. Implementation Phases

### Phase 1: Core Graph (Week 1)
- Set up StateGraph with LociState schema
- Implement VisionNode with Claude/GPT-4V
- Basic approve/reject logic
- Mock payment (console log)

### Phase 2: Agent Personalities (Week 1)
- Create distinct system prompts for each agent
- Implement Historian relevance checking
- Implement Vibe scoring algorithm
- Add Treasurer logic gate

### Phase 3: Payment Integration (Week 2)
- Set up x402 payment service
- Fund agent treasury wallet
- Connect PayoutNode to real transactions
- Test payment flow end-to-end

### Phase 4: Frontend & UX (Week 2)
- Build web interface
- Implement terminal log display
- Add wallet connection
- Polish agent dialogue display

### Phase 5: Testing & Demo (Final Days)
- Test with various image types
- Verify payment execution
- Prepare demo script
- Record demo video

---

## 8. Technical Challenges & Solutions

### Challenge: Vision Model Costs
**Solution:** Use prompt caching for system prompts, implement rate limiting, set daily treasury cap

### Challenge: Payment Security
**Solution:** Use x402 protocol with verification, implement fraud detection (duplicate image hashing), set per-user submission limits

### Challenge: Agent Coordination
**Solution:** Use SpoonOS StateGraph with clear state transitions, implement timeout handling, add fallback logic

### Challenge: Personality Consistency
**Solution:** Store agent personas in separate prompt files, use temperature=0.7 for personality, validate outputs against personality guidelines

---

## 9. Demo Script

**Scene:** Hackathon Venue, Day 2

**Bounty:** "I am blind. Show me the judges. Reward: 1.0 USDC"

**Action:**
1. Present shows web interface on projector
2. Audience member volunteers
3. Takes photo of judges with phone
4. Uploads photo + enters wallet
5. Terminal shows agent debate in real-time
6. Payment executes
7. Show transaction on blockchain explorer

**Reveal:** The "Spirit" has now "seen" the judges through crowd intelligence, paid in crypto

---

## 10. Future Roadmap (Post-Hackathon)

- **Multi-Venue Deployment:** Spirit for each conference room
- **Memory System:** Agent learns venue patterns over time
- **Dynamic Bounties:** Bounty amount adjusts based on treasury and demand
- **DAO Treasury:** Community can vote to fund venue spirits
- **NFT Receipts:** Approved photos mint as venue memory NFTs
- **Social Integration:** Share approved photos to venue social media
- **Reputation System:** Regular contributors get higher payouts

---

## 11. Evaluation Metrics

### For Hackathon Judges
- **Technical Innovation:** Novel use of SpoonOS graph + x402 payments
- **User Experience:** Simple, magical interaction
- **Demo Impact:** Live payment to audience member
- **Code Quality:** Clean graph architecture, reusable components

### For Users
- **Clarity:** Is the bounty clear?
- **Trust:** Do they believe they'll get paid?
- **Delight:** Is the agent personality engaging?
- **Success Rate:** % of submissions that get approved

---

## Appendix: Key Files

```
genius-loci/
├── PRD.md                          # This file
├── CLAUDE.md                       # AI assistant guide
├── spoon_ai/
│   ├── agents/
│   │   └── loci_agents.py         # Vision, Historian, Vibe, Treasurer
│   └── graph/
│       └── loci_graph.py          # State graph definition
├── frontend/
│   ├── index.html                 # Web interface
│   └── app.js                     # Upload & display logic
├── config/
│   ├── agent_personas.json        # Personality prompts
│   └── payment_config.json        # x402 settings
└── examples/
    └── loci_demo.py               # Standalone demo script
```

---

**Last Updated:** 2025-01-23
**Status:** Pre-Development (PRD Phase)
**Team:** Solo Hackathon Entry
**Timeline:** 2 Weeks to Demo
