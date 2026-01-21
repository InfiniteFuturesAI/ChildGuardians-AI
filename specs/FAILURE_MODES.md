# Failure Modes & Guardrails Specification

> **Version:** 1.0  
> **Status:** Draft  
> **Last Updated:** 2026-01-17

---

## Core Principle

> **If a mistake can invalidate a trial, the system must prevent the mistake from being possible.**

Not warn. Not recommend. **Prevent.**

---

## How to Read This Document

Each failure mode includes:
- **What Goes Wrong**: The procedural error
- **Consequence**: How cases collapse
- **System Control**: How CHILD GUARDIANS prevents it
- **Legal Rationale**: Why this matters in court
- **Audit Behavior**: How the system logs prevention

---

## Category 1: Evidence Collection Failures

### FM-001: Unlawful Collection
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence collected without legal authority (no warrant, expired warrant, exceeded scope) |
| **Consequence** | Evidence excluded under exclusionary rule; case dismissed |
| **System Control** | Evidence object cannot be created without `legal_basis` field. Authority validity checked at creation time. |
| **Legal Rationale** | Fourth Amendment (US), Section 8 Charter (CA), ECHR Article 8 (EU) |
| **Audit Behavior** | Blocked creation logged with `PREFLIGHT_FAIL_NO_LEGAL_BASIS` |

### FM-002: Warrant Scope Exceeded
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Officer collects evidence outside warrant parameters |
| **Consequence** | Evidence excluded; potential civil liability |
| **System Control** | `scope_limitations` array enforced at collection. System validates acquisition against stated scope. |
| **Legal Rationale** | Particularity requirement; Franks v. Delaware |
| **Audit Behavior** | Warning flag `SCOPE_EXCEEDED` triggers supervisor review |

### FM-003: Warrant Expired During Collection
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Collection occurs after warrant validity period |
| **Consequence** | All evidence after expiry is fruit of poisonous tree |
| **System Control** | `authority_valid_until` checked in real-time. Collection blocked if expired. |
| **Legal Rationale** | Temporal limits are constitutional requirements |
| **Audit Behavior** | Hard block `AUTHORITY_EXPIRED` with timestamp |

### FM-004: Missing Timestamp
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence has no reliable creation timestamp |
| **Consequence** | Cannot prove when evidence was collected; authenticity challenged |
| **System Control** | `created_at` is mandatory UTC timestamp, cryptographically signed at creation |
| **Legal Rationale** | Foundation requirement for evidence authenticity |
| **Audit Behavior** | Preflight fatal error `TIMESTAMP_MISSING` |

### FM-005: Timestamp Manipulation
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Timestamp altered to fit narrative |
| **Consequence** | Evidence excluded; officer perjury charges |
| **System Control** | Timestamps are immutable and cryptographically bound to evidence hash |
| **Legal Rationale** | Authenticity and integrity requirements |
| **Audit Behavior** | Tamper detection triggers `INTEGRITY_VIOLATION` |

---

## Category 2: Chain of Custody Failures

### FM-006: Undocumented Transfer
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence changes hands without documentation |
| **Consequence** | Chain of custody broken; evidence challenged as tampered |
| **System Control** | All access is through system; every touch logged automatically |
| **Legal Rationale** | Chain of custody is foundation of evidence reliability |
| **Audit Behavior** | Every action creates `chain_of_custody` entry |

### FM-007: Missing Signatures
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Transfer documents lack required signatures |
| **Consequence** | Defense argues evidence could have been tampered |
| **System Control** | Every chain entry includes Ed25519 cryptographic signature |
| **Legal Rationale** | Signatures prove specific human accountability |
| **Audit Behavior** | Unsigned entries impossible; system enforces signing |

### FM-008: Gap in Custody Timeline
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Period where evidence location is unknown |
| **Consequence** | Reasonable doubt about evidence integrity |
| **System Control** | Evidence never leaves system; "gaps" are logically impossible |
| **Legal Rationale** | Continuous custody is presumption of integrity |
| **Audit Behavior** | Custody audit can prove continuous control |

### FM-009: Unauthorized Access
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence accessed by unauthorized person |
| **Consequence** | Tampering opportunity; defense challenge |
| **System Control** | Access requires valid authority + jurisdiction permission map match |
| **Legal Rationale** | Restricted access prevents contamination claims |
| **Audit Behavior** | Blocked access logged `ACCESS_DENIED_UNAUTHORIZED` |

### FM-010: Access Without Justification
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Officer accesses evidence without case nexus |
| **Consequence** | Fishing expedition; privacy violation |
| **System Control** | Sensitive actions require `action_justification` field |
| **Legal Rationale** | Access must be need-to-know, not curiosity |
| **Audit Behavior** | Unjustified access flagged to watchdog |

---

## Category 3: Jurisdiction Failures

### FM-011: Wrong Jurisdiction Acted
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Officer from jurisdiction A prosecutes crime in jurisdiction B |
| **Consequence** | Lack of jurisdiction = case dismissed |
| **System Control** | `permission_map.can_initiate_prosecution` enforced at UI level |
| **Legal Rationale** | Territorial jurisdiction is foundational |
| **Audit Behavior** | Action blocked `JURISDICTION_NOT_PERMITTED` |

### FM-012: Treaty Requirements Ignored
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | International evidence used without treaty process |
| **Consequence** | Evidence excluded; diplomatic incident |
| **System Control** | `requires_treaty` array blocks action until treaty request logged |
| **Legal Rationale** | MLAT, bilateral treaty requirements |
| **Audit Behavior** | Block until `treaty_coverage` satisfied |

### FM-013: Sovereignty Violation
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Country A accesses evidence Country B has jurisdiction over |
| **Consequence** | International law violation; evidence tainted |
| **System Control** | `must_not_access` array enforces explicit prohibitions |
| **Legal Rationale** | National sovereignty in criminal matters |
| **Audit Behavior** | Hard block `SOVEREIGNTY_VIOLATION` |

### FM-014: Incorrect Country Determination
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Hosting country misidentified, wrong jurisdiction routed |
| **Consequence** | Wasted resources; potential wrongful prosecution |
| **System Control** | Multiple data points for country determination; confidence scoring |
| **Legal Rationale** | Accuracy prevents jurisdictional challenges |
| **Audit Behavior** | Low-confidence determinations flagged for review |

### FM-015: Dual Jurisdiction Conflict
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Two countries both claim prosecution authority |
| **Consequence** | Parallel prosecutions; double jeopardy issues |
| **System Control** | `cross_border_refs` tracks all jurisdictions; conflict detection |
| **Legal Rationale** | Ne bis in idem (double jeopardy) protection |
| **Audit Behavior** | Conflict alert sent to coordinating body (Interpol/Europol) |

---

## Category 4: Disclosure Failures

### FM-016: Brady Violation (Exculpatory Evidence Withheld)
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence favorable to defendant not disclosed |
| **Consequence** | Conviction overturned; prosecutor sanctioned |
| **System Control** | `brady_flags` array tracks exculpatory relevance; automatic disclosure alerts |
| **Legal Rationale** | Brady v. Maryland constitutional requirement |
| **Audit Behavior** | Brady-flagged evidence triggers `DISCLOSURE_REQUIRED` |

### FM-017: Disclosure Deadline Missed
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Required disclosure not made within time limit |
| **Consequence** | Evidence excluded or mistrial |
| **System Control** | `disclosure_deadline` tracked with countdown alerts |
| **Legal Rationale** | Due process requires timely disclosure |
| **Audit Behavior** | Deadline clock at 7 days triggers red alert |

### FM-018: Incomplete Disclosure
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Some required material not disclosed |
| **Consequence** | Appeals; retrials; sanctions |
| **System Control** | System tracks all linked evidence; disclosure checklist enforced |
| **Legal Rationale** | Complete disclosure prevents sandbagging |
| **Audit Behavior** | Disclosure completion requires attestation |

### FM-019: Disclosure to Wrong Party
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence disclosed to unauthorized recipient |
| **Consequence** | Privacy violation; investigation compromise |
| **System Control** | Disclosure routing enforced by jurisdiction permission map |
| **Legal Rationale** | Need-to-know limits on evidence access |
| **Audit Behavior** | All disclosures logged with recipient verification |

### FM-020: Victim Data Improperly Disclosed
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Victim identifying information leaked |
| **Consequence** | Re-victimization; civil liability; statute violation |
| **System Control** | Victim data fields marked `RESTRICTED`; separate permission required |
| **Legal Rationale** | Victim protection statutes (e.g., Crime Victims Rights Act) |
| **Audit Behavior** | Victim data access logged `VICTIM_DATA_ACCESS` with justification |

---

## Category 5: Evidence Integrity Failures

### FM-021: Hash Mismatch
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence hash at trial doesn't match hash at collection |
| **Consequence** | Evidence excluded as potentially tampered |
| **System Control** | Hash computed at creation, verified at every access |
| **Legal Rationale** | Digital evidence authentication requirement |
| **Audit Behavior** | Mismatch triggers `INTEGRITY_VIOLATION` |

### FM-022: Evidence Altered After Sealing
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Sealed evidence modified |
| **Consequence** | Tampering; evidence excluded; criminal liability |
| **System Control** | Evidence objects are append-only; modifications create correction records |
| **Legal Rationale** | Immutability is integrity guarantee |
| **Audit Behavior** | Any modification attempt logged; original preserved |

### FM-023: Missing Metadata
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence lacks context (source, method, date) |
| **Consequence** | Cannot authenticate; foundation challenge |
| **System Control** | Mandatory fields enforced at preflight; cannot proceed without |
| **Legal Rationale** | Authentication requires context |
| **Audit Behavior** | Missing metadata = preflight failure |

### FM-024: Perceptual Hash Only (No Cryptographic Hash)
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Near-duplicate match without exact match capability |
| **Consequence** | Defense argues material is different |
| **System Control** | SHA256 or SHA3-512 required; perceptual hashes are supplemental |
| **Legal Rationale** | Cryptographic certainty > perceptual similarity |
| **Audit Behavior** | Warning if only perceptual hash present |

### FM-025: Database Match Outdated
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Match against stale known-CSAM database |
| **Consequence** | False positives; wrongful investigation |
| **System Control** | Database version tracked; staleness threshold enforced |
| **Legal Rationale** | Currency of comparison data matters |
| **Audit Behavior** | Database version recorded with match |

---

## Category 6: Timing Failures

### FM-026: Statute of Limitations Expired
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Prosecution initiated after limitation period |
| **Consequence** | Case dismissed automatically |
| **System Control** | `statutory_limitation` clock tracked with alerts |
| **Legal Rationale** | Statutes of limitation are jurisdictional bars |
| **Audit Behavior** | Clock expiry triggers `STATUTE_EXPIRED` |

### FM-027: Case Inactive Too Long
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Case stalls with no action for extended period |
| **Consequence** | Evidence degrades; witnesses forget; justice denied |
| **System Control** | `inactivity_threshold_days` triggers escalation |
| **Legal Rationale** | Speedy justice requirement; victim rights |
| **Audit Behavior** | Inactivity flagged to watchdog |

### FM-028: MLAT Request Timeout
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | International request expires without response |
| **Consequence** | Evidence unavailable; case proceeds without key evidence |
| **System Control** | Treaty request deadlines tracked; reminders sent |
| **Legal Rationale** | Treaty obligations have timelines |
| **Audit Behavior** | Timeout logged; escalation to diplomatic channels |

### FM-029: Delayed Victim Notification
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Victim not notified of case developments in time |
| **Consequence** | Victim rights violation; complaint; oversight failure |
| **System Control** | Victim notification triggers automated when status changes |
| **Legal Rationale** | Crime Victims Rights Act; VOCA |
| **Audit Behavior** | Notification tracked with timestamp |

### FM-030: Warrant Application Delay
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Time-sensitive warrant not obtained in time |
| **Consequence** | Evidence lost; suspect escapes |
| **System Control** | Urgency flags on evidence objects; priority routing |
| **Legal Rationale** | Preservation of evidence is time-critical |
| **Audit Behavior** | High-priority items tracked for response time |

---

## Category 7: Human Error Failures

### FM-031: Wrong Evidence Attached to Case
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence from Case A attached to Case B |
| **Consequence** | Confusion; mistrial; wrongful prosecution |
| **System Control** | `linked_case_ids` validated; cross-check with case parameters |
| **Legal Rationale** | Evidence must relate to charged conduct |
| **Audit Behavior** | Linkage requires confirmation; mismatch flagged |

### FM-032: Duplicate Evidence Submission
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Same evidence submitted multiple times with different metadata |
| **Consequence** | Confusion; chain of custody questions |
| **System Control** | Hash deduplication at ingestion; single source of truth |
| **Legal Rationale** | One evidence object per unique material |
| **Audit Behavior** | Duplicate attempts logged `DUPLICATE_DETECTED` |

### FM-033: Victim Misidentification
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Wrong person identified as victim |
| **Consequence** | Wrongful investigation; trauma to innocent party |
| **System Control** | Victim identification requires confidence scoring; review threshold |
| **Legal Rationale** | Accuracy protects innocent parties |
| **Audit Behavior** | Low-confidence IDs flagged for human review |

### FM-034: Suspect Misidentification
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence attributed to wrong suspect |
| **Consequence** | Wrongful prosecution; actual perpetrator escapes |
| **System Control** | System does NOT identify suspects; only routes evidence |
| **Legal Rationale** | Suspect identification is human judgment |
| **Audit Behavior** | N/A - system explicitly excludes suspect profiling |

### FM-035: Manual Data Entry Error
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Typo in critical field (date, name, case number) |
| **Consequence** | Evidence misrouted; case management failure |
| **System Control** | Validation rules on all fields; format enforcement |
| **Legal Rationale** | Data accuracy is procedural requirement |
| **Audit Behavior** | Validation failures blocked at entry |

---

## Category 8: Suppression Failures

### FM-036: Evidence Buried (No Action Taken)
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | High-profile or sensitive case quietly abandoned |
| **Consequence** | Justice denied; public trust destroyed |
| **System Control** | Watchdog monitors inactivity; surfaces stalled cases |
| **Legal Rationale** | Accountability for action/inaction |
| **Audit Behavior** | Inactivity on high-severity cases triggers watchdog |

### FM-037: Unauthorized Sealing
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence sealed (hidden) without proper authority |
| **Consequence** | Evidence unavailable when needed; abuse of power |
| **System Control** | Sealing requires justification + witness + supervisor approval |
| **Legal Rationale** | Sealing is exceptional; must be justified |
| **Audit Behavior** | All seal actions logged with full justification |

### FM-038: Evidence Deletion
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence destroyed before retention period |
| **Consequence** | Spoliation; obstruction; appeals |
| **System Control** | Deletion is impossible; only archival after retention |
| **Legal Rationale** | Preservation duty until all proceedings complete |
| **Audit Behavior** | Deletion attempts logged as `DELETION_ATTEMPTED` |

### FM-039: Access Log Tampering
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Audit logs modified to hide actions |
| **Consequence** | Accountability destroyed; cover-up |
| **System Control** | Logs are append-only, cryptographically chained |
| **Legal Rationale** | Audit integrity is oversight foundation |
| **Audit Behavior** | Log tampering triggers `INTEGRITY_VIOLATION` |

### FM-040: Political Interference
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | External pressure to drop or slow case |
| **Consequence** | Justice denied; public trust destroyed |
| **System Control** | Process-based immunity; watchdog surfaces unusual patterns |
| **Legal Rationale** | Prosecutorial independence |
| **Audit Behavior** | Access patterns analyzed for anomalies |

---

## Category 9: Technical Failures

### FM-041: System Downtime During Collection
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence collected but cannot be ingested |
| **Consequence** | Provenance gap; chain of custody break |
| **System Control** | Offline collection protocol; queue with cryptographic timestamps |
| **Legal Rationale** | Continuous operation is reliability requirement |
| **Audit Behavior** | Offline ingestion logged with reconciliation |

### FM-042: Encryption Key Loss
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Keys to access encrypted evidence lost |
| **Consequence** | Evidence inaccessible; case collapses |
| **System Control** | Key escrow with multiple custodians; recovery protocol |
| **Legal Rationale** | Evidence must remain accessible |
| **Audit Behavior** | Key access logged; rotation tracked |

### FM-043: Database Corruption
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Data corrupted in storage |
| **Consequence** | Evidence integrity compromised |
| **System Control** | Multiple replicas; integrity verification; rollback capability |
| **Legal Rationale** | Data integrity is system requirement |
| **Audit Behavior** | Corruption detection triggers `INTEGRITY_CHECK_FAILED` |

### FM-044: Version Mismatch
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Different system versions produce incompatible evidence |
| **Consequence** | Evidence from older version cannot be validated |
| **System Control** | Schema version in every evidence object; backward compatibility |
| **Legal Rationale** | Evidence must remain interpretable |
| **Audit Behavior** | Version logged with every evidence object |

### FM-045: Hash Algorithm Obsolescence
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Hash algorithm (e.g., SHA-1) becomes cryptographically weak |
| **Consequence** | Evidence identity can be spoofed |
| **System Control** | Multiple hash algorithms; upgrade path defined |
| **Legal Rationale** | Cryptographic currency is evidence reliability |
| **Audit Behavior** | Algorithm upgrade tracked; old hashes preserved |

---

## Category 10: Oversight Failures

### FM-046: Watchdog Silenced
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Oversight system disabled or bypassed |
| **Consequence** | Suppression possible; accountability gone |
| **System Control** | Watchdog operates independently; no single point of control |
| **Legal Rationale** | Oversight must be independent |
| **Audit Behavior** | Watchdog health checked continuously |

### FM-047: No Independent Verification
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Evidence accepted without external validation |
| **Consequence** | Single point of failure; fabrication possible |
| **System Control** | Hash matches validated against multiple authoritative databases |
| **Legal Rationale** | Independent verification is reliability |
| **Audit Behavior** | Verification sources logged |

### FM-048: Transparency Report Suppressed
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Annual transparency data not published |
| **Consequence** | Public trust eroded; abuse hidden |
| **System Control** | Transparency reports generated automatically; cannot be blocked |
| **Legal Rationale** | Public accountability is design requirement |
| **Audit Behavior** | Report generation logged; publication verified |

### FM-049: Audit Trail Incomplete
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Some actions not logged |
| **Consequence** | Accountability gaps; suspicion |
| **System Control** | Every system action creates log entry; no exceptions |
| **Legal Rationale** | Complete audit trail is reliability foundation |
| **Audit Behavior** | Audit completeness verified continuously |

### FM-050: Conflict of Interest Undetected
| Attribute | Description |
|-----------|-------------|
| **What Goes Wrong** | Officer with conflict accesses case |
| **Consequence** | Bias; impropriety; appeal grounds |
| **System Control** | Conflict declaration required; access reviewed |
| **Legal Rationale** | Impartiality is procedural requirement |
| **Audit Behavior** | Access patterns flagged for conflict review |

---

## Summary Statistics

| Category | Count | Severity |
|----------|-------|----------|
| Evidence Collection | 5 | Critical |
| Chain of Custody | 5 | Critical |
| Jurisdiction | 5 | High |
| Disclosure | 5 | Critical |
| Evidence Integrity | 5 | Critical |
| Timing | 5 | High |
| Human Error | 5 | Medium |
| Suppression | 5 | Critical |
| Technical | 5 | High |
| Oversight | 5 | Critical |

---

## Integration with Defense Attorney Simulator

All 50 failure modes are checked by the Defense Attorney Simulator before evidence export. See: [Defense Attorney Simulator Specification](./DEFENSE_SIMULATOR.md)

---

*Failure Modes & Guardrails Specification v1.0 — CHILD GUARDIANS*
