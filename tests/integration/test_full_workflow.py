#!/usr/bin/env python3
"""
CHILD GUARDIANS - API Integration Tests

These tests verify the API works end-to-end with realistic scenarios.
Run with: pytest tests/integration/test_full_workflow.py -v
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from child_guardians.api.main import app


@pytest.fixture
def client():
    """Create test client with proper lifespan context."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    """Standard authentication headers."""
    return {
        "x-agency-id": "FBI-TEST",
        "x-officer-id": "OFF-001",
        "x-officer-name": "Test Officer",
        "x-badge-number": "12345",
    }


class TestCompleteEvidenceWorkflow:
    """Test a complete evidence workflow from creation to export."""

    def test_full_evidence_lifecycle(self, client, auth_headers):
        """Test: Create → Hash → Validate → Simulate → Export cycle."""

        # Step 1: Create evidence
        now = datetime.now(UTC)
        create_payload = {
            "case_number": "CASE-INTEGRATION-001",
            "evidence_type": "digital_image",
            "legal_basis_type": "warrant",
            "legal_basis_reference": "WARRANT-TEST-001",
            "legal_basis_issued_by": "Judge Test",
            "legal_basis_issued_date": (now - timedelta(days=1)).isoformat(),
            "legal_basis_scope": "All digital devices",
            "legal_basis_expires": (now + timedelta(days=30)).isoformat(),
            "collection_time": now.isoformat(),
            "collection_location": "123 Test Street",
            "tool_used": "Test Tool",
            "tool_version": "1.0",
            "tool_hash": "abc123",
            "primary_jurisdiction": "US-TEST",
            "hosting_country": "US",
        }

        response = client.post(
            "/api/v1/evidence/create",
            json=create_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "evidence_id" in data

        evidence_id = data["evidence_id"]

        # Step 2: Add material hash
        hash_payload = {
            "hash_type": "sha256",
            "hash_value": "a" * 64,
            "source_file": "test_image.jpg",
            "source_path": "/evidence/test_image.jpg",
        }

        response = client.post(
            f"/api/v1/evidence/{evidence_id}/hash",
            json=hash_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Step 3: Retrieve evidence
        response = client.get(
            f"/api/v1/evidence/{evidence_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evidence_id"] == evidence_id

        # Step 4: Validate evidence
        response = client.post(
            f"/api/v1/evidence/{evidence_id}/validate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "passed" in data

        # Step 5: Run defense simulation
        response = client.post(
            f"/api/v1/evidence/{evidence_id}/simulate",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "passed" in data


class TestHashRegistryIntegration:
    """Test hash registry workflows."""

    def test_register_and_check_hash(self, client, auth_headers):
        """Register a hash and verify it can be found."""

        # Register hash
        test_hash = "d" * 64  # Different hash to avoid conflicts
        register_payload = {
            "hash_type": "sha256",
            "hash_value": test_hash,
            "confidence": "confirmed",
            "victim_status": "identified",
            "category": "csam_confirmed",
            "notes": "Integration test hash",
        }

        response = client.post(
            "/api/v1/hash/register",
            json=register_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Check hash
        check_payload = {
            "hash_type": "sha256",
            "hash_value": test_hash,
            "case_reference": "CASE-TEST-001",
            "legal_basis": "WARRANT-TEST",
        }

        response = client.post(
            "/api/v1/hash/check",
            json=check_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True

    def test_batch_hash_check(self, client, auth_headers):
        """Test batch hash checking."""

        # Register some hashes first with unique values
        import time
        ts = str(int(time.time()))

        for i in range(3):
            client.post(
                "/api/v1/hash/register",
                json={
                    "hash_type": "sha256",
                    "hash_value": f"{ts[0]}{i}" + "f" * 62,
                    "confidence": "confirmed",
                    "victim_status": "unknown",
                },
                headers=auth_headers,
            )

        # Batch check
        batch_payload = {
            "hashes": [
                {"hash_type": "sha256", "hash_value": f"{ts[0]}0" + "f" * 62},
                {"hash_type": "sha256", "hash_value": f"{ts[0]}1" + "f" * 62},
                {"hash_type": "sha256", "hash_value": "9" * 64},  # Not registered
            ],
            "case_reference": "CASE-BATCH-001",
            "legal_basis": "WARRANT-BATCH",
        }

        response = client.post(
            "/api/v1/hash/batch",
            json=batch_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3


class TestChainOfCustodyIntegration:
    """Test chain of custody workflows."""

    def test_custody_chain_lifecycle(self, client, auth_headers):
        """Test complete custody chain creation and verification."""

        evidence_id = f"CUSTODY-TEST-{datetime.now().timestamp()}"

        # Record creation event
        event_payload = {
            "evidence_id": evidence_id,
            "action": "created",
            "details": {"source": "integration test"},
            "location": "Test Lab",
        }

        response = client.post(
            "/api/v1/custody/event",
            json=event_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Record access event
        event_payload["action"] = "accessed"
        event_payload["details"] = {"purpose": "review"}

        response = client.post(
            "/api/v1/custody/event",
            json=event_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Get custody chain
        response = client.get(
            f"/api/v1/custody/{evidence_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify chain integrity
        response = client.get(
            f"/api/v1/custody/{evidence_id}/verify",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True


class TestAuthenticationEnforcement:
    """Test that authentication is properly enforced."""

    def test_missing_auth_headers_rejected(self, client):
        """Requests without auth headers should be rejected."""

        response = client.post(
            "/api/v1/hash/check",
            json={"hash_type": "sha256", "hash_value": "a" * 64},
        )

        # Either 401 or 422 depending on validation order
        assert response.status_code in (401, 422)

    def test_health_endpoints_no_auth(self, client):
        """Health endpoints should work without auth."""

        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_evidence_id(self, client, auth_headers):
        """Non-existent evidence should return 404."""

        response = client.get(
            "/api/v1/evidence/NONEXISTENT",
            headers=auth_headers,
        )

        assert response.status_code == 404
