"""
Tests for Chain of Custody
"""


import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from child_guardians.core.chain_of_custody import (
    ChainOfCustody,
    CustodyAction,
    CustodyEvent,
)


class TestChainOfCustody:
    """Tests for ChainOfCustody class."""

    @pytest.fixture
    def custody(self):
        """Create an in-memory custody chain for testing."""
        return ChainOfCustody(":memory:")

    @pytest.fixture
    def signing_keys(self):
        """Generate signing keys for testing."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    def test_record_event(self, custody):
        """Test recording a custody event."""
        event = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        assert event.evidence_id == "EV-001"
        assert event.action == CustodyAction.CREATED
        assert event.previous_hash == ChainOfCustody.GENESIS_HASH

    def test_chain_linking(self, custody):
        """Test that events are properly chained."""
        # Create first event
        event1 = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        # Create second event
        event2 = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.ACCESSED,
            actor_id="OFF-002",
            actor_name="Jane Smith",
            actor_agency="FBI",
        )

        # Second event should link to first
        assert event2.previous_hash == event1.event_hash

    def test_get_chain(self, custody):
        """Test retrieving complete chain."""
        # Create multiple events
        for i in range(5):
            custody.record_event(
                evidence_id="EV-001",
                action=CustodyAction.ACCESSED,
                actor_id=f"OFF-{i:03d}",
                actor_name=f"Officer {i}",
                actor_agency="FBI",
            )

        chain = custody.get_chain("EV-001")

        assert len(chain) == 5
        # Check chronological order
        for i in range(1, len(chain)):
            assert chain[i].timestamp >= chain[i-1].timestamp

    def test_verify_valid_chain(self, custody):
        """Test verification of valid chain."""
        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.SEALED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        result = custody.verify_chain("EV-001")

        assert result["valid"] is True
        assert result["events_checked"] == 2
        assert len(result["issues"]) == 0

    def test_signed_events(self, custody, signing_keys):
        """Test event signing."""
        private_key, public_key = signing_keys

        event = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
            private_key=private_key,
        )

        assert event.signature is not None
        assert len(event.signature) > 0

    def test_verify_signatures(self, custody, signing_keys):
        """Test signature verification in chain verification."""
        private_key, public_key = signing_keys

        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
            private_key=private_key,
        )

        result = custody.verify_chain(
            "EV-001",
            public_keys={"OFF-001": public_key}
        )

        assert result["valid"] is True

    def test_event_details(self, custody):
        """Test recording event details."""
        details = {
            "file_hash": "abc123",
            "action_reason": "Routine verification",
        }

        event = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.ACCESSED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
            details=details,
        )

        assert event.details == details

    def test_get_events_by_actor(self, custody):
        """Test retrieving events by actor."""
        # Create events from different actors
        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        custody.record_event(
            evidence_id="EV-002",
            action=CustodyAction.CREATED,
            actor_id="OFF-002",
            actor_name="Jane Smith",
            actor_agency="Local PD",
        )

        custody.record_event(
            evidence_id="EV-003",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        events = custody.get_events_by_actor("OFF-001")

        assert len(events) == 2
        assert all(e.actor_id == "OFF-001" for e in events)

    def test_export_chain(self, custody):
        """Test chain export for court."""
        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.SEALED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
        )

        export = custody.export_chain("EV-001")

        assert export["evidence_id"] == "EV-001"
        assert export["chain_valid"] is True
        assert export["total_events"] == 2
        assert "events" in export
        assert "summary" in export

    def test_statistics(self, custody):
        """Test statistics collection."""
        # Create events across multiple evidence items
        for ev_id in ["EV-001", "EV-002", "EV-003"]:
            custody.record_event(
                evidence_id=ev_id,
                action=CustodyAction.CREATED,
                actor_id="OFF-001",
                actor_name="John Doe",
                actor_agency="FBI",
            )

        custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.SEALED,
            actor_id="OFF-002",
            actor_name="Jane Smith",
            actor_agency="Local PD",
        )

        stats = custody.get_statistics()

        assert stats["unique_evidence_items"] == 3
        assert stats["total_events"] == 4
        assert "created" in stats["events_by_action"]
        assert "FBI" in stats["events_by_agency"]

    def test_empty_chain_verification(self, custody):
        """Test verification of non-existent chain."""
        result = custody.verify_chain("NONEXISTENT")

        assert result["valid"] is False
        assert "No custody events found" in result["error"]

    def test_event_serialization(self, custody):
        """Test event serialization."""
        event = custody.record_event(
            evidence_id="EV-001",
            action=CustodyAction.CREATED,
            actor_id="OFF-001",
            actor_name="John Doe",
            actor_agency="FBI",
            details={"note": "Test"},
        )

        data = event.to_dict()
        restored = CustodyEvent.from_dict(data)

        assert restored.event_id == event.event_id
        assert restored.evidence_id == event.evidence_id
        assert restored.action == event.action
        assert restored.details == event.details


class TestCustodyAction:
    """Tests for CustodyAction enum."""

    def test_all_actions_exist(self):
        """Test that all expected actions exist."""
        expected_actions = [
            "CREATED", "ACCESSED", "MODIFIED", "HASH_ADDED",
            "VALIDATED", "SEALED", "EXPORTED", "TRANSFERRED", "ARCHIVED"
        ]

        for action in expected_actions:
            assert hasattr(CustodyAction, action)
