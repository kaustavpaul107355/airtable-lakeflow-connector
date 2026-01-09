# Deployment Guide

## ⚠️ Current Status

This connector is **ready for expert review** but encounters a serialization error when deployed to `/Workspace/`.

**For detailed issue analysis, see:** [../CURRENT_ISSUE.md](../CURRENT_ISSUE.md)

---

## 🧪 Local Testing - ✅ Works

The connector has been fully validated locally:

```bash
cd airtable-connector
./setup_local_test.sh
source venv/bin/activate
python ingest_local.py
```

**Result:**
```
✅ Connection test passed
✅ Table discovery passed (3 tables found)
✅ Schema inference passed
✅ Data read passed (50+ records)
```

**See:** [LOCAL_TESTING.md](./LOCAL_TESTING.md) for detailed instructions.

---

## 🚀 Databricks Deployment - ❌ Blocked

### Attempted Methods

#### Method 1: Official Lakeflow UI Tool
```
+New → Add or upload data → Community connectors
→ Point to GitHub repo
→ UI tool deploys to /Workspace/
→ ❌ Result: ModuleNotFoundError: No module named 'pipeline'
```

#### Method 2: Manual /Workspace/ Upload
```
Upload complete directory structure to /Workspace/
→ Create DLT pipeline via UI
→ Point to ingest.py
→ ❌ Result: Same serialization error
```

### Root Cause

**Python Data Source API Serialization:**
- Official pattern uses `spark.read.format("lakeflow_connect")`
- Spark serializes connector + all imports to workers
- Workers can't resolve `pipeline`, `libs`, `sources` modules in `/Workspace/`
- This appears to be a Databricks platform limitation

**Error:**
```
pyspark.serializers.SerializationError
ModuleNotFoundError: No module named 'pipeline'
```

---

## 📋 Prerequisites

### 1. Unity Catalog Connection

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_airtable_token',
  base_id 'your_base_id',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

**Verify:**
```sql
SHOW CONNECTIONS;
DESCRIBE CONNECTION airtable;
```

### 2. Code Repository

**GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector

---

## 🤔 Questions for Experts

### 1. Deployment Location
- Does the official pattern require `/Repos/` deployment?
- Can `/Workspace/` deployment work with proper configuration?

### 2. Packaging
- Should connector be packaged as a wheel file?
- How to handle Python module resolution for workers?

### 3. UI Tool
- Are there specific UI tool settings we're missing?
- Does UI tool expect different file structure?

### 4. Alternative Approaches
- Is there a different deployment method for `/Workspace/`?
- Any framework requirements we're missing?

---

## 📖 Additional Documentation

| Document | Description |
|----------|-------------|
| **[CURRENT_ISSUE.md](../CURRENT_ISSUE.md)** | Detailed issue analysis for experts |
| **[LOCAL_TESTING.md](./LOCAL_TESTING.md)** | Local testing guide (works perfectly) |
| **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** | Common issues & solutions |
| **[WORKSPACE_DEPLOYMENT.md](./WORKSPACE_DEPLOYMENT.md)** | Attempted workspace deployment steps |
| **[README.md](../README.md)** | Project overview |
| **[CHANGELOG.md](../CHANGELOG.md)** | Complete version history |

---

## ✅ What's Ready

1. **✅ Connector Implementation** - Fully functional (local tests pass)
2. **✅ Framework Integration** - Follows official pattern
3. **✅ UC Integration** - Correct pattern (no UC access in connector)
4. **✅ Documentation** - Comprehensive guides
5. **❌ Deployment** - Blocked by serialization issue

---

## 🙏 Need Expert Guidance

The connector is **complete and correct** per the official framework, but we need guidance on:

1. Proper deployment method for the official pattern
2. How to handle `/Workspace/` vs `/Repos/` requirements
3. Whether wheel packaging is needed
4. Any missing configuration or setup steps

**Please see [CURRENT_ISSUE.md](../CURRENT_ISSUE.md) for detailed analysis and specific questions.**

---

**Contact:** kaustav.paul@databricks.com  
**Repository:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector  
**Status:** Ready for Expert Review
