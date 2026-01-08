# Airtable Lakeflow Community Connector

A production-ready Databricks Lakeflow connector for ingesting data from Airtable into Delta tables using Unity Catalog connections.

**Status:** ✅ Production Ready  
**Version:** v1.2.0 (Workspace Deployment)  
**Framework:** [Databricks Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)  
**Last Updated:** January 8, 2026

---

## 🎯 Quick Start

### Prerequisites
1. **Unity Catalog Connection** (stores credentials securely):
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

2. **GitHub Repository** with this connector code

### Deploy Using Official Lakeflow UI

1. **In Databricks:** +New → Add or upload data → Community connectors

2. **Point to GitHub:**
   ```
   https://github.com/kaustavpaul107355/airtable-lakeflow-connector
   ```

3. **Configure Pipeline:**
   - Source: UC connection `airtable`
   - Tables: Select tables to ingest
   - Destination: Your catalog and schema
   - **NO configuration keys needed!**

4. **Deploy & Run** - Data flows automatically!

---

## ✨ Key Features

- ✅ **Zero Explicit Credentials** - UC connection handles everything automatically
- ✅ **Workspace Deployment** - Works without Repos access
- ✅ **No Serialization** - Connector runs on driver only
- ✅ **Official UI Tool** - Deploy via Databricks Lakeflow UI
- ✅ **Table Discovery** - Automatically discover all tables in Airtable base
- ✅ **Schema Inference** - Map Airtable field types to Spark types
- ✅ **Table Name Sanitization** - Handle spaces and special characters
- ✅ **Delta Lake Integration** - Write to Unity Catalog tables
- ✅ **DLT Compatible** - Full Delta Live Tables integration
- ✅ **Local Testing** - Validate before deployment
- ✅ **Retry Logic** - Exponential backoff for API failures

---

## 📂 Project Structure

```
airtable-connector/
├── ingest.py                      # Main entry point (Workspace deployment)
├── ingest_local.py                # Local testing script
├── create_uc_connection.sql       # UC connection template
├── setup_local_test.sh            # Local setup automation
│
├── sources/                       # Connector implementation
│   ├── airtable/
│   │   └── airtable.py           # Main connector class
│   └── interface/
│       └── lakeflow_connect.py   # Base interface
│
├── libs/                          # Utilities
│   ├── common/
│   │   └── source_loader.py      # Framework utilities
│   └── spec_parser.py            # Spec validation & sanitization
│
├── pipeline/                      # Framework layer (preserved for compatibility)
│   ├── ingestion_pipeline.py     # Official DLT orchestration
│   └── lakeflow_python_source.py # Spark Data Source registration
│
├── pipeline-spec/                 # Pydantic models
│   └── airtable_spec.py          # Pipeline spec validation
│
├── tests/                         # Unit tests
│   ├── test_airtable_connector.py
│   ├── test_pipeline_spec.py
│   └── test_pydantic_integration.py
│
└── docs/                          # Documentation
    ├── WORKSPACE_DEPLOYMENT.md    # Complete deployment guide
    ├── LOCAL_TESTING.md           # Local testing guide
    └── TROUBLESHOOTING.md         # Common issues & solutions
```

---

## 🚀 Deployment

### Method 1: Official Lakeflow UI (Recommended)

**This is the easiest method - use the official Databricks UI tool:**

1. Go to: **+New → Add or upload data → Community connectors**
2. Enter GitHub URL: `https://github.com/kaustavpaul107355/airtable-lakeflow-connector`
3. Configure tables and destination
4. Deploy!

**The UI tool will:**
- ✅ Clone code from GitHub to Workspace
- ✅ Discover the connector automatically
- ✅ Create DLT pipeline
- ✅ Handle all setup

See **[WORKSPACE_DEPLOYMENT.md](./WORKSPACE_DEPLOYMENT.md)** for detailed instructions.

---

### Method 2: Manual Workspace Upload

If you need to deploy manually:

1. Upload complete directory structure to `/Workspace/Users/your.name@databricks.com/airtable-connector/`
2. Create DLT pipeline via UI
3. Point to `ingest.py` in your Workspace folder

See **[WORKSPACE_DEPLOYMENT.md](./WORKSPACE_DEPLOYMENT.md)** for step-by-step guide.

---

## 🧪 Local Testing

Test your connector before deploying to Databricks:

```bash
# 1. Setup (one-time)
cd airtable-connector
./setup_local_test.sh

# 2. Configure credentials
cp .credentials.example .credentials
# Edit .credentials with your Airtable token and base_id

# 3. Run tests
source venv/bin/activate
python ingest_local.py
```

Expected output:
```
✅ Connection test passed
✅ Table discovery passed (3 tables found)
✅ Schema inference passed
✅ Data read passed (X records)
```

See **[docs/LOCAL_TESTING.md](./docs/LOCAL_TESTING.md)** for detailed instructions.

---

## 📋 Configuration

### Unity Catalog Connection

```sql
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'your_token',      -- Airtable Personal Access Token
  base_id 'your_base_id',         -- Airtable base ID (e.g., appXXXXXXXXXXXXXX)
  base_url 'https://api.airtable.com/v0'  -- API base URL
);
```

### Pipeline Spec (in `ingest.py`)

The connector is pre-configured for three tables. To add more tables, edit `ingest.py`:

```python
@dlt.table(name="your_table_name", comment="Your Table")
def your_function_name():
    source_table = "Your Table Name"  # Exact name in Airtable
    schema = connector.get_table_schema(source_table, {})
    records_iter, _ = connector.read_table(source_table, {}, {})
    records = list(records_iter)
    return spark.createDataFrame(records, schema)
```

---

## 🏗️ Architecture

### How It Works (No Serialization)

```
1. UC Connection
   └─> Stores: bearer_token, base_id, base_url

2. ingest.py (runs on driver)
   └─> Queries UC via SQL: system.information_schema.connections
   └─> Creates: AirtableLakeflowConnector instance (driver only)

3. @dlt.table functions
   └─> Call connector methods on driver
   └─> Fetch data from Airtable API
   └─> Return simple DataFrames

4. Spark Workers
   └─> Receive only simple data (no connector code)
   └─> No serialization issues!

5. DLT
   └─> Writes DataFrames to Delta tables
```

**Key Point:** Connector stays on driver, only data goes to workers!

---

## 🐛 Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'sources'` | Missing files or wrong structure | Verify all files uploaded (see WORKSPACE_DEPLOYMENT.md) |
| `Cannot retrieve UC connection credentials` | UC connection not accessible | Run `DESCRIBE CONNECTION airtable;` to verify |
| `404 Not Found` | Wrong base_id or table names | Check UC connection settings |
| `401 Unauthorized` | Invalid token | Regenerate Airtable token |

See **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** for detailed solutions.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[WORKSPACE_DEPLOYMENT.md](./WORKSPACE_DEPLOYMENT.md)** | Complete deployment guide (UI tool & manual) |
| **[docs/LOCAL_TESTING.md](./docs/LOCAL_TESTING.md)** | Local development and testing |
| **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** | Common issues and solutions |
| **[CHANGELOG.md](./CHANGELOG.md)** | Version history and changes |

---

## 🔄 Update Workflow

When you update the code in GitHub:

1. **Local Development:**
   ```bash
   # Edit code
   python ingest_local.py  # Test locally
   ```

2. **Git Sync:**
   ```bash
   git add -A
   git commit -m "Your changes"
   git push origin main
   ```

3. **Redeploy:**
   - Use Lakeflow UI tool to redeploy from GitHub
   - Or manually update files in Workspace

---

## 📊 Example Usage

### Query Your Data

```sql
-- Check tables created
SHOW TABLES IN main.default;

-- View data
SELECT * FROM main.default.packaging_tasks LIMIT 10;
SELECT * FROM main.default.campaigns LIMIT 10;
SELECT * FROM main.default.creative_requests LIMIT 10;

-- Row counts
SELECT COUNT(*) FROM main.default.packaging_tasks;
```

---

## 🤝 Contributing

This connector follows the official Databricks Lakeflow Community Connectors framework.

**Framework Reference:**  
https://github.com/databrickslabs/lakeflow-community-connectors

**Key Principles:**
- ✅ Implement `LakeflowConnect` interface
- ✅ Support Unity Catalog connections
- ✅ Enable local testing
- ✅ Zero explicit credentials
- ✅ Works in Workspace (no Repos required)

---

## 📝 License

Apache 2.0

---

## 🔗 Links

- **GitHub:** https://github.com/kaustavpaul107355/airtable-lakeflow-connector
- **Databricks Lakeflow:** https://github.com/databrickslabs/lakeflow-community-connectors
- **Airtable API:** https://airtable.com/developers/web/api/introduction

---

## 📞 Support

1. **Check Documentation:** See `docs/` folder and `WORKSPACE_DEPLOYMENT.md`
2. **Review CHANGELOG:** See `CHANGELOG.md` for known issues
3. **Test Locally:** Run `python ingest_local.py` to isolate issues
4. **Check Logs:** DLT UI → Event Log for detailed errors

---

## ✅ What Makes This Connector Special

- 🎯 **Works in Workspace** - No Repos access required
- 🔒 **Zero Explicit Credentials** - UC connection handles everything
- 🚀 **No Serialization** - Avoids common Spark distribution issues
- 🛠️ **Official UI Compatible** - Deploy via Databricks Lakeflow UI tool
- 🧪 **Local Testing** - Validate before deployment
- 📦 **Complete Package** - All files and docs included

---

**🎉 Ready to ingest Airtable data into Databricks!**

**Version:** v1.2.0 (Workspace Deployment) | **Status:** Production Ready | **Pattern:** Simplified (No Serialization)
