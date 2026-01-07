"""
Lakeflow Airtable Connector

Production-ready connector for syncing Airtable data to Databricks Delta Lake,
following the Lakeflow Community Connectors standard.

Example:
    >>> from sources import AirtableLakeflowConnector
    >>> connector = AirtableLakeflowConnector({
    ...     "token": "patk...",
    ...     "base_id": "app...",
    ... })
    >>> tables = connector.list_tables()
"""

__version__ = "1.0.0"
__author__ = "Kaustav Paul"
__license__ = "Apache-2.0"

from .airtable import AirtableLakeflowConnector, LakeflowConnect

__all__ = [
    "AirtableLakeflowConnector",
    "LakeflowConnect",
    "airtable",
    "interface",
    "__version__",
]

