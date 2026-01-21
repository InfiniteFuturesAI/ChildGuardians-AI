# How to Review This Repository

> **Purpose:** Guide reviewers to the right documents, in the right order, based on their role and concerns.

---

## Start Here (Everyone)

| Document | Time | What You'll Learn |
|----------|------|-------------------|
| [COVER_LETTER.md](./COVER_LETTER.md) | 3 min | What this is, what it isn't, what we're asking |
| [README.md](./README.md) | 5 min | System overview, core principles, document map |

After these two documents, follow the path for your role below.

---

## Reading Paths by Role

### 🏛️ Legislative Staff / Policy Advisors

**Your concern:** Is this safe to support? Will it create political risk? Does it respect rights?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [docs/CHARTER.md](./docs/CHARTER.md) | Non-negotiable design assumptions |
| 2 | [docs/SURVEILLANCE_EXCLUSION.md](./docs/SURVEILLANCE_EXCLUSION.md) | Plain-language privacy guarantees |
| 3 | [docs/WHAT_THIS_SYSTEM_WILL_NEVER_DO.md](./docs/WHAT_THIS_SYSTEM_WILL_NEVER_DO.md) | Permanent boundaries — formatted for lawmakers |
| 4 | [specs/WATCHDOG.md](./specs/WATCHDOG.md) | How oversight prevents abuse |

**Skip for now:** Technical specs (API, Evidence Object schema)

**Key question this path answers:** *"Can I recommend this without creating liability?"*

---

### ⚖️ Police Legal Counsel / Agency Attorneys

**Your concern:** Will evidence from this system be admissible? What foundation is required?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [specs/FAILURE_MODES.md](./specs/FAILURE_MODES.md) | 50 ways cases collapse — and how system prevents each |
| 2 | [specs/EVIDENCE_OBJECT.md](./specs/EVIDENCE_OBJECT.md) | Complete evidence schema with chain of custody |
| 3 | [specs/DEFENSE_SIMULATOR.md](./specs/DEFENSE_SIMULATOR.md) | 35 defense challenges the system validates before export |
| 4 | [docs/LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) | Opinion template, testimony guide, data sovereignty mapping |

**Skip for now:** Dark web monitoring (Industrial Magnet), Victim Engine

**Key question this path answers:** *"Will this survive a motion to suppress?"*

---

### 👨‍⚖️ Prosecutors / District Attorneys

**Your concern:** Does this force prosecution? Does it respect discretion? Will it create disclosure problems?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [specs/GJEP.md](./specs/GJEP.md) — Section 7 | Evidence Preservation ≠ Prosecution Mandate |
| 2 | [specs/FAILURE_MODES.md](./specs/FAILURE_MODES.md) — Disclosure section | Brady/disclosure safeguards |
| 3 | [specs/DEFENSE_SIMULATOR.md](./specs/DEFENSE_SIMULATOR.md) | Pre-export validation prevents discovery surprises |
| 4 | [docs/LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) — Testimony Guide | Preparing officers for cross-examination |

**Skip for now:** Technical architecture, API specifications

**Key question this path answers:** *"Does this help me or create obligations I can't meet?"*

---

### 🖥️ Agency IT / Technical Reviewers

**Your concern:** How complex is deployment? What's the integration surface? What are the security requirements?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [docs/DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) — Part 13 | Minimal Viable Deployment (3 components, 3 weeks) |
| 2 | [specs/API.md](./specs/API.md) | Integration endpoints, auth model, rate limits |
| 3 | [specs/EVIDENCE_OBJECT.md](./specs/EVIDENCE_OBJECT.md) | Data schema and lifecycle |
| 4 | [specs/INDUSTRIAL_MAGNET.md](./specs/INDUSTRIAL_MAGNET.md) | Dark web monitoring architecture (if applicable) |

**Skip for now:** Legal appendices, failure modes (legal focus)

**Key question this path answers:** *"Can we actually deploy this with our resources?"*

---

### 🔒 Civil Liberties Reviewers / Privacy Advocates

**Your concern:** Is this surveillance? Does it respect rights? Can it be misused?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [docs/SURVEILLANCE_EXCLUSION.md](./docs/SURVEILLANCE_EXCLUSION.md) | What the system does NOT see — plain language |
| 2 | [docs/WHAT_THIS_SYSTEM_WILL_NEVER_DO.md](./docs/WHAT_THIS_SYSTEM_WILL_NEVER_DO.md) | 50+ prohibitions, permanently enforced |
| 3 | [docs/LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) — Data Sovereignty section | GDPR/privacy framework mapping |
| 4 | [specs/WATCHDOG.md](./specs/WATCHDOG.md) | Independent oversight architecture |
| 5 | [docs/CHARTER.md](./docs/CHARTER.md) | Scope lock — cannot expand beyond CSAM |

**Skip for now:** Operational specs (CIVIS-CYBER, API)

**Key question this path answers:** *"Is this actually restrained, or just marketed as restrained?"*

---

### 👶 Child Protection Organizations / NGOs

**Your concern:** Does this actually protect children? Does it prioritize victims?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [specs/VICTIM_ENGINE.md](./specs/VICTIM_ENGINE.md) | Re-victimization detection, victim services integration |
| 2 | [specs/INDUSTRIAL_MAGNET.md](./specs/INDUSTRIAL_MAGNET.md) | How resurfacing material is detected |
| 3 | [specs/WATCHDOG.md](./specs/WATCHDOG.md) | Prevents cases from being buried |
| 4 | [specs/ECP.md](./specs/ECP.md) | Preventing generation of new material |

**Skip for now:** Legal/technical implementation details

**Key question this path answers:** *"Does this center children, or just law enforcement convenience?"*

---

### 🌐 International Bodies / Treaty Organizations

**Your concern:** Does this respect sovereignty? How does cross-border coordination work?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [specs/GJEP.md](./specs/GJEP.md) | Global Justice Evidence Plane — jurisdiction-agnostic preservation |
| 2 | [docs/CHARTER.md](./docs/CHARTER.md) — Sovereignty section | No country overrides another |
| 3 | [specs/EVIDENCE_OBJECT.md](./specs/EVIDENCE_OBJECT.md) — Jurisdiction section | Permission maps, treaty requirements |
| 4 | [docs/LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) — Data Sovereignty | Cross-border data handling |

**Skip for now:** Operational deployment details

**Key question this path answers:** *"Does this create a global police force, or coordinate existing authorities?"*

---

### 👮 Frontline Investigators / CSAM Unit Officers

**Your concern:** Will this help me do my job? Will it protect me?

| Order | Document | Why |
|-------|----------|-----|
| 1 | [specs/CIVIS_CYBER.md](./specs/CIVIS_CYBER.md) | The interface you'll actually use |
| 2 | [docs/DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) — Part 5 | Officer experience, exposure limits, wellness |
| 3 | [specs/DEFENSE_SIMULATOR.md](./specs/DEFENSE_SIMULATOR.md) | How the system protects your cases |
| 4 | [docs/LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) — Testimony Guide | Preparing for court |

**Skip for now:** Architecture specs, oversight details

**Key question this path answers:** *"Does this make my job easier or harder?"*

---

## Quick Reference: Document Purposes

| Document | Primary Purpose |
|----------|-----------------|
| COVER_LETTER.md | Executive summary for decision-makers |
| README.md | Technical overview and navigation |
| CHARTER.md | Non-negotiable principles |
| SURVEILLANCE_EXCLUSION.md | Privacy guarantees (plain language) |
| WHAT_THIS_SYSTEM_WILL_NEVER_DO.md | Permanent prohibitions |
| LEGAL_APPENDICES.md | Legal templates, privacy mapping |
| DEPLOYMENT_GUIDE.md | How to adopt the system |
| EVIDENCE_OBJECT.md | Court-safe evidence schema |
| FAILURE_MODES.md | 50 ways cases fail + prevention |
| DEFENSE_SIMULATOR.md | Pre-export validation |
| WATCHDOG.md | Oversight architecture |
| INDUSTRIAL_MAGNET.md | Dark web monitoring |
| GJEP.md | Cross-border evidence preservation |
| CIVIS_CYBER.md | Investigator interface |
| VICTIM_ENGINE.md | Victim protection layer |
| ECP.md | Generation prevention |
| API.md | Technical integration |

---

## How Long Will Review Take?

| Depth | Time | What You'll Cover |
|-------|------|-------------------|
| **Executive scan** | 15 min | Cover letter + README + one role-specific doc |
| **Policy review** | 1-2 hours | Full path for your role |
| **Technical review** | 4-6 hours | All specifications |
| **Legal review** | 1-2 days | Full suite with jurisdictional mapping |

---

## Questions This Repository Answers

| Question | Start Here |
|----------|------------|
| "Is this surveillance?" | [SURVEILLANCE_EXCLUSION.md](./docs/SURVEILLANCE_EXCLUSION.md) |
| "Will evidence hold up in court?" | [FAILURE_MODES.md](./specs/FAILURE_MODES.md) |
| "Does this force prosecution?" | [GJEP.md](./specs/GJEP.md) — Section 7 |
| "How complex is deployment?" | [DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) — Part 13 |
| "What can this system never do?" | [WHAT_THIS_SYSTEM_WILL_NEVER_DO.md](./docs/WHAT_THIS_SYSTEM_WILL_NEVER_DO.md) |
| "Who provides oversight?" | [WATCHDOG.md](./specs/WATCHDOG.md) |
| "How are victims protected?" | [VICTIM_ENGINE.md](./specs/VICTIM_ENGINE.md) |
| "What about GDPR/privacy laws?" | [LEGAL_APPENDICES.md](./docs/LEGAL_APPENDICES.md) — Data Sovereignty |

---

## Feedback Welcome

If you find gaps, ambiguities, or failure modes we haven't anticipated:

- Document them
- Share them

This specification improves through critique, not protection from it.

---

*How to Review This Repository v1.0 — CHILD GUARDIANS*
