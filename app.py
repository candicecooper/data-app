import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from functools import wraps
import traceback
from supabase import create_client, Client

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = "https://szhebjnxxiwomgediufp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6aGViam54eGl3b21nZWRpdWZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1MjgxMjMsImV4cCI6MjA3NzEwNDEyM30.AFGZkidWXf07VDcGXRId-rFg5SdAEwmq7EiHM-Zuu5o"

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ERROR HANDLING SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app_errors.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(AppError):
    pass

def handle_errors(user_message: str = "An error occurred"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{func.__name__}: {e.message}", exc_info=True)
                st.error(e.user_message)
                return None
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                st.error(f"{user_message}. Please try again or contact support.")
                with st.expander("Error Details"):
                    st.code(str(e))
                return None
        return wrapper
    return decorator

# --- CONFIG ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

PLOTLY_THEME = 'plotly'

# --- MOCK DATA (used only if DB empty) ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's2', 'name': 'Daniel Lee', 'role': 'PY', 'active': True, 'archived': False},
    {'id': 's3', 'name': 'Sarah Chen', 'role': 'SY', 'active': True, 'archived': False},
    {'id': 's4', 'name': 'Admin User', 'role': 'ADM', 'active': True, 'archived': False},
    {'id': 's5', 'name': 'Michael Torres', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's6', 'name': 'Jessica Williams', 'role': 'PY', 'active': True, 'archived': False},
]

STAFF_ROLES = ['JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO']

MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'dob': '2012-03-15', 'edid': 'ED12345', 'profile_status': 'Complete', 'program': 'SY', 'archived': False},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'dob': '2011-07-22', 'edid': 'ED12346', 'profile_status': 'Draft', 'program': 'PY', 'archived': False},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'dob': '2010-11-08', 'edid': 'ED12347', 'profile_status': 'Pending', 'program': 'SY', 'archived': False},
    {'id': 'stu_004', 'name': 'Emma T.', 'grade': 'R', 'dob': '2017-05-30', 'edid': 'ED12348', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_005', 'name': 'Oliver S.', 'grade': 'Y2', 'dob': '2015-09-12', 'edid': 'ED12349', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_006', 'name': 'Sophie M.', 'grade': 'Y5', 'dob': '2014-01-25', 'edid': 'ED12350', 'profile_status': 'Complete', 'program': 'PY', 'archived': False},
    {'id': 'stu_arch_001', 'name': 'Jackson P.', 'grade': 'Y10', 'dob': '2009-04-17', 'edid': 'ED12351', 'profile_status': 'Complete', 'program': 'SY', 'archived': True},
    {'id': 'stu_arch_002', 'name': 'Ava L.', 'grade': 'Y6', 'dob': '2013-12-03', 'edid': 'ED12352', 'profile_status': 'Complete', 'program': 'PY', 'archived': True},
]

PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

GRADE_OPTIONS = {
    'JP': ['R', 'Y1', 'Y2'],
    'PY': ['Y3', 'Y4', 'Y5', 'Y6'],
    'SY': ['Y7', 'Y8', 'Y9', 'Y10', 'Y11', 'Y12']
}

behaviour_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']
behaviourS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Other - Specify']

ANTECEDENTS_NEW = [
    "Requested to transition activity",
    "Given instruction/demand (Academic)",
    "Given instruction/demand (Non-Academic)",
    "Peer conflict/Teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory over-stimulation (Noise/Lights)",
    "Access to preferred item/activity denied"
]

INTERVENTIONS = [
    "Prompted use of coping skill (e.g., breathing)",
    "Proximity control/Non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break/Choice of task",
    "Used planned ignoring of minor behaviour",
    "Staff de-escalation script/Verbal coaching",
    "Removed other students from area for safety",
    "Called for staff support/Backup"
]

# SUPPORT TYPES – cleaned (no brackets)
SUPPORT_TYPES = [
    "1:1 Individual Support",
    "Independent",
    "Small Group",
    "Large Group"
]

LOCATIONS = [
    "--- Select Location ---",
    "JP Classroom",
    "JP Spill Out",
    "PY Classroom",
    "PY Spill Out",
    "SY Classroom",
    "SY Spill Out",
    "Student Kitchen",
    "Admin",
    "Gate",
    "Library",
    "Van/Kia",
    "Swimming",
    "Yard",
    "Playground",
    "Toilets",
    "Excursion",
    "Other"
]

VALID_PAGES = [
    'login', 'landing', 'program_students',
    'direct_log_form', 'critical_incident_abch',
    'student_analysis', 'admin_portal'
]

# --- DATA LOADING FUNCTIONS (SUPABASE) ---

def load_students_from_db() -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()
        response = supabase.table('students').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error loading students: {e}")
        return MOCK_STUDENTS.copy()

def load_staff_from_db() -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()
        response = supabase.table('staff').select('*').execute()
        return response.data if response.data else MOCK_STAFF.copy()
    except Exception as e:
        logger.error(f"Error loading staff: {e}")
        return MOCK_STAFF.copy()

def load_incidents_from_db() -> List[Dict[str, Any]]:
    try:
        supabase = get_supabase_client()
        response = supabase.table('incidents').select('*').execute()
        incidents = []
        if response.data:
            for inc in response.data:
                normalized = inc.copy()
                normalized['date'] = inc.get('incident_date', inc.get('date', ''))
                normalized['time'] = inc.get('incident_time', inc.get('time', ''))
                normalized['day'] = inc.get('day_of_week', inc.get('day', ''))
                incidents.append(normalized)
        return incidents
    except Exception as e:
        logger.error(f"Error loading incidents: {e}")
        return []

def load_system_settings() -> Dict[str, Any]:
    try:
        supabase = get_supabase_client()
        response = supabase.table('system_settings').select('*').execute()
        settings = {}
        if response.data:
            for setting in response.data:
                settings[setting['setting_key']] = setting['setting_value']
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}

# --- SESSION STATE INITIALISATION ---

def initialize_session_state():
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data from database..."):
            st.session_state.students_list = load_students_from_db()
            st.session_state.staff_list = load_staff_from_db()
            st.session_state.incidents = load_incidents_from_db()
            st.session_state.system_settings = load_system_settings()
            st.session_state.data_loaded = True

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'current_incident_id' not in st.session_state:
        st.session_state.current_incident_id = None
    if 'abch_row_count' not in st.session_state:
        st.session_state.abch_row_count = 1

# --- CORE HELPERS ---

def navigate_to(page: str, student_id: Optional[str] = None, program: Optional[str] = None):
    try:
        if page not in VALID_PAGES:
            raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")

        st.session_state.current_page = page
        if student_id:
            st.session_state.selected_student_id = student_id
        if program:
            st.session_state.selected_program = program
        st.rerun()
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        st.error("Navigation failed.")
        st.session_state.current_page = 'landing'
        st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, str]]:
    try:
        if not student_id:
            return None
        return next((s for s in st.session_state.students_list if s['id'] == student_id), None)
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None

def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    try:
        return next((i for i in st.session_state.incidents if i.get('id') == incident_id), None)
    except Exception as e:
        logger.error(f"Error retrieving incident: {e}")
        return None

def get_active_staff() -> List[Dict[str, Any]]:
    try:
        return [s for s in st.session_state.staff_list if s['active'] and not s.get('archived', False)]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []

def get_staff_by_id(staff_id: str) -> Optional[Dict[str, Any]]:
    try:
        if not staff_id:
            return None
        return next((s for s in st.session_state.staff_list if s['id'] == staff_id), None)
    except Exception as e:
        logger.error(f"Error retrieving staff member: {e}")
        return None

def get_session_window(incident_time: time) -> str:
    try:
        if time(9, 0) <= incident_time <= time(11, 0):
            return "Morning (9:00am - 11:00am)"
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            return "Middle (11:01am - 1:00pm)"
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            return "Afternoon (1:01pm - 2:45pm)"
        else:
            return "Outside School Hours (N/A)"
    except Exception:
        return "Unknown Session"

# --- STAFF & STUDENT ADD / ARCHIVE (unchanged from your original) ---
#  [Keeping your previous implementations for add_staff_member, archive_staff_member,
#   unarchive_staff_member, add_student, get_students_by_program, etc.]

# ... to keep this answer a bit shorter, those helpers are unchanged.
# You can keep your existing versions here.

# --- AUTHENTICATION ---

def verify_login(email: str) -> Optional[Dict[str, Any]]:
    try:
        if not email or not email.strip():
            return None
        email = email.strip().lower()
        staff_member = next(
            (s for s in st.session_state.staff_list
             if s.get('email', '').lower() == email and not s.get('archived', False)),
            None
        )
        return staff_member
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None

# --- VALIDATION ---

def validate_incident_form(location, reported_by, behaviour_type, severity_level, incident_date, incident_time):
    errors = []
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or not reported_by.get('name'):
        errors.append("Reporter (staff member) is missing")
    if behaviour_type == "--- Select behaviour ---":
        errors.append("Please select a behaviour Type")
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")
    if errors:
        raise ValidationError("Form validation failed", "Please correct: " + ", ".join(errors))

# --- LOGIN PAGE ---

@handle_errors("Unable to load login page")
def render_login_page():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">🔐</div>
        <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
        <p class="hero-subtitle">Staff Login</p>
        <p class="hero-tagline">Please enter your registered staff email address to access the system</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔑 Login")
        email = st.text_input("Email Address", placeholder="your.email@example.com", key="login_email")
        if st.button("🚀 Login", type="primary", use_container_width=True):
            if email:
                staff_member = verify_login(email)
                if staff_member:
                    st.session_state.logged_in = True
                    st.session_state.current_user = staff_member
                    st.session_state.current_page = 'landing'
                    st.success(f"✅ Welcome back, {staff_member['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Email not found. Please contact an administrator to register.")
            else:
                st.warning("⚠️ Please enter your email address")

# --- LANDING PAGE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        current_user = st.session_state.get('current_user', {})
        st.markdown(f"### 👋 Welcome, {current_user.get('name', 'User')}!")
        st.caption(f"Role: {current_user.get('role', 'N/A')} | {current_user.get('email', 'N/A')}")
    with col_logout:
        st.markdown("##")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = 'login'
            st.rerun()

    st.markdown("---")
    # (Keep your existing animated hero + quick actions here)
    # ...

# --- PROGRAM STUDENTS PAGE ---
# (Keep your existing render_program_students implementation)

# --- ADMIN PORTAL ---
# (Keep your existing render_admin_portal / render_staff_management / render_student_management)

# =========================================================
# INCIDENT LOG PAGE (UPDATED)
# =========================================================

@handle_errors("Unable to load incident form")
def render_direct_log_form():
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])

    st.markdown("---")

    with st.form("incident_form"):
        st.markdown("### Incident Details")
        col1, col2 = st.columns(2)

        with col1:
            incident_date = st.date_input(
                "Date of Incident (DD/MM/YYYY)", value=datetime.now(), format="DD/MM/YYYY"
            )
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)

        with col2:
            # Auto-reported by current_user
            st.markdown("### Staff Member Reporting")
            current_user = st.session_state.get('current_user')
            if current_user:
                st.info(f"{current_user.get('name', 'Unknown')} ({current_user.get('role', 'N/A')})")
                reported_by = {
                    'id': current_user.get('id'),
                    'name': current_user.get('name'),
                    'role': current_user.get('role'),
                    'is_special': False
                }
            else:
                st.error("No logged-in user found.")
                reported_by = {'id': None, 'name': None, 'role': None, 'is_special': False}

        st.markdown("### Behaviour Information")
        col3, col4 = st.columns(2)

        with col3:
            behaviour_type = st.selectbox(
                "Behaviour Type",
                options=["--- Select behaviour ---"] + behaviourS_FBA
            )
            antecedent = st.selectbox("Antecedent (Trigger)", options=ANTECEDENTS_NEW)

        with col4:
            intervention = st.selectbox("Adult Action / Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)

        # Additional staff involved
        st.markdown("### Additional Staff Involved")
        active_staff = get_active_staff()
        name_to_staff = {s['name']: s for s in active_staff if s.get('id') != reported_by.get('id')}
        additional_staff_names = st.multiselect(
            "Select additional staff (if any)",
            options=list(name_to_staff.keys())
        )
        additional_staff_list = [
            {'id': name_to_staff[name]['id'], 'name': name} for name in additional_staff_names
        ]

        severity_level = st.slider("Severity Level (1=Low, 5=Critical)", 1, 5, 2)

        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional context about the incident...",
            height=120
        )

        # --- Simple Hypothesis Section ---
        st.markdown("### Hypothesis – Best Guess of Behaviour Function")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            hypothesis_direction = st.radio(
                "Direction",
                ["To Get", "To Avoid"],
                index=0,
                horizontal=True
            )
        with col_h2:
            hypothesis_function = st.selectbox(
                "Function Type",
                ["tangible", "request", "activity", "sensory", "attention"]
            )
        hypothesis_summary = f"{hypothesis_direction} {hypothesis_function}"

        submitted = st.form_submit_button("Submit Incident Report", type="primary", use_container_width=True)

        if submitted:
            try:
                validate_incident_form(
                    location, reported_by, behaviour_type,
                    severity_level, incident_date, incident_time
                )

                session = get_session_window(incident_time)

                new_incident = {
                    'student_id': student_id,
                    'student_name': student['name'],
                    'incident_date': incident_date.strftime('%Y-%m-%d'),
                    'incident_time': incident_time.strftime('%H:%M:%S'),
                    'day_of_week': incident_date.strftime('%A'),
                    'session': session,
                    'location': location,
                    'reported_by_name': reported_by['name'],
                    'reported_by_id': reported_by['id'],
                    'reported_by_role': reported_by['role'],
                    'is_special_staff': False,
                    'behaviour_type': behaviour_type,
                    'antecedent': antecedent,
                    'intervention': intervention,
                    'support_type': support_type,
                    'severity': severity_level,
                    'description': description,
                    'is_critical': severity_level >= 3,
                    'additional_staff': additional_staff_list,
                    'hypothesis_direction': hypothesis_direction,
                    'hypothesis_function': hypothesis_function,
                    'hypothesis_summary': hypothesis_summary
                }

                supabase = get_supabase_client()
                response = supabase.table('incidents').insert(new_incident).execute()

                if response.data:
                    saved_incident = response.data[0]
                    saved_incident['date'] = saved_incident['incident_date']
                    saved_incident['time'] = saved_incident['incident_time']
                    saved_incident['day'] = saved_incident['day_of_week']
                    st.session_state.incidents.append(saved_incident)
                    st.success("✅ Incident report submitted successfully!")

                    if severity_level >= 3:
                        st.warning("⚠️ This is a critical incident (Severity 3-5). Redirecting to Critical ABCH form.")
                        st.session_state.current_incident_id = saved_incident.get('id')
                        navigate_to('critical_incident_abch')
                    else:
                        col_another, col_return = st.columns(2)
                        with col_another:
                            if st.button("➕ Log Another Incident", use_container_width=True):
                                st.rerun()
                        with col_return:
                            if st.button("↩️ Return to Student List", use_container_width=True):
                                navigate_to('program_students', program=student['program'])
                else:
                    st.error("Failed to save incident to database")

            except ValidationError as e:
                st.error(e.user_message)

# =========================================================
# CRITICAL INCIDENT ABCH FORM (multi-line)
# =========================================================

def render_critical_incident_abch_form():
    st.title("🚨 Critical Incident ABCH Form")

    incident_id = st.session_state.get('current_incident_id')
    quick_incident = get_incident_by_id(incident_id) if incident_id else None

    if quick_incident:
        st.caption(f"Linked to quick incident for {quick_incident.get('student_name', 'Unknown')} on {quick_incident.get('incident_date')}")
        with st.expander("View quick incident details"):
            st.json(quick_incident)
    else:
        st.info("No linked quick incident found. You can still complete the ABCH table manually.")

    st.markdown("---")
    st.markdown("### ABCH Table – Add lines for each key part of the incident")

    # Number of ABCH rows
    row_count = st.session_state.get('abch_row_count', 1)

    abch_rows = []
    for i in range(row_count):
        with st.container(border=True):
            st.markdown(f"**Incident Element {i+1}**")
            colA1, colA2, colA3, colB, colC, colH = st.columns([1.2, 2, 1.2, 2, 2, 1.6])

            # Defaults from quick incident only on first row
            default_location = quick_incident.get('location', '') if quick_incident and i == 0 else ''
            default_context = quick_incident.get('antecedent', '') if quick_incident and i == 0 else ''
            default_time = quick_incident.get('incident_time', '') if quick_incident and i == 0 else ''
            default_behaviour = quick_incident.get('behaviour_type', '') if quick_incident and i == 0 else ''
            default_consequence = ""  # none from quick log
            default_hyp = quick_incident.get('hypothesis_summary', '') if quick_incident and i == 0 else ''

            with colA1:
                loc = st.text_input("Location", value=default_location, key=f"abch_loc_{i}")
            with colA2:
                ctx = st.text_area("Context (what was happening)", value=default_context, key=f"abch_ctx_{i}", height=80)
            with colA3:
                tme = st.text_input("Time", value=default_time, key=f"abch_time_{i}")
            with colB:
                beh = st.text_area("Behaviour (observed)", value=default_behaviour, key=f"abch_beh_{i}", height=80)
            with colC:
                cons = st.text_area("Consequences (what happened after)", value=default_consequence, key=f"abch_cons_{i}", height=80)
            with colH:
                dir_val = st.radio(
                    "Direction",
                    ["To Get", "To Avoid"],
                    index=0,
                    key=f"abch_dir_{i}"
                )
                func_val = st.selectbox(
                    "Function",
                    ["tangible", "request", "activity", "sensory", "attention"],
                    key=f"abch_func_{i}"
                )
                hyp_text = f"{dir_val} {func_val}"
                st.caption(f"Hypothesis: {hyp_text}")

            abch_rows.append({
                'location': loc,
                'context': ctx,
                'time': tme,
                'behaviour': beh,
                'consequence': cons,
                'direction': dir_val,
                'function': func_val,
                'hypothesis': hyp_text
            })

    if st.button("➕ Add another ABCH line"):
        st.session_state.abch_row_count = row_count + 1
        st.rerun()

    st.markdown("---")
    st.markdown("### Safety Responses (non-restraint)")
    safety_responses = st.multiselect(
        "Select safety actions used",
        [
            "Supportive stance",
            "Cleared nearby students",
            "Student moved to safer space",
            "Additional staff attended",
            "Safety / risk plan enacted",
            "Continued monitoring until regulated",
            "First aid offered"
        ]
    )

    st.markdown("### Notifications")
    notifications = st.multiselect(
        "Who was notified?",
        [
            "Parent / Carer",
            "Line Manager",
            "Safety & Wellbeing / SSS",
            "DCP",
            "SAPOL",
            "First Aid",
            "ED155 Injury Report Completed",
            "Transport Home Arranged"
        ]
    )

    st.markdown("### Outcome Actions")
    col_o1, col_o2 = st.columns(2)
    with col_o1:
        removed = st.checkbox("Removed from learning environment")
        family_contact = st.checkbox("Family contact / meeting arranged")
        safety_updated = st.checkbox("Safety & Risk plan developed / reviewed")
    with col_o2:
        transport_home = st.checkbox("Transport home required")
        other_outcomes = st.text_area("Other outcomes to be pursued", height=80)

    st.markdown("### Recommendations (Trauma-informed)")
    default_recs = (
        "Increase predictability and co-regulation during identified trigger times. "
        "Use CPI Supportive stance and Berry Street Body/Relationship strategies to help the student "
        "return to their window of tolerance. Align adjustments with Australian Curriculum General "
        "Capabilities (Personal and Social Capability), explicitly teaching help-seeking and "
        "self-regulation skills."
    )
    recommendations = st.text_area("Recommendations", value=default_recs, height=120)

    if st.button("💾 Save Critical Incident Summary", type="primary"):
        record = {
            'quick_incident_id': incident_id,
            'abch_rows': abch_rows,
            'safety_responses': safety_responses,
            'notifications': notifications,
            'outcomes': {
                'removed': removed,
                'family_contact': family_contact,
                'safety_updated': safety_updated,
                'transport_home': transport_home,
                'other_outcomes': other_outcomes
            },
            'recommendations': recommendations,
            'created_at': datetime.now().isoformat()
        }
        st.success("Critical Incident ABCH summary saved (local session only in this version).")
        with st.expander("View saved data"):
            st.json(record)

        # After saving, you might want to send them back to analysis or student page
        if st.button("↩️ Return to Student Analysis"):
            navigate_to('student_analysis')

# =========================================================
# STUDENT ANALYSIS (kept simple placeholder)
# =========================================================

@handle_errors("Unable to load student analysis")
def render_student_analysis():
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])

    st.markdown("---")
    student_incidents = [inc for inc in st.session_state.incidents if inc.get('student_id') == student_id]

    if not student_incidents:
        st.info("No incident data available for this student yet.")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to('direct_log_form', student_id=student_id)
        return

    st.markdown("### Summary (quick placeholder – can be extended)")
    st.metric("Total Incidents", len(student_incidents))
    critical_count = len([i for i in student_incidents if i.get('is_critical')])
    st.metric("Critical Incidents", critical_count)

    # You can extend with graphs here as needed.

# =========================================================
# MAIN APP ROUTER
# =========================================================

def main():
    initialize_session_state()

    if not st.session_state.get('logged_in', False):
        render_login_page()
        return

    current_page = st.session_state.get('current_page', 'landing')

    if current_page == 'login':
        render_login_page()
    elif current_page == 'landing':
        render_landing_page()
    elif current_page == 'program_students':
        # use your existing render_program_students
        render_program_students()
    elif current_page == 'direct_log_form':
        render_direct_log_form()
    elif current_page == 'critical_incident_abch':
        render_critical_incident_abch_form()
    elif current_page == 'student_analysis':
        render_student_analysis()
    elif current_page == 'admin_portal':
        render_admin_portal()
    else:
        st.error("Unknown page")
        navigate_to('landing')

if __name__ == '__main__':
    main()
