# Databricks Repos Setup - Quick Start

## Overview

We've identified the correct pattern used by [official Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors): **Databricks Repos** for proper Python package structure.

**Key Insight:** The GitHub examples (HubSpot, Salesforce, etc.) don't use wheels - they use Repos directly!

## Why This is the Solution

**The Problem We've Been Having:**
- `ModuleNotFoundError: No module named 'pipeline'`
- Custom data source serialization fails
- Workers can't import modules

**The Root Cause:**
- Workspace files (`/Workspace/...`) don't provide proper Python packaging
- `sys.path` manipulation doesn't work for serialized objects

**The Solution:**
- Use Databricks Repos (`/Repos/...`) - provides proper Python package environment
- Same as GitHub examples
- No wheel building needed
- No Git push required (manual upload works!)

## Quick Setup (3 Steps)

### Step 1: Create Base Folder (UI)

1. Go to [Databricks Workspace](https://e2-dogfood.staging.cloud.databricks.com)
2. Click **"Repos"** in sidebar
3. Right-click your username → **"Create"** → **"Folder"**
4. Name: `airtable-connector`
5. Creates: `/Repos/kaustav.paul@databricks.com/airtable-connector`

### Step 2: Upload Files (CLI)

```bash
cd /path/to/airtable-connector
./upload_to_repos.sh staging
```

This uploads all Python files to Repos structure.

### Step 3: Configure DLT Pipeline

**Minimum Configuration:**

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
  "development": true,
  "serverless": true
}
```

**Key Points:**
- ✅ Entry point: `/Repos/.../sdp_ingest/airtable_sdp_repos.py`
- ✅ No `libraries.whl` needed
- ✅ No `configuration` section (UC provides credentials)
- ✅ No `root_path` needed

## What Makes This Work

| Aspect | Workspace Files | Databricks Repos |
|--------|----------------|------------------|
| Python packaging | ❌ Limited | ✅ Proper |
| Module imports | ❌ sys.path hacks | ✅ Native |
| Serialization | ❌ Fails | ✅ Works |
| Pattern match | ❌ Custom | ✅ Official |

## Files Created

- `sdp_ingest/airtable_sdp_repos.py` - DLT pipeline for Repos
- `upload_to_repos.sh` - Upload script
- `REPOS_MANUAL_DEPLOYMENT.md` - Full documentation

## Next Steps

1. **Create base folder** in Databricks UI (Step 1 above)
2. **Run upload script:** `./upload_to_repos.sh staging`
3. **Create/update DLT pipeline** with Repos path
4. **Start pipeline** - should work without `ModuleNotFoundError`!

## Expected Result

✅ No `ModuleNotFoundError`  
✅ Custom data source registers  
✅ UC connection resolved  
✅ 6 bronze tables created  
✅ Data ingested successfully  
✅ **Matches official GitHub pattern!**

## References

- [Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)
- [HubSpot Example](https://github.com/databrickslabs/lakeflow-community-connectors/tree/master/sources/hubspot)
- Full docs: `REPOS_MANUAL_DEPLOYMENT.md`

