# Dark Web Industrial Magnet Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Industrial Magnet is a **passive, lawful, evidence-preserving** dark web monitoring system designed to:

- Detect resurfacing of known CSAM material
- Track re-victimization events
- Provide court-admissible evidence objects
- Route intelligence to appropriate jurisdictions

This system **never interacts** with criminals. It is a gravitational field that makes reappearance visible.

---

## 2. Core Principle

> **"Criminals hide by scattering. This system wins by making reappearance visible forever."**

---

## 3. Access Model (Non-Negotiable)

### 3.1 Hard Rules

| Rule | Rationale |
|------|-----------|
| ✅ Read-only Tor access | No participation in criminal activity |
| ✅ No authenticated accounts | No impersonation or deception |
| ✅ No marketplace logins | No conspiracy liability |
| ✅ No content requests that alter state | No entrapment risk |
| ✅ No downloads of illegal material | Content never stored |
| ✅ Zero interaction | System is observer, never participant |

### 3.2 Legal Preservation

This model preserves:
- **Legality** — No criminal acts by the system
- **Admissibility** — Evidence is untainted
- **Operator safety** — No exposure to prosecution
- **Chain of custody** — Clear provenance

---

## 4. Collection Strategy (Needle, Not Hay)

### 4.1 What the System Collects

| Input Type | Source | Purpose |
|------------|--------|---------|
| Known CSAM hash lists | NCMEC, IWF, Interpol | Match detection |
| Known abuse forum structures | Law enforcement intelligence | Pattern recognition |
| Known paste/dump formats | Historical analysis | Format matching |
| Known re-hosting patterns | Takedown records | Mirror detection |
| Known takedown-evading mirrors | Prior enforcement | Resurfacing tracking |

### 4.2 What the System Outputs

| Output | Description |
|--------|-------------|
| Hash hits | Exact match to known-CSAM database |
| Near-duplicate hits | Perceptual hash similarity above threshold |
| Reappearance events | Material seen again after prior takedown |
| Evidence objects | Court-ready packages for GJEP |

### 4.3 What the System Does NOT Collect

| Excluded | Reason |
|----------|--------|
| ❌ Bulk crawl data | Legal exposure, useless noise |
| ❌ User account information | Deanonymization prohibited |
| ❌ Forum posts/conversations | Not needed for hash matching |
| ❌ Metadata beyond routing | Minimization principle |

---

## 5. Content Handling Rules (Critical)

### 5.1 Absolute Prohibitions

| Rule | Enforcement |
|------|-------------|
| ❌ Never store raw CSAM | Content discarded after hashing |
| ❌ Never render images to humans | AI pre-filter only |
| ❌ Never train models on illegal content | Prohibited by design |
| ❌ Never retain payload | Only hashes + metadata kept |

### 5.2 Permitted Operations

| Operation | Implementation |
|-----------|----------------|
| ✅ Compute cryptographic hashes in memory | SHA256, SHA3-512 |
| ✅ Compute perceptual hashes | PhotoDNA-style, PDQ |
| ✅ Store only hashes + metadata | Evidence objects |
| ✅ Discard payload immediately | RAM-only processing |

### 5.3 Core Insight

> **Evidence is the fingerprint, not the body.**

This is what makes the system deployable, legal, and ethical.

---

## 6. Hash-First Pipeline

### 6.1 Pipeline Architecture

```
┌─────────────────┐
│   Tor Sources   │
│ (Passive Crawl) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ephemeral Fetch │
│  (RAM Only)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hash Extraction │
│ SHA256 + PDQ    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Known-CSAM Match?           │
├─────────────────────────────┤
│ Compare against:            │
│ • NCMEC hash database       │
│ • IWF hash database         │
│ • Interpol ICSE database    │
│ • National LE databases     │
└────────┬────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────┐  ┌───────────────────┐
│ No   │  │ Yes               │
│ Match│  │                   │
└──┬───┘  └─────────┬─────────┘
   │                │
   ▼                ▼
┌──────┐  ┌───────────────────┐
│DISCARD│  │ Create Evidence   │
│(No    │  │ Object            │
│Record)│  └─────────┬─────────┘
└───────┘            │
                     ▼
         ┌───────────────────┐
         │ Global Justice    │
         │ Evidence Plane    │
         │ (GJEP)            │
         └─────────┬─────────┘
                   │
                   ▼
         ┌───────────────────┐
         │ Jurisdiction      │
         │ Routing           │
         └───────────────────┘
```

### 6.2 Key Properties

| Property | Implementation |
|----------|----------------|
| **No match = no record** | Prevents surveillance creep |
| **Memory-only processing** | No content persistence |
| **Hash-first matching** | Content never analyzed by humans |
| **Immediate discard** | Payload gone after hash extraction |

---

## 7. Dark Web Pattern Intelligence

### 7.1 Allowed AI Tasks

AI is used for structure and behavior detection, NOT content judgment.

| Task | Purpose |
|------|---------|
| Forum structure similarity | Detect related/mirror forums |
| Re-posting cadence detection | Identify organized distribution |
| Mirror propagation tracking | Track content migration after takedown |
| Filename mutation patterns | Detect evasion techniques |
| Hosting churn timelines | Predict infrastructure changes |

### 7.2 Questions AI Answers

| Allowed Questions | Prohibited Questions |
|-------------------|----------------------|
| "Where does this material keep resurfacing?" | "Who is guilty?" |
| "What hosting patterns exist?" | "Who should be investigated?" |
| "How quickly do mirrors appear after takedown?" | "What is this person doing?" |
| "What filename mutations are used?" | "Who uploaded this?" |

### 7.3 AI Boundaries

| Boundary | Enforcement |
|----------|-------------|
| No suspect identification | System outputs evidence, not accusations |
| No content analysis | Only metadata patterns |
| No predictive policing | Only historical pattern recognition |
| No autonomous action | All outputs require human decision |

---

## 8. Victim Re-Identification (Highest Priority)

### 8.1 When Hash Matches Known Victim Material

```python
def on_victim_material_match(evidence: EvidenceObject, victim_id: str):
    # 1. Increment re-victimization counter
    evidence.victim_data.revictimization_count += 1
    
    # 2. Update last-seen timestamp
    evidence.victim_data.last_resurfaced_at = now_utc()
    
    # 3. Route alerts
    alert_victim_country_le(evidence, victim_id)
    alert_victim_services(evidence, victim_id)
    
    # 4. Trigger priority takedown
    if evidence.victim_data.victim_status == "RESCUED":
        evidence.victim_data.priority_takedown = True
        escalate_takedown(evidence)
```

### 8.2 Victim Protection Outputs

| Output | Recipient | Content |
|--------|-----------|---------|
| LE Alert | Victim's national LE | Evidence object + urgency flag |
| Victim Services Alert | Victim services authority | Resurfacing notification |
| Takedown Request | Hosting provider | Hash + hosting location |
| Re-victimization Report | Case management | Updated counter |

### 8.3 Why This Matters

> **This is the human reason the system exists.**

Every resurfacing is a new violation of the victim. The system makes these events visible immediately, not months later.

---

## 9. Jurisdiction Routing (Automated, Lawful)

### 9.1 Routing Logic

For each evidence object:

```python
def route_evidence(evidence: EvidenceObject):
    routing = {
        "hosting_country": identify_hosting_country(evidence),
        "victim_country": evidence.victim_data.victim_country,
        "transit_countries": identify_transit_infrastructure(evidence),
        "treaty_coverage": calculate_treaty_coverage(evidence)
    }
    
    # Determine who can act
    can_act = []
    for country in [routing["hosting_country"], routing["victim_country"]]:
        if has_jurisdiction(country, evidence):
            can_act.append(country)
    
    # Determine who must not act
    must_not = []
    for country in all_countries():
        if not has_jurisdiction(country, evidence):
            must_not.append(country)
    
    evidence.jurisdiction.permission_map = {
        "can_view_metadata": can_act + coordinating_bodies(),
        "can_view_hashes": can_act,
        "can_export_evidence": can_act,
        "can_initiate_prosecution": can_act,
        "must_not_access": must_not
    }
```

### 9.2 Routing Rules

| Scenario | Routing |
|----------|---------|
| Hosting and victim in same country | Single country gets full access |
| Hosting ≠ victim country | Both countries get access; treaty may be required |
| Transit infrastructure involved | Transit countries get metadata only |
| Unknown victim country | Hosting country + Interpol coordination |

### 9.3 Metadata-Only Forwarding

| What is Forwarded | What is NOT Forwarded |
|-------------------|----------------------|
| Hash values | Actual content |
| Timestamp | Raw URLs |
| Hosting location | User information |
| Treaty requirements | Investigation details |
| Urgency flags | Unrelated case data |

---

## 10. Operator Safety (Often Ignored, Must Be Designed)

### 10.1 Mandatory Protections

| Protection | Implementation |
|------------|----------------|
| No visual exposure by default | AI pre-filter before any human review |
| Tiered access clearance | Role-based access with escalation |
| Automatic exposure limits | Daily/weekly limits on sensitive access |
| Mandatory mental-health rotation | Forced rotation after threshold |
| Wellness check integration | Automatic referral triggers |

### 10.2 Exposure Control

```python
class OperatorSafetyController:
    
    MAX_DAILY_EXPOSURE = 20  # metadata reviews
    MAX_WEEKLY_EXPOSURE = 80
    MANDATORY_BREAK_AFTER = 4  # consecutive reviews
    ROTATION_THRESHOLD_MONTHS = 6
    
    def can_access(self, operator: Operator, evidence: EvidenceObject) -> bool:
        if operator.daily_exposure >= self.MAX_DAILY_EXPOSURE:
            return False, "Daily limit reached"
        
        if operator.weekly_exposure >= self.MAX_WEEKLY_EXPOSURE:
            return False, "Weekly limit reached"
        
        if operator.consecutive_reviews >= self.MANDATORY_BREAK_AFTER:
            return False, "Break required"
        
        if operator.months_on_duty >= self.ROTATION_THRESHOLD_MONTHS:
            return False, "Rotation required"
        
        return True, "Access permitted"
```

### 10.3 Why This Matters

This is both **ethical** and **operationally necessary**:
- Prevents burnout
- Reduces secondary trauma
- Maintains operational effectiveness
- Complies with duty of care

---

## 11. Audit & Abuse Prevention

### 11.1 Logging Requirements

Every action is logged:

| Field | Purpose |
|-------|---------|
| What was accessed | Evidence ID |
| When | UTC timestamp |
| By which system | System component ID |
| For what purpose | Action justification |
| Session context | IP hash, session ID |

### 11.2 Watchdog Triggers

| Condition | Trigger |
|-----------|---------|
| Evidence stalls | No action for >90 days on high-severity case |
| Access spikes | Unusual access pattern for operator |
| Jurisdiction routing halts | Evidence not routed within SLA |
| High-severity inactive | Priority case without recent activity |
| Repeated access without action | Potential abuse indicator |

### 11.3 Purpose

> **This prevents "quiet burial."**

Evidence cannot be ignored, suppressed, or buried without the system surfacing the inaction.

---

## 12. What This System NEVER Does

### 12.1 Explicit Prohibitions

| Prohibition | Rationale |
|-------------|-----------|
| ❌ No deanonymization | Civil liberties; creates liability |
| ❌ No hacking | Criminal act; poisons evidence |
| ❌ No sting operations | Requires human judgment; entrapment risk |
| ❌ No suspect profiling | Civil liberties; not system role |
| ❌ No autonomous reporting without thresholds | Prevents false positives |
| ❌ No expansion beyond CSAM | Scope creep destroys public trust |
| ❌ No content storage | Only hashes and metadata |
| ❌ No human visual review of content | AI pre-filter only |

### 12.2 Why These Prohibitions Exist

> **These keep public trust intact.**

The system is powerful. These boundaries ensure power is not abused.

---

## 13. Integration with CHILD GUARDIANS Ecosystem

### 13.1 System Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    CHILD GUARDIANS ECOSYSTEM                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐     ┌──────────────────┐     ┌─────────────┐  │
│  │   ECP   │────▶│ Industrial Magnet│────▶│ Hash Registry│  │
│  │(Stops   │     │ (Finds           │     │ (Confirms    │  │
│  │ Gen)    │     │  Resurfacing)    │     │  Illegality) │  │
│  └─────────┘     └────────┬─────────┘     └──────┬──────┘  │
│                           │                       │         │
│                           ▼                       │         │
│  ┌─────────────────────────────────────────────────┐       │
│  │              Victim Engine                      │       │
│  │           (Protects Children)                   │◀──────┘ │
│  └─────────────────────┬───────────────────────────┘        │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────┐       │
│  │              CIVIS-CYBER                        │       │
│  │        (Investigator Interface)                 │       │
│  └─────────────────────┬───────────────────────────┘        │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────┐       │
│  │     GJEP (Global Justice Evidence Plane)        │       │
│  │          (Border-Proof Evidence)                │       │
│  └─────────────────────┬───────────────────────────┘        │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────┐       │
│  │              Watchdog                           │       │
│  │         (Prevents Suppression)                  │       │
│  └─────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 13.2 Data Flow

| From | To | Data |
|------|------|------|
| Industrial Magnet | GJEP | Evidence objects (hash matches) |
| Industrial Magnet | Victim Engine | Resurfacing alerts |
| Industrial Magnet | Hash Registry | New hash verifications |
| GJEP | CIVIS-CYBER | Jurisdiction-filtered evidence |
| Watchdog | All Systems | Inactivity alerts |

---

## 14. Deployment Considerations

### 14.1 Infrastructure Requirements

| Component | Requirement |
|-----------|-------------|
| Tor Access | Read-only, ephemeral connections |
| Hash Computation | High-throughput, RAM-only |
| Database | Known-CSAM hash databases (authorized access) |
| Storage | Evidence objects only (no content) |
| Network | Secure, isolated, monitored |

### 14.2 Operational Security

| Measure | Purpose |
|---------|---------|
| Air-gapped processing | Prevent content exfiltration |
| Multi-party key management | Prevent single-point compromise |
| Audit log integrity | Immutable, cryptographically chained |
| Access tiering | Role-based, need-to-know |

---

## 15. Summary

The Industrial Magnet is:

- **Passive** — Never interacts
- **Lawful** — Never violates law
- **Evidentiary** — Creates court-ready objects
- **Protective** — Prioritizes victim safety
- **Accountable** — Every action logged
- **Bounded** — Explicit prohibitions enforced

> **You're not building a crawler. You're building a lawful gravitational field.**

---

*Industrial Magnet Specification v1.0 — CHILD GUARDIANS*
