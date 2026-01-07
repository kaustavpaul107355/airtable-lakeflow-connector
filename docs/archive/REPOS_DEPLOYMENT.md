# Databricks Repos Deployment Guide

## Overview

This guide explains how to deploy the Airtable Lakeflow Connector using Databricks Repos for proper SDP/DLT integration.

## Why Databricks Repos?

**Workspace Files (`/Workspace/Users/...`):**
- ❌ Limited Python module import support
- ❌ Custom data source serialization issues
- ❌ Inconsistent `sys.path` handling

**Databricks Repos (`/Repos/...`):**
- ✅ Proper Python package structure
- ✅ Reliable module imports
- ✅ Custom data source serialization works
- ✅ **This is how official Lakeflow connectors work!**

## Prerequisites

1. **Unity Catalog Connection** created (already done):
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

2. **Git repository** (this repo!)

3. **Databricks workspace** with Repos enabled

## Deployment Steps

### Step 1: Set Up Git Integration

1. Go to **User Settings** → **Git Integration** in Databricks
2. Connect your Git provider (GitHub, GitLab, Azure DevOps, etc.)
3. Authorize access

### Step 2: Clone Repository to Databricks Repos

**Option A: Via UI**
1. Navigate to **Repos** in Databricks sidebar
2. Click **"Add Repo"**
3. Enter your Git repository URL
4. Clone to: `/Repos/kaustav.paul@databricks.com/airtable-connector`

**Option B: Via CLI**
```bash
databricks repos create \
  --url <your-git-repo-url> \
  --provider github \
  --path /Repos/kaustav.paul@databricks.com/airtable-connector \
  --profile staging
```

### Step 3: Verify Repo Structure

After cloning, verify the structure in Databricks Repos:

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
│   └── airtable_sdp_correct.py
├── pipeline-spec/
│   └── airtable_spec.py
└── README.md
```

### Step 4: Create/Update DLT Pipeline

**Pipeline Configuration (JSON):**

```json
{
  "name": "Airtable Lakeflow Connector (Repos)",
  "libraries": [
    {
      "notebook": {
        "path": "/Repos/kaustav.paul@databricks.com/airtable-connector/sdp_ingest/airtable_sdp_correct.py"
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
- ✅ Entry point: `/Repos/.../sdp_ingest/airtable_sdp_correct.py`
- ✅ No `root_path` needed (Repos handles this automatically)
- ✅ No configuration section needed (UC connection provides credentials)
- ✅ No hardcoded credentials!

### Step 5: Run the Pipeline

1. Go to **Workflows** → **Delta Live Tables** in Databricks
2. Find your pipeline
3. Click **"Start"**
4. Monitor the run in the pipeline UI

**Expected Output:**
- 6 bronze tables created:
  - `kaustavpaul_demo.airtable_connector.bronze_sku_candidates`
  - `kaustavpaul_demo.airtable_connector.bronze_launch_milestones`
  - `kaustavpaul_demo.airtable_connector.bronze_compliance_records`
  - `kaustavpaul_demo.airtable_connector.bronze_packaging_tasks`
  - `kaustavpaul_demo.airtable_connector.bronze_marketing_assets`
  - `kaustavpaul_demo.airtable_connector.bronze_vendors`

## How It Works

### UC Connection Resolution

```python
spark.read
  .format("lakeflow_connect")
  .option("databricks.connection", "airtable")  # ← UC connection name
  .option("tableName", "SKU Candidates")
  .load()
```

**What happens:**
1. DLT sees `.option("databricks.connection", "airtable")`
2. DLT queries Unity Catalog for connection details
3. UC returns: `bearer_token`, `base_id`, `base_url`
4. DLT passes these as options to `AirtableLakeflowConnector.__init__(options)`
5. Connector uses credentials to fetch data from Airtable
6. Data is written to Delta Lake

**No credentials in code!** ✅

### Repos Benefits

1. **Proper Python packaging**
   - `sys.path` automatically includes Repos path
   - Modules import correctly

2. **Serialization works**
   - Custom data sources can be pickled/unpickled
   - Workers have access to all modules

3. **Version control**
   - Changes tracked in Git
   - Easy rollback and collaboration

4. **SDP compliance**
   - Follows official Lakeflow pattern
   - Compatible with all DLT features

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Cause:** Files might still be uploaded as Workspace files instead of Repos

**Solution:**
1. Verify you're using `/Repos/...` path, not `/Workspace/...`
2. Check that files are visible in Databricks Repos UI
3. Ensure Python files have proper `__init__.py` files

### Issue: "UC connection not found"

**Cause:** UC connection not accessible from pipeline

**Solution:**
1. Verify UC connection exists: `DESCRIBE CONNECTION airtable;`
2. Ensure pipeline has permission to access UC connection
3. Check catalog/schema permissions

### Issue: "No records ingested"

**Cause:** Airtable credentials or table names incorrect

**Solution:**
1. Test UC connection: `DESCRIBE CONNECTION airtable;`
2. Verify token has access to Airtable base
3. Check table names match exactly (case-sensitive!)

## Local Development

For local testing without Repos:

1. Use `configs/dev_config.json` (gitignored)
2. Run `notebooks/test_airtable_connector.py`
3. Test individual functions before deploying

## Next Steps

1. ✅ Deploy to Repos (this guide)
2. Add data quality expectations in DLT
3. Create downstream silver/gold layers
4. Set up monitoring and alerts
5. Schedule pipeline runs

## References

- [Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)
- [Databricks Repos Documentation](https://docs.databricks.com/repos/index.html)
- [Delta Live Tables Documentation](https://docs.databricks.com/delta-live-tables/index.html)

