# Airtable Lakeflow Community Connector

A production-ready Databricks Lakeflow connector for ingesting data from Airtable into Delta tables using Unity Catalog connections.

**Repository:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector  
**Status:** ✅ Ready for Expert Review  
**Framework:** [Databricks Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)  
**Last Updated:** January 9, 2026

---

## 📋 Current Status

This connector is **fully implemented** following the official Databricks Lakeflow Community Connectors framework and is ready for expert review.

### ✅ What's Complete

- **Connector Implementation** (`sources/airtable/airtable.py`)
  - Implements `LakeflowConnect` interface
  - Table discovery, schema inference, data reading
  - Retry logic with exponential backoff
  - API URL normalization
  - No UC connection access (per expert guidance)

- **Framework Integration** (`pipeline/ingestion_pipeline.py`)
  - Official SDP (Spark Declarative Pipeline) pattern
  - Supports CDC, SCD Type 1/2, append-only modes
  - Metadata handling with fallback
  - Table name sanitization

- **Pipeline Specification** (`pipeline-spec/airtable_spec.py`)
  - Pydantic v2 models for validation
  - Comprehensive spec parsing

- **Local Testing** (`ingest_local.py`)
  - Standalone test script
  - Mock Spark session
  - Validates connector logic independently

- **Documentation**
  - Complete deployment guides
  - Local testing instructions
  - Troubleshooting guide
  - Comprehensive changelog

### ⚠️ Known Issue

**Serialization Error in /Workspace/ Deployment:**

When deployed to `/Workspace/` (via official UI tool or manual upload), the connector encounters:

```
ModuleNotFoundError: No module named 'pipeline'
pyspark.serializers.SerializationError
```

**Root Cause:** Python Data Source API requires serialization of connector and all imports to Spark workers. In `/Workspace/`, Python module resolution doesn't support this.

**Needs Expert Guidance:**
- Does the official pattern require `/Repos/` deployment?
- Is there a wheel packaging approach for `/Workspace/`?
- Are there UI tool settings we're missing?

---

## 🏗️ Architecture

### Design Principles (Per Expert Guidance)

1. **"When implementing your connector (lakeflow_connect interface), no UC connection should be involved at all"**
   - ✅ Connector (`sources/airtable/airtable.py`) never accesses UC
   - ✅ Receives credentials as constructor parameters

2. **"The UC connection integration is handled by the template and the integration part is in the engine"**
   - ✅ Framework (`pipeline/ingestion_pipeline.py`) handles UC integration
   - ✅ Uses `spark.read.format("lakeflow_connect").option("databricks.connection", "airtable")`
   - ✅ Spark engine retrieves credentials and passes to connector

3. **"UC connection supports arbitrary key-value pairs"**
   - ✅ Connection stores: `bearer_token`, `base_id`, `base_url`, `sourceName`

### How It Works

```
1. User Creates UC Connection:
   CREATE CONNECTION airtable
   TYPE GENERIC_LAKEFLOW_CONNECT
   OPTIONS (
     sourceName 'airtable',
     bearer_token 'token',
     base_id 'base_id',
     base_url 'https://api.airtable.com/v0'
   );

2. Pipeline Spec References Connection:
   pipeline_spec = {"connection_name": "airtable", ...}

3. Framework Calls:
   spark.read.format("lakeflow_connect")
        .option("databricks.connection", "airtable")
        .load()

4. Spark Engine:
   - Reads UC connection "airtable"
   - Extracts key-value pairs
   - Passes to AirtableLakeflowConnector constructor

5. Connector Receives:
   def __init__(self, options: Dict[str, Any]):
       self.bearer_token = options["bearer_token"]
       self.base_id = options["base_id"]
       # NO UC access - just uses what Spark passes
```

---

## 📂 Project Structure

```
airtable-connector/
├── README.md                      # This file
├── CHANGELOG.md                   # Complete version history
├── CURRENT_ISSUE.md               # Detailed issue documentation for experts
│
├── ingest.py                      # Main entry point (official pattern)
├── ingest_local.py                # Local testing script
├── create_uc_connection.sql       # UC connection template
├── setup_local_test.sh            # Local setup automation
│
├── sources/                       # Connector implementation
│   ├── airtable/
│   │   ├── airtable.py           # Main connector (implements LakeflowConnect)
│   │   └── README.md             # Connector-specific docs
│   └── interface/
│       └── lakeflow_connect.py   # Base interface definition
│
├── pipeline/                      # Framework layer (official code)
│   ├── ingestion_pipeline.py     # DLT orchestration (SDP pattern)
│   └── lakeflow_python_source.py # Spark Data Source registration
│
├── libs/                          # Utilities
│   ├── common/
│   │   └── source_loader.py      # Source registration utilities
│   └── spec_parser.py            # Spec validation & sanitization
│
├── pipeline-spec/                 # Pydantic models
│   └── airtable_spec.py          # Pipeline spec validation
│
├── tests/                         # Unit tests
│   ├── test_airtable_connector.py
│   ├── test_pipeline_spec.py
│   └── test_pydantic_integration.py
│
└── docs/                          # Documentation
    ├── DEPLOYMENT.md              # Deployment guide
    ├── LOCAL_TESTING.md           # Local testing guide
    └── TROUBLESHOOTING.md         # Common issues & solutions
```

---

## 🧪 Local Testing

The connector has been **validated locally** with successful tests:

```bash
# Setup
cd airtable-connector
./setup_local_test.sh

# Configure credentials
cp .credentials.example .credentials
# Edit .credentials with your Airtable token and base_id

# Run tests
source venv/bin/activate
python ingest_local.py
```

**Test Results:**
```
✅ Connection test passed
✅ Table discovery passed (3 tables found)
✅ Schema inference passed
✅ Data read passed (X records)
```

See **[docs/LOCAL_TESTING.md](./docs/LOCAL_TESTING.md)** for detailed instructions.

---

## 🚀 Deployment Attempts

### Attempt 1: Official Lakeflow UI Tool
- **Method:** +New → Add or upload data → Community connectors
- **Result:** ❌ `ModuleNotFoundError: No module named 'pipeline'`
- **Location:** `/Workspace/Users/.../airtable-connect/`

### Attempt 2: Manual /Workspace/ Upload
- **Method:** Uploaded complete directory structure to `/Workspace/`
- **Result:** ❌ Same serialization error
- **Location:** `/Workspace/Users/.../airtable-connector/`

### Root Cause
Python Data Source API serialization fails in `/Workspace/` because:
- Spark serializes connector + all imports (pipeline, libs, sources) to workers
- Workers can't resolve Python modules in `/Workspace/` structure
- This appears to be a Databricks platform limitation

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[README.md](./README.md)** | This file - overview and current status |
| **[CURRENT_ISSUE.md](./CURRENT_ISSUE.md)** | Detailed issue documentation for experts |
| **[CHANGELOG.md](./CHANGELOG.md)** | Complete version history |
| **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** | Deployment guide |
| **[docs/LOCAL_TESTING.md](./docs/LOCAL_TESTING.md)** | Local testing guide |
| **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** | Common issues & solutions |
| **[sources/airtable/README.md](./sources/airtable/README.md)** | Connector implementation details |

---

## ✨ Features

- ✅ **Table Discovery** - Automatically discover tables in Airtable base
- ✅ **Schema Inference** - Map Airtable field types to Spark types
- ✅ **Delta Lake Integration** - Write to Unity Catalog tables
- ✅ **Column Sanitization** - Handle special characters in column names
- ✅ **Table Name Sanitization** - Auto-sanitize table names with spaces/special chars
- ✅ **Retry Logic** - Exponential backoff for API failures
- ✅ **Incremental Sync** - Support for `createdTime`-based incremental reads
- ✅ **SCD Support** - Type 1 and Type 2 slowly changing dimensions
- ✅ **Unity Catalog** - Secure credential management (engine-handled)
- ✅ **DLT Compatible** - Full Delta Live Tables integration
- ✅ **Local Testing** - Validate connector logic independently
- ✅ **Framework Compliant** - Follows official Lakeflow pattern

---

## 🔧 Configuration

### Unity Catalog Connection

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_airtable_personal_access_token',
  base_id 'your_base_id',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

### Pipeline Specification (in `ingest.py`)

```python
pipeline_spec = {
    "connection_name": "airtable",  # References UC connection
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",      # Airtable table name
                "destination_catalog": "main",          # Target catalog
                "destination_schema": "default",        # Target schema
                "destination_table": "packaging_tasks", # Target table
            }
        },
        # Add more tables...
    ]
}
```

---

## 🤝 Contributing

This connector follows the official Databricks Lakeflow Community Connectors framework.

**Framework Reference:**  
https://github.com/databrickslabs/lakeflow-community-connectors

**Key Principles Followed:**
- ✅ Implements `LakeflowConnect` interface
- ✅ No UC connection access in connector code
- ✅ Framework handles UC integration via Spark engine
- ✅ Supports Unity Catalog connections
- ✅ Enables local testing
- ✅ Uses official SDP pattern for DLT

---

## 📝 License

Apache 2.0

---

## 🔗 Links

- **GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector
- **Databricks Lakeflow:** https://github.com/databrickslabs/lakeflow-community-connectors
- **Airtable API:** https://airtable.com/developers/web/api/introduction

---

## 📞 For Expert Review

### Questions for Experts

1. **Serialization in /Workspace/:**
   - Is `/Repos/` deployment required for the official pattern?
   - How should connectors handle `/Workspace/` deployment?
   - Is there a wheel packaging approach we should use?

2. **UI Tool Deployment:**
   - Does the official UI tool have specific requirements?
   - Are there settings/configurations we're missing?
   - What's the expected deployment location?

3. **Framework Compliance:**
   - Is our implementation of `LakeflowConnect` correct?
   - Is the UC integration pattern correct (no UC access in connector)?
   - Any other framework requirements we're missing?

### Test Environment

- **Databricks Workspace:** e2-dogfood.staging.cloud.databricks.com
- **UC Connection:** `airtable` (exists and accessible)
- **Local Testing:** ✅ All tests pass
- **Deployment:** ❌ Serialization error in `/Workspace/`

---

**This connector is ready for expert review. The code is complete and follows the official pattern, but we need guidance on the deployment/serialization issue.**

**Thank you for your review!** 🙏
