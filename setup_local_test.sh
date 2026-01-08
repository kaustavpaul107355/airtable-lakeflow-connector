#!/bin/bash
# Local Testing Setup Script for Airtable Lakeflow Connector

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧪 AIRTABLE LAKEFLOW CONNECTOR - LOCAL TESTING SETUP"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if we're in the correct directory
if [ ! -f "sources/airtable/airtable.py" ]; then
    echo "✗ Error: Please run this script from the airtable-connector directory"
    exit 1
fi

echo "Step 1: Setting up Python virtual environment..."
echo "───────────────────────────────────────────────────────────────────────────────"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created virtual environment"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Activated virtual environment"

echo ""
echo "Step 2: Installing dependencies..."
echo "───────────────────────────────────────────────────────────────────────────────"

# Upgrade pip
pip install --upgrade pip --quiet

# Install requirements
pip install -r requirements.txt --quiet
echo "✓ Installed requirements.txt"

# Install python-dotenv for .credentials file
pip install python-dotenv --quiet
echo "✓ Installed python-dotenv"

echo ""
echo "Step 3: Setting up credentials..."
echo "───────────────────────────────────────────────────────────────────────────────"

# Check if .credentials exists
if [ ! -f ".credentials" ]; then
    if [ -f ".credentials.example" ]; then
        cp .credentials.example .credentials
        echo "✓ Created .credentials from .credentials.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .credentials file with your actual values:"
        echo "   AIRTABLE_TOKEN=your_actual_token"
        echo "   AIRTABLE_BASE_ID=your_actual_base_id"
        echo ""
        echo "   Then run: python ingest.py"
        exit 0
    else
        echo "✗ .credentials.example not found"
        exit 1
    fi
else
    echo "✓ .credentials file exists"
    
    # Check if credentials are filled in
    if grep -q "YOUR_AIRTABLE" .credentials; then
        echo ""
        echo "⚠️  WARNING: .credentials still has placeholder values!"
        echo "   Edit .credentials with your actual token and base_id"
        echo ""
        exit 1
    fi
fi

echo ""
echo "Step 4: Verifying setup..."
echo "───────────────────────────────────────────────────────────────────────────────"

# Check for required files
REQUIRED_FILES=(
    "sources/airtable/airtable.py"
    "pipeline-spec/airtable_spec.py"
    "pipeline/ingestion_pipeline.py"
    "libs/common/source_loader.py"
    "ingest.py"
    ".credentials"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ Missing: $file"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo ""
    echo "✗ Some required files are missing"
    exit 1
fi

# Check __init__.py files
echo ""
echo "Checking __init__.py files..."
INIT_DIRS=(
    "sources"
    "sources/airtable"
    "sources/interface"
    "pipeline-spec"
    "pipeline"
    "libs"
    "libs/common"
    "tests"
)

for dir in "${INIT_DIRS[@]}"; do
    if [ -f "$dir/__init__.py" ]; then
        echo "✓ $dir/__init__.py"
    else
        echo "✗ Missing: $dir/__init__.py"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo ""
    echo "✗ Some __init__.py files are missing"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Edit ingest.py to configure your table names (line 95-125)"
echo "  2. Run the local test:"
echo ""
echo "     python ingest.py"
echo ""
echo "  3. Verify all tests pass"
echo "  4. Share results with your Databricks expert"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"

