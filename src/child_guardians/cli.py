"""
CHILD GUARDIANS - Command Line Interface

Provides commands for:
- Running the API server
- Managing hash registry
- Verifying evidence integrity
- Exporting audit reports
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from child_guardians.core.chain_of_custody import ChainOfCustody
from child_guardians.core.defense_simulator import DefenseSimulator
from child_guardians.core.evidence_object import EvidenceObject
from child_guardians.core.hash_registry import HashRegistry, MatchConfidence, VictimStatus


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="child-guardians",
        description="CHILD GUARDIANS - Evidence Management System",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server command
    server_parser = subparsers.add_parser("serve", help="Start API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Hash commands
    hash_parser = subparsers.add_parser("hash", help="Hash registry operations")
    hash_subparsers = hash_parser.add_subparsers(dest="hash_command")

    hash_check = hash_subparsers.add_parser("check", help="Check a hash")
    hash_check.add_argument("hash_value", help="Hash to check")
    hash_check.add_argument("--type", default="sha256", choices=["sha256", "sha3_512"])
    hash_check.add_argument("--db", default="hash_registry.db", help="Database path")

    hash_register = hash_subparsers.add_parser("register", help="Register a hash")
    hash_register.add_argument("hash_value", help="Hash to register")
    hash_register.add_argument("--type", default="sha256", choices=["sha256", "sha3_512"])
    hash_register.add_argument("--confidence", default="confirmed")
    hash_register.add_argument("--db", default="hash_registry.db", help="Database path")

    hash_stats = hash_subparsers.add_parser("stats", help="Show registry statistics")
    hash_stats.add_argument("--db", default="hash_registry.db", help="Database path")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify evidence integrity")
    verify_parser.add_argument("evidence_file", help="Evidence JSON file to verify")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Export audit reports")
    audit_parser.add_argument("--evidence-id", help="Specific evidence ID")
    audit_parser.add_argument("--output", "-o", default="audit_report.json", help="Output file")
    audit_parser.add_argument("--db", default="custody.db", help="Custody database path")

    # Simulate command
    sim_parser = subparsers.add_parser("simulate", help="Run defense simulation")
    sim_parser.add_argument("evidence_file", help="Evidence JSON file")
    sim_parser.add_argument("--output", "-o", help="Output results to file")

    # Version command
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "hash":
        cmd_hash(args)
    elif args.command == "verify":
        cmd_verify(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    elif args.command == "version":
        cmd_version()
    else:
        parser.print_help()
        sys.exit(1)


def cmd_serve(args):
    """Start the API server."""
    import uvicorn

    print(f"Starting CHILD GUARDIANS API server on {args.host}:{args.port}")
    uvicorn.run(
        "child_guardians.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def cmd_hash(args):
    """Handle hash registry commands."""
    if args.hash_command == "check":
        registry = HashRegistry(args.db)
        result = registry.check(
            hash_type=args.type,
            hash_value=args.hash_value,
            querying_agency="CLI",
            querying_officer="cli-user",
        )

        if result.found:
            print("✓ MATCH FOUND")
            print(f"  Confidence: {result.record.confidence.value}")
            print(f"  Victim Status: {result.record.victim_status.value}")
            print(f"  Category: {result.record.category}")
            print(f"  First Seen: {result.record.first_seen}")
        else:
            print("✗ No match found")

        registry.close()

    elif args.hash_command == "register":
        registry = HashRegistry(args.db)
        success = registry.register(
            hash_type=args.type,
            hash_value=args.hash_value,
            confidence=MatchConfidence(args.confidence),
            victim_status=VictimStatus.UNKNOWN,
            source_authority="CLI",
        )

        if success:
            print(f"✓ Hash registered: {args.hash_value[:32]}...")
        else:
            print("✗ Hash already exists")

        registry.close()

    elif args.hash_command == "stats":
        registry = HashRegistry(args.db)
        stats = registry.get_statistics()

        print("Hash Registry Statistics")
        print("=" * 40)
        print(f"Total Hashes: {stats['total_hashes']:,}")
        print(f"Total Queries: {stats['total_queries']:,}")
        print(f"Total Matches: {stats['total_matches']:,}")
        print(f"Match Rate: {stats['match_rate']:.2%}")

        if stats['by_hash_type']:
            print("\nBy Hash Type:")
            for ht, count in stats['by_hash_type'].items():
                print(f"  {ht}: {count:,}")

        registry.close()


def cmd_verify(args):
    """Verify evidence integrity."""
    evidence_path = Path(args.evidence_file)

    if not evidence_path.exists():
        print(f"Error: File not found: {evidence_path}")
        sys.exit(1)

    with open(evidence_path) as f:
        data = json.load(f)

    evidence = EvidenceObject.from_dict(data)

    print(f"Verifying evidence: {evidence.evidence_id}")
    print("=" * 50)

    # Check validation status
    print(f"Status: {evidence.status.value}")
    print(f"Case Number: {evidence.case_number}")
    print(f"Created: {evidence.created_at}")

    # Verify chain of custody
    print(f"\nChain of Custody: {len(evidence.chain_of_custody)} events")

    # Run defense simulation
    simulator = DefenseSimulator()
    if evidence.status.value in ("validated", "sealed", "exported"):
        result = simulator.evaluate(evidence)

        print("\nDefense Simulation:")
        print(f"  Score: {result['score']}/100")
        print(f"  Passed: {'✓' if result['passed'] else '✗'}")

        if result['blocking_failures']:
            print(f"  Blocking Failures: {len(result['blocking_failures'])}")
            for failure in result['blocking_failures']:
                print(f"    - {failure['challenge_id']}: {failure['question']}")

    print("\nVerification complete.")


def cmd_audit(args):
    """Export audit report."""
    custody = ChainOfCustody(args.db)

    if args.evidence_id:
        # Export single evidence chain
        report = custody.export_chain(args.evidence_id)
    else:
        # Export statistics
        report = {
            "generated_at": datetime.now(UTC).isoformat(),
            "statistics": custody.get_statistics(),
        }

    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Audit report written to: {output_path}")
    custody.close()


def cmd_simulate(args):
    """Run defense simulation on evidence."""
    evidence_path = Path(args.evidence_file)

    if not evidence_path.exists():
        print(f"Error: File not found: {evidence_path}")
        sys.exit(1)

    with open(evidence_path) as f:
        data = json.load(f)

    evidence = EvidenceObject.from_dict(data)
    simulator = DefenseSimulator()

    # Force validated status for simulation
    from child_guardians.core.evidence_object import EvidenceStatus
    if evidence.status == EvidenceStatus.DRAFT:
        evidence.status = EvidenceStatus.VALIDATED

    result = simulator.evaluate(evidence)

    print("Defense Attorney Simulation Results")
    print("=" * 50)
    print(f"Evidence ID: {evidence.evidence_id}")
    print(f"Case Number: {evidence.case_number}")
    print()
    print(f"Overall Score: {result['score']}/100")
    print(f"Passed: {'✓ YES - Ready for export' if result['passed'] else '✗ NO - Not ready for export'}")
    print()

    print(f"Recommendation: {result['recommendation']}")
    print()

    if result['blocking_failures']:
        print("CRITICAL FAILURES (Must Fix):")
        for failure in result['blocking_failures']:
            print(f"  ✗ [{failure['challenge_id']}] {failure['question']}")
            print(f"    → {failure['explanation']}")
        print()

    if result['major_failures']:
        print("MAJOR FAILURES:")
        for failure in result['major_failures']:
            print(f"  ⚠ [{failure['challenge_id']}] {failure['question']}")
            print(f"    → {failure['explanation']}")
        print()

    if result['warnings']:
        print(f"WARNINGS ({len(result['warnings'])} items):")
        for warning in result['warnings'][:5]:  # Show first 5
            print(f"  • [{warning['challenge_id']}] {warning['explanation']}")
        if len(result['warnings']) > 5:
            print(f"  ... and {len(result['warnings']) - 5} more")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nFull results written to: {args.output}")


def cmd_version():
    """Show version information."""
    from child_guardians import __version__
    print(f"CHILD GUARDIANS v{__version__}")


if __name__ == "__main__":
    main()
