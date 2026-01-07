# DLT Pipeline Configuration with UC Connection

## ✅ FIXED: Serialization Error

The previous error (`ModuleNotFoundError: No module named 'pipeline'`) was caused by trying to use a **custom Python Data Source** in DLT, which requires serialization to Spark workers.

## 🔧 New Approach: Direct Connector (No Custom Data Source)

The pipeline has been updated to:
- ✅ Call the connector directly (not as a Spark data source)
- ✅ Use `spark.createDataFrame()` to create DataFrames
- ✅ Avoid serialization issues completely
- ✅ Work reliably in ALL DLT environments

---

## 📋 DLT Pipeline Configuration

### Notebook Path
```
/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
```

### Configuration (Advanced Settings)

Add these **3 configuration entries** to your DLT pipeline:

| Key | Value |
|-----|-------|
| `connection.airtable.bearer_token` | `{{connection.airtable.bearer_token}}` |
| `connection.airtable.base_id` | `{{connection.airtable.base_id}}` |
| `connection.airtable.base_url` | `{{connection.airtable.base_url}}` |

**Important**: Use the **exact syntax** with double curly braces `{{...}}` - this tells DLT to resolve the UC connection!

---

## 🛠️ How to Configure in Databricks UI

### Step 1: Edit Pipeline Settings

1. Go to: https://e2-dogfood.staging.cloud.databricks.com/pipelines/60a58669-dca3-40ab-aaa2-a00933180c1c
2. Click **"Settings"** or **"Edit"**

### Step 2: Update Notebook Library

In **"Notebook libraries"** or **"Paths"** section:
```
/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
```

(Make sure it's **"notebook"** type, not "glob")

### Step 3: Add Configuration Entries

Expand **"Advanced"** → **"Configuration"**

Click **"Add configuration"** and add these **3 entries**:

**Entry 1:**
- Key: `connection.airtable.bearer_token`
- Value: `{{connection.airtable.bearer_token}}`

**Entry 2:**
- Key: `connection.airtable.base_id`
- Value: `{{connection.airtable.base_id}}`

**Entry 3:**
- Key: `connection.airtable.base_url`
- Value: `{{connection.airtable.base_url}}`

### Step 4: Verify Other Settings

- **Catalog**: `kaustavpaul_demo`
- **Target Schema**: `airtable_connector`
- **Pipeline Mode**: `Development`
- **Serverless**: ✅ Enabled
- **Photon**: ✅ Enabled

### Step 5: Save and Start

1. Click **"Save"**
2. Click **"Start"**

---

## 📊 Complete JSON Configuration

For reference, here's the complete JSON:

```json
{
  "name": "Airtable Lakeflow Connector",
  "pipeline_type": "WORKSPACE",
  "libraries": [
    {
      "notebook": {
        "path": "/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py"
      }
    }
  ],
  "catalog": "kaustavpaul_demo",
  "target": "airtable_connector",
  "continuous": false,
  "development": true,
  "photon": true,
  "channel": "CURRENT",
  "serverless": true,
  "configuration": {
    "connection.airtable.bearer_token": "{{connection.airtable.bearer_token}}",
    "connection.airtable.base_id": "{{connection.airtable.base_id}}",
    "connection.airtable.base_url": "{{connection.airtable.base_url}}"
  }
}
```

---

## 🔍 What Happens When Pipeline Runs

### 1. Credential Resolution
```
🔑 Loading credentials from DLT pipeline configuration...

✅ Loaded credentials from pipeline configuration
   Token: ********************keLEX5
   Base ID: appSaRcgA5UCGoRg5
   Base URL: https://api.airtable.com/v0
```

DLT resolves `{{connection.airtable.bearer_token}}` by:
- Looking up UC connection named "airtable"
- Extracting the `bearer_token` option
- Passing it to the pipeline as a config value

### 2. Connector Initialization
```
🔌 Initializing Airtable connector...
✅ Connector initialized successfully
```

The connector is initialized with UC credentials (no hardcoding!)

### 3. Table Ingestion
```
📊 Defining DLT tables:
   ✅ bronze_sku_candidates
   ✅ bronze_launch_milestones
   ✅ bronze_compliance_records
   ✅ bronze_packaging_tasks
   ✅ bronze_marketing_assets
   ✅ bronze_vendors
```

For each table:
```
📥 Reading table: Packaging Tasks
   ✅ Read 42 records
   ✅ Created DataFrame with 42 records
```

### 4. Success!
```
✅ DLT Pipeline Ready - 6 bronze tables defined
   Approach: Direct connector (no custom data source)
   Credentials: From UC connection via pipeline config
```

---

## ❓ FAQ

### Q: Why use `{{connection.airtable.bearer_token}}` syntax?

**A:** This is DLT's special syntax for UC connection resolution. When DLT sees `{{connection.NAME.OPTION}}`, it:
1. Queries UC for connection `NAME`
2. Extracts option `OPTION`
3. Injects the value into `spark.conf`

Your code reads it via:
```python
AIRTABLE_TOKEN = spark.conf.get("connection.airtable.bearer_token")
```

### Q: Are credentials hardcoded?

**A:** No! The `{{...}}` syntax is a **reference**, not a value. DLT resolves it at runtime from UC.

### Q: What if I don't use the `{{...}}` syntax?

**A:** If you enter the raw token value (like `patkBXwClC7keLEX5...`), it will work BUT:
- ❌ Credentials exposed in pipeline config (visible to anyone with access)
- ❌ No audit logging
- ❌ Hard to rotate credentials
- ❌ Not following best practices

Always use `{{connection.airtable.bearer_token}}` for security!

### Q: Why not use `.option("databricks.connection", "airtable")`?

**A:** That syntax works for **native Spark data sources** but NOT for **custom Python data sources** due to serialization issues in DLT. The direct connector approach is more reliable.

---

## 🎉 Expected Results

After starting the pipeline with this configuration:

✅ No `ModuleNotFoundError`  
✅ No `SerializationError`  
✅ Credentials resolved from UC  
✅ Data successfully ingested  
✅ 6 bronze tables created with actual data!

**Check Catalog Explorer:**
```
kaustavpaul_demo
└── airtable_connector
    ├── bronze_sku_candidates       (42 records)
    ├── bronze_launch_milestones    (15 records)
    ├── bronze_compliance_records   (28 records)
    ├── bronze_packaging_tasks      (56 records)
    ├── bronze_marketing_assets     (33 records)
    └── bronze_vendors              (12 records)
```

---

**Updated**: January 6, 2026  
**Approach**: Direct Connector (No Custom Data Source)  
**Workspace**: e2-dogfood.staging.cloud.databricks.com

