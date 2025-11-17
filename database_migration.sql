-- Behaviour Support App - Database Migration Script
-- Run these commands in your Supabase SQL editor

-- ============================================
-- STAFF TABLE UPDATES
-- ============================================

-- Add new columns to staff table
ALTER TABLE staff ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE staff ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE staff ADD COLUMN IF NOT EXISTS email TEXT;

-- Add unique constraint to email
ALTER TABLE staff ADD CONSTRAINT staff_email_unique UNIQUE (email);

-- Add created_date if it doesn't exist
ALTER TABLE staff ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW();

-- ============================================
-- STUDENTS TABLE UPDATES
-- ============================================

-- Add new columns to students table
ALTER TABLE students ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE students ADD COLUMN IF NOT EXISTS last_name TEXT;

-- Add created_date if it doesn't exist
ALTER TABLE students ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW();

-- ============================================
-- DATA MIGRATION FOR EXISTING RECORDS
-- ============================================

-- IMPORTANT: You'll need to manually update existing records
-- to split names and add email addresses.

-- Example for updating an existing staff member:
/*
UPDATE staff 
SET 
    first_name = 'Emily',
    last_name = 'Jones',
    email = 'emily.jones@example.com'
WHERE id = 's1';
*/

-- Example for updating an existing student:
/*
UPDATE students 
SET 
    first_name = 'Izack',
    last_name = 'N.'
WHERE id = 'stu_001';
*/

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check staff table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'staff'
ORDER BY ordinal_position;

-- Check students table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'students'
ORDER BY ordinal_position;

-- View staff members without emails (need to be updated)
SELECT id, name, role, email
FROM staff
WHERE email IS NULL AND archived = false;

-- View students without first/last names (need to be updated)
SELECT id, name, first_name, last_name
FROM students
WHERE (first_name IS NULL OR last_name IS NULL) AND archived = false;

-- ============================================
-- OPTIONAL: CREATE INDEXES FOR PERFORMANCE
-- ============================================

-- Index on staff email for faster login lookups
CREATE INDEX IF NOT EXISTS idx_staff_email ON staff(email);

-- Index on student EDID for faster lookups
CREATE INDEX IF NOT EXISTS idx_student_edid ON students(edid);

-- Index on incidents student_id for faster queries
CREATE INDEX IF NOT EXISTS idx_incidents_student_id ON incidents(student_id);

-- ============================================
-- SAMPLE DATA FOR TESTING
-- ============================================

-- Insert a test staff member (you can login with this email)
INSERT INTO staff (first_name, last_name, name, email, role, active, archived)
VALUES 
    ('Test', 'Administrator', 'Test Administrator', 'admin@test.com', 'ADM', true, false),
    ('Test', 'Teacher', 'Test Teacher', 'teacher@test.com', 'JP', true, false)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- ROLLBACK COMMANDS (if needed)
-- ============================================

-- CAUTION: Only run these if you need to undo the changes

/*
ALTER TABLE staff DROP COLUMN IF EXISTS first_name;
ALTER TABLE staff DROP COLUMN IF EXISTS last_name;
ALTER TABLE staff DROP COLUMN IF EXISTS email;
ALTER TABLE staff DROP CONSTRAINT IF EXISTS staff_email_unique;

ALTER TABLE students DROP COLUMN IF EXISTS first_name;
ALTER TABLE students DROP COLUMN IF EXISTS last_name;

DROP INDEX IF EXISTS idx_staff_email;
DROP INDEX IF EXISTS idx_student_edid;
DROP INDEX IF EXISTS idx_incidents_student_id;
*/
