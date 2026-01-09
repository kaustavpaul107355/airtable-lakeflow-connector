# Airtable Lakeflow Connector - Changelog

## [v1.3.0 - Final] - 2026-01-09

### Ready for Expert Review

**Status:** Implementation complete, deployment blocked by serialization issue.

**What's Complete:**
- ✅ Connector implementation (`sources/airtable/airtable.py`)
- ✅ Framework integration (`pipeline/ingestion_pipeline.py`)
- ✅ Local testing (all tests pass)
- ✅ Documentation (comprehensive)
- ✅ Follows official Lakeflow pattern per expert guidance

**Current Issue:**
- ❌ Serialization error when deployed to `/Workspace/`
- Error: `ModuleNotFoundError: No module named 'pipeline'`
- Root cause: Python Data Source API serialization fails in `/Workspace/`
- See `CURRENT_ISSUE.md` for detailed analysis

**Expert Guidance Implemented:**
1. ✅ "Connector should not access UC connection" - Connector receives credentials from Spark engine
2. ✅ "UC integration handled by template and engine" - Framework uses `spark.read.format("lakeflow_connect")`
3. ✅ "UC connection supports arbitrary key-value pairs" - Connection stores all required options

**Files Changed:**
- `README.md` - Updated for expert review submission
- `CURRENT_ISSUE.md` - NEW: Detailed issue documentation
- `CHANGELOG.md` - This file
- `docs/WORKSPACE_DEPLOYMENT.md` - Moved from root (consolidated)

**Questions for Experts:**
1. Is `/Repos/` deployment required for official pattern?
2. How to make `/Workspace/` deployment work?
3. Should we use wheel packaging?
4. Any other deployment approach?

---

## [v1.2.0] - 2026-01-08

### Workspace Deployment Attempt

**Changes:**
- Attempted simplified pattern to bypass serialization
- Added sys.path manipulation for `/Workspace/`
- Multiple credential retrieval methods
- Enhanced error handling

**Result:** Still encountered serialization issues with official pattern.

**Learning:** Official pattern requires proper Python packaging that `/Workspace/` doesn't provide.

---

## [v1.1.0] - 2026-01-08

### Official Pattern Restoration

**Changes:**
- Restored official pattern using `pipeline/ingestion_pipeline.py`
- Removed manual UC credential queries
- Framework handles UC integration via Spark engine

**Key Insight:** Per expert guidance, connector should never access UC directly.

---

## [v1.0.1] - 2026-01-08

### Table Name Sanitization

**Problem:** Table names with spaces/special characters caused SQL parsing errors.

**Solution:** Centralized `sanitize_table_name()` function.

**Rules:**
1. Convert to lowercase
2. Replace spaces, hyphens with underscores
3. Remove special characters
4. Handle leading digits

**Examples:**
| Input | Output |
|-------|--------|
| `Packaging Tasks` | `packaging_tasks` |
| `Creative Requests` | `creative_requests` |
| `My-Table (2024)` | `my_table_2024` |

---

## [v1.0.0] - 2026-01-08

### Initial Production Release

#### Major Features

1. **DLT Integration**
   - Official SDP (Spark Declarative Pipeline) pattern
   - `@sdp.view()` decorators
   - CDC, SCD Type 1/2, append-only support

2. **Metadata Handling**
   - Query `_lakeflow_metadata` table
   - Graceful fallback to defaults
   - Override via `table_configuration`

3. **API URL Normalization**
   - Strip trailing `/` and `/v0`
   - Prevent URL duplication

4. **Import Path Corrections**
   - Fixed: `libs.common.source_loader` (not `libs.source_loader`)
   - Standardized directory structure

5. **Pipeline Spec Format**
   - Per-table settings (not global defaults)
   - Each table specifies catalog, schema, table name

---

## Features Summary

### Connector Features
- ✅ Table Discovery - Automatically discover tables in Airtable base
- ✅ Schema Inference - Map Airtable field types to Spark types
- ✅ Delta Lake Integration - Write to Unity Catalog tables
- ✅ Column Sanitization - Handle special characters
- ✅ Table Name Sanitization - Auto-sanitize names with spaces/special chars
- ✅ Retry Logic - Exponential backoff for API failures
- ✅ Incremental Sync - `createdTime`-based incremental reads
- ✅ SCD Support - Type 1 and Type 2 slowly changing dimensions
- ✅ Unity Catalog - Secure credential management (engine-handled)
- ✅ DLT Compatible - Full Delta Live Tables integration
- ✅ Local Testing - Validate connector logic independently

### Framework Compliance
- ✅ Implements `LakeflowConnect` interface
- ✅ No UC connection access in connector
- ✅ Framework handles UC integration
- ✅ Uses official SDP pattern
- ✅ Supports Unity Catalog connections
- ✅ Proper error handling and logging

---

## Known Limitations

1. **Deployment:** Serialization error in `/Workspace/` (needs expert guidance)
2. **Metadata API:** Doesn't implement `get_metadata` option (uses fallback)
3. **Incremental Sync:** Based on `createdTime` only
4. **Nested Objects:** Complex Airtable types flatten to JSON strings

---

## Configuration

### Unity Catalog Connection
```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_token',
  base_id 'your_base_id',
  base_url 'https://api.airtable.com/v0'
);
```

### Pipeline Specification
```python
pipeline_spec = {
    "connection_name": "airtable",
    "objects": [
        {
            "table": {
                "source_table": "Table Name",
                "destination_catalog": "main",
                "destination_schema": "default",
                "destination_table": "table_name",
            }
        }
    ]
}
```

---

## Repository

- **GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector
- **Branch:** main
- **License:** Apache 2.0
- **Framework:** https://github.com/databrickslabs/lakeflow-community-connectors

---

## Version Summary

| Version | Status | Key Changes |
|---------|--------|-------------|
| **v1.3.0** | ✅ Ready for Review | Final documentation, issue analysis |
| **v1.2.0** | ⚠️ Attempted | Workspace deployment attempts |
| **v1.1.0** | ✅ Correct Pattern | Official pattern per expert guidance |
| **v1.0.1** | ✅ Feature | Table name sanitization |
| **v1.0.0** | ✅ Initial | Production release |

---

## Breaking Changes

### v1.3.0
- **Documentation:** Restructured for expert review
- **Issue:** Serialization error documented in CURRENT_ISSUE.md

### v1.1.0
- **Credential Handling:** Removed all explicit UC access
- **Pattern:** Must use official framework pattern

### v1.0.1
- **Table Names:** Auto-sanitization may change default names

### v1.0.0
- **Pipeline Spec:** Changed from global to per-table settings
- **Import Paths:** Changed to `libs.common.source_loader`

---

## Migration Guide

### Current State (v1.3.0)

**For Experts Reviewing:**
1. Clone repository: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`
2. Review `CURRENT_ISSUE.md` for detailed problem analysis
3. Local testing works: `python ingest_local.py`
4. Deployment blocked: Serialization error in `/Workspace/`

**Need Guidance On:**
- Proper deployment method for official pattern
- `/Repos/` vs `/Workspace/` requirements
- Wheel packaging approach
- Any missing framework requirements

---

**Current Version:** v1.3.0 (Final - Ready for Expert Review)  
**Status:** Implementation Complete, Deployment Blocked  
**Contact:** kaustav.paul@databricks.com  
**Date:** January 9, 2026
