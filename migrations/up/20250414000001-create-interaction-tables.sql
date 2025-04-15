# migrations/up/20250414000001-create-interaction-tables.sql
-- Migration: Create Interaction Tables
-- Created at: 2025-04-14T00:00:01

-- Create interaction status enum type
CREATE TYPE interaction_status_enum AS ENUM ('ACTIVE', 'COMPLETED', 'ABANDONED');

-- Create interactions table
CREATE TABLE interactions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    session_id UUID NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    status interaction_status_enum NOT NULL DEFAULT 'ACTIVE',
    tags TEXT[] DEFAULT '{}',
    meta_data JSONB DEFAULT '{}'::jsonb  
);

-- Create prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY,
    interaction_id UUID NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    context JSONB DEFAULT '{}'::jsonb,
    client_metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT uq_prompt_sequence UNIQUE (interaction_id, sequence_number)
);

-- Create responses table
CREATE TABLE responses (
    id UUID PRIMARY KEY,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    model_confidence FLOAT,
    error TEXT,
    CONSTRAINT uq_prompt_response UNIQUE (prompt_id)
);

-- Create interaction_bookmarks table
CREATE TABLE interaction_bookmarks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    interaction_id UUID NOT NULL REFERENCES interactions(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_bookmark UNIQUE (user_id, interaction_id)
);

-- Create indexes
CREATE INDEX idx_interactions_user_id ON interactions(user_id);
CREATE INDEX idx_interactions_model_id ON interactions(model_id);
CREATE INDEX idx_interactions_status ON interactions(status);
CREATE INDEX idx_interactions_started_at ON interactions(started_at);
CREATE INDEX idx_prompts_interaction_id ON prompts(interaction_id);
CREATE INDEX idx_responses_prompt_id ON responses(prompt_id);
CREATE INDEX idx_bookmarks_user_id ON interaction_bookmarks(user_id);
CREATE INDEX idx_bookmarks_interaction_id ON interaction_bookmarks(interaction_id);