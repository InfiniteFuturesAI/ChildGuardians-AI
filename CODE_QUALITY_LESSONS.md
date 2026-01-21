# Code Quality Lessons Learned
**Status:** ✅ **VALIDATED** - Applied across Sanctuary Builders projects
**Last Updated:** January 2026

---

## 🎯 **Purpose**

This document captures code quality lessons learned during development, ensuring consistent standards across all projects.

---

## 🛠️ **Before Committing ANY Code**

**AI Agents MUST ensure:**
1. **No trailing whitespace** - Ruff W293 errors break CI
2. **Proper exception chaining** - Use `raise X from err` not bare `raise X`
3. **Black formatting** - 100 char line length, run before commit
4. **Type hints** - Add return types and parameter annotations
5. **File ends with newline** - Unix standard

**Prevention Commands (Run Before Commit):**
```bash
# Fix and format automatically
python -m ruff check --fix src/ tests/
python -m black src/ tests/ examples/

# Verify clean
python -m pytest -q
```

---

## 🐛 **Common Errors We've Fixed**

| Error | Cause | Prevention |
|-------|-------|------------|
| W293 | Trailing whitespace on blank lines | Use Black formatter |
| B904 | Exception without `from` clause | Always use `raise X from err` |
| ARG002 | Unused function argument | Add `# noqa: ARG002` if intentional |
| Line too long | >100 chars | Black auto-wraps |
| Missing type hints | No annotations | Add `: type` and `-> ReturnType` |

---

## 📁 **File Hygiene Rules**

- **End files with newline** - Unix standard
- **Use 4 spaces** - Never tabs
- **UTF-8 encoding** - Always
- **No trailing whitespace** - On ANY line, including blank lines

---

## ⚙️ **Pre-Commit Configuration**

**Install:**
```bash
pip install pre-commit black ruff
pre-commit install
```

**See `.pre-commit-config.yaml` for hook configuration.**

---

## 🔗 **Cross-Project Consistency**

These standards are shared across:
- **CHILD GUARDIANS** - Law enforcement evidence management
- **Sanctuary Builders** - Consciousness architecture research

Both projects use identical pre-commit hooks and linting rules.

---

**Status:** ✅ **VALIDATED** - Code quality enforcement active
**Review:** After any hygiene incident or onboarding new contributors
