#!/usr/bin/env python3
"""
CHILD GUARDIANS - System Verification Script

This script verifies that the system is correctly installed and functioning.
Run this after installation to confirm everything works.

Usage:
    python scripts/verify_installation.py
"""

import sys
import traceback
from datetime import UTC, datetime, timedelta


def check_imports():
    """Verify all modules can be imported."""
    print("Checking imports...")

    try:
        from child_guardians import __version__
        print(f"  ✓ child_guardians v{__version__}")
    except ImportError as e:
        print(f"  ✗ Failed to import child_guardians: {e}")
        return False

    try:
        from child_guardians.core.evidence_object import EvidenceObject  # noqa: F401
        print("  ✓ EvidenceObject")
    except ImportError as e:
        print(f"  ✗ Failed to import EvidenceObject: {e}")
        return False

    try:
        from child_guardians.core.hash_registry import HashRegistry  # noqa: F401
        print("  ✓ HashRegistry")
    except ImportError as e:
        print(f"  ✗ Failed to import HashRegistry: {e}")
        return False

    try:
        from child_guardians.core.chain_of_custody import ChainOfCustody  # noqa: F401
        print("  ✓ ChainOfCustody")
    except ImportError as e:
        print(f"  ✗ Failed to import ChainOfCustody: {e}")
        return False

    try:
        from child_guardians.core.defense_simulator import DefenseSimulator  # noqa: F401
        print("  ✓ DefenseSimulator")
    except ImportError as e:
        print(f"  ✗ Failed to import DefenseSimulator: {e}")
        return False

    try:
        from child_guardians.api.main import app  # noqa: F401
        print("  ✓ FastAPI application")
    except ImportError as e:
        print(f"  ✗ Failed to import API: {e}")
        return False

    return True


def check_evidence_workflow():
    """Test complete evidence workflow."""
    print("\nTesting evidence workflow...")

    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        from child_guardians.core.defense_simulator import DefenseSimulator
        from child_guardians.core.evidence_object import (
            CollectionDetails,
            EvidenceObject,
            JurisdictionMap,
            LegalBasis,
            LegalBasisType,
            MaterialHash,
        )

        # Create evidence
        legal_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="TEST-WARRANT-001",
            issued_by="Test Judge",
            issued_date=datetime.now(UTC) - timedelta(days=1),
            scope="Test scope",
            expires=datetime.now(UTC) + timedelta(days=30),
        )

        collection = CollectionDetails(
            officer_id="TEST-001",
            officer_name="Test Officer",
            badge_number="12345",
            agency="Test Agency",
            agency_unit="Test Unit",
            collection_time=datetime.now(UTC),
            collection_location="Test Location",
            tool_used="Test Tool",
            tool_version="1.0",
            tool_hash="abc123",
        )

        jurisdiction = JurisdictionMap(
            primary_jurisdiction="US-TEST",
            hosting_country="US",
            can_export_evidence=["Test Agency"],
        )

        evidence = EvidenceObject(
            case_number="TEST-CASE-001",
            evidence_type="test",
            legal_basis=legal_basis,
            collection_details=collection,
            jurisdiction=jurisdiction,
        )
        print("  ✓ Evidence object created")

        # Add hash
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="a" * 64,
            source_file="test.jpg",
            source_path="/test/test.jpg",
            computed_by="TEST-001",
        )
        evidence.add_material_hash(material_hash)
        print("  ✓ Material hash added")

        # Validate
        result = evidence.validate()
        if result["passed"]:
            print("  ✓ Validation passed")
        else:
            print(f"  ⚠ Validation issues: {len(result['issues'])}")

        # Run defense simulation
        simulator = DefenseSimulator()
        sim_result = simulator.evaluate(evidence)
        print(f"  ✓ Defense simulation: score {sim_result['score']}/100")

        # Seal
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        content_hash = evidence.seal(private_key, "TEST-001")
        print(f"  ✓ Evidence sealed: {content_hash[:16]}...")

        # Verify seal
        if evidence.verify_seal(public_key):
            print("  ✓ Seal verified")
        else:
            print("  ✗ Seal verification failed")
            return False

        # Serialize/deserialize
        data = evidence.to_dict()
        restored = EvidenceObject.from_dict(data)
        if restored.evidence_id == evidence.evidence_id:
            print("  ✓ Serialization roundtrip")
        else:
            print("  ✗ Serialization failed")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Evidence workflow failed: {e}")
        traceback.print_exc()
        return False


def check_hash_registry():
    """Test hash registry functionality."""
    print("\nTesting hash registry...")

    try:
        from child_guardians.core.hash_registry import (
            HashRegistry,
            HashType,
            MatchConfidence,
            VictimStatus,
            compute_hash,
        )

        # Create in-memory registry
        registry = HashRegistry(":memory:")
        print("  ✓ Registry created")

        # Register hash
        test_hash = "b" * 64
        success = registry.register(
            hash_type=HashType.SHA256,
            hash_value=test_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="Test",
        )
        if success:
            print("  ✓ Hash registered")
        else:
            print("  ✗ Registration failed")
            return False

        # Check hash
        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value=test_hash,
            querying_agency="Test",
            querying_officer="TEST-001",
        )
        if result.found:
            print("  ✓ Hash lookup works")
        else:
            print("  ✗ Hash lookup failed")
            return False

        # Test compute_hash
        data_hash = compute_hash(b"test data", HashType.SHA256)
        if len(data_hash) == 64:
            print("  ✓ Hash computation works")
        else:
            print("  ✗ Hash computation failed")
            return False

        # Statistics
        stats = registry.get_statistics()
        if stats["total_hashes"] == 1:
            print("  ✓ Statistics work")
        else:
            print("  ✗ Statistics incorrect")
            return False

        registry.close()
        return True

    except Exception as e:
        print(f"  ✗ Hash registry test failed: {e}")
        traceback.print_exc()
        return False


def check_chain_of_custody():
    """Test chain of custody functionality."""
    print("\nTesting chain of custody...")

    try:
        from child_guardians.core.chain_of_custody import (
            ChainOfCustody,
            CustodyAction,
        )

        # Create in-memory custody chain
        custody = ChainOfCustody(":memory:")
        print("  ✓ Custody chain created")

        # Record events
        event1 = custody.record_event(
            evidence_id="TEST-EV-001",
            action=CustodyAction.CREATED,
            actor_id="TEST-001",
            actor_name="Test Officer",
            actor_agency="Test Agency",
        )
        print("  ✓ Event recorded")

        event2 = custody.record_event(
            evidence_id="TEST-EV-001",
            action=CustodyAction.SEALED,
            actor_id="TEST-001",
            actor_name="Test Officer",
            actor_agency="Test Agency",
        )

        # Verify chain
        if event2.previous_hash == event1.event_hash:
            print("  ✓ Chain linking works")
        else:
            print("  ✗ Chain linking failed")
            return False

        # Get chain
        chain = custody.get_chain("TEST-EV-001")
        if len(chain) == 2:
            print("  ✓ Chain retrieval works")
        else:
            print("  ✗ Chain retrieval failed")
            return False

        # Verify chain integrity
        result = custody.verify_chain("TEST-EV-001")
        if result["valid"]:
            print("  ✓ Chain verification works")
        else:
            print("  ✗ Chain verification failed")
            return False

        # Export
        export = custody.export_chain("TEST-EV-001")
        if export["total_events"] == 2:
            print("  ✓ Chain export works")
        else:
            print("  ✗ Chain export failed")
            return False

        custody.close()
        return True

    except Exception as e:
        print(f"  ✗ Chain of custody test failed: {e}")
        traceback.print_exc()
        return False


def check_defense_simulator():
    """Test defense simulator functionality."""
    print("\nTesting defense simulator...")

    try:
        from child_guardians.core.defense_simulator import (
            ChallengeCategory,
            DefenseSimulator,
        )

        simulator = DefenseSimulator()

        # Check challenge count
        if len(simulator.challenges) == 35:
            print("  ✓ All 35 challenges registered")
        else:
            print(f"  ✗ Expected 35 challenges, got {len(simulator.challenges)}")
            return False

        # Check all categories covered
        categories = {c.category for c in simulator.challenges}
        if len(categories) == 7:
            print("  ✓ All 7 categories covered")
        else:
            print(f"  ✗ Expected 7 categories, got {len(categories)}")
            return False

        # Each category should have 5 challenges
        for cat in ChallengeCategory:
            count = len([c for c in simulator.challenges if c.category == cat])
            if count != 5:
                print(f"  ✗ {cat.value} has {count} challenges, expected 5")
                return False
        print("  ✓ Each category has 5 challenges")

        return True

    except Exception as e:
        print(f"  ✗ Defense simulator test failed: {e}")
        traceback.print_exc()
        return False


def check_api():
    """Test API can be loaded."""
    print("\nTesting API...")

    try:
        from fastapi.testclient import TestClient

        from child_guardians.api.main import app

        client = TestClient(app)

        # Health check
        response = client.get("/health")
        if response.status_code == 200:
            print("  ✓ Health endpoint works")
        else:
            print(f"  ✗ Health check failed: {response.status_code}")
            return False

        # Readiness check - may be 503 if database not configured (expected)
        response = client.get("/ready")
        if response.status_code == 200:
            print("  ✓ Ready endpoint works (database configured)")
        elif response.status_code == 503:
            print("  ✓ Ready endpoint works (database not configured - expected)")
        else:
            print(f"  ✗ Ready check failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("CHILD GUARDIANS - Installation Verification")
    print("=" * 60)

    results = {
        "imports": check_imports(),
        "evidence_workflow": check_evidence_workflow(),
        "hash_registry": check_hash_registry(),
        "chain_of_custody": check_chain_of_custody(),
        "defense_simulator": check_defense_simulator(),
        "api": check_api(),
    }

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {check}: {status}")

    print()
    if all_passed:
        print("All checks passed! ✓")
        print("CHILD GUARDIANS is ready for use.")
        sys.exit(0)
    else:
        print("Some checks failed. ✗")
        print("Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
