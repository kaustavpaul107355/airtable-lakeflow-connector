"""
Airtable connector package for Lakeflow.
"""

from .airtable import AirtableLakeflowConnector

# Alias for compatibility with Lakeflow template
LakeflowConnect = AirtableLakeflowConnector

__all__ = ["AirtableLakeflowConnector", "LakeflowConnect"]

