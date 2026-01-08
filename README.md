# Airtable Lakeflow Community Connector

A production-ready Databricks Lakeflow connector for ingesting data from Airtable into Delta tables using Unity Catalog connections.

**Status:** ✅ Production Ready  
**Version:** v1.1.0  
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

2. **Databricks Repos** with this code checked out

### Deploy in 3 Steps

1. **Sync Databricks Repo:**
   - Go to Repos → Your repo → Pull latest changes

2. **Create DLT Pipeline:**
   - Workflows → Delta Live Tables → Create Pipeline
   - Source: `/Repos/.../airtable-lakeflow-connector/ingest.py`
   - Target: Your catalog and schema
   - **NO configuration keys needed!**

3. **Run Pipeline:**
   - Click Start
   - Data flows from Airtable → Delta tables automatically

---

## ✨ Key Features

- ✅ **Zero Explicit Credentials** - UC connection handles everything automatically
- ✅ **Table Discovery** - Automatically discover all tables in Airtable base
- ✅ **Schema Inference** - Map Airtable field types to Spark types
- ✅ **Table Name Sanitization** - Handle spaces and special characters
- ✅ **Delta Lake Integration** - Write to Unity Catalog tables
- ✅ **SCD Support** - Type 1 and Type 2 slowly changing dimensions
- ✅ **Incremental Sync** - `createdTime`-based incremental loads
- ✅ **DLT Compatible** - Full Delta Live Tables integration
- ✅ **Local Testing** - Validate before deployment
- ✅ **Retry Logic** - Exponential backoff for API failures

---

## 📂 Project Structure

```
airtable-connector/
├── ingest.py                      # Databricks deployment entry point
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
├── pipeline/                      # Framework layer (official)
│   ├── ingestion_pipeline.py     # DLT orchestration (SDP pattern)
│   └── lakeflow_python_source.py # Spark Data Source registration
│
├── libs/                          # Utilities
│   ├── common/
│   │   └── source_loader.py      # Source registration
│   └── spec_parser.py            # Spec validation & sanitization
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
    ├── DEPLOYMENT.md              # Databricks deployment guide
    ├── LOCAL_TESTING.md           # Local testing guide
    └── TROUBLESHOOTING.md         # Common issues & solutions
```

---

## 🚀 Deployment

### Official Pattern (Recommended)

This connector uses the **official Lakeflow pattern** where:
- ✅ UC connection stores credentials
- ✅ Spark Data Source API retrieves them automatically
- ✅ NO explicit credential access anywhere
- ✅ NO Databricks secrets configuration
- ✅ NO pipeline configuration keys

**How it works:**
```
UC Connection → Spark Data Source API → Connector → Airtable API
```

See **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** for complete instructions.

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

### Pipeline Spec (in `ingest.py`)

```python
pipeline_spec = {
    "connection_name": "airtable",  # UC connection name
    
    "objects": [
        {
            "table": {
                "source_table": "Packaging Tasks",      # Airtable table name
                "destination_catalog": "main",          # Target catalog
                "destination_schema": "default",        # Target schema
                "destination_table": "packaging_tasks", # Target table (optional)
                
                # Optional: Advanced configuration
                "table_configuration": {
                    "scd_type": "SCD_TYPE_1",           # or SCD_TYPE_2, APPEND_ONLY
                    "primary_keys": ["id"],             # Primary keys (default: ["id"])
                    "sequence_by": "updated_at",        # For SCD Type 2
                    "batch_size": 100,                  # API batch size
                    "filter_formula": "..."             # Airtable filter
                }
            }
        }
    ]
}
```

### Table Name Sanitization

Tables with spaces or special characters are automatically sanitized:

| Airtable Table Name | Sanitized Name |
|---------------------|----------------|
| `Packaging Tasks` | `packaging_tasks` |
| `Creative Requests` | `creative_requests` |
| `My-Table (2024)` | `my_table_2024` |

You can override by explicitly setting `destination_table`.

---

## 🐛 Troubleshooting

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'pipeline'` | Code not in Repos | Move to `/Repos/`, not `/Workspace/` |
| `[NO_TABLES_IN_PIPELINE]` | Old ingestion pipeline | Sync repo to get latest code |
| `404 Not Found` | Wrong base_id | Check UC connection settings |
| `401 Unauthorized` | Invalid token | Regenerate Airtable token |

See **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** for detailed solutions.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** | Complete Databricks deployment guide |
| **[LOCAL_TESTING.md](./docs/LOCAL_TESTING.md)** | Local development and testing |
| **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** | Common issues and solutions |
| **[CHANGELOG.md](./CHANGELOG.md)** | Version history and changes |

---

## 🏗️ Architecture

### Credential Flow (Zero Explicit Access)

```
1. UC Connection
   └─> Stores: bearer_token, base_id, base_url

2. ingest.py
   └─> Calls: register_lakeflow_source(spark)
   └─> Registers: AirtableLakeflowConnector as Spark Data Source

3. ingestion_pipeline.py
   └─> Calls: spark.read.format("lakeflow_connect")
              .option("databricks.connection", "airtable")
              .load()

4. Spark Data Source API
   └─> Retrieves connection "airtable" from UC
   └─> Extracts credentials automatically
   └─> Passes to AirtableLakeflowConnector

5. Connector
   └─> Makes API calls to Airtable
   └─> Returns data to Spark

6. DLT
   └─> Applies SCD/CDC logic
   └─> Writes to Delta tables
```

**Key Point:** Credentials flow through Spark's Data Source API automatically. No explicit access needed!

---

## 🔄 Update Workflow

When you make changes:

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

3. **Databricks Sync:**
   - Repos → Your repo → Pull

4. **Rerun Pipeline:**
   - DLT automatically uses updated code

---

## 📊 Example Tables

### Packaging Tasks
```sql
SELECT * FROM main.default.packaging_tasks LIMIT 5;
```

### Campaigns
```sql
SELECT * FROM main.default.campaigns LIMIT 5;
```

### Creative Requests
```sql
SELECT * FROM main.default.creative_requests LIMIT 5;
```

---

## 🤝 Contributing

This connector follows the official Databricks Lakeflow Community Connectors framework.

**Framework Reference:**  
https://github.com/databrickslabs/lakeflow-community-connectors

**Key Principles:**
- ✅ Implement `LakeflowConnect` interface
- ✅ Use official `ingestion_pipeline.py` (SDP pattern)
- ✅ Support Unity Catalog connections
- ✅ Enable local testing
- ✅ Zero explicit credentials

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

1. **Check Documentation:** See `docs/` folder
2. **Review CHANGELOG:** See `CHANGELOG.md` for known issues
3. **Test Locally:** Run `python ingest_local.py` to isolate issues
4. **Check Logs:** DLT UI → Event Log for detailed errors

---

**🎉 Ready to ingest Airtable data into Databricks!**

**Version:** v1.1.0 | **Status:** Production Ready | **Pattern:** Official Lakeflow (Zero Explicit Credentials)
