# 🚨 URGENT: DLT Table Definition Issue

## Problem

```
[NO_TABLES_IN_PIPELINE] Pipelines are expected to have at least one table defined  
but no tables were found in your pipeline.
```

## Root Cause

Our `ingestion_pipeline.py` doesn't use DLT/SDP decorators. DLT expects to see table definitions using `@dlt.table()` or `@sdp.view()` decorators, but our code just reads and writes data without declaring tables.

## What's Wrong

**Current implementation (INCORRECT for DLT):**
```python
# pipeline/ingestion_pipeline.py
def ingest(spark, pipeline_spec):
    for obj in objects:
        df = spark.read.format("lakeflow_connect").load()  # No DLT decorator!
        df.write.saveAsTable(table_name)  # Direct write, no DLT table
```

**Official pattern (CORRECT for DLT):**
```python
# From official lakeflow-community-connectors
from pyspark import pipelines as sdp

def ingest(spark, pipeline_spec):
    for table in tables:
        @sdp.view(name=view_name)  # DLT decorator!
        def create_view():
            return spark.read.format("lakeflow_connect").load()
        
        sdp.create_streaming_table(name=destination_table)  # DLT table!
        sdp.apply_changes(...)
```

## Solution Required

We need to update `pipeline/ingestion_pipeline.py` to use the official Lakeflow pattern from:
https://github.com/databrickslabs/lakeflow-community-connectors/blob/master/pipeline/ingestion_pipeline.py

This file uses:
- `from pyspark import pipelines as sdp`
- `@sdp.view()` decorators
- `sdp.create_streaming_table()` and `sdp.apply_changes()`

## Impact

This is a **fundamental architectural issue**. Our implementation was designed for direct Spark usage, but DLT requires declarative table definitions with decorators.

## Options

### Option 1: Use Official ingestion_pipeline.py
Replace our custom implementation with the official one from the Lakeflow repository.

### Option 2: Contact Expert ASAP
The expert might have a simpler deployment method that doesn't require manual DLT pipeline setup.

### Option 3: Simplified DLT Version
Create a minimal DLT-compatible version that uses decorators.

## Recommendation

**Contact your Databricks expert immediately** with this question:

> "My custom Airtable connector works perfectly in local testing (8/8 tests passed).  
> However, when I try to run it in a DLT pipeline, I get:  
> `[NO_TABLES_IN_PIPELINE] no tables were found`
>
> This is because my `ingestion_pipeline.py` doesn't use `@dlt.table()` or `@sdp.view()` decorators.
> 
> The official Lakeflow framework uses Spark Declarative Pipeline (SDP) with decorators.
> My implementation directly reads/writes data without DLT table definitions.
> 
> **Questions:**
> 1. Should I use the official Lakeflow UI/CLI tools instead of manual DLT setup?
> 2. Or do I need to rewrite my ingestion_pipeline.py to use SDP decorators?
> 3. Is there a simpler deployment path for custom connectors?
> 
> Repository: https://github.com/kaustavpaul107355/airtable-lakeflow-connector  
> Connector works: Local tests all pass  
> Issue: DLT deployment pattern mismatch"

## Why This Happened

I built a working connector implementation but didn't realize that DLT pipelines require declarative table definitions with decorators, not imperative read/write code. The connector itself is correct - it's just the DLT integration layer that needs updating.

---

**Status:** Awaiting expert guidance on deployment approach  
**Created:** January 8, 2026
