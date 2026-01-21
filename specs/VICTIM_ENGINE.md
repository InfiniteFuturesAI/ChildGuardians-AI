# Victim Engine Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Victim Engine is the **victim-first intelligence layer** of CHILD GUARDIANS. Its sole purpose is to:

- Track known victims and their material
- Detect re-victimization (material resurfacing)
- Prioritize victim protection over prosecution
- Route alerts to victim services
- Minimize additional trauma

> **"This is the human reason the system exists."**

---

## 2. Core Principle

> **Every resurfacing of victim material is a new violation.**

The Victim Engine makes these events visible immediately — not months or years later.

---

## 3. What the Victim Engine Tracks

### 3.1 Victim Record (Pseudonymized)

```json
{
  "victim_id": "cryptographic pseudonym (not PII)",
  "victim_country": "ISO 3166-1 alpha-2",
  "victim_age_at_abuse": "age category, not exact",
  "victim_status": "UNIDENTIFIED | IDENTIFIED | RESCUED | DECEASED",
  "material_hashes": ["array of known material hashes"],
  "first_known_appearance": "ISO 8601 UTC",
  "last_seen_at": "ISO 8601 UTC",
  "revictimization_count": "integer",
  "priority_level": "STANDARD | HIGH | CRITICAL",
  "services_notified": "boolean",
  "national_authority": "authority ID"
}
```

### 3.2 What Is NOT Stored

| Data | Reason |
|------|--------|
| ❌ Victim name | Privacy protection |
| ❌ Exact age | Minimization |
| ❌ Address/location | Safety |
| ❌ Family details | Privacy |
| ❌ Raw imagery | Never stored |

**Victim identification happens at authorized national authorities — not in CHILD GUARDIANS.**

---

## 4. Re-Victimization Detection

### 4.1 How It Works

```
Industrial Magnet detects hash match
              │
              ▼
Hash checked against victim material registry
              │
         ┌────┴────┐
         │         │
         ▼         ▼
    No match    Match found
    (standard   │
     flow)      ▼
           Victim Engine triggered
              │
              ▼
        ┌─────────────────────────────┐
        │ Re-victimization Protocol   │
        │ • Increment counter         │
        │ • Update last_seen          │
        │ • Elevate priority          │
        │ • Alert victim's authority  │
        │ • Alert victim services     │
        │ • Trigger priority takedown │
        └─────────────────────────────┘
```

### 4.2 Re-Victimization Response

| Action | Timing |
|--------|--------|
| Counter incremented | Immediate |
| Timestamp updated | Immediate |
| National authority alerted | <1 hour |
| Victim services notified | <1 hour |
| Priority takedown triggered | <4 hours |
| GJEP evidence anchored | <1 hour |

---

## 5. Priority Classification

### 5.1 Priority Levels

| Level | Criteria | Response SLA |
|-------|----------|--------------|
| **CRITICAL** | Rescued victim, material resurfacing | <1 hour |
| **HIGH** | Identified victim, active distribution | <4 hours |
| **STANDARD** | Unidentified victim, known material | <24 hours |

### 5.2 Automatic Priority Elevation

Priority automatically increases when:

| Trigger | Elevation |
|---------|-----------|
| Victim identified | STANDARD → HIGH |
| Victim rescued | HIGH → CRITICAL |
| Resurfacing frequency increases | +1 level |
| Multiple platforms involved | +1 level |
| Cross-border distribution detected | +1 level |

---

## 6. Victim Services Integration

### 6.1 Who Receives Alerts

| Recipient | Data Received |
|-----------|---------------|
| **National LE (Victim's Country)** | Full evidence object |
| **Victim Services Authority** | Resurfacing notification (no imagery) |
| **Case Worker (if assigned)** | Priority alert |

### 6.2 What Victim Services Receive

```json
{
  "alert_type": "REVICTIMIZATION",
  "victim_id": "pseudonymized",
  "victim_status": "RESCUED",
  "resurfacing_count": 47,
  "last_seen_platform": "platform category (not URL)",
  "recommended_action": "welfare check",
  "case_worker_id": "assigned worker or null"
}
```

**No imagery. No URLs. No details that re-traumatize.**

### 6.3 Why This Matters

Many victims are:
- Unaware their material is still circulating
- Re-traumatized each time they learn of resurfacing
- Entitled to support and notification

The system balances:
- Right to know
- Protection from harm
- Actionable support

---

## 7. Victim-Centric Safeguards

### 7.1 Mandatory Protections

| Protection | Implementation |
|------------|----------------|
| No visual exposure | All matching is hash-based |
| Minimal data | Only what's needed for protection |
| Controlled notification | Services decide how to inform victim |
| Trauma-aware timing | Notifications batched when appropriate |
| Support integration | Automatic referral paths |

### 7.2 What the System Never Does

| Prohibition | Reason |
|-------------|--------|
| ❌ Contact victims directly | Not system's role |
| ❌ Share victim details with media | Privacy protection |
| ❌ Expose victim identity in reports | Safety |
| ❌ Require victim participation | Voluntary only |
| ❌ Store victim testimony | Separate, protected systems |

---

## 8. Unidentified Victim Tracking

### 8.1 Purpose

Many victims remain unidentified. The system still:

- Tracks material distribution
- Monitors resurfacing patterns
- Preserves evidence for future identification
- Enables victim identification efforts

### 8.2 Unidentified Victim Record

```json
{
  "victim_id": "auto-generated pseudonym",
  "victim_status": "UNIDENTIFIED",
  "material_hashes": ["array"],
  "first_known_appearance": "timestamp",
  "distribution_regions": ["ISO country codes"],
  "identification_attempts": "count",
  "linked_series": "series ID or null"
}
```

### 8.3 Identification Support

When new information emerges:

```
New intelligence received
         │
         ▼
Match against unidentified victims
         │
    ┌────┴────┐
    │         │
    ▼         ▼
No match   Potential match
    │         │
    ▼         ▼
Continue   Route to identification unit
tracking   │
           ▼
      Status update: UNIDENTIFIED → IDENTIFIED
           │
           ▼
      Priority elevation: STANDARD → HIGH
```

---

## 9. Integration with Other Systems

### 9.1 Inbound Data

| Source | Data |
|--------|------|
| **Industrial Magnet** | New hash matches |
| **Hash Registry** | Known victim material lists |
| **National Authorities** | Victim status updates |
| **Victim Services** | Case worker assignments |

### 9.2 Outbound Data

| Destination | Data |
|-------------|------|
| **National LE** | Priority alerts, evidence objects |
| **Victim Services** | Resurfacing notifications |
| **GJEP** | Victim-tagged evidence anchors |
| **Watchdog** | Inactivity on victim cases |

---

## 10. Metrics & Reporting

### 10.1 Internal Metrics (Operational)

| Metric | Purpose |
|--------|---------|
| Resurfacing detection latency | System performance |
| Alert delivery time | SLA compliance |
| Takedown success rate | Effectiveness |
| Identification rate | Victim services effectiveness |

### 10.2 Aggregate Transparency (Public)

| Metric | Public? |
|--------|---------|
| Total known victim material tracked | ✅ Count only |
| Resurfacing events detected | ✅ Count only |
| Average time to takedown | ✅ Aggregate |
| Victims newly identified | ✅ Count only |

### 10.3 What Is Never Public

| Data | Reason |
|------|--------|
| ❌ Individual victim information | Privacy |
| ❌ Specific material details | Exploitation risk |
| ❌ Platform-specific data | Operational security |

---

## 11. Watchdog Integration

### 11.1 What Watchdog Monitors

| Condition | Trigger |
|-----------|---------|
| Victim case stalls | Inactivity alert |
| High resurfacing, no takedown | Priority escalation |
| Victim services not notified | Process failure flag |
| Critical victim case inactive | Immediate escalation |

### 11.2 Purpose

> **Victim cases cannot be quietly buried.**

The Watchdog ensures that high-priority victim protection doesn't stall because it's inconvenient.

---

## 12. Legal & Ethical Framework

### 12.1 Victim Rights Respected

| Right | Implementation |
|-------|----------------|
| **Privacy** | Pseudonymization, minimal data |
| **Notification** | Through services, not directly |
| **Support** | Automatic referral integration |
| **Agency** | Victim controls their participation |
| **Protection** | Material takedown priority |

### 12.2 Applicable Frameworks

| Framework | Relevance |
|-----------|-----------|
| Crime Victims Rights Act (US) | Notification rights |
| Victims of Crime Compensation | Support integration |
| GDPR (EU) | Data minimization |
| Child protection statutes | Priority handling |

---

## 13. Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VICTIM ENGINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Victim Registry (Pseudonymized)         │   │
│  │  • Victim IDs                                        │   │
│  │  • Material hashes                                   │   │
│  │  • Status tracking                                   │   │
│  │  • Resurfacing counts                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Match Engine                            │   │
│  │  • Hash comparison                                   │   │
│  │  • Near-duplicate detection                          │   │
│  │  • Series correlation                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │    Alert     │ │   Priority   │ │   Services   │       │
│  │   Router     │ │   Manager    │ │  Integrator  │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Summary

The Victim Engine ensures:

| Guarantee | Mechanism |
|-----------|-----------|
| **Re-victimization is visible** | Hash matching + instant alerts |
| **Victims are prioritized** | Priority classification system |
| **Support is triggered** | Automatic services notification |
| **Protection is urgent** | Priority takedown triggers |
| **Cases cannot stall** | Watchdog monitors victim cases |
| **Privacy is protected** | Pseudonymization + minimization |

> **"Every resurfacing is a new violation. This system makes that visible forever."**

---

*Victim Engine Specification v1.0 — CHILD GUARDIANS*
