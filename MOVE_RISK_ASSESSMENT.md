# Risk Assessment: Moving airtable-connector Directory

**Date:** January 7, 2026  
**Requested Action:** Move airtable-connector from nested location to root level

## 📍 Move Details

**From:** `/Users/kaustav.paul/CursorProjects/Databricks/airtable-connector`  
**To:** `/Users/kaustav.paul/CursorProjects/Databricks/airtable-connector`

## ✅ Risk Assessment Results

### OVERALL RISK LEVEL: **🟢 LOW - SAFE TO MOVE**

---

## Detailed Assessment

### 1. Git Repository Status ✅ **SAFE**

- **Finding:** airtable-connector is a **standalone git repository**
- **Remote:** `https://github.com/kaustavpaul107355/airtable-lakeflow-connector.git`
- **Current branch:** `main`
- **Latest commit:** `695c101` (Local testing framework)
- **Uncommitted changes:** 0
- **Parent repo:** None (databricks-starter has no .git)

**Risk:** ✅ **NONE** - Standalone repo will move intact with its .git directory

---

### 2. Path Dependencies ⚠️ **REQUIRES UPDATE**

**Finding:** Documentation files contain hardcoded paths:

```
./DATABRICKS_DEPLOYMENT_FIX.md
./WORKSPACE_SYNC_GUIDE.md
./COMPLETE_VERIFICATION_CHECKLIST.md (2 instances)
./GITHUB_SETUP.md
./LOCAL_TESTING_GUIDE.md (2 instances)
```

**Example:**
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
```

**Risk:** ⚠️ **MINOR** - Only affects documentation, not code functionality
**Mitigation:** Automated find-and-replace after move

---

### 3. Python Code Dependencies ✅ **SAFE**

- **Imports:** All use relative imports (no absolute paths)
- **sys.path:** No references to parent directory structure
- **Package structure:** Self-contained (sources/, pipeline/, libs/)

**Risk:** ✅ **NONE** - Python code is location-agnostic

---

### 4. External References ✅ **SAFE**

- **Finding:** No other projects reference airtable-connector
- **Checked:** All Python, Markdown, YAML, JSON files in databricks-starter/

**Risk:** ✅ **NONE** - No external dependencies

---

### 5. Virtual Environment ⚠️ **REQUIRES RECREATION**

- **Finding:** venv directory exists (created for local testing)
- **Issue:** Python virtual environments contain absolute paths

**Risk:** ⚠️ **MINOR** - venv will break, but easy to recreate
**Mitigation:** Delete venv after move, run `./setup_local_test.sh` to recreate

---

### 6. Destination Status ✅ **SAFE**

- **Finding:** Destination path does not exist
- **No conflicts:** Nothing will be overwritten

**Risk:** ✅ **NONE** - Clean destination

---

### 7. Symlinks/Hard Links ✅ **SAFE**

- **Finding:** No symbolic links or hard links found

**Risk:** ✅ **NONE** - No link breakage concerns

---

### 8. GitHub Remote ✅ **SAFE**

- **Finding:** GitHub remote URL is not path-dependent
- **Current:** `https://github.com/kaustavpaul107355/airtable-lakeflow-connector.git`

**Risk:** ✅ **NONE** - Git push/pull will work from new location

---

## 🎯 Pre-Move Checklist

- [x] Git repository status clean (no uncommitted changes)
- [x] Standalone git repo (not submodule)
- [x] No parent git tracking
- [x] No external project dependencies
- [x] Destination path available
- [x] GitHub remote configured
- [x] Latest changes pushed to GitHub

## 🔧 Post-Move Required Actions

### 1. Update Documentation Paths (6 files)

Files requiring path updates:
- `DATABRICKS_DEPLOYMENT_FIX.md`
- `WORKSPACE_SYNC_GUIDE.md`
- `COMPLETE_VERIFICATION_CHECKLIST.md` (2 instances)
- `GITHUB_SETUP.md`
- `LOCAL_TESTING_GUIDE.md` (2 instances)

**Automated Fix:**
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector

# Find and replace old path with new path
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" \) \
  -not -path "*/venv/*" -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -exec sed -i '' 's|/airtable-connector|/airtable-connector|g' {} \;
```

### 2. Recreate Virtual Environment

```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
rm -rf venv
./setup_local_test.sh
```

### 3. Verify Git Status

```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
git status
git remote -v
```

### 4. Test Functionality

```bash
# Run local tests to verify everything works
python ingest.py
```

### 5. Commit Path Updates

```bash
git add .
git commit -m "chore: Update documentation paths after directory move"
git push origin main
```

## 📋 Move Procedure

### Step 1: Perform the Move
```bash
mv /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector \
   /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
```

### Step 2: Update Documentation Paths
```bash
cd /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector
find . -type f \( -name "*.md" -o -name "*.sh" \) \
  -not -path "*/venv/*" -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -exec sed -i '' 's|/airtable-connector|/airtable-connector|g' {} \;
```

### Step 3: Recreate Virtual Environment
```bash
rm -rf venv
./setup_local_test.sh
```

### Step 4: Verify & Test
```bash
git status
python ingest.py  # Run tests
```

### Step 5: Commit & Push
```bash
git add .
git commit -m "chore: Update documentation paths after directory move

Moved directory from:
  databricks-starter/databricks-apps/airtable-connector
To:
  /Users/kaustav.paul/CursorProjects/Databricks/airtable-connector

Updated all documentation references to reflect new location."
git push origin main
```

## 🎯 Benefits of Moving

1. **Cleaner Structure:** Top-level location for a standalone project
2. **Shorter Paths:** Easier to navigate and reference
3. **Independence:** Clear separation from databricks-starter workspace
4. **Professionalism:** Matches typical project organization

## ⚠️ Potential Issues & Solutions

| Issue | Likelihood | Solution |
|-------|------------|----------|
| Documentation paths outdated | **High** | Automated find-replace (provided) |
| venv breaks | **Certain** | Recreate with setup script |
| Git remote issues | **Very Low** | Remote URL is not path-dependent |
| Python imports break | **Very Low** | All imports are relative |
| GitHub sync issues | **Very Low** | .git moves with directory |

## ✅ Final Recommendation

**PROCEED WITH MOVE - SAFE OPERATION**

The move is **low risk** and **straightforward**. The main considerations are:
1. Update documentation paths (automated script provided)
2. Recreate virtual environment (one command)
3. Commit the path updates to git

All critical components (git repo, Python code, GitHub remote) will work seamlessly after the move.

---

**Assessment Completed:** 2026-01-07  
**Assessor:** Comprehensive automated analysis  
**Confidence Level:** High

