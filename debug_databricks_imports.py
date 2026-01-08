# Databricks notebook source
# MAGIC %md
# MAGIC # 🔍 Debug Airtable Connector Import Issues
# MAGIC 
# MAGIC Run this notebook to diagnose why `libs.source_loader` can't be found.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Check Current Python Path

# COMMAND ----------

import sys
import os

print("=" * 80)
print("PYTHON PATH")
print("=" * 80)
for i, path in enumerate(sys.path, 1):
    print(f"{i}. {path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Verify Workspace Files Exist

# COMMAND ----------

workspace_path = "/Workspace/Users/kaustav.paul@databricks.com/airtable-connect-sdp/airtable-connect-sdp"

print("=" * 80)
print(f"CHECKING: {workspace_path}")
print("=" * 80)

required_files = [
    "ingest.py",
    "libs/__init__.py",
    "libs/common/__init__.py",
    "libs/common/source_loader.py",
    "pipeline/__init__.py",
    "pipeline/ingestion_pipeline.py",
    "pipeline/lakeflow_python_source.py",
    "pipeline-spec/__init__.py",
    "pipeline-spec/airtable_spec.py",
    "sources/__init__.py",
    "sources/airtable/__init__.py",
    "sources/airtable/airtable.py",
    "sources/interface/__init__.py",
    "sources/interface/lakeflow_connect.py"
]

missing_files = []
for file in required_files:
    full_path = os.path.join(workspace_path, file)
    exists = os.path.exists(full_path)
    status = "✓" if exists else "✗"
    print(f"{status} {file}")
    if not exists:
        missing_files.append(file)

if missing_files:
    print("\n" + "=" * 80)
    print("⚠️  MISSING FILES")
    print("=" * 80)
    for file in missing_files:
        print(f"  ✗ {file}")
else:
    print("\n✅ All required files exist!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Try Adding Path and Importing

# COMMAND ----------

# Add workspace path to sys.path
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)
    print(f"✓ Added to sys.path: {workspace_path}")
else:
    print(f"✓ Already in sys.path: {workspace_path}")

print("\n" + "=" * 80)
print("TESTING IMPORTS")
print("=" * 80)

# Test imports
imports_to_test = [
    ("libs.source_loader", "get_register_function"),
    ("pipeline.ingestion_pipeline", "ingest"),
    ("sources.airtable.airtable", "AirtableLakeflowConnector"),
    ("pipeline_spec.airtable_spec", "AirtablePipelineSpec"),
]

successful_imports = []
failed_imports = []

for module_name, attr_name in imports_to_test:
    try:
        module = __import__(module_name, fromlist=[attr_name])
        attr = getattr(module, attr_name)
        print(f"✓ Successfully imported: {module_name}.{attr_name}")
        successful_imports.append(module_name)
    except Exception as e:
        print(f"✗ Failed to import {module_name}: {e}")
        failed_imports.append((module_name, str(e)))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Display Directory Structure

# COMMAND ----------

def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """Print directory structure"""
    if current_depth >= max_depth:
        return
    
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
        return
    except FileNotFoundError:
        print(f"{prefix}[Not Found]")
        return
    
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        
        if os.path.isdir(full_path):
            print(f"{prefix}{connector}{entry}/")
            extension = "    " if is_last else "│   "
            print_directory_tree(full_path, prefix + extension, max_depth, current_depth + 1)
        else:
            print(f"{prefix}{connector}{entry}")

print("=" * 80)
print("DIRECTORY STRUCTURE")
print("=" * 80)
print(f"{workspace_path}/")
print_directory_tree(workspace_path, max_depth=3)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Diagnostic Summary

# COMMAND ----------

print("=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

print(f"\n📁 Workspace Path: {workspace_path}")
print(f"   Exists: {'✓ Yes' if os.path.exists(workspace_path) else '✗ No'}")

print(f"\n📦 Required Files:")
print(f"   Total: {len(required_files)}")
print(f"   Present: {len(required_files) - len(missing_files)}")
print(f"   Missing: {len(missing_files)}")

print(f"\n🔧 Import Tests:")
print(f"   Successful: {len(successful_imports)}")
print(f"   Failed: {len(failed_imports)}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if missing_files:
    print("\n⚠️  ACTION REQUIRED: Missing Files")
    print("   You need to upload these files to your workspace:")
    for file in missing_files:
        print(f"   - {file}")
    print("\n   Use Databricks CLI:")
    print("   databricks workspace import-dir <local-path> <workspace-path>")

elif failed_imports:
    print("\n⚠️  ACTION REQUIRED: Import Failures")
    print("   Files exist but imports fail. Possible causes:")
    print("   1. Files uploaded as notebooks instead of Python files")
    print("   2. Missing or incorrect __init__.py files")
    print("   3. Syntax errors in Python files")
    print("\n   Check each failed import:")
    for module, error in failed_imports:
        print(f"   - {module}: {error}")

else:
    print("\n✅ ALL CHECKS PASSED!")
    print("   Your connector files are properly uploaded and importable.")
    print("\n   Next steps:")
    print("   1. Check your ingest.py file has proper sys.path setup")
    print("   2. Or better: Use official Lakeflow UI/CLI tools instead!")

print("\n" + "=" * 80)
print("EXPERT ADVICE")
print("=" * 80)
print("""
Based on expert guidance, you should NOT be doing manual deployment!

Instead:
1. Use Databricks Lakeflow UI:
   Workspace → +New → Add or upload data → Community connectors

2. Or use Lakeflow CLI tool:
   Clone: https://github.com/databrickslabs/lakeflow-community-connectors
   Navigate to: tools/community_connector
   Follow CLI documentation

3. Or ask your Databricks expert for the correct deployment method

Your connector code is correct (on GitHub):
https://github.com/kaustavpaul107355/airtable-lakeflow-connector

The issue is just the deployment method!
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: Quick Fix (Temporary)
# MAGIC 
# MAGIC If you must continue with manual approach, add this to the top of your `ingest.py`:

# COMMAND ----------

print("=" * 80)
print("TEMPORARY FIX FOR ingest.py")
print("=" * 80)

fix_code = '''
# Add at the TOP of your ingest.py file:

import sys
import os

# Get the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add to Python path if not already there
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"Added to sys.path: {current_dir}")

# Now your imports should work:
from pipeline.ingestion_pipeline import ingest
from libs.source_loader import get_register_function
'''

print(fix_code)

print("\n" + "=" * 80)
print("⚠️  WARNING: This is a WORKAROUND, not the solution!")
print("=" * 80)
print("The official Lakeflow tools handle all this automatically.")
print("Ask your expert for the proper deployment method.")

