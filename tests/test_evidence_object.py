"""
Tests for EvidenceObject
"""

from datetime import UTC, datetime, timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from child_guardians.core.defense_simulator import DefenseSimulator
from child_guardians.core.evidence_object import (
    CollectionDetails,
    EvidenceObject,
    EvidenceStatus,
    JurisdictionMap,
    LegalBasis,
    LegalBasisType,
    MaterialHash,
)


class TestEvidenceObject:
    """Tests for EvidenceObject class."""

    @pytest.fixture
    def valid_legal_basis(self):
        """Create a valid legal basis for testing."""
        return LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="2024-WARRANT-12345",
            issued_by="Judge Smith",
            issued_date=datetime.now(UTC) - timedelta(days=1),
            scope="Digital devices at 123 Main St",
            expires=datetime.now(UTC) + timedelta(days=30),
        )

    @pytest.fixture
    def valid_collection_details(self):
        """Create valid collection details for testing."""
        return CollectionDetails(
            officer_id="OFF-001",
            officer_name="John Doe",
            badge_number="12345",
            agency="FBI",
            agency_unit="Cyber Division",
            collection_time=datetime.now(UTC),
            collection_location="123 Main St, Anytown, USA",
            tool_used="FTK Imager",
            tool_version="4.7.1",
            tool_hash="abc123def456",
            witness_present=True,
            witness_name="Jane Smith",
        )

    @pytest.fixture
    def valid_jurisdiction(self):
        """Create valid jurisdiction map for testing."""
        return JurisdictionMap(
            primary_jurisdiction="US-VA",
            hosting_country="US",
            victim_country="US",
            can_view_metadata=["FBI", "NCMEC"],
            can_view_hashes=["FBI", "NCMEC", "INTERPOL"],
            can_export_evidence=["FBI"],
            can_initiate_prosecution=["FBI"],
        )

    @pytest.fixture
    def evidence_object(self, valid_legal_basis, valid_collection_details, valid_jurisdiction):
        """Create a basic evidence object for testing."""
        return EvidenceObject(
            case_number="CASE-2024-001",
            evidence_type="digital_image",
            legal_basis=valid_legal_basis,
            collection_details=valid_collection_details,
            jurisdiction=valid_jurisdiction,
        )

    def test_evidence_creation(self, evidence_object):
        """Test basic evidence object creation."""
        assert evidence_object.evidence_id is not None
        assert evidence_object.case_number == "CASE-2024-001"
        assert evidence_object.status == EvidenceStatus.DRAFT
        assert len(evidence_object.chain_of_custody) == 1  # Creation event

    def test_add_material_hash(self, evidence_object):
        """Test adding material hashes to evidence."""
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )

        evidence_object.add_material_hash(material_hash)

        assert len(evidence_object.material_hashes) == 1
        assert evidence_object.material_hashes[0].hash_value == material_hash.hash_value

    def test_cannot_modify_sealed_evidence(self, evidence_object):
        """Test that sealed evidence cannot be modified."""
        # Add hash and validate
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)
        evidence_object.validate()

        # Seal the evidence
        private_key = ed25519.Ed25519PrivateKey.generate()
        evidence_object.seal(private_key, "OFF-001")

        # Try to add another hash
        with pytest.raises(ValueError, match="Cannot modify sealed evidence"):
            evidence_object.add_material_hash(material_hash)

    def test_validation_fails_without_hashes(self, evidence_object):
        """Test that validation fails without material hashes."""
        result = evidence_object.validate()

        assert result["passed"] is False
        assert any(issue["code"] == "MATERIAL-001" for issue in result["issues"])

    def test_validation_passes_with_valid_data(self, evidence_object):
        """Test that validation passes with complete data."""
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)

        result = evidence_object.validate()

        assert result["passed"] is True
        assert evidence_object.status == EvidenceStatus.VALIDATED

    def test_seal_and_verify(self, evidence_object):
        """Test sealing and verification of evidence."""
        # Setup
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)
        evidence_object.validate()

        # Generate keys
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Seal
        content_hash = evidence_object.seal(private_key, "OFF-001")

        assert evidence_object.status == EvidenceStatus.SEALED
        assert content_hash is not None
        assert len(content_hash) == 128  # SHA3-512 hex

        # Verify
        assert evidence_object.verify_seal(public_key) is True

    def test_verification_fails_with_wrong_key(self, evidence_object):
        """Test that verification fails with wrong public key."""
        # Setup
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)
        evidence_object.validate()

        # Seal with one key
        private_key1 = ed25519.Ed25519PrivateKey.generate()
        evidence_object.seal(private_key1, "OFF-001")

        # Try to verify with different key
        private_key2 = ed25519.Ed25519PrivateKey.generate()
        public_key2 = private_key2.public_key()

        assert evidence_object.verify_seal(public_key2) is False

    def test_defense_simulation(self, evidence_object):
        """Test defense attorney simulation."""
        # Setup
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)
        evidence_object.validate()

        # Run simulation
        simulator = DefenseSimulator()
        result = evidence_object.run_defense_simulation(simulator)

        assert "passed" in result
        assert "score" in result
        assert "blocking_failures" in result
        assert "recommendation" in result

    def test_serialization_roundtrip(self, evidence_object):
        """Test that evidence can be serialized and deserialized."""
        # Add some data
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence_object.add_material_hash(material_hash)

        # Serialize
        data = evidence_object.to_dict()

        # Deserialize
        restored = EvidenceObject.from_dict(data)

        assert restored.evidence_id == evidence_object.evidence_id
        assert restored.case_number == evidence_object.case_number
        assert len(restored.material_hashes) == len(evidence_object.material_hashes)

    def test_custody_gap_detection(self, evidence_object):
        """Test detection of custody gaps."""
        # Manually create a gap
        evidence_object.chain_of_custody.append({
            "timestamp": (datetime.now(UTC) + timedelta(hours=48)).isoformat(),
            "action": "accessed",
            "actor": "OFF-002",
        })

        gaps = evidence_object._check_custody_gaps()

        assert len(gaps) >= 1
        assert any(g["duration"] > 12 for g in gaps)


class TestLegalBasis:
    """Tests for LegalBasis class."""

    def test_expired_warrant_detection(self):
        """Test that expired warrants are detected."""
        expired_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="2024-WARRANT-EXPIRED",
            issued_by="Judge Expired",
            issued_date=datetime.now(UTC) - timedelta(days=60),
            scope="Test scope",
            expires=datetime.now(UTC) - timedelta(days=30),
        )

        collection = CollectionDetails(
            officer_id="OFF-001",
            officer_name="Test Officer",
            badge_number="12345",
            agency="FBI",
            agency_unit="Test",
            collection_time=datetime.now(UTC),
            collection_location="Test Location",
            tool_used="Test Tool",
            tool_version="1.0",
            tool_hash="abc123",
        )

        jurisdiction = JurisdictionMap(
            primary_jurisdiction="US-VA",
            hosting_country="US",
        )

        evidence = EvidenceObject(
            case_number="CASE-EXPIRED",
            evidence_type="test",
            legal_basis=expired_basis,
            collection_details=collection,
            jurisdiction=jurisdiction,
        )

        # Add hash to pass that check
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123" * 10,
            source_file="test.jpg",
            source_path="/test",
            computed_by="OFF-001",
        )
        evidence.add_material_hash(material_hash)

        result = evidence.validate()

        assert result["passed"] is False
        assert any(issue["code"] == "LEGAL-002" for issue in result["issues"])


class TestMaterialHash:
    """Tests for MaterialHash class."""

    def test_hash_serialization(self):
        """Test hash serialization."""
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )

        data = material_hash.to_dict()
        restored = MaterialHash.from_dict(data)

        assert restored.hash_type == material_hash.hash_type
        assert restored.hash_value == material_hash.hash_value
        assert restored.source_file == material_hash.source_file
