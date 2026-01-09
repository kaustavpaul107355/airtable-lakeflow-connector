# Current Issue - Serialization Error in /Workspace/ Deployment

**Date:** January 9, 2026  
**Status:** Blocked - Needs Expert Guidance  
**Repository:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector

---

## 📋 Summary

The Airtable Lakeflow connector is **fully implemented** following the official framework pattern, but encounters a **serialization error** when deployed to `/Workspace/` (the only available deployment location for this user).

---

## ✅ What's Working

### 1. Local Testing - ✅ All Tests Pass

```bash
$ python ingest_local.py

✅ Connection test passed
✅ Table discovery passed (3 tables found: Packaging Tasks, Campaigns, Creative Requests)
✅ Schema inference passed
✅ Data read passed (50+ records fetched successfully)
```

**Conclusion:** Connector logic is correct and functional.

---

### 2. Code Implementation - ✅ Follows Official Pattern

Per expert guidance received:

> "when implementing your connector (lakeflow_connect interface), no UC connection should be involved at all. The UC connection integration is handled by the template and the integration part is in the engine."

**Our Implementation:**

**Connector (`sources/airtable/airtable.py`):**
```python
class AirtableLakeflowConnector(LakeflowConnect):
    def __init__(self, options: Dict[str, Any]):
        # Receives credentials from Spark engine - NO UC access
        self.bearer_token = options["bearer_token"]
        self.base_id = options["base_id"]
        self.base_url = options.get("base_url", "https://api.airtable.com/v0")
        # ... rest of initialization
```

**Framework (`pipeline/ingestion_pipeline.py`):**
```python
def _create_snapshot_table(...):
    @sdp.view(name=view_name)
    def v():
        return (
            spark.readStream.format("lakeflow_connect")
            .option("databricks.connection", connection_name)  # ← Engine handles UC
            .option("tableName", source_table)
            .load()
        )
```

**Entry Point (`ingest.py`):**
```python
from pipeline.ingestion_pipeline import ingest
from libs.common.source_loader import get_register_function

pipeline_spec = {"connection_name": "airtable", ...}

register_lakeflow_source = get_register_function("airtable")
register_lakeflow_source(spark)
ingest(spark, pipeline_spec)
```

**Conclusion:** Code follows official pattern correctly.

---

## ❌ What's Not Working

### Deployment Error - Serialization Failure

**Error Message:**
```
com.databricks.pipelines.UnresolvedDatasetException: Failed to read dataset 'packaging_tasks_staging'

pyspark.errors.exceptions.captured.AnalysisException: 
[PYTHON_DATA_SOURCE_ERROR] Failed to create Python data source instance:

ModuleNotFoundError: No module named 'pipeline'

pyspark.serializers.SerializationError: Caused by Traceback:
  File "/databricks/spark/python/pyspark/serializers.py", line 194, in _read_with_length
    return self.loads(obj)
  File "/databricks/spark/python/pyspark/serializers.py", line 702, in loads
    return cloudpickle.loads(obj, encoding=encoding)
ModuleNotFoundError: No module named 'pipeline'
```

**Location:**
```
File "/Workspace/Users/kaustav.paul@databricks.com/airtable-connect/airtable-connect/pipeline/ingestion_pipeline.py", line 60
```

---

## 🔍 Root Cause Analysis

### What's Happening

1. **Driver Node:**
   - Registers `AirtableLakeflowConnector` as Spark Data Source
   - Creates connector instance with all imports (`pipeline`, `libs`, `sources`)

2. **Serialization:**
   - Spark's Python Data Source API serializes connector to send to workers
   - Serialization includes connector class + all imported modules

3. **Worker Nodes:**
   - Receive serialized connector
   - Attempt to deserialize and import modules
   - **FAIL:** Can't find `pipeline` module in Python path

### Why It Fails in /Workspace/

**In `/Workspace/`:**
- Files are just stored as workspace objects
- Python module resolution doesn't work for Data Sources
- `sys.path` doesn't include workspace paths for worker nodes
- Workers can't import `pipeline`, `libs`, `sources` modules

**Expected in `/Repos/`:**
- Git-backed folders with proper Python package structure
- Databricks handles Python path setup automatically
- Workers can resolve module imports

---

## 🚀 Deployment Attempts

### Attempt 1: Official Lakeflow UI Tool

**Method:**
1. Databricks UI: +New → Add or upload data → Community connectors
2. Pointed to GitHub: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`
3. UI tool cloned code to `/Workspace/Users/kaustav.paul@databricks.com/airtable-connect/`

**Result:** ❌ Serialization error

---

### Attempt 2: Manual /Workspace/ Upload

**Method:**
1. Uploaded complete directory structure to `/Workspace/`
2. Created DLT pipeline via UI
3. Pointed to `ingest.py`

**Result:** ❌ Same serialization error

---

### Attempt 3: Added sys.path Manipulation

**Method:**
Added to `ingest.py`:
```python
import sys
import os
current_dir = os.path.dirname(dbutils.notebook.entry_point...)
sys.path.insert(0, current_dir)
```

**Result:** ❌ Still fails - `sys.path` on driver doesn't affect workers

---

## 🤔 Questions for Experts

### 1. Deployment Location

**Question:** Does the official Lakeflow pattern require `/Repos/` deployment?

**Context:**
- User doesn't have `/Repos/` access in their workspace
- Official UI tool deploys to `/Workspace/`
- All attempts in `/Workspace/` fail with serialization error

**Options:**
- A) `/Repos/` is required - user needs access
- B) `/Workspace/` should work - we're missing something
- C) Different deployment method needed (wheel package?)

---

### 2. UI Tool Behavior

**Question:** How does the official UI tool handle Python packaging/serialization?

**Context:**
- UI tool successfully clones code to `/Workspace/`
- But doesn't solve serialization issue
- Are there settings/configurations we're missing?

**Expected:**
- Does UI tool set up Python paths?
- Does it package code differently?
- Should it deploy to `/Repos/` instead?

---

### 3. Wheel Packaging

**Question:** Should connectors be packaged as wheel files for `/Workspace/` deployment?

**Context:**
- We have `pyproject.toml` configured
- Could build wheel and upload to DBFS
- Would this solve the serialization issue?

**Approach:**
```bash
python -m build
# Upload wheel to DBFS
# Reference in DLT pipeline libraries
```

---

### 4. Framework Requirements

**Question:** Are there specific framework requirements for deployment we're missing?

**Context:**
- Code follows official pattern (per expert guidance)
- Local testing works perfectly
- Only deployment fails

**Checklist:**
- ✅ Implements `LakeflowConnect` interface
- ✅ No UC access in connector
- ✅ Uses official `pipeline/ingestion_pipeline.py`
- ✅ Registers via `libs.common.source_loader`
- ✅ Uses SDP decorators
- ❓ Missing deployment requirement?

---

## 📊 Environment Details

### Databricks Workspace
- **URL:** e2-dogfood.staging.cloud.databricks.com
- **User:** kaustav.paul@databricks.com
- **Access:** `/Workspace/` only (no `/Repos/` access)

### Unity Catalog Connection
```sql
-- Connection exists and is accessible
DESCRIBE CONNECTION airtable;

-- Output:
-- connection_name: airtable
-- connection_type: GENERIC_LAKEFLOW_CONNECT
-- options: {sourceName: airtable, bearer_token: ***, base_id: ***, base_url: https://api.airtable.com/v0}
```

### DLT Pipeline Configuration
```json
{
  "name": "Airtable Lakeflow Connector",
  "libraries": [
    {
      "notebook": {
        "path": "/Workspace/Users/kaustav.paul@databricks.com/airtable-connect/airtable-connect/ingest.py"
      }
    }
  ],
  "target": "main.default",
  "continuous": false,
  "development": true,
  "photon": true,
  "serverless": true
}
```

---

## 🎯 What We Need

### Immediate Need

**Clear guidance on ONE of these approaches:**

1. **Get /Repos/ Access**
   - If `/Repos/` is required, user will request access
   - Confirm this is the only supported deployment method

2. **Fix /Workspace/ Deployment**
   - Provide steps to make official pattern work in `/Workspace/`
   - Explain what we're missing

3. **Use Wheel Packaging**
   - Confirm wheel packaging is the right approach
   - Provide deployment steps for wheel-based deployment

4. **Alternative Approach**
   - If official pattern doesn't support `/Workspace/`, what's the alternative?
   - Is there a different connector pattern for this scenario?

---

## 📁 Repository Structure

```
airtable-connector/
├── ingest.py                      # Entry point (official pattern)
├── sources/airtable/airtable.py   # Connector implementation
├── pipeline/ingestion_pipeline.py # Framework (official SDP)
├── libs/common/source_loader.py   # Registration utilities
├── pipeline-spec/airtable_spec.py # Pydantic models
├── tests/                         # Unit tests (all pass)
└── docs/                          # Complete documentation
```

**All code available at:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector

---

## ✅ What's Ready for Review

1. **✅ Connector Implementation** - Fully functional (local tests pass)
2. **✅ Framework Integration** - Follows official pattern
3. **✅ Documentation** - Comprehensive guides and docs
4. **✅ UC Integration** - Correct pattern (no UC access in connector)
5. **❌ Deployment** - Blocked by serialization issue

---

## 🙏 Request for Expert Guidance

We've implemented the connector correctly per the official framework, but are blocked on deployment due to the serialization issue in `/Workspace/`.

**Please advise on:**
1. Is `/Repos/` deployment required?
2. How to make `/Workspace/` deployment work?
3. Should we use wheel packaging?
4. Any other deployment approach we should try?

**Thank you for your guidance!**

---

**Contact:** kaustav.paul@databricks.com  
**Repository:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector  
**Date:** January 9, 2026
