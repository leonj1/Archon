-- Migration to remove project management features
-- This script drops all project-related tables and functions

BEGIN;

-- Remove RLS policies and triggers only if tables exist
-- This ensures the migration is idempotent and safe on partially-reset DBs
DO $$
BEGIN
  IF to_regclass('public.archon_projects') IS NOT NULL THEN
    DROP POLICY IF EXISTS "Allow service role full access to archon_projects" ON archon_projects;
    DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_projects" ON archon_projects;
    DROP TRIGGER IF EXISTS update_archon_projects_updated_at ON archon_projects;
  END IF;

  IF to_regclass('public.archon_tasks') IS NOT NULL THEN
    DROP POLICY IF EXISTS "Allow service role full access to archon_tasks" ON archon_tasks;
    DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_tasks" ON archon_tasks;
    DROP TRIGGER IF EXISTS update_archon_tasks_updated_at ON archon_tasks;
  END IF;

  IF to_regclass('public.archon_project_sources') IS NOT NULL THEN
    DROP POLICY IF EXISTS "Allow service role full access to archon_project_sources" ON archon_project_sources;
    DROP POLICY IF EXISTS "Allow authenticated users to read and update archon_project_sources" ON archon_project_sources;
  END IF;
END $$;

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
DO $$
BEGIN
  IF to_regclass('public.credentials') IS NOT NULL THEN
    DELETE FROM public.credentials WHERE key IN ('PROJECTS_ENABLED');
  END IF;
END $$;

COMMIT;