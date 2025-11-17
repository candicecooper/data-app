-- Add missing program column to students table
ALTER TABLE students ADD COLUMN IF NOT EXISTS program TEXT;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'students'
ORDER BY ordinal_position;

-- Show current students to see what data we have
SELECT id, name, first_name, last_name, grade, program 
FROM students
LIMIT 20;
