#!/usr/bin/env python3
"""
CHILD GUARDIANS - Example: Complete Evidence Workflow

⚠️ DEMO ONLY - All data in this example is synthetic.
Do not use these credentials, case numbers, or identifiers in production.

This example demonstrates the complete workflow from evidence collection
to court-ready export.

Run with: python examples/complete_workflow.py
"""

from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.asymmetric import ed25519

from child_guardians.core.chain_of_custody import ChainOfCustody, CustodyAction
from child_guardians.core.defense_simulator import DefenseSimulator
from child_guardians.core.evidence_object import (
    CollectionDetails,
    EvidenceObject,
    JurisdictionMap,
    LegalBasis,
    LegalBasisType,
    MaterialHash,
)
from child_guardians.core.hash_registry import (
    HashRegistry,
    HashType,
    MatchConfidence,
    VictimStatus,
    compute_hash,
)


def main():
    print("=" * 60)
    print("CHILD GUARDIANS - Complete Evidence Workflow Example")
    print("=" * 60)

    # Initialize components
    registry = HashRegistry(":memory:")  # Use in-memory for demo
    custody = ChainOfCustody(":memory:")
    simulator = DefenseSimulator()

    # Generate agency signing key (in production, use HSM)
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    print("\n[1] Creating Evidence Object...")

    # Create legal basis (warrant)
    now = datetime.now(UTC)
    legal_basis = LegalBasis(
        basis_type=LegalBasisType.WARRANT,
        reference="WARRANT-2024-001",
        issued_by="Magistrate Judge Smith",
        issued_date=now - timedelta(hours=6),
        scope="Search of digital devices at 123 Main Street",
        expires=now + timedelta(days=30),
    )

    # Create collection details
    collection = CollectionDetails(
        officer_id="FBI-AGENT-001",
        officer_name="Special Agent Jane Doe",
        badge_number="SA-12345",
        agency="Federal Bureau of Investigation",
        agency_unit="Cyber Crimes Unit",
        collection_time=now - timedelta(hours=2),
        collection_location="123 Main Street, Anytown, US",
        tool_used="FTK Imager",
        tool_version="4.7.1.2",
        tool_hash="sha256:abc123def456...",
    )

    # Create jurisdiction map
    jurisdiction = JurisdictionMap(
        primary_jurisdiction="US-FBI",
        hosting_country="US",
        can_export_evidence=["FBI", "DOJ", "NCMEC"],
    )

    # Create evidence object
    evidence = EvidenceObject(
        case_number="CYBER-2024-00042",
        evidence_type="digital_image",
        legal_basis=legal_basis,
        collection_details=collection,
        jurisdiction=jurisdiction,
    )

    print(f"  Evidence ID: {evidence.evidence_id}")
    print(f"  Status: {evidence.status.value}")

    # Record custody event
    custody.record_event(
        evidence_id=evidence.evidence_id,
        action=CustodyAction.CREATED,
        actor_id=collection.officer_id,
        actor_name=collection.officer_name,
        actor_agency=collection.agency,
        details={"case_number": evidence.case_number},
    )

    print("\n[2] Computing and Checking Hash...")

    # Simulate file data
    file_data = b"This represents the actual file content"
    file_hash = compute_hash(file_data, HashType.SHA256)

    # Register a known hash for demo purposes
    registry.register(
        hash_type=HashType.SHA256,
        hash_value=file_hash,
        confidence=MatchConfidence.CONFIRMED,
        victim_status=VictimStatus.IDENTIFIED,
        source_authority="NCMEC",
        category="csam_confirmed",
    )

    # Check hash against registry
    match_result = registry.check(
        hash_type=HashType.SHA256,
        hash_value=file_hash,
        querying_agency="FBI",
        querying_officer=collection.officer_id,
        case_reference=evidence.case_number,
        legal_basis=legal_basis.reference,
    )

    print(f"  File Hash: {file_hash[:32]}...")
    print(f"  Registry Match: {'YES' if match_result.found else 'NO'}")
    if match_result.found:
        print(f"  Confidence: {match_result.record.confidence.value}")
        print(f"  Victim Status: {match_result.record.victim_status.value}")

    # Add hash to evidence
    material_hash = MaterialHash(
        hash_type="sha256",
        hash_value=file_hash,
        source_file="image_001.jpg",
        source_path="/evidence/device/images/image_001.jpg",
        computed_by=collection.officer_id,
        computed_at=now,
    )
    evidence.add_material_hash(material_hash)

    # Note: registry match info is logged in chain of custody

    # Record hash added
    custody.record_event(
        evidence_id=evidence.evidence_id,
        action=CustodyAction.MODIFIED,
        actor_id=collection.officer_id,
        actor_name=collection.officer_name,
        actor_agency=collection.agency,
        details={"action": "hash_added", "hash_type": "sha256"},
    )

    print("\n[3] Running Validation...")

    validation_result = evidence.validate()
    print(f"  Validation Passed: {validation_result['passed']}")
    if not validation_result["passed"]:
        print(f"  Issues: {len(validation_result['issues'])}")
        for issue in validation_result["issues"][:3]:
            print(f"    - {issue}")

    print("\n[4] Running Defense Simulation...")

    # Run defense simulation before sealing - using the evidence method stores results
    defense_result = evidence.run_defense_simulation(simulator)

    print(f"  Score: {defense_result['score']}/100")
    print(f"  Passed: {defense_result['passed']}")

    if defense_result["blocking_failures"]:
        print(f"  Blocking Failures: {len(defense_result['blocking_failures'])}")
        for failure in defense_result["blocking_failures"]:
            print(f"    ✗ {failure['challenge_id']}: {failure['question']}")

    if defense_result["major_failures"]:
        print(f"  Major Failures: {len(defense_result['major_failures'])}")

    if defense_result["warnings"]:
        print(f"  Warnings: {len(defense_result['warnings'])}")

    print(f"\n  Recommendation: {defense_result['recommendation']}")

    print("\n[5] Sealing Evidence...")

    if defense_result["passed"]:
        content_hash = evidence.seal(private_key, collection.officer_id)
        print(f"  Evidence Sealed: {content_hash[:32]}...")

        # Record seal event
        custody.record_event(
            evidence_id=evidence.evidence_id,
            action=CustodyAction.SEALED,
            actor_id=collection.officer_id,
            actor_name=collection.officer_name,
            actor_agency=collection.agency,
            details={"content_hash": content_hash},
        )

        # Verify seal
        seal_valid = evidence.verify_seal(public_key)
        print(f"  Seal Valid: {seal_valid}")
    else:
        print("  ✗ Cannot seal - defense simulation failed")
        print("  Fix the blocking issues and try again")

    print("\n[6] Chain of Custody Summary...")

    chain = custody.get_chain(evidence.evidence_id)
    print(f"  Total Events: {len(chain)}")
    for event in chain:
        print(
            f"    {event.timestamp.strftime('%H:%M:%S')} - {event.action.value} by {event.actor_name}"
        )

    # Verify chain integrity
    verify_result = custody.verify_chain(evidence.evidence_id)
    print(f"  Chain Integrity: {'VALID' if verify_result['valid'] else 'BROKEN'}")

    print("\n[7] Export for Court...")

    if evidence.status.value == "sealed":
        export = evidence.export_for_court(collection.officer_id)

        print(f"  Exported: {export['exported_at']}")
        print(f"  Content Hash: {export['content_hash'][:32]}...")
        print(f"  Case Number: {export['case_number']}")

        # Record export
        custody.record_event(
            evidence_id=evidence.evidence_id,
            action=CustodyAction.EXPORTED,
            actor_id=collection.officer_id,
            actor_name=collection.officer_name,
            actor_agency=collection.agency,
            details={"purpose": "court_submission"},
        )

    print("\n[8] Final Statistics...")

    registry_stats = registry.get_statistics()
    print(f"  Registry Queries: {registry_stats['total_queries']}")
    print(f"  Registry Matches: {registry_stats['total_matches']}")

    custody_stats = custody.get_statistics()
    print(f"  Custody Events: {custody_stats['total_events']}")

    # Cleanup
    registry.close()
    custody.close()

    print("\n" + "=" * 60)
    print("Workflow Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
