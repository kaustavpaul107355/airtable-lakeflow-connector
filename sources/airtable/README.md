# Airtable Connector

**Lakeflow Community Connector** for syncing Airtable data to Databricks Delta Lake.

---

## Overview

The Airtable connector implements the `LakeflowConnect` interface to provide seamless data ingestion from Airtable bases to Databricks Delta Lake tables.

### Features

- ✅ Automatic table discovery via Airtable Meta API
- ✅ Schema inference from Airtable field types
- ✅ Incremental syncs (snapshot, append-only)
- ✅ Column name sanitization for Delta Lake compatibility
- ✅ Pagination support for large tables (100 records/request)
- ✅ Retry logic with exponential backoff (3 retries)
- ✅ Configurable batch sizes and timeouts
- ✅ Support for complex field types (arrays, objects as JSON)

---

## Quick Start

### 1. Authentication

Create an Airtable Personal Access Token:
1. Go to https://airtable.com/create/tokens
2. Create a new token
3. Add scopes:
   - `data.records:read` (required)
   - `schema.bases:read` (required)
4. Add access to your base
5. Copy the token (starts with `patk...`)

### 2. Get Your Base ID

From your Airtable base URL:
```
https://airtable.com/{BASE_ID}/...
                      ^^^^^^^^^^^
                      This is your base_id
```

### 3. Use the Connector

```python
from sources.airtable.airtable import AirtableLakeflowConnector

# Initialize connector
connector = AirtableLakeflowConnector({
    "token": "patkXXX...",
    "base_id": "appXXX...",
})

# List tables
tables = connector.list_tables()
print(f"Available tables: {tables}")

# Get schema for a table
schema = connector.get_table_schema("Customers", {})
print(schema)

# Read table data
records_iter, next_offset = connector.read_table("Customers", {}, {})
for record in records_iter:
    print(record)
```

---

## API Reference

### `AirtableLakeflowConnector(options)`

Initialize the connector with configuration options.

#### Parameters

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `token` | str | ✅ Yes | - | Airtable Personal Access Token |
| `base_id` | str | ✅ Yes | - | Airtable Base ID (format: `app...`) |
| `batch_size` | int | No | 100 | Records per API request (1-100) |
| `max_retries` | int | No | 3 | Maximum retry attempts |
| `timeout` | int | No | 30 | Request timeout in seconds |

#### Example

```python
connector = AirtableLakeflowConnector({
    "token": "patkXXX...",
    "base_id": "appXXX...",
    "batch_size": 50,        # Smaller batches
    "max_retries": 5,        # More retries
    "timeout": 60,           # Longer timeout
})
```

---

### `list_tables() -> list[str]`

List all tables in the Airtable base.

#### Returns
- `list[str]`: List of table names

#### Example

```python
tables = connector.list_tables()
# Returns: ["Customers", "Orders", "Products"]
```

#### Raises
- `ConnectionError`: If API request fails after retries

---

### `get_table_schema(table_name, table_options) -> StructType`

Get PySpark schema for a table.

#### Parameters
- `table_name` (str): Name of the table (case-sensitive)
- `table_options` (dict): Additional options (unused for Airtable)

#### Returns
- `StructType`: PySpark schema with sanitized column names

#### Example

```python
schema = connector.get_table_schema("Customers", {})

# Schema fields are automatically:
# - Lowercased
# - Spaces replaced with underscores
# - Special characters removed

# Example transformation:
# "Customer Name" → "customer_name"
# "SKU (2024)" → "sku_2024"
```

#### Column Types

| Airtable Type | PySpark Type | Notes |
|---------------|--------------|-------|
| Single line text | StringType | - |
| Long text | StringType | - |
| Number | DoubleType | Integers also mapped to Double |
| Checkbox | BooleanType | - |
| Date | StringType | ISO 8601 format |
| Phone | StringType | - |
| Email | StringType | - |
| URL | StringType | - |
| Multiple select | StringType | JSON array as string |
| Attachments | StringType | JSON array of URLs |
| Linked records | StringType | JSON array of IDs |
| Rollup | StringType | Varies by formula |
| Formula | StringType | Result as string |

---

### `read_table_metadata(table_name, table_options) -> dict`

Get metadata about a table for ingestion configuration.

#### Parameters
- `table_name` (str): Name of the table
- `table_options` (dict): Additional options

#### Returns

```python
{
    "primary_keys": ["id"],              # Always ["id"] for Airtable
    "cursor_field": "createdtime",       # For incremental syncs
    "ingestion_type": "snapshot"         # Default ingestion mode
}
```

#### Ingestion Types

- **`snapshot`**: Full table refresh (default)
- **`append`**: Append new records only
- **`cdc`**: Change Data Capture (not yet supported for Airtable)

---

### `read_table(table_name, start_offset, table_options) -> tuple[Iterator[dict], dict]`

Read data from a table with pagination and incremental sync support.

#### Parameters
- `table_name` (str): Name of the table
- `start_offset` (dict): Starting offset for incremental reads
  - `{}`: Read from beginning
  - `{"offset": "rec..."}`: Resume from offset
- `table_options` (dict): Additional options (unused)

#### Returns
- `Iterator[dict]`: Iterator of records as dictionaries
- `dict`: Next offset for incremental reads

#### Example

```python
# Full read
records_iter, next_offset = connector.read_table("Customers", {}, {})
records = list(records_iter)
print(f"Read {len(records)} records")

# Incremental read (resume from offset)
more_records, final_offset = connector.read_table("Customers", next_offset, {})
```

#### Record Format

```python
{
    "id": "recXXX...",                    # Airtable record ID
    "createdtime": "2024-01-01T00:00:00Z",  # ISO timestamp
    "customer_name": "John Doe",          # Sanitized field names
    "email": "john@example.com",
    "tags": '["vip", "active"]',          # Arrays as JSON strings
    # ... other fields
}
```

---

## Usage with Spark

### Register Data Source

```python
from pipeline.lakeflow_python_source import LakeflowSource

# Register the data source
spark.dataSource.register(LakeflowSource)
```

### Read as DataFrame

```python
df = (
    spark.read
    .format("lakeflow_connect")
    .option("source_name", "airtable")
    .option("token", "patkXXX...")
    .option("base_id", "appXXX...")
    .option("tableName", "Customers")
    .load()
)

df.show()
```

### Use with Pipeline

```python
from pipeline.ingestion_pipeline import ingest
from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig

spec = AirtablePipelineSpec(
    token="patkXXX...",
    base_id="appXXX...",
    default_catalog="my_catalog",
    default_schema="airtable_data",
    objects=[
        TableSpec(table=TableConfig(
            source_table="Customers",
            destination_table="customers"
        ))
    ]
)

ingest(spark, spec)
```

---

## Field Type Mapping

### Simple Types

```python
# Airtable → PySpark
"Single line text" → StringType()
"Number" → DoubleType()
"Checkbox" → BooleanType()
"Date" → StringType()  # ISO 8601
```

### Complex Types

```python
# Multiple select (stored as JSON string)
["tag1", "tag2"] → '["tag1", "tag2"]'

# Attachments (stored as JSON string)
[{"url": "...", "filename": "..."}] → '[{"url": "...", "filename": "..."}]'

# Linked records (stored as JSON string)
["recXXX", "recYYY"] → '["recXXX", "recYYY"]'
```

To parse complex types in Spark:

```python
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import ArrayType, StringType

# Parse JSON array
df_parsed = df.withColumn(
    "tags_array",
    from_json(col("tags"), ArrayType(StringType()))
)
```

---

## Column Name Sanitization

Airtable allows spaces and special characters in field names, but Delta Lake has restrictions. The connector automatically sanitizes column names:

### Sanitization Rules

| Original | Sanitized | Rule |
|----------|-----------|------|
| `Customer Name` | `customer_name` | Spaces → underscores |
| `SKU (2024)` | `sku_2024` | Parentheses removed |
| `Price/Unit` | `price_unit` | Slashes → underscores |
| `Config.File` | `config_file` | Dots → underscores |
| `First-Name` | `first_name` | Hyphens → underscores |

All names are also **lowercased** for consistency.

---

## Performance

### Pagination

- **Batch size**: 100 records per request (Airtable API limit)
- **Automatic pagination**: Handles tables with 1000s of records
- **Memory efficient**: Uses iterators, not loading all data at once

### Rate Limiting

- **Airtable limit**: 5 requests/second
- **Connector handling**: Built-in retry logic with exponential backoff
- **Configurable**: Adjust `max_retries` and `timeout` as needed

### Optimization Tips

```python
# For large tables
connector = AirtableLakeflowConnector({
    "token": "...",
    "base_id": "...",
    "batch_size": 100,     # Max batch size
    "max_retries": 5,      # More retries for reliability
    "timeout": 60,         # Longer timeout for large responses
})
```

---

## Error Handling

### Common Errors

#### 1. **403 Forbidden**

**Cause**: Token lacks permissions or table doesn't exist  
**Solution**:
- Verify token has `data.records:read` and `schema.bases:read` scopes
- Check table name is case-sensitive and correct
- Ensure base is added to token's access list

#### 2. **401 Unauthorized**

**Cause**: Invalid or expired token  
**Solution**:
- Generate a new token at https://airtable.com/create/tokens
- Verify token format (should start with `patk`)

#### 3. **404 Not Found**

**Cause**: Base ID is incorrect  
**Solution**:
- Verify base_id from Airtable URL
- Format should be `appXXX...` (starts with `app`)

#### 4. **429 Too Many Requests**

**Cause**: Rate limit exceeded (5 requests/second)  
**Solution**:
- Automatic retry logic handles this
- Increase `max_retries` if needed
- Add delays between manual requests

### Retry Logic

The connector automatically retries failed requests with exponential backoff:

```
Attempt 1: Immediate
Attempt 2: 2 seconds delay
Attempt 3: 4 seconds delay
```

---

## Limitations

### Current Limitations

- ❌ **No write support**: Read-only connector (intentional design)
- ❌ **No formula evaluation**: Formulas are not evaluated server-side
- ❌ **Attachment data not downloaded**: Only URLs are stored
- ⚠️ **Rate limits**: Airtable's 5 requests/second limit applies
- ⚠️ **Complex types as strings**: Arrays/objects stored as JSON strings

### Workarounds

**For write operations**:
- Use Airtable's API directly or another tool

**For formula fields**:
- Formulas return computed results (read-only)

**For attachments**:
- URLs are provided; download separately if needed

---

## Examples

### Example 1: List All Tables

```python
connector = AirtableLakeflowConnector({
    "token": "patkXXX...",
    "base_id": "appXXX...",
})

tables = connector.list_tables()
for table in tables:
    print(f"- {table}")
```

### Example 2: Inspect Schema

```python
table_name = "Customers"
schema = connector.get_table_schema(table_name, {})

print(f"Schema for {table_name}:")
for field in schema.fields:
    print(f"  {field.name}: {field.dataType}")
```

### Example 3: Read with Pagination

```python
table_name = "Large Table"
all_records = []
offset = {}

while True:
    records_iter, next_offset = connector.read_table(table_name, offset, {})
    batch = list(records_iter)
    
    if not batch:
        break
    
    all_records.extend(batch)
    offset = next_offset
    
    print(f"Read {len(batch)} records, total: {len(all_records)}")

print(f"Finished! Total records: {len(all_records)}")
```

### Example 4: Filter and Transform

```python
# Read data
records_iter, _ = connector.read_table("Customers", {}, {})
records = list(records_iter)

# Filter active customers
active_customers = [
    r for r in records 
    if r.get("status") == "active"
]

# Create Spark DataFrame
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

df = spark.createDataFrame(active_customers)
df.show()
```

---

## Testing

### Unit Tests

```bash
# Run connector tests
pytest tests/test_airtable_connector.py -v
```

### Integration Tests

```bash
# Requires live Airtable credentials
pytest --integration \
  --airtable-token="patkXXX..." \
  --airtable-base-id="appXXX..." \
  -v
```

### Test Credentials

Set test credentials via:
1. **Command line**: `pytest --airtable-token=... --airtable-base-id=...`
2. **Environment**: `export AIRTABLE_TEST_TOKEN=... AIRTABLE_TEST_BASE_ID=...`
3. **File**: Create `.credentials` in project root

---

## Contributing

Contributions welcome! This connector follows the Lakeflow Community Connectors standard.

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black sources/airtable/

# Lint
ruff sources/airtable/

# Type check
mypy sources/airtable/
```

---

## Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: See main [README.md](../../README.md)
- **Lakeflow Standard**: [databrickslabs/lakeflow-community-connectors](https://github.com/databrickslabs/lakeflow-community-connectors)

---

**Version**: 1.0.0  
**Last Updated**: January 5, 2026  
**Status**: Production Ready ✅

