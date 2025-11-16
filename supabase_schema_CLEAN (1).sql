-- Behaviour Support & Data Analysis Tool - Supabase Schema
-- Execute this in your Supabase SQL Editor

-- ============================================
-- 1. STUDENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    dob DATE NOT NULL,
    grade TEXT NOT NULL,
    program TEXT NOT NULL CHECK (program IN ('JP', 'PY', 'SY')),
    edid TEXT UNIQUE NOT NULL,
    profile_status TEXT DEFAULT 'Draft' CHECK (profile_status IN ('Draft', 'Pending', 'Complete')),
    archived BOOLEAN DEFAULT FALSE,
    archived_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_students_program ON students(program) WHERE archived = FALSE;
CREATE INDEX IF NOT EXISTS idx_students_edid ON students(edid);
CREATE INDEX IF NOT EXISTS idx_students_archived ON students(archived);

-- ============================================
-- 2. STAFF TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS staff (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO')),
    active BOOLEAN DEFAULT TRUE,
    archived BOOLEAN DEFAULT FALSE,
    archived_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for active staff lookups
CREATE INDEX IF NOT EXISTS idx_staff_active ON staff(active, archived);
CREATE INDEX IF NOT EXISTS idx_staff_role ON staff(role) WHERE archived = FALSE;

-- ============================================
-- 3. INCIDENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    incident_date DATE NOT NULL,
    incident_time TIME NOT NULL,
    day_of_week TEXT NOT NULL,
    session TEXT NOT NULL,
    location TEXT NOT NULL,
    
    -- Staff information
    reported_by_id UUID REFERENCES staff(id),
    reported_by_name TEXT NOT NULL,
    reported_by_role TEXT NOT NULL,
    is_special_staff BOOLEAN DEFAULT FALSE,
    
    -- Behavior details
    behavior_type TEXT NOT NULL,
    antecedent TEXT NOT NULL,
    intervention TEXT NOT NULL,
    support_type TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 5),
    is_critical BOOLEAN DEFAULT FALSE,
    description TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_incidents_student ON incidents(student_id);
CREATE INDEX IF NOT EXISTS idx_incidents_date ON incidents(incident_date DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_critical ON incidents(is_critical) WHERE is_critical = TRUE;
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_behavior ON incidents(behavior_type);
CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidents(location);

-- ============================================
-- 4. CRITICAL INCIDENT REPORTS (ABCH Form)
-- ============================================
CREATE TABLE IF NOT EXISTS critical_incident_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    
    -- ABCH Details
    context TEXT NOT NULL,
    behavior_description TEXT NOT NULL,
    consequences TEXT NOT NULL,
    
    -- Notifications
    manager_notified BOOLEAN NOT NULL,
    manager_name TEXT,
    manager_notification_time TIMESTAMPTZ,
    
    parent_notified BOOLEAN NOT NULL,
    parent_name TEXT,
    parent_notification_time TIMESTAMPTZ,
    
    -- Additional details
    witnesses TEXT,
    injuries BOOLEAN DEFAULT FALSE,
    injury_details TEXT,
    property_damage BOOLEAN DEFAULT FALSE,
    property_damage_details TEXT,
    
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_notes TEXT,
    
    -- Metadata
    created_by UUID REFERENCES staff(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_critical_reports_student ON critical_incident_reports(student_id);
CREATE INDEX IF NOT EXISTS idx_critical_reports_date ON critical_incident_reports(created_at DESC);

-- ============================================
-- 5. SYSTEM SETTINGS
-- ============================================
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key TEXT UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
    ('locations', '["JP Classroom", "JP Spill Out", "PY Classroom", "PY Spill Out", "SY Classroom", "SY Spill Out", "Student Kitchen", "Admin", "Gate", "Library", "Van/Kia", "Swimming", "Yard", "Playground", "Toilets", "Excursion", "Other"]'::jsonb, 'Available incident locations'),
    ('behaviors', '["Verbal Refusal", "Elopement", "Property Destruction", "Aggression (Peer)", "Other - Specify"]'::jsonb, 'Behavior types'),
    ('antecedents', '["Requested to transition activity", "Given instruction/demand (Academic)", "Given instruction/demand (Non-Academic)", "Peer conflict/Teasing", "Staff attention shifted away", "Unstructured free time (Recess/Lunch)", "Sensory over-stimulation (Noise/Lights)", "Access to preferred item/activity denied"]'::jsonb, 'Antecedent options'),
    ('interventions', '["Prompted use of coping skill (e.g., breathing)", "Proximity control/Non-verbal cue", "Redirection to a preferred activity", "Offered a break/Choice of task", "Used planned ignoring of minor behavior", "Staff de-escalation script/Verbal coaching", "Removed other students from area for safety", "Called for staff support/Backup"]'::jsonb, 'Intervention strategies'),
    ('support_types', '["1:1 (Individual Support)", "Independent (No direct support)", "Small Group (3-5 students)", "Large Group (Whole class/assembly)"]'::jsonb, 'Support type options')
ON CONFLICT (setting_key) DO NOTHING;

-- ============================================
-- 6. AUDIT LOG (Optional but recommended)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_by UUID,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_date ON audit_log(changed_at DESC);

-- ============================================
-- 7. TRIGGERS FOR UPDATED_AT
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
DROP TRIGGER IF EXISTS update_staff_updated_at ON staff;
DROP TRIGGER IF EXISTS update_incidents_updated_at ON incidents;
DROP TRIGGER IF EXISTS update_critical_reports_updated_at ON critical_incident_reports;

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_critical_reports_updated_at BEFORE UPDATE ON critical_incident_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 8. ROW LEVEL SECURITY (RLS) - Basic Setup
-- ============================================
-- Enable RLS on all tables
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE critical_incident_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow all operations on students" ON students;
DROP POLICY IF EXISTS "Allow all operations on staff" ON staff;
DROP POLICY IF EXISTS "Allow all operations on incidents" ON incidents;
DROP POLICY IF EXISTS "Allow all operations on critical_incident_reports" ON critical_incident_reports;
DROP POLICY IF EXISTS "Allow all operations on system_settings" ON system_settings;
DROP POLICY IF EXISTS "Allow all operations on audit_log" ON audit_log;

-- Create policies (allowing all operations for now - customize based on your auth needs)
CREATE POLICY "Allow all operations on students" ON students FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on staff" ON staff FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on incidents" ON incidents FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on critical_incident_reports" ON critical_incident_reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on system_settings" ON system_settings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all operations on audit_log" ON audit_log FOR ALL USING (true) WITH CHECK (true);

-- ============================================
-- 9. HELPFUL VIEWS
-- ============================================

-- View: Active students with incident counts
CREATE OR REPLACE VIEW active_students_summary AS
SELECT 
    s.id,
    s.name,
    s.grade,
    s.program,
    s.edid,
    s.profile_status,
    COUNT(i.id) as total_incidents,
    COUNT(CASE WHEN i.is_critical THEN 1 END) as critical_incidents,
    AVG(i.severity) as avg_severity,
    MAX(i.incident_date) as last_incident_date
FROM students s
LEFT JOIN incidents i ON s.id = i.student_id
WHERE s.archived = FALSE
GROUP BY s.id, s.name, s.grade, s.program, s.edid, s.profile_status;

-- View: Recent incidents (last 30 days)
CREATE OR REPLACE VIEW recent_incidents AS
SELECT 
    i.*,
    s.name as student_name,
    s.grade,
    s.program
FROM incidents i
JOIN students s ON i.student_id = s.id
WHERE i.incident_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY i.incident_date DESC, i.incident_time DESC;

-- View: Staff activity summary
CREATE OR REPLACE VIEW staff_activity_summary AS
SELECT 
    st.id,
    st.name,
    st.role,
    COUNT(i.id) as incidents_reported,
    MAX(i.incident_date) as last_report_date
FROM staff st
LEFT JOIN incidents i ON st.id = i.reported_by_id
WHERE st.archived = FALSE AND st.active = TRUE
GROUP BY st.id, st.name, st.role;

-- ============================================
-- VERIFICATION
-- ============================================

-- Show all created tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND table_name IN ('students', 'staff', 'incidents', 'critical_incident_reports', 'system_settings', 'audit_log')
ORDER BY table_name;
