# Defense Attorney Simulator Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## 1. Purpose

The Defense Attorney Simulator (DAS) is a pre-export validation system that subjects every evidence object to the same scrutiny a skilled defense attorney would apply in court.

**Goal**: Evidence that passes DAS will survive:
- Disclosure challenges
- Foundation challenges
- Chain of custody challenges
- Jurisdictional challenges
- Constitutional/Charter challenges
- Authentication challenges

---

## 2. Core Principle

> **No evidence leaves the system without proving it can survive adversarial challenge.**

The DAS is not punitive — it is protective:
- Protects cases from collapse
- Protects officers from procedural liability
- Protects prosecutors from Brady violations
- Protects victims from failed prosecutions

---

## 3. When DAS Runs

| Trigger | Required? | Override? |
|---------|-----------|-----------|
| Export to prosecutor | ✅ Mandatory | No |
| Export to international body | ✅ Mandatory | No |
| Export for court submission | ✅ Mandatory | No |
| Internal case review | ⚠️ Optional | Yes |
| High-profile case flag | ✅ Mandatory | No |

---

## 4. DAS Challenge Categories

### 4.1 Challenge Structure

Each challenge asks a question a defense attorney would ask. The system must provide an answer.

```
┌─────────────────────────────────────────────────────────┐
│              DEFENSE ATTORNEY SIMULATOR                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  For each Evidence Object:                              │
│                                                         │
│  ┌─────────────┐                                        │
│  │ Challenge 1 │──▶ Pass / Warn / Fail                  │
│  └─────────────┘                                        │
│  ┌─────────────┐                                        │
│  │ Challenge 2 │──▶ Pass / Warn / Fail                  │
│  └─────────────┘                                        │
│  ┌─────────────┐                                        │
│  │ Challenge N │──▶ Pass / Warn / Fail                  │
│  └─────────────┘                                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Final Verdict:                                   │    │
│  │   ✅ EXPORTABLE                                  │    │
│  │   ⚠️ EXPORTABLE WITH WARNINGS                   │    │
│  │   ❌ NOT EXPORTABLE (Remediation Required)      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Challenge Checklist

### Category A: Lawful Collection (Constitutional/Charter)

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| A1 | "Was there lawful authority to collect this evidence?" | `legal_basis.authority_type` is valid and documented | Missing or invalid |
| A2 | "Was the authority valid at time of collection?" | `authority_valid_from` ≤ `created_at` ≤ `authority_valid_until` | Outside validity window |
| A3 | "Was collection within the scope of authority?" | Acquisition method matches `scope_limitations` | Scope exceeded |
| A4 | "Was the collection method itself lawful?" | `acquisition_method` in [PASSIVE_CRAWL, WARRANT_EXECUTION, VOLUNTARY_DISCLOSURE, MLAT] | Unlawful method |
| A5 | "Was there any violation of privacy rights?" | No active interaction with target; passive collection only | Active intrusion detected |

### Category B: Authentication & Integrity

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| B1 | "Can you prove this evidence is what you claim it is?" | Cryptographic hash present and verified | Hash missing or mismatch |
| B2 | "Has this evidence been altered since collection?" | `object_hash` matches computed hash; signatures valid | Integrity violation |
| B3 | "Can you prove when this evidence was collected?" | `created_at` cryptographically bound | Timestamp unverifiable |
| B4 | "Is this a true and accurate copy?" | Original hash matches; no transformation applied | Copy differs from original |
| B5 | "Can you explain the file format and metadata?" | `file_type_detected` matches `file_type_claimed`; metadata present | Format inconsistency |

### Category C: Chain of Custody

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| C1 | "Can you account for every person who touched this evidence?" | Complete `chain_of_custody` array with all actions | Gaps in chain |
| C2 | "Can you prove each transfer was authorized?" | Every chain entry has valid `actor_authority` | Unauthorized access |
| C3 | "Is there any period where evidence location is unknown?" | Continuous custody; no gaps | Custody gap detected |
| C4 | "Can you prove the evidence wasn't tampered with during storage?" | Encryption at rest; integrity checks pass | Encryption or integrity failure |
| C5 | "Who had access and why?" | Every access has `action_justification` for sensitive actions | Unjustified access present |

### Category D: Jurisdiction

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| D1 | "Does this court have jurisdiction over this evidence?" | Requesting authority in `permission_map.can_initiate_prosecution` | Not authorized |
| D2 | "Were international treaty requirements followed?" | `treaty_coverage` satisfied or not required | Treaty required but missing |
| D3 | "Was sovereignty of other nations respected?" | Requesting authority not in `must_not_access` | Sovereignty violation |
| D4 | "Is the hosting country correctly identified?" | `hosting_country` has high confidence determination | Low confidence or unknown |
| D5 | "Are there conflicting jurisdictional claims?" | No unresolved conflicts in `cross_border_refs` | Unresolved conflict exists |

### Category E: Disclosure (Brady)

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| E1 | "Has all exculpatory evidence been disclosed?" | All `brady_flags` items disclosed | Undisclosed Brady material |
| E2 | "Was disclosure timely?" | `disclosure_completed` before `disclosure_deadline` | Deadline missed |
| E3 | "Is disclosure complete?" | All linked evidence disclosed | Incomplete disclosure |
| E4 | "Was victim privacy protected in disclosure?" | Victim data redacted appropriately | Victim data exposed |
| E5 | "Are there any undisclosed related evidence items?" | All `linked_evidence_ids` reviewed for disclosure | Related items not reviewed |

### Category F: Foundation & Relevance

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| F1 | "Is this evidence relevant to the charged conduct?" | `linked_case_ids` contains valid case with matching charges | No case linkage |
| F2 | "Can a witness testify to its authenticity?" | System can generate authentication certificate | Cannot authenticate |
| F3 | "Is the known-CSAM database reliable and current?" | Match database has documented authority and currency | Database stale or unverified |
| F4 | "Is the hash match methodology accepted?" | Hash algorithm is current and court-accepted | Obsolete algorithm |
| F5 | "Is the similarity threshold for near-duplicates defensible?" | Perceptual hash threshold documented and validated | Threshold not defensible |

### Category G: Timeliness

| ID | Challenge Question | Pass Condition | Fail Condition |
|----|-------------------|----------------|----------------|
| G1 | "Is prosecution within statute of limitations?" | `statutory_limitation` not expired | Statute expired |
| G2 | "Was evidence preserved timely?" | `created_at` within reasonable time of offense | Unreasonable delay |
| G3 | "Was warrant executed timely?" | Execution within warrant validity | Warrant expired at execution |
| G4 | "Have MLAT deadlines been met?" | Treaty requests timely | Treaty timeout |
| G5 | "Has the defendant's right to speedy trial been respected?" | Case activity within thresholds | Undue delay |

---

## 6. Verdict Rules

### 6.1 Result Types

| Result | Symbol | Meaning |
|--------|--------|---------|
| **PASS** | ✅ | Challenge fully satisfied |
| **WARN** | ⚠️ | Challenge satisfied with noted concern |
| **FAIL** | ❌ | Challenge not satisfied; remediation required |

### 6.2 Final Verdict Calculation

```python
def calculate_verdict(challenges: List[ChallengeResult]) -> Verdict:
    fails = [c for c in challenges if c.result == FAIL]
    warns = [c for c in challenges if c.result == WARN]
    
    if len(fails) > 0:
        return Verdict.NOT_EXPORTABLE, fails, "Remediation required"
    
    if len(warns) > 5:
        return Verdict.MANUAL_REVIEW, warns, "Excessive warnings require review"
    
    if len(warns) > 0:
        return Verdict.EXPORTABLE_WITH_WARNINGS, warns, "Proceed with caution"
    
    return Verdict.EXPORTABLE, [], "Clean export"
```

### 6.3 Verdict Actions

| Verdict | Action |
|---------|--------|
| ✅ EXPORTABLE | Export proceeds |
| ⚠️ EXPORTABLE_WITH_WARNINGS | Export proceeds; warnings logged; supervisor notified |
| 🔍 MANUAL_REVIEW | Export blocked until human review |
| ❌ NOT_EXPORTABLE | Export blocked; remediation path provided |

---

## 7. Remediation Paths

When a challenge fails, DAS provides a specific remediation path:

### Example Remediation Output

```json
{
  "challenge_id": "A2",
  "challenge_question": "Was the authority valid at time of collection?",
  "result": "FAIL",
  "reason": "Evidence collected after warrant expiry",
  "evidence_field": "legal_basis.authority_valid_until",
  "field_value": "2025-12-01T00:00:00Z",
  "collection_time": "2025-12-15T14:30:00Z",
  "remediation": {
    "options": [
      {
        "option": "OBTAIN_NEW_AUTHORITY",
        "description": "Obtain fresh warrant covering collection date",
        "feasibility": "LOW - evidence already collected"
      },
      {
        "option": "INDEPENDENT_SOURCE",
        "description": "Demonstrate evidence would have been discovered through independent lawful source",
        "feasibility": "MEDIUM - if parallel investigation exists"
      },
      {
        "option": "INEVITABLE_DISCOVERY",
        "description": "Argue evidence would have been inevitably discovered",
        "feasibility": "MEDIUM - jurisdiction dependent"
      },
      {
        "option": "EXCLUDE_EVIDENCE",
        "description": "Do not use this evidence object",
        "feasibility": "HIGH - always available"
      }
    ],
    "legal_research": [
      "Murray v. United States, 487 U.S. 533 (1988) - Independent source doctrine",
      "Nix v. Williams, 467 U.S. 431 (1984) - Inevitable discovery doctrine"
    ]
  }
}
```

---

## 8. DAS Report Format

### 8.1 Report Structure

```
╔══════════════════════════════════════════════════════════════╗
║           DEFENSE ATTORNEY SIMULATOR REPORT                  ║
╠══════════════════════════════════════════════════════════════╣
║ Evidence ID:    [UUID]                                       ║
║ Report ID:      [UUID]                                       ║
║ Generated:      [ISO 8601 UTC]                               ║
║ Requested By:   [Authority ID]                               ║
║ Purpose:        [EXPORT_PROSECUTOR | EXPORT_COURT | REVIEW]  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ FINAL VERDICT:  ✅ EXPORTABLE                                ║
║                 ⚠️ EXPORTABLE WITH WARNINGS                  ║
║                 🔍 MANUAL REVIEW REQUIRED                    ║
║                 ❌ NOT EXPORTABLE                            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                     CHALLENGE RESULTS                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ A. Lawful Collection                                         ║
║    A1: ✅ PASS - Lawful authority documented                 ║
║    A2: ✅ PASS - Authority valid at collection               ║
║    A3: ✅ PASS - Collection within scope                     ║
║    A4: ✅ PASS - Collection method lawful                    ║
║    A5: ✅ PASS - No privacy violation                        ║
║                                                              ║
║ B. Authentication & Integrity                                ║
║    B1: ✅ PASS - Hash verified                               ║
║    B2: ✅ PASS - No alteration detected                      ║
║    B3: ✅ PASS - Timestamp verified                          ║
║    B4: ✅ PASS - True copy confirmed                         ║
║    B5: ⚠️ WARN - File type mismatch (minor)                 ║
║                                                              ║
║ [... additional categories ...]                              ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                     WARNINGS DETAIL                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ B5: File type mismatch                                       ║
║     Detected: image/jpeg                                     ║
║     Claimed:  image/png                                      ║
║     Impact:   Minor - content hash still valid               ║
║     Action:   Note in submission; not fatal to admissibility ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                     CERTIFICATION                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ This evidence object has been subjected to simulated         ║
║ adversarial challenge consistent with defense scrutiny       ║
║ in common law jurisdictions.                                 ║
║                                                              ║
║ Report Hash:    [SHA3-512]                                   ║
║ System Version: [Version]                                    ║
║ Signature:      [Ed25519]                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 9. Integration Points

### 9.1 Export Flow

```
Evidence Object
      │
      ▼
┌─────────────┐
│Export Request│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│Defense Attorney     │
│Simulator            │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌────────┐  ┌────────────┐
│  PASS  │  │ FAIL/WARN  │
└───┬────┘  └─────┬──────┘
    │             │
    ▼             ▼
┌────────┐  ┌────────────┐
│ Export │  │ Remediation│
│Package │  │ or Manual  │
└────────┘  │ Review     │
            └────────────┘
```

### 9.2 DAS API

```python
class DefenseAttorneySimulator:
    
    def run_full_challenge(
        self, 
        evidence: EvidenceObject,
        purpose: ExportPurpose,
        requesting_authority: AuthorityID
    ) -> DASReport:
        """
        Run all challenges against an evidence object.
        
        Returns complete DAS report with verdict and remediation paths.
        """
        pass
    
    def run_category(
        self,
        evidence: EvidenceObject,
        category: ChallengeCategory
    ) -> List[ChallengeResult]:
        """
        Run only one category of challenges.
        
        Useful for iterative remediation.
        """
        pass
    
    def get_remediation(
        self,
        evidence: EvidenceObject,
        failed_challenge: ChallengeID
    ) -> RemediationOptions:
        """
        Get detailed remediation options for a specific failure.
        """
        pass
    
    def generate_certification(
        self,
        evidence: EvidenceObject,
        report: DASReport
    ) -> Certification:
        """
        Generate signed certification for court submission.
        """
        pass
```

---

## 10. Jurisdiction-Specific Modules

DAS supports jurisdiction-specific challenge modules:

### 10.1 Available Modules

| Module | Jurisdiction | Additional Challenges |
|--------|--------------|----------------------|
| `das_us_federal` | United States Federal | Fourth Amendment, Fifth Amendment, Brady |
| `das_us_state` | US State (configurable) | State constitutional provisions |
| `das_canada` | Canada | Section 8 Charter, R. v. Grant analysis |
| `das_uk` | United Kingdom | PACE, Human Rights Act |
| `das_eu` | European Union | GDPR, ECHR Article 8 |
| `das_australia` | Australia | Evidence Act, Bunning v. Cross |
| `das_interpol` | International | MLAT, treaty requirements |

### 10.2 Module Selection

```python
das = DefenseAttorneySimulator(
    modules=[
        "das_core",           # Always required
        "das_canada",         # Primary jurisdiction
        "das_interpol"        # International evidence
    ]
)
```

---

## 11. Continuous Improvement

### 11.1 Learning from Court Outcomes

When evidence is challenged in actual court proceedings:

1. **Outcome logged** — Did evidence survive challenge?
2. **Challenge mapped** — Which DAS challenge category?
3. **Gap analysis** — Did DAS catch this issue?
4. **Module update** — Add new challenge if needed

### 11.2 Version Control

Each DAS report includes:
- System version
- Module versions
- Challenge set version

This allows retrospective analysis: "Would this evidence pass under current rules?"

---

## 12. Operator Interface

### 12.1 Pre-Export Warning

Before export, officers see:

```
╔══════════════════════════════════════════════════════════╗
║         DEFENSE ATTORNEY SIMULATOR SUMMARY               ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Evidence ID: 7f3a9c2e-...                               ║
║                                                          ║
║  Verdict: ⚠️ EXPORTABLE WITH WARNINGS                   ║
║                                                          ║
║  Warnings:                                               ║
║    • B5: Minor file type mismatch                        ║
║    • G4: MLAT response pending (non-blocking)            ║
║                                                          ║
║  Recommendation:                                         ║
║    Proceed with export. Note warnings in submission.     ║
║                                                          ║
║  [View Full Report]  [Proceed to Export]  [Cancel]       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### 12.2 Failure Blocking Screen

If DAS fails:

```
╔══════════════════════════════════════════════════════════╗
║         EXPORT BLOCKED                                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Evidence ID: 7f3a9c2e-...                               ║
║                                                          ║
║  Verdict: ❌ NOT EXPORTABLE                              ║
║                                                          ║
║  Fatal Issues:                                           ║
║    • A2: Evidence collected after warrant expiry         ║
║                                                          ║
║  Remediation Options:                                    ║
║    1. Obtain new authority (feasibility: LOW)            ║
║    2. Independent source doctrine (feasibility: MEDIUM)  ║
║    3. Exclude this evidence from case                    ║
║                                                          ║
║  [View Full Report]  [Request Supervisor Review]         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## 13. Why This Works

### 13.1 For Officers

- **No surprise court failures** — issues caught early
- **Clear remediation paths** — not just "fix it"
- **Documentation provided** — for supervisor review

### 13.2 For Prosecutors

- **Confident evidence** — already challenged
- **Disclosure tracked** — Brady compliance built-in
- **Court-ready packages** — with certification

### 13.3 For Defense Attorneys

- **Transparent process** — can request DAS report
- **Reproducible results** — same system, same challenges
- **Professional respect** — system takes defense seriously

### 13.4 For Victims

- **Fewer failed prosecutions** — cases survive court
- **Faster justice** — issues caught early, not at trial
- **Reduced trauma** — fewer mistrials and retrials

---

*Defense Attorney Simulator Specification v1.0 — CHILD GUARDIANS*
