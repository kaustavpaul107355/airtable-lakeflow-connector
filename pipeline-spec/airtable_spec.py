"""
Airtable Pipeline Specification using Pydantic

This module defines the validated schema for Airtable ingestion pipelines,
following the Lakeflow Community Connectors standard.

Example Usage:
    >>> from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig
    >>> 
    >>> spec = AirtablePipelineSpec(
    ...     token="patk...",
    ...     base_id="app...",
    ...     default_catalog="my_catalog",
    ...     default_schema="airtable_data",
    ...     objects=[
    ...         TableSpec(table=TableConfig(source_table="Customers"))
    ...     ]
    ... )
    >>> print(spec.get_full_table_name(spec.objects[0].table))
    'my_catalog.airtable_data.customers'
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Literal
from enum import Enum


class SCDType(str, Enum):
    """Slowly Changing Dimension types for table updates"""
    
    SCD_TYPE_1 = "SCD_TYPE_1"      # Full refresh / overwrite
    SCD_TYPE_2 = "SCD_TYPE_2"      # Track history with versioning
    APPEND_ONLY = "APPEND_ONLY"    # Append only, no updates


class TableConfiguration(BaseModel):
    """Table-specific configuration options for sync behavior"""
    
    scd_type: SCDType = Field(
        default=SCDType.SCD_TYPE_1,
        description="How to handle updates: SCD_TYPE_1 (overwrite), SCD_TYPE_2 (history), APPEND_ONLY"
    )
    
    primary_keys: Optional[List[str]] = Field(
        default=None,
        description="Override primary keys (defaults to connector's recommendation: ['id'])"
    )
    
    filter_formula: Optional[str] = Field(
        default=None,
        description="Airtable formula to filter records (e.g., \"{Status} = 'Active'\")",
        example="{Status} = 'Active'"
    )
    
    batch_size: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Records per API request (1-100, Airtable limit)"
    )
    
    class Config:
        use_enum_values = True
        extra = "forbid"


class TableConfig(BaseModel):
    """Configuration for a single table to sync from Airtable"""
    
    source_table: str = Field(
        ...,  # Required field
        min_length=1,
        description="Name of the table in Airtable (case-sensitive)",
        example="SKU Candidates"
    )
    
    destination_catalog: Optional[str] = Field(
        default=None,
        description="Target catalog (defaults to pipeline default)"
    )
    
    destination_schema: Optional[str] = Field(
        default=None,
        description="Target schema (defaults to pipeline default)"
    )
    
    destination_table: Optional[str] = Field(
        default=None,
        description="Target table name (defaults to sanitized source_table)",
        example="sku_candidates"
    )
    
    table_configuration: TableConfiguration = Field(
        default_factory=TableConfiguration,
        description="Table-specific sync options"
    )
    
    @field_validator('destination_table', mode='before')
    @classmethod
    def default_destination_table(cls, v, info):
        """Auto-generate destination table name from source if not provided"""
        if not v and info.data.get('source_table'):
            # Sanitize: lowercase, replace spaces and special chars with underscores
            sanitized = (
                info.data['source_table']
                .lower()
                .replace(' ', '_')
                .replace('-', '_')
                .replace('(', '')
                .replace(')', '')
                .replace('/', '_')
                .replace('.', '_')
            )
            return sanitized
        return v
    
    class Config:
        extra = "forbid"


class TableSpec(BaseModel):
    """Wrapper for table configuration (matches YAML structure)"""
    
    table: TableConfig = Field(
        ...,
        description="Table configuration object"
    )
    
    class Config:
        extra = "forbid"


class AirtablePipelineSpec(BaseModel):
    """
    Complete Airtable pipeline specification with validation.
    
    Follows the Lakeflow Community Connectors standard for pipeline specs.
    
    Authentication Options:
        - connection_name: Unity Catalog connection (for metadata/governance)
        - token + base_id: Direct authentication (required if no connection_name)
    
    Example:
        >>> spec = AirtablePipelineSpec(
        ...     token="patkBXwClC7keLEX5...",
        ...     base_id="appSaRcgA5UCGoRg5",
        ...     default_catalog="kaustavpaul_demo",
        ...     default_schema="airtable_connector",
        ...     objects=[
        ...         TableSpec(table=TableConfig(
        ...             source_table="Vendors",
        ...             destination_table="vendors",
        ...             table_configuration=TableConfiguration(
        ...                 scd_type=SCDType.SCD_TYPE_1
        ...             )
        ...         ))
        ...     ]
        ... )
    """
    
    # Authentication (mutually exclusive options)
    connection_name: Optional[str] = Field(
        default=None,
        description="Unity Catalog connection name (for metadata/governance only)"
    )
    
    token: Optional[str] = Field(
        default=None,
        min_length=20,
        description="Airtable Personal Access Token (required if no connection_name)"
    )
    
    base_id: Optional[str] = Field(
        default=None,
        pattern=r'^app[a-zA-Z0-9]+$',
        description="Airtable Base ID (required, format: app...)",
        example="appSaRcgA5UCGoRg5"
    )
    
    # Target location
    default_catalog: str = Field(
        ...,  # Required
        min_length=1,
        description="Default target catalog for all tables",
        example="kaustavpaul_demo"
    )
    
    default_schema: str = Field(
        ...,  # Required
        min_length=1,
        description="Default target schema for all tables",
        example="airtable_connector"
    )
    
    # Tables to sync
    objects: List[TableSpec] = Field(
        ...,  # Required
        min_items=1,
        description="List of tables to sync from Airtable"
    )
    
    @model_validator(mode='after')
    def validate_authentication(self):
        """Ensure valid authentication configuration"""
        connection_name = self.connection_name
        token = self.token
        base_id = self.base_id
        
        # Must have base_id always
        if not base_id:
            raise ValueError(
                "base_id is required. "
                "Get it from your Airtable base URL: https://airtable.com/{BASE_ID}/..."
            )
        
        # Must have either connection_name OR token (not both, not neither)
        if connection_name and token:
            raise ValueError(
                "Cannot specify both connection_name and token. "
                "Use connection_name for UC metadata OR token for direct auth."
            )
        
        if not connection_name and not token:
            raise ValueError(
                "Must provide either connection_name (for UC) or token (for direct auth). "
                "Get a token from: https://airtable.com/create/tokens"
            )
        
        return self
    
    @field_validator('objects', mode='after')
    @classmethod
    def validate_unique_destinations(cls, v, info):
        """Ensure no duplicate destination tables"""
        default_catalog = info.data.get('default_catalog')
        default_schema = info.data.get('default_schema')
        
        destinations = set()
        for obj in v:
            table = obj.table
            catalog = table.destination_catalog or default_catalog
            schema = table.destination_schema or default_schema
            dest_table = table.destination_table
            
            full_name = f"{catalog}.{schema}.{dest_table}"
            if full_name in destinations:
                raise ValueError(
                    f"Duplicate destination table: {full_name}. "
                    f"Each table must have a unique destination."
                )
            destinations.add(full_name)
        
        return v
    
    class Config:
        extra = "forbid"  # Reject unknown fields
        validate_assignment = True  # Validate on field assignment
    
    def get_full_table_name(self, table_config: TableConfig) -> str:
        """
        Get fully qualified table name for a table config.
        
        Args:
            table_config: Table configuration
        
        Returns:
            Fully qualified name: catalog.schema.table
        
        Example:
            >>> spec.get_full_table_name(spec.objects[0].table)
            'kaustavpaul_demo.airtable_connector.vendors'
        """
        catalog = table_config.destination_catalog or self.default_catalog
        schema = table_config.destination_schema or self.default_schema
        table = table_config.destination_table
        return f"{catalog}.{schema}.{table}"


# Convenience functions for loading from YAML/dict

def load_pipeline_spec_from_dict(data: dict) -> AirtablePipelineSpec:
    """
    Load and validate pipeline spec from dictionary.
    
    Args:
        data: Dictionary (from YAML or JSON)
    
    Returns:
        Validated AirtablePipelineSpec
    
    Raises:
        ValidationError: If spec is invalid
    
    Example:
        >>> data = {
        ...     "token": "patk...",
        ...     "base_id": "app...",
        ...     "default_catalog": "my_catalog",
        ...     "default_schema": "my_schema",
        ...     "objects": [{"table": {"source_table": "Customers"}}]
        ... }
        >>> spec = load_pipeline_spec_from_dict(data)
    """
    return AirtablePipelineSpec(**data)


def load_pipeline_spec_from_yaml(yaml_path: str) -> AirtablePipelineSpec:
    """
    Load and validate pipeline spec from YAML file.
    
    Args:
        yaml_path: Path to YAML file
    
    Returns:
        Validated AirtablePipelineSpec
    
    Raises:
        ValidationError: If spec is invalid
        FileNotFoundError: If file doesn't exist
    
    Example:
        >>> spec = load_pipeline_spec_from_yaml("pipeline-spec/airtable_pipeline.yaml")
    """
    import yaml
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return AirtablePipelineSpec(**data)


# Type aliases for convenience
PipelineSpec = AirtablePipelineSpec

__all__ = [
    'AirtablePipelineSpec',
    'TableSpec',
    'TableConfig',
    'TableConfiguration',
    'SCDType',
    'load_pipeline_spec_from_dict',
    'load_pipeline_spec_from_yaml',
    'PipelineSpec',
]

