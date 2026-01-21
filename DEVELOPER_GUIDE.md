# CHILD GUARDIANS - Developer Guide

This guide covers everything needed to develop, test, and deploy CHILD GUARDIANS.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Development Setup](#development-setup)
4. [Testing](#testing)
5. [API Reference](#api-reference)
6. [Deployment](#deployment)
7. [Security Considerations](#security-considerations)

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/child-guardians/child-guardians.git
cd child-guardians

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Verify installation
python scripts/verify_installation.py

# Run tests
pytest

# Start development server
make run
```

---

## Architecture Overview

### Core Components

```
child_guardians/
├── core/
│   ├── evidence_object.py    # Court-safe evidence container
│   ├── hash_registry.py      # Known CSAM hash database
│   ├── chain_of_custody.py   # Append-only audit trail
│   └── defense_simulator.py  # Pre-export validation (35 challenges)
├── api/
│   └── main.py               # FastAPI REST endpoints
├── config.py                 # Configuration management
└── cli.py                    # Command-line interface
```

### Data Flow

```
[Evidence Collection]
        ↓
[EvidenceObject Creation]
        ↓
[Hash Computation & Registry Check]
        ↓
[Chain of Custody Logging]
        ↓
[Pre-flight Validation]
        ↓
[Defense Simulation (35 Challenges)]
        ↓
[Cryptographic Sealing]
        ↓
[Court Export]
```

### Key Design Principles

1. **Evidence is born court-safe** - Not fixed later
2. **Append-only audit trail** - Cannot be deleted
3. **Cryptographic integrity** - Every step is hashed and signed
4. **Pre-export validation** - Defense simulator catches errors before court
5. **Jurisdiction-aware** - Permission maps embedded in every evidence object

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional, for containerized testing)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | development/staging/production | development |
| `SECRET_KEY` | Cryptographic secret (generate for production) | - |
| `DATABASE_URL` | Database connection string | sqlite:///data/child_guardians.db |
| `LOG_LEVEL` | Logging level | INFO |

### Code Style

We use:
- **Black** for formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
make format

# Check linting
make lint

# Type check
make type-check

# Run all checks
make check
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=child_guardians --cov-report=html

# Specific test file
pytest tests/test_evidence_object.py

# Specific test
pytest tests/test_evidence_object.py::TestEvidenceObject::test_seal_and_verify
```

### Test Categories

| Test File | Component | Tests |
|-----------|-----------|-------|
| `test_evidence_object.py` | EvidenceObject | Creation, validation, sealing, serialization |
| `test_hash_registry.py` | HashRegistry | Registration, lookup, batch checking |
| `test_chain_of_custody.py` | ChainOfCustody | Event recording, chain verification |
| `test_defense_simulator.py` | DefenseSimulator | 35 challenge evaluation |
| `test_api.py` | REST API | All endpoints |

### Writing Tests

```python
import pytest
from child_guardians.core.evidence_object import EvidenceObject

class TestMyFeature:
    @pytest.fixture
    def my_fixture(self):
        # Setup code
        return SomeObject()
    
    def test_something(self, my_fixture):
        result = my_fixture.do_something()
        assert result == expected
```

---

## API Reference

### Authentication

All API requests require authentication headers:

```
X-Agency-ID: FBI-CYBERCRIMES
X-Officer-ID: OFF-12345
X-Officer-Name: John Doe
X-Badge-Number: 98765
```

### Endpoints

#### Health Check

```http
GET /health
```

Returns system health status.

#### Hash Registry

```http
POST /api/v1/hash/check
Content-Type: application/json

{
    "hash_type": "sha256",
    "hash_value": "abc123...",
    "case_reference": "CASE-2024-001",
    "legal_basis": "WARRANT-12345"
}
```

```http
POST /api/v1/hash/register
Content-Type: application/json

{
    "hash_type": "sha256",
    "hash_value": "abc123...",
    "confidence": "confirmed",
    "victim_status": "identified",
    "category": "csam_confirmed"
}
```

#### Evidence Management

```http
POST /api/v1/evidence/create
Content-Type: application/json

{
    "case_number": "CASE-2024-001",
    "evidence_type": "digital_image",
    "legal_basis_type": "warrant",
    "legal_basis_reference": "WARRANT-12345",
    ...
}
```

```http
GET /api/v1/evidence/{evidence_id}
POST /api/v1/evidence/{evidence_id}/hash
POST /api/v1/evidence/{evidence_id}/validate
POST /api/v1/evidence/{evidence_id}/simulate
```

#### Chain of Custody

```http
GET /api/v1/custody/{evidence_id}
POST /api/v1/custody/event
GET /api/v1/custody/{evidence_id}/verify
GET /api/v1/custody/{evidence_id}/export
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t child-guardians:latest .

# Run container
docker run -p 8000:8000 child-guardians:latest

# With docker-compose
docker-compose up -d
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f deploy/k8s/

# Check deployment
kubectl get pods -n child-guardians

# View logs
kubectl logs -f deployment/child-guardians-api -n child-guardians
```

### Production Checklist

- [ ] Generate secure `SECRET_KEY`
- [ ] Configure TLS termination
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring/alerting
- [ ] Review network policies
- [ ] Configure rate limiting
- [ ] Enable audit logging

---

## Security Considerations

### Data Protection

1. **Hash-Only Storage** - System stores ONLY hashes, never actual content
2. **Encryption at Rest** - Database should use encryption
3. **Encryption in Transit** - TLS required for all API calls
4. **Access Logging** - All queries logged for audit

### Key Management

```python
# Generate signing keys
from cryptography.hazmat.primitives.asymmetric import ed25519

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()
```

Keys should be:
- Generated per-agency
- Stored in secure key management (HSM recommended)
- Rotated annually
- Never stored in code or git

### Audit Trail

The system maintains complete audit trails:
- All hash queries logged
- All evidence access logged
- Chain of custody is append-only
- Cryptographic verification available

---

## Troubleshooting

### Common Issues

**Import Errors**
```bash
pip install -e .  # Reinstall package
python scripts/verify_installation.py  # Run verification
```

**Database Errors**
```bash
# Reset database (development only!)
rm -f data/*.db
```

**Test Failures**
```bash
pytest -v --tb=long  # Verbose output
pytest --pdb  # Drop into debugger on failure
```

### Getting Help

1. Check the [specs](specs/) documentation
2. Run the verification script
3. Check GitHub issues
4. Contact the development team

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make check`
5. Submit pull request

All contributions must:
- Pass all tests
- Include test coverage
- Follow code style guidelines
- Include documentation updates
