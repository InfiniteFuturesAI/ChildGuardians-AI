# CIVIS-CYBER Specification

> **Civic Investigation & Victim Intelligence Suite**  
> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

CIVIS-CYBER is the **law enforcement and social services investigator interface** for the CHILD GUARDIANS ecosystem. It provides:

- Structured intake for cybercrime reports
- Evidence correlation across cases
- Victim harm assessment
- Court-ready evidence packaging
- Platform and financial institution liaison
- Investigator AI assistance (advisor, not actor)

> **"Reduce burden on investigators. Raise evidence quality. Protect victims."**

---

## 2. Who Uses This

### 2.1 Primary Users

| User Type | Use Case |
|-----------|----------|
| **Police Cybercrime Units** | Case investigation, evidence handling |
| **Financial Crimes Teams** | Fraud correlation, payment tracing |
| **Social Services Investigators** | Victim assessment, risk prioritization |
| **Victim Support Case Workers** | Harm documentation, service coordination |
| **Crown Prosecutors / DAs** | Read-only evidence review |

### 2.2 Access Tiers

| Tier | Access Level | Can Do |
|------|--------------|--------|
| **Officer** | Case-specific | View assigned cases, add evidence |
| **Analyst** | Unit-wide | Cross-case correlation, pattern analysis |
| **Supervisor** | Unit-wide + audit | Review all cases, approve exports |
| **Administrator** | System-wide | Configuration, access management |
| **Prosecutor** | Read-only | View completed evidence packages |

---

## 3. Module Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CIVIS-CYBER                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Intake    │ │  Analysis   │ │   Victim    │           │
│  │  & Triage   │ │  & Pattern  │ │    Harm     │           │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
│         │               │               │                   │
│         └───────────────┼───────────────┘                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Evidence Management Core                │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Evidence   │ │  Platform   │ │ Investigator│           │
│  │  Packaging  │ │   Liaison   │ │     AI      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Module 1: Intake & Triage

### 4.1 Problem Solved

Front-line officers and social workers receive raw, chaotic inputs:
- Screenshots
- Email forwards
- Chat logs
- URLs
- Victim narratives

They don't know what matters or how to structure it.

### 4.2 Solution

Guided intake that converts chaos into structured case data.

### 4.3 Features

| Feature | Description |
|---------|-------------|
| **Guided Upload** | Step-by-step evidence submission |
| **Metadata Extraction** | Automatic timestamp, domain, platform detection |
| **Victim Narrative Capture** | Plain language, trauma-aware prompts |
| **Auto-Classification** | Scam / impersonation / coercion / extortion / fraud / CSAM |
| **Confidence Scoring** | Likelihood of criminal activity (0-100%) |
| **Duplicate Detection** | Link to existing cases with same indicators |

### 4.4 Output

**Case Packet v1** — a clean, standardized starting point containing:
- All uploaded evidence (hashed, timestamped)
- Extracted metadata
- Preliminary classification
- Recommended next steps

---

## 5. Module 2: Analysis & Pattern Intelligence

### 5.1 Problem Solved

Each case looks isolated. Criminal networks stay invisible.

### 5.2 Solution

Passive intelligence correlation — no probing, no hacking.

### 5.3 Features

| Feature | Description |
|---------|-------------|
| **Domain Lineage** | Historical ownership, DNS changes |
| **URL Expansion** | Resolve shortened links (historical) |
| **Language Fingerprinting** | Template reuse detection across cases |
| **Timing Patterns** | Campaign correlation by date/time |
| **Platform Clustering** | Same actor across platforms |
| **Infrastructure Mapping** | Shared hosting, payment processors |

### 5.4 Key Rule

> **Everything here is observational, not interactive.**

No engagement with suspects. No active probing.

### 5.5 Output

| Output | Description |
|--------|-------------|
| Campaign Cluster ID | "Likely same campaign as cases X, Y, Z" |
| Prior Report Count | "Seen in 47 prior reports" |
| Infrastructure Confidence | Shared infra probability (0-100%) |
| Pattern Timeline | When this campaign started, peaked, shifted |

---

## 6. Module 3: Victim Harm & Risk Index

### 6.1 Problem Solved

Most tools focus on suspects. This module focuses on **victims**.

### 6.2 Why This Matters

Social services need to prioritize people, not just cases.

### 6.3 Features

| Feature | Description |
|---------|-------------|
| **Financial Harm Estimate** | Actual + projected loss |
| **Psychological Risk Flags** | Coercion, shame pressure, urgency framing |
| **Vulnerability Indicators** | New business, elderly, disability, language barriers |
| **Escalation Risk** | Sextortion → self-harm risk assessment |
| **Re-victimization Tracking** | Same victim targeted multiple times |

### 6.4 Risk Categories

| Category | Description | Priority |
|----------|-------------|----------|
| **CRITICAL** | Immediate safety concern | Instant escalation |
| **HIGH** | Significant harm, vulnerable victim | Same-day review |
| **MEDIUM** | Substantial loss, stable victim | Standard timeline |
| **LOW** | Minor harm, low vulnerability | Queue-based |

### 6.5 Output

**Victim Risk Profile** — used for:
- Case prioritization
- Resource allocation
- Victim services referral
- Wellness check triggers

---

## 7. Module 4: Evidence Packaging & Chain of Custody

### 7.1 Problem Solved

Good cases die in court because evidence handling is sloppy.

### 7.2 Solution

Automated, boring, court-safe rigor.

### 7.3 Features

| Feature | Description |
|---------|-------------|
| **Immutable Hashes** | SHA-256 + SHA3-512 at intake |
| **Timeline Reconstruction** | Chronological evidence ordering |
| **Source Provenance** | Where each piece came from |
| **Officer Annotations** | Locked + logged notes |
| **Correction Records** | Append-only fixes, never alterations |

### 7.4 Export Formats

| Format | Recipient |
|--------|-----------|
| **Crown/Prosecutor Bundle** | Legal proceedings |
| **Platform Takedown Request** | Meta, Google, Microsoft, etc. |
| **Financial Institution Referral** | Banks, payment processors |
| **Victim Services Package** | Support agencies |
| **GJEP Anchor Package** | Global evidence preservation |

### 7.5 Chain of Custody

Every action logged:
- Who accessed
- When
- What action
- Cryptographic signature

**Defense attorneys cannot attack what they cannot find gaps in.**

---

## 8. Module 5: Platform & Financial Liaison

### 8.1 Problem Solved

Officers waste hours writing takedown requests that get rejected.

### 8.2 Solution

Pre-formatted, evidence-backed notices that actually work.

### 8.3 Features

| Feature | Description |
|---------|-------------|
| **Platform Templates** | Meta, Google, Microsoft, TikTok, etc. |
| **Telecom Templates** | Phone number, SMS, VOIP providers |
| **Financial Templates** | Banks, payment processors, crypto exchanges |
| **Jurisdiction-Aware Language** | Local legal requirements embedded |
| **Confidence Weighting** | Higher confidence = higher priority |
| **Follow-Up Tracking** | Response monitoring, escalation triggers |

### 8.4 Template Example

```
TAKEDOWN REQUEST — [Platform Name]
────────────────────────────────────────

Case Reference: [CIVIS-CYBER Case ID]
Requesting Authority: [Agency Name]
Jurisdiction: [Country + Legal Basis]

Evidence Summary:
• Material Type: [CSAM / Fraud / Impersonation]
• Hash: [SHA-256]
• URL: [Location]
• First Seen: [Timestamp]
• Confidence: [HIGH / MEDIUM / LOW]

Legal Basis: [Statute / Treaty / MLAT Reference]

Action Requested: [Removal / Account Suspension / Data Preservation]

Response Required By: [Date]

Attached: Evidence Object [ID]
```

---

## 9. Module 6: Investigator AI

### 9.1 Core Principle

> **The AI is an advisor, not an actor.**

### 9.2 What AI CAN Do

| Capability | Description |
|------------|-------------|
| **Summarize Cases** | Condense complex evidence into brief |
| **Flag Missing Evidence** | "Chain of custody gap detected" |
| **Suggest Next Steps** | Lawful investigative actions |
| **Highlight Similar Cases** | Pattern matching to closed cases |
| **Explain Classifications** | "This looks criminal because..." |
| **Translate Technical Details** | Make evidence court-understandable |

### 9.3 What AI CANNOT Do

| Prohibition | Reason |
|-------------|--------|
| ❌ Message suspects | No autonomous interaction |
| ❌ Generate threats | No intimidation |
| ❌ Automate reporting floods | No vigilantism |
| ❌ Make arrest decisions | Human judgment required |
| ❌ Assign guilt | Due process protection |
| ❌ Access evidence outside permissions | Jurisdiction enforcement |

### 9.4 AI Explainability

Every AI recommendation includes:
- Reasoning chain
- Evidence basis
- Confidence level
- Alternative interpretations

**No "black box" conclusions.**

---

## 10. Governance & Safety

### 10.1 Access Control

| Control | Implementation |
|---------|----------------|
| Role-based access | Only see what your role permits |
| Jurisdiction locks | Only access cases in your jurisdiction |
| Audit logging | Every action recorded |
| Session limits | Automatic timeout |
| Exposure limits | Maximum daily evidence reviews |

### 10.2 Investigator Safety

| Protection | Implementation |
|------------|----------------|
| AI pre-filter | No direct exposure to traumatic content |
| Exposure counters | Daily/weekly limits |
| Mandatory breaks | Forced pause after threshold |
| Wellness integration | Automatic support referrals |
| Rotation alerts | "Time for assignment change" |

### 10.3 Abuse Prevention

| Risk | Mitigation |
|------|------------|
| Fishing expeditions | Access requires case linkage |
| Evidence tampering | Append-only, cryptographic integrity |
| Unauthorized access | Multi-factor + role verification |
| Data exfiltration | Export logging + approval workflow |

---

## 11. Integration Points

### 11.1 Inbound

| Source | Data Received |
|--------|---------------|
| Industrial Magnet | Hash matches from dark web |
| Tip Lines | Public submissions |
| Partner Agencies | Cross-border referrals |
| Financial Institutions | Suspicious activity reports |

### 11.2 Outbound

| Destination | Data Sent |
|-------------|-----------|
| GJEP | Anchored evidence objects |
| Defense Attorney Simulator | Pre-export validation |
| Prosecutor Systems | Court-ready packages |
| Victim Services | Risk profiles (metadata only) |
| Platform Abuse Teams | Takedown requests |

---

## 12. Workflow Example

### 12.1 Scam Report Flow

```
1. Victim files complaint
         │
         ▼
2. Front-line officer opens CIVIS-CYBER
         │
         ▼
3. Guided intake collects:
   • Screenshots
   • Messages
   • URLs
   • Victim narrative
         │
         ▼
4. System auto-classifies:
   • Type: Impersonation scam
   • Confidence: 87%
   • Similar campaigns: 3 found
         │
         ▼
5. Victim Harm Index calculated:
   • Financial loss: $2,400
   • Vulnerability: Elderly
   • Risk level: HIGH
         │
         ▼
6. Investigator AI suggests:
   • "Request data preservation from [platform]"
   • "Similar to Campaign Cluster #447"
   • "Consider financial freeze request"
         │
         ▼
7. Officer generates platform notice
         │
         ▼
8. Evidence packaged, anchored to GJEP
         │
         ▼
9. Case assigned for investigation
```

---

## 13. Why Officers Will Use This

| Benefit | How Delivered |
|---------|---------------|
| **Less paperwork** | Templates + auto-fill |
| **Cleaner evidence** | Born court-safe |
| **Fewer dead ends** | Pattern correlation |
| **Better cooperation** | Standard formats accepted by platforms |
| **Career protection** | Documented process |
| **Reduced trauma** | AI pre-filter |

---

## 14. Why Victims Benefit

| Benefit | How Delivered |
|---------|---------------|
| **Faster response** | Prioritization by harm |
| **Better outcomes** | Evidence survives court |
| **Trauma-aware** | Intake designed for sensitivity |
| **Not forgotten** | GJEP prevents case burial |
| **Services connected** | Automatic referrals |

---

## 15. Summary

CIVIS-CYBER provides:

| Capability | Purpose |
|------------|---------|
| **Structured intake** | Chaos → order |
| **Pattern analysis** | Isolated → connected |
| **Victim prioritization** | Cases → people |
| **Evidence packaging** | Raw → court-ready |
| **Platform liaison** | Requests → results |
| **AI assistance** | Overloaded → supported |

> **"Expert witness assistant, not enforcer."**

---

*CIVIS-CYBER Specification v1.0 — CHILD GUARDIANS*
