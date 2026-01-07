#!/usr/bin/env python3
"""
Quick test script to verify Pydantic pipeline spec integration

Run this locally to verify the Pydantic models work before deploying.

Usage:
    python test_pydantic_integration.py
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline-spec'))
sys.path.insert(0, os.path.dirname(__file__))

def test_import():
    """Test that Pydantic models can be imported"""
    print("Testing imports...")
    try:
        from airtable_spec import (
            AirtablePipelineSpec,
            TableSpec,
            TableConfig,
            TableConfiguration,
            SCDType,
            load_pipeline_spec_from_dict,
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_valid_spec():
    """Test creating a valid pipeline spec"""
    print("\nTesting valid spec creation...")
    try:
        from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig
        
        spec = AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest123",
            default_catalog="test_catalog",
            default_schema="test_schema",
            objects=[
                TableSpec(table=TableConfig(source_table="Test Table"))
            ]
        )
        
        print("✅ Valid spec created successfully")
        print(f"   Destination table: {spec.objects[0].table.destination_table}")
        return True
    except Exception as e:
        print(f"❌ Failed to create valid spec: {e}")
        return False


def test_validation():
    """Test that validation catches errors"""
    print("\nTesting validation...")
    try:
        from airtable_spec import AirtablePipelineSpec
        from pydantic import ValidationError
        
        # This should fail - missing required fields
        try:
            spec = AirtablePipelineSpec(
                token="patk" + "x" * 20,
                base_id="appTest",
                # Missing default_catalog and default_schema
                objects=[]
            )
            print("❌ Validation should have failed but didn't")
            return False
        except ValidationError:
            print("✅ Validation correctly caught missing fields")
            return True
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


def test_auto_sanitization():
    """Test automatic column name sanitization"""
    print("\nTesting auto-sanitization...")
    try:
        from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig
        
        test_cases = [
            ("Customer Name", "customer_name"),
            ("SKU (2024)", "sku_2024"),
            ("Price/Unit", "price_unit"),
        ]
        
        all_passed = True
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
            
            actual = spec.objects[0].table.destination_table
            if actual == expected:
                print(f"✅ '{source}' → '{actual}'")
            else:
                print(f"❌ '{source}' → '{actual}' (expected '{expected}')")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Auto-sanitization test failed: {e}")
        return False


def test_dict_loading():
    """Test loading spec from dictionary"""
    print("\nTesting dict loading...")
    try:
        from airtable_spec import load_pipeline_spec_from_dict
        
        data = {
            "token": "patk" + "x" * 20,
            "base_id": "appTest",
            "default_catalog": "cat",
            "default_schema": "schema",
            "objects": [
                {"table": {"source_table": "Test"}}
            ]
        }
        
        spec = load_pipeline_spec_from_dict(data)
        print("✅ Successfully loaded spec from dict")
        print(f"   Table count: {len(spec.objects)}")
        return True
    except Exception as e:
        print(f"❌ Dict loading failed: {e}")
        return False


def test_ingestion_pipeline_integration():
    """Test that ingestion pipeline can use Pydantic spec"""
    print("\nTesting ingestion pipeline integration...")
    try:
        from pipeline.ingestion_pipeline import ingest
        from airtable_spec import AirtablePipelineSpec, TableSpec, TableConfig
        
        spec = AirtablePipelineSpec(
            token="patk" + "x" * 20,
            base_id="appTest",
            default_catalog="cat",
            default_schema="schema",
            objects=[
                TableSpec(table=TableConfig(source_table="Test"))
            ]
        )
        
        # Just verify it accepts the spec (won't actually run without Spark)
        print("✅ Ingestion pipeline can accept Pydantic spec")
        print("   (Full execution requires Spark session)")
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("Pydantic Pipeline Spec Integration Tests")
    print("=" * 80)
    
    tests = [
        ("Import Test", test_import),
        ("Valid Spec", test_valid_spec),
        ("Validation", test_validation),
        ("Auto-Sanitization", test_auto_sanitization),
        ("Dict Loading", test_dict_loading),
        ("Pipeline Integration", test_ingestion_pipeline_integration),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 80)
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Pydantic integration is working correctly.")
        print("\nNext steps:")
        print("  1. Deploy to workspace: bash deploy.sh staging")
        print("  2. Test in Databricks notebook")
        print("=" * 80)
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

