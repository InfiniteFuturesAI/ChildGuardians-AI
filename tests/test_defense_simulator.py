"""
Tests for Defense Attorney Simulator
"""

from datetime import UTC, datetime, timedelta

import pytest

from child_guardians.core.defense_simulator import (
    ChallengeCategory,
    DefenseSimulator,
)
from child_guardians.core.evidence_object import (
    CollectionDetails,
    EvidenceObject,
    JurisdictionMap,
    LegalBasis,
    LegalBasisType,
    MaterialHash,
)


class TestDefenseSimulator:
    """Tests for DefenseSimulator class."""

    @pytest.fixture
    def simulator(self):
        """Create a simulator for testing."""
        return DefenseSimulator()

    @pytest.fixture
    def complete_evidence(self):
        """Create a complete, valid evidence object."""
        legal_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="2024-WARRANT-12345",
            issued_by="Judge Smith",
            issued_date=datetime.now(UTC) - timedelta(days=1),
            scope="Digital devices at 123 Main St",
            expires=datetime.now(UTC) + timedelta(days=30),
        )

        collection_details = CollectionDetails(
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

        jurisdiction = JurisdictionMap(
            primary_jurisdiction="US-VA",
            hosting_country="US",
            victim_country="US",
            can_view_metadata=["FBI", "NCMEC"],
            can_view_hashes=["FBI", "NCMEC", "INTERPOL"],
            can_export_evidence=["FBI"],
            can_initiate_prosecution=["FBI"],
        )

        evidence = EvidenceObject(
            case_number="CASE-2024-001",
            evidence_type="digital_image",
            legal_basis=legal_basis,
            collection_details=collection_details,
            jurisdiction=jurisdiction,
        )

        # Add material hash
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence.add_material_hash(material_hash)
        evidence.validate()

        return evidence

    @pytest.fixture
    def incomplete_evidence(self):
        """Create an incomplete evidence object."""
        legal_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="",  # Missing reference!
            issued_by="",  # Missing issuer!
            issued_date=datetime.now(UTC) - timedelta(days=1),
            scope="",  # Missing scope!
        )

        collection_details = CollectionDetails(
            officer_id="OFF-001",
            officer_name="John Doe",
            badge_number="12345",
            agency="FBI",
            agency_unit="Cyber Division",
            collection_time=datetime.now(UTC),
            collection_location="",  # Missing location!
            tool_used="",  # Missing tool!
            tool_version="",
            tool_hash="",  # Missing tool hash!
        )

        jurisdiction = JurisdictionMap(
            primary_jurisdiction="",  # Missing jurisdiction!
            hosting_country="US",
        )

        evidence = EvidenceObject(
            case_number="CASE-2024-002",
            evidence_type="digital_image",
            legal_basis=legal_basis,
            collection_details=collection_details,
            jurisdiction=jurisdiction,
        )

        # Add hash but don't validate (so it stays in draft)
        material_hash = MaterialHash(
            hash_type="sha256",
            hash_value="abc123def456" * 4,
            source_file="image001.jpg",
            source_path="/evidence/seized/image001.jpg",
            computed_by="OFF-001",
        )
        evidence.add_material_hash(material_hash)
        # Force status to validated for simulation
        from child_guardians.core.evidence_object import EvidenceStatus
        evidence.status = EvidenceStatus.VALIDATED

        return evidence

    def test_simulator_has_35_challenges(self, simulator):
        """Test that simulator has all 35 challenges."""
        assert len(simulator.challenges) == 35

    def test_all_categories_covered(self, simulator):
        """Test that all challenge categories are covered."""
        categories = {c.category for c in simulator.challenges}

        expected_categories = {
            ChallengeCategory.LAWFUL_COLLECTION,
            ChallengeCategory.AUTHENTICATION,
            ChallengeCategory.CHAIN_OF_CUSTODY,
            ChallengeCategory.JURISDICTION,
            ChallengeCategory.DISCLOSURE,
            ChallengeCategory.FOUNDATION,
            ChallengeCategory.TIMELINESS,
        }

        assert categories == expected_categories

    def test_complete_evidence_passes(self, simulator, complete_evidence):
        """Test that complete evidence passes simulation."""
        result = simulator.evaluate(complete_evidence)

        assert result["passed"] is True
        assert result["score"] >= 70  # Should score well
        assert len(result["blocking_failures"]) == 0

    def test_incomplete_evidence_fails(self, simulator, incomplete_evidence):
        """Test that incomplete evidence fails simulation."""
        result = simulator.evaluate(incomplete_evidence)

        # Should have critical failures
        assert len(result["blocking_failures"]) > 0 or len(result["major_failures"]) > 2
        assert result["passed"] is False

    def test_result_structure(self, simulator, complete_evidence):
        """Test that result has expected structure."""
        result = simulator.evaluate(complete_evidence)

        required_keys = [
            "passed", "score", "evaluated_at", "total_challenges",
            "blocking_failures", "major_failures", "warnings",
            "results_by_category", "category_scores", "recommendation"
        ]

        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_category_scores(self, simulator, complete_evidence):
        """Test that category scores are computed."""
        result = simulator.evaluate(complete_evidence)

        category_scores = result["category_scores"]

        for category in ChallengeCategory:
            assert category.value in category_scores
            assert "score" in category_scores[category.value]
            assert "status" in category_scores[category.value]

    def test_recommendation_generated(self, simulator, complete_evidence, incomplete_evidence):
        """Test that appropriate recommendations are generated."""
        good_result = simulator.evaluate(complete_evidence)
        bad_result = simulator.evaluate(incomplete_evidence)

        # Good evidence should get positive recommendation
        assert "ready" in good_result["recommendation"].lower() or "may be exported" in good_result["recommendation"].lower()

        # Bad evidence should get blocking recommendation
        assert "BLOCKED" in bad_result["recommendation"] or "resolve" in bad_result["recommendation"].lower()

    def test_severity_levels(self, simulator):
        """Test that challenges have proper severity levels."""
        valid_severities = {"critical", "major", "minor"}

        for challenge in simulator.challenges:
            assert challenge.severity in valid_severities, f"Invalid severity for {challenge.id}"

    def test_challenge_id_format(self, simulator):
        """Test that challenge IDs follow expected format."""
        # IDs should be like LC-001, AU-002, etc.
        import re
        pattern = r"^[A-Z]{2,3}-\d{3}$"

        for challenge in simulator.challenges:
            assert re.match(pattern, challenge.id), f"Invalid ID format: {challenge.id}"

    def test_score_calculation(self, simulator, complete_evidence):
        """Test that score is between 0 and 100."""
        result = simulator.evaluate(complete_evidence)

        assert 0 <= result["score"] <= 100


class TestChallengeCategories:
    """Tests for specific challenge categories."""

    @pytest.fixture
    def simulator(self):
        return DefenseSimulator()

    def test_lawful_collection_challenges(self, simulator):
        """Test that lawful collection category has 5 challenges."""
        lc_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.LAWFUL_COLLECTION
        ]
        assert len(lc_challenges) == 5

    def test_authentication_challenges(self, simulator):
        """Test that authentication category has 5 challenges."""
        auth_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.AUTHENTICATION
        ]
        assert len(auth_challenges) == 5

    def test_chain_of_custody_challenges(self, simulator):
        """Test that chain of custody category has 5 challenges."""
        coc_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.CHAIN_OF_CUSTODY
        ]
        assert len(coc_challenges) == 5

    def test_jurisdiction_challenges(self, simulator):
        """Test that jurisdiction category has 5 challenges."""
        jur_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.JURISDICTION
        ]
        assert len(jur_challenges) == 5

    def test_disclosure_challenges(self, simulator):
        """Test that disclosure category has 5 challenges."""
        dis_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.DISCLOSURE
        ]
        assert len(dis_challenges) == 5

    def test_foundation_challenges(self, simulator):
        """Test that foundation category has 5 challenges."""
        fnd_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.FOUNDATION
        ]
        assert len(fnd_challenges) == 5

    def test_timeliness_challenges(self, simulator):
        """Test that timeliness category has 5 challenges."""
        tim_challenges = [
            c for c in simulator.challenges
            if c.category == ChallengeCategory.TIMELINESS
        ]
        assert len(tim_challenges) == 5
