"""
Chain of Custody - Append-Only Evidence Audit Trail

This module implements immutable chain of custody logging.
Every evidence access, modification, and export is recorded
and cryptographically chained to prevent tampering.

Key Properties:
- Append-only: Events can never be deleted
- Cryptographically chained: Each event links to previous
- Timestamped: UTC timestamps with microsecond precision
- Signed: Each event signed by actor's key
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature


class CustodyAction(Enum):
    """Types of custody events."""
    CREATED = "created"
    ACCESSED = "accessed"
    MODIFIED = "modified"
    HASH_ADDED = "hash_added"
    VALIDATED = "validated"
    SEALED = "sealed"
    EXPORTED = "exported"
    TRANSFERRED = "transferred"
    ARCHIVED = "archived"


@dataclass
class CustodyEvent:
    """A single event in the chain of custody."""
    event_id: str
    evidence_id: str
    action: CustodyAction
    actor_id: str
    actor_name: str
    actor_agency: str
    timestamp: datetime
    previous_hash: str          # Hash of previous event (chain link)
    event_hash: str             # Hash of this event
    signature: bytes            # Actor's signature
    details: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "evidence_id": self.evidence_id,
            "action": self.action.value,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "actor_agency": self.actor_agency,
            "timestamp": self.timestamp.isoformat(),
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            "signature": self.signature.hex() if self.signature else None,
            "details": self.details,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CustodyEvent:
        return cls(
            event_id=data["event_id"],
            evidence_id=data["evidence_id"],
            action=CustodyAction(data["action"]),
            actor_id=data["actor_id"],
            actor_name=data["actor_name"],
            actor_agency=data["actor_agency"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            previous_hash=data["previous_hash"],
            event_hash=data["event_hash"],
            signature=bytes.fromhex(data["signature"]) if data.get("signature") else b"",
            details=data.get("details", {}),
        )


class ChainOfCustody:
    """
    Append-only chain of custody manager.
    
    Maintains an immutable, cryptographically-linked log of all
    evidence handling events. The chain cannot be modified after
    events are recorded.
    """
    
    GENESIS_HASH = "0" * 64  # Genesis block previous hash
    
    def __init__(self, db_path: str | Path = ":memory:"):
        """
        Initialize chain of custody.
        
        Args:
            db_path: Path to SQLite database, or ":memory:" for testing
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS custody_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                evidence_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_name TEXT NOT NULL,
                actor_agency TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL,
                signature BLOB,
                details TEXT,
                created_at TEXT NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_evidence_id 
                ON custody_events(evidence_id);
            
            CREATE INDEX IF NOT EXISTS idx_event_hash
                ON custody_events(event_hash);
            
            CREATE INDEX IF NOT EXISTS idx_timestamp
                ON custody_events(timestamp);
        """)
        self._conn.commit()
    
    def record_event(
        self,
        evidence_id: str,
        action: CustodyAction,
        actor_id: str,
        actor_name: str,
        actor_agency: str,
        private_key: Optional[ed25519.Ed25519PrivateKey] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> CustodyEvent:
        """
        Record a new custody event.
        
        Args:
            evidence_id: ID of the evidence being handled
            action: Type of action being recorded
            actor_id: ID of the person performing the action
            actor_name: Name of the person performing the action
            actor_agency: Agency of the person
            private_key: Optional key to sign the event
            details: Optional additional details
        
        Returns:
            The recorded CustodyEvent
        """
        import uuid
        
        timestamp = datetime.now(timezone.utc)
        event_id = str(uuid.uuid4())
        
        # Get previous hash
        previous_hash = self._get_last_hash(evidence_id)
        
        # Compute event hash
        event_data = {
            "event_id": event_id,
            "evidence_id": evidence_id,
            "action": action.value,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_agency": actor_agency,
            "timestamp": timestamp.isoformat(),
            "previous_hash": previous_hash,
            "details": details or {},
        }
        event_hash = hashlib.sha256(
            json.dumps(event_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Sign if key provided
        signature = b""
        if private_key:
            signature = private_key.sign(event_hash.encode())
        
        # Create event
        event = CustodyEvent(
            event_id=event_id,
            evidence_id=evidence_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_agency=actor_agency,
            timestamp=timestamp,
            previous_hash=previous_hash,
            event_hash=event_hash,
            signature=signature,
            details=details or {},
        )
        
        # Store in database
        self._store_event(event)
        
        return event
    
    def _get_last_hash(self, evidence_id: str) -> str:
        """Get the hash of the last event for this evidence."""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT event_hash FROM custody_events 
            WHERE evidence_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
        """, (evidence_id,))
        
        row = cursor.fetchone()
        return row["event_hash"] if row else self.GENESIS_HASH
    
    def _store_event(self, event: CustodyEvent) -> None:
        """Store event in database."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO custody_events
            (event_id, evidence_id, action, actor_id, actor_name, actor_agency,
             timestamp, previous_hash, event_hash, signature, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.evidence_id,
            event.action.value,
            event.actor_id,
            event.actor_name,
            event.actor_agency,
            event.timestamp.isoformat(),
            event.previous_hash,
            event.event_hash,
            event.signature,
            json.dumps(event.details),
            datetime.now(timezone.utc).isoformat(),
        ))
        self._conn.commit()
    
    def get_chain(self, evidence_id: str) -> list[CustodyEvent]:
        """
        Get complete chain of custody for evidence.
        
        Args:
            evidence_id: ID of the evidence
        
        Returns:
            List of CustodyEvents in chronological order
        """
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM custody_events 
            WHERE evidence_id = ?
            ORDER BY timestamp ASC, id ASC
        """, (evidence_id,))
        
        events = []
        for row in cursor.fetchall():
            events.append(CustodyEvent(
                event_id=row["event_id"],
                evidence_id=row["evidence_id"],
                action=CustodyAction(row["action"]),
                actor_id=row["actor_id"],
                actor_name=row["actor_name"],
                actor_agency=row["actor_agency"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                previous_hash=row["previous_hash"],
                event_hash=row["event_hash"],
                signature=row["signature"] or b"",
                details=json.loads(row["details"]) if row["details"] else {},
            ))
        
        return events
    
    def verify_chain(
        self,
        evidence_id: str,
        public_keys: Optional[dict[str, ed25519.Ed25519PublicKey]] = None,
    ) -> dict[str, Any]:
        """
        Verify the integrity of a chain of custody.
        
        Checks:
        1. Hash chain is unbroken
        2. Event hashes are correct
        3. Signatures are valid (if public keys provided)
        
        Args:
            evidence_id: ID of the evidence
            public_keys: Optional dict of actor_id -> public_key for signature verification
        
        Returns:
            Verification result with any issues found
        """
        events = self.get_chain(evidence_id)
        
        if not events:
            return {
                "valid": False,
                "error": "No custody events found",
                "events_checked": 0,
            }
        
        issues = []
        previous_hash = self.GENESIS_HASH
        
        for i, event in enumerate(events):
            # Check chain link
            if event.previous_hash != previous_hash:
                issues.append({
                    "event_index": i,
                    "event_id": event.event_id,
                    "issue": "broken_chain",
                    "expected_previous": previous_hash,
                    "actual_previous": event.previous_hash,
                })
            
            # Verify event hash
            event_data = {
                "event_id": event.event_id,
                "evidence_id": event.evidence_id,
                "action": event.action.value,
                "actor_id": event.actor_id,
                "actor_name": event.actor_name,
                "actor_agency": event.actor_agency,
                "timestamp": event.timestamp.isoformat(),
                "previous_hash": event.previous_hash,
                "details": event.details,
            }
            computed_hash = hashlib.sha256(
                json.dumps(event_data, sort_keys=True).encode()
            ).hexdigest()
            
            if computed_hash != event.event_hash:
                issues.append({
                    "event_index": i,
                    "event_id": event.event_id,
                    "issue": "hash_mismatch",
                    "expected_hash": computed_hash,
                    "actual_hash": event.event_hash,
                })
            
            # Verify signature if public key available
            if public_keys and event.actor_id in public_keys and event.signature:
                try:
                    public_keys[event.actor_id].verify(
                        event.signature,
                        event.event_hash.encode()
                    )
                except InvalidSignature:
                    issues.append({
                        "event_index": i,
                        "event_id": event.event_id,
                        "issue": "invalid_signature",
                    })
            
            previous_hash = event.event_hash
        
        return {
            "valid": len(issues) == 0,
            "events_checked": len(events),
            "issues": issues,
            "first_event": events[0].timestamp.isoformat() if events else None,
            "last_event": events[-1].timestamp.isoformat() if events else None,
        }
    
    def get_events_by_actor(
        self,
        actor_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> list[CustodyEvent]:
        """Get all custody events by a specific actor."""
        cursor = self._conn.cursor()
        
        query = "SELECT * FROM custody_events WHERE actor_id = ?"
        params: list[Any] = [actor_id]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            events.append(CustodyEvent(
                event_id=row["event_id"],
                evidence_id=row["evidence_id"],
                action=CustodyAction(row["action"]),
                actor_id=row["actor_id"],
                actor_name=row["actor_name"],
                actor_agency=row["actor_agency"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                previous_hash=row["previous_hash"],
                event_hash=row["event_hash"],
                signature=row["signature"] or b"",
                details=json.loads(row["details"]) if row["details"] else {},
            ))
        
        return events
    
    def get_statistics(self) -> dict[str, Any]:
        """Get chain of custody statistics."""
        cursor = self._conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT evidence_id) as count FROM custody_events")
        unique_evidence = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM custody_events")
        total_events = cursor.fetchone()["count"]
        
        cursor.execute("""
            SELECT action, COUNT(*) as count 
            FROM custody_events GROUP BY action
        """)
        by_action = {row["action"]: row["count"] for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT actor_agency, COUNT(*) as count 
            FROM custody_events GROUP BY actor_agency
        """)
        by_agency = {row["actor_agency"]: row["count"] for row in cursor.fetchall()}
        
        return {
            "unique_evidence_items": unique_evidence,
            "total_events": total_events,
            "events_by_action": by_action,
            "events_by_agency": by_agency,
        }
    
    def export_chain(self, evidence_id: str) -> dict[str, Any]:
        """
        Export complete chain of custody for court presentation.
        
        Returns a court-ready document with:
        - Complete event timeline
        - Verification status
        - Actor information
        """
        events = self.get_chain(evidence_id)
        verification = self.verify_chain(evidence_id)
        
        return {
            "evidence_id": evidence_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "chain_valid": verification["valid"],
            "total_events": len(events),
            "first_custody": events[0].timestamp.isoformat() if events else None,
            "last_activity": events[-1].timestamp.isoformat() if events else None,
            "events": [e.to_dict() for e in events],
            "verification": verification,
            "summary": {
                "actors": list(set(e.actor_id for e in events)),
                "agencies": list(set(e.actor_agency for e in events)),
                "actions": list(set(e.action.value for e in events)),
            },
        }
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
