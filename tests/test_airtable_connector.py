"""
Tests for Airtable Lakeflow Connector

Run these tests against a live Airtable base to validate the connector.
"""

import pytest
from sources.airtable import LakeflowConnect


# Test configuration - update these with your credentials
TEST_OPTIONS = {
    "token": "YOUR_TEST_TOKEN",  # Replace with actual token for testing
    "base_id": "YOUR_TEST_BASE_ID",  # Replace with actual base ID
}


@pytest.fixture
def connector():
    """Create a connector instance for testing"""
    return LakeflowConnect(TEST_OPTIONS)


def test_connector_initialization():
    """Test that connector initializes correctly"""
    connector = LakeflowConnect(TEST_OPTIONS)
    assert connector.base_id == TEST_OPTIONS["base_id"]


def test_list_tables(connector):
    """Test that connector can list tables"""
    tables = connector.list_tables()
    assert isinstance(tables, list)
    assert len(tables) > 0
    print(f"Found {len(tables)} tables: {tables}")


def test_get_table_schema(connector):
    """Test that connector can get table schema"""
    tables = connector.list_tables()
    assert len(tables) > 0
    
    first_table = tables[0]
    schema = connector.get_table_schema(first_table, {})
    
    assert schema is not None
    assert len(schema.fields) > 0
    # Should have at least id and createdTime fields
    field_names = [f.name for f in schema.fields]
    assert "id" in field_names
    assert "createdTime" in field_names
    print(f"Schema for '{first_table}': {schema.simpleString()}")


def test_read_table_metadata(connector):
    """Test that connector returns metadata"""
    tables = connector.list_tables()
    assert len(tables) > 0
    
    first_table = tables[0]
    metadata = connector.read_table_metadata(first_table, {})
    
    assert "primary_keys" in metadata
    assert "cursor_field" in metadata
    assert "ingestion_type" in metadata
    assert metadata["primary_keys"] == ["id"]
    print(f"Metadata for '{first_table}': {metadata}")


def test_read_table(connector):
    """Test that connector can read table data"""
    tables = connector.list_tables()
    assert len(tables) > 0
    
    first_table = tables[0]
    records_iter, next_offset = connector.read_table(first_table, {}, {})
    
    # Read first few records
    records = []
    for i, record in enumerate(records_iter):
        records.append(record)
        if i >= 4:  # Just read first 5 records
            break
    
    assert len(records) > 0
    assert "id" in records[0]
    assert "createdTime" in records[0]
    print(f"Read {len(records)} sample records from '{first_table}'")
    print(f"Next offset: {next_offset}")


def test_incremental_read(connector):
    """Test incremental reading with offset"""
    tables = connector.list_tables()
    assert len(tables) > 0
    
    first_table = tables[0]
    
    # First read
    records_iter1, offset1 = connector.read_table(first_table, {}, {})
    records1 = list(records_iter1)
    
    # Second read with offset (should return no new records in test)
    records_iter2, offset2 = connector.read_table(first_table, offset1, {})
    records2 = list(records_iter2)
    
    print(f"First read: {len(records1)} records, offset: {offset1}")
    print(f"Second read: {len(records2)} records, offset: {offset2}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

