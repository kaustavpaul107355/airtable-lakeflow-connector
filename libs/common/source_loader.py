"""
Source loader utility for dynamically loading Lakeflow connectors.
"""

import importlib


def get_register_function(source_name: str):
    """
    Get the registration function for a specific source connector.
    
    Args:
        source_name: Name of the source (e.g., 'airtable', 'github', 'zendesk')
    
    Returns:
        Function that registers the Lakeflow data source with Spark
    
    Example:
        register_fn = get_register_function('airtable')
        register_fn(spark)
    """
    def register_lakeflow_source(spark):
        """Register the Lakeflow data source with Spark"""
        from pipeline.lakeflow_python_source import LakeflowSource
        spark.dataSource.register(LakeflowSource)
        return LakeflowSource
    
    return register_lakeflow_source


def get_connector_class(source_name: str):
    """
    Dynamically load and return the connector class for a source.
    
    Args:
        source_name: Name of the source (e.g., 'airtable')
    
    Returns:
        The LakeflowConnect implementation class
    
    Example:
        ConnectorClass = get_connector_class('airtable')
        connector = ConnectorClass(options)
    """
    module = importlib.import_module(f"sources.{source_name}")
    return module.LakeflowConnect

