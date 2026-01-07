-- ============================================================================
-- Unity Catalog Connection for Airtable Lakeflow Connector
-- ============================================================================
-- 
-- Based on expert guidance:
-- 1. Use GENERIC_LAKEFLOW_CONNECT type
-- 2. Pass bearer_token as plain text (NOT base64 encoded)
--
-- Run this in Databricks SQL or a notebook cell
-- ============================================================================

-- For your workspace
CREATE CONNECTION IF NOT EXISTS airtable
TYPE GENERIC_LAKEFLOW_CONNECT
OPTIONS (
  sourceName 'airtable',
  bearer_token 'YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN',
  base_id 'YOUR_AIRTABLE_BASE_ID',
  base_url 'https://api.airtable.com/v0'
)
COMMENT 'Airtable API connection for Lakeflow Community Connector';

-- Verify the connection was created
DESCRIBE CONNECTION airtable;

-- Expected output should show:
-- Connection Name: airtable
-- Type: GENERIC_LAKEFLOW_CONNECT
-- Options: bearer_token, base_id, base_url
-- Comment: Airtable API connection for Lakeflow Community Connector

-- ============================================================================
-- Alternative: If connection already exists, update it
-- ============================================================================
-- 
-- If you get an error that the connection already exists, drop and recreate:
-- 
-- DROP CONNECTION IF EXISTS airtable;
-- 
-- Then re-run the CREATE CONNECTION statement above
-- 
-- ============================================================================

-- ============================================================================
-- For alternative workspace (if needed)
-- ============================================================================
-- 
-- CREATE CONNECTION IF NOT EXISTS airtable_connection
-- TYPE GENERIC_LAKEFLOW_CONNECT
-- OPTIONS (
--   bearer_token 'YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN',
--   base_id 'YOUR_AIRTABLE_BASE_ID',
--   base_url 'https://api.airtable.com/v0'
-- )
-- COMMENT 'Airtable API connection for Lakeflow Community Connector';
-- 
-- ============================================================================

