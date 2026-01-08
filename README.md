# Airtable Lakeflow Community Connector

A production-ready Databricks Lakeflow connector for ingesting data from Airtable into Delta tables using Unity Catalog connections.

**Status:** ✅ Implementation Complete - Ready for Official Tool Integration  
**Framework:** [Databricks Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors)  
**Last Updated:** January 8, 2026

---

## ⚠️ **IMPORTANT: Two Deployment Modes**

This connector supports both **local testing** and **Databricks deployment**:

| File | Purpose | Where to Use |
|------|---------|--------------|
| **`ingest.py`** | Databricks deployment (production) | ☁️ Databricks workspace |
| **`ingest_local.py`** | Local testing with mock Spark | 💻 Your local machine |

**Use `ingest.py` for all Databricks deployments** - it has the correct import paths and no `__file__` dependencies.

📚 **Documentation:**
- **[Databricks Deployment Guide](./docs/DEPLOYMENT.md)** - Complete Databricks deployment instructions
- **[Local Testing Guide](./docs/LOCAL_TESTING.md)** - Local development and testing

---

## 🎯 Quick Start

This connector is designed to be deployed using the official Databricks UI or CLI tools.

### Using Databricks UI (Recommended)
1. Go to Databricks workspace
2. Click **"+New"** → **"Add or upload data"** → **"Community connectors"**
3. Click **"+ Add Community Connector"**
4. Point to this repository
5. Configure tables and destination
6. Deploy!

### Using CLI Tool
```bash
# Clone the official repository
git clone https://github.com/databrickslabs/lakeflow-community-connectors.git
cd lakeflow-community-connectors/tools/community_connector

# Use CLI to create connector (follow tool documentation)
# Integrate this Airtable connector code
```

---

## 📊 What This Connector Does

### Capabilities
- ✅ **Full Airtable Integration** - Connect to any Airtable base
- ✅ **Unity Catalog Support** - Secure credential management via UC connections
- ✅ **Incremental Reads** - Efficient data synchronization
- ✅ **Schema Detection** - Automatic schema discovery
- ✅ **Type Mapping** - Airtable types → Spark types
- ✅ **Multiple Tables** - Sync multiple tables simultaneously
- ✅ **SCD Type 2** - Historical tracking support

### Supported Airtable Features
- **Tables:** Any table in your Airtable base
- **Fields:** All standard field types (text, number, date, attachments, etc.)
- **Formulas:** Read formula values
- **Linked Records:** Capture linked record IDs
- **Attachments:** Store attachment metadata and URLs

---

## 🏗️ Project Structure

```
airtable-connector/
├── sources/                           # Connector implementation
│   ├── airtable/
│   │   ├── airtable.py               # ✅ Main connector (production-ready)
│   │   ├── __init__.py
│   │   └── README.md                  # Connector-specific docs
│   └── interface/
│       ├── lakeflow_connect.py        # Base interface
│       └── __init__.py
│
├── pipeline-spec/                     # Pipeline specification
│   ├── airtable_spec.py              # ✅ Pydantic spec (production-ready)
│   └── __init__.py
│
├── pipeline/                          # Framework files
│   ├── ingestion_pipeline.py         # Core ingestion logic
│   ├── lakeflow_python_source.py     # PySpark Data Source
│   └── __init__.py
│
├── libs/                              # Shared utilities
│   └── common/
│       ├── source_loader.py          # Module loading
│       └── __init__.py
│
├── tests/                             # Test suite
│   ├── test_airtable_connector.py    # Connector tests
│   ├── test_pipeline_spec.py         # Spec tests
│   ├── test_pydantic_integration.py  # Integration tests
│   ├── conftest.py                   # Fixtures
│   └── __init__.py
│
├── docs/                              # Documentation
│   └── archive/                       # Historical/learning materials
│
├── README.md                          # This file
├── OFFICIAL_APPROACH_GUIDE.md        # Deployment guide
└── CLEANUP_REPORT.md                 # Cleanup documentation
```

---

## 🔑 Prerequisites

### 1. Unity Catalog Connection

Create a UC connection for Airtable:

```sql
CREATE CONNECTION airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  base_url 'https://api.airtable.com',
  base_id 'your_base_id',
  access_token 'your_access_token'
);
```

**How to get credentials:**
- **Base ID:** Found in Airtable URL: `https://airtable.com/{base_id}/...`
- **Access Token:** Create at https://airtable.com/create/tokens
  - Required scopes: `data.records:read`, `schema.bases:read`

### 2. Databricks Requirements
- Unity Catalog enabled
- Delta Live Tables (DLT) access
- Workspace permissions for creating connectors

---

## 📋 Configuration Example

When using the UI or CLI tools, configure your connector with a pipeline spec:

```python
pipeline_spec = {
    "connection_name": "airtable",  # UC connection name
    "base_id": "appXXXXXXXXXXXXXX",
    "default_catalog": "my_catalog",
    "default_schema": "airtable_data",
    "objects": [
        {
            "table": {
                "source_table": "Tasks",
                "destination_table": "tasks",
                "primary_keys": ["id"]
            }
        },
        {
            "table": {
                "source_table": "Projects",
                "destination_table": "projects",
                "primary_keys": ["id"]
            }
        }
    ]
}
```

---

## 🚀 Implementation Details

### Connector Class: `AirtableLakeflowConnector`

Located in `sources/airtable/airtable.py`:

```python
class AirtableLakeflowConnector(LakeflowConnect):
    """
    Airtable connector implementing the LakeflowConnect interface.
    
    Supports:
    - Dynamic schema discovery
    - Incremental data reads
    - UC connection credential resolution
    - Type mapping (Airtable → Spark)
    """
    
    def __init__(self, options: dict[str, str]) -> None:
        """Initialize with UC connection options."""
    
    def list_tables(self) -> list[str]:
        """List all tables in the Airtable base."""
    
    def get_table_schema(self, table_name: str, ...) -> StructType:
        """Get Spark schema for an Airtable table."""
    
    def read_table_metadata(self, table_name: str, ...) -> dict:
        """Get table metadata (keys, cursor field, ingestion type)."""
    
    def read_table(self, table_name: str, ...) -> (Iterator[dict], dict):
        """Read table data incrementally."""
```

### Pipeline Specification: `AirtablePipelineSpec`

Located in `pipeline-spec/airtable_spec.py`:

```python
class AirtablePipelineSpec(BaseModel):
    """
    Pydantic model for pipeline configuration validation.
    
    Features:
    - Field validation
    - Type checking
    - Default value handling
    - Pydantic v2 compatible
    """
    
    connection_name: str  # UC connection
    base_id: Optional[str]  # Airtable base ID
    default_catalog: str  # Target catalog
    default_schema: str  # Target schema
    objects: List[TableSpec]  # Tables to sync
```

---

## 🧪 Testing

Run the test suite:

```bash
# Install dependencies
pip install pytest pydantic pyairtable pyspark

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_airtable_connector.py -v

# Run with coverage
pytest tests/ --cov=sources --cov=pipeline-spec
```

### Test Coverage:
- ✅ Connector initialization and authentication
- ✅ Table listing and schema detection
- ✅ Type mapping validation
- ✅ Incremental read logic
- ✅ Pipeline spec validation (Pydantic v2)
- ✅ UC connection integration

---

## 📚 Documentation

### Main Documentation:
- **[OFFICIAL_APPROACH_GUIDE.md](./OFFICIAL_APPROACH_GUIDE.md)** - Deployment using UI/CLI tools
- **[sources/airtable/README.md](./sources/airtable/README.md)** - Connector-specific documentation
- **[CLEANUP_REPORT.md](./CLEANUP_REPORT.md)** - Codebase organization details

### Archived Learning Materials:
See `docs/archive/` for historical documentation and troubleshooting guides created during development.

---

## 🔧 Technical Details

### Authentication
- Uses Unity Catalog connections (`GENERIC_LAKEFLOW_CONNECT`)
- No credentials in code or configuration
- Secure token management via UC

### Data Flow
```
Airtable API
    ↓
UC Connection (credentials)
    ↓
AirtableLakeflowConnector (this code)
    ↓
Spark Data Source API
    ↓
Delta Live Tables
    ↓
Delta Tables (Unity Catalog)
```

### Type Mapping

| Airtable Type | Spark Type | Notes |
|---------------|------------|-------|
| singleLineText | StringType | - |
| multilineText | StringType | - |
| number | DoubleType | Includes decimals |
| currency | DecimalType(18,2) | Fixed precision |
| date | DateType | - |
| dateTime | TimestampType | With timezone |
| checkbox | BooleanType | - |
| singleSelect | StringType | Value stored |
| multipleSelects | ArrayType(StringType) | Array of values |
| multipleRecordLinks | ArrayType(StringType) | Array of linked IDs |
| attachment | ArrayType(StructType) | Array of attachment objects |
| formula | StringType | Computed value |
| rollup | StringType | Aggregated value |

---

## 🐛 Troubleshooting

### Common Issues:

**Issue:** "Connection 'airtable' not found"  
**Solution:** Create UC connection (see Prerequisites section)

**Issue:** "Invalid credentials"  
**Solution:** Verify access token has required scopes and is valid

**Issue:** "Base not found"  
**Solution:** Check base_id in UC connection matches your Airtable base

**Issue:** "Table not found"  
**Solution:** Verify table name matches exactly (case-sensitive)

For more help, see the [GitHub repository issues](https://github.com/databrickslabs/lakeflow-community-connectors/issues).

---

## 🤝 Contributing

This connector follows the [Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors) framework.

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See `CONTRIBUTING.md` in the main repository for detailed guidelines.

---

## 📄 License

This project follows the license of the parent [Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors) repository.

---

## 🙏 Acknowledgments

- Built on the [Databricks Lakeflow Community Connectors](https://github.com/databrickslabs/lakeflow-community-connectors) framework
- Uses the [Spark Python Data Source API](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataSource.html)
- Integrates with [Airtable API](https://airtable.com/developers/web/api/introduction)

---

## 📞 Support

- **Framework Issues:** [GitHub Issues](https://github.com/databrickslabs/lakeflow-community-connectors/issues)
- **Airtable API:** [Airtable Support](https://support.airtable.com/)
- **Databricks:** [Databricks Documentation](https://docs.databricks.com/)

---

## 🚀 Next Steps

1. **Review** [OFFICIAL_APPROACH_GUIDE.md](./OFFICIAL_APPROACH_GUIDE.md)
2. **Set up** Unity Catalog connection
3. **Deploy** using Databricks UI or CLI tool
4. **Configure** your tables and run the pipeline
5. **Monitor** data ingestion in DLT

**Your connector is ready to deploy!** ✨
