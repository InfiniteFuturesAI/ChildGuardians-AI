# Law Enforcement Deployment Guide

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## Purpose of This Document

This guide is for **law enforcement decision-makers** evaluating CHILD GUARDIANS for deployment. It answers:

1. What is this system?
2. What is this system NOT?
3. What legal assumptions underpin it?
4. What evidence standards does it meet?
5. How does it handle jurisdiction?
6. What oversight guarantees exist?
7. How do we pilot it safely?

---

## Part 1: Executive Summary

### 1.1 What CHILD GUARDIANS Does

| Capability | Description |
|------------|-------------|
| **Detects resurfacing CSAM** | Matches known-illegal material across dark web and clearnet |
| **Creates court-ready evidence** | Evidence objects that survive defense challenge |
| **Routes to correct jurisdiction** | Automatic permission mapping by country |
| **Prevents procedural errors** | Guardrails that block trial-killing mistakes |
| **Protects victims** | Re-victimization tracking with priority alerts |
| **Ensures accountability** | Watchdog prevents suppression |

### 1.2 What CHILD GUARDIANS Does NOT Do

| Prohibition | Rationale |
|-------------|-----------|
| ❌ No deanonymization | Civil liberties protection |
| ❌ No hacking | Evidence admissibility |
| ❌ No suspect profiling | Civil liberties protection |
| ❌ No content storage | Legal compliance |
| ❌ No expansion beyond CSAM | Scope integrity |

### 1.3 Why Adopt This System?

| Benefit | Mechanism |
|---------|-----------|
| **Cleaner evidence** | Born court-safe, not fixed later |
| **Fewer dead ends** | Hash matching eliminates false positives |
| **Less officer trauma** | AI pre-filter before human review |
| **Fewer jurisdictional headaches** | Automatic permission mapping |
| **Better international cooperation** | Treaty-aware routing |
| **Political cover** | Process-based, not discretionary |

---

## Part 2: Legal Framework

### 2.1 Design Assumptions

The system is built on these legal realities:

1. **Officers cannot violate local law to "get results"**
   - System enforces jurisdiction, not officers

2. **Evidence must survive disclosure, defense challenge, and appeals**
   - Defense Attorney Simulator validates before export

3. **Jurisdictional limits are real**
   - Every evidence object contains a permission map

4. **International cooperation is slow**
   - Design for asynchronous, treaty-aware routing

### 2.2 Evidentiary Standards Met

| Standard | How System Complies |
|----------|---------------------|
| **Authentication** | Cryptographic hashes + timestamps |
| **Chain of custody** | Every touch logged, signed |
| **Foundation** | Metadata complete at creation |
| **Best evidence** | Original hash preserved |
| **Relevance** | Case linkage required |
| **Disclosure** | Brady tracking built-in |

### 2.3 Constitutional/Charter Compliance

| Right | System Safeguard |
|-------|------------------|
| **Fourth Amendment (US) / Section 8 Charter (CA)** | Legal basis required for collection |
| **Fifth Amendment / Section 7 Charter** | No self-incrimination mechanisms |
| **Sixth Amendment / Section 11 Charter** | Disclosure requirements enforced |
| **ECHR Article 8** | Passive collection only; no active intrusion |

---

## Part 3: How the System Works

### 3.1 Evidence Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    EVIDENCE FLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                            │
│  │ Collection  │ ← Passive hash matching (Industrial Magnet)│
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Validation  │ ← Pre-flight checks (legal basis, etc.)    │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Sealing     │ ← Cryptographic immutability               │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Routing     │ ← Jurisdiction permission mapping          │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Access      │ ← Officers query; system responds          │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Export      │ ← Defense Attorney Simulator validates     │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │ Court       │ ← Evidence package with certification      │
│  └─────────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Key System Components

| Component | Function |
|-----------|----------|
| **Industrial Magnet** | Passive dark web monitoring |
| **Hash Registry** | Known-CSAM database matching |
| **Evidence Object** | Court-ready evidence container |
| **GJEP** | Global evidence storage |
| **CIVIS-CYBER** | Officer query interface |
| **Defense Simulator** | Pre-export validation |
| **Watchdog** | Oversight and accountability |

---

## Part 4: Jurisdiction Handling

### 4.1 How Jurisdiction Works

Each evidence object contains a **permission map**:

```
permission_map:
  can_view_metadata: [RCMP, FBI, Europol]
  can_view_hashes: [RCMP, FBI]
  can_export_evidence: [RCMP]
  can_initiate_prosecution: [RCMP]
  must_not_access: [...]
  requires_treaty: [FBI → RCMP requires MLAT]
```

Officers never need to ask "Can we act on this?" — the system answers automatically.

### 4.2 International Cooperation

| Scenario | System Behavior |
|----------|-----------------|
| Same country (hosting + victim) | Full access to national authority |
| Different countries | Both notified; treaty requirements shown |
| Treaty required | Action blocked until treaty request logged |
| Coordinating body | Interpol/Europol get routing role |

### 4.3 Sovereignty Guarantees

- No country sees evidence it isn't entitled to
- No country can act outside its jurisdiction
- Treaty requirements are enforced, not suggested

---

## Part 5: Officer Experience

### 5.1 What Officers See

Officers interact with the system through **CIVIS-CYBER**, which:

- Shows only evidence they're permitted to access
- Provides jurisdiction status automatically
- Guides them through procedural requirements
- Blocks mistakes before they happen

### 5.2 Workflow Example

```
1. Officer logs in with agency credentials
2. Officer queries by hash, case, or victim ID
3. System returns matching evidence objects
4. Each object shows:
   - Jurisdiction status (can you act?)
   - Procedural status (is it export-ready?)
   - Risk clocks (deadlines approaching?)
   - Linked cases (related evidence?)
5. Officer selects evidence for export
6. Defense Attorney Simulator runs
7. If pass: Export proceeds
8. If fail: Remediation path shown
```

### 5.3 Error Prevention

| Common Mistake | System Prevention |
|----------------|-------------------|
| Acting without jurisdiction | Permission map blocks action |
| Missing warrant | Legal basis required at creation |
| Expired warrant | Validity checked in real-time |
| Disclosure failure | Deadline tracking with alerts |
| Chain of custody gap | All access logged automatically |

---

## Part 6: Oversight Guarantees

### 6.1 Watchdog System

The Watchdog independently monitors:

- **Inactivity**: Cases that stall are visible
- **Anomalies**: Unusual access patterns flagged
- **Suppression**: Evidence cannot be quietly buried

### 6.2 Transparency

| Report | Frequency | Audience |
|--------|-----------|----------|
| Activity Summary | Weekly | Supervisors |
| Oversight Report | Monthly | Agency heads |
| Public Transparency | Annual | Public (aggregate only) |

### 6.3 What Watchdog Does NOT Do

- Does not accuse individuals
- Does not make decisions
- Does not interfere with operations
- Only surfaces patterns for human judgment

---

## Part 7: Pilot Deployment

### 7.1 Recommended Pilot Structure

| Phase | Duration | Scope |
|-------|----------|-------|
| **Phase 1: Shadow Mode** | 3 months | Read-only; no operational dependency |
| **Phase 2: Parallel Mode** | 3 months | System + traditional methods; compare |
| **Phase 3: Assisted Mode** | 6 months | System primary; traditional backup |
| **Phase 4: Full Deployment** | Ongoing | System is operational standard |

### 7.2 Phase 1: Shadow Mode

| Activity | Description |
|----------|-------------|
| Connect to system | Read-only access |
| View evidence objects | No action taken |
| Compare to existing cases | Validate accuracy |
| Identify gaps | Report to development team |
| Train officers | Familiarization without risk |

### 7.3 Success Criteria for Phase Advancement

| Metric | Phase 1→2 | Phase 2→3 | Phase 3→4 |
|--------|-----------|-----------|-----------|
| Evidence accuracy | >95% | >98% | >99% |
| Jurisdiction correctness | >95% | >99% | 100% |
| Officer satisfaction | Neutral | Positive | Strong positive |
| Defense Simulator pass rate | N/A | >90% | >95% |
| Zero false accusations | Required | Required | Required |

---

## Part 8: Training Requirements

### 8.1 Role-Based Training

| Role | Training Duration | Topics |
|------|-------------------|--------|
| **Officer** | 4 hours | System use, evidence handling |
| **Supervisor** | 8 hours | Above + oversight, alerts |
| **Administrator** | 16 hours | Above + configuration, audit |
| **Prosecutor** | 4 hours | Evidence export, court presentation |

### 8.2 Training Modules

| Module | Content |
|--------|---------|
| **System Overview** | What it does, what it doesn't do |
| **Evidence Objects** | Structure, lifecycle, immutability |
| **Jurisdiction Handling** | Permission maps, treaty requirements |
| **Defense Simulator** | How it works, remediation paths |
| **Watchdog Alerts** | What they mean, how to respond |
| **Court Presentation** | Explaining evidence to judges |

### 8.3 Embedded Learning

The system teaches as officers work:
- Explanations for blocked actions
- Legal rationale for requirements
- Remediation guidance for failures

---

## Part 9: Technical Requirements

### 9.1 Connectivity

| Requirement | Specification |
|-------------|---------------|
| Internet access | Secure, monitored |
| VPN to GJEP | Required for evidence access |
| Authentication | Agency SSO or issued credentials |
| Encryption | TLS 1.3 minimum |

### 9.2 Workstation Requirements

| Component | Minimum |
|-----------|---------|
| Browser | Modern (Chrome, Edge, Firefox) |
| Authentication | Hardware token or biometric |
| Screen privacy | Required for evidence review |

### 9.3 Data Handling

| Data Type | Handling |
|-----------|----------|
| Evidence objects | Never stored locally |
| Hashes | May be cached for matching |
| Reports | May be exported (logged) |
| Content | Never accessible to officers |

---

## Part 10: Addressing Common Concerns

### 10.1 "Will this create more work?"

**No.** The system:
- Pre-validates evidence (less court prep)
- Automates jurisdiction checks (less research)
- Prevents mistakes (less remediation)
- Tracks deadlines (less manual monitoring)

### 10.2 "Will defense attorneys attack this system?"

**They can try.** The system is designed to survive:
- Every evidence object passes Defense Simulator
- Methodology is documented and auditable
- Chain of custody is cryptographically proven
- The system invites scrutiny, not avoiding it

### 10.3 "Will this expose officers to trauma?"

**Less than current methods.** The system:
- AI pre-filters before human review
- Enforces exposure limits
- Tracks wellness indicators
- Mandates rotation

### 10.4 "Will this create liability?"

**Less than current methods.** The system:
- Prevents procedural errors
- Documents all actions
- Provides political cover (process-based)
- Shares burden across jurisdictions

### 10.5 "Can we trust a global system?"

**You don't have to trust it — audit it.** The system:
- Is open-source
- Has independent oversight
- Publishes transparency reports
- Respects sovereignty by design

---

## Part 11: Getting Started

### 11.1 Decision Checklist

| Question | Answer Required |
|----------|-----------------|
| Is there executive sponsorship? | Yes |
| Is there legal review approval? | Yes |
| Is there IT security approval? | Yes |
| Is there union/association consultation? | Recommended |
| Is there public affairs preparation? | Recommended |

### 11.2 Initial Steps

1. **Designate pilot lead** — Single point of contact
2. **Complete legal review** — Confirm jurisdictional compliance
3. **Complete security assessment** — Confirm technical requirements
4. **Select pilot unit** — Cybercrime or child exploitation unit
5. **Schedule training** — Before Phase 1 begins
6. **Establish reporting** — Weekly check-ins during pilot

### 11.3 Support Available

| Resource | Description |
|----------|-------------|
| **Technical support** | 24/7 during pilot |
| **Legal guidance** | Model policies and court templates |
| **Training materials** | Role-based modules |
| **Community forum** | Lessons learned from other agencies |

---

## Part 12: Summary

### What This System Gives You

| Benefit | How It's Delivered |
|---------|---------------------|
| Evidence that survives court | Defense Attorney Simulator |
| Jurisdictional clarity | Automatic permission mapping |
| Procedural guardrails | Pre-flight checks, risk clocks |
| Officer protection | AI pre-filter, exposure limits |
| Political cover | Process-based, not discretionary |
| International cooperation | Treaty-aware routing |
| Accountability | Watchdog oversight |

### What This System Asks of You

| Requirement | Rationale |
|-------------|-----------|
| Follow procedural requirements | Evidence must be court-safe |
| Respond to Watchdog alerts | Accountability is mutual |
| Participate in transparency | Public trust is earned |
| Provide feedback | System improves with use |

### The Bottom Line

> **Police want this. The public will demand it. This guide shows how to deploy it safely.**

The system is designed for law enforcement, by understanding law enforcement:
- Your constraints are encoded in the design
- Your procedures are enforced by the system
- Your officers are protected, not burdened
- Your cases survive court, not collapse in it

---

## Part 13: Minimal Viable Deployment (Fast Start)

### Purpose

Not every agency needs the full ecosystem on day one. This section defines the **smallest useful deployment** that delivers value immediately.

---

### Minimal Configuration (3 Components)

| Component | Function | Time to Deploy |
|-----------|----------|----------------|
| **Hash Registry** | Query known CSAM hashes | 1 week |
| **Evidence Object** | Create court-safe evidence packages | 1 week |
| **Defense Simulator** | Pre-export validation | 1 week |

**Total: 3 weeks to operational capability**

---

### What This Gives You

| Capability | Immediate Value |
|------------|----------------|
| ✅ Hash matching | Confirm illegal material instantly |
| ✅ Chain of custody | Court-ready from day one |
| ✅ Pre-flight checks | Catch trial-killing errors before they happen |

---

### What This Does NOT Give You (Add Later)

| Component | Add When |
|-----------|----------|
| Industrial Magnet | When ready for dark web monitoring |
| GJEP | When cross-border coordination needed |
| Victim Engine | When victim services integration ready |
| Watchdog | When oversight infrastructure in place |
| CIVIS-CYBER full UI | When training capacity allows |

---

### Minimal Deployment Checklist

| Step | Action | Owner |
|------|--------|-------|
| 1 | Legal review of 3 components | Counsel |
| 2 | IT security approval | IT |
| 3 | Install hash registry client | IT |
| 4 | Train 2-3 investigators | Unit lead |
| 5 | Run first case (supervised) | Pilot team |
| 6 | Debrief and document lessons | All |

---

### Time-to-Value Estimates

| Milestone | Timeline |
|-----------|----------|
| First hash query | Day 1 |
| First evidence package created | Week 1 |
| First pre-flight validation | Week 2 |
| First court export | Week 3-4 |
| Pilot evaluation | Week 6-8 |

---

### Scaling Up

After successful minimal deployment:

1. **Month 2-3:** Add CIVIS-CYBER full interface
2. **Month 3-4:** Integrate Victim Engine
3. **Month 4-6:** Connect to GJEP for cross-border
4. **Month 6+:** Implement Watchdog oversight

**Start small. Prove value. Expand with confidence.**

---

## Appendices

### Appendix A: Model Legal Opinion Template

A template legal opinion for agency counsel reviewing deployment.

### Appendix B: Court Testimony Guide

Guidance for officers testifying about system-generated evidence.

### Appendix C: Public Communications Template

Template press releases and FAQ for public announcement.

### Appendix D: Union/Association Briefing Materials

Materials for officer association consultation.

---

*Law Enforcement Deployment Guide v1.0 — CHILD GUARDIANS*
