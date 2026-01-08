# Workspace Deployment Guide

## ✅ Complete Instructions for /Workspace/ Deployment (No Repos Access)

This guide is for deploying the Airtable connector to a Databricks Workspace folder when you don't have access to Repos.

---

## 📋 Prerequisites

1. ✅ Unity Catalog connection named `airtable` exists
2. ✅ Access to create DLT pipelines in your workspace
3. ✅ Write access to a folder in `/Workspace/Users/your.name@databricks.com/`

---

## 🗂️ Step 1: Upload Complete Directory Structure

You must upload **ALL** files maintaining the exact directory structure:

```
/Workspace/Users/your.name@databricks.com/airtable-connector/
├── ingest.py                          # Main entry point
│
├── sources/
│   ├── __init__.py
│   ├── airtable/
│   │   ├── __init__.py
│   │   └── airtable.py                # Connector implementation
│   └── interface/
│       ├── __init__.py
│       └── lakeflow_connect.py        # Base interface
│
├── libs/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   └── source_loader.py           # May be imported by other modules
│   └── spec_parser.py                 # Utility functions
│
└── pipeline-spec/
    ├── __init__.py
    └── airtable_spec.py                # Pydantic models
```

### How to Upload:

**Option A: Using Databricks UI**
1. Go to **Workspace** → **Users** → **your.name@databricks.com**
2. Click **Create** → **Folder** → Name it `airtable-connector`
3. For each file:
   - Click **Create** → **File**
   - Copy-paste content from GitHub
   - Save with correct name
4. Create subdirectories (`sources/`, `libs/`, etc.) and repeat

**Option B: Using Databricks CLI**
```bash
# Install Databricks CLI if not already installed
pip install databricks-cli

# Configure authentication
databricks configure --token

# Upload entire directory
databricks workspace import_dir \
  ./airtable-connector \
  /Users/your.name@databricks.com/airtable-connector \
  --overwrite
```

**Option C: Using Python Script**
```python
from databricks.sdk import WorkspaceClient
import os

w = WorkspaceClient()

def upload_directory(local_dir, remote_dir):
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            remote_path = f"{remote_dir}/{relative_path}"
            
            with open(local_path, 'r') as f:
                content = f.read()
            
            w.workspace.import_(
                path=remote_path,
                content=content.encode('utf-8'),
                format='SOURCE'
            )
            print(f"Uploaded: {remote_path}")

upload_directory(
    './airtable-connector',
    '/Users/your.name@databricks.com/airtable-connector'
)
```

---

## 🔧 Step 2: Verify Directory Structure

Run this in a Databricks notebook to verify:

```python
import os

base_path = "/Workspace/Users/your.name@databricks.com/airtable-connector"

required_files = [
    "ingest.py",
    "sources/__init__.py",
    "sources/airtable/__init__.py",
    "sources/airtable/airtable.py",
    "sources/interface/__init__.py",
    "sources/interface/lakeflow_connect.py",
    "libs/__init__.py",
    "libs/common/__init__.py",
    "libs/common/source_loader.py",
    "libs/spec_parser.py",
    "pipeline-spec/__init__.py",
    "pipeline-spec/airtable_spec.py",
]

print("Checking directory structure...")
all_present = True

for file in required_files:
    file_path = f"{base_path}/{file}"
    exists = dbutils.fs.ls(file_path.replace("/Workspace", "/Workspace/")) # Check if exists
    if exists:
        print(f"✅ {file}")
    else:
        print(f"❌ MISSING: {file}")
        all_present = False

if all_present:
    print("\n✅ All required files present!")
else:
    print("\n❌ Some files are missing. Please upload them.")
```

---

## 🎯 Step 3: Create DLT Pipeline via UI

1. **Go to Workflows → Delta Live Tables**

2. **Click "Create Pipeline"**

3. **Configure Pipeline:**

   **General Settings:**
   - **Pipeline name:** `Airtable Lakeflow Connector`
   - **Product edition:** `Advanced`
   
   **Source Code:**
   - **Paths:** Click "+ Add file or folder"
   - **Enter path:** `/Workspace/Users/your.name@databricks.com/airtable-connector/ingest.py`
   - ⚠️ **Important:** Must be the full path to `ingest.py`
   
   **Destination:**
   - **Catalog:** `main` (or your catalog)
   - **Target schema:** `default` (or your schema)
   
   **Compute:**
   - **Cluster mode:** Fixed size or Autoscaling
   - **Workers:** 1-2 (sufficient for most Airtable workloads)
   - **Photon acceleration:** ✅ Enabled
   - **Serverless:** ✅ Enabled (if available)
   
   **Advanced Settings:**
   - **Configuration:** Leave empty (NO keys needed!)
   - **Development mode:** ✅ Enabled (for testing)
   - **Channel:** Current

4. **Click "Create"**

---

## ▶️ Step 4: Run the Pipeline

1. In the DLT pipeline UI, click **"Start"**

2. **Monitor the Event Log:**
   - Look for: "🚀 Airtable Lakeflow Connector - Workspace Deployment"
   - Check for: "✅ Credentials retrieved from UC connection"
   - Verify: "✅ Connector initialized"
   - Watch: Table creation progress

3. **Expected Output:**
   ```
   ✓ Detected notebook path: /Workspace/.../airtable-connector/ingest.py
   ✓ Added to sys.path: /Workspace/.../airtable-connector
   ✓ Imports successful
   
   🔍 Attempting to retrieve UC connection credentials...
      Method 1: Query system.information_schema.connections...
      ✅ Method 1 succeeded!
   
   ✅ Base ID: appSaRcgA5...
   ✅ Base URL: https://api.airtable.com/v0
   ✅ Token: patABC123...
   ✅ Credentials retrieved from UC connection 'airtable'
   
   ✓ Connector initialized on driver node
   
   📊 Fetching data from Airtable: Packaging Tasks
      ✅ Fetched 25 records from Packaging Tasks
   
   📊 Fetching data from Airtable: Campaigns
      ✅ Fetched 10 records from Campaigns
   
   📊 Fetching data from Airtable: Creative Requests
      ✅ Fetched 15 records from Creative Requests
   
   ✅ PIPELINE DEFINITION COMPLETE
   ```

---

## 🐛 Troubleshooting

### Error 1: `ModuleNotFoundError: No module named 'sources'`

**Cause:** Missing files or incorrect directory structure

**Fix:**
1. Verify ALL files uploaded (see Step 2)
2. Check all `__init__.py` files exist
3. Ensure path in DLT points to correct `ingest.py` location

---

### Error 2: `Cannot retrieve UC connection credentials`

**Cause:** UC connection not accessible or doesn't exist

**Fix:**

1. **Verify connection exists:**
   ```sql
   SHOW CONNECTIONS;
   ```
   Should show `airtable` in the list

2. **Check connection details:**
   ```sql
   DESCRIBE CONNECTION airtable;
   ```
   Should show bearer_token, base_id, base_url

3. **Test connection access:**
   ```python
   # Run in notebook
   spark.sql("SELECT * FROM system.information_schema.connections WHERE connection_name = 'airtable'").show()
   ```
   Should return 1 row

4. **Check permissions:**
   - You need `USE CONNECTION` permission on `airtable`
   - Contact admin if you don't have access

---

### Error 3: `404 Not Found` from Airtable API

**Cause:** Wrong base_id or table names

**Fix:**
1. Verify base_id in UC connection
2. Check table names match exactly (case-sensitive)
3. Test with local script first (`ingest_local.py`)

---

### Error 4: `401 Unauthorized` from Airtable API

**Cause:** Invalid or expired token

**Fix:**
1. Generate new Personal Access Token in Airtable
2. Update UC connection:
   ```sql
   ALTER CONNECTION airtable
   SET OPTIONS (bearer_token = 'new_token_here');
   ```
3. Ensure token has required scopes: `data.records:read`, `schema.bases:read`

---

## 🔍 Step 5: Verify Data

After successful pipeline run:

```sql
-- Check tables created
SHOW TABLES IN main.default;

-- Verify data
SELECT * FROM main.default.packaging_tasks LIMIT 10;
SELECT * FROM main.default.campaigns LIMIT 10;
SELECT * FROM main.default.creative_requests LIMIT 10;

-- Check row counts
SELECT COUNT(*) FROM main.default.packaging_tasks;
SELECT COUNT(*) FROM main.default.campaigns;
SELECT COUNT(*) FROM main.default.creative_requests;
```

---

## 🔄 Updating the Code

When you update the code in GitHub:

1. **Download latest from GitHub** (or pull locally)
2. **Re-upload changed files** to Workspace using same method as Step 1
3. **Rerun DLT pipeline** - it will use updated code

**Note:** Unlike Repos, Workspace doesn't auto-sync with Git. You must manually update files.

---

## ✅ Success Checklist

Before marking deployment complete:

- [ ] All files uploaded to /Workspace/
- [ ] Directory structure matches exactly
- [ ] UC connection `airtable` exists and accessible
- [ ] DLT pipeline created
- [ ] Pipeline points to correct `/Workspace/.../ingest.py` path
- [ ] Pipeline runs successfully
- [ ] Tables appear in target catalog/schema
- [ ] Data counts match Airtable
- [ ] No errors in Event Log

---

## 📞 Getting Help

If you encounter issues:

1. **Check Event Log** in DLT UI for detailed error messages
2. **Test locally** using `ingest_local.py` to isolate Databricks vs connector issues
3. **Verify UC connection** using SQL queries above
4. **Check file structure** using verification script in Step 2

---

## 🎯 Key Points

✅ **NO Repos access needed** - Everything works in /Workspace/
✅ **NO explicit credentials** - Retrieved from UC connection automatically
✅ **NO serialization** - Connector runs on driver only
✅ **Complete directory structure required** - All files must be present
✅ **Manual sync needed** - Update files manually when code changes

---

**Your deployment should now work! Good luck! 🚀**
