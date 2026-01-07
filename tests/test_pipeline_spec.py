"""
Tests for Pydantic pipeline spec validation

These tests ensure that pipeline specifications are properly validated
and provide helpful error messages when misconfigured.
"""

import pytest
from pydantic import ValidationError
import sys
import os

# Add pipeline-spec to path for imports
pipeline_spec_path = os.path.join(os.path.dirname(__file__), '..', 'pipeline-spec')
if pipeline_spec_path not in sys.path:
    sys.path.insert(0, pipeline_spec_path)

from airtable_spec import (
    AirtablePipelineSpec,
    TableSpec,
    TableConfig,
    TableConfiguration,
    SCDType,
    load_pipeline_spec_from_dict,
)


# ==============================================================================
# Valid Spec Tests
# ==============================================================================

def test_valid_spec_with_token():
    """Test creating a valid spec with direct token authentication"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,  # Valid token format
        base_id="appTestBase123",
        default_catalog="catalog",
        default_schema="schema",
        objects=[
            TableSpec(table=TableConfig(source_table="Table1"))
        ]
    )
    
    assert spec.token.startswith("patk")
    assert spec.base_id == "appTestBase123"
    assert len(spec.objects) == 1
    assert spec.objects[0].table.source_table == "Table1"


def test_valid_spec_with_connection():
    """Test creating a valid spec with UC connection"""
    spec = AirtablePipelineSpec(
        connection_name="airtable_connection",
        base_id="appTest123",
        default_catalog="catalog",
        default_schema="schema",
        objects=[
            TableSpec(table=TableConfig(source_table="Table1"))
        ]
    )
    
    assert spec.connection_name == "airtable_connection"
    assert spec.token is None


def test_valid_spec_multiple_tables():
    """Test spec with multiple tables"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appTest",
        default_catalog="cat",
        default_schema="schema",
        objects=[
            TableSpec(table=TableConfig(source_table="Table1")),
            TableSpec(table=TableConfig(source_table="Table2")),
            TableSpec(table=TableConfig(source_table="Table3")),
        ]
    )
    
    assert len(spec.objects) == 3


# ==============================================================================
# Required Fields Tests
# ==============================================================================

def test_missing_required_fields():
    """Test that required fields are enforced"""
    with pytest.raises(ValidationError) as exc_info:
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            # Missing default_catalog and default_schema
            objects=[]
        )
    
    errors = exc_info.value.errors()
    field_names = [e['loc'][0] for e in errors]
    assert 'default_catalog' in field_names
    assert 'default_schema' in field_names


def test_missing_objects():
    """Test that at least one table is required"""
    with pytest.raises(ValidationError, match="at least 1 item"):
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[]  # Empty list not allowed
        )


def test_missing_source_table():
    """Test that source_table is required"""
    with pytest.raises(ValidationError):
        TableConfig()  # Missing source_table


# ==============================================================================
# Authentication Validation Tests
# ==============================================================================

def test_missing_authentication():
    """Test that either connection_name or token is required"""
    with pytest.raises(ValidationError, match="Must provide either"):
        AirtablePipelineSpec(
            # Missing both connection_name and token
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )


def test_both_authentication_methods():
    """Test that both connection_name and token cannot be provided"""
    with pytest.raises(ValidationError, match="Cannot specify both"):
        AirtablePipelineSpec(
            connection_name="conn",
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )


def test_missing_base_id():
    """Test that base_id is always required"""
    with pytest.raises(ValidationError, match="base_id is required"):
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            # Missing base_id
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )


# ==============================================================================
# Format Validation Tests
# ==============================================================================

def test_base_id_format():
    """Test base_id regex validation"""
    with pytest.raises(ValidationError, match="string does not match regex"):
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="invalid",  # Must start with 'app'
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )


def test_token_min_length():
    """Test token minimum length validation"""
    with pytest.raises(ValidationError, match="at least 20 characters"):
        AirtablePipelineSpec(
            token="short",  # Too short
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )


# ==============================================================================
# Duplicate Destination Tests
# ==============================================================================

def test_duplicate_destinations():
    """Test that duplicate destination tables are rejected"""
    with pytest.raises(ValidationError, match="Duplicate destination"):
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[
                TableSpec(table=TableConfig(
                    source_table="Table1",
                    destination_table="same_table"
                )),
                TableSpec(table=TableConfig(
                    source_table="Table2",
                    destination_table="same_table"  # Duplicate!
                ))
            ]
        )


def test_duplicate_destinations_across_catalogs_ok():
    """Test that same table name in different catalogs is allowed"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appTest",
        default_catalog="cat1",
        default_schema="schema",
        objects=[
            TableSpec(table=TableConfig(
                source_table="Table1",
                destination_table="same_table"
            )),
            TableSpec(table=TableConfig(
                source_table="Table2",
                destination_catalog="cat2",  # Different catalog
                destination_table="same_table"
            ))
        ]
    )
    
    assert len(spec.objects) == 2


# ==============================================================================
# Default Value Tests
# ==============================================================================

def test_default_destination_table():
    """Test that destination_table defaults to sanitized source_table"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appTest",
        default_catalog="cat",
        default_schema="schema",
        objects=[
            TableSpec(table=TableConfig(source_table="My Table"))
        ]
    )
    
    table = spec.objects[0].table
    assert table.destination_table == "my_table"  # Sanitized


def test_default_destination_table_special_chars():
    """Test sanitization of various special characters"""
    test_cases = [
        ("SKU Candidates", "sku_candidates"),
        ("Launch-Milestones", "launch_milestones"),
        ("Data (2024)", "data_2024"),
        ("Reports/Daily", "reports_daily"),
        ("Config.Files", "config_files"),
    ]
    
    for source, expected in test_cases:
        spec = AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[
                TableSpec(table=TableConfig(source_table=source))
            ]
        )
        assert spec.objects[0].table.destination_table == expected


def test_default_table_configuration():
    """Test that TableConfiguration defaults are applied"""
    config = TableConfiguration()
    
    assert config.scd_type == "SCD_TYPE_1"
    assert config.primary_keys is None
    assert config.filter_formula is None
    assert config.batch_size == 100


# ==============================================================================
# SCD Type Tests
# ==============================================================================

def test_scd_type_enum():
    """Test SCD type validation"""
    config = TableConfiguration(scd_type=SCDType.SCD_TYPE_2)
    assert config.scd_type == "SCD_TYPE_2"
    
    config2 = TableConfiguration(scd_type="APPEND_ONLY")
    assert config2.scd_type == "APPEND_ONLY"


def test_invalid_scd_type():
    """Test that invalid SCD type is rejected"""
    with pytest.raises(ValidationError, match="Input should be"):
        TableConfiguration(scd_type="INVALID_TYPE")


# ==============================================================================
# Batch Size Tests
# ==============================================================================

def test_batch_size_limits():
    """Test batch_size range validation"""
    # Valid
    config = TableConfiguration(batch_size=50)
    assert config.batch_size == 50
    
    # Too small
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        TableConfiguration(batch_size=0)
    
    # Too large
    with pytest.raises(ValidationError, match="less than or equal to 100"):
        TableConfiguration(batch_size=101)


# ==============================================================================
# Extra Fields Tests
# ==============================================================================

def test_extra_fields_rejected():
    """Test that unknown fields are rejected"""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))],
            unknown_field="should fail"  # Extra field
        )


def test_table_config_extra_fields():
    """Test that extra fields in TableConfig are rejected"""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TableConfig(
            source_table="Test",
            invalid_option="value"
        )


# ==============================================================================
# Helper Function Tests
# ==============================================================================

def test_get_full_table_name():
    """Test get_full_table_name helper"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appTest",
        default_catalog="my_catalog",
        default_schema="my_schema",
        objects=[
            TableSpec(table=TableConfig(
                source_table="Test Table",
                destination_table="test_table"
            ))
        ]
    )
    
    full_name = spec.get_full_table_name(spec.objects[0].table)
    assert full_name == "my_catalog.my_schema.test_table"


def test_get_full_table_name_with_overrides():
    """Test get_full_table_name with catalog/schema overrides"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appTest",
        default_catalog="default_cat",
        default_schema="default_schema",
        objects=[
            TableSpec(table=TableConfig(
                source_table="Test",
                destination_catalog="custom_cat",
                destination_schema="custom_schema",
                destination_table="test_table"
            ))
        ]
    )
    
    full_name = spec.get_full_table_name(spec.objects[0].table)
    assert full_name == "custom_cat.custom_schema.test_table"


def test_load_pipeline_spec_from_dict():
    """Test loading spec from dictionary"""
    data = {
        "token": "patk" + "x" * 20,
        "base_id": "appTest123",
        "default_catalog": "my_catalog",
        "default_schema": "my_schema",
        "objects": [
            {"table": {"source_table": "Customers"}}
        ]
    }
    
    spec = load_pipeline_spec_from_dict(data)
    
    assert isinstance(spec, AirtablePipelineSpec)
    assert spec.default_catalog == "my_catalog"
    assert len(spec.objects) == 1


def test_load_pipeline_spec_from_dict_invalid():
    """Test that loading invalid dict raises ValidationError"""
    data = {
        "token": "patk" + "x" * 20,
        # Missing required fields
        "objects": []
    }
    
    with pytest.raises(ValidationError):
        load_pipeline_spec_from_dict(data)


# ==============================================================================
# Complex Configuration Tests
# ==============================================================================

def test_complex_pipeline_spec():
    """Test a realistic, complex pipeline spec"""
    spec = AirtablePipelineSpec(
        token="patk" + "x" * 20,
        base_id="appSaRcgA5UCGoRg5",
        default_catalog="kaustavpaul_demo",
        default_schema="airtable_connector",
        objects=[
            TableSpec(table=TableConfig(
                source_table="Launch Milestones",
                destination_table="launch_milestones",
                table_configuration=TableConfiguration(
                    scd_type=SCDType.APPEND_ONLY,
                    batch_size=50
                )
            )),
            TableSpec(table=TableConfig(
                source_table="Vendors",
                destination_table="vendors",
                table_configuration=TableConfiguration(
                    scd_type=SCDType.SCD_TYPE_1,
                    primary_keys=["id"],
                    filter_formula="{Status} = 'Active'"
                )
            )),
            TableSpec(table=TableConfig(
                source_table="Compliance Records",
                destination_catalog="kaustavpaul_demo",
                destination_schema="compliance",
                destination_table="records",
                table_configuration=TableConfiguration(
                    scd_type=SCDType.SCD_TYPE_2
                )
            )),
        ]
    )
    
    assert len(spec.objects) == 3
    
    # Verify first table
    assert spec.objects[0].table.source_table == "Launch Milestones"
    assert spec.objects[0].table.table_configuration.scd_type == "APPEND_ONLY"
    
    # Verify second table
    assert spec.objects[1].table.table_configuration.filter_formula == "{Status} = 'Active'"
    
    # Verify third table with overrides
    full_name = spec.get_full_table_name(spec.objects[2].table)
    assert full_name == "kaustavpaul_demo.compliance.records"


# ==============================================================================
# Error Message Tests
# ==============================================================================

def test_helpful_error_messages():
    """Test that validation errors provide helpful messages"""
    try:
        AirtablePipelineSpec(
            # Missing token and connection_name
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[TableSpec(table=TableConfig(source_table="T"))]
        )
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        error_msg = str(e)
        assert "Must provide either" in error_msg
        assert "token" in error_msg or "connection_name" in error_msg


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

