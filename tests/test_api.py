"""
Tests for the REST API
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from child_guardians.api.main import app


@pytest.fixture(scope="module")
def client_with_lifespan():
    """Create test client with proper lifespan context."""
    # Use context manager to properly trigger lifespan events
    with TestClient(app) as client:
        yield client


class TestAPI:
    """Tests for the REST API."""

    @pytest.fixture
    def client(self):
        """Create test client with lifespan."""
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def auth_headers(self):
        """Standard auth headers for testing."""
        return {
            "x-agency-id": "FBI-TEST",
            "x-officer-id": "OFF-001",
            "x-officer-name": "Test Officer",
            "x-badge-number": "12345",
        }

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_hash_check_not_found(self, client, auth_headers):
        """Test hash check for non-existent hash."""
        response = client.post(
            "/api/v1/hash/check",
            json={
                "hash_type": "sha256",
                "hash_value": "a" * 64,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["found"] is False

    def test_hash_register_and_check(self, client, auth_headers):
        """Test registering and then checking a hash."""
        test_hash = "b" * 64

        # Register hash
        register_response = client.post(
            "/api/v1/hash/register",
            json={
                "hash_type": "sha256",
                "hash_value": test_hash,
                "confidence": "confirmed",
                "victim_status": "identified",
                "category": "csam_confirmed",
            },
            headers=auth_headers,
        )

        assert register_response.status_code == 200
        assert register_response.json()["registered"] is True

        # Check hash
        check_response = client.post(
            "/api/v1/hash/check",
            json={
                "hash_type": "sha256",
                "hash_value": test_hash,
            },
            headers=auth_headers,
        )

        assert check_response.status_code == 200
        data = check_response.json()
        assert data["found"] is True
        assert data["confidence"] == "confirmed"

    def test_batch_hash_check(self, client, auth_headers):
        """Test batch hash checking."""
        response = client.post(
            "/api/v1/hash/batch",
            json={
                "hashes": [
                    {"hash_type": "sha256", "hash_value": "1" * 64},
                    {"hash_type": "sha256", "hash_value": "2" * 64},
                    {"hash_type": "sha256", "hash_value": "3" * 64},
                ],
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["results"]) == 3

    def test_hash_statistics(self, client, auth_headers):
        """Test statistics endpoint."""
        response = client.get(
            "/api/v1/hash/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_hashes" in data
        assert "total_queries" in data

    def test_create_evidence(self, client, auth_headers):
        """Test evidence creation."""
        response = client.post(
            "/api/v1/evidence/create",
            json={
                "case_number": "CASE-2024-API-001",
                "evidence_type": "digital_image",
                "legal_basis_type": "warrant",
                "legal_basis_reference": "WARRANT-2024-001",
                "legal_basis_issued_by": "Judge Test",
                "legal_basis_issued_date": datetime.now(UTC).isoformat(),
                "legal_basis_scope": "Test scope",
                "collection_location": "Test Location",
                "tool_used": "Test Tool",
                "tool_version": "1.0",
                "primary_jurisdiction": "US-VA",
                "hosting_country": "US",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "evidence_id" in data
        assert data["case_number"] == "CASE-2024-API-001"
        assert data["status"] == "draft"

    def test_get_evidence(self, client, auth_headers):
        """Test retrieving evidence."""
        # Create evidence first
        create_response = client.post(
            "/api/v1/evidence/create",
            json={
                "case_number": "CASE-2024-API-002",
                "evidence_type": "digital_image",
                "legal_basis_type": "warrant",
                "legal_basis_reference": "WARRANT-2024-002",
                "legal_basis_issued_by": "Judge Test",
                "legal_basis_issued_date": datetime.now(UTC).isoformat(),
                "legal_basis_scope": "Test scope",
                "collection_location": "Test Location",
                "tool_used": "Test Tool",
                "tool_version": "1.0",
                "primary_jurisdiction": "US-VA",
                "hosting_country": "US",
            },
            headers=auth_headers,
        )

        evidence_id = create_response.json()["evidence_id"]

        # Get evidence
        get_response = client.get(
            f"/api/v1/evidence/{evidence_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["evidence_id"] == evidence_id

    def test_evidence_not_found(self, client, auth_headers):
        """Test 404 for non-existent evidence."""
        response = client.get(
            "/api/v1/evidence/nonexistent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_add_evidence_hash(self, client, auth_headers):
        """Test adding hash to evidence."""
        # Create evidence
        create_response = client.post(
            "/api/v1/evidence/create",
            json={
                "case_number": "CASE-2024-API-003",
                "evidence_type": "digital_image",
                "legal_basis_type": "warrant",
                "legal_basis_reference": "WARRANT-2024-003",
                "legal_basis_issued_by": "Judge Test",
                "legal_basis_issued_date": datetime.now(UTC).isoformat(),
                "legal_basis_scope": "Test scope",
                "collection_location": "Test Location",
                "tool_used": "Test Tool",
                "tool_version": "1.0",
                "primary_jurisdiction": "US-VA",
                "hosting_country": "US",
            },
            headers=auth_headers,
        )

        evidence_id = create_response.json()["evidence_id"]

        # Add hash
        hash_response = client.post(
            f"/api/v1/evidence/{evidence_id}/hash",
            json={
                "hash_type": "sha256",
                "hash_value": "c" * 64,
                "source_file": "test.jpg",
                "source_path": "/evidence/test.jpg",
            },
            headers=auth_headers,
        )

        assert hash_response.status_code == 200
        assert hash_response.json()["added"] is True

    def test_validate_evidence(self, client, auth_headers):
        """Test evidence validation."""
        # Create evidence with hash
        create_response = client.post(
            "/api/v1/evidence/create",
            json={
                "case_number": "CASE-2024-API-004",
                "evidence_type": "digital_image",
                "legal_basis_type": "warrant",
                "legal_basis_reference": "WARRANT-2024-004",
                "legal_basis_issued_by": "Judge Test",
                "legal_basis_issued_date": datetime.now(UTC).isoformat(),
                "legal_basis_scope": "Test scope",
                "collection_location": "Test Location",
                "tool_used": "Test Tool",
                "tool_version": "1.0",
                "primary_jurisdiction": "US-VA",
                "hosting_country": "US",
            },
            headers=auth_headers,
        )

        evidence_id = create_response.json()["evidence_id"]

        # Add hash
        client.post(
            f"/api/v1/evidence/{evidence_id}/hash",
            json={
                "hash_type": "sha256",
                "hash_value": "d" * 64,
                "source_file": "test.jpg",
                "source_path": "/evidence/test.jpg",
            },
            headers=auth_headers,
        )

        # Validate
        validate_response = client.post(
            f"/api/v1/evidence/{evidence_id}/validate",
            headers=auth_headers,
        )

        assert validate_response.status_code == 200
        data = validate_response.json()
        assert "passed" in data

    def test_custody_chain(self, client, auth_headers):
        """Test custody chain endpoints."""
        # Record event
        event_response = client.post(
            "/api/v1/custody/event",
            json={
                "evidence_id": "EV-API-001",
                "action": "created",
            },
            headers=auth_headers,
        )

        assert event_response.status_code == 200

        # Get chain
        chain_response = client.get(
            "/api/v1/custody/EV-API-001",
            headers=auth_headers,
        )

        assert chain_response.status_code == 200
        data = chain_response.json()
        assert len(data["events"]) >= 1

    def test_custody_verification(self, client, auth_headers):
        """Test custody chain verification."""
        # Create some events
        client.post(
            "/api/v1/custody/event",
            json={
                "evidence_id": "EV-API-002",
                "action": "created",
            },
            headers=auth_headers,
        )

        # Verify
        verify_response = client.get(
            "/api/v1/custody/EV-API-002/verify",
            headers=auth_headers,
        )

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert "valid" in data

    def test_missing_auth_headers(self, client):
        """Test that requests without auth headers fail."""
        response = client.post(
            "/api/v1/hash/check",
            json={
                "hash_type": "sha256",
                "hash_value": "a" * 64,
            },
        )

        assert response.status_code == 422  # Validation error for missing headers

    def test_cors_middleware_absent_with_empty_origins(self, client):
        """Default config has no CORS origins; preflight should not return CORS headers."""
        response = client.options(
            "/health",
            headers={
                "Origin": "https://attacker.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in {k.lower() for k in response.headers}


class TestAPIAudit:
    """Tests for API audit functionality."""

    @pytest.fixture
    def client(self):
        with TestClient(app) as client:
            yield client

    @pytest.fixture
    def auth_headers(self):
        return {
            "x-agency-id": "FBI-TEST",
            "x-officer-id": "OFF-001",
            "x-officer-name": "Test Officer",
            "x-badge-number": "12345",
        }

    def test_query_log(self, client, auth_headers):
        """Test query log retrieval."""
        # Make some queries
        client.post(
            "/api/v1/hash/check",
            json={"hash_type": "sha256", "hash_value": "e" * 64},
            headers=auth_headers,
        )

        # Get log
        response = client.get(
            "/api/v1/audit/queries",
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_custody_statistics(self, client, auth_headers):
        """Test custody statistics."""
        response = client.get(
            "/api/v1/audit/custody",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
