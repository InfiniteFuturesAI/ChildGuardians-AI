# Evidence Object Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Evidence Object is the atomic unit of the CHILD GUARDIANS system. Every piece of evidence exists as an immutable, self-describing, jurisdiction-aware object that:

- Is **born court-safe** (not fixed later)
- Contains **complete provenance**
- Enforces **jurisdictional permissions**
- Maintains **unbroken chain of custody**
- Survives **defense challenge**

---

## 2. Evidence Object Schema

```json
{
  "evidence_id": "UUID v7 (time-ordered)",
  "version": "1.0",
  "created_at": "ISO 8601 UTC timestamp",
  "sealed_at": "ISO 8601 UTC timestamp",
  
  "material": {
    "hash_sha256": "string",
    "hash_sha3_512": "string",
    "hash_photodna": "string (perceptual)",
    "hash_pdq": "string (perceptual, Facebook standard)",
    "file_size_bytes": "integer",
    "file_type_detected": "string",
    "file_type_claimed": "string"
  },
  
  "match_data": {
    "matched_database": "NCMEC | IWF | Interpol | Other",
    "matched_hash_type": "SHA256 | PhotoDNA | PDQ",
    "match_confidence": "EXACT | NEAR_DUPLICATE | THRESHOLD",
    "known_victim_id": "string or null",
    "known_series_id": "string or null"
  },
  
  "source": {
    "acquisition_system": "Industrial Magnet | ECP | CIVIS-CYBER",
    "acquisition_method": "PASSIVE_CRAWL | TIP_LINE | WARRANT_EXECUTION",
    "source_url_hash": "string (URL never stored plaintext)",
    "source_platform_type": "CLEARNET | TOR | I2P | TELEGRAM | OTHER",
    "source_country": "ISO 3166-1 alpha-2",
    "hosting_provider_hash": "string or null",
    "first_seen_at": "ISO 8601 UTC",
    "last_seen_at": "ISO 8601 UTC"
  },
  
  "legal_basis": {
    "authority_type": "WARRANT | MLAT | VOLUNTARY_DISCLOSURE | PASSIVE_COLLECTION",
    "authority_reference": "string (warrant number, treaty reference)",
    "authority_jurisdiction": "ISO 3166-1 alpha-2",
    "authority_valid_from": "ISO 8601 UTC",
    "authority_valid_until": "ISO 8601 UTC",
    "scope_limitations": ["array of scope restrictions"]
  },
  
  "jurisdiction": {
    "victim_country": "ISO 3166-1 alpha-2 or UNKNOWN",
    "hosting_country": "ISO 3166-1 alpha-2",
    "uploader_country": "ISO 3166-1 alpha-2 or UNKNOWN",
    "transit_countries": ["array of ISO 3166-1 alpha-2"],
    
    "permission_map": {
      "can_view_metadata": ["array of authority IDs"],
      "can_view_hashes": ["array of authority IDs"],
      "can_export_evidence": ["array of authority IDs"],
      "can_initiate_prosecution": ["array of authority IDs"],
      "must_not_access": ["array of authority IDs"],
      "requires_treaty": ["array of treaty references"]
    },
    
    "treaty_coverage": {
      "bilateral_treaties": ["array of treaty references"],
      "multilateral_treaties": ["MLAT | Budapest Convention | etc"],
      "pending_requests": ["array of request IDs"]
    }
  },
  
  "victim_data": {
    "victim_id": "string or null (if known)",
    "victim_country": "ISO 3166-1 alpha-2 or UNKNOWN",
    "victim_age_category": "PREPUBESCENT | PUBESCENT | UNKNOWN",
    "victim_status": "IDENTIFIED | RESCUED | UNIDENTIFIED | DECEASED",
    "revictimization_count": "integer",
    "last_resurfaced_at": "ISO 8601 UTC",
    "victim_services_notified": "boolean",
    "priority_takedown": "boolean"
  },
  
  "chain_of_custody": [
    {
      "action": "CREATED | ACCESSED | EXPORTED | SEALED | CORRECTION",
      "timestamp": "ISO 8601 UTC",
      "actor_id": "string (system or officer ID)",
      "actor_authority": "string (agency identifier)",
      "action_justification": "string",
      "ip_hash": "string",
      "session_id": "string",
      "signature": "Ed25519 signature"
    }
  ],
  
  "procedural_status": {
    "preflight_passed": "boolean",
    "preflight_warnings": ["array of warning codes"],
    "defense_simulator_passed": "boolean",
    "defense_simulator_issues": ["array of issue codes"],
    "disclosure_required": "boolean",
    "disclosure_deadline": "ISO 8601 UTC or null",
    "disclosure_completed": "boolean",
    "brady_flags": ["array of exculpatory relevance flags"],
    "exportable": "boolean",
    "export_blocked_reason": "string or null"
  },
  
  "case_linkage": {
    "linked_case_ids": ["array of case IDs"],
    "linked_evidence_ids": ["array of evidence IDs"],
    "linked_suspect_hashes": ["array of suspect identifier hashes"],
    "cross_border_refs": ["array of international case references"]
  },
  
  "risk_clocks": {
    "warrant_expiry": "ISO 8601 UTC or null",
    "retention_limit": "ISO 8601 UTC",
    "statutory_limitation": "ISO 8601 UTC or null",
    "inactivity_threshold_days": "integer",
    "last_activity_at": "ISO 8601 UTC",
    "escalation_triggered": "boolean"
  },
  
  "metadata": {
    "system_version": "string",
    "schema_version": "1.0",
    "classification": "LAW_ENFORCEMENT_SENSITIVE",
    "handling_instructions": ["array of handling codes"],
    "retention_policy": "string",
    "deletion_prohibited_until": "ISO 8601 UTC"
  },
  
  "integrity": {
    "object_hash": "SHA3-512 of entire object excluding this field",
    "signature": "Ed25519 signature by sealing authority",
    "witness_signatures": ["array of witness authority signatures"],
    "blockchain_anchor": "string or null (optional immutability proof)"
  }
}
```

---

## 3. Evidence Object Lifecycle

### 3.1 Lifecycle States

```
┌─────────────┐
│   CREATED   │ ← Initial acquisition
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PREFLIGHT  │ ← Validation checks
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌────────────┐
│ PASS │ │ FAIL/WARN  │
└──┬───┘ └─────┬──────┘
   │           │
   │           ▼
   │    ┌─────────────┐
   │    │ REMEDIATION │
   │    └──────┬──────┘
   │           │
   ◄───────────┘
       │
       ▼
┌─────────────┐
│   SEALED    │ ← Immutable, signed
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ROUTED    │ ← Jurisdiction mapping applied
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  AVAILABLE  │ ← Queryable by authorized parties
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌──────┐ ┌────────────┐
│ACCESS│ │   EXPORT   │
└──┬───┘ └─────┬──────┘
   │           │
   │           ▼
   │    ┌─────────────────┐
   │    │DEFENSE SIMULATOR│
   │    └────────┬────────┘
   │             │
   │         ┌───┴───┐
   │         │       │
   │         ▼       ▼
   │      ┌──────┐ ┌──────┐
   │      │ PASS │ │ FAIL │
   │      └──┬───┘ └──┬───┘
   │         │        │
   │         ▼        ▼
   │    ┌────────┐ ┌────────────┐
   │    │ EXPORT │ │   LOCKED   │
   │    └────────┘ └────────────┘
   │
   ▼
┌─────────────┐
│  ARCHIVED   │ ← Retention complete
└─────────────┘
```

### 3.2 State Transition Rules

| From State | To State | Trigger | Requirements |
|------------|----------|---------|--------------|
| CREATED | PREFLIGHT | Automatic | All required fields present |
| PREFLIGHT | SEALED | Preflight pass | No fatal errors |
| PREFLIGHT | REMEDIATION | Preflight fail | Fatal error detected |
| REMEDIATION | PREFLIGHT | Correction added | Correction record appended |
| SEALED | ROUTED | Automatic | Jurisdiction map computed |
| ROUTED | AVAILABLE | Automatic | At least one authority permitted |
| AVAILABLE | ACCESSED | Query by authority | Authority in permission map |
| AVAILABLE | EXPORT | Export request | Defense Simulator pass |
| EXPORT | LOCKED | Simulator fail | Remediation path provided |
| AVAILABLE | ARCHIVED | Retention complete | All obligations met |

---

## 4. Pre-Flight Checks (Mandatory)

Evidence cannot enter the system unless these checks pass:

### 4.1 Fatal Errors (Block Creation)

| Check | Validation |
|-------|------------|
| `timestamp_valid` | Created_at is valid UTC, not future |
| `hash_present` | At least SHA256 or SHA3-512 present |
| `source_recorded` | Acquisition system identified |
| `legal_basis_attached` | Authority type and reference present |
| `legal_basis_valid` | Authority not expired at acquisition |
| `jurisdiction_identified` | At least hosting_country present |

### 4.2 Warnings (Allow with Flag)

| Check | Validation |
|-------|------------|
| `victim_unknown` | Victim data incomplete |
| `perceptual_hash_missing` | PhotoDNA or PDQ not computed |
| `treaty_uncertain` | Treaty coverage unclear |
| `scope_broad` | Legal authority scope unusually wide |

---

## 5. Immutability Rules

### 5.1 Append-Only Principle

Evidence objects are **never modified**. Changes are recorded as:

```json
{
  "chain_of_custody": [
    {
      "action": "CORRECTION",
      "timestamp": "2026-01-17T14:30:00Z",
      "actor_id": "officer_12345",
      "actor_authority": "RCMP",
      "action_justification": "Victim country corrected after MLAT response",
      "correction_field": "victim_data.victim_country",
      "correction_old_value": "UNKNOWN",
      "correction_new_value": "CA",
      "signature": "..."
    }
  ]
}
```

### 5.2 What Cannot Be Corrected

| Field | Immutable? | Reason |
|-------|------------|--------|
| `evidence_id` | ✅ Yes | Identity anchor |
| `created_at` | ✅ Yes | Provenance |
| `material.hash_*` | ✅ Yes | Evidence identity |
| `source.*` | ✅ Yes | Acquisition record |
| `chain_of_custody.*` | ✅ Yes | Audit trail |
| `integrity.*` | ✅ Yes | Tamper detection |
| `legal_basis.*` | ⚠️ Append only | Can add, not remove |
| `victim_data.*` | ⚠️ Append only | Can correct with justification |
| `jurisdiction.*` | ⚠️ Append only | Can expand, not restrict |

---

## 6. Jurisdiction Permission Map

### 6.1 How Permissions Work

```python
def can_access(officer, evidence):
    if officer.authority_id in evidence.jurisdiction.permission_map.must_not_access:
        return False, "Explicitly blocked"
    
    if officer.authority_id in evidence.jurisdiction.permission_map.can_view_metadata:
        return True, "Metadata access granted"
    
    if evidence.jurisdiction.requires_treaty:
        if not treaty_active(officer.authority_id, evidence):
            return False, "Treaty required but not active"
    
    return evaluate_default_rules(officer, evidence)
```

### 6.2 Permission Inheritance

| Level | Inherits From | Can Override |
|-------|---------------|--------------|
| `can_export_evidence` | None | N/A |
| `can_initiate_prosecution` | None | N/A |
| `can_view_hashes` | `can_view_metadata` | Yes |
| `can_view_metadata` | None | N/A |

---

## 7. Chain of Custody Requirements

### 7.1 Every Action Records

| Field | Purpose |
|-------|---------|
| `action` | What was done |
| `timestamp` | When (UTC, cryptographically bound) |
| `actor_id` | Who (system or officer) |
| `actor_authority` | Which agency |
| `action_justification` | Why (mandatory for sensitive actions) |
| `ip_hash` | Where (privacy-preserving) |
| `session_id` | Session context |
| `signature` | Cryptographic proof |

### 7.2 Automated Chain Entries

| Action | Trigger | Justification Required |
|--------|---------|------------------------|
| CREATED | Acquisition complete | No (automatic) |
| SEALED | Preflight pass | No (automatic) |
| ACCESSED | Any query | No (automatic) |
| EXPORTED | Export to external system | Yes |
| CORRECTION | Field update | Yes |

---

## 8. Risk Clocks

### 8.1 Clock Types

| Clock | Purpose | Default Threshold |
|-------|---------|-------------------|
| `warrant_expiry` | Legal authority timeout | Varies by jurisdiction |
| `retention_limit` | Maximum storage duration | 25 years (configurable) |
| `statutory_limitation` | Prosecution deadline | Varies by offense/jurisdiction |
| `inactivity_threshold_days` | No action on evidence | 90 days |

### 8.2 Clock Alerts

| Condition | Action |
|-----------|--------|
| Clock at 30 days | Yellow alert to case owner |
| Clock at 7 days | Red alert to case owner + supervisor |
| Clock at 0 | Watchdog notified, escalation required |

---

## 9. Integration Points

### 9.1 Inbound Sources

| System | Evidence Type | Trust Level |
|--------|---------------|-------------|
| Industrial Magnet | Hash matches from dark web | HIGH |
| ECP | Generation attempts blocked | HIGH |
| CIVIS-CYBER | Officer-submitted evidence | MEDIUM (requires legal basis) |
| Tip Line | Public submissions | LOW (requires validation) |

### 9.2 Outbound Destinations

| System | What Is Sent | Conditions |
|--------|--------------|------------|
| GJEP | Complete evidence object | Always |
| National LE Systems | Jurisdiction-filtered view | Permission map allows |
| Prosecutors | Export package | Defense Simulator pass |
| Victim Services | Victim alert data only | Victim identified + priority |

---

## 10. Security Requirements

### 10.1 Encryption

| State | Encryption |
|-------|------------|
| At rest | AES-256-GCM |
| In transit | TLS 1.3 minimum |
| Hash storage | Encrypted at rest, decrypted only for matching |

### 10.2 Access Control

| Level | Requirements |
|-------|--------------|
| View metadata | Valid authority + in permission map |
| View hashes | Valid authority + active case linkage |
| Export | Valid authority + Defense Simulator pass |
| Seal/Correct | System admin + justification + witness |

---

*Evidence Object Specification v1.0 — CHILD GUARDIANS*
