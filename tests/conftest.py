"""
Pytest configuration and shared fixtures for Airtable connector tests

This module provides:
- Test credentials management
- Connector fixtures
- Spark session fixtures
- Common test utilities
"""

import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ==============================================================================
# Test Configuration
# ==============================================================================

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires live Airtable connection)"
    )
    parser.addoption(
        "--airtable-token",
        action="store",
        default=None,
        help="Airtable Personal Access Token for testing"
    )
    parser.addoption(
        "--airtable-base-id",
        action="store",
        default=None,
        help="Airtable Base ID for testing"
    )


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires live connection)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --integration flag is passed"""
    if config.getoption("--integration"):
        return
    
    skip_integration = pytest.mark.skip(reason="need --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


# ==============================================================================
# Credential Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def airtable_credentials(request):
    """
    Load test credentials from environment or command line.
    
    Priority:
    1. Command line arguments (--airtable-token, --airtable-base-id)
    2. Environment variables (AIRTABLE_TEST_TOKEN, AIRTABLE_TEST_BASE_ID)
    3. .credentials file (if exists)
    
    Yields:
        dict: Credentials dictionary with 'token' and 'base_id'
    
    Raises:
        pytest.skip: If credentials are not available
    """
    # Try command line arguments
    token = request.config.getoption("--airtable-token")
    base_id = request.config.getoption("--airtable-base-id")
    
    # Try environment variables
    if not token:
        token = os.getenv("AIRTABLE_TEST_TOKEN")
    if not base_id:
        base_id = os.getenv("AIRTABLE_TEST_BASE_ID")
    
    # Try .credentials file
    if not token or not base_id:
        creds_file = os.path.join(os.path.dirname(__file__), '..', '.credentials')
        if os.path.exists(creds_file):
            with open(creds_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'AIRTABLE_TOKEN' and not token:
                            token = value.strip()
                        elif key.strip() == 'AIRTABLE_BASE_ID' and not base_id:
                            base_id = value.strip()
    
    if not token or not base_id:
        pytest.skip(
            "Airtable test credentials not found. Provide via:\n"
            "  1. Command line: pytest --airtable-token=... --airtable-base-id=...\n"
            "  2. Environment: export AIRTABLE_TEST_TOKEN=... AIRTABLE_TEST_BASE_ID=...\n"
            "  3. File: Create .credentials file with AIRTABLE_TOKEN and AIRTABLE_BASE_ID"
        )
    
    return {
        "token": token,
        "base_id": base_id,
    }


# ==============================================================================
# Connector Fixtures
# ==============================================================================

@pytest.fixture
def airtable_connector(airtable_credentials):
    """
    Create an Airtable connector instance for testing.
    
    Args:
        airtable_credentials: Fixture providing test credentials
    
    Returns:
        AirtableLakeflowConnector: Initialized connector instance
    """
    from sources.airtable.airtable import AirtableLakeflowConnector
    return AirtableLakeflowConnector(airtable_credentials)


@pytest.fixture
def connector_with_custom_options(airtable_credentials):
    """
    Factory fixture to create connectors with custom options.
    
    Args:
        airtable_credentials: Fixture providing test credentials
    
    Returns:
        Callable: Function that creates connector with custom options
    
    Example:
        >>> connector = connector_with_custom_options(batch_size=50, max_retries=5)
    """
    def _create_connector(**custom_options):
        from sources.airtable.airtable import AirtableLakeflowConnector
        options = {**airtable_credentials, **custom_options}
        return AirtableLakeflowConnector(options)
    
    return _create_connector


# ==============================================================================
# Spark Session Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def spark_session():
    """
    Create a Spark session for testing (if PySpark is available).
    
    Yields:
        SparkSession: Spark session for testing
    
    Raises:
        pytest.skip: If PySpark is not available
    """
    try:
        from pyspark.sql import SparkSession
        
        spark = (
            SparkSession.builder
            .appName("AirtableConnectorTests")
            .master("local[2]")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
            .getOrCreate()
        )
        
        yield spark
        
        spark.stop()
    except ImportError:
        pytest.skip("PySpark not available for testing")


@pytest.fixture
def spark_with_lakeflow_source(spark_session):
    """
    Spark session with LakeflowSource registered.
    
    Args:
        spark_session: Base Spark session fixture
    
    Returns:
        SparkSession: Spark session with data source registered
    """
    from pipeline.lakeflow_python_source import LakeflowSource
    spark_session.dataSource.register(LakeflowSource)
    return spark_session


# ==============================================================================
# Mock Fixtures
# ==============================================================================

@pytest.fixture
def mock_airtable_response():
    """
    Factory fixture for creating mock Airtable API responses.
    
    Returns:
        Callable: Function that creates mock response data
    
    Example:
        >>> response = mock_airtable_response(
        ...     records=[{"id": "rec123", "fields": {"Name": "Test"}}]
        ... )
    """
    def _create_response(records=None, offset=None):
        response = {}
        if records is not None:
            response["records"] = records
        if offset is not None:
            response["offset"] = offset
        return response
    
    return _create_response


@pytest.fixture
def mock_tables_response():
    """
    Factory fixture for creating mock table list responses.
    
    Returns:
        Callable: Function that creates mock table list data
    
    Example:
        >>> response = mock_tables_response(["Customers", "Orders"])
    """
    def _create_response(table_names):
        return {
            "tables": [{"name": name} for name in table_names]
        }
    
    return _create_response


# ==============================================================================
# Test Data Fixtures
# ==============================================================================

@pytest.fixture
def sample_airtable_records():
    """
    Sample Airtable records for testing.
    
    Returns:
        list: Sample records with various field types
    """
    return [
        {
            "id": "rec001",
            "createdTime": "2024-01-01T00:00:00.000Z",
            "fields": {
                "Name": "Product A",
                "Price": 99.99,
                "In Stock": True,
                "Tags": ["electronics", "featured"],
                "Description": "A great product"
            }
        },
        {
            "id": "rec002",
            "createdTime": "2024-01-02T00:00:00.000Z",
            "fields": {
                "Name": "Product B",
                "Price": 149.99,
                "In Stock": False,
                "Tags": ["furniture"],
                "Description": "Another product"
            }
        },
    ]


@pytest.fixture
def sample_table_schema():
    """
    Sample PySpark schema for testing.
    
    Returns:
        StructType: Sample schema matching sample records
    """
    from pyspark.sql.types import (
        StructType, StructField, StringType, DoubleType, BooleanType
    )
    
    return StructType([
        StructField("id", StringType(), False),
        StructField("createdtime", StringType(), True),
        StructField("name", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("in_stock", BooleanType(), True),
        StructField("tags", StringType(), True),  # JSON array as string
        StructField("description", StringType(), True),
    ])


# ==============================================================================
# Utility Fixtures
# ==============================================================================

@pytest.fixture
def temp_credentials_file(tmp_path):
    """
    Create a temporary .credentials file for testing.
    
    Args:
        tmp_path: pytest's built-in tmp_path fixture
    
    Returns:
        Path: Path to temporary credentials file
    """
    creds_file = tmp_path / ".credentials"
    creds_file.write_text(
        "AIRTABLE_TOKEN=patk_test_token_for_testing\n"
        "AIRTABLE_BASE_ID=appTestBase123\n"
    )
    return creds_file


@pytest.fixture(autouse=True)
def reset_imports():
    """
    Reset module imports between tests to ensure clean state.
    
    This fixture runs automatically for every test.
    """
    yield
    # Cleanup happens after test


# ==============================================================================
# Assertion Helpers
# ==============================================================================

@pytest.fixture
def assert_valid_schema():
    """
    Helper to assert that a schema is valid for Delta Lake.
    
    Returns:
        Callable: Function that validates schema
    """
    def _assert_schema(schema):
        from pyspark.sql.types import StructType
        
        assert isinstance(schema, StructType), "Schema must be StructType"
        assert len(schema.fields) > 0, "Schema must have at least one field"
        
        # Check for required fields
        field_names = [f.name for f in schema.fields]
        assert "id" in field_names, "Schema must include 'id' field"
        assert "createdtime" in field_names, "Schema must include 'createdtime' field"
        
        # Check for Delta Lake compatible names (lowercase, underscores)
        for field in schema.fields:
            assert field.name.islower(), f"Field name must be lowercase: {field.name}"
            assert " " not in field.name, f"Field name must not contain spaces: {field.name}"
        
        return True
    
    return _assert_schema


@pytest.fixture
def assert_valid_records():
    """
    Helper to assert that records are valid for ingestion.
    
    Returns:
        Callable: Function that validates records
    """
    def _assert_records(records):
        assert isinstance(records, list), "Records must be a list"
        
        for record in records:
            assert isinstance(record, dict), "Each record must be a dict"
            assert "id" in record, "Each record must have 'id'"
            assert isinstance(record["id"], str), "Record 'id' must be string"
        
        return True
    
    return _assert_records


# ==============================================================================
# Performance Fixtures
# ==============================================================================

@pytest.fixture
def benchmark_timer():
    """
    Simple benchmark timer for performance tests.
    
    Returns:
        Callable: Context manager for timing operations
    
    Example:
        >>> with benchmark_timer() as timer:
        ...     # do something
        ...     pass
        >>> print(f"Took {timer.elapsed:.2f} seconds")
    """
    import time
    
    class Timer:
        def __enter__(self):
            self.start = time.time()
            return self
        
        def __exit__(self, *args):
            self.end = time.time()
            self.elapsed = self.end - self.start
    
    return Timer


# ==============================================================================
# Cleanup Fixtures
# ==============================================================================

@pytest.fixture(scope="function", autouse=True)
def cleanup_test_tables(spark_session):
    """
    Cleanup test tables after each test.
    
    This fixture runs automatically for every test that uses spark_session.
    """
    yield
    
    # Cleanup test tables (if any were created)
    try:
        test_catalogs = ["test_catalog", "test_cat"]
        for catalog in test_catalogs:
            try:
                spark_session.sql(f"DROP SCHEMA IF EXISTS {catalog}.test_schema CASCADE")
            except:
                pass
    except:
        pass


# ==============================================================================
# Documentation
# ==============================================================================

@pytest.fixture
def test_documentation():
    """
    Provide documentation about test fixtures.
    
    Returns:
        dict: Documentation about available fixtures
    """
    return {
        "credentials": [
            "airtable_credentials",
            "temp_credentials_file",
        ],
        "connectors": [
            "airtable_connector",
            "connector_with_custom_options",
        ],
        "spark": [
            "spark_session",
            "spark_with_lakeflow_source",
        ],
        "mocks": [
            "mock_airtable_response",
            "mock_tables_response",
        ],
        "test_data": [
            "sample_airtable_records",
            "sample_table_schema",
        ],
        "utilities": [
            "assert_valid_schema",
            "assert_valid_records",
            "benchmark_timer",
        ],
    }

