"""
CHILD GUARDIANS - Evidence Management System for Child Protection

This system provides court-safe evidence management infrastructure
for law enforcement agencies investigating child sexual abuse material.

Core Principles:
- Evidence is born court-safe, not fixed later
- The system responds to queries; it never initiates action
- AI advises; humans decide
- Oversight is structural, not optional
"""

__version__ = "0.1.0"
__author__ = "CHILD GUARDIANS Project"
__license__ = "Public Domain Dedication"

from child_guardians.core.chain_of_custody import ChainOfCustody
from child_guardians.core.defense_simulator import DefenseSimulator
from child_guardians.core.evidence_object import EvidenceObject
from child_guardians.core.hash_registry import HashRegistry

__all__ = [
    "EvidenceObject",
    "HashRegistry",
    "ChainOfCustody",
    "DefenseSimulator",
]
