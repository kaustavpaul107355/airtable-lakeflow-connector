# 🚀 Databricks Deployment Guide

## ✅ **Official Lakeflow Pattern - Zero Explicit Credentials**

This connector uses the **official Lakeflow Community Connectors pattern** where:

- ✅ **UC Connection** stores credentials securely
- ✅ **No explicit credential access** in code or pipeline config
- ✅ **Automatic credential injection** via `databricks.connection` option
- ✅ **Databricks Repos** ensures proper Python serialization

---

## 📋 **Prerequisites**

1. ✅ **Unity Catalog Connection** named `airtable` exists
2. ✅ **Databricks Repos** has your code checked out
3. ✅ **Permissions** to create DLT pipelines

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

**That's it!** The connector will automatically use these credentials. No other configuration needed.

---

## 📂 **Step 2: Deploy Code to Databricks Repos**

### **Why Repos?**
- ✅ Proper Python package resolution
- ✅ Handles serialization for Spark workers
- ✅ Git version control
- ✅ No manual `sys.path` manipulation

### **Option A: Sync Existing Repo** (if already set up)

1. Go to **Repos** in your Databricks workspace
2. Navigate to your `airtable-lakeflow-connector` repo
3. Click branch dropdown → **Pull latest changes**

### **Option B: Create New Repo** (first time)

1. Go to **Repos** → **Add Repo**
2. Git repo URL: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`
3. Click **Create Repo**

Your code will be at:
```
/Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/
```

---

## 🎯 **Step 3: Create DLT Pipeline**

### **Using Databricks UI** (RECOMMENDED)

1. Go to **Workflows** → **Delta Live Tables**
2. Click **Create Pipeline**
3. Configure:

**Basic Settings:**
- **Pipeline Name**: `Airtable Lakeflow Connector`
- **Product Edition**: `Advanced` (for CDC/SCD support)
- **Source Code**: 
  - Path: `/Repos/Users/your.name@databricks.com/airtable-lakeflow-connector/ingest.py`
  - **CRITICAL**: Must be in `/Repos/`, NOT `/Workspace/`

**Target:**
- **Catalog**: `main` (or your catalog)
- **Schema**: `default` (or your schema)

**Compute:**
- **Cluster Mode**: Fixed or Autoscaling
- **Workers**: 1 (sufficient for most Airtable datasets)
- **Photon**: ✅ Enabled
- **Serverless**: ✅ Enabled (if available)

**Other Settings:**
- **Development Mode**: ✅ Enabled (for testing)
- **Channel**: Current
- **Storage Location**: (leave default)

**🚨 IMPORTANT: No Configuration Keys Needed!**

Do NOT add any of these:
- ❌ `connection.airtable.bearer_token`
- ❌ `connection.airtable.base_id`
- ❌ `connection.airtable.base_url`

The official pattern retrieves these automatically from the UC connection!

4. Click **Create**

---

### **Using JSON Configuration**

```json
{
  "name": "Airtable Lakeflow Connector",
  "storage": "/mnt/dlt/airtable",
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
  "edition": "ADVANCED",
  "clusters": [
    {
      "label": "default",
      "num_workers": 1
    }
  ]
}
```

**Note:** No `configuration` section needed!

---

## ▶️ **Step 4: Run the Pipeline**

1. Click **Start** in DLT UI
2. Monitor execution in **Event Log**
3. Check **Graph** tab for table lineage

**Expected Output:**
```
🚀 Airtable Lakeflow Connector - Official Pattern
Source: airtable
UC Connection: airtable
Tables: 3

✅ Using UC connection - no explicit credentials needed

✓ Connector registered

📊 Creating table: main.default.packaging_tasks
📊 Creating table: main.default.campaigns
📊 Creating table: main.default.creative_requests

✅ Ingestion pipeline completed!
```

---

## 🔍 **Step 5: Verify Data**

```sql
-- Check tables were created
SHOW TABLES IN main.default;

-- Verify data
SELECT * FROM main.default.packaging_tasks LIMIT 10;
SELECT * FROM main.default.campaigns LIMIT 10;
SELECT * FROM main.default.creative_requests LIMIT 10;

-- Row counts
SELECT COUNT(*) FROM main.default.packaging_tasks;
SELECT COUNT(*) FROM main.default.campaigns;
SELECT COUNT(*) FROM main.default.creative_requests;
```

---

## 🐛 **Troubleshooting**

### **Error 1: `ModuleNotFoundError: No module named 'pipeline'`**

**Cause:** Code not in Databricks Repos

**Fix:**
1. Verify DLT pipeline path starts with `/Repos/` (not `/Workspace/`)
2. If in Workspace, move to Repos:
   - Create new repo pointing to your GitHub
   - Update DLT pipeline path

**Correct path:**
```
✅ /Repos/Users/name@company.com/airtable-lakeflow-connector/ingest.py
❌ /Workspace/Users/name@company.com/airtable-connector/ingest.py
```

---

### **Error 2: `[NO_TABLES_IN_PIPELINE]`**

**Cause:** DLT can't find table definitions

**Fix:**
1. Verify `ingest.py` path is correct
2. Check Repos has latest code (`git pull`)
3. Ensure `pipeline/ingestion_pipeline.py` exists and has `@dlt.table` or SDP decorators

---

### **Error 3: `404 Not Found` from Airtable API**

**Cause:** Wrong `base_id` or table names

**Fix:**
1. Verify `base_id` in UC connection: `DESCRIBE CONNECTION airtable;`
2. Check table names in `ingest.py` match Airtable exactly (case-sensitive)
3. Test locally first: `python ingest_local.py`

---

### **Error 4: `401 Unauthorized` from Airtable API**

**Cause:** Invalid token

**Fix:**
1. Generate new Personal Access Token in Airtable
2. Update UC connection:
   ```sql
   ALTER CONNECTION airtable
   SET OPTIONS (bearer_token = 'new_token_here');
   ```
3. Ensure token has scopes: `data.records:read`, `schema.bases:read`

---

### **Error 5: UC Connection Not Found**

**Cause:** Connection doesn't exist or no permissions

**Fix:**
1. Check connection exists: `SHOW CONNECTIONS;`
2. If missing, create it (see Step 1)
3. Verify you have `USE CONNECTION` permission

---

## 🔄 **Update Workflow**

When you make code changes:

**1. Local Development:**
```bash
cd airtable-connector
# Edit code
python ingest_local.py  # Test locally
```

**2. Git Sync:**
```bash
git add -A
git commit -m "Your changes"
git push origin main
```

**3. Databricks Sync:**
- Go to Repos → Your repo
- Click **...** → **Pull** latest changes

**4. Rerun Pipeline:**
- Click **Start** (uses updated code automatically)

---

## 📊 **How It Works (Technical)**

### **Credential Flow:**

```
1. You create UC connection
   └─> Databricks stores credentials securely

2. DLT runs ingest.py
   └─> Calls: register_lakeflow_source(spark)
   └─> Registers AirtableLakeflowConnector as Spark Data Source

3. ingestion_pipeline.py executes
   └─> Calls: spark.read.format("lakeflow_connect")
                    .option("databricks.connection", "airtable")
                    .load()
   
4. Spark Data Source API
   └─> Retrieves connection "airtable" from UC
   └─> Extracts credentials automatically
   └─> Passes to AirtableLakeflowConnector instance
   
5. Connector makes API calls
   └─> Uses credentials from UC
   └─> Returns data to Spark
   
6. DLT creates tables
   └─> Applies SCD/CDC logic
   └─> Writes to Delta tables
```

**Key Point:** Credentials flow through Spark's Data Source API automatically. No explicit access needed anywhere!

---

## ✅ **Deployment Checklist**

Before marking complete:

- [ ] UC connection `airtable` exists
- [ ] Code in Databricks Repos (not Workspace)
- [ ] DLT pipeline path starts with `/Repos/`
- [ ] NO configuration keys added to pipeline
- [ ] Pipeline runs successfully
- [ ] Data visible in target tables
- [ ] Row counts match Airtable

---

## 📞 **Getting Help**

If issues persist:

**1. Check Setup:**
```sql
-- Verify UC connection
DESCRIBE CONNECTION airtable;

-- Check tables
SHOW TABLES IN main.default;
```

**2. Review Logs:**
- DLT UI → Event Log tab
- Look for Python tracebacks

**3. Contact Expert:**
> "Using official Lakeflow pattern with UC connection.
> Local testing passes.
> 
> Current error: [paste error]
> 
> Setup:
> - UC connection: airtable (DESCRIBE shows it exists)
> - Code location: /Repos/.../airtable-lakeflow-connector/
> - DLT pipeline: [link]
> - No explicit credentials configured (as required)
> 
> Can you help troubleshoot?"

---

## 🎯 **Key Takeaways**

1. ✅ **UC Connection** = Single source of truth for credentials
2. ✅ **Databricks Repos** = Proper serialization and packages
3. ✅ **Official Pattern** = `spark.read.format("lakeflow_connect")`
4. ✅ **No Explicit Credentials** = Anywhere!
5. ✅ **Automatic Injection** = Via Spark Data Source API

---

**🎉 You're ready! Sync your Databricks Repo and run the pipeline!**
