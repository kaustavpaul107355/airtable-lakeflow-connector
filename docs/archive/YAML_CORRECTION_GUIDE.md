# 🔧 YAML Correction Guide - Line by Line

## 📋 Your Current YAML → Corrected YAML

Below is a **field-by-field comparison** showing exactly what to change.

---

## ❌ CURRENT YAML (What You Have)

```yaml
id: e89fc3e0-42e4-478e-a1e0-742b91105052
pipeline_type: WORKSPACE
name: airtable
libraries:
  - glob:
      include: /Workspace/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/**
schema: default
continuous: false
development: false
photon: true
channel: CURRENT
catalog: main
serverless: true
root_path: /Workspace/Users/kaustav.paul@databricks.com/lakeflow-community-connectors
```

---

## ✅ CORRECTED YAML (What You Need)

```yaml
name: Airtable Lakeflow Connector
pipeline_type: WORKSPACE
libraries:
  - notebook:
      path: /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
catalog: kaustavpaul_demo
target: airtable_connector
continuous: false
development: true
photon: true
channel: CURRENT
serverless: true
```

---

## 🔍 FIELD-BY-FIELD CHANGES

### Field 1: `id` ❌ REMOVE
```yaml
# CURRENT (WRONG):
id: e89fc3e0-42e4-478e-a1e0-742b91105052

# CORRECTED:
# (Remove this line - it's auto-generated)
```
**Action:** Delete this entire line

---

### Field 2: `name` ✏️ CHANGE
```yaml
# CURRENT:
name: airtable

# CORRECTED:
name: Airtable Lakeflow Connector
```
**Action:** Change to more descriptive name (optional but recommended)

---

### Field 3: `pipeline_type` ✅ KEEP
```yaml
# CURRENT (CORRECT):
pipeline_type: WORKSPACE
```
**Action:** No change needed

---

### Field 4: `libraries` 🔴 MAJOR CHANGE
```yaml
# CURRENT (WRONG):
libraries:
  - glob:
      include: /Workspace/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/**

# CORRECTED:
libraries:
  - notebook:
      path: /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
```

**Changes:**
1. `glob` → `notebook`
2. `include` → `path`
3. Remove `/Workspace` prefix
4. Change `**` wildcard to specific file: `airtable_sdp_correct.py`

**Action:** 
- Change library type from "Glob" to "Notebook"
- Use exact file path (not pattern)

---

### Field 5: `catalog` 🔴 CHANGE
```yaml
# CURRENT (WRONG):
catalog: main

# CORRECTED:
catalog: kaustavpaul_demo
```
**Action:** Change from `main` to `kaustavpaul_demo`

---

### Field 6: `schema` / `target` 🔴 CHANGE
```yaml
# CURRENT (WRONG):
schema: default

# CORRECTED:
target: airtable_connector
```
**Action:** 
- Change field name from `schema` to `target`
- Change value from `default` to `airtable_connector`

---

### Field 7: `continuous` ✅ KEEP
```yaml
# CURRENT (CORRECT):
continuous: false
```
**Action:** No change needed

---

### Field 8: `development` 🔴 CHANGE
```yaml
# CURRENT (WRONG):
development: false

# CORRECTED:
development: true
```
**Action:** Change from `false` to `true`

---

### Field 9: `photon` ✅ KEEP
```yaml
# CURRENT (CORRECT):
photon: true
```
**Action:** No change needed

---

### Field 10: `channel` ✅ KEEP
```yaml
# CURRENT (CORRECT):
channel: CURRENT
```
**Action:** No change needed

---

### Field 11: `serverless` ✅ KEEP
```yaml
# CURRENT (CORRECT):
serverless: true
```
**Action:** No change needed

---

### Field 12: `root_path` ❌ REMOVE
```yaml
# CURRENT (WRONG):
root_path: /Workspace/Users/kaustav.paul@databricks.com/lakeflow-community-connectors

# CORRECTED:
# (Remove this line - not needed)
```
**Action:** Delete this entire line

---

## 📊 SUMMARY OF CHANGES

| Field | Current | Corrected | Action |
|-------|---------|-----------|--------|
| `id` | `e89fc3e0-...` | *(remove)* | DELETE |
| `name` | `airtable` | `Airtable Lakeflow Connector` | CHANGE |
| `pipeline_type` | `WORKSPACE` | `WORKSPACE` | KEEP |
| `libraries` | `glob` + `/Workspace/.../**` | `notebook` + `/Users/.../airtable_sdp_correct.py` | MAJOR CHANGE |
| `catalog` | `main` | `kaustavpaul_demo` | CHANGE |
| `schema` | `default` | *(remove field)* | DELETE |
| `target` | *(missing)* | `airtable_connector` | ADD |
| `continuous` | `false` | `false` | KEEP |
| `development` | `false` | `true` | CHANGE |
| `photon` | `true` | `true` | KEEP |
| `channel` | `CURRENT` | `CURRENT` | KEEP |
| `serverless` | `true` | `true` | KEEP |
| `root_path` | `/Workspace/...` | *(remove)* | DELETE |

**Total Changes:** 7 fields need modification

---

## 🎯 QUICK REFERENCE - CORRECTED YAML

Copy this entire block:

```yaml
name: Airtable Lakeflow Connector
pipeline_type: WORKSPACE
libraries:
  - notebook:
      path: /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
catalog: kaustavpaul_demo
target: airtable_connector
continuous: false
development: true
photon: true
channel: CURRENT
serverless: true
```

---

## 🖥️ HOW TO APPLY IN UI

Since you're editing YAML in the UI, here's how to make each change:

### Option 1: Edit YAML Directly (If Available)
1. Look for "Edit as YAML" or "YAML" tab
2. Select all current YAML
3. Delete it
4. Paste the corrected YAML above
5. Click "Save"

### Option 2: Edit Fields in UI Form
If your UI shows form fields instead of raw YAML:

#### Step 1: Library Configuration
- **Find:** "Notebook libraries" or "Paths" section
- **Current:** Shows "Glob" with `/Workspace/Users/.../sdp_ingest/**`
- **Actions:**
  1. Click edit/delete on the glob entry
  2. Add new entry of type "Notebook"
  3. Enter path: `/Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py`
  4. ⚠️ Critical: Remove `/Workspace` prefix!

#### Step 2: Catalog
- **Find:** "Catalog" field
- **Change from:** `main`
- **Change to:** `kaustavpaul_demo`

#### Step 3: Target Schema
- **Find:** "Target" or "Schema" field
- **Change from:** `default`
- **Change to:** `airtable_connector`
- **Note:** Field name should be "Target" not "Schema"

#### Step 4: Development Mode
- **Find:** "Development" checkbox or toggle
- **Change from:** `false` (unchecked)
- **Change to:** `true` (checked)

#### Step 5: Advanced Settings
- **Find:** "Advanced" or "More options" section
- **Find:** "Root path" field
- **Action:** Clear/delete the value (leave empty)

#### Step 6: Remove ID (If Visible)
- **Find:** "Pipeline ID" field
- **Action:** If editable, clear it (usually not editable, that's OK)

#### Step 7: Verify
- **Check that Configuration section is EMPTY** (no key-value pairs)
- No entries for credentials or connection details

---

## ✅ FINAL CHECKLIST

Before clicking "Save" and "Start", verify:

- [ ] Library type is "Notebook" (not "Glob")
- [ ] Path is `/Users/kaustav.paul@databricks.com/.../airtable_sdp_correct.py`
- [ ] Path does NOT start with `/Workspace`
- [ ] Catalog is `kaustavpaul_demo`
- [ ] Target is `airtable_connector`
- [ ] Development is `true`
- [ ] Root path is empty/removed
- [ ] Configuration section is empty
- [ ] No credential entries anywhere

---

## 🚨 MOST CRITICAL CHANGES

If you can only focus on a few, these are MUST-HAVES:

### 1. Library Path (Most Critical) 🔴
**WRONG:**
```yaml
libraries:
  - glob:
      include: /Workspace/Users/.../sdp_ingest/**
```

**CORRECT:**
```yaml
libraries:
  - notebook:
      path: /Users/kaustav.paul@databricks.com/lakeflow-community-connectors/sources/airtable-connector/sdp_ingest/airtable_sdp_correct.py
```

### 2. Catalog & Target 🔴
**WRONG:**
```yaml
catalog: main
schema: default
```

**CORRECT:**
```yaml
catalog: kaustavpaul_demo
target: airtable_connector
```

### 3. Remove Root Path 🔴
**WRONG:**
```yaml
root_path: /Workspace/Users/.../lakeflow-community-connectors
```

**CORRECT:**
```yaml
# (Don't include this field at all)
```

---

## 💡 KEY INSIGHTS

### Why Remove `/Workspace`?
- `/Workspace` is the physical filesystem mount point
- DLT expects logical paths: `/Users/...`, `/Repos/...`
- Using `/Workspace` will cause "file not found" errors

### Why Change `glob` to `notebook`?
- Glob patterns (`**`) are for multiple files
- You have a single pipeline notebook
- DLT needs the exact file path

### Why `target` instead of `schema`?
- `target` is the standard DLT term
- Both work, but `target` is more correct
- Avoid confusion with schema concepts

### Why `development: true`?
- Enables detailed error messages
- Better for testing and debugging
- Change to `false` only after successful testing

---

## 📞 READY TO APPLY?

Once you've made these changes:
1. Click "Save"
2. Review any validation errors
3. If successful, proceed to "Start"
4. Report back what happens!

**I'm here to help if you encounter any issues during the update!** 🚀

