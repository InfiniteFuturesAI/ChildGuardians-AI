# API Specifications

> **Specification:** v1.0  
> **Component:** Integration Layer  
> **Status:** Draft  
> **Classification:** Law Enforcement Confidential  

---

## 1. Overview

This document defines the API specifications for integrating with the CHILD GUARDIANS ecosystem. All APIs are designed for law enforcement and authorized agencies only.

**Base Principle:** Pull-based design. Systems respond to authorized queries — they never push or act autonomously.

---

## 2. Authentication & Authorization

### 2.1 Authentication Model

```
┌─────────────────────────────────────────────────────┐
│              AUTHENTICATION FLOW                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Agency Registration (offline, verified)         │
│  2. Certificate Issuance (agency-level)             │
│  3. Officer Credential (individual-level)           │
│  4. mTLS + JWT Token (per-session)                  │
│  5. Request Signing (per-request)                   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2.2 Authorization Tiers

| Tier | Access Level | Typical Role |
|------|--------------|--------------|
| **1** | Hash queries only | Patrol officer |
| **2** | Evidence package read | Detective |
| **3** | Evidence package create/export | CSAM investigator |
| **4** | Cross-jurisdiction coordination | Federal/international |
| **5** | System administration | Technical lead |

### 2.3 Request Signing

Every API request must include:

```json
{
  "request_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "officer_id": "badge-or-credential",
  "agency_id": "registered-agency",
  "justification": "case-reference",
  "signature": "ECDSA-P256-SHA256"
}
```

---

## 3. Core APIs

### 3.1 Hash Registry API

**Purpose:** Query known CSAM hashes

#### Check Single Hash

```
POST /api/v1/registry/check
```

**Request:**
```json
{
  "hash_type": "sha256",
  "hash_value": "a948904f2f0f479b8f8564...",
  "request_context": {
    "case_number": "2026-CSAM-001",
    "legal_basis": "warrant-12345"
  }
}
```

**Response:**
```json
{
  "match": true,
  "confidence": "confirmed",
  "first_seen": "2024-03-15T08:00:00Z",
  "category": "csam_identified",
  "victim_status": "known_victim",
  "jurisdiction_flags": ["US", "UK", "CA"],
  "evidence_package_available": true,
  "package_id": "EP-2024-00123"
}
```

#### Batch Check

```
POST /api/v1/registry/batch-check
```

**Request:**
```json
{
  "hashes": [
    {"type": "sha256", "value": "a948904f..."},
    {"type": "sha256", "value": "b123456f..."},
    {"type": "photodna", "value": "base64..."}
  ],
  "request_context": {
    "case_number": "2026-CSAM-001",
    "legal_basis": "warrant-12345"
  }
}
```

**Response:**
```json
{
  "results": [
    {"hash": "a948904f...", "match": true, "package_id": "EP-2024-00123"},
    {"hash": "b123456f...", "match": false},
    {"hash": "base64...", "match": true, "package_id": "EP-2024-00456"}
  ],
  "summary": {
    "total_checked": 3,
    "matches": 2,
    "new_hashes": 1
  }
}
```

### 3.2 Evidence Package API

**Purpose:** Create, retrieve, and export court-safe evidence packages

#### Create Evidence Package

```
POST /api/v1/evidence/packages
```

**Request:**
```json
{
  "case_number": "2026-CSAM-001",
  "evidence_type": "device_seizure",
  "material_hashes": [
    {
      "type": "sha256",
      "value": "a948904f...",
      "source_file": "image001.jpg",
      "source_path": "/seized/sdcard/DCIM/"
    }
  ],
  "legal_basis": {
    "type": "warrant",
    "reference": "warrant-12345",
    "issued_by": "Judge Smith",
    "issued_date": "2026-01-15",
    "scope": "digital_devices"
  },
  "collection_details": {
    "officer": "Det. Johnson",
    "badge": "12345",
    "agency": "Metro PD Cyber Unit",
    "collection_time": "2026-01-15T14:30:00Z",
    "tool_used": "FTK Imager 4.7",
    "tool_hash": "sha256:verified"
  }
}
```

**Response:**
```json
{
  "package_id": "EP-2026-00789",
  "status": "created",
  "chain_of_custody_id": "COC-2026-00789",
  "created_at": "2026-01-15T14:35:00Z",
  "pre_flight_status": "pending",
  "next_steps": [
    "Run pre-flight validation",
    "Add additional evidence as collected",
    "Export when court-ready"
  ]
}
```

#### Get Evidence Package

```
GET /api/v1/evidence/packages/{package_id}
```

**Response:**
```json
{
  "package_id": "EP-2026-00789",
  "status": "validated",
  "case_number": "2026-CSAM-001",
  "created_at": "2026-01-15T14:35:00Z",
  "last_updated": "2026-01-16T09:00:00Z",
  "material_count": 47,
  "known_victim_count": 3,
  "new_victim_count": 0,
  "pre_flight": {
    "status": "passed",
    "score": 95,
    "warnings": [
      {
        "code": "TIMING-001",
        "message": "14 hours between seizure and hash extraction",
        "severity": "warning",
        "recommendation": "Document custody during gap"
      }
    ],
    "blocks": []
  },
  "jurisdiction": {
    "primary": "US-CA",
    "secondary": ["US-NY", "UK"],
    "permission_map": {
      "US-CA": "full",
      "US-NY": "read_only",
      "UK": "pending_mlat"
    }
  },
  "chain_of_custody": [
    {
      "timestamp": "2026-01-15T14:35:00Z",
      "action": "created",
      "actor": "Det. Johnson",
      "agency": "Metro PD",
      "hash_before": null,
      "hash_after": "sha256:abc123..."
    }
  ]
}
```

#### Run Pre-Flight Validation

```
POST /api/v1/evidence/packages/{package_id}/preflight
```

**Response:**
```json
{
  "package_id": "EP-2026-00789",
  "pre_flight_result": "passed_with_warnings",
  "score": 92,
  "categories": {
    "lawful_collection": {"status": "pass", "score": 100},
    "authentication": {"status": "pass", "score": 95},
    "chain_of_custody": {"status": "warning", "score": 80},
    "jurisdiction": {"status": "pass", "score": 100},
    "disclosure": {"status": "pass", "score": 90},
    "foundation": {"status": "pass", "score": 95},
    "timeliness": {"status": "pass", "score": 85}
  },
  "warnings": [
    {
      "code": "COC-003",
      "question": "Can you account for every person who touched this device?",
      "current_answer": "Gap: 14 hours overnight",
      "recommendation": "Add custody log entry for overnight storage"
    }
  ],
  "blocks": [],
  "export_ready": true
}
```

#### Export Evidence Package

```
POST /api/v1/evidence/packages/{package_id}/export
```

**Request:**
```json
{
  "export_format": "court_bundle",
  "destination": "prosecutor",
  "recipient": {
    "name": "ADA Martinez",
    "agency": "County DA Cyber Unit",
    "secure_email": "martinez@da.county.gov"
  },
  "include": {
    "evidence_summary": true,
    "chain_of_custody": true,
    "pre_flight_report": true,
    "hash_verification": true,
    "victim_impact": "redacted"
  }
}
```

**Response:**
```json
{
  "export_id": "EX-2026-00123",
  "status": "generated",
  "package_id": "EP-2026-00789",
  "export_format": "court_bundle",
  "files": [
    "evidence_summary.pdf",
    "chain_of_custody.pdf",
    "hash_manifest.json",
    "pre_flight_report.pdf"
  ],
  "secure_delivery": {
    "method": "encrypted_transfer",
    "recipient_notified": true,
    "download_expires": "2026-01-20T14:35:00Z"
  },
  "audit_entry": "Export logged in chain of custody"
}
```

### 3.3 Victim Engine API

**Purpose:** Query victim status and coordinate services

#### Check Victim Status

```
POST /api/v1/victims/status
```

**Request:**
```json
{
  "hash": "sha256:a948904f...",
  "request_context": {
    "case_number": "2026-CSAM-001",
    "purpose": "new_material_identified"
  }
}
```

**Response:**
```json
{
  "victim_id": "VID-2024-00456",
  "status": "known_identified",
  "services_status": "active",
  "priority_level": "3",
  "re_victimization_events": 12,
  "last_seen": "2026-01-10T00:00:00Z",
  "jurisdiction_of_record": "US-TX",
  "notification_status": "services_notified",
  "law_enforcement_contact": {
    "agency": "FBI Dallas",
    "case_agent": "SA Williams",
    "reference": "FBI-2024-CSAM-789"
  }
}
```

#### Report New Victim Material

```
POST /api/v1/victims/material
```

**Request:**
```json
{
  "material_hash": "sha256:newmaterial...",
  "discovery_context": {
    "case_number": "2026-CSAM-001",
    "source": "seized_device",
    "discovery_date": "2026-01-15"
  },
  "victim_indicators": {
    "estimated_age": "8-10",
    "identifying_features": false,
    "series_match": "possible"
  }
}
```

**Response:**
```json
{
  "material_id": "MAT-2026-00123",
  "victim_match": "pending_analysis",
  "priority": "high",
  "ncmec_report": {
    "status": "generated",
    "report_id": "NCMEC-2026-123456"
  },
  "next_steps": [
    "Analysis team will review within 24 hours",
    "Victim services notified if match found",
    "Case agent will be updated"
  ]
}
```

### 3.4 Cross-Jurisdiction API

**Purpose:** Coordinate evidence sharing across jurisdictions

#### Request Jurisdiction Access

```
POST /api/v1/jurisdiction/access-request
```

**Request:**
```json
{
  "requesting_agency": "Metro PD Cyber Unit",
  "requesting_jurisdiction": "US-CA",
  "target_jurisdiction": "UK",
  "package_id": "EP-2026-00789",
  "legal_basis": {
    "type": "mlat_request",
    "treaty_reference": "US-UK MLAT 2003",
    "urgency": "standard"
  },
  "scope": "read_only",
  "purpose": "Victim identified as UK national"
}
```

**Response:**
```json
{
  "request_id": "JAR-2026-00456",
  "status": "submitted",
  "target_authority": "UK NCA",
  "estimated_response": "14-21 days",
  "interim_access": "none",
  "expedite_available": true,
  "expedite_criteria": "imminent_harm"
}
```

#### Check Jurisdiction Permissions

```
GET /api/v1/jurisdiction/permissions/{package_id}
```

**Response:**
```json
{
  "package_id": "EP-2026-00789",
  "primary_jurisdiction": "US-CA",
  "permissions": {
    "US": {
      "status": "full_access",
      "basis": "domestic"
    },
    "UK": {
      "status": "pending",
      "request_id": "JAR-2026-00456",
      "expected": "2026-02-05"
    },
    "CA": {
      "status": "read_only",
      "basis": "five_eyes"
    }
  },
  "restricted_jurisdictions": ["RU", "CN"],
  "restriction_reason": "no_treaty_coverage"
}
```

### 3.5 Watchdog API

**Purpose:** Oversight access for monitoring system health

#### Get System Health

```
GET /api/v1/watchdog/health
```

**Response:**
```json
{
  "timestamp": "2026-01-17T12:00:00Z",
  "overall_status": "healthy",
  "components": {
    "hash_registry": "operational",
    "evidence_packages": "operational",
    "victim_engine": "operational",
    "cross_jurisdiction": "operational"
  },
  "alerts": {
    "critical": 0,
    "warning": 2,
    "info": 15
  },
  "stalled_cases": 3,
  "inactivity_warnings": 7
}
```

#### Get Transparency Metrics

```
GET /api/v1/watchdog/transparency
```

**Response:**
```json
{
  "period": "2026-Q1",
  "metrics": {
    "total_queries": 125000,
    "evidence_packages_created": 3400,
    "packages_exported": 2800,
    "cross_jurisdiction_requests": 450,
    "average_case_duration_days": 45,
    "pre_flight_pass_rate": 0.94,
    "victim_notifications": 1200
  },
  "aggregate_by_jurisdiction": {
    "US": 2100,
    "UK": 450,
    "CA": 380,
    "AU": 290,
    "other": 180
  }
}
```

---

## 4. Error Handling

### 4.1 Error Response Format

```json
{
  "error": {
    "code": "AUTH_001",
    "message": "Insufficient authorization tier",
    "required_tier": 3,
    "current_tier": 2,
    "remediation": "Request tier upgrade from agency administrator"
  },
  "request_id": "uuid-v4",
  "timestamp": "ISO-8601"
}
```

### 4.2 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `AUTH_001` | Authorization | Insufficient tier |
| `AUTH_002` | Authorization | Invalid credentials |
| `AUTH_003` | Authorization | Expired session |
| `JUR_001` | Jurisdiction | No access to jurisdiction |
| `JUR_002` | Jurisdiction | Pending MLAT required |
| `EVD_001` | Evidence | Package not found |
| `EVD_002` | Evidence | Pre-flight failed |
| `EVD_003` | Evidence | Export blocked |
| `SYS_001` | System | Rate limited |
| `SYS_002` | System | Service unavailable |

---

## 5. Rate Limits

| Tier | Requests/Hour | Batch Size |
|------|---------------|------------|
| 1 | 100 | 10 |
| 2 | 500 | 50 |
| 3 | 2000 | 200 |
| 4 | 10000 | 1000 |
| 5 | Unlimited | 5000 |

---

## 6. Audit Requirements

Every API call is logged with:

| Field | Purpose |
|-------|---------|
| `request_id` | Unique identifier |
| `timestamp` | When request made |
| `officer_id` | Who made request |
| `agency_id` | Organization |
| `endpoint` | What was accessed |
| `justification` | Why (case reference) |
| `response_code` | Success/failure |
| `data_accessed` | What was returned (hashed) |

---

## 7. SDK Availability

| Language | Status | Notes |
|----------|--------|-------|
| Python | Available | Primary SDK |
| Java | Available | Enterprise integration |
| .NET | Available | Windows forensic tools |
| JavaScript | Planned | Web dashboard |

---

*API Specification v1.0 — CHILD GUARDIANS*
