"""
Tests for child_guardians.cli module.

Tests CLI argument parsing and command execution.
"""

import json
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from child_guardians.cli import (
    cmd_audit,
    cmd_hash,
    cmd_simulate,
    cmd_verify,
    cmd_version,
    main,
)
from child_guardians.core.evidence_object import (
    CollectionDetails,
    EvidenceObject,
    EvidenceStatus,
    JurisdictionMap,
    LegalBasis,
    LegalBasisType,
)


class TestMainParser:
    """Tests for main CLI parser."""

    def test_no_command_shows_help(self, capsys):
        """Test that no command shows help and exits."""
        with patch.object(sys, "argv", ["child-guardians"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_version_command(self, capsys):
        """Test version command output."""
        cmd_version()
        captured = capsys.readouterr()
        assert "CHILD GUARDIANS" in captured.out
        assert "v" in captured.out

    def test_serve_command_args(self):
        """Test serve command argument parsing."""
        with patch.object(
            sys, "argv", ["child-guardians", "serve", "--host", "0.0.0.0", "--port", "9000"]
        ):
            with patch("child_guardians.cli.cmd_serve") as mock_serve:
                main()
                mock_serve.assert_called_once()
                args = mock_serve.call_args[0][0]
                assert args.host == "0.0.0.0"
                assert args.port == 9000


class TestCmdHash:
    """Tests for hash registry CLI commands."""

    def test_hash_check_not_found(self, capsys):
        """Test hash check when hash not in registry."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        args = MagicMock()
        args.hash_command = "check"
        args.db = db_path
        args.type = "sha256"
        args.hash_value = "abc123def456"

        cmd_hash(args)

        captured = capsys.readouterr()
        assert "No match found" in captured.out

        Path(db_path).unlink(missing_ok=True)

    def test_hash_register_success(self, capsys):
        """Test successful hash registration."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        args = MagicMock()
        args.hash_command = "register"
        args.db = db_path
        args.type = "sha256"
        args.hash_value = "deadbeef" * 8
        args.confidence = "confirmed"

        cmd_hash(args)

        captured = capsys.readouterr()
        assert "Hash registered" in captured.out

        Path(db_path).unlink(missing_ok=True)

    def test_hash_check_found(self, capsys):
        """Test hash check when hash is found."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # First register
        args = MagicMock()
        args.hash_command = "register"
        args.db = db_path
        args.type = "sha256"
        args.hash_value = "cafebabe" * 8
        args.confidence = "confirmed"
        cmd_hash(args)

        # Then check
        args.hash_command = "check"
        cmd_hash(args)

        captured = capsys.readouterr()
        assert "MATCH FOUND" in captured.out
        assert "Confidence" in captured.out

        Path(db_path).unlink(missing_ok=True)

    def test_hash_stats(self, capsys):
        """Test hash stats command."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        args = MagicMock()
        args.hash_command = "stats"
        args.db = db_path

        cmd_hash(args)

        captured = capsys.readouterr()
        assert "Hash Registry Statistics" in captured.out
        assert "Total Hashes" in captured.out

        Path(db_path).unlink(missing_ok=True)


class TestCmdVerify:
    """Tests for evidence verification CLI command."""

    def _create_test_evidence(self) -> EvidenceObject:
        """Create a test evidence object."""
        now = datetime.now(UTC)
        legal_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="WARRANT-TEST-001",
            issued_by="Test Judge",
            issued_date=now - timedelta(hours=1),
            scope="Test scope",
            expires=now + timedelta(days=30),
        )
        collection = CollectionDetails(
            officer_id="TEST-001",
            officer_name="Test Officer",
            badge_number="T-12345",
            agency="Test Agency",
            agency_unit="Test Unit",
            collection_time=now,
            collection_location="Test Location",
            tool_used="Test Tool",
            tool_version="1.0",
            tool_hash="sha256:test",
        )
        jurisdiction = JurisdictionMap(
            primary_jurisdiction="TEST",
            hosting_country="US",
            can_export_evidence=["TEST"],
        )
        return EvidenceObject(
            case_number="TEST-CASE-001",
            evidence_type="test",
            legal_basis=legal_basis,
            collection_details=collection,
            jurisdiction=jurisdiction,
        )

    def test_verify_file_not_found(self, capsys):
        """Test verify with non-existent file."""
        args = MagicMock()
        args.evidence_file = "/nonexistent/file.json"

        with pytest.raises(SystemExit) as exc_info:
            cmd_verify(args)
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_verify_valid_evidence(self, capsys):
        """Test verify with valid evidence file."""
        evidence = self._create_test_evidence()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(evidence.to_dict(), f)
            evidence_path = f.name

        args = MagicMock()
        args.evidence_file = evidence_path

        cmd_verify(args)

        captured = capsys.readouterr()
        assert "Verifying evidence" in captured.out
        assert evidence.evidence_id in captured.out
        assert "Verification complete" in captured.out

        Path(evidence_path).unlink(missing_ok=True)


class TestCmdAudit:
    """Tests for audit CLI command."""

    def test_audit_stats(self, capsys):
        """Test audit command with statistics."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db:
            db_path = db.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        args = MagicMock()
        args.db = db_path
        args.evidence_id = None
        args.output = output_path

        cmd_audit(args)

        captured = capsys.readouterr()
        assert "Audit report written to" in captured.out

        # Verify output file
        with open(output_path) as f:
            report = json.load(f)
        assert "generated_at" in report
        assert "statistics" in report

        Path(db_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


class TestCmdSimulate:
    """Tests for defense simulation CLI command."""

    def _create_test_evidence(self) -> EvidenceObject:
        """Create a test evidence object."""
        now = datetime.now(UTC)
        legal_basis = LegalBasis(
            basis_type=LegalBasisType.WARRANT,
            reference="WARRANT-TEST-001",
            issued_by="Test Judge",
            issued_date=now - timedelta(hours=1),
            scope="Test scope",
            expires=now + timedelta(days=30),
        )
        collection = CollectionDetails(
            officer_id="TEST-001",
            officer_name="Test Officer",
            badge_number="T-12345",
            agency="Test Agency",
            agency_unit="Test Unit",
            collection_time=now,
            collection_location="Test Location",
            tool_used="Test Tool",
            tool_version="1.0",
            tool_hash="sha256:test",
        )
        jurisdiction = JurisdictionMap(
            primary_jurisdiction="TEST",
            hosting_country="US",
            can_export_evidence=["TEST"],
        )
        return EvidenceObject(
            case_number="TEST-CASE-001",
            evidence_type="test",
            legal_basis=legal_basis,
            collection_details=collection,
            jurisdiction=jurisdiction,
        )

    def test_simulate_file_not_found(self, capsys):
        """Test simulate with non-existent file."""
        args = MagicMock()
        args.evidence_file = "/nonexistent/file.json"
        args.output = None

        with pytest.raises(SystemExit) as exc_info:
            cmd_simulate(args)
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_simulate_valid_evidence(self, capsys):
        """Test simulate with valid evidence."""
        evidence = self._create_test_evidence()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(evidence.to_dict(), f)
            evidence_path = f.name

        args = MagicMock()
        args.evidence_file = evidence_path
        args.output = None

        cmd_simulate(args)

        captured = capsys.readouterr()
        assert "Defense Attorney Simulation Results" in captured.out
        assert "Overall Score" in captured.out
        assert "Recommendation" in captured.out

        Path(evidence_path).unlink(missing_ok=True)

    def test_simulate_with_output_file(self, capsys):
        """Test simulate with output file."""
        evidence = self._create_test_evidence()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(evidence.to_dict(), f)
            evidence_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        args = MagicMock()
        args.evidence_file = evidence_path
        args.output = output_path

        cmd_simulate(args)

        captured = capsys.readouterr()
        assert "Full results written to" in captured.out

        # Verify output file
        with open(output_path) as f:
            results = json.load(f)
        assert "score" in results
        assert "passed" in results

        Path(evidence_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


class TestCmdServe:
    """Tests for serve CLI command."""

    def test_serve_calls_uvicorn(self, capsys):
        """Test that serve command calls uvicorn."""
        with patch.dict("sys.modules", {"uvicorn": MagicMock()}) as modules:
            import importlib
            import child_guardians.cli

            importlib.reload(child_guardians.cli)

            mock_uvicorn = sys.modules["uvicorn"]

            args = MagicMock()
            args.host = "127.0.0.1"
            args.port = 8000
            args.reload = False

            child_guardians.cli.cmd_serve(args)

            mock_uvicorn.run.assert_called_once_with(
                "child_guardians.api.main:app",
                host="127.0.0.1",
                port=8000,
                reload=False,
            )
