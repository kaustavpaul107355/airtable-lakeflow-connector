# 🚀 Databricks Deployment Guide

## 📋 **Prerequisites**

Before deploying, ensure you have:

1. ✅ **UC Connection Created**: A Unity Catalog connection named `airtable`
2. ✅ **Databricks Repo**: Code checked out in Databricks Repos
3. ✅ **Permissions**: Access to create DLT pipelines and write to target catalog/schema

---

## 🔧 **Step 1: Create Unity Catalog Connection**

Run this SQL in your Databricks workspace:

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_airtable_personal_access_token',
  base_id '<your-airtable-base-id>',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

**Verify it was created:**
```sql
SHOW CONNECTIONS;
DESCRIBE CONNECTION airtable;
```

---

## 📂 **Step 2: Deploy Code to Databricks Repos**

### **Option A: Sync Existing Repo** (if already set up)

1. Go to your Databricks workspace
2. Navigate to **Repos** → `/Users/your.name@databricks.com/`
3. Find your `airtable-connector` repo
4. Click the branch dropdown → **Pull latest changes**

### **Option B: Create New Repo** (first time)

1. Go to **Repos** in Databricks
2. Click **Add Repo**
3. Enter repo URL: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`
4. Click **Create**

Your code will be at:
```
/Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/
```

---

## 🎯 **Step 3: Create DLT Pipeline**

### **Method 1: Using Databricks UI** (RECOMMENDED)

1. Go to **Workflows** → **Delta Live Tables**
2. Click **Create Pipeline**
3. Fill in the form:

**Basic Settings:**
- **Pipeline Name**: `Airtable Lakeflow Connector`
- **Product Edition**: `Advanced`
- **Notebook/File Path**: `/Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/ingest.py`
- **Target**: 
  - Catalog: `main` (or your catalog)
  - Schema: `default` (or your schema)

**Compute Settings:**
- **Cluster Mode**: `Fixed Size` or `Autoscaling`
- **Workers**: `1` (for small datasets)
- **Cluster Policy**: (optional)
- **Photon**: ✅ Enabled
- **Serverless**: ✅ Enabled (if available)

**Advanced Settings → Configuration:**

**🚨 CRITICAL: Add these configuration parameters:**

```
Key: connection.airtable.bearer_token
Value: {{secrets/your-secret-scope/airtable-token}}

Key: connection.airtable.base_id
Value: <your-airtable-base-id>

Key: connection.airtable.base_url
Value: https://api.airtable.com/v0
```

**Important Notes:**
- Use Databricks Secrets for the token (recommended)
- Or temporarily use plain text value for testing: `patABC123...`
- The keys MUST match exactly: `connection.airtable.*`

**Other Settings:**
- **Development Mode**: ✅ Enabled (for testing)
- **Channel**: `Current` (or `Preview`)
- **Storage Location**: (leave default)

4. Click **Create**

---

### **Method 2: Using JSON Configuration**

Create a file `dlt_pipeline_config.json`:

```json
{
  "name": "Airtable Lakeflow Connector",
  "storage": "/mnt/dlt/airtable",
  "configuration": {
    "connection.airtable.bearer_token": "{{secrets/your-scope/airtable-token}}",
    "connection.airtable.base_id": "<your-airtable-base-id>",
    "connection.airtable.base_url": "https://api.airtable.com/v0"
  },
  "clusters": [
    {
      "label": "default",
      "num_workers": 1,
      "autoscale": {
        "min_workers": 1,
        "max_workers": 2
      }
    }
  ],
  "libraries": [
    {
      "notebook": {
        "path": "/Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/ingest.py"
      }
    }
  ],
  "target": "main.default",
  "continuous": false,
  "development": true,
  "photon": true,
  "edition": "ADVANCED"
}
```

Deploy via CLI:
```bash
databricks pipelines create --json-file dlt_pipeline_config.json
```

---

## 🔐 **Step 4: Set Up Databricks Secrets** (RECOMMENDED)

Instead of hardcoding your Airtable token, use Databricks Secrets:

### **Create Secret Scope:**
```bash
databricks secrets create-scope --scope airtable-secrets
```

### **Add Secret:**
```bash
databricks secrets put --scope airtable-secrets --key token
# This will open an editor - paste your Airtable token and save
```

### **Update DLT Configuration:**
```
Key: connection.airtable.bearer_token
Value: {{secrets/airtable-secrets/token}}
```

---

## ▶️ **Step 5: Run the Pipeline**

1. In DLT UI, click **Start**
2. Monitor the execution:
   - Check **Graph** tab for table dependencies
   - Check **Event Log** for detailed logs
   - Check **Data Quality** for any issues

3. Expected output:
   ```
   ✅ packaging_tasks: X records loaded
   ✅ campaigns: Y records loaded
   ✅ creative_requests: Z records loaded
   ```

---

## 🔍 **Step 6: Verify Data**

Query your tables:

```sql
-- Check tables were created
SHOW TABLES IN main.default;

-- Verify data
SELECT * FROM main.default.packaging_tasks LIMIT 10;
SELECT * FROM main.default.campaigns LIMIT 10;
SELECT * FROM main.default.creative_requests LIMIT 10;

-- Check row counts
SELECT 
  'packaging_tasks' as table_name, 
  COUNT(*) as row_count 
FROM main.default.packaging_tasks
UNION ALL
SELECT 
  'campaigns', 
  COUNT(*) 
FROM main.default.campaigns
UNION ALL
SELECT 
  'creative_requests', 
  COUNT(*) 
FROM main.default.creative_requests;
```

---

## 🐛 **Troubleshooting Common Errors**

### **Error 1: `SparkNoSuchElementException: [SQL_CONF_NOT_FOUND] connection.airtable.bearer_token`**

**Cause:** DLT pipeline configuration missing required keys

**Fix:**
1. Go to DLT Pipeline → **Settings** → **Advanced** → **Configuration**
2. Add the three required configuration keys (see Step 3 above)
3. Save and restart pipeline

**Visual Guide:**
```
DLT UI
├── Your Pipeline
│   ├── Settings (⚙️)
│   │   ├── Advanced
│   │   │   ├── Configuration ← ADD KEYS HERE
│   │   │   │   ├── connection.airtable.bearer_token: {{secrets/...}}
│   │   │   │   ├── connection.airtable.base_id: appXXXXX
│   │   │   │   └── connection.airtable.base_url: https://...
```

---

### **Error 2: `ModuleNotFoundError: No module named 'sources'`**

**Cause:** Code not in Databricks Repos, or wrong path in DLT config

**Fix:**
1. Ensure code is in `/Repos/` directory (NOT `/Workspace/Users/`)
2. Update DLT pipeline path to point to Repos location
3. Repos provides proper Python package resolution

**Correct path format:**
```
✅ /Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/ingest.py
❌ /Workspace/Users/your.name@databricks.com/airtable-connector/ingest.py
```

---

### **Error 3: `404 Not Found` from Airtable API**

**Cause:** Wrong `base_id` or table names

**Fix:**
1. Verify `base_id` in your UC connection or DLT config
2. Check table names in `ingest.py` match Airtable exactly (case-sensitive)
3. Test locally first: `python ingest_local.py`

---

### **Error 4: `401 Unauthorized` from Airtable API**

**Cause:** Invalid or expired Airtable token

**Fix:**
1. Generate new Personal Access Token in Airtable
2. Update Databricks secret or DLT configuration
3. Ensure token has correct scopes: `data.records:read`, `schema.bases:read`

---

### **Error 5: `[NO_TABLES_IN_PIPELINE]`**

**Cause:** DLT can't find @dlt.table definitions

**Fix:**
1. Verify `ingest.py` path in DLT config is correct
2. Check `ingest.py` has @dlt.table decorators
3. Ensure Python code is syntactically valid

---

## 📊 **Monitoring & Operations**

### **Check Pipeline Status:**
```sql
-- View pipeline runs
SELECT * FROM system.livelinetables.pipeline_events 
WHERE pipeline_id = 'your-pipeline-id'
ORDER BY timestamp DESC
LIMIT 100;
```

### **Monitor Data Freshness:**
```sql
-- Check last update time
DESCRIBE EXTENDED main.default.packaging_tasks;
```

### **Schedule Pipeline:**

In DLT UI → **Settings** → **Triggers**:
- **Triggered**: Manual execution
- **Continuous**: Runs continuously
- **Scheduled**: Cron-based schedule (e.g., `0 0 * * *` for daily at midnight)

---

## 🔄 **Update Workflow**

When you update the connector code:

1. **Local Changes:**
   ```bash
   cd /path/to/airtable-connector
   # Make your changes
   python ingest_local.py  # Test locally
   ```

2. **Git Sync:**
   ```bash
   git add -A
   git commit -m "Your changes"
   git push origin main
   ```

3. **Databricks Sync:**
   - Go to Repos in Databricks
   - Click branch dropdown → **Pull**
   - Or: Click **...** → **Git** → **Pull latest changes**

4. **Rerun Pipeline:**
   - DLT will automatically use updated code
   - Click **Start** to run with new changes

---

## 📞 **Getting Help**

If you encounter issues:

1. **Check Logs:**
   - DLT UI → **Event Log** tab
   - Look for Python tracebacks

2. **Verify Setup:**
   ```bash
   # Local testing
   cd airtable-connector
   python ingest_local.py
   ```

3. **Review Checklist:**
   - [ ] UC connection exists and has correct credentials
   - [ ] Code is in Databricks Repos (not Workspace)
   - [ ] DLT pipeline configuration has `connection.airtable.*` keys
   - [ ] Table names in `ingest.py` match Airtable
   - [ ] Local testing passes

4. **Contact Expert:**
   > "I've followed the deployment guide and verified all prerequisites.
   > Local testing passes successfully.
   > 
   > Current error: [paste error message]
   > 
   > Configuration:
   > - Pipeline: [link to DLT pipeline]
   > - Code location: [path in Repos]
   > - UC connection: [output of DESCRIBE CONNECTION airtable]
   > 
   > Can you help troubleshoot?"

---

## ✅ **Deployment Checklist**

Before marking deployment as complete:

- [ ] ✅ UC connection `airtable` exists
- [ ] ✅ Code deployed to Databricks Repos
- [ ] ✅ DLT pipeline created
- [ ] ✅ Configuration keys added to DLT pipeline
- [ ] ✅ Databricks secrets configured (recommended)
- [ ] ✅ Pipeline runs successfully
- [ ] ✅ Data visible in target tables
- [ ] ✅ Row counts match expectations
- [ ] ✅ Documentation updated for your team

---

## 🎯 **Next Steps After Deployment**

1. **Productionize:**
   - Move to production catalog/schema
   - Set up automated scheduling
   - Configure alerting/monitoring
   - Add data quality checks

2. **Optimize:**
   - Review query performance
   - Add partitioning if needed
   - Optimize cluster size
   - Enable Auto Loader for incremental loads

3. **Extend:**
   - Add more Airtable tables
   - Implement CDC (Change Data Capture)
   - Add transformations in downstream tables
   - Build downstream analytics/reports

---

**🎉 You're all set! Your Airtable data should now be flowing into Databricks!**
