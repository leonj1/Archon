-- Migration to remove project management features
-- This script drops all project-related tables and functions

BEGIN;

-- Remove RLS policies first
DROP POLICY IF EXISTS "Allow service role full access to archon_projects" ON archon_projects;
DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_projects" ON archon_projects;
DROP POLICY IF EXISTS "Allow service role full access to archon_tasks" ON archon_tasks;
DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_tasks" ON archon_tasks;
DROP POLICY IF EXISTS "Allow service role full access to archon_project_sources" ON archon_project_sources;
DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_project_sources" ON archon_project_sources;

-- Drop table triggers
DROP TRIGGER IF EXISTS update_archon_projects_updated_at ON archon_projects;
DROP TRIGGER IF EXISTS update_archon_tasks_updated_at ON archon_tasks;

-- Drop functions
DROP FUNCTION IF EXISTS archive_task_soft(UUID);

-- Drop tables in dependency order (child tables first)
DROP TABLE IF EXISTS archon_document_versions CASCADE;
DROP TABLE IF EXISTS archon_project_sources CASCADE;
DROP TABLE IF EXISTS archon_tasks CASCADE;
DROP TABLE IF EXISTS archon_projects CASCADE;

-- Drop custom types
DROP TYPE IF EXISTS task_status CASCADE;

-- Remove credentials related to projects
DELETE FROM credentials WHERE key IN ('PROJECTS_ENABLED');

COMMIT;