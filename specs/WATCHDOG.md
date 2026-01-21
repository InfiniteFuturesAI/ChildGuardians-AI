# Watchdog & Oversight Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Watchdog is an independent oversight system that:

- **Surfaces inactivity** without accusations
- **Detects anomalies** without judgment
- **Prevents suppression** without interference
- **Generates transparency** without sensationalism

> **The Watchdog cannot act — it can only surface facts.**

---

## 2. Core Principle

> **"Sunlight is the best disinfectant."**

The Watchdog makes patterns visible. It does not make decisions. Decisions remain with humans, but patterns cannot be hidden.

---

## 3. Independence Architecture

### 3.1 Separation Guarantees

| Guarantee | Implementation |
|-----------|----------------|
| No single point of control | Distributed watchdog nodes |
| Cannot be disabled unilaterally | Requires supermajority to suspend |
| Logs cannot be altered | Append-only, cryptographically chained |
| Reports cannot be blocked | Automated generation and distribution |

### 3.2 Governance Structure

```
┌─────────────────────────────────────────────────────────┐
│                  WATCHDOG GOVERNANCE                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐                                    │
│  │ Technical Board │ ← Maintains code and algorithms    │
│  └────────┬────────┘                                    │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐                                    │
│  │ Oversight Board │ ← Reviews watchdog outputs         │
│  └────────┬────────┘                                    │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐                                    │
│  │ Public Reports  │ ← Aggregate, anonymized data       │
│  └─────────────────┘                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. What the Watchdog Monitors

### 4.1 Evidence Lifecycle Monitoring

| Metric | Threshold | Trigger |
|--------|-----------|---------|
| Time since evidence creation | >7 days | Yellow alert |
| Time since last action | >30 days | Orange alert |
| Time since last action (high-severity) | >14 days | Red alert |
| Time since last action (victim identified) | >7 days | Critical alert |

### 4.2 Access Pattern Monitoring

| Pattern | Concern | Action |
|---------|---------|--------|
| Access without subsequent action | Possible browsing | Log for review |
| Repeated access to same evidence | Possible fixation | Supervisor alert |
| Access outside normal hours | Possible unauthorized | Security review |
| Access from unusual location | Possible compromise | Security alert |
| Bulk access requests | Possible exfiltration | Immediate block |

### 4.3 Jurisdiction Routing Monitoring

| Metric | Threshold | Trigger |
|--------|-----------|---------|
| Evidence not routed | >48 hours | System alert |
| Routing rejected by recipient | Any rejection | Review required |
| Treaty request pending | >30 days | Escalation to coordination |
| Cross-border conflict unresolved | >14 days | Interpol/Europol alert |

### 4.4 Suppression Indicators

| Indicator | Detection Method | Action |
|-----------|------------------|--------|
| High-profile case stalled | Severity + inactivity | Oversight board notified |
| Multiple stalls by same authority | Pattern analysis | Aggregate report |
| Evidence sealed without prosecution | Seal + no case outcome | Review required |
| Access denied to entitled authority | Permission map violation | Immediate escalation |

---

## 5. Alert Levels

### 5.1 Alert Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      ALERT LEVELS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐                                                │
│  │ BLUE    │  Informational — logged, no action required    │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │ YELLOW  │  Attention — supervisor notified               │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │ ORANGE  │  Warning — case owner + supervisor notified    │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │ RED     │  Urgent — escalation to oversight board        │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │CRITICAL │  Emergency — immediate oversight intervention  │
│  └─────────┘                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Alert Routing

| Level | Recipients |
|-------|------------|
| BLUE | System log only |
| YELLOW | Case owner, supervisor |
| ORANGE | Case owner, supervisor, unit commander |
| RED | Oversight board, agency head |
| CRITICAL | Oversight board, agency head, external ombudsman |

---

## 6. Inactivity Detection

### 6.1 Inactivity Algorithm

```python
def check_inactivity(evidence: EvidenceObject) -> Alert:
    days_inactive = (now() - evidence.risk_clocks.last_activity_at).days
    
    # Severity-adjusted thresholds
    if evidence.match_data.known_victim_id:
        threshold = CRITICAL_THRESHOLD  # 7 days
    elif evidence.procedural_status.severity == "HIGH":
        threshold = HIGH_THRESHOLD  # 14 days
    else:
        threshold = NORMAL_THRESHOLD  # 30 days
    
    if days_inactive > threshold * 3:
        return Alert.CRITICAL, "Prolonged inactivity on priority evidence"
    elif days_inactive > threshold * 2:
        return Alert.RED, "Significant inactivity"
    elif days_inactive > threshold:
        return Alert.ORANGE, "Approaching inactivity threshold"
    elif days_inactive > threshold * 0.7:
        return Alert.YELLOW, "Activity declining"
    
    return Alert.BLUE, "Normal activity"
```

### 6.2 What Counts as Activity

| Activity | Resets Clock? |
|----------|---------------|
| Evidence accessed for review | ✅ Yes |
| Evidence exported | ✅ Yes |
| Case linked | ✅ Yes |
| Jurisdiction routing completed | ✅ Yes |
| Treaty request submitted | ✅ Yes |
| Note added with justification | ✅ Yes |
| Automated system access | ❌ No |
| Bulk query hit | ❌ No |

---

## 7. Anomaly Detection

### 7.1 Behavioral Anomalies

| Anomaly | Detection | Response |
|---------|-----------|----------|
| Access outside working hours | Time-based pattern | Flag for review |
| Access from new IP/location | Location change detection | Verification required |
| Access volume spike | Statistical deviation | Rate limiting |
| Sequential evidence access | Pattern detection | Supervisor alert |
| Evidence access without case linkage | Relationship check | Justification required |

### 7.2 System Anomalies

| Anomaly | Detection | Response |
|---------|-----------|----------|
| Evidence creation spike | Volume monitoring | Source verification |
| Hash match rate deviation | Statistical baseline | Algorithm review |
| Routing failures | Error rate tracking | System diagnostic |
| Audit log gaps | Continuity check | Immediate investigation |

---

## 8. Transparency Reports

### 8.1 Report Types

| Report | Frequency | Audience | Content |
|--------|-----------|----------|---------|
| System Health | Daily | Operators | Technical metrics |
| Activity Summary | Weekly | Supervisors | Case activity |
| Oversight Report | Monthly | Oversight board | Patterns, anomalies |
| Public Transparency | Annual | Public | Aggregate outcomes |

### 8.2 Public Transparency Report Contents

| Metric | Description |
|--------|-------------|
| Evidence objects created | Total count (no details) |
| Reappearances detected | Number of resurfacing events |
| Jurisdictions cooperating | List of participating authorities |
| Average time to first action | Efficiency metric |
| Cases with inactivity alerts | Count (no identifying info) |
| Takedowns triggered | Number of successful takedowns |
| Re-victimization alerts sent | Victim protection metric |

### 8.3 What Public Reports Do NOT Contain

| Excluded | Reason |
|----------|--------|
| ❌ Individual case details | Privacy, investigation integrity |
| ❌ Officer names | Personnel privacy |
| ❌ Victim information | Victim protection |
| ❌ Specific URLs or locations | Operational security |
| ❌ Investigation techniques | Operational security |

---

## 9. Escalation Procedures

### 9.1 Escalation Matrix

| Condition | Level 1 | Level 2 | Level 3 |
|-----------|---------|---------|---------|
| Inactivity (normal case) | Supervisor | Unit commander | Oversight board |
| Inactivity (high-profile) | Unit commander | Agency head | External ombudsman |
| Access anomaly | Supervisor | Security team | Agency head |
| Evidence suppression pattern | Unit commander | Oversight board | External authority |
| Audit integrity concern | Security team | Oversight board | External auditor |

### 9.2 Escalation Timeline

```
Day 0: Issue detected → YELLOW alert
  │
  ▼
Day 3: No response → ORANGE alert, escalate to Level 1
  │
  ▼
Day 7: No response → RED alert, escalate to Level 2
  │
  ▼
Day 14: No response → CRITICAL alert, escalate to Level 3
  │
  ▼
Day 21: External notification (if applicable)
```

---

## 10. Abuse Prevention

### 10.1 Watchdog Self-Monitoring

The Watchdog monitors itself:

| Self-Check | Purpose |
|------------|---------|
| Alert generation rate | Detect suppression of alerts |
| Report publication verification | Confirm reports are distributed |
| Configuration change detection | Prevent rule tampering |
| Node health monitoring | Ensure distributed operation |

### 10.2 Anti-Corruption Measures

| Measure | Implementation |
|---------|----------------|
| Distributed nodes | No single point of control |
| Multi-signature configuration | Changes require multiple approvals |
| Immutable logs | Append-only, cryptographically chained |
| External audit | Periodic third-party review |
| Whistleblower channel | Anonymous reporting path |

---

## 11. Integration Points

### 11.1 Data Sources

| Source | Data Received |
|--------|---------------|
| GJEP | Evidence lifecycle events |
| CIVIS-CYBER | Access logs, case linkages |
| Industrial Magnet | Collection events |
| Defense Simulator | Export events |
| All Systems | Error logs, anomalies |

### 11.2 Data Outputs

| Destination | Data Sent |
|-------------|-----------|
| Supervisors | Activity alerts |
| Oversight board | Pattern reports |
| External ombudsmen | Critical escalations |
| Public | Transparency reports |

---

## 12. Governance of the Watchdog

### 12.1 Who Controls the Watchdog?

| Function | Controller |
|----------|------------|
| Algorithm design | Technical board (multi-stakeholder) |
| Threshold settings | Oversight board |
| Alert routing | Configuration committee |
| Suspension/modification | Supermajority vote (≥75%) |

### 12.2 Watchdog Charter

The Watchdog operates under its own charter:

1. **Independence**: No operational authority can disable the Watchdog
2. **Transparency**: All Watchdog actions are themselves logged
3. **Neutrality**: Watchdog surfaces facts, not judgments
4. **Proportionality**: Alerts are calibrated to severity
5. **Accountability**: Watchdog governance is itself auditable

---

## 13. Implementation Specification

### 13.1 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WATCHDOG ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Event Stream                       │   │
│  │  (All system events flow through here)               │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Inactivity  │ │   Anomaly    │ │  Compliance  │       │
│  │  Detector    │ │   Detector   │ │  Checker     │       │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘       │
│         │                │                │                │
│         └────────────────┼────────────────┘                │
│                          ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Alert Manager                      │   │
│  │  (Deduplicates, prioritizes, routes)                 │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│              ┌────────────┼────────────┐                   │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Supervisor  │ │  Oversight   │ │   Public     │       │
│  │  Dashboard   │ │  Board       │ │   Reports    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 13.2 Event Schema

```json
{
  "event_id": "UUID",
  "event_type": "EVIDENCE_CREATED | EVIDENCE_ACCESSED | CASE_LINKED | ...",
  "timestamp": "ISO 8601 UTC",
  "actor_id": "string",
  "actor_authority": "string",
  "evidence_id": "UUID",
  "case_id": "UUID or null",
  "metadata": {},
  "signature": "Ed25519"
}
```

### 13.3 Alert Schema

```json
{
  "alert_id": "UUID",
  "alert_level": "BLUE | YELLOW | ORANGE | RED | CRITICAL",
  "alert_type": "INACTIVITY | ANOMALY | COMPLIANCE | ESCALATION",
  "created_at": "ISO 8601 UTC",
  "evidence_id": "UUID or null",
  "case_id": "UUID or null",
  "description": "string",
  "recommended_action": "string",
  "escalation_path": ["Level 1", "Level 2", "Level 3"],
  "current_escalation_level": 0,
  "acknowledged": false,
  "acknowledged_by": "string or null",
  "resolved": false,
  "resolved_by": "string or null",
  "resolution_notes": "string or null"
}
```

---

## 14. Operational Scenarios

### 14.1 Scenario: Stalled High-Profile Case

```
Day 0:  High-profile CSAM evidence created
Day 1:  Routed to national authority
Day 7:  No action taken
        → YELLOW alert to supervisor
Day 14: No action taken
        → ORANGE alert to unit commander
Day 21: No action taken
        → RED alert to oversight board
Day 28: Oversight board inquiry initiated
Day 30: Either action taken or external escalation
```

### 14.2 Scenario: Access Anomaly

```
Event:  Officer accesses 50 evidence objects in 1 hour
        (Normal: 5-10 per hour)
        
Detection: Anomaly detector flags volume spike

Alert:  ORANGE alert to supervisor and security team

Action: Officer must provide justification
        If justified (bulk case review): Alert resolved
        If unjustified: Access suspended, investigation

```

### 14.3 Scenario: Suppression Attempt

```
Event:  Evidence sealed without case outcome
        + High-severity flag
        + Victim identified
        
Detection: Compliance checker flags pattern

Alert:  RED alert to oversight board

Action: Oversight board reviews sealing justification
        If justified: Documented and closed
        If unjustified: External ombudsman notified
```

---

## 15. Why This Works

### 15.1 For Honest Officers

- **Protection from false accusations** — patterns surface, not individuals
- **Cover from political pressure** — process-based immunity
- **Visibility of workload** — inactivity thresholds are known

### 15.2 For Supervisors

- **Early warning** — problems surface before they become crises
- **Documentation** — all alerts create audit trail
- **Defensible decisions** — system-driven, not personal

### 15.3 For Victims

- **Cases cannot be buried** — inactivity is visible
- **Priority cases are prioritized** — victim-identified cases have shorter thresholds
- **Transparency builds trust** — public sees outcomes (not details)

### 15.4 For Public Trust

- **No "trust us"** — system is auditable
- **Aggregate visibility** — outcomes are public
- **Independent oversight** — watchdog is not controlled by operators

---

## 16. Summary

The Watchdog ensures:

| Guarantee | Mechanism |
|-----------|-----------|
| Evidence cannot be buried | Inactivity detection |
| Access cannot be hidden | Anomaly detection |
| Patterns cannot be suppressed | Automated reporting |
| Oversight cannot be bypassed | Independent governance |
| Trust is earned, not assumed | Public transparency |

> **The Watchdog does not create power. It makes power accountable.**

---

*Watchdog & Oversight Specification v1.0 — CHILD GUARDIANS*
