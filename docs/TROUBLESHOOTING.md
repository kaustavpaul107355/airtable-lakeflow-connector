# 🔧 Troubleshooting Guide

## Issue: Airtable Connection Not Appearing in UI

### **Symptom:**
When using the Databricks UI to ingest from Airtable connector, you see "Create connection" instead of your existing `airtable` connection being prepopulated.

### **Root Causes:**

#### **1. UC Connection Doesn't Exist (Most Common)**
The Unity Catalog connection may not have been created yet, or was deleted.

**Solution:**
```sql
-- Check if connection exists
SHOW CONNECTIONS;

-- If not present, create it:
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

#### **2. Wrong Catalog/Schema Context**
You might be viewing connections in a different catalog than where the connection was created.

**Solution:**
```sql
-- Set the correct catalog context
USE CATALOG kaustavpaul_demo;  -- or your catalog name

-- Then check connections
SHOW CONNECTIONS;
```

#### **3. Permission Issues**
You may not have permission to view or use the connection.

**Solution:**
```sql
-- Check connection permissions
DESCRIBE CONNECTION airtable;

-- Grant permissions if needed (requires admin)
GRANT USAGE ON CONNECTION airtable TO `your.email@databricks.com`;
```

#### **4. Connection in Different Workspace**
If you're in e2-dogfood staging vs. production, connections don't carry over.

**Solution:**
- Verify which workspace you're in
- Recreate the connection in the current workspace

---

## Quick Diagnostic Script

Run this in a Databricks SQL notebook or query editor:

```sql
-- 1. Check current context
SELECT current_catalog(), current_schema();

-- 2. List all connections
SHOW CONNECTIONS;

-- 3. If airtable exists, verify it
DESCRIBE CONNECTION airtable;

-- 4. Test connection options
SELECT connection_name, connection_type, comment
FROM system.information_schema.connections
WHERE connection_name = 'airtable';
```

---

## Expected Results

### **If Connection Exists:**
```
+----------------+------------------------+---------------------------+
| connection_name| connection_type        | comment                   |
+----------------+------------------------+---------------------------+
| airtable       | GENERIC_LAKEFLOW_CONNECT| Airtable API connection... |
+----------------+------------------------+---------------------------+
```

### **If Connection Missing:**
```
No rows returned
```
→ You need to create the connection

---

## Step-by-Step Fix

### **Option A: Create Connection via SQL**

1. Open a Databricks SQL editor or notebook
2. Run the CREATE CONNECTION statement:

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'patkYOUR_ACTUAL_TOKEN_HERE',
  base_id 'appYOUR_BASE_ID',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';
```

3. Verify creation:
```sql
SHOW CONNECTIONS;
```

4. Return to the Community Connectors UI and refresh

### **Option B: Create Connection via UI**

1. In the Community Connectors flow, click **"Create connection"**
2. Fill in the connection details:
   - **Name:** `airtable`
   - **Type:** `GENERIC_LAKEFLOW_CONNECT`
   - **Options:**
     - `sourceName`: `airtable`
     - `bearer_token`: Your Airtable token
     - `base_id`: Your Airtable base ID
     - `base_url`: `https://api.airtable.com/v0`

3. Save and proceed with ingestion setup

---

## Verification Checklist

Before proceeding with ingestion:

- [ ] Connection exists: `SHOW CONNECTIONS;` returns `airtable`
- [ ] Connection type is correct: `GENERIC_LAKEFLOW_CONNECT`
- [ ] You have permissions: `DESCRIBE CONNECTION airtable;` succeeds
- [ ] Options are correct: `sourceName`, `bearer_token`, `base_id`, `base_url`
- [ ] You're in the correct workspace (e2-dogfood staging)
- [ ] You're in the correct catalog context

---

## Common Mistakes

### ❌ **Mistake 1: Wrong Connection Type**
```sql
-- Wrong:
CREATE CONNECTION airtable TYPE EXTERNAL ...

-- Correct:
CREATE CONNECTION airtable TYPE GENERIC_LAKEFLOW_CONNECT ...
```

### ❌ **Mistake 2: Missing sourceName**
```sql
-- Wrong:
OPTIONS (
  bearer_token '...',
  base_id '...'
)

-- Correct:
OPTIONS (
  sourceName 'airtable',  -- ← Required!
  bearer_token '...',
  base_id '...'
)
```

### ❌ **Mistake 3: Case Sensitivity**
```sql
-- Connection names are case-sensitive in some contexts
SHOW CONNECTIONS;  -- Might show "Airtable" vs "airtable"
```

---

## Debug Information to Collect

If the issue persists, gather this information:

1. **Current Workspace:**
   - URL: `https://e2-dogfood.staging.cloud.databricks.com/...`
   - Workspace ID: (visible in URL)

2. **Current Context:**
   ```sql
   SELECT current_catalog(), current_schema();
   ```

3. **All Connections:**
   ```sql
   SHOW CONNECTIONS;
   ```

4. **User Permissions:**
   ```sql
   SHOW GRANTS ON CONNECTION airtable;
   ```

5. **Screenshot of:**
   - The Community Connectors UI
   - The SQL query results

---

## After Creating/Finding Connection

Once the connection appears in the UI:

1. **Select the connection:** `airtable` should now be in the dropdown
2. **Proceed to Ingestion Setup** (Step 2)
3. **Configure tables** to ingest
4. **Set destination** catalog/schema
5. **Create and run** the DLT pipeline

---

## Still Having Issues?

### **Quick Test:**
Try creating a test connection with a different name:

```sql
CREATE CONNECTION IF NOT EXISTS airtable_test
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_token',
  base_id 'your_base_id',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Test connection';
```

If this appears in the UI but `airtable` doesn't, there may be a caching issue. Try:
- Refreshing the page
- Clearing browser cache
- Using an incognito window

### **Contact Your Expert:**
Share these details:
- Workspace: e2-dogfood staging
- Issue: Connection not visible in UI
- What you tried: (list steps above)
- SQL query results: (attach SHOW CONNECTIONS output)

---

## References

- **Unity Catalog Connections:** https://docs.databricks.com/en/connect/unity-catalog/connections.html
- **Lakeflow Community Connectors:** https://github.com/databrickslabs/lakeflow-community-connectors
- **Your Connector Docs:** `docs/DEPLOYMENT.md`

---

**Last Updated:** January 8, 2026
