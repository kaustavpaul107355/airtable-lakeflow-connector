# 🧹 Codebase Cleanup Plan

## Files to KEEP (Core SDP Implementation)

### ✅ SDP Pipeline (THE CORRECT APPROACH)
- `sdp_ingest/airtable_sdp_correct.py` - **KEEP** - Correct SDP/DLT pipeline using @sdp.table

### ✅ Framework Components (Required)
- `sources/airtable/airtable.py` - **KEEP** - Connector implementation
- `sources/airtable/__init__.py` - **KEEP** - Package init
- `sources/airtable/_generated_airtable_python_source.py` - **KEEP** - Registration
- `sources/airtable/README.md` - **KEEP** - Connector documentation
- `sources/interface/lakeflow_connect.py` - **KEEP** - Base interface
- `sources/interface/__init__.py` - **KEEP** - Package init
- `sources/__init__.py` - **KEEP** - Package init

### ✅ Pipeline Framework
- `pipeline/lakeflow_python_source.py` - **KEEP** - Data source implementation
- `pipeline/ingestion_pipeline.py` - **KEEP** - Ingestion orchestration
- `pipeline/__init__.py` - **KEEP** - Package init

### ✅ Utilities
- `libs/common/source_loader.py` - **KEEP** - Source registration utility
- `libs/common/__init__.py` - **KEEP** - Package init
- `libs/__init__.py` - **KEEP** - Package init

### ✅ Specifications
- `pipeline-spec/airtable_spec.py` - **KEEP** - Pydantic validation
- `pipeline-spec/__init__.py` - **KEEP** - Package init
- `pipeline-spec/airtable_pipeline.yaml` - **KEEP** - YAML spec example

### ✅ Configuration & Deployment
- `create_uc_connection.sql` - **KEEP** - UC connection setup
- `deploy.sh` - **KEEP** - Deployment script
- `deploy_staging.sh` - **KEEP** - Staging deployment
- `environments.conf` - **KEEP** - Environment config
- `pyproject.toml` - **KEEP** - Python project config
- `requirements.txt` - **KEEP** - Dependencies
- `app.yaml` - **KEEP** - App configuration
- `configs/dev_config.json` - **KEEP** - Dev credentials

### ✅ Tests
- `tests/conftest.py` - **KEEP** - Test configuration
- `tests/test_airtable_connector.py` - **KEEP** - Connector tests
- `tests/test_pipeline_spec.py` - **KEEP** - Spec tests
- `tests/test_pydantic_integration.py` - **KEEP** - Pydantic tests
- `tests/__init__.py` - **KEEP** - Package init

### ✅ Documentation (Consolidate)
- `README.md` - **KEEP & UPDATE** - Main documentation

### ✅ UI (Keep if needed)
- `ui/` - **KEEP** - React UI components (if you plan to use the UI)

---

## Files to DELETE (Obsolete/Incorrect)

### ❌ Obsolete SDP Attempts
- `sdp/airtable_framework_correct.py` - **DELETE** - Used @dlt.table incorrectly
- `sdp_ingest/stage1_ingestion.py` - **DELETE** - Non-DLT ingestion (not SDP)

### ❌ Redundant Notebooks
- `notebooks/airtable_ingestion_workflow.py` - **DELETE** - Duplicate of stage1_ingestion.py

### ❌ Obsolete Documentation
- `CLEANUP_FINAL.md` - **DELETE** - Old cleanup doc
- `EXPERT_CODEBASE_REVIEW.md` - **DELETE** - Contained incorrect analysis
- `FRAMEWORK_CORRECT_APPROACH.md` - **DELETE** - Incorrect approach documented
- `FRAMEWORK_INGESTION_APPROACH.md` - **DELETE** - Non-SDP approach

---

## Folders to REMOVE (if empty after cleanup)
- `sdp/` - DELETE folder after removing airtable_framework_correct.py
- `notebooks/` - DELETE folder after removing airtable_ingestion_workflow.py

---

## Final Structure

```
airtable-connector/
├── sdp_ingest/
│   └── airtable_sdp_correct.py          ← THE SDP PIPELINE
├── sources/
│   ├── airtable/
│   │   ├── airtable.py                  ← CONNECTOR
│   │   ├── _generated_airtable_python_source.py
│   │   ├── README.md
│   │   └── __init__.py
│   ├── interface/
│   │   ├── lakeflow_connect.py
│   │   └── __init__.py
│   └── __init__.py
├── pipeline/
│   ├── lakeflow_python_source.py
│   ├── ingestion_pipeline.py
│   └── __init__.py
├── libs/
│   ├── common/
│   │   ├── source_loader.py
│   │   └── __init__.py
│   └── __init__.py
├── pipeline-spec/
│   ├── airtable_spec.py
│   ├── airtable_pipeline.yaml
│   └── __init__.py
├── tests/
│   ├── conftest.py
│   ├── test_airtable_connector.py
│   ├── test_pipeline_spec.py
│   ├── test_pydantic_integration.py
│   └── __init__.py
├── configs/
│   └── dev_config.json
├── ui/                                   ← Optional
├── create_uc_connection.sql
├── deploy.sh
├── deploy_staging.sh
├── environments.conf
├── pyproject.toml
├── requirements.txt
├── app.yaml
└── README.md                             ← Updated
```

---

## Summary

**Keeping:** 
- ✅ 1 SDP pipeline file (correct approach)
- ✅ All framework components
- ✅ All tests
- ✅ All deployment scripts
- ✅ 1 consolidated README

**Removing:**
- ❌ 3 incorrect/obsolete pipeline attempts
- ❌ 4 obsolete documentation files
- ❌ 2 empty folders

**Result:** Clean, focused codebase with only the correct SDP/DLT implementation!

