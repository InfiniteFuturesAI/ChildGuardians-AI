# Contributing to CHILD GUARDIANS

Thank you for your interest in contributing to child protection infrastructure.

---

## 📋 **Documentation Status Markers**

All contributions must use these markers consistently:

| Marker | Meaning | Use When |
|--------|---------|----------|
| 💡 **THEORETICAL** | Requires testing | New concepts, untested ideas |
| 🔬 **TESTING PROTOCOL** | Ready to validate | Test specifications |
| 📋 **DESIGN SPECIFICATION** | Ready to implement | Approved designs |
| ⚙️ **IN DEVELOPMENT** | Currently building | Active work |
| ✅ **VALIDATED** | Empirically confirmed | Tested with data |
| ❌ **FAILED TEST** | Valuable negative result | Learning from failures |
| ⏳ **REQUIRES PILOT** | Needs real-world testing | Pre-deployment |
| 🚀 **OPERATIONAL** | Production ready | Fully deployed |

---

## 🔲 **Failure Capture Doctrine**

> **If a system cannot produce an auditable failure artifact, it is not allowed to operate at speed.**

### **Required Practices:**

1. **Tests must capture failure context** - What was believed at moment of failure
2. **Failed tests are preserved** - ❌ markers indicate learning, not shame
3. **Chain of custody for failures** - Who, what, when, why
4. **Reconstruction capability** - Can we replay the failure?

### **When Your Code Fails:**

```python
# BAD: Silent failure
try:
    process_evidence(evidence)
except Exception:
    pass  # ❌ Lost learning opportunity

# GOOD: Failure artifact
try:
    process_evidence(evidence)
except Exception as e:
    failure_artifact = {
        "timestamp": datetime.now(UTC).isoformat(),
        "evidence_state": evidence.to_dict(),
        "error": str(e),
        "traceback": traceback.format_exc(),
        "context": {"what_we_believed": "..."}
    }
    log_failure_artifact(failure_artifact)
    raise
```

---

## 🔒 **Security Hygiene**

### **NEVER Include:**
- Real case numbers or law enforcement references
- Real officer names, badge numbers, or agency identifiers
- Real victim identifiers or case details
- Real CSAM hash values (even known ones)
- Production credentials, API keys, or tokens
- PII (names, emails, addresses, phone numbers)

### **ALWAYS Use:**
- Synthetic/demo data labeled "DEMO ONLY"
- Obviously fake identifiers (e.g., `FBI-AGENT-001`, `SA-12345`)
- `example.com` or `agency.example.gov` for domains
- `DEMO_ONLY_XXXXXXXX` for credential placeholders

---

## 🧪 **Testing Requirements**

### **Before Submitting:**

```bash
# Run all tests
pytest

# Run linting
ruff check src/ tests/

# Run formatting check
black --check src/ tests/

# Run type checking
mypy src/
```

### **Test Philosophy:**

- **Disprove vigorously** - Try to break your theories
- **Improve code when tests fail** - Not the tests
- **Accept negative results** - They teach truth
- **Report effect sizes honestly** - No exaggeration

---

## 📝 **Pull Request Process**

1. **Create feature branch** from `main`
2. **Add tests** for new functionality
3. **Run full test suite** locally
4. **Update documentation** if behavior changed
5. **Add status markers** to new docs
6. **Submit PR** with clear description

### **PR Checklist:**
- [ ] Tests pass locally
- [ ] Linting passes
- [ ] No real credentials or PII
- [ ] Demo data labeled appropriately
- [ ] Status markers applied
- [ ] Documentation updated

---

## 🎯 **Mission Alignment**

Every contribution should:

- ✅ **Protect children** through better evidence handling
- ✅ **Preserve legal admissibility** of evidence
- ✅ **Respect jurisdictional boundaries** by design
- ✅ **Prevent procedural errors** before they occur
- ✅ **Enable oversight** not surveillance

---

## 🚨 **What We Won't Accept**

- ❌ Code that bypasses evidence integrity controls
- ❌ Features that enable surveillance
- ❌ Changes that compromise legal admissibility
- ❌ Anything that could harm victims
- ❌ Contributions that violate the noncommercial license

---

## 📫 **Questions?**

Open an issue with the `question` label.

---

**Status:** ✅ **VALIDATED** - Contributing guidelines established
