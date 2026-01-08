# 🚀 Databricks Deployment Guide

## ⚠️ **IMPORTANT: Use the Correct Ingest File!**

Your error happened because you used the wrong file in Databricks:

```
❌ DON'T USE: ingest.py (for local testing only)
✅ DO USE: ingest_databricks.py (for Databricks deployment)
```

---

## 📋 **Quick Fix for Your Current Error**

### **Error You're Seeing:**
```python
NameError: name '__file__' is not defined
```

### **Why This Happens:**
- `ingest.py` is designed for LOCAL testing and uses `__file__`
- Databricks notebooks don't support `__file__`
- You need to use `ingest_databricks.py` instead

### **Solution:**
In your Databricks workspace at:
```
/Users/kaustav.paul@databricks.com/airtable-connector/
```

Run **`ingest_databricks.py`** instead of `ingest.py`!

---

## 🎯 **Complete Databricks Deployment Steps**

### **Step 1: Verify UC Connection**

First, ensure your Unity Catalog connection exists:

```sql
-- Run this in a Databricks SQL cell or notebook:
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_airtable_token_here',
  base_id 'appSaRcgA5UCGoRg5',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

**Check if connection exists:**
```sql
SHOW CONNECTIONS;
```

### **Step 2: Update Configuration in `ingest_databricks.py`**

Edit the `pipeline_spec` section to match your tables:

```python
pipeline_spec = {
    "connection_name": "airtable",  # Must match UC connection name
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",        # ← Your Airtable table name
                "destination_table": "packaging_tasks",   # ← Target table name
            }
        },
        {
            "table": {
                "source_table": "Campaigns",
                "destination_table": "campaigns",
            }
        },
        # Add more tables...
    ]
}
```

### **Step 3: Set Up DLT Pipeline (Recommended)**

Create a Delta Live Tables pipeline with this configuration:

**Method A: Using Databricks UI**

1. Go to **Workflows** → **Delta Live Tables**
2. Click **Create Pipeline**
3. Configure:
   - **Name:** `Airtable Lakeflow Connector`
   - **Product Edition:** Advanced (for CDC support)
   - **Notebook/File:** `/Users/kaustav.paul@databricks.com/airtable-connector/ingest_databricks.py`
   - **Target Catalog:** `kaustavpaul_demo`
   - **Target Schema:** `airtable_connector`
   - **Development Mode:** ✅ Enabled (for testing)
   - **Serverless:** ✅ Enabled (recommended)

**Method B: Using JSON Configuration**

```json
{
  "id": "your-pipeline-id",
  "pipeline_type": "WORKSPACE",
  "name": "Airtable Lakeflow Connector",
  "libraries": [
    {
      "notebook": {
        "path": "/Users/kaustav.paul@databricks.com/airtable-connector/ingest_databricks.py"
      }
    }
  ],
  "schema": "airtable_connector",
  "catalog": "kaustavpaul_demo",
  "continuous": false,
  "development": true,
  "photon": true,
  "serverless": true
}
```

### **Step 4: Run the Pipeline**

1. Click **Start** in the DLT UI
2. Monitor the pipeline execution
3. Check for any errors in the logs

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: `ModuleNotFoundError: No module named 'pipeline'`**

**Cause:** Code not in Databricks Repos, Python path not set up correctly

**Solution:**
- Deploy via Databricks Repos (recommended)
- Or use official UI/CLI tool (contact expert)
- Databricks Repos ensures proper Python module resolution

### **Issue 2: `NameError: name '__file__' is not defined`**

**Cause:** Using `ingest.py` instead of `ingest_databricks.py`

**Solution:**
- Use `ingest_databricks.py` for Databricks deployment
- Use `ingest.py` only for local testing

### **Issue 3: `SparkNoSuchElementException: [SQL_CONF_NOT_FOUND]`**

**Cause:** UC connection not found or misconfigured

**Solution:**
1. Verify connection exists: `SHOW CONNECTIONS;`
2. Check connection name in `pipeline_spec` matches UC connection
3. Ensure connection has correct options (token, base_id, base_url)

### **Issue 4: `404 Not Found` from Airtable API**

**Cause:** Incorrect `base_id` or table names

**Solution:**
1. Verify `base_id` in UC connection
2. Check table names are exact (case-sensitive)
3. Test credentials with local `ingest.py` first

---

## 📊 **Verification Checklist**

Before deployment, ensure:

- [ ] ✅ Local testing passed (`python ingest.py` succeeded)
- [ ] ✅ UC connection created and verified
- [ ] ✅ Using `ingest_databricks.py` (not `ingest.py`)
- [ ] ✅ Table names in `pipeline_spec` match Airtable
- [ ] ✅ Target catalog/schema exists and you have permissions
- [ ] ✅ Code deployed via Databricks Repos (for proper imports)

---

## 🎯 **Recommended Deployment Path**

According to the [official Lakeflow documentation](https://github.com/databrickslabs/lakeflow-community-connectors) and expert guidance:

### **Best Practice: Use Official Tools**

1. **Databricks UI** (Easiest)
   - Go to **+New** → **Add or upload data**
   - Select **Community connectors**
   - Choose **+ Add Community Connector**
   - Point to your Git repo or use official repo

2. **CLI Tool** (For Automation)
   - Tool location: `tools/community_connector`
   - Handles all scaffolding automatically
   - Recommended for CI/CD workflows

**Why use official tools?**
- ✅ Handles Python packaging automatically
- ✅ Proper serialization for Spark workers
- ✅ Follows DLT best practices
- ✅ No manual path manipulation needed

### **What to Ask Your Expert:**

> "Local testing is complete and successful (8/8 tests passed)!
> 
> I'm ready to deploy to Databricks. I see there are two recommended methods:
> 
> 1. Databricks UI: +New → Add or upload data → Community connectors
> 2. CLI Tool: tools/community_connector
> 
> Which method would you recommend for my workspace (e2-dogfood)?
> 
> Also, should I be using Databricks Repos for the deployment, or does the UI/CLI handle that automatically?"

---

## 🔄 **Development Workflow**

### **Recommended Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LOCAL DEVELOPMENT                                         │
│    • Edit connector code                                     │
│    • Run: python ingest.py                                   │
│    • Verify: All tests pass                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GIT SYNC                                                  │
│    • Commit changes to GitHub                                │
│    • Push to main branch                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DATABRICKS DEPLOYMENT                                     │
│    • Use official UI or CLI tool                             │
│    • Point to your Git repo                                  │
│    • Connector is deployed automatically                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. VALIDATE IN DATABRICKS                                    │
│    • Run DLT pipeline                                        │
│    • Check data in target tables                             │
│    • Monitor for errors                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📞 **Next Steps**

1. ✅ **You've completed:** Local testing and validation
2. 🎯 **You're here:** Ready to deploy to Databricks
3. 📞 **Next action:** Contact expert for recommended deployment method

**You're in great shape - the connector works perfectly! Just need the official deployment process.** 🎉
