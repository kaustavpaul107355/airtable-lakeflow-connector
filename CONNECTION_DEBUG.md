# 🔍 Connection Exists But Not Prepopulated - Debug Guide

**Your Situation:**
- ✅ UC Connection exists: https://e2-dogfood.staging.cloud.databricks.com/explore/connections/airtable
- ❌ Not appearing as prepopulated option in Community Connectors UI
- ❓ Shows "Create connection" button instead

---

## 🎯 Root Cause Analysis

Since the connection exists but isn't recognized by the Community Connectors UI, this typically means:

### **Most Likely: Connector Not Registered in Databricks**

The official Databricks Community Connectors UI is looking for **officially registered connectors**, not custom ones uploaded to your workspace. Your custom Airtable connector may not be visible to the UI flow yet.

---

## ✅ **What to Verify**

### **1. Check Connection Properties**

Run this SQL to see the exact connection configuration:

```sql
DESCRIBE CONNECTION airtable;
```

**Expected Output:**
```
name: airtable
connection_type: GENERIC_LAKEFLOW_CONNECT
options:
  sourceName: airtable        ← Must match exactly
  bearer_token: ***
  base_id: appSaRcgA5UCGoRg5
  base_url: https://api.airtable.com/v0
```

**Critical Check:** The `sourceName` option MUST be exactly `airtable` (lowercase, no spaces).

### **2. Check Connection Metadata**

```sql
SELECT *
FROM system.information_schema.connections
WHERE connection_name = 'airtable';
```

Look for any differences in:
- `connection_type` - Must be `GENERIC_LAKEFLOW_CONNECT`
- `connection_url` - Should show the configuration
- `owner` - Make sure you have access

---

## 🚨 **The Real Issue: Custom Connector vs Official UI**

### **What's Happening:**

The Databricks Community Connectors UI you're accessing is designed to work with **officially supported connectors** that are:
1. Pre-registered in the Databricks system
2. Available in the official repository
3. Recognized by the platform

**Your custom Airtable connector** is:
- ✅ Properly implemented
- ✅ Follows the official standard
- ✅ Has a UC connection created
- ❌ **But not yet registered with the Databricks Community Connectors system**

### **This Explains Why:**

- In previous attempts, you may have seen "airtable" if:
  - You were testing with a different flow
  - There was an officially supported Airtable connector available
  - You were in a different environment

- Now you see "Create connection" because:
  - The UI doesn't know about your custom connector code yet
  - It's asking you to connect to a source it doesn't recognize

---

## 🔧 **Solution Options**

### **Option A: Use the Official Deployment Method (Recommended)**

This is what your expert has been suggesting!

**Don't use the UI wizard yet.** Instead, deploy your connector using one of these methods:

#### **Method 1: CLI Tool**
```bash
# From the official repository
cd lakeflow-community-connectors/tools/community_connector

# Use the CLI to deploy your custom connector
# This will register it properly with the system
```

#### **Method 2: Manual DLT Pipeline (Databricks Repos)**

Since you have your code in Databricks Repos:

1. **Create a DLT Pipeline manually** (not through Community Connectors UI)
2. **Point it to your `ingest_databricks.py`** in Repos
3. **Configure it to use your UC connection**

**Path to your code in Repos:**
```
/Repos/your.email@databricks.com/airtable-lakeflow-connector/ingest_databricks.py
```

Or if it's in the workspace:
```
/Users/kaustav.paul@databricks.com/airtable-connector/ingest_databricks.py
```

### **Option B: Click "Create Connection" and Manually Configure**

Since the UI doesn't recognize your connector, you can:

1. **Click "Create connection"** in the UI
2. **Manually configure** the connection parameters
3. **Provide your connector code location** if prompted

But this may not work if the UI expects officially registered connectors only.

---

## 📋 **Recommended: Manual DLT Pipeline Setup**

This is the most reliable approach for custom connectors:

### **Step 1: Go to Delta Live Tables**
https://e2-dogfood.staging.cloud.databricks.com/?o=6051921418418893#joblist/pipelines

### **Step 2: Create Pipeline**

Click **"Create Pipeline"** and configure:

**Pipeline Settings:**
- **Name:** `Airtable Lakeflow Connector`
- **Product Edition:** `Advanced` (for CDC support)
- **Pipeline Mode:** `Triggered`

**Source Code:**
- **Notebook/File Path:** 
  ```
  /Users/kaustav.paul@databricks.com/airtable-connector/ingest_databricks.py
  ```
  Or if in Repos:
  ```
  /Repos/kaustav.paul@databricks.com/airtable-lakeflow-connector/ingest_databricks.py
  ```

**Target:**
- **Catalog:** `kaustavpaul_demo` (or your catalog)
- **Schema:** `airtable_connector` (or your schema)

**Compute:**
- **Serverless:** ✅ Enabled (recommended)

**Advanced Configuration:**
You shouldn't need any extra configuration since `ingest_databricks.py` will use the UC connection automatically.

### **Step 3: Save and Start**

1. Click **"Create"**
2. Click **"Start"** to run the pipeline
3. Monitor the execution

---

## 🎯 **Why This Works**

When you create a DLT pipeline pointing directly to your `ingest_databricks.py`:

1. **It loads your connector code** from the file
2. **It calls** `get_register_function("airtable")` to register your connector
3. **It runs** `ingest(spark, pipeline_spec)` with your configuration
4. **It uses** the UC connection `airtable` automatically
5. **It creates** Delta tables in your target catalog/schema

**No UI wizard needed!**

---

## 🔍 **Debug Questions for Your Expert**

Share this with your expert:

> "I have a custom Airtable Lakeflow connector that I've developed following the official standard:
> 
> - ✅ UC connection exists: `airtable` (GENERIC_LAKEFLOW_CONNECT)
> - ✅ Code is standard-compliant and tested locally (8/8 tests passed)
> - ✅ Code location: `/Users/kaustav.paul@databricks.com/airtable-connector/`
> - ✅ GitHub: https://github.com/kaustavpaul107355/airtable-lakeflow-connector
> 
> **Question:** When I use the Community Connectors UI ("+New" → "Airtable-connector"), 
> it shows "Create connection" instead of prepopulating my existing UC connection.
> 
> Should I:
> A. Register my connector with the Community Connectors system first?
> B. Create a manual DLT pipeline pointing to my `ingest_databricks.py`?
> C. Use the CLI tool to deploy?
> D. Something else?
> 
> The connection exists and I can view it at:
> https://e2-dogfood.staging.cloud.databricks.com/explore/connections/airtable"

---

## 📊 **Expected Behavior Comparison**

### **Official Supported Connector:**
```
Community Connectors UI
  ↓
Recognizes "stripe", "github", "zendesk" (officially supported)
  ↓
Shows existing connections in dropdown
  ↓
Easy wizard-based setup
```

### **Your Custom Connector:**
```
Community Connectors UI
  ↓
Doesn't recognize custom "airtable" connector yet
  ↓
Shows "Create connection" (generic)
  ↓
May not work with wizard ❌
```

**Solution:** Bypass the UI wizard, create DLT pipeline manually ✅

---

## ✅ **Action Items**

**Right Now:**

1. **Verify your connection properties:**
   ```sql
   DESCRIBE CONNECTION airtable;
   ```
   Make sure `sourceName = 'airtable'`

2. **Contact your expert** with the question above

3. **In parallel, try manual DLT pipeline:**
   - Go to Delta Live Tables
   - Create pipeline pointing to your `ingest_databricks.py`
   - Use the settings I provided above
   - Try to start it

**This will tell us:**
- If the connection works when accessed directly
- If there's an issue with your connector code
- If it's purely a UI registration issue

---

## 🎯 **Most Likely Next Steps**

Your expert will probably say:

**Option 1:** "Create a manual DLT pipeline - here's the exact configuration..."

**Option 2:** "Use the CLI tool to register your connector first..."

**Option 3:** "The Community Connectors UI is for officially supported connectors only. For custom connectors, use method X..."

Either way, you're very close! The hard part (building the connector) is done. This is just a deployment workflow question.

---

**Created:** January 8, 2026  
**Status:** Awaiting expert guidance on deployment method
