"""
REST API for CHILD GUARDIANS

This module provides a FastAPI-based REST API for law enforcement
integration. All endpoints require authentication and log access.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from child_guardians.core.chain_of_custody import ChainOfCustody, CustodyAction
from child_guardians.core.defense_simulator import DefenseSimulator
from child_guardians.core.evidence_object import (
    CollectionDetails,
    EvidenceObject,
    JurisdictionMap,
    LegalBasis,
    LegalBasisType,
    MaterialHash,
)
from child_guardians.core.hash_registry import (
    HashRegistry,
    MatchConfidence,
    VictimStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("child_guardians.api")


# ===== Global Resources =====

registry: HashRegistry | None = None
custody: ChainOfCustody | None = None
simulator: DefenseSimulator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    global registry, custody, simulator

    # Initialize components
    # In production, these would connect to persistent storage
    registry = HashRegistry()
    custody = ChainOfCustody()
    simulator = DefenseSimulator()

    logger.info("CHILD GUARDIANS API initialized")

    yield

    # Cleanup
    if registry:
        registry.close()
    if custody:
        custody.close()

    logger.info("CHILD GUARDIANS API shutdown")


# ===== FastAPI Application =====

app = FastAPI(
    title="CHILD GUARDIANS API",
    description="Evidence management system for law enforcement",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS configuration - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Request/Response Models =====

class AgencyAuth(BaseModel):
    """Authentication context from headers."""
    agency_id: str
    officer_id: str
    officer_name: str
    badge_number: str


class HashCheckRequest(BaseModel):
    """Request to check a hash."""
    hash_type: str = Field(..., description="Hash type: sha256, sha3_512, photodna, pdq")
    hash_value: str = Field(..., description="Hex-encoded hash value")
    case_reference: str | None = Field(None, description="Optional case number")
    legal_basis: str | None = Field(None, description="Optional legal authority reference")


class HashCheckResponse(BaseModel):
    """Response from hash check."""
    found: bool
    confidence: str | None = None
    victim_status: str | None = None
    category: str | None = None
    evidence_available: bool = False
    jurisdiction_flags: list[str] = []


class BatchHashCheckRequest(BaseModel):
    """Request to check multiple hashes."""
    hashes: list[HashCheckRequest]
    case_reference: str | None = None
    legal_basis: str | None = None


class HashRegisterRequest(BaseModel):
    """Request to register a new hash."""
    hash_type: str
    hash_value: str
    confidence: str = "confirmed"
    victim_status: str = "unknown"
    category: str = "csam_confirmed"
    series_id: str | None = None
    jurisdictions: list[str] | None = None


class EvidenceCreateRequest(BaseModel):
    """Request to create new evidence object."""
    case_number: str
    evidence_type: str
    legal_basis_type: str
    legal_basis_reference: str
    legal_basis_issued_by: str
    legal_basis_issued_date: str
    legal_basis_scope: str
    legal_basis_expires: str | None = None
    collection_location: str
    tool_used: str
    tool_version: str
    tool_hash: str = ""
    witness_present: bool = False
    witness_name: str | None = None
    primary_jurisdiction: str
    hosting_country: str
    victim_country: str | None = None


class MaterialHashRequest(BaseModel):
    """Request to add a material hash."""
    hash_type: str
    hash_value: str
    source_file: str
    source_path: str


class CustodyEventRequest(BaseModel):
    """Request to record a custody event."""
    evidence_id: str
    action: str
    details: dict[str, Any] | None = None


class DefenseSimulationResponse(BaseModel):
    """Response from defense simulation."""
    passed: bool
    score: int
    blocking_failures: list[dict]
    major_failures: list[dict]
    warnings: list[dict]
    recommendation: str


# ===== Authentication Dependency =====

async def get_auth(
    x_agency_id: str = Header(..., description="Agency identifier"),
    x_officer_id: str = Header(..., description="Officer identifier"),
    x_officer_name: str = Header(..., description="Officer name"),
    x_badge_number: str = Header(..., description="Badge number"),
) -> AgencyAuth:
    """Extract authentication from headers."""
    return AgencyAuth(
        agency_id=x_agency_id,
        officer_id=x_officer_id,
        officer_name=x_officer_name,
        badge_number=x_badge_number,
    )


# ===== Middleware =====

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests for audit trail."""
    start_time = datetime.now(UTC)

    response = await call_next(request)

    duration = (datetime.now(UTC) - start_time).total_seconds()

    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s - "
        f"Agency: {request.headers.get('x-agency-id', 'unknown')}"
    )

    return response


# ===== Health Endpoints =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "0.1.0",
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    global registry, custody, simulator

    ready = all([registry, custody, simulator])

    if not ready:
        raise HTTPException(status_code=503, detail="Service not ready")

    return {
        "ready": True,
        "components": {
            "hash_registry": registry is not None,
            "chain_of_custody": custody is not None,
            "defense_simulator": simulator is not None,
        },
    }


# ===== Hash Registry Endpoints =====

@app.post("/api/v1/hash/check", response_model=HashCheckResponse)
async def check_hash(
    request: HashCheckRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """
    Check if a hash exists in the known CSAM registry.

    All queries are logged for audit purposes.
    """
    global registry

    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    result = registry.check(
        hash_type=request.hash_type,
        hash_value=request.hash_value,
        querying_agency=auth.agency_id,
        querying_officer=auth.officer_id,
        case_reference=request.case_reference,
        legal_basis=request.legal_basis,
    )

    if not result.found:
        return HashCheckResponse(found=False)

    return HashCheckResponse(
        found=True,
        confidence=result.record.confidence.value if result.record else None,
        victim_status=result.record.victim_status.value if result.record else None,
        category=result.record.category if result.record else None,
        evidence_available=result.evidence_package_available,
        jurisdiction_flags=result.jurisdiction_flags,
    )


@app.post("/api/v1/hash/batch")
async def batch_check_hashes(
    request: BatchHashCheckRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """Check multiple hashes in a single request."""
    global registry

    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    hashes = [(h.hash_type, h.hash_value) for h in request.hashes]

    results = registry.batch_check(
        hashes=hashes,
        querying_agency=auth.agency_id,
        querying_officer=auth.officer_id,
        case_reference=request.case_reference,
        legal_basis=request.legal_basis,
    )

    return {
        "total": len(results),
        "matches": sum(1 for r in results if r.found),
        "results": [r.to_dict() for r in results],
    }


@app.post("/api/v1/hash/register")
async def register_hash(
    request: HashRegisterRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """
    Register a new hash in the registry.

    Requires appropriate authority level.
    """
    global registry

    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    success = registry.register(
        hash_type=request.hash_type,
        hash_value=request.hash_value,
        confidence=MatchConfidence(request.confidence),
        victim_status=VictimStatus(request.victim_status),
        source_authority=auth.agency_id,
        category=request.category,
        series_id=request.series_id,
        jurisdictions=request.jurisdictions,
    )

    if not success:
        raise HTTPException(status_code=409, detail="Hash already exists")

    logger.info(
        f"Hash registered by {auth.officer_id} ({auth.agency_id}): "
        f"{request.hash_type}:{request.hash_value[:16]}..."
    )

    return {"registered": True, "hash_type": request.hash_type}


@app.get("/api/v1/hash/statistics")
async def hash_statistics(auth: AgencyAuth = Depends(get_auth)):
    """Get registry statistics."""
    global registry

    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    return registry.get_statistics()


# ===== Evidence Object Endpoints =====

# In-memory evidence storage (use database in production)
evidence_store: dict[str, EvidenceObject] = {}


@app.post("/api/v1/evidence/create")
async def create_evidence(
    request: EvidenceCreateRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """Create a new evidence object."""

    legal_basis = LegalBasis(
        basis_type=LegalBasisType(request.legal_basis_type),
        reference=request.legal_basis_reference,
        issued_by=request.legal_basis_issued_by,
        issued_date=datetime.fromisoformat(request.legal_basis_issued_date),
        scope=request.legal_basis_scope,
        expires=datetime.fromisoformat(request.legal_basis_expires) if request.legal_basis_expires else None,
    )

    collection_details = CollectionDetails(
        officer_id=auth.officer_id,
        officer_name=auth.officer_name,
        badge_number=auth.badge_number,
        agency=auth.agency_id,
        agency_unit="",  # Could be added to auth
        collection_time=datetime.now(UTC),
        collection_location=request.collection_location,
        tool_used=request.tool_used,
        tool_version=request.tool_version,
        tool_hash=request.tool_hash,
        witness_present=request.witness_present,
        witness_name=request.witness_name,
    )

    jurisdiction = JurisdictionMap(
        primary_jurisdiction=request.primary_jurisdiction,
        hosting_country=request.hosting_country,
        victim_country=request.victim_country,
    )

    evidence = EvidenceObject(
        case_number=request.case_number,
        evidence_type=request.evidence_type,
        legal_basis=legal_basis,
        collection_details=collection_details,
        jurisdiction=jurisdiction,
    )

    # Store evidence
    evidence_store[evidence.evidence_id] = evidence

    logger.info(
        f"Evidence created by {auth.officer_id}: "
        f"{evidence.evidence_id} for case {request.case_number}"
    )

    return {
        "evidence_id": evidence.evidence_id,
        "case_number": evidence.case_number,
        "status": evidence.status.value,
        "created_at": evidence.created_at.isoformat(),
    }


@app.get("/api/v1/evidence/{evidence_id}")
async def get_evidence(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
):
    """Get evidence object by ID."""
    global custody

    if evidence_id not in evidence_store:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence = evidence_store[evidence_id]

    # Log access
    if custody:
        custody.record_event(
            evidence_id=evidence_id,
            action=CustodyAction.ACCESSED,
            actor_id=auth.officer_id,
            actor_name=auth.officer_name,
            actor_agency=auth.agency_id,
        )

    return evidence.to_dict()


@app.post("/api/v1/evidence/{evidence_id}/hash")
async def add_evidence_hash(
    evidence_id: str,
    request: MaterialHashRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """Add a material hash to evidence object."""

    if evidence_id not in evidence_store:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence = evidence_store[evidence_id]

    material_hash = MaterialHash(
        hash_type=request.hash_type,
        hash_value=request.hash_value,
        source_file=request.source_file,
        source_path=request.source_path,
        computed_by=auth.officer_id,
    )

    try:
        evidence.add_material_hash(material_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    return {
        "added": True,
        "hash_count": len(evidence.material_hashes),
    }


@app.post("/api/v1/evidence/{evidence_id}/validate")
async def validate_evidence(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
):
    """Run pre-flight validation on evidence."""

    if evidence_id not in evidence_store:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence = evidence_store[evidence_id]

    try:
        result = evidence.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    return result


@app.post("/api/v1/evidence/{evidence_id}/simulate")
async def simulate_defense(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
) -> DefenseSimulationResponse:
    """Run defense attorney simulation against evidence."""
    global simulator

    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not initialized")

    if evidence_id not in evidence_store:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence = evidence_store[evidence_id]

    try:
        result = evidence.run_defense_simulation(simulator)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    return DefenseSimulationResponse(
        passed=result["passed"],
        score=result["score"],
        blocking_failures=result["blocking_failures"],
        major_failures=result["major_failures"],
        warnings=result["warnings"],
        recommendation=result["recommendation"],
    )


# ===== Chain of Custody Endpoints =====

@app.get("/api/v1/custody/{evidence_id}")
async def get_custody_chain(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
):
    """Get complete chain of custody for evidence."""
    global custody

    if not custody:
        raise HTTPException(status_code=503, detail="Custody not initialized")

    events = custody.get_chain(evidence_id)

    return {
        "evidence_id": evidence_id,
        "events": [e.to_dict() for e in events],
        "total_events": len(events),
    }


@app.post("/api/v1/custody/event")
async def record_custody_event(
    request: CustodyEventRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    """Record a custody event."""
    global custody

    if not custody:
        raise HTTPException(status_code=503, detail="Custody not initialized")

    event = custody.record_event(
        evidence_id=request.evidence_id,
        action=CustodyAction(request.action),
        actor_id=auth.officer_id,
        actor_name=auth.officer_name,
        actor_agency=auth.agency_id,
        details=request.details,
    )

    return event.to_dict()


@app.get("/api/v1/custody/{evidence_id}/verify")
async def verify_custody_chain(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
):
    """Verify integrity of custody chain."""
    global custody

    if not custody:
        raise HTTPException(status_code=503, detail="Custody not initialized")

    return custody.verify_chain(evidence_id)


@app.get("/api/v1/custody/{evidence_id}/export")
async def export_custody_chain(
    evidence_id: str,
    auth: AgencyAuth = Depends(get_auth),
):
    """Export chain of custody for court."""
    global custody

    if not custody:
        raise HTTPException(status_code=503, detail="Custody not initialized")

    return custody.export_chain(evidence_id)


# ===== Audit Endpoints =====

@app.get("/api/v1/audit/queries")
async def get_query_log(
    agency: str | None = None,
    auth: AgencyAuth = Depends(get_auth),
):
    """Get hash query audit log."""
    global registry

    if not registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")

    # Restrict to own agency unless admin
    if agency and agency != auth.agency_id:
        raise HTTPException(status_code=403, detail="Can only view own agency logs")

    return registry.get_query_log(agency=auth.agency_id)


@app.get("/api/v1/audit/custody")
async def get_custody_statistics(auth: AgencyAuth = Depends(get_auth)):
    """Get custody statistics."""
    global custody

    if not custody:
        raise HTTPException(status_code=503, detail="Custody not initialized")

    return custody.get_statistics()


# ===== Error Handlers =====

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# ===== Application Factory =====

def create_app() -> FastAPI:
    """Factory function for creating the application."""
    return app
