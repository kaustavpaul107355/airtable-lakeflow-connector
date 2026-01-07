# Databricks Repos Deployment Guide (Manual Upload)

## Overview

This guide explains how to deploy the Airtable Lakeflow Connector using Databricks Repos **without Git integration**. We'll manually upload files to create a proper Python package structure.

## Why Databricks Repos?

Based on the [official Lakeflow Community Connectors repository](https://github.com/databrickslabs/lakeflow-community-connectors/tree/master/sources), connectors work properly in Repos because:

- ✅ **Proper Python package structure** - `/Repos/` provides correct module resolution
- ✅ **Custom data source serialization works** - Workers can import modules during deserialization
- ✅ **No manual `sys.path` manipulation** - Repos handles this automatically
- ✅ **Same environment as GitHub examples** - HubSpot, Salesforce, etc.

**Key Insight:** The GitHub examples don't use wheels - they use Repos directly!

## Prerequisites

1. **Unity Catalog Connection** (already created):
   ```sql
   CREATE CONNECTION airtable
   TYPE GENERIC_LAKEFLOW_CONNECT
   OPTIONS (
     sourceName 'airtable',
     bearer_token '<your_token>',
     base_id 'appSaRcgA5UCGoRg5',
     base_url 'https://api.airtable.com'
   );
   ```

2. **Databricks workspace** with Repos enabled

## Deployment Steps

### Step 1: Create Repos Folder (Manual - Via UI)

1. Go to **Repos** in Databricks sidebar
2. Click your username to expand
3. Create a new folder structure:
   - Right-click → **"Create"** → **"Folder"**
   - Name: `airtable-connector`
   - Full path: `/Repos/kaustav.paul@databricks.com/airtable-connector`

### Step 2: Upload Python Packages

Upload these directories to the Repos folder:

**Using Databricks CLI:**

```bash
# Navigate to your local airtable-connector directory
cd /path/to/airtable-connector

# Upload sources/
databricks workspace import-dir sources \
  /Repos/kaustav.paul@databricks.com/airtable-connector/sources \
  --profile staging

# Upload pipeline/
databricks workspace import-dir pipeline \
  /Repos/kaustav.paul@databricks.com/airtable-connector/pipeline \
  --profile staging

# Upload libs/
databricks workspace import-dir libs \
  /Repos/kaustav.paul@databricks.com/airtable-connector/libs \
  --profile staging

# Upload sdp_ingest/
databricks workspace import-dir sdp_ingest \
  /Repos/kaustav.paul@databricks.com/airtable-connector/sdp_ingest \
  --profile staging

# Upload pipeline-spec/ (optional, for validation)
databricks workspace import-dir pipeline-spec \
  /Repos/kaustav.paul@databricks.com/airtable-connector/pipeline-spec \
  --profile staging
```

**Or using deploy script:**

```bash
./deploy.sh staging repos
```

### Step 3: Verify Repos Structure

After uploading, verify in Databricks UI:

```
/Repos/kaustav.paul@databricks.com/airtable-connector/
├── sources/
│   ├── __init__.py
│   ├── interface/
│   │   ├── __init__.py
│   │   └── lakeflow_connect.py
│   └── airtable/
│       ├── __init__.py
│       ├── airtable.py
│       └── _generated_airtable_python_source.py
├── pipeline/
│   ├── __init__.py
│   ├── lakeflow_python_source.py
│   └── ingestion_pipeline.py
├── libs/
│   ├── __init__.py
│   └── common/
│       ├── __init__.py
│       └── source_loader.py
├── sdp_ingest/
│   └── airtable_sdp_repos.py
└── pipeline-spec/
    └── airtable_spec.py
```

**Important:** All files should be of type `FILE`, not `NOTEBOOK`. You can verify by checking file icons in the UI.

### Step 4: Create/Update DLT Pipeline

**Pipeline Configuration (JSON):**

```json
{
  "name": "Airtable Lakeflow Connector - Repos",
  "libraries": [
    {
      "notebook": {
        "path": "/Repos/kaustav.paul@databricks.com/airtable-connector/sdp_ingest/airtable_sdp_repos.py"
      }
    }
  ],
  "catalog": "kaustavpaul_demo",
  "schema": "airtable_connector",
  "continuous": false,
  "development": true,
  "photon": true,
  "channel": "CURRENT",
  "serverless": true
}
```

**Key Points:**
- ✅ Entry point: `/Repos/.../sdp_ingest/airtable_sdp_repos.py`
- ✅ No `libraries.whl` needed
- ✅ No `configuration` section needed (UC provides credentials)
- ✅ No `root_path` needed (Repos handles it)

**Via UI:**

1. Go to **Workflows** → **Delta Live Tables**
2. Click **"Create Pipeline"** or edit existing
3. Settings:
   - **Name:** `Airtable Lakeflow Connector - Repos`
   - **Notebook libraries:** `/Repos/kaustav.paul@databricks.com/airtable-connector/sdp_ingest/airtable_sdp_repos.py`
   - **Target:**
     - Catalog: `kaustavpaul_demo`
     - Schema: `airtable_connector`
   - **Development mode:** Enabled
4. Save

### Step 5: Run the Pipeline

1. Go to your DLT pipeline
2. Click **"Start"**
3. Monitor execution in the pipeline UI

**Expected Output:**
- ✅ No `ModuleNotFoundError`
- ✅ Custom data source registers successfully
- ✅ UC connection `airtable` resolved automatically
- ✅ 6 bronze tables created:
  - `kaustavpaul_demo.airtable_connector.bronze_sku_candidates`
  - `kaustavpaul_demo.airtable_connector.bronze_launch_milestones`
  - `kaustavpaul_demo.airtable_connector.bronze_compliance_records`
  - `kaustavpaul_demo.airtable_connector.bronze_packaging_tasks`
  - `kaustavpaul_demo.airtable_connector.bronze_marketing_assets`
  - `kaustavpaul_demo.airtable_connector.bronze_vendors`

## How It Works

### Repos Environment Benefits

**Without Repos (/Workspace/...):**
- ❌ Modules aren't proper packages
- ❌ `sys.path` manipulation required
- ❌ Workers can't import during deserialization
- ❌ `ModuleNotFoundError: No module named 'pipeline'`

**With Repos (/Repos/...):**
- ✅ Proper Python package environment
- ✅ Modules importable on all nodes
- ✅ Custom data source serializes correctly
- ✅ **Same as GitHub examples!**

### UC Connection Resolution

```python
spark.read
  .format("lakeflow_connect")
  .option("databricks.connection", "airtable")
  .option("tableName", "SKU Candidates")
  .load()
```

**What happens:**
1. DLT sees `.option("databricks.connection", "airtable")`
2. DLT queries Unity Catalog for connection details
3. UC returns: `bearer_token`, `base_id`, `base_url`
4. Options passed to `AirtableLakeflowConnector.__init__(options)`
5. Connector fetches data from Airtable
6. Data written to Delta Lake

**No credentials in code!** ✅

## Comparison: Workspace vs Repos

| Feature | Workspace Files | Databricks Repos |
|---------|----------------|------------------|
| Python packaging | ❌ Limited | ✅ Proper |
| Module imports | ❌ Requires sys.path | ✅ Automatic |
| Data source serialization | ❌ Fails | ✅ Works |
| Matches GitHub examples | ❌ No | ✅ Yes |
| Git integration required | N/A | ❌ No (manual upload) |
| SDP compliance | ⚠️ Workarounds needed | ✅ Native |

## Troubleshooting

### Issue: "No such file or directory" during upload

**Cause:** Repos folder doesn't exist

**Solution:**
1. Create the parent folder in Repos UI first
2. Then upload subdirectories via CLI

### Issue: "ModuleNotFoundError" still occurs

**Cause:** Files uploaded as NOTEBOOK type instead of FILE

**Solution:**
1. Check file types in Databricks UI
2. Re-upload using `--format SOURCE` flag:
   ```bash
   databricks workspace import file.py /Repos/.../file.py \
     --language PYTHON --format SOURCE --overwrite
   ```

### Issue: "UC connection not found"

**Cause:** UC connection not accessible

**Solution:**
1. Verify: `DESCRIBE CONNECTION airtable;`
2. Check permissions on UC connection
3. Ensure pipeline has access to catalog

## Updating the Connector

When you make changes locally:

```bash
# Upload specific changed files
databricks workspace import \
  --file sources/airtable/airtable.py \
  --language PYTHON --format SOURCE --overwrite \
  /Repos/kaustav.paul@databricks.com/airtable-connector/sources/airtable/airtable.py \
  --profile staging

# Or re-upload entire directory
databricks workspace import-dir sources \
  /Repos/kaustav.paul@databricks.com/airtable-connector/sources \
  --overwrite --profile staging
```

No DLT pipeline reconfiguration needed - just restart the pipeline!

## Key Differences from Workspace Deployment

1. **Path:** `/Repos/...` instead of `/Workspace/...`
2. **Package structure:** Properly handled by Repos
3. **No `sys.path` manipulation:** Not needed in pipeline code
4. **No wheel building:** Direct file upload works

## This is the Official Pattern!

According to [databrickslabs/lakeflow-community-connectors](https://github.com/databrickslabs/lakeflow-community-connectors), official connectors:
- ✅ Use Repos structure (not wheels)
- ✅ Rely on proper Python packaging
- ✅ Work with `.option("databricks.connection")`
- ✅ No hardcoded credentials

Your connector now follows the same pattern! 🎉

## References

- [Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)
- [Databricks Repos Documentation](https://docs.databricks.com/repos/index.html)
- [Delta Live Tables Documentation](https://docs.databricks.com/delta-live-tables/index.html)
- [Unity Catalog Connections](https://docs.databricks.com/data-governance/unity-catalog/connections.html)

