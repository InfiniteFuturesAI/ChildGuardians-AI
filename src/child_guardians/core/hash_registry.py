"""
Hash Registry - Known CSAM Hash Database Interface

This module implements the Hash Registry specification.
It provides lookup and registration of known illegal material hashes
WITHOUT storing any actual content.

The registry stores ONLY:
- Cryptographic hashes (SHA-256, SHA3-512)
- Perceptual hashes (PhotoDNA-style, PDQ)
- Metadata about when/where hash was first identified
- Victim status indicators

The registry NEVER stores:
- Actual images or videos
- Personal identifying information
- Suspect information
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class HashType(Enum):
    """Supported hash algorithms."""

    SHA256 = "sha256"
    SHA3_512 = "sha3_512"
    PHOTODNA = "photodna"
    PDQ = "pdq"


class MatchConfidence(Enum):
    """Confidence level of hash match."""

    CONFIRMED = "confirmed"  # Human-verified CSAM
    HIGH = "high"  # Algorithm match, high confidence
    MEDIUM = "medium"  # Perceptual match, medium confidence
    PENDING_REVIEW = "pending"  # Awaiting verification


class VictimStatus(Enum):
    """Status of victim identification."""

    IDENTIFIED = "identified"  # Victim known to authorities
    UNIDENTIFIED = "unidentified"  # Victim not yet identified
    UNKNOWN = "unknown"  # Status not determined


@dataclass
class HashRecord:
    """A record in the hash registry."""

    hash_type: HashType
    hash_value: str
    confidence: MatchConfidence
    victim_status: VictimStatus
    first_seen: datetime
    last_seen: datetime
    source_authority: str  # Which authority first reported
    category: str  # csam_confirmed, csam_suspected, etc.
    series_id: str | None = None  # If part of known series

    def to_dict(self) -> dict[str, Any]:
        return {
            "hash_type": self.hash_type.value,
            "hash_value": self.hash_value,
            "confidence": self.confidence.value,
            "victim_status": self.victim_status.value,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "source_authority": self.source_authority,
            "category": self.category,
            "series_id": self.series_id,
        }


@dataclass
class HashMatch:
    """Result of a hash lookup."""

    found: bool
    record: HashRecord | None = None
    evidence_package_available: bool = False
    evidence_package_id: str | None = None
    jurisdiction_flags: list[str] = None

    def __post_init__(self):
        if self.jurisdiction_flags is None:
            self.jurisdiction_flags = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "found": self.found,
            "record": self.record.to_dict() if self.record else None,
            "evidence_package_available": self.evidence_package_available,
            "evidence_package_id": self.evidence_package_id,
            "jurisdiction_flags": self.jurisdiction_flags,
        }


class HashRegistry:
    """
    Registry of known CSAM material hashes.

    This class provides:
    - Hash lookup against known illegal material
    - Hash registration for new identified material
    - Batch checking for efficiency
    - Audit logging of all queries

    The registry uses SQLite for portability but can be
    adapted to other backends for production use.
    """

    def __init__(self, db_path: str | Path = ":memory:"):
        """
        Initialize hash registry.

        Args:
            db_path: Path to SQLite database, or ":memory:" for testing
        """
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row

        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_type TEXT NOT NULL,
                hash_value TEXT NOT NULL,
                confidence TEXT NOT NULL,
                victim_status TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                source_authority TEXT NOT NULL,
                category TEXT NOT NULL,
                series_id TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(hash_type, hash_value)
            );

            CREATE INDEX IF NOT EXISTS idx_hash_lookup
                ON hashes(hash_type, hash_value);

            CREATE TABLE IF NOT EXISTS evidence_packages (
                hash_id INTEGER NOT NULL,
                package_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (hash_id) REFERENCES hashes(id)
            );

            CREATE TABLE IF NOT EXISTS jurisdiction_flags (
                hash_id INTEGER NOT NULL,
                jurisdiction TEXT NOT NULL,
                FOREIGN KEY (hash_id) REFERENCES hashes(id)
            );

            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_time TEXT NOT NULL,
                hash_type TEXT NOT NULL,
                hash_value TEXT NOT NULL,
                found INTEGER NOT NULL,
                querying_agency TEXT NOT NULL,
                querying_officer TEXT NOT NULL,
                case_reference TEXT,
                legal_basis TEXT
            );
        """)
        self._conn.commit()

    def check(
        self,
        hash_type: HashType | str,
        hash_value: str,
        querying_agency: str,
        querying_officer: str,
        case_reference: str | None = None,
        legal_basis: str | None = None,
    ) -> HashMatch:
        """
        Check if a hash exists in the registry.

        All queries are logged for audit purposes.

        Args:
            hash_type: Type of hash (sha256, sha3_512, photodna, pdq)
            hash_value: The hash value to check
            querying_agency: Agency making the query
            querying_officer: Officer ID making the query
            case_reference: Optional case number
            legal_basis: Optional legal authority reference

        Returns:
            HashMatch with results
        """
        if isinstance(hash_type, str):
            hash_type = HashType(hash_type)

        # Normalize hash value
        hash_value = hash_value.lower().strip()

        cursor = self._conn.cursor()

        # Query for hash
        cursor.execute(
            """
            SELECT * FROM hashes
            WHERE hash_type = ? AND hash_value = ?
        """,
            (hash_type.value, hash_value),
        )

        row = cursor.fetchone()

        # Log the query
        cursor.execute(
            """
            INSERT INTO query_log
            (query_time, hash_type, hash_value, found, querying_agency,
             querying_officer, case_reference, legal_basis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now(UTC).isoformat(),
                hash_type.value,
                hash_value,
                1 if row else 0,
                querying_agency,
                querying_officer,
                case_reference,
                legal_basis,
            ),
        )
        self._conn.commit()

        if not row:
            return HashMatch(found=False)

        # Build record
        record = HashRecord(
            hash_type=HashType(row["hash_type"]),
            hash_value=row["hash_value"],
            confidence=MatchConfidence(row["confidence"]),
            victim_status=VictimStatus(row["victim_status"]),
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            source_authority=row["source_authority"],
            category=row["category"],
            series_id=row["series_id"],
        )

        # Get evidence packages
        cursor.execute(
            """
            SELECT package_id FROM evidence_packages WHERE hash_id = ?
        """,
            (row["id"],),
        )
        packages = cursor.fetchall()

        # Get jurisdiction flags
        cursor.execute(
            """
            SELECT jurisdiction FROM jurisdiction_flags WHERE hash_id = ?
        """,
            (row["id"],),
        )
        jurisdictions = [r["jurisdiction"] for r in cursor.fetchall()]

        # Update last_seen
        cursor.execute(
            """
            UPDATE hashes SET last_seen = ? WHERE id = ?
        """,
            (datetime.now(UTC).isoformat(), row["id"]),
        )
        self._conn.commit()

        return HashMatch(
            found=True,
            record=record,
            evidence_package_available=len(packages) > 0,
            evidence_package_id=packages[0]["package_id"] if packages else None,
            jurisdiction_flags=jurisdictions,
        )

    def batch_check(
        self,
        hashes: list[tuple[HashType | str, str]],
        querying_agency: str,
        querying_officer: str,
        case_reference: str | None = None,
        legal_basis: str | None = None,
    ) -> list[HashMatch]:
        """
        Check multiple hashes in a single operation.

        Args:
            hashes: List of (hash_type, hash_value) tuples
            querying_agency: Agency making the query
            querying_officer: Officer ID making the query
            case_reference: Optional case number
            legal_basis: Optional legal authority reference

        Returns:
            List of HashMatch results in same order as input
        """
        results = []
        for hash_type, hash_value in hashes:
            result = self.check(
                hash_type=hash_type,
                hash_value=hash_value,
                querying_agency=querying_agency,
                querying_officer=querying_officer,
                case_reference=case_reference,
                legal_basis=legal_basis,
            )
            results.append(result)
        return results

    def register(
        self,
        hash_type: HashType | str,
        hash_value: str,
        confidence: MatchConfidence,
        victim_status: VictimStatus,
        source_authority: str,
        category: str = "csam_confirmed",
        series_id: str | None = None,
        jurisdictions: list[str] | None = None,
    ) -> bool:
        """
        Register a new hash in the registry.

        Args:
            hash_type: Type of hash
            hash_value: The hash value
            confidence: Confidence level of identification
            victim_status: Status of victim identification
            source_authority: Authority that identified this material
            category: Classification category
            series_id: Optional series identifier
            jurisdictions: Optional list of relevant jurisdictions

        Returns:
            True if registered, False if already exists
        """
        if isinstance(hash_type, str):
            hash_type = HashType(hash_type)

        hash_value = hash_value.lower().strip()
        now = datetime.now(UTC).isoformat()

        cursor = self._conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO hashes
                (hash_type, hash_value, confidence, victim_status, first_seen,
                 last_seen, source_authority, category, series_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    hash_type.value,
                    hash_value,
                    confidence.value,
                    victim_status.value,
                    now,
                    now,
                    source_authority,
                    category,
                    series_id,
                    now,
                ),
            )

            hash_id = cursor.lastrowid

            # Add jurisdiction flags
            if jurisdictions:
                for jurisdiction in jurisdictions:
                    cursor.execute(
                        """
                        INSERT INTO jurisdiction_flags (hash_id, jurisdiction)
                        VALUES (?, ?)
                    """,
                        (hash_id, jurisdiction),
                    )

            self._conn.commit()
            return True

        except sqlite3.IntegrityError:
            # Hash already exists
            return False

    def link_evidence_package(self, hash_value: str, package_id: str) -> bool:
        """Link an evidence package to a hash."""
        cursor = self._conn.cursor()

        cursor.execute(
            """
            SELECT id FROM hashes WHERE hash_value = ?
        """,
            (hash_value.lower().strip(),),
        )

        row = cursor.fetchone()
        if not row:
            return False

        cursor.execute(
            """
            INSERT INTO evidence_packages (hash_id, package_id, created_at)
            VALUES (?, ?, ?)
        """,
            (row["id"], package_id, datetime.now(UTC).isoformat()),
        )

        self._conn.commit()
        return True

    def get_query_log(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        agency: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve query log for audit purposes.

        Args:
            start_time: Optional start of time range
            end_time: Optional end of time range
            agency: Optional filter by agency

        Returns:
            List of query log entries
        """
        cursor = self._conn.cursor()

        query = "SELECT * FROM query_log WHERE 1=1"
        params: list[Any] = []

        if start_time:
            query += " AND query_time >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND query_time <= ?"
            params.append(end_time.isoformat())

        if agency:
            query += " AND querying_agency = ?"
            params.append(agency)

        query += " ORDER BY query_time DESC"

        cursor.execute(query, params)

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        cursor = self._conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM hashes")
        total_hashes = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT hash_type, COUNT(*) as count
            FROM hashes GROUP BY hash_type
        """)
        by_type = {row["hash_type"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT victim_status, COUNT(*) as count
            FROM hashes GROUP BY victim_status
        """)
        by_victim_status = {row["victim_status"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as total FROM query_log")
        total_queries = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) as matches FROM query_log WHERE found = 1
        """)
        total_matches = cursor.fetchone()["matches"]

        return {
            "total_hashes": total_hashes,
            "by_hash_type": by_type,
            "by_victim_status": by_victim_status,
            "total_queries": total_queries,
            "total_matches": total_matches,
            "match_rate": total_matches / total_queries if total_queries > 0 else 0,
        }

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def compute_hash(data: bytes, hash_type: HashType = HashType.SHA256) -> str:
    """
    Compute hash of binary data.

    Args:
        data: Binary data to hash
        hash_type: Type of hash to compute

    Returns:
        Hex-encoded hash value
    """
    if hash_type == HashType.SHA256:
        return hashlib.sha256(data).hexdigest()
    elif hash_type == HashType.SHA3_512:
        return hashlib.sha3_512(data).hexdigest()
    elif hash_type in (HashType.PHOTODNA, HashType.PDQ):
        # Perceptual hashing requires specialized libraries
        # This is a placeholder - actual implementation would use
        # PhotoDNA SDK or PDQ library
        raise NotImplementedError(
            f"{hash_type.value} requires specialized perceptual hashing library"
        )
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")


def compute_file_hash(file_path: str | Path, hash_type: HashType = HashType.SHA256) -> str:
    """
    Compute hash of a file.

    Args:
        file_path: Path to file
        hash_type: Type of hash to compute

    Returns:
        Hex-encoded hash value
    """
    with open(file_path, "rb") as f:
        return compute_hash(f.read(), hash_type)
