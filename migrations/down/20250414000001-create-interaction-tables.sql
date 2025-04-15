# migrations/down/20250414000001-create-interaction-tables.sql
-- Migration: Create Interaction Tables (DOWN)
-- Created at: 2025-04-14T00:00:01

-- Drop tables
DROP TABLE IF EXISTS interaction_bookmarks;
DROP TABLE IF EXISTS responses;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS interactions;

-- Drop enum types
DROP TYPE IF EXISTS interaction_status_enum;