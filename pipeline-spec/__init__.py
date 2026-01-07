"""
Airtable Pipeline Specification Package

Provides Pydantic models for type-safe, validated pipeline configuration
following the Lakeflow Community Connectors standard.

Example:
    >>> from pipeline_spec import AirtablePipelineSpec, TableSpec, TableConfig
    >>> spec = AirtablePipelineSpec(
    ...     token="patk...",
    ...     base_id="app...",
    ...     default_catalog="my_catalog",
    ...     default_schema="my_schema",
    ...     objects=[
    ...         TableSpec(table=TableConfig(source_table="Customers"))
    ...     ]
    ... )
"""

from .airtable_spec import (
    AirtablePipelineSpec,
    TableSpec,
    TableConfig,
    TableConfiguration,
    SCDType,
    load_pipeline_spec_from_dict,
    load_pipeline_spec_from_yaml,
    PipelineSpec,
)

__version__ = "1.0.0"
__author__ = "Kaustav Paul"
__license__ = "Apache-2.0"

__all__ = [
    "AirtablePipelineSpec",
    "TableSpec",
    "TableConfig",
    "TableConfiguration",
    "SCDType",
    "load_pipeline_spec_from_dict",
    "load_pipeline_spec_from_yaml",
    "PipelineSpec",
    "__version__",
]

