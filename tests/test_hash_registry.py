"""
Tests for HashRegistry
"""


import pytest

from child_guardians.core.hash_registry import (
    HashRegistry,
    HashType,
    MatchConfidence,
    VictimStatus,
    compute_hash,
)


class TestHashRegistry:
    """Tests for HashRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create an in-memory registry for testing."""
        return HashRegistry(":memory:")

    @pytest.fixture
    def sample_hash(self):
        """Sample hash value for testing."""
        return "a" * 64  # Valid SHA-256 length

    def test_registry_initialization(self, registry):
        """Test that registry initializes correctly."""
        stats = registry.get_statistics()
        assert stats["total_hashes"] == 0
        assert stats["total_queries"] == 0

    def test_register_hash(self, registry, sample_hash):
        """Test registering a new hash."""
        success = registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
            category="csam_confirmed",
        )

        assert success is True

        stats = registry.get_statistics()
        assert stats["total_hashes"] == 1

    def test_duplicate_registration_fails(self, registry, sample_hash):
        """Test that duplicate registration fails."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        # Try to register same hash again
        success = registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.HIGH,
            victim_status=VictimStatus.UNIDENTIFIED,
            source_authority="NCMEC",
        )

        assert success is False

    def test_check_existing_hash(self, registry, sample_hash):
        """Test checking for an existing hash."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="Local PD",
            querying_officer="OFF-001",
        )

        assert result.found is True
        assert result.record.confidence == MatchConfidence.CONFIRMED
        assert result.record.victim_status == VictimStatus.IDENTIFIED

    def test_check_nonexistent_hash(self, registry):
        """Test checking for a non-existent hash."""
        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value="b" * 64,
            querying_agency="Local PD",
            querying_officer="OFF-001",
        )

        assert result.found is False
        assert result.record is None

    def test_hash_normalization(self, registry, sample_hash):
        """Test that hashes are normalized (lowercase, stripped)."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash.upper(),  # Register with uppercase
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        # Check with lowercase
        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash.lower(),
            querying_agency="Local PD",
            querying_officer="OFF-001",
        )

        assert result.found is True

    def test_batch_check(self, registry):
        """Test batch hash checking."""
        # Register some hashes
        for i in range(5):
            registry.register(
                hash_type=HashType.SHA256,
                hash_value=str(i) * 64,
                confidence=MatchConfidence.CONFIRMED,
                victim_status=VictimStatus.UNKNOWN,
                source_authority="FBI",
            )

        # Batch check - some exist, some don't
        hashes_to_check = [
            (HashType.SHA256, "0" * 64),  # exists
            (HashType.SHA256, "1" * 64),  # exists
            (HashType.SHA256, "9" * 64),  # doesn't exist
        ]

        results = registry.batch_check(
            hashes=hashes_to_check,
            querying_agency="Local PD",
            querying_officer="OFF-001",
        )

        assert len(results) == 3
        assert results[0].found is True
        assert results[1].found is True
        assert results[2].found is False

    def test_query_logging(self, registry, sample_hash):
        """Test that queries are logged."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        # Make some queries
        registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="Local PD",
            querying_officer="OFF-001",
            case_reference="CASE-001",
        )

        registry.check(
            hash_type=HashType.SHA256,
            hash_value="nonexistent" * 4,
            querying_agency="Local PD",
            querying_officer="OFF-002",
        )

        # Check query log
        log = registry.get_query_log()

        assert len(log) == 2
        assert log[0]["querying_agency"] == "Local PD"

    def test_query_log_filtering(self, registry, sample_hash):
        """Test query log filtering."""
        # Make queries from different agencies
        registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="FBI",
            querying_officer="OFF-001",
        )

        registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="Local PD",
            querying_officer="OFF-002",
        )

        # Filter by agency
        fbi_log = registry.get_query_log(agency="FBI")

        assert len(fbi_log) == 1
        assert fbi_log[0]["querying_agency"] == "FBI"

    def test_link_evidence_package(self, registry, sample_hash):
        """Test linking evidence packages to hashes."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        success = registry.link_evidence_package(sample_hash, "PKG-001")
        assert success is True

        # Check that package is linked
        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="FBI",
            querying_officer="OFF-001",
        )

        assert result.evidence_package_available is True
        assert result.evidence_package_id == "PKG-001"

    def test_jurisdiction_flags(self, registry, sample_hash):
        """Test jurisdiction flags on hashes."""
        registry.register(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
            jurisdictions=["US", "UK", "CA"],
        )

        result = registry.check(
            hash_type=HashType.SHA256,
            hash_value=sample_hash,
            querying_agency="FBI",
            querying_officer="OFF-001",
        )

        assert result.found is True
        assert "US" in result.jurisdiction_flags
        assert "UK" in result.jurisdiction_flags

    def test_statistics(self, registry):
        """Test statistics reporting."""
        # Register various hashes
        registry.register(
            hash_type=HashType.SHA256,
            hash_value="1" * 64,
            confidence=MatchConfidence.CONFIRMED,
            victim_status=VictimStatus.IDENTIFIED,
            source_authority="FBI",
        )

        registry.register(
            hash_type=HashType.SHA3_512,
            hash_value="2" * 128,
            confidence=MatchConfidence.HIGH,
            victim_status=VictimStatus.UNIDENTIFIED,
            source_authority="NCMEC",
        )

        # Make some queries
        registry.check(HashType.SHA256, "1" * 64, "FBI", "OFF-001")
        registry.check(HashType.SHA256, "nonexistent", "FBI", "OFF-001")

        stats = registry.get_statistics()

        assert stats["total_hashes"] == 2
        assert stats["total_queries"] == 2
        assert stats["total_matches"] == 1
        assert stats["match_rate"] == 0.5


class TestComputeHash:
    """Tests for hash computation functions."""

    def test_compute_sha256(self):
        """Test SHA-256 computation."""
        data = b"test data"
        hash_value = compute_hash(data, HashType.SHA256)

        assert len(hash_value) == 64  # SHA-256 is 32 bytes = 64 hex chars
        assert hash_value == "916f0027a575074ce72a331777c3478d6513f786a591bd892da1a577bf2335f9"

    def test_compute_sha3_512(self):
        """Test SHA3-512 computation."""
        data = b"test data"
        hash_value = compute_hash(data, HashType.SHA3_512)

        assert len(hash_value) == 128  # SHA3-512 is 64 bytes = 128 hex chars

    def test_perceptual_hash_not_implemented(self):
        """Test that perceptual hashes raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            compute_hash(b"test", HashType.PHOTODNA)

        with pytest.raises(NotImplementedError):
            compute_hash(b"test", HashType.PDQ)
