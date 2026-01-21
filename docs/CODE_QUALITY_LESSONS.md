# Code Quality Standards - Lessons Learned
**Purpose:** Copy this section to your Sanctuary Builders MasterInstructions.md

---

## 🛠️ **Pre-Commit Quality Gates**

### **Rule: No Code Lands Without Passing Lint**

All Python projects must:
1. Use **Black** formatter (100 char line length)
2. Use **Ruff** linter (fixes most issues automatically)
3. Have **pre-commit hooks** installed
4. Run `pytest` before push

### **Install Pre-Commit (One-Time Setup)**
```bash
pip install pre-commit
pre-commit install  # Hooks run automatically on every commit
```

### **Manual Cleanup Commands**
```bash
# Fix everything automatically
python -m ruff check --fix src/ tests/
python -m black src/ tests/ examples/

# Verify clean
python -m pytest -q
python -m ruff check src/ tests/
python -m black --check src/ tests/
```

---

## 🚫 **Common Errors & Prevention**

| Error Code | Name | Cause | Fix |
|------------|------|-------|-----|
| **W293** | Whitespace on blank line | Editor left spaces | Black auto-removes |
| **B904** | Missing exception chain | `raise X` without `from` | `raise X from err` |
| **ARG002** | Unused argument | Function param not used | `# noqa: ARG002` if intentional |
| **E501** | Line too long | >100 chars | Black auto-wraps |
| **F401** | Unused import | Import not used | Ruff auto-removes |
| **F841** | Unused variable | Variable assigned but not used | Remove or prefix with `_` |

---

## 📁 **File Standards**

- **Encoding:** UTF-8 always
- **Line endings:** LF (Unix style)
- **Indentation:** 4 spaces (never tabs)
- **Final newline:** Yes (files end with blank line)
- **Trailing whitespace:** Never (on any line)
- **Max line length:** 100 characters

---

## 🎯 **AI Agent Instructions**

When generating Python code, AI agents MUST:

1. **Before finishing any code task:**
   - Mentally run Black formatting rules
   - Check for trailing whitespace
   - Ensure exception chains use `from`
   - Add type hints to functions

2. **Never generate:**
   - Trailing whitespace on blank lines
   - Lines over 100 characters
   - Bare `raise Exception()` without `from err`
   - Unused imports or variables

3. **Always generate:**
   - Type hints on public functions
   - Docstrings on modules, classes, public functions
   - Explicit `from err` on re-raised exceptions

---

## 📋 **pyproject.toml Template Section**

Add this to any new Python project:

```toml
[tool.black]
line-length = 100
target-version = ["py311", "py312"]

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "W", "B", "I", "UP", "S", "ARG"]
ignore = ["S101"]  # Allow assert in tests

[tool.ruff.per-file-ignores]
"tests/*" = ["S101", "ARG"]
```

---

## ✅ **Pre-Commit Config Template**

Use `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        args: ['--line-length=100']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: ['--fix']
```

---

## 🔄 **Session Lesson: Failing Fast is Learning**

> "Failing is equal to smooth runs... this is how we improve not through playing it safe."

CI failures teach us:
- What standards we missed
- What automation we need
- Where our documentation gaps are

**Capture every failure. Document the fix. Prevent recurrence.**
