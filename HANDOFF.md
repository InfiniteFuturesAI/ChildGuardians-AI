# CHILD GUARDIANS - Handoff Guide

## For Receiving Teams: What You're Getting

This repository contains a **production-ready implementation** of the CHILD GUARDIANS evidence management system. Everything needed to deploy, test, and extend is included.

---

## Repository Structure

```
ChildGuardians AI/
├── README.md                    # Project overview
├── COVER_LETTER.md              # For policymakers
├── HOW_TO_REVIEW.md             # Audience-specific reading paths
├── DEVELOPER_GUIDE.md           # This file's technical companion
│
├── docs/                        # Policy & legal documentation
│   ├── CHARTER.md               # Non-negotiable design principles
│   ├── DEPLOYMENT_GUIDE.md      # Law enforcement pilot guide
│   ├── WHAT_THIS_SYSTEM_WILL_NEVER_DO.md
│   ├── SURVEILLANCE_EXCLUSION.md
│   └── LEGAL_APPENDICES.md
│
├── specs/                       # Technical specifications
│   ├── EVIDENCE_OBJECT.md       # Court-safe evidence schema
│   ├── FAILURE_MODES.md         # 50 failure modes with guardrails
│   ├── DEFENSE_SIMULATOR.md     # 35 challenge questions
│   ├── INDUSTRIAL_MAGNET.md     # Dark web monitoring
│   ├── WATCHDOG.md              # Independent oversight
│   ├── GJEP.md                  # Global evidence plane
│   ├── CIVIS_CYBER.md           # Investigator interface
│   ├── VICTIM_ENGINE.md         # Re-victimization prevention
│   ├── ECP.md                   # Ethical content prevention
│   └── API.md                   # Integration endpoints
│
├── src/child_guardians/         # Python implementation
│   ├── core/
│   │   ├── evidence_object.py   # ~400 lines, fully documented
│   │   ├── hash_registry.py     # ~350 lines, SQLite-backed
│   │   ├── chain_of_custody.py  # ~300 lines, append-only
│   │   └── defense_simulator.py # ~600 lines, 35 challenges
│   ├── api/
│   │   └── main.py              # FastAPI REST endpoints
│   ├── config.py                # Environment configuration
│   └── cli.py                   # Command-line interface
│
├── tests/                       # Comprehensive test suite
│   ├── test_evidence_object.py  # 15+ test cases
│   ├── test_hash_registry.py    # 15+ test cases
│   ├── test_chain_of_custody.py # 12+ test cases
│   ├── test_defense_simulator.py# 10+ test cases
│   └── test_api.py              # 20+ API tests
│
├── scripts/
│   └── verify_installation.py   # System verification
│
├── deploy/
│   └── k8s/
│       └── deployment.yaml      # Kubernetes manifests
│
├── .github/workflows/
│   └── ci.yml                   # CI/CD pipeline
│
├── Dockerfile                   # Production container
├── Dockerfile.dev               # Development container
├── docker-compose.yml           # Local orchestration
├── pyproject.toml               # Python project config
├── Makefile                     # Common commands
├── .env.example                 # Environment template
└── .gitignore
```

---

## Quick Verification (5 Minutes)

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Run verification script
python scripts/verify_installation.py

# 3. Run test suite
pytest -v

# 4. Start development server
make run

# 5. Check health endpoint
curl http://localhost:8000/health
```

Expected output from verification:
```
CHILD GUARDIANS - Installation Verification
============================================
Checking imports...
  ✓ child_guardians v0.1.0
  ✓ EvidenceObject
  ✓ HashRegistry
  ✓ ChainOfCustody
  ✓ DefenseSimulator
  ✓ FastAPI application

Testing evidence workflow...
  ✓ Evidence object created
  ✓ Material hash added
  ✓ Validation passed
  ✓ Defense simulation: score 85/100
  ✓ Evidence sealed
  ✓ Seal verified
  ✓ Serialization roundtrip

...

All checks passed! ✓
```

---

## What's Been Built

### Core Functionality (100% Complete)

| Component | Status | Lines | Tests |
|-----------|--------|-------|-------|
| Evidence Object | ✅ Complete | 400 | 15+ |
| Hash Registry | ✅ Complete | 350 | 15+ |
| Chain of Custody | ✅ Complete | 300 | 12+ |
| Defense Simulator | ✅ Complete | 600 | 10+ |
| REST API | ✅ Complete | 500 | 20+ |
| CLI | ✅ Complete | 250 | - |
| Configuration | ✅ Complete | 150 | - |

### Infrastructure (100% Complete)

| Component | Status |
|-----------|--------|
| Dockerfile (production) | ✅ |
| Dockerfile (development) | ✅ |
| docker-compose.yml | ✅ |
| Kubernetes manifests | ✅ |
| CI/CD pipeline | ✅ |
| Environment configuration | ✅ |

### Documentation (100% Complete)

| Document | Purpose |
|----------|---------|
| README.md | Project overview |
| COVER_LETTER.md | Policymaker summary |
| HOW_TO_REVIEW.md | Audience-specific paths |
| DEVELOPER_GUIDE.md | Technical development |
| All specs/*.md | Technical specifications |
| All docs/*.md | Policy documentation |

---

## Testing the Core Features

### 1. Evidence Object Lifecycle

```python
from child_guardians.core.evidence_object import (
    EvidenceObject, LegalBasis, LegalBasisType,
    CollectionDetails, JurisdictionMap, MaterialHash
)
from datetime import datetime, timezone, timedelta

# Create evidence
evidence = EvidenceObject(
    case_number="CASE-2024-001",
    evidence_type="digital_image",
    legal_basis=LegalBasis(
        basis_type=LegalBasisType.WARRANT,
        reference="WARRANT-12345",
        issued_by="Judge Smith",
        issued_date=datetime.now(timezone.utc),
        scope="Digital devices",
    ),
    collection_details=CollectionDetails(
        officer_id="OFF-001",
        officer_name="John Doe",
        badge_number="12345",
        agency="FBI",
        agency_unit="Cyber",
        collection_time=datetime.now(timezone.utc),
        collection_location="123 Main St",
        tool_used="FTK Imager",
        tool_version="4.7",
        tool_hash="abc123",
    ),
    jurisdiction=JurisdictionMap(
        primary_jurisdiction="US-VA",
        hosting_country="US",
        can_export_evidence=["FBI"],
    ),
)

# Add material hash
evidence.add_material_hash(MaterialHash(
    hash_type="sha256",
    hash_value="a" * 64,
    source_file="image.jpg",
    source_path="/evidence/image.jpg",
    computed_by="OFF-001",
))

# Validate
result = evidence.validate()
print(f"Validation passed: {result['passed']}")
```

### 2. Hash Registry

```python
from child_guardians.core.hash_registry import (
    HashRegistry, HashType, MatchConfidence, VictimStatus
)

registry = HashRegistry(":memory:")  # In-memory for testing

# Register known hash
registry.register(
    hash_type=HashType.SHA256,
    hash_value="known_csam_hash_here",
    confidence=MatchConfidence.CONFIRMED,
    victim_status=VictimStatus.IDENTIFIED,
    source_authority="FBI",
)

# Check a hash
result = registry.check(
    hash_type=HashType.SHA256,
    hash_value="suspicious_hash",
    querying_agency="Local PD",
    querying_officer="OFF-002",
)
print(f"Match found: {result.found}")
```

### 3. Defense Simulation

```python
from child_guardians.core.defense_simulator import DefenseSimulator

simulator = DefenseSimulator()
result = simulator.evaluate(evidence)

print(f"Score: {result['score']}/100")
print(f"Passed: {result['passed']}")
print(f"Blocking failures: {len(result['blocking_failures'])}")
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/api/v1/hash/check` | POST | Check hash against registry |
| `/api/v1/hash/register` | POST | Register new hash |
| `/api/v1/hash/batch` | POST | Batch hash check |
| `/api/v1/evidence/create` | POST | Create evidence object |
| `/api/v1/evidence/{id}` | GET | Get evidence |
| `/api/v1/evidence/{id}/hash` | POST | Add material hash |
| `/api/v1/evidence/{id}/validate` | POST | Run validation |
| `/api/v1/evidence/{id}/simulate` | POST | Run defense simulation |
| `/api/v1/custody/{id}` | GET | Get custody chain |
| `/api/v1/custody/event` | POST | Record custody event |
| `/api/v1/custody/{id}/verify` | GET | Verify chain integrity |

---

## Deployment Options

### Option 1: Local Development
```bash
make dev
make run
```

### Option 2: Docker
```bash
docker-compose up -d
```

### Option 3: Kubernetes
```bash
kubectl apply -f deploy/k8s/
```

---

## What's NOT Included (By Design)

1. **Actual CSAM hashes** - System works with placeholder data
2. **Real agency credentials** - Use your own authentication
3. **Production secrets** - Generate your own SECRET_KEY
4. **Perceptual hashing libraries** - PhotoDNA requires license; PDQ can be integrated

---

## Extending the System

### Adding New Challenge Questions

Edit `defense_simulator.py`:

```python
self.challenges.append(Challenge(
    id="NEW-001",
    category=ChallengeCategory.YOUR_CATEGORY,
    question="Your challenge question?",
    severity="critical",  # or "major" or "minor"
    evaluator=self._your_evaluator_method,
))
```

### Integrating External Hash Database

The `HashRegistry` class is designed to be swapped:

```python
class ExternalHashRegistry(HashRegistry):
    def check(self, ...):
        # Call external API instead of SQLite
        pass
```

### Adding New API Endpoints

Edit `api/main.py`:

```python
@app.post("/api/v1/your/endpoint")
async def your_endpoint(
    request: YourRequest,
    auth: AgencyAuth = Depends(get_auth),
):
    # Your implementation
    pass
```

---

## Cost of Implementation

| Item | Estimated Effort | Notes |
|------|------------------|-------|
| Deploy to staging | 1 day | Docker or Kubernetes |
| Connect to real hash DB | 1-2 weeks | API integration |
| Agency authentication | 1-2 weeks | OAuth/SAML integration |
| Production hardening | 2-4 weeks | Security review, pen testing |
| UI development | 4-8 weeks | If needed |

**Minimal viable deployment: 3 components, 3 weeks** (see `docs/DEPLOYMENT_GUIDE.md`)

---

## Questions?

The code is documented. The specs explain the "why." The tests show expected behavior.

If something is unclear:
1. Check the specification documents
2. Run the tests with `-v` for verbose output
3. Read the docstrings in the source code

This system was designed to be understood, tested, and extended by teams who receive it without the original author present.
