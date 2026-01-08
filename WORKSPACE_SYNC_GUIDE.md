# 🔄 Workspace Sync Guide

This guide helps you keep your local codebase and Databricks workspace in sync after cleanup.

---

## 📊 Current State

### Local Codebase (Clean): ✅
- 21 essential files
- Organized structure  
- Production-ready
- Well-documented

### Workspace Status: ⚠️
- May contain old experimental files
- Needs cleanup to match local
- Should sync essential files only

---

## 🎯 Sync Strategy

Since you'll be using the **official Databricks UI or CLI tools** to deploy the connector, you don't need to manually sync files to the workspace. The tools will handle this automatically.

### Recommended Approach:

**DON'T manually upload files to workspace**  
**DO use the official deployment method:**
1. Databricks UI → "+New" → "Add or upload data" → "Community connectors"
2. Or use CLI tool from `tools/community_connector`

The tools will:
- ✅ Upload only necessary files
- ✅ Generate proper structure
- ✅ Create entry points automatically
- ✅ Follow framework rules

---

## 🧹 Workspace Cleanup (If Needed)

If you have old files in your workspace that you want to clean up:

### Files to Remove from Workspace:

```bash
# Navigate to your workspace directory
# /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/

# Remove these experimental/old files if they exist:
sdp_ingest/airtable_sdp_correct.py
sdp_ingest/airtable_sdp_repos.py
setup.py
deploy.sh
deploy_staging.sh  
upload_to_repos.sh
_app.yaml
configs/dev_config.json
pipeline-spec/airtable_pipeline.yaml
sources/airtable/_generated_airtable_python_source.py
```

### Via Databricks UI:
1. Go to Workspace
2. Navigate to connector directory
3. Select files/folders to delete
4. Click "Move to trash"

### Via Databricks CLI:
```bash
# List files
databricks workspace ls /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/

# Remove file
databricks workspace rm /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py

# Remove directory
databricks workspace rm -r /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/
```

---

## ✅ Essential Files to Keep in Workspace

These files should be in your workspace (but the official tools will handle this):

### Core Implementation:
```
sources/
├── airtable/
│   ├── __init__.py
│   ├── airtable.py
│   └── README.md
└── interface/
    ├── __init__.py
    └── lakeflow_connect.py
```

### Pipeline Spec:
```
pipeline-spec/
├── __init__.py
└── airtable_spec.py
```

### Framework Files:
```
pipeline/
├── __init__.py
├── ingestion_pipeline.py
└── lakeflow_python_source.py

libs/
└── common/
    ├── __init__.py
    └── source_loader.py
```

### Tests (Optional in workspace):
```
tests/
├── __init__.py
├── conftest.py
├── test_airtable_connector.py
├── test_pipeline_spec.py
└── test_pydantic_integration.py
```

---

## 🚀 Deployment Workflow

### Step 1: Clean Local Codebase
✅ **Done!** Your local codebase is clean and organized.

### Step 2: Choose Deployment Method

**Option A: Databricks UI (Recommended)**
1. Go to Databricks workspace
2. Click "+New" → "Add or upload data"
3. Select "Community connectors"  
4. Click "+ Add Community Connector"
5. Point to your Git repository or upload files
6. UI will handle workspace deployment automatically

**Option B: CLI Tool**
1. Clone official repo: `git clone https://github.com/databrickslabs/lakeflow-community-connectors.git`
2. Navigate to: `cd lakeflow-community-connectors/tools/community_connector`
3. Use CLI to create connector
4. CLI will handle workspace deployment automatically

### Step 3: Verify Deployment
- Check that connector appears in workspace
- Verify files are properly structured
- Run tests if needed

---

## 📝 Git Integration (Optional)

If you want to use Git for version control and sync:

### 1. Initialize Git Repository (If Not Already)
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
git init
git add .
git commit -m "Clean codebase: Production-ready Airtable connector"
```

### 2. Push to Remote Repository
```bash
# Add remote (GitHub, GitLab, etc.)
git remote add origin <your-repo-url>
git push -u origin main
```

### 3. Link Databricks Repos
1. In Databricks, go to "Repos"
2. Click "Add Repo"
3. Enter your Git URL
4. Clone into workspace

Now changes sync automatically via Git!

---

## 🔄 Ongoing Sync Strategy

### For Development:

**Local Development:**
1. Make changes locally
2. Test locally with pytest
3. Commit to Git
4. Push to remote

**Databricks Deployment:**
1. Databricks Repos syncs from Git automatically
2. Or use UI/CLI to update connector
3. Run DLT pipeline to test

### For Production:

**Use the official tools exclusively:**
- No manual file management
- No custom uploads
- Let framework handle everything

---

## ⚠️ Important Notes

1. **Don't manually sync files to workspace** - Use official tools
2. **Workspace is managed by framework** - Don't edit files directly
3. **Local codebase is source of truth** - Keep it clean
4. **Git is optional but recommended** - For version control
5. **Official tools handle deployment** - They know best practices

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Only essential files in workspace
- [ ] No experimental files remaining
- [ ] Proper directory structure
- [ ] Framework files intact
- [ ] Connector code accessible
- [ ] Tests passing (if applicable)
- [ ] Documentation available

---

## 🆘 Troubleshooting

**Issue:** Old files still in workspace  
**Solution:** Use Databricks UI or CLI to remove them

**Issue:** Connector not found after deployment  
**Solution:** Verify file paths match framework expectations

**Issue:** Import errors  
**Solution:** Ensure all `__init__.py` files are present

**Issue:** Sync conflicts  
**Solution:** Official tools regenerate structure - let them

---

## 📞 Next Steps

1. ✅ Local cleanup complete
2. ⏳ Choose deployment method (UI or CLI)
3. ⏳ Deploy using official tools
4. ⏳ Verify workspace sync
5. ⏳ Test connector in DLT pipeline

See **[OFFICIAL_APPROACH_GUIDE.md](./OFFICIAL_APPROACH_GUIDE.md)** for detailed deployment instructions!

---

**Remember:** The official UI/CLI tools are designed to handle workspace sync automatically. Trust the framework! 🚀

