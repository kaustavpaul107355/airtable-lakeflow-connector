"""
Lakeflow Ingestion Pipeline (Updated with Pydantic Validation)

This module provides the orchestration logic for running Lakeflow connectors.
It handles:
- Pipeline spec parsing and validation (Pydantic)
- Table iteration
- DataFrame creation and writing to Delta Lake
- Error handling and logging
"""

from typing import Dict, Any, Union
import sys
import os

# Add pipeline-spec to path for imports
pipeline_spec_path = os.path.join(os.path.dirname(__file__), '..', 'pipeline-spec')
if pipeline_spec_path not in sys.path:
    sys.path.insert(0, pipeline_spec_path)

try:
    from airtable_spec import AirtablePipelineSpec, load_pipeline_spec_from_dict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️  Pydantic validation not available. Install pydantic>=2.5.0 for validation.")


def ingest(spark, pipeline_spec: Union[Dict[str, Any], 'AirtablePipelineSpec']):
    """
    Execute a Lakeflow ingestion pipeline with Pydantic validation.
    
    Args:
        spark: SparkSession
        pipeline_spec: Pipeline configuration (dict or AirtablePipelineSpec)
            - Can be a raw dict (will be validated)
            - Can be a pre-validated AirtablePipelineSpec object
    
    Raises:
        ValidationError: If pipeline_spec is invalid
    
    Example pipeline_spec (dict):
        {
            "token": "patkXXX...",
            "base_id": "appXXX...",
            "default_catalog": "my_catalog",
            "default_schema": "airtable_data",
            "objects": [
                {
                    "table": {
                        "source_table": "Customers",
                        "destination_table": "customers",
                        "table_configuration": {
                            "scd_type": "SCD_TYPE_1"
                        }
                    }
                }
            ]
        }
    
    Example pipeline_spec (Pydantic):
        >>> from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig
        >>> spec = AirtablePipelineSpec(
        ...     token="patkXXX...",
        ...     base_id="appXXX...",
        ...     default_catalog="my_catalog",
        ...     default_schema="airtable_data",
        ...     objects=[TableSpec(table=TableConfig(source_table="Customers"))]
        ... )
        >>> ingest(spark, spec)
    """
    
    # Validate and convert to Pydantic model if needed
    if PYDANTIC_AVAILABLE:
        if isinstance(pipeline_spec, dict):
            try:
                spec = load_pipeline_spec_from_dict(pipeline_spec)
                print(f"✅ Pipeline spec validated successfully")
            except Exception as e:
                print(f"❌ Pipeline spec validation failed:")
                print(f"   {e}")
                raise
        else:
            # Already a Pydantic model
            spec = pipeline_spec
    else:
        # Fallback to dict-based parsing (no validation)
        print("⚠️  Running without Pydantic validation")
        if isinstance(pipeline_spec, dict):
            spec = type('obj', (object,), {
                'connection_name': pipeline_spec.get('connection_name'),
                'token': pipeline_spec.get('token'),
                'base_id': pipeline_spec.get('base_id'),
                'default_catalog': pipeline_spec.get('default_catalog'),
                'default_schema': pipeline_spec.get('default_schema'),
                'objects': [type('obj', (object,), {
                    'table': type('obj', (object,), {
                        'source_table': obj.get('table', {}).get('source_table'),
                        'destination_catalog': obj.get('table', {}).get('destination_catalog'),
                        'destination_schema': obj.get('table', {}).get('destination_schema'),
                        'destination_table': obj.get('table', {}).get('destination_table', 
                            obj.get('table', {}).get('source_table', '').lower().replace(' ', '_')),
                        'table_configuration': type('obj', (object,), {
                            'scd_type': obj.get('table', {}).get('table_configuration', {}).get('scd_type', 'SCD_TYPE_1'),
                            'batch_size': obj.get('table', {}).get('table_configuration', {}).get('batch_size', 100),
                            'filter_formula': obj.get('table', {}).get('table_configuration', {}).get('filter_formula'),
                        })(),
                    })()
                })() for obj in pipeline_spec.get('objects', [])]
            })()
        else:
            spec = pipeline_spec
    
    connection_name = spec.connection_name if hasattr(spec, 'connection_name') else None
    default_catalog = spec.default_catalog
    default_schema = spec.default_schema
    objects = spec.objects
    
    # Get credentials
    token = spec.token if hasattr(spec, 'token') else None
    base_id = spec.base_id if hasattr(spec, 'base_id') else None
    
    print(f"🚀 Starting Lakeflow ingestion pipeline")
    print(f"   Connection: {connection_name if connection_name else 'Direct credentials'}")
    print(f"   Default target: {default_catalog}.{default_schema}")
    print(f"   Tables to sync: {len(objects)}")
    print()
    
    for obj_spec in objects:
        # Access table config from Pydantic model
        table = obj_spec.table if hasattr(obj_spec, 'table') else obj_spec
        source_table = table.source_table if hasattr(table, 'source_table') else None
        
        if not source_table:
            print(f"⚠️  Skipping object with no source_table defined")
            continue
        
        # Determine target location (Pydantic model provides defaults)
        dest_catalog = table.destination_catalog or default_catalog
        dest_schema = table.destination_schema or default_schema
        dest_table = table.destination_table
        
        # Use helper method if available
        if PYDANTIC_AVAILABLE and hasattr(spec, 'get_full_table_name'):
            full_table_name = spec.get_full_table_name(table)
        else:
            full_table_name = f"{dest_catalog}.{dest_schema}.{dest_table}"
        
        print(f"📊 Syncing table: {source_table} → {full_table_name}")
        
        try:
            # Read from Lakeflow connector
            df = (
                spark.read
                .format("lakeflow_connect")
                .option("tableName", source_table)
                .option("source_name", "airtable")
            )
            
            # Add credentials (if provided directly in pipeline_spec)
            if token:
                df = df.option("token", token)
            if base_id:
                df = df.option("base_id", base_id)
            
            # Add connection options (if using UC connection)
            if connection_name:
                df = df.option("databricks.connection", connection_name)
            
            # Add any table-specific options
            if hasattr(table, 'table_configuration'):
                config = table.table_configuration
                df = df.option("batch_size", str(config.batch_size if hasattr(config, 'batch_size') else 100))
                
                if hasattr(config, 'filter_formula') and config.filter_formula:
                    df = df.option("filter_formula", config.filter_formula)
            
            df = df.load()
            
            # Write to Delta Lake
            if hasattr(table, 'table_configuration'):
                scd_type = table.table_configuration.scd_type if hasattr(table.table_configuration, 'scd_type') else "SCD_TYPE_1"
            else:
                scd_type = "SCD_TYPE_1"
            
            if scd_type == "SCD_TYPE_1":
                # Simple overwrite
                df.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
                print(f"   ✅ Wrote {df.count()} records (SCD_TYPE_1)")
            
            elif scd_type == "SCD_TYPE_2":
                # SCD Type 2 is not yet implemented (planned for future release)
                # See ROADMAP.md for implementation details
                print(f"   ⚠️  SCD_TYPE_2 not yet supported, falling back to full refresh")
                df.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
                print(f"   ✅ Wrote {df.count()} records (overwrite mode)")
            
            elif scd_type == "APPEND_ONLY":
                df.write.format("delta").mode("append").saveAsTable(full_table_name)
                print(f"   ✅ Appended {df.count()} records")
            
            else:
                raise ValueError(f"Unknown scd_type: {scd_type}")
            
        except Exception as e:
            print(f"   ❌ Error syncing {source_table}: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        print()
    
    print("🎉 Pipeline execution complete!")

