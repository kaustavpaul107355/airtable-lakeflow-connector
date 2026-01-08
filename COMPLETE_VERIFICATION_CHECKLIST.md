# ✅ Complete Verification Checklist

**Date:** January 7, 2026  
**Status:** Let's verify everything is correct before proceeding

---

## 📋 Part 1: Local Codebase Verification

### Core Connector Implementation

**Location:** `sources/airtable/airtable.py`

Verify this file contains:
- [ ] `AirtableLakeflowConnector` class
- [ ] Extends `LakeflowConnect` interface
- [ ] Methods: `__init__`, `list_tables`, `get_table_schema`, `read_table_metadata`, `read_table`
- [ ] Unity Catalog connection support (reads from `options` dict)
- [ ] No hardcoded credentials

**Quick Check:**
```bash
grep -q "class AirtableLakeflowConnector(LakeflowConnect)" sources/airtable/airtable.py && echo "✓ Class exists" || echo "✗ Class missing"
grep -q "def list_tables" sources/airtable/airtable.py && echo "✓ list_tables exists" || echo "✗ Missing method"
grep -q "def get_table_schema" sources/airtable/airtable.py && echo "✓ get_table_schema exists" || echo "✗ Missing method"
grep -q "def read_table" sources/airtable/airtable.py && echo "✓ read_table exists" || echo "✗ Missing method"
```

---

### Pipeline Specification

**Location:** `pipeline-spec/airtable_spec.py`

Verify this file contains:
- [ ] `AirtablePipelineSpec` class (Pydantic BaseModel)
- [ ] Fields: `connection_name`, `default_catalog`, `default_schema`, `objects`
- [ ] Pydantic v2 compatible (uses `@model_validator` not `@root_validator`)
- [ ] `load_pipeline_spec_from_dict` function

**Quick Check:**
```bash
grep -q "class AirtablePipelineSpec(BaseModel)" pipeline-spec/airtable_spec.py && echo "✓ Spec class exists" || echo "✗ Missing"
grep -q "@model_validator" pipeline-spec/airtable_spec.py && echo "✓ Pydantic v2 compatible" || echo "⚠ Check Pydantic version"
grep -q "connection_name.*str" pipeline-spec/airtable_spec.py && echo "✓ connection_name field exists" || echo "✗ Missing field"
```

---

### Framework Files

**Location:** `pipeline/`, `libs/`

Verify these exist:
- [ ] `pipeline/ingestion_pipeline.py` - Contains `ingest()` function
- [ ] `pipeline/lakeflow_python_source.py` - PySpark Data Source implementation
- [ ] `libs/common/source_loader.py` - Contains `get_register_function()`
- [ ] All `__init__.py` files present in every directory

**Quick Check:**
```bash
find . -name "__init__.py" | wc -l | xargs echo "Number of __init__.py files:"
test -f pipeline/ingestion_pipeline.py && echo "✓ ingestion_pipeline.py exists" || echo "✗ Missing"
test -f pipeline/lakeflow_python_source.py && echo "✓ lakeflow_python_source.py exists" || echo "✗ Missing"
test -f libs/common/source_loader.py && echo "✓ source_loader.py exists" || echo "✗ Missing"
```

---

### Tests

**Location:** `tests/`

Verify these exist:
- [ ] `test_airtable_connector.py` - Connector tests
- [ ] `test_pipeline_spec.py` - Spec validation tests
- [ ] `test_pydantic_integration.py` - Pydantic v2 tests
- [ ] `conftest.py` - Test fixtures

**Quick Check:**
```bash
ls tests/test_*.py | wc -l | xargs echo "Number of test files:"
```

---

### Documentation

Verify these exist:
- [ ] `README.md` - Main project documentation
- [ ] `INDEX.md` - Documentation navigation hub
- [ ] `OFFICIAL_APPROACH_GUIDE.md` - Deployment guide
- [ ] `CLEANUP_REPORT.md` - Cleanup documentation
- [ ] `GITHUB_SETUP.md` - GitHub setup instructions
- [ ] `docs/archive/` - Archived materials

**Quick Check:**
```bash
ls *.md | wc -l | xargs echo "Number of markdown docs:"
```

---

## 📋 Part 2: GitHub Repository Verification

### Repository Status

**URL:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector

Verify:
- [ ] Repository exists and is public
- [ ] All files pushed successfully
- [ ] No secrets in repository (credentials sanitized)
- [ ] README visible on main page
- [ ] Latest commit shows clean history

**Check Locally:**
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/databricks-starter/databricks-apps/airtable-connector
git remote -v
git status
git log --oneline -3
```

**Expected Output:**
```
origin  https://github.com/kaustavpaul107355/airtable-lakeflow-connector.git (fetch)
origin  https://github.com/kaustavpaul107355/airtable-lakeflow-connector.git (push)

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

### Security Check

Verify no secrets leaked:
- [ ] `.credentials` file is in `.gitignore`
- [ ] No tokens in `create_uc_connection.sql`
- [ ] `.credentials.example` has placeholders only

**Quick Check:**
```bash
# Should show .credentials is ignored
git check-ignore .credentials && echo "✓ .credentials ignored" || echo "✗ NOT ignored!"

# Should NOT find any real tokens
git log --all -p | grep -i "patkB" && echo "⚠ TOKEN FOUND IN HISTORY!" || echo "✓ No tokens in history"

# Check current files
grep "YOUR_AIRTABLE" create_uc_connection.sql && echo "✓ Placeholders used" || echo "⚠ Check for real tokens"
```

---

## 📋 Part 3: Connector Code Quality

### Interface Implementation

**File:** `sources/airtable/airtable.py`

Check if it properly implements `LakeflowConnect`:

```python
# Required methods from LakeflowConnect interface:
# 1. __init__(self, options: dict[str, str])
# 2. list_tables(self) -> list[str]
# 3. get_table_schema(self, table_name: str, ...) -> StructType
# 4. read_table_metadata(self, table_name: str, ...) -> dict
# 5. read_table(self, table_name: str, ...) -> (Iterator[dict], dict)
```

**Verify:**
- [ ] All 5 methods implemented
- [ ] Credentials read from `options` parameter (not hardcoded)
- [ ] Returns correct types (StructType, Iterator, etc.)
- [ ] Error handling present

---

### Pydantic v2 Compatibility

**File:** `pipeline-spec/airtable_spec.py`

Check for Pydantic v2 patterns:

```bash
# Should use @model_validator, NOT @root_validator
grep "@root_validator" pipeline-spec/airtable_spec.py && echo "⚠ Using deprecated Pydantic v1 syntax" || echo "✓ Pydantic v2 compatible"

# Should use model_validator with mode
grep "@model_validator(mode=" pipeline-spec/airtable_spec.py && echo "✓ Correct v2 syntax" || echo "⚠ Check validator syntax"

# Should use ConfigDict or model_config, NOT class Config
grep "class Config:" pipeline-spec/airtable_spec.py && echo "⚠ Using old Config class" || echo "✓ No old Config class"
```

---

## 📋 Part 4: Unity Catalog Connection

### UC Connection Configuration

**File:** `create_uc_connection.sql`

Verify:
- [ ] Uses `GENERIC_LAKEFLOW_CONNECT` type
- [ ] No real tokens (placeholders only)
- [ ] Includes `bearer_token`, `base_id`, `base_url` options
- [ ] Has clear comments/instructions

**The UC connection should look like:**
```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN',
  base_id 'YOUR_AIRTABLE_BASE_ID',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

---

## 📋 Part 5: Structure & Organization

### Directory Structure

Expected structure:
```
airtable-connector/
├── sources/
│   ├── __init__.py                    ← Required
│   ├── airtable/
│   │   ├── __init__.py                ← Required
│   │   ├── airtable.py                ← Main connector
│   │   └── README.md
│   └── interface/
│       ├── __init__.py                ← Required
│       └── lakeflow_connect.py
├── pipeline-spec/
│   ├── __init__.py                    ← Required
│   └── airtable_spec.py
├── pipeline/
│   ├── __init__.py                    ← Required
│   ├── ingestion_pipeline.py
│   └── lakeflow_python_source.py
├── libs/
│   ├── __init__.py                    ← Required
│   └── common/
│       ├── __init__.py                ← Required
│       └── source_loader.py
├── tests/
│   ├── __init__.py                    ← Required
│   ├── conftest.py
│   ├── test_airtable_connector.py
│   ├── test_pipeline_spec.py
│   └── test_pydantic_integration.py
├── docs/
│   └── archive/                       ← Archived materials
├── .gitignore                         ← Proper ignore rules
├── .credentials.example               ← Safe template
├── README.md
├── INDEX.md
├── OFFICIAL_APPROACH_GUIDE.md
└── requirements.txt
```

**Verify all __init__.py files exist:**
```bash
find . -type d \( -name sources -o -name pipeline -o -name libs -o -name tests -o -name pipeline-spec \) -exec sh -c 'for dir; do test -f "$dir/__init__.py" && echo "✓ $dir/__init__.py" || echo "✗ MISSING: $dir/__init__.py"; done' sh {} +
```

---

## 📋 Part 6: Dependencies

### Python Dependencies

**File:** `requirements.txt`

Verify it includes:
- [ ] `pydantic>=2.0.0` (for Pydantic v2)
- [ ] `pyairtable` (for Airtable API)
- [ ] `pyspark` (if needed for local testing)
- [ ] Any other dependencies your connector uses

**Check:**
```bash
grep -q "pydantic" requirements.txt && echo "✓ Pydantic listed" || echo "⚠ Missing pydantic"
grep -q "pyairtable" requirements.txt && echo "✓ pyairtable listed" || echo "⚠ Missing pyairtable"
```

---

## 📋 Part 7: What Could Be Missing

### Common Oversights

Based on the error you're seeing, check these:

1. **Package Structure in GitHub:**
   - [ ] Is the connector at repo root? Or in a subdirectory?
   - [ ] Does the UI tool know which directory contains the connector?

2. **Missing Manifest/Config:**
   - [ ] Does Lakeflow need an `app.yaml` or similar manifest?
   - [ ] Is there a specific config file the UI expects?

3. **Packaging:**
   - [ ] Does the connector need to be built as a wheel?
   - [ ] Is there a `setup.py` or `pyproject.toml` needed for packaging?

4. **Entry Point:**
   - [ ] Does the UI expect a specific entry point file name?
   - [ ] Should `ingest.py` be at repo root vs in a subdirectory?

---

## 📋 Part 8: Compare to Official Connectors

### Reference Check

Let's compare your structure to the official Lakeflow connectors:

**Official Repository:** https://github.com/databrickslabs/lakeflow-community-connectors

**Check if your structure matches:**
```bash
# If you have the official repo cloned:
ls -la lakeflow-community-connectors/sources/

# Look for patterns in existing connectors
# Compare their directory structure to yours
```

**Key things to check:**
1. Do official connectors have an `ingest.py` at a specific location?
2. Do they have additional config files you're missing?
3. What's in their `__init__.py` files?
4. Do they use a specific packaging method?

---

## ✅ Verification Commands

Run these commands from your connector directory:

```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/databricks-starter/databricks-apps/airtable-connector

echo "=== FILE STRUCTURE CHECK ==="
find . -name "*.py" -type f | grep -v __pycache__ | grep -v ".git" | sort

echo ""
echo "=== __init__.py FILES CHECK ==="
find . -name "__init__.py" | sort

echo ""
echo "=== CRITICAL FILES CHECK ==="
for file in \
  "sources/airtable/airtable.py" \
  "pipeline-spec/airtable_spec.py" \
  "pipeline/ingestion_pipeline.py" \
  "libs/common/source_loader.py" \
  ".gitignore" \
  ".credentials.example" \
  "requirements.txt"; do
  test -f "$file" && echo "✓ $file" || echo "✗ MISSING: $file"
done

echo ""
echo "=== DOCUMENTATION CHECK ==="
for file in README.md INDEX.md OFFICIAL_APPROACH_GUIDE.md; do
  test -f "$file" && echo "✓ $file" || echo "✗ MISSING: $file"
done

echo ""
echo "=== GIT STATUS ==="
git status --short
git remote -v

echo ""
echo "=== SECURITY CHECK ==="
git check-ignore .credentials && echo "✓ .credentials is ignored" || echo "⚠ .credentials NOT ignored!"
grep -q "YOUR_AIRTABLE" create_uc_connection.sql && echo "✓ No real tokens in SQL" || echo "⚠ Check SQL file"

echo ""
echo "=== DEPENDENCY CHECK ==="
grep -i "pydantic" requirements.txt
grep -i "pyairtable" requirements.txt

echo ""
echo "=== FILE COUNT ==="
echo "Python files: $(find . -name '*.py' -not -path './.git/*' -not -path '*/__pycache__/*' | wc -l)"
echo "Test files: $(find tests -name 'test_*.py' 2>/dev/null | wc -l)"
echo "Documentation: $(find . -maxdepth 1 -name '*.md' | wc -l)"
```

---

## 🎯 Final Verification Questions

Before proceeding with deployment, answer these:

### About Your Connector Code:
- [ ] Does your connector implement all required LakeflowConnect methods?
- [ ] Does it read credentials from the `options` dict (not hardcoded)?
- [ ] Is it Pydantic v2 compatible?
- [ ] Do all imports work locally?

### About Your GitHub Repo:
- [ ] Is the repo public and accessible?
- [ ] Are all files pushed successfully?
- [ ] No secrets leaked in history?
- [ ] README is clear and helpful?

### About UC Connection:
- [ ] Have you created the UC connection in Databricks?
- [ ] Does it use `GENERIC_LAKEFLOW_CONNECT` type?
- [ ] Are the credentials correct?
- [ ] Can you test the connection independently?

### About Deployment:
- [ ] Which UI did you use? (exact path)
- [ ] What did the UI create?
- [ ] Did you point it to your GitHub repo or upload files?
- [ ] What error did you get and when?

---

## 📝 Action Items

Based on this verification:

1. **Run the verification commands above** and note any failures
2. **Check your GitHub repo** - does structure match what's expected?
3. **Compare to official connectors** - any obvious differences?
4. **Document what the UI did** - exactly what got created in workspace?

Then we can identify exactly what's missing or wrong!

---

## 💡 Most Likely Issues

Based on typical deployment problems:

1. **Missing `ingest.py` at repo root** - UI might expect it there
2. **Missing manifest file** - UI might need `connector.yaml` or similar
3. **Wrong directory structure** - Connector should be at specific location
4. **UI not fully implemented** - Your workspace might not have full UI support yet
5. **Need to use CLI instead** - UI might be for different connector types

Let's verify everything first, then we'll know exactly what to fix! 🎯

