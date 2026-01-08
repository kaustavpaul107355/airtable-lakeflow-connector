# Table Name Sanitization - Comprehensive Fix

## Date: January 8, 2026

## Problem
Table names with spaces, special characters, or starting with numbers were causing SQL parsing errors in multiple places:
1. **View names** (e.g., "Packaging Tasks_staging") - ParseException
2. **Destination table names** (when not explicitly specified in spec)
3. **Inconsistent sanitization logic** across the codebase

## Solution
Created a centralized `sanitize_table_name()` function with comprehensive logic:

### Sanitization Rules
```python
def sanitize_table_name(table_name: str) -> str:
    """
    Sanitize table name to be a valid SQL identifier.
    
    Rules:
    1. Convert to lowercase
    2. Replace spaces, hyphens with underscores
    3. Remove parentheses, brackets, braces
    4. Remove special characters (keep only alphanumeric + underscore)
    5. Replace multiple underscores with single underscore
    6. Remove leading/trailing underscores
    7. Prepend 'table_' if starts with digit
    """
```

### Examples
| Input | Output |
|-------|--------|
| `Packaging Tasks` | `packaging_tasks` |
| `Creative Requests` | `creative_requests` |
| `My-Table (2024)` | `my_table_2024` |
| `Campaigns` | `campaigns` |
| `Test__Multiple___Underscores` | `test_multiple_underscores` |
| `123StartWithNumber` | `table_123startwithnumber` |
| `Special!@#$%^&*()Chars` | `special_chars` |
| `  Trim Spaces  ` | `trim_spaces` |

## Changes Made

### 1. libs/spec_parser.py
**Added:**
- `sanitize_table_name()` function (centralized sanitization logic)
- Import of `re` module for regex operations

**Updated:**
- `get_full_destination_table_name()` method now sanitizes source table names when `destination_table` is not specified

**Before:**
```python
table = obj.table.destination_table or table_name  # ❌ Could have spaces
```

**After:**
```python
table = obj.table.destination_table or sanitize_table_name(table_name)  # ✅ Always sanitized
```

### 2. pipeline/ingestion_pipeline.py
**Updated:**
- Import `sanitize_table_name` from `libs.spec_parser`
- Replaced inline sanitization logic with centralized function call

**Before:**
```python
sanitized_table = table.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
```

**After:**
```python
sanitized_table = sanitize_table_name(table)
```

## Impact

### What's Fixed
✅ **View names:** All auto-generated staging views use sanitized names
✅ **Destination tables:** Default table names are sanitized when not explicitly specified
✅ **Consistency:** Same sanitization logic everywhere
✅ **Edge cases:** Handles multiple underscores, leading/trailing spaces, special chars, numbers

### What Users Can Do Now
1. **Use any table name in Airtable** - spaces, special chars, etc. all work
2. **Optional destination_table** - can omit it and get auto-sanitized name
3. **Predictable names** - clear sanitization rules, documented behavior

### Backward Compatibility
⚠️ **Breaking change if:**
- You were relying on `destination_table` defaulting to unsanitized source table name
- Solution: Explicitly set `destination_table` in your pipeline spec

✅ **Not breaking if:**
- You already specify `destination_table` explicitly (recommended practice)
- Your source table names don't have spaces or special characters

## Files Changed
1. `libs/spec_parser.py`
   - Added `sanitize_table_name()` function
   - Updated `get_full_destination_table_name()` to use sanitization
   
2. `pipeline/ingestion_pipeline.py`
   - Imported `sanitize_table_name`
   - Replaced inline sanitization with function call

## Testing
Manual verification with common table name patterns:
- Tables with spaces ✅
- Tables with hyphens ✅
- Tables with parentheses ✅
- Tables with special characters ✅
- Tables starting with numbers ✅
- Tables with multiple underscores ✅

## Documentation
- Function docstring includes examples
- Comments explain the sanitization logic
- This document provides comprehensive overview

## Recommendation for Users

### Best Practice (Recommended)
Always explicitly specify `destination_table` in your pipeline spec:
```python
{
    "table": {
        "source_table": "Packaging Tasks",  # Original Airtable name
        "destination_catalog": "main",
        "destination_schema": "default",
        "destination_table": "packaging_tasks",  # Explicit sanitized name
    }
}
```

### Automatic (Now Supported)
Let the framework auto-sanitize:
```python
{
    "table": {
        "source_table": "Packaging Tasks",  # Original Airtable name
        "destination_catalog": "main",
        "destination_schema": "default",
        # destination_table omitted - will auto-sanitize to "packaging_tasks"
    }
}
```

Both approaches work correctly now!

## Version
This fix is part of v1.0.1 (patch release)
