# Global Justice Evidence Plane (GJEP) Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Global Justice Evidence Plane is the **jurisdiction-agnostic evidence preservation layer** that ensures:

- Evidence cannot die when inconvenient
- Borders don't kill prosecutions
- Truth survives politics, power, and time

> **"Law enforcement needs jurisdiction to act. It does not need jurisdiction to preserve truth."**

---

## 2. Core Problem Solved

Criminal networks deliberately exploit jurisdictional fragmentation:

| Tactic | Effect |
|--------|--------|
| Host in Country A | Country B can't seize servers |
| Route through Country B | Logs split across jurisdictions |
| Store data in Country C | Data sovereignty blocks access |
| Process payments in Country D | Financial trail fragmented |
| Target victims in Country E | No single authority has full picture |

**GJEP defeats this by separating evidence existence from enforcement authority.**

---

## 3. Design Principle

```
┌─────────────────────────────────────────────────────────────┐
│                   SEPARATION OF CONCERNS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRUTH PRESERVATION          ENFORCEMENT ACTION             │
│  (Borderless, neutral)       (Local, lawful)                │
│                                                             │
│  • Evidence exists           • Arrests happen               │
│  • Hashes stored             • Prosecutions proceed         │
│  • Timestamps sealed         • Sentences rendered           │
│  • Chain preserved           • Victims protected            │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  GJEP handles this           National authorities do this   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. What GJEP Stores

### 4.1 Stored (Evidence Fingerprints)

| Data Type | Purpose |
|-----------|---------|
| Cryptographic hashes | Exact material identification |
| Perceptual hashes | Near-duplicate detection |
| Timestamps (UTC, signed) | When material existed |
| Source metadata | Where material was found |
| Transformation signatures | Resized, cropped, re-encoded variants |
| Chain of custody events | Who accessed, when, why |
| Victim reappearance indicators | Re-victimization tracking |
| Jurisdiction mapping | Who can act |

### 4.2 NOT Stored (Critical)

| Data Type | Reason |
|-----------|--------|
| ❌ Raw CSAM imagery | Never retained |
| ❌ Personal identifying information | Privacy protection |
| ❌ Investigative hypotheses | Not evidence |
| ❌ Suspect profiles | Civil liberties |
| ❌ Private communications | Warrant required |

**GJEP stores proof, not content.**

---

## 5. Evidence Object in GJEP

Each evidence object anchored in GJEP contains:

```json
{
  "gjep_anchor": {
    "anchor_id": "UUID v7",
    "anchored_at": "ISO 8601 UTC",
    "evidence_hash": "SHA3-512 of evidence object",
    
    "multi_party_escrow": {
      "law_enforcement_anchor": "signature",
      "judicial_anchor": "signature",
      "watchdog_anchor": "signature"
    },
    
    "jurisdiction_map": {
      "hosting_country": "ISO 3166-1 alpha-2",
      "victim_country": "ISO 3166-1 alpha-2 or UNKNOWN",
      "transit_countries": ["array"],
      "can_act": ["array of authority IDs"],
      "must_not_act": ["array of authority IDs"],
      "treaty_required": ["array of treaty references"]
    },
    
    "access_log": [
      {
        "accessor": "authority ID",
        "timestamp": "ISO 8601 UTC",
        "action": "VIEW | EXPORT | QUERY",
        "signature": "Ed25519"
      }
    ],
    
    "status": {
      "active_investigation": "boolean",
      "prosecution_initiated": "boolean",
      "sealed": "boolean",
      "seal_justification": "string or null",
      "inactivity_days": "integer"
    }
  }
}
```

---

## 6. Multi-Party Escrow (No Single Point of Failure)

### 6.1 Three-Party Anchor

Every evidence object is simultaneously anchored by:

| Party | Role |
|-------|------|
| **Law Enforcement Vault** | Operational access |
| **Judicial Escrow** | Legal oversight |
| **Watchdog Ledger** | Independent verification |

**Deletion requires all three parties. None can unilaterally erase.**

### 6.2 Access Requirements

| Action | Requirements |
|--------|--------------|
| View metadata | Single-party authorization |
| Export evidence | Two-party authorization |
| Seal evidence | Judicial authorization + justification |
| Delete evidence | Impossible (only archival after retention) |

---

## 7. Evidence Preservation ≠ Prosecution Mandate

### The Critical Distinction

> **Evidence immortality does NOT mean mandatory prosecution.**

This section exists because prosecutors and justice ministries may fear being forced to pursue every preserved case. That fear is unfounded.

### What Evidence Preservation Means

| Preserved Evidence Guarantees | Does NOT Guarantee |
|------------------------------|--------------------|
| Evidence cannot be destroyed | Prosecution will occur |
| Chain of custody survives | Charges will be filed |
| Future access is possible | Conviction will result |
| Truth is not lost to time | Resources will be allocated |

### Prosecutorial Discretion Is Preserved

Prosecutors retain full discretion over:

| Decision | Authority |
|----------|----------|
| Whether to file charges | Prosecutor |
| Which charges to file | Prosecutor |
| Whether to plea bargain | Prosecutor |
| Whether to dismiss | Prosecutor (with justification) |
| Resource allocation | Prosecutor's office |

### Legitimate Reasons for Non-Prosecution

The following are **valid, documented reasons** to not prosecute preserved evidence:

| Reason | Example |
|--------|---------|
| Insufficient evidence for conviction | Hash match alone without corroboration |
| Jurisdictional limitations | Foreign suspect, no extradition |
| Resource constraints | Higher-priority cases pending |
| Victim considerations | Victim requests no prosecution |
| Statute of limitations | Expired (though evidence remains) |
| Deceased suspect | No defendant to prosecute |
| Cooperation agreements | Suspect cooperating on larger case |

### What IS Required

| Requirement | Why |
|-------------|-----|
| **Document the decision** | Accountability |
| **Log the justification** | Transparency |
| **Seal if appropriate** | Not delete |

### What the Watchdog Monitors

The Watchdog does NOT force prosecution. It surfaces patterns:

| Pattern | Watchdog Action |
|---------|----------------|
| Single case not prosecuted | No action (discretion respected) |
| Category of cases consistently ignored | Aggregate report published |
| Cases stalled beyond threshold | Inactivity alert generated |
| Evidence accessed then buried | Suppression flag raised |

**The Watchdog asks questions. It does not give orders.**

### Summary

- Evidence persistence ≠ prosecution requirement
- Discretion is preserved
- Accountability is added
- Suppression is prevented
- Legitimate non-prosecution is documented, not forbidden

**The goal is that no case is buried because it's inconvenient — not that every case is prosecuted regardless of merit.**

---

## 7. Jurisdiction Routing

### 7.1 Automatic Mapping

When evidence enters GJEP:

```python
def map_jurisdiction(evidence: EvidenceObject) -> JurisdictionMap:
    return {
        "hosting_country": identify_hosting(evidence.source),
        "victim_country": evidence.victim_data.country or "UNKNOWN",
        "transit_countries": identify_transit(evidence.source),
        
        "can_act": determine_authorized_authorities(
            hosting=hosting_country,
            victim=victim_country,
            treaties=active_treaties()
        ),
        
        "must_not_act": determine_prohibited_authorities(
            all_authorities() - can_act
        ),
        
        "treaty_required": determine_treaty_requirements(
            requester=None,  # Computed per-request
            evidence=evidence
        )
    }
```

### 7.2 What Each Authority Receives

| Authority Type | Access Level |
|----------------|--------------|
| Hosting country LE | Full evidence access |
| Victim country LE | Full evidence access |
| Transit country LE | Metadata only |
| Coordinating body (Interpol) | Routing metadata only |
| Unauthorized country | Nothing |

---

## 8. Evidence Cannot Die

### 8.1 Immortality Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| Cannot be deleted | Append-only storage; deletion impossible |
| Cannot be altered | Cryptographic hashes verify integrity |
| Cannot be hidden | Multi-party escrow; no single controller |
| Cannot stall silently | Inactivity triggers watchdog |
| Cannot be sealed without record | Sealing requires justification + audit |

### 8.2 What Happens When Someone Tries

| Attempt | System Response |
|---------|-----------------|
| Delete evidence | Operation rejected; attempt logged |
| Alter evidence | Integrity check fails; tampering flagged |
| Hide evidence | Multi-party escrow prevents concealment |
| Ignore evidence | Inactivity clock triggers escalation |
| Seal without justification | Sealing rejected; attempt logged |

---

## 9. Treaty Activation Keys

### 9.1 Traditional Model (Broken)

```
Evidence collected → Treaty requested → Months pass → Evidence shared
                                              ↓
                                        Evidence lost / expired
```

### 9.2 GJEP Model (Fixed)

```
Evidence collected → Evidence anchored → Evidence preserved
                                              ↓
                          Treaty requested → Evidence unlocked
                                              ↓
                          Case resumes (not restarts)
```

**Treaties unlock preserved evidence. They don't start the clock.**

### 9.3 Treaty-Aware Access

```python
def check_treaty_access(requester: Authority, evidence: EvidenceObject) -> AccessResult:
    if requester in evidence.jurisdiction.can_act:
        return AccessResult.GRANTED
    
    if evidence.jurisdiction.treaty_required:
        pending = get_treaty_requests(requester, evidence)
        if pending and pending.status == "APPROVED":
            return AccessResult.GRANTED
        elif pending and pending.status == "PENDING":
            return AccessResult.PENDING_TREATY
        else:
            return AccessResult.TREATY_REQUIRED
    
    return AccessResult.DENIED
```

---

## 10. International Coordination (Not Control)

### 10.1 Role of International Bodies

| Body | Role | Cannot Do |
|------|------|-----------|
| **Interpol** | Route evidence, coordinate requests | Command national LE |
| **Europol** | Coordinate EU-wide, analyze patterns | Override member states |
| **NCMEC** | Hash database, victim identification | Enforce outside US |

**They are routers and coordinators, not commanders.**

### 10.2 Sovereignty Preserved

- Each nation's laws are encoded in the jurisdiction map
- No country sees evidence it isn't entitled to
- No country is forced to act
- Treaty requirements are enforced, not bypassed

---

## 11. Escalation to International Jurisdiction

### 11.1 When International Courts Can Act

In narrow, treaty-defined circumstances:

| Condition | Escalation Path |
|-----------|-----------------|
| National authority fails to act | Escalation after threshold period |
| Offender hides behind immunity | International jurisdiction triggered |
| Cross-border organized network | Coordinated prosecution |
| State-level protection of offenders | International fallback |

### 11.2 Escalation Is Exception, Not Default

```
National enforcement (default)
        │
        ▼
Inactivity detected
        │
        ▼
Escalation warning
        │
        ▼
National authority notified
        │
        ▼
Still inactive?
   ┌────┴────┐
   │         │
   ▼         ▼
 Action   Escalation to
 taken    coordinating body
            │
            ▼
        International
        jurisdiction
        consideration
```

---

## 12. Transparency Without Exposure

### 12.1 Public Transparency Reports

GJEP publishes annual aggregate data:

| Metric | Public? |
|--------|---------|
| Evidence objects anchored | ✅ Count only |
| Jurisdictions participating | ✅ List |
| Average time to first action | ✅ Aggregate |
| Stalled cases flagged | ✅ Count only |
| Takedowns triggered | ✅ Count only |
| Re-victimization events detected | ✅ Count only |

### 12.2 What Is Never Public

| Data | Reason |
|------|--------|
| ❌ Individual case details | Investigation integrity |
| ❌ Victim information | Victim protection |
| ❌ Suspect information | Due process |
| ❌ Specific evidence | Operational security |

---

## 13. Technical Architecture

### 13.1 Storage Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     GJEP STORAGE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Distributed Ledger (Append-Only)           │   │
│  │                                                       │   │
│  │  • Evidence hashes                                    │   │
│  │  • Timestamps                                         │   │
│  │  • Chain of custody                                   │   │
│  │  • Access logs                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │     LE       │ │   Judicial   │ │   Watchdog   │       │
│  │    Vault     │ │    Escrow    │ │    Ledger    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                             │
│  (Three independent anchors; no single point of failure)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 13.2 Access Layer

```
┌─────────────────────────────────────────────────────────────┐
│                     GJEP ACCESS LAYER                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   API Gateway                         │   │
│  │  • Authentication                                     │   │
│  │  • Authorization (jurisdiction check)                 │   │
│  │  • Rate limiting                                      │   │
│  │  • Audit logging                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  National    │ │ International│ │   Watchdog   │       │
│  │  LE Systems  │ │   Bodies     │ │   Systems    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Why Criminals Hate This Model

| Criminal Tactic | Why It Fails |
|-----------------|--------------|
| "Host it offshore" | Evidence preserved anyway |
| "Delay until logs expire" | Evidence already anchored |
| "Exploit jurisdiction gaps" | Gaps mapped, not fatal |
| "Wait out investigators" | Evidence does not age out |
| "Use political protection" | Watchdog flags inactivity |
| "Scatter across borders" | Evidence follows, borders don't block |

**Time stops being their ally. Distance stops being their shield.**

---

## 15. Why This Is Not Mass Surveillance

| What GJEP Does | What GJEP Does NOT Do |
|----------------|----------------------|
| ✅ Preserves known illegal material evidence | ❌ Scan private communications |
| ✅ Tracks reappearance of adjudicated CSAM | ❌ Profile individuals |
| ✅ Routes to lawful authorities | ❌ Assign guilt |
| ✅ Maintains audit trails | ❌ Punish autonomously |
| ✅ Enables lawful prosecution | ❌ Bypass due process |

**This survives constitutional, charter, and human-rights review.**

---

## 16. The Epstein Problem — Solved Structurally

The concern:

> "Evidence dies when inconvenient. High-profile offenders are protected."

GJEP makes this structurally impossible:

| Protection Mechanism | How It Works |
|---------------------|--------------|
| Evidence existence is public (aggregate) | Cannot claim "it doesn't exist" |
| Inactivity is visible | Cannot quietly stall |
| Suppression leaves fingerprints | Cannot hide burial attempts |
| Watchdog reports stalling | Cannot rely on internal cover |
| Multi-party escrow | Cannot unilaterally destroy |

**No conspiracy theories required. Just mechanical accountability.**

---

## 17. Summary

GJEP ensures:

| Guarantee | Mechanism |
|-----------|-----------|
| Evidence cannot be erased | Append-only, multi-party escrow |
| Borders don't kill cases | Jurisdiction-agnostic preservation |
| Time doesn't expire evidence | Permanent anchoring |
| Power doesn't suppress truth | Independent watchdog |
| Treaties unlock, not block | Evidence preserved before request |

> **"Facts don't need extradition."**

---

*Global Justice Evidence Plane Specification v1.0 — CHILD GUARDIANS*
