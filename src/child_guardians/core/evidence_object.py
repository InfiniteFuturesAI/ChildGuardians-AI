"""
Evidence Object - Court-Safe Evidence Container

This module implements the Evidence Object specification from EVIDENCE_OBJECT.md.
Every evidence object is born court-safe with complete chain of custody,
legal basis, and jurisdiction mapping.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519


class EvidenceStatus(Enum):
    """Lifecycle states for evidence objects."""

    DRAFT = "draft"  # Being assembled
    VALIDATED = "validated"  # Pre-flight passed
    SEALED = "sealed"  # Immutable, court-ready
    EXPORTED = "exported"  # Sent to prosecution
    ARCHIVED = "archived"  # Retention period complete


class LegalBasisType(Enum):
    """Types of legal authority for evidence collection."""

    WARRANT = "warrant"
    CONSENT = "consent"
    EXIGENT = "exigent_circumstances"
    PLAIN_VIEW = "plain_view"
    PLATFORM_DISCLOSURE = "platform_disclosure"
    INTERNATIONAL_REQUEST = "international_request"


@dataclass
class MaterialHash:
    """Cryptographic fingerprint of evidence material."""

    hash_type: str  # sha256, sha3_512, photodna, pdq
    hash_value: str  # Hex-encoded hash
    source_file: str  # Original filename
    source_path: str  # Path on source device/system
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    computed_by: str = ""  # Officer/tool that computed hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "hash_type": self.hash_type,
            "hash_value": self.hash_value,
            "source_file": self.source_file,
            "source_path": self.source_path,
            "computed_at": self.computed_at.isoformat(),
            "computed_by": self.computed_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MaterialHash:
        return cls(
            hash_type=data["hash_type"],
            hash_value=data["hash_value"],
            source_file=data["source_file"],
            source_path=data["source_path"],
            computed_at=datetime.fromisoformat(data["computed_at"]),
            computed_by=data.get("computed_by", ""),
        )


@dataclass
class LegalBasis:
    """Legal authority for evidence collection."""

    basis_type: LegalBasisType
    reference: str  # Warrant number, consent form ID, etc.
    issued_by: str  # Judge name, consenting party, etc.
    issued_date: datetime
    scope: str  # What the authority covers
    expires: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "basis_type": self.basis_type.value,
            "reference": self.reference,
            "issued_by": self.issued_by,
            "issued_date": self.issued_date.isoformat(),
            "scope": self.scope,
            "expires": self.expires.isoformat() if self.expires else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LegalBasis:
        return cls(
            basis_type=LegalBasisType(data["basis_type"]),
            reference=data["reference"],
            issued_by=data["issued_by"],
            issued_date=datetime.fromisoformat(data["issued_date"]),
            scope=data["scope"],
            expires=datetime.fromisoformat(data["expires"]) if data.get("expires") else None,
        )


@dataclass
class JurisdictionMap:
    """Permission mapping for cross-jurisdiction evidence handling."""

    primary_jurisdiction: str  # ISO 3166-1 alpha-2 + subdivision
    hosting_country: str
    victim_country: str | None = None
    can_view_metadata: list[str] = field(default_factory=list)
    can_view_hashes: list[str] = field(default_factory=list)
    can_export_evidence: list[str] = field(default_factory=list)
    can_initiate_prosecution: list[str] = field(default_factory=list)
    requires_treaty: dict[str, str] = field(default_factory=dict)  # agency -> treaty ref
    must_not_access: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_jurisdiction": self.primary_jurisdiction,
            "hosting_country": self.hosting_country,
            "victim_country": self.victim_country,
            "can_view_metadata": self.can_view_metadata,
            "can_view_hashes": self.can_view_hashes,
            "can_export_evidence": self.can_export_evidence,
            "can_initiate_prosecution": self.can_initiate_prosecution,
            "requires_treaty": self.requires_treaty,
            "must_not_access": self.must_not_access,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JurisdictionMap:
        return cls(
            primary_jurisdiction=data["primary_jurisdiction"],
            hosting_country=data["hosting_country"],
            victim_country=data.get("victim_country"),
            can_view_metadata=data.get("can_view_metadata", []),
            can_view_hashes=data.get("can_view_hashes", []),
            can_export_evidence=data.get("can_export_evidence", []),
            can_initiate_prosecution=data.get("can_initiate_prosecution", []),
            requires_treaty=data.get("requires_treaty", {}),
            must_not_access=data.get("must_not_access", []),
        )


@dataclass
class CollectionDetails:
    """Metadata about evidence collection."""

    officer_id: str
    officer_name: str
    badge_number: str
    agency: str
    agency_unit: str
    collection_time: datetime
    collection_location: str
    tool_used: str
    tool_version: str
    tool_hash: str  # Hash of forensic tool for verification
    witness_present: bool = False
    witness_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "officer_id": self.officer_id,
            "officer_name": self.officer_name,
            "badge_number": self.badge_number,
            "agency": self.agency,
            "agency_unit": self.agency_unit,
            "collection_time": self.collection_time.isoformat(),
            "collection_location": self.collection_location,
            "tool_used": self.tool_used,
            "tool_version": self.tool_version,
            "tool_hash": self.tool_hash,
            "witness_present": self.witness_present,
            "witness_name": self.witness_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CollectionDetails:
        return cls(
            officer_id=data["officer_id"],
            officer_name=data["officer_name"],
            badge_number=data["badge_number"],
            agency=data["agency"],
            agency_unit=data["agency_unit"],
            collection_time=datetime.fromisoformat(data["collection_time"]),
            collection_location=data["collection_location"],
            tool_used=data["tool_used"],
            tool_version=data["tool_version"],
            tool_hash=data["tool_hash"],
            witness_present=data.get("witness_present", False),
            witness_name=data.get("witness_name"),
        )


class EvidenceObject:
    """
    Court-safe evidence container.

    Evidence objects are immutable once sealed. All modifications
    before sealing are logged in the chain of custody.
    """

    def __init__(
        self,
        case_number: str,
        evidence_type: str,
        legal_basis: LegalBasis,
        collection_details: CollectionDetails,
        jurisdiction: JurisdictionMap,
    ):
        self.evidence_id = str(uuid.uuid7()) if hasattr(uuid, "uuid7") else str(uuid.uuid4())
        self.case_number = case_number
        self.evidence_type = evidence_type
        self.legal_basis = legal_basis
        self.collection_details = collection_details
        self.jurisdiction = jurisdiction

        self.status = EvidenceStatus.DRAFT
        self.created_at = datetime.now(UTC)
        self.sealed_at: datetime | None = None
        self.exported_at: datetime | None = None

        self.material_hashes: list[MaterialHash] = []
        self.chain_of_custody: list[dict[str, Any]] = []
        self.pre_flight_results: dict[str, Any] | None = None
        self.defense_simulation_results: dict[str, Any] | None = None

        # Cryptographic integrity
        self._content_hash: str | None = None
        self._seal_signature: bytes | None = None

        # Record creation in chain of custody
        self._log_custody_event("created", self.collection_details.officer_id)

    def add_material_hash(self, material_hash: MaterialHash) -> None:
        """Add a material hash to this evidence object."""
        if self.status != EvidenceStatus.DRAFT:
            raise ValueError("Cannot modify sealed evidence")

        self.material_hashes.append(material_hash)
        self._log_custody_event(
            "hash_added",
            material_hash.computed_by,
            {"hash_type": material_hash.hash_type, "source_file": material_hash.source_file},
        )

    def validate(self) -> dict[str, Any]:
        """Run pre-flight validation checks."""
        if self.status != EvidenceStatus.DRAFT:
            raise ValueError("Evidence already validated")

        issues: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []

        # Check legal basis
        if not self.legal_basis.reference:
            issues.append(
                {
                    "code": "LEGAL-001",
                    "message": "Missing legal basis reference",
                    "severity": "error",
                }
            )

        if self.legal_basis.expires and self.legal_basis.expires < datetime.now(UTC):
            issues.append(
                {"code": "LEGAL-002", "message": "Legal authority has expired", "severity": "error"}
            )

        # Check collection details
        if not self.collection_details.tool_hash:
            warnings.append(
                {
                    "code": "COLLECTION-001",
                    "message": "Forensic tool hash not recorded",
                    "severity": "warning",
                }
            )

        # Check material hashes
        if not self.material_hashes:
            issues.append(
                {
                    "code": "MATERIAL-001",
                    "message": "No material hashes recorded",
                    "severity": "error",
                }
            )

        # Check chain of custody gaps
        custody_gaps = self._check_custody_gaps()
        for gap in custody_gaps:
            warnings.append(
                {
                    "code": "CUSTODY-001",
                    "message": f"Custody gap detected: {gap['duration']} hours",
                    "severity": "warning",
                    "details": gap,
                }
            )

        result = {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now(UTC).isoformat(),
        }

        self.pre_flight_results = result

        if result["passed"]:
            self.status = EvidenceStatus.VALIDATED
            self._log_custody_event("validated", self.collection_details.officer_id)

        return result

    def seal(self, private_key: ed25519.Ed25519PrivateKey, sealing_officer: str) -> str:
        """
        Seal the evidence object, making it immutable.

        Returns the content hash for verification.
        """
        if self.status != EvidenceStatus.VALIDATED:
            raise ValueError("Evidence must be validated before sealing")

        # Compute content hash
        content = self._serialize_for_hashing()
        self._content_hash = hashlib.sha3_512(content.encode()).hexdigest()

        # Sign with private key
        self._seal_signature = private_key.sign(self._content_hash.encode())

        self.sealed_at = datetime.now(UTC)
        self.status = EvidenceStatus.SEALED

        self._log_custody_event("sealed", sealing_officer, {"content_hash": self._content_hash})

        return self._content_hash

    def verify_seal(self, public_key: ed25519.Ed25519PublicKey) -> bool:
        """Verify the evidence seal is intact."""
        if self.status not in (
            EvidenceStatus.SEALED,
            EvidenceStatus.EXPORTED,
            EvidenceStatus.ARCHIVED,
        ):
            return False

        if not self._content_hash or not self._seal_signature:
            return False

        # Recompute content hash
        content = self._serialize_for_hashing()
        current_hash = hashlib.sha3_512(content.encode()).hexdigest()

        if current_hash != self._content_hash:
            return False

        # Verify signature
        try:
            public_key.verify(self._seal_signature, self._content_hash.encode())
            return True
        except Exception:
            return False

    def run_defense_simulation(self, simulator) -> dict[str, Any]:
        """Run the Defense Attorney Simulator against this evidence."""
        if self.status not in (EvidenceStatus.VALIDATED, EvidenceStatus.SEALED):
            raise ValueError("Evidence must be validated before defense simulation")

        results = simulator.evaluate(self)
        self.defense_simulation_results = results

        self._log_custody_event(
            "defense_simulation", "system", {"passed": results["passed"], "score": results["score"]}
        )

        return results

    def export_for_court(self, exporting_officer: str) -> dict[str, Any]:
        """
        Export evidence package for court.

        Requires:
        - Sealed status
        - Passed defense simulation
        """
        if self.status != EvidenceStatus.SEALED:
            raise ValueError("Evidence must be sealed before export")

        if not self.defense_simulation_results or not self.defense_simulation_results["passed"]:
            raise ValueError("Evidence must pass defense simulation before export")

        self.exported_at = datetime.now(UTC)
        self.status = EvidenceStatus.EXPORTED

        self._log_custody_event("exported", exporting_officer)

        return {
            "evidence_id": self.evidence_id,
            "case_number": self.case_number,
            "content_hash": self._content_hash,
            "exported_at": self.exported_at.isoformat(),
            "package": self.to_dict(),
        }

    def _log_custody_event(
        self, action: str, actor: str, details: dict[str, Any] | None = None
    ) -> None:
        """Record an event in the chain of custody."""
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "actor": actor,
            "evidence_id": self.evidence_id,
            "hash_before": self._compute_state_hash(),
        }
        if details:
            event["details"] = details

        self.chain_of_custody.append(event)

        # Update hash_after
        event["hash_after"] = self._compute_state_hash()

    def _compute_state_hash(self) -> str:
        """Compute hash of current evidence state."""
        state = {
            "evidence_id": self.evidence_id,
            "case_number": self.case_number,
            "status": self.status.value,
            "material_hashes": [h.to_dict() for h in self.material_hashes],
            "custody_count": len(self.chain_of_custody),
        }
        return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:16]

    def _serialize_for_hashing(self) -> str:
        """Serialize evidence for content hash computation."""
        data = {
            "evidence_id": self.evidence_id,
            "case_number": self.case_number,
            "evidence_type": self.evidence_type,
            "legal_basis": self.legal_basis.to_dict(),
            "collection_details": self.collection_details.to_dict(),
            "jurisdiction": self.jurisdiction.to_dict(),
            "material_hashes": [h.to_dict() for h in self.material_hashes],
            "created_at": self.created_at.isoformat(),
        }
        return json.dumps(data, sort_keys=True)

    def _check_custody_gaps(self) -> list[dict[str, Any]]:
        """Check for gaps in chain of custody."""
        gaps = []
        if len(self.chain_of_custody) < 2:
            return gaps

        for i in range(1, len(self.chain_of_custody)):
            prev = datetime.fromisoformat(self.chain_of_custody[i - 1]["timestamp"])
            curr = datetime.fromisoformat(self.chain_of_custody[i]["timestamp"])

            gap_hours = (curr - prev).total_seconds() / 3600
            if gap_hours > 12:  # Flag gaps over 12 hours
                gaps.append(
                    {
                        "from": self.chain_of_custody[i - 1]["timestamp"],
                        "to": self.chain_of_custody[i]["timestamp"],
                        "duration": round(gap_hours, 2),
                    }
                )

        return gaps

    def to_dict(self) -> dict[str, Any]:
        """Serialize evidence object to dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "case_number": self.case_number,
            "evidence_type": self.evidence_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sealed_at": self.sealed_at.isoformat() if self.sealed_at else None,
            "exported_at": self.exported_at.isoformat() if self.exported_at else None,
            "legal_basis": self.legal_basis.to_dict(),
            "collection_details": self.collection_details.to_dict(),
            "jurisdiction": self.jurisdiction.to_dict(),
            "material_hashes": [h.to_dict() for h in self.material_hashes],
            "chain_of_custody": self.chain_of_custody,
            "pre_flight_results": self.pre_flight_results,
            "defense_simulation_results": self.defense_simulation_results,
            "content_hash": self._content_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceObject:
        """Deserialize evidence object from dictionary."""
        obj = cls(
            case_number=data["case_number"],
            evidence_type=data["evidence_type"],
            legal_basis=LegalBasis.from_dict(data["legal_basis"]),
            collection_details=CollectionDetails.from_dict(data["collection_details"]),
            jurisdiction=JurisdictionMap.from_dict(data["jurisdiction"]),
        )

        obj.evidence_id = data["evidence_id"]
        obj.status = EvidenceStatus(data["status"])
        obj.created_at = datetime.fromisoformat(data["created_at"])
        obj.sealed_at = datetime.fromisoformat(data["sealed_at"]) if data.get("sealed_at") else None
        obj.exported_at = (
            datetime.fromisoformat(data["exported_at"]) if data.get("exported_at") else None
        )
        obj.material_hashes = [MaterialHash.from_dict(h) for h in data.get("material_hashes", [])]
        obj.chain_of_custody = data.get("chain_of_custody", [])
        obj.pre_flight_results = data.get("pre_flight_results")
        obj.defense_simulation_results = data.get("defense_simulation_results")
        obj._content_hash = data.get("content_hash")

        return obj
