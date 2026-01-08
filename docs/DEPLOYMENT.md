# 🚀 Databricks Deployment Guide

## ⚠️ **Important: See WORKSPACE_DEPLOYMENT.md**

This connector is designed for **Workspace deployment** using the official Databricks Lakeflow UI tool.

**For complete deployment instructions, see:**  
**[../WORKSPACE_DEPLOYMENT.md](../WORKSPACE_DEPLOYMENT.md)**

---

## 🎯 Quick Start

### Method 1: Official Lakeflow UI Tool (Recommended)

1. **In Databricks:** +New → Add or upload data → Community connectors

2. **Enter GitHub URL:**
   ```
   https://github.com/kaustavpaul107355/airtable-lakeflow-connector
   ```

3. **Configure:**
   - Source: UC connection `airtable`
   - Tables: Select tables to ingest
   - Destination: Your catalog and schema

4. **Deploy & Run!**

---

### Method 2: Manual Workspace Upload

If you need to manually upload files:

1. Upload complete directory structure to `/Workspace/Users/your.name@databricks.com/airtable-connector/`
2. Create DLT pipeline via UI
3. Point to `ingest.py` in your Workspace folder

---

## 📋 Prerequisites

### 1. Unity Catalog Connection

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_airtable_token',
  base_id 'your_base_id',
  base_url 'https://api.airtable.com/v0'
);
```

**Verify:**
```sql
SHOW CONNECTIONS;
DESCRIBE CONNECTION airtable;
```

---

## ✅ Key Points

- ✅ **Works in /Workspace/** - No Repos access required
- ✅ **Zero explicit credentials** - Retrieved from UC connection automatically
- ✅ **No serialization** - Connector runs on driver only
- ✅ **Official UI compatible** - Deploy via Databricks Lakeflow UI tool
- ✅ **No configuration keys** - UC connection handles everything

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'sources'`

**Cause:** Missing files or incorrect directory structure

**Fix:** Ensure all files uploaded (see WORKSPACE_DEPLOYMENT.md Step 1)

---

### Error: `Cannot retrieve UC connection credentials`

**Cause:** UC connection not accessible

**Fix:**
1. Verify connection exists: `SHOW CONNECTIONS;`
2. Check connection details: `DESCRIBE CONNECTION airtable;`
3. Verify you have `USE CONNECTION` permission

---

### Error: `404 Not Found` from Airtable API

**Cause:** Wrong base_id or table names

**Fix:**
1. Verify base_id in UC connection
2. Check table names match exactly (case-sensitive)
3. Test locally first: `python ingest_local.py`

---

## 📖 Complete Documentation

For detailed step-by-step instructions, see:

- **[WORKSPACE_DEPLOYMENT.md](../WORKSPACE_DEPLOYMENT.md)** - Complete deployment guide
- **[LOCAL_TESTING.md](./LOCAL_TESTING.md)** - Local testing guide
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues & solutions
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history

---

## 🔗 Quick Links

- **GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector
- **Databricks Lakeflow:** https://github.com/databrickslabs/lakeflow-community-connectors
- **Airtable API:** https://airtable.com/developers/web/api/introduction

---

**For complete deployment instructions with screenshots and troubleshooting, see [WORKSPACE_DEPLOYMENT.md](../WORKSPACE_DEPLOYMENT.md)**
