# Airtable Lakeflow Connector - Changelog

## [v1.2.0] - 2026-01-08

### Workspace Deployment - Production Ready

**Major Update:** Complete solution for Workspace deployment using official Lakeflow UI tool.

**What's New:**
- ✅ **Official UI Tool Support** - Deploy via +New → Community connectors
- ✅ **Workspace Deployment** - Works without Repos access
- ✅ **Robust Credential Retrieval** - Multiple fallback methods for UC connection
- ✅ **Enhanced sys.path Setup** - Reliable imports in /Workspace/ folders
- ✅ **Better Error Handling** - Clear messages at every step
- ✅ **Complete Documentation** - WORKSPACE_DEPLOYMENT.md with step-by-step guide

**How It Works:**
1. Official Lakeflow UI tool clones GitHub repo to /Workspace/
2. `ingest.py` sets up Python paths for /Workspace/ compatibility
3. Credentials retrieved from UC via SQL query (2 fallback methods)
4. Connector runs on driver only (no serialization to workers)
5. `@dlt.table` decorators define tables
6. Simple data distributed to workers (no complex objects)

**Files Changed:**
- `ingest.py` - Complete rewrite for Workspace deployment
- `WORKSPACE_DEPLOYMENT.md` - NEW: Complete deployment guide
- `README.md` - Updated for v1.2.0 and Workspace deployment
- `CHANGELOG.md` - This file

**Deployment Methods:**
1. **Official UI Tool** (Recommended): +New → Community connectors → Point to GitHub
2. **Manual Upload**: Upload files to /Workspace/ and create DLT pipeline

**Key Benefits:**
- ✅ No Repos access required
- ✅ No explicit credentials
- ✅ No serialization issues
- ✅ Works with official Lakeflow UI tool
- ✅ Comprehensive error handling

---

## [v1.1.0] - 2026-01-08

### Official Lakeflow Pattern Restoration

**Critical Change:** Reverted to official Lakeflow pattern that uses UC connection automatically.

**What Changed:**
- ✅ Restored `ingest.py` to use official pattern
- ✅ Credentials automatically retrieved from UC connection (NO explicit access)
- ✅ NO `spark.conf.get()` for credentials
- ✅ NO Databricks secrets configuration
- ✅ NO pipeline configuration for credentials

**Why:**
- User requirement: Zero explicit credentials anywhere in code or configuration
- Official Lakeflow pattern handles credential injection automatically via Spark Data Source API
- Simpler, cleaner, more secure

**Files Changed:**
- `ingest.py` - Restored official pattern
- `docs/DEPLOYMENT.md` - Updated to reflect automatic credential handling
- Removed `SIMPLIFIED_PATTERN.md` (violated requirement)

---

### Table Name Sanitization (v1.0.1)

**Problem:** Table names with spaces, special characters, or starting with numbers caused SQL parsing errors.

**Solution:** Centralized `sanitize_table_name()` function with comprehensive logic:

**Sanitization Rules:**
1. Convert to lowercase
2. Replace spaces, hyphens with underscores
3. Remove parentheses, brackets, braces
4. Remove special characters (keep only alphanumeric + underscore)
5. Replace multiple underscores with single underscore
6. Remove leading/trailing underscores
7. Prepend 'table_' if starts with digit

**Examples:**
| Input | Output |
|-------|--------|
| `Packaging Tasks` | `packaging_tasks` |
| `Creative Requests` | `creative_requests` |
| `My-Table (2024)` | `my_table_2024` |
| `123StartWithNumber` | `table_123startwithnumber` |

**Files Changed:**
- `libs/spec_parser.py` - Added `sanitize_table_name()` function
- `pipeline/ingestion_pipeline.py` - Uses centralized sanitization

**Impact:**
- ✅ View names: All auto-generated staging views use sanitized names
- ✅ Destination tables: Default table names sanitized when not explicitly specified
- ✅ Consistency: Same sanitization logic everywhere
- ✅ Edge cases: Handles all special characters, numbers, spaces

---

## [v1.0.0] - 2026-01-08

### Initial Production Release

#### 1. DLT Integration - Declarative Pipeline Pattern
**Problem:** DLT pipeline failed with `[NO_TABLES_IN_PIPELINE]` error.

**Root Cause:** Custom `ingestion_pipeline.py` used imperative Spark operations instead of DLT's required declarative pattern.

**Fix:**
- Replaced custom implementation with official SDP (Spark Declarative Pipeline) pattern
- Added `@sdp.view()` decorators for DLT table recognition
- Implemented proper DLT functions:
  - `_create_cdc_table()` with `sdp.apply_changes()`
  - `_create_snapshot_table()` with `sdp.apply_changes_from_snapshot()`
  - `_create_append_table()` with `@sdp.append_flow()`

**Files Changed:**
- `pipeline/ingestion_pipeline.py` - Replaced with official implementation
- `libs/spec_parser.py` - Added official SpecParser from Databricks Labs
- `ingest.py` - Updated spec format to match SpecParser

---

#### 2. Metadata Query Error Fix
**Problem:** `[DATA_SOURCE_OPTION_NOT_ALLOWED_BY_CONNECTION] Option get_metadata is not allowed` error.

**Root Cause:** Official ingestion pipeline tried to use `get_metadata=true` option, which isn't supported by UC connections.

**Fix:**
- Changed metadata query to use the metadata table (`_lakeflow_metadata`)
- Added graceful fallback to default values when metadata not available
- Default behavior: snapshot ingestion with "id" as primary key
- Metadata can be overridden in pipeline spec via `table_configuration`

**Files Changed:**
- `pipeline/ingestion_pipeline.py` - Updated `_get_table_metadata()` to query metadata table

---

#### 3. API URL Normalization
**Problem:** API requests failing with 404 errors due to URL path duplication (e.g., `/v0/v0/...`).

**Root Cause:** Unity Catalog connections may include `/v0` in the base URL, causing duplication when constructing API endpoints.

**Fix:**
- Added URL normalization in connector methods
- Strip trailing `/` and `/v0` before constructing API endpoints
- Applied to: `list_tables()`, `get_table_schema()`, `read_table()`

**Files Changed:**
- `sources/airtable/airtable.py` - Added base_url normalization

---

#### 4. Import Path Corrections
**Problem:** `ModuleNotFoundError: No module named 'libs.source_loader'` errors in Databricks.

**Root Cause:** Incorrect import paths - should be `libs.common.source_loader`.

**Fix:**
- Corrected import statements across codebase
- Standardized directory structure

**Files Changed:**
- `ingest.py` - Fixed import from `libs.common.source_loader`
- `ingest_local.py` - Fixed import paths for local testing

---

#### 5. Pipeline Spec Format Update
**Problem:** Validation errors for missing fields (`default_catalog`, `default_schema`, `base_id`).

**Root Cause:** Spec format didn't match official SpecParser requirements.

**Fix:**
- Updated to official pipeline spec format
- Moved global defaults to per-table settings
- Each table now specifies: `destination_catalog`, `destination_schema`, `destination_table`

---

#### 6. Codebase Cleanup & Consolidation
**Actions Taken:**
- Removed stale documentation files
- Consolidated all fixes into this CHANGELOG.md
- Kept essential documentation in `docs/` directory:
  - `DEPLOYMENT.md`
  - `LOCAL_TESTING.md`
  - `TROUBLESHOOTING.md`

---

### Features

✅ **Table Discovery:** Automatically discover tables in Airtable base
✅ **Schema Inference:** Map Airtable field types to Spark types
✅ **Delta Lake Integration:** Write to Unity Catalog tables
✅ **Column Sanitization:** Handle special characters in column names
✅ **Table Name Sanitization:** Auto-sanitize table names with spaces/special chars
✅ **Retry Logic:** Exponential backoff for API failures
✅ **Incremental Sync:** Support for `createdTime`-based incremental reads
✅ **Full Refresh:** Snapshot mode for complete data reload
✅ **SCD Support:** Type 1 and Type 2 slowly changing dimensions
✅ **Unity Catalog:** Secure credential management (automatic injection)
✅ **DLT Compatible:** Full Delta Live Tables integration
✅ **Local Testing:** Test connector logic outside Databricks
✅ **Zero Explicit Credentials:** UC connection handles everything
✅ **Workspace Deployment:** Works without Repos access

---

### Known Limitations

1. **Metadata API:** Connector doesn't implement `get_metadata` option (uses fallback defaults)
2. **Incremental Sync:** Based on `createdTime` only (no custom cursor support yet)
3. **Nested Objects:** Complex Airtable types flatten to JSON strings

---

### Configuration Options

#### In Unity Catalog Connection
- `bearer_token` - Airtable Personal Access Token (required)
- `base_id` - Airtable base ID (required)
- `base_url` - API base URL (default: `https://api.airtable.com/v0`)

#### In ingest.py (per table)
- `source_table` - Table name in Airtable (required)
- Destination is defined in `@dlt.table` decorator

---

### Repository

- **GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector
- **Branch:** main
- **License:** Apache 2.0

---

### Credits

Built on the Databricks Lakeflow Community Connectors framework.

Reference: https://github.com/databrickslabs/lakeflow-community-connectors

---

## Summary of Changes

| Version | Key Changes |
|---------|-------------|
| **v1.2.0** | ✅ Workspace deployment, Official UI tool support, Robust credential retrieval |
| **v1.1.0** | ✅ Restored official pattern (zero explicit credentials) |
| **v1.0.1** | ✅ Added comprehensive table name sanitization |
| **v1.0.0** | ✅ DLT integration, metadata fix, API normalization, spec updates |

---

## Breaking Changes

### v1.2.0
- **Deployment Method:** Now optimized for Workspace deployment via official UI tool
- **Pattern:** Simplified pattern (no Python Data Source serialization)

### v1.1.0
- **Credential Handling:** Removed all explicit credential access. UC connection now required.

### v1.0.1
- **Table Names:** Auto-sanitization may change default destination table names. Explicitly set `destination_table` if you need specific names.

### v1.0.0
- **Pipeline Spec Format:** Changed from global defaults to per-table settings
- **Import Paths:** Changed from `libs.source_loader` to `libs.common.source_loader`
- **Ingestion Pipeline:** Now requires official SDP-based implementation

---

## Migration Guide

### To v1.2.0 (Current)

1. **Ensure UC connection exists:**
   ```sql
   DESCRIBE CONNECTION airtable;
   ```

2. **Deploy via official UI tool:**
   - +New → Add or upload data → Community connectors
   - Point to GitHub: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`

3. **Or manually upload to /Workspace/**
   - Follow WORKSPACE_DEPLOYMENT.md

4. **No configuration keys needed!**

---

**Current Version:** v1.2.0  
**Status:** Production Ready  
**Pattern:** Simplified (No Serialization)  
**Deployment:** Workspace (Official UI Tool)
