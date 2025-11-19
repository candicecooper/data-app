import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
import random
import uuid
import plotly.express as px
from typing import List, Dict, Any, Optional
import logging
from functools import wraps

# =========================================================
# 0. BASIC CONFIG / LOGGING
# =========================================================

st.set_page_config(
    page_title="Behaviour Support & Data Analysis - Sandbox",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

SANDBOX_MODE = True  # clear flag so we remember this is mock data only

# =========================================================
# 1. ERROR HANDLING DECORATOR
# =========================================================

class AppError(Exception):
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(AppError):
    pass

def handle_errors(user_message: str = "An error occurred"):
    """Decorator to catch and handle errors nicely in Streamlit."""
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
                st.error(f"{user_message}.")
                with st.expander("Error details"):
                    st.code(str(e))
                return None
        return wrapper
    return decorator

# =========================================================
# 2. CONSTANTS / OPTIONS
# =========================================================

PLOTLY_THEME = "plotly"

STAFF_ROLES = ['JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO']

PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

GRADE_OPTIONS = {
    'JP': ['R', 'Y1', 'Y2'],
    'PY': ['Y3', 'Y4', 'Y5', 'Y6'],
    'SY': ['Y7', 'Y8', 'Y9', 'Y10', 'Y11', 'Y12']
}

BEHAVIOURS = [
    'Verbal Refusal',
    'Elopement',
    'Property Destruction',
    'Aggression (Peer)',
    'Aggression (Staff)',
    'Other - Specify'
]

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

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class/assembly)"
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
    'login',
    'landing',
    'program_students',
    'direct_log_form',
    'critical_incident_abch',
    'student_analysis',
    'admin_portal'
]

# =========================================================
# 3. MOCK DATA GENERATION (SANDBOX)
# =========================================================

def generate_mock_students() -> List[Dict[str, Any]]:
    students = [
        # JP
        {'id': 'student_JP001', 'first_name': 'Emma', 'last_name': 'Thompson', 'name': 'Emma Thompson',
         'grade': 'R', 'dob': '2018-03-15', 'edid': 'JP001', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_JP002', 'first_name': 'Oliver', 'last_name': 'Martinez', 'name': 'Oliver Martinez',
         'grade': 'Y1', 'dob': '2017-07-22', 'edid': 'JP002', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_JP003', 'first_name': 'Sophia', 'last_name': 'Wilson', 'name': 'Sophia Wilson',
         'grade': 'Y2', 'dob': '2016-11-08', 'edid': 'JP003', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},
        # PY
        {'id': 'student_PY001', 'first_name': 'Liam', 'last_name': 'Chen', 'name': 'Liam Chen',
         'grade': 'Y3', 'dob': '2015-05-30', 'edid': 'PY001', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_PY002', 'first_name': 'Ava', 'last_name': 'Rodriguez', 'name': 'Ava Rodriguez',
         'grade': 'Y4', 'dob': '2014-09-12', 'edid': 'PY002', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_PY003', 'first_name': 'Noah', 'last_name': 'Brown', 'name': 'Noah Brown',
         'grade': 'Y6', 'dob': '2012-01-25', 'edid': 'PY003', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},
        # SY
        {'id': 'student_SY001', 'first_name': 'Isabella', 'last_name': 'Garcia', 'name': 'Isabella Garcia',
         'grade': 'Y7', 'dob': '2011-04-17', 'edid': 'SY001', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_SY002', 'first_name': 'Ethan', 'last_name': 'Davis', 'name': 'Ethan Davis',
         'grade': 'Y9', 'dob': '2009-12-03', 'edid': 'SY002', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_SY003', 'first_name': 'Mia', 'last_name': 'Anderson', 'name': 'Mia Anderson',
         'grade': 'Y11', 'dob': '2007-08-20', 'edid': 'SY003', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
    ]
    return students

def generate_mock_staff() -> List[Dict[str, Any]]:
    staff = [
        {'id': 'staff_1', 'first_name': 'Sarah', 'last_name': 'Johnson', 'name': 'Sarah Johnson',
         'email': 'sarah.johnson@demo.edu.au', 'role': 'JP', 'active': True, 'archived': False},
        {'id': 'staff_2', 'first_name': 'Michael', 'last_name': 'Lee', 'name': 'Michael Lee',
         'email': 'michael.lee@demo.edu.au', 'role': 'JP', 'active': True, 'archived': False},
        {'id': 'staff_3', 'first_name': 'Jessica', 'last_name': 'Williams', 'name': 'Jessica Williams',
         'email': 'jessica.williams@demo.edu.au', 'role': 'PY', 'active': True, 'archived': False},
        {'id': 'staff_4', 'first_name': 'David', 'last_name': 'Martinez', 'name': 'David Martinez',
         'email': 'david.martinez@demo.edu.au', 'role': 'PY', 'active': True, 'archived': False},
        {'id': 'staff_5', 'first_name': 'Emily', 'last_name': 'Brown', 'name': 'Emily Brown',
         'email': 'emily.brown@demo.edu.au', 'role': 'SY', 'active': True, 'archived': False},
        {'id': 'staff_6', 'first_name': 'James', 'last_name': 'Wilson', 'name': 'James Wilson',
         'email': 'james.wilson@demo.edu.au', 'role': 'SY', 'active': True, 'archived': False},
        {'id': 'staff_admin', 'first_name': 'Admin', 'last_name': 'Demo', 'name': 'Admin Demo',
         'email': 'admin@demo.edu.au', 'role': 'ADM', 'active': True, 'archived': False},
    ]
    return staff

def generate_mock_incidents(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    incidents = []
    student_ids = [s['id'] for s in students]
    student_lookup = {s['id']: s['name'] for s in students}
    staff_names = [s['name'] for s in generate_mock_staff()]

    behaviours = BEHAVIOURS
    locations = LOCATIONS[1:]  # skip placeholder
    antecedents = ANTECEDENTS_NEW
    interventions = INTERVENTIONS

    base_date = datetime.now() - timedelta(days=90)

    for i in range(80):
        student_id = random.choice(student_ids)
        incident_date = base_date + timedelta(days=random.randint(0, 85))

        hour = random.choices([9, 10, 11, 12, 13, 14], weights=[2, 3, 2, 1, 2, 3])[0]
        minute = random.randint(0, 59)
        incident_time = time(hour=hour, minute=minute)
        time_str = incident_time.strftime("%H:%M")

        severity = random.choices([1, 2, 3, 4, 5], weights=[4, 3, 2, 1, 0.5])[0]
        is_critical = severity >= 3  # sandbox rule

        # rough pattern biases
        beh = random.choice(behaviours)
        if is_critical:
            beh = random.choice(['Aggression (Peer)', 'Aggression (Staff)', 'Elopement'])

        antecedent_choice = random.choice(antecedents)
        if beh.startswith("Aggression"):
            antecedent_choice = random.choice([
                "Peer conflict/Teasing",
                "Staff attention shifted away"
            ])

        intervention_choice = random.choice(interventions)
        if is_critical:
            intervention_choice = random.choice([
                "Staff de-escalation script/Verbal coaching",
                "Removed other students from area for safety",
                "Called for staff support/Backup"
            ])

        session = "Morning (9:00am - 11:00am)" if time(9, 0) <= incident_time <= time(11, 0) \
            else "Middle (11:01am - 1:00pm)" if time(11, 0, 1) <= incident_time <= time(13, 0) \
            else "Afternoon (1:01pm - 2:45pm)" if time(13, 0, 1) <= incident_time <= time(14, 45) \
            else "Outside School Hours (N/A)"

        inc_id = f"mock_{i+1}"

        incidents.append({
            'id': inc_id,
            'student_id': student_id,
            'student_name': student_lookup[student_id],
            'incident_date': incident_date.strftime('%Y-%m-%d'),
            'date': incident_date.strftime('%Y-%m-%d'),
            'incident_time': time_str,
            'time': time_str,
            'day_of_week': incident_date.strftime('%A'),
            'day': incident_date.strftime('%A'),
            'session': session,
            'location': random.choice(locations),
            'reported_by_name': random.choice(staff_names),
            'reported_by_id': None,
            'reported_by_role': random.choice(['Teacher', 'SSO']),
            'is_special_staff': False,
            'behaviour_type': beh,
            'antecedent': antecedent_choice,
            'intervention': intervention_choice,
            'support_type': random.choice(['1:1 (Individual Support)', 'Small Group (3-5 students)']),
            'severity': severity,
            'description': f"Mock incident {i+1} involving {beh.lower()}",
            'is_critical': is_critical,
            'incident_type': 'Critical' if is_critical else 'Quick',
            # ABCH fields initially empty
            'abch_location': '',
            'abch_context': '',
            'abch_behaviour': '',
            'abch_consequence': '',
            'abch_hypothesis': '',
            # Outcomes
            'outcome_send_home': False,
            'outcome_leave_grounds': False,
            'outcome_student_injury': False,
            'outcome_staff_injury': False,
            'outcome_property_damage': False,
            'outcome_sexualised_behaviour': False,
            'sapol_contacted': False,
            'sapol_reason': '',
            'ambulance_contacted': False,
            'taken_to_hospital': False,
            'line_manager_notified': is_critical,
            'parent_notified': True if is_critical else random.choice([True, False]),
        })

    return incidents

# =========================================================
# 4. SESSION STATE INIT & HELPERS
# =========================================================

def initialize_session_state():
    if 'data_loaded' not in st.session_state:
        st.session_state.students_list = generate_mock_students()
        st.session_state.staff_list = generate_mock_staff()
        st.session_state.incidents = generate_mock_incidents(st.session_state.students_list)
        st.session_state.data_loaded = True

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

    if 'selected_student_id' not in st.session_state:
        st.session_state.selected_student_id = None

    if 'selected_program' not in st.session_state:
        st.session_state.selected_program = 'JP'

    if 'selected_incident_id' not in st.session_state:
        st.session_state.selected_incident_id = None

def navigate_to(page: str,
                student_id: Optional[str] = None,
                program: Optional[str] = None,
                incident_id: Optional[str] = None):
    """Changes the current page in session state and reruns."""
    if page not in VALID_PAGES:
        raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")

    st.session_state.current_page = page
    if student_id:
        st.session_state.selected_student_id = student_id
    if program:
        st.session_state.selected_program = program
    if incident_id:
        st.session_state.selected_incident_id = incident_id
    st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    if not student_id:
        return None
    for s in st.session_state.students_list:
        if s['id'] == student_id:
            return s
    return None

def get_active_staff() -> List[Dict[str, Any]]:
    return [s for s in st.session_state.staff_list if s.get('active', True) and not s.get('archived', False)]

def calculate_age(dob_str: str) -> str:
    try:
        if not dob_str:
            return "N/A"
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return str(age)
    except Exception:
        return "N/A"

# =========================================================
# 5. AUTH (SANDBOX)
# =========================================================

def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Sandbox login: any registered email with password 'demo'."""
    if not email or not password:
        return None
    email = email.strip().lower()
    if password != "demo":
        return None
    for staff in st.session_state.staff_list:
        if staff.get('email', '').lower() == email and not staff.get('archived', False):
            return staff
    return None

# =========================================================
# 6. VALIDATION
# =========================================================

def validate_incident_form(location, reported_by, behaviour_type, severity_level,
                           incident_date, incident_time):
    errors = []
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or reported_by.get('id') is None:
        errors.append("Please select a Staff Member")
    if behaviour_type == "--- Select behaviour ---":
        errors.append("Please select a Behaviour Type")
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")
    if errors:
        raise ValidationError("Form validation failed", "Please correct: " + ", ".join(errors))

# =========================================================
# 7. REUSABLE COMPONENTS
# =========================================================

def render_staff_selector(label: str = "Staff Member",
                          key: str = "staff_selector",
                          include_special_options: bool = True):
    active_staff = get_active_staff()
    options = [{'id': None, 'name': '--- Select Staff ---', 'role': None, 'special': False}]

    if include_special_options:
        options.append({'id': 'TRT', 'name': 'TRT (Relief Teacher)', 'role': 'TRT', 'special': True})
        options.append({'id': 'External_SSO', 'name': 'External SSO', 'role': 'External SSO', 'special': True})
        options.append({'id': 'divider', 'name': '─────────────────', 'role': None, 'special': False})

    options.extend([{**s, 'special': False} for s in active_staff])
    selectable = [o for o in options if o['id'] != 'divider']

    selected = st.selectbox(
        label,
        options=selectable,
        format_func=lambda x: f"{x['name']}" + (f" ({x['role']})" if x.get('role') and not x.get('special') else ""),
        key=key
    )

    if selected and selected.get('special'):
        st.markdown(f"**{selected['name']} selected** – please enter their name:")
        specific = st.text_input(
            f"Enter {selected['role']} Name",
            key=f"{key}_specific_name",
            placeholder=f"Full name of {selected['role']}"
        )
        if specific and specific.strip():
            return {
                'id': selected['id'],
                'name': specific.strip(),
                'role': selected['role'],
                'is_special': True
            }
        else:
            return {
                'id': selected['id'],
                'name': f"{selected['role']} (Name Required)",
                'role': selected['role'],
                'is_special': True,
                'name_missing': True
            }

    return selected

# =========================================================
# 8. PAGES
# =========================================================

# ------------------ LOGIN PAGE ------------------ #

@handle_errors("Unable to load login page")
def render_login_page():
    st.markdown("""
    <div style="background:#111827;padding:1rem 1.5rem;border-radius:0.75rem;margin-bottom:1rem;">
      <strong style="color:#f97316;">🔥 SANDBOX VERSION</strong>
      <span style="color:#e5e7eb;margin-left:0.75rem;">
        Mock data only – safe to explore and click everything.
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section" style="text-align:center;padding:3rem 2rem;margin-bottom:2rem;">
        <div style="font-size:4rem;margin-bottom:0.5rem;">🔐</div>
        <h1 style="font-size:2.5rem;font-weight:800;margin-bottom:0.5rem;">
            Behaviour Support & Data Analysis
        </h1>
        <p style="margin:0.25rem 0;color:#9ca3af;">Staff Login – Sandbox Environment</p>
        <p style="margin:0.25rem 0;color:#6b7280;font-size:0.9rem;">
            Use any registered staff email with password <strong>demo</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### 🔑 Login")

            email = st.text_input("Email Address", placeholder="admin@demo.edu.au", key="login_email")
            password = st.text_input("Password", type="password", placeholder="demo", key="login_password")

            if st.button("🚀 Login", type="primary", use_container_width=True):
                staff_member = verify_login(email, password)
                if staff_member:
                    st.session_state.logged_in = True
                    st.session_state.current_user = staff_member
                    st.session_state.current_page = 'landing'
                    st.success(f"✅ Welcome back, {staff_member['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password (sandbox uses password: demo)")

# ------------------ LANDING PAGE ------------------ #

@handle_errors("Unable to load landing page")
def render_landing_page():
    current_user = st.session_state.get('current_user', {})

    # Top bar
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.markdown(f"### 👋 Welcome, {current_user.get('name', 'User')}!")
        st.caption(f"Role: {current_user.get('role', 'N/A')} | {current_user.get('email', 'N/A')}")

    with col_logout:
        st.markdown("##")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = 'login'
            st.rerun()

    # Sandbox banner
    st.markdown("""
    <div style="background:linear-gradient(90deg,#4f46e5,#a855f7);padding:1rem 1.5rem;border-radius:0.75rem;margin:1rem 0;">
      <strong style="color:white;">🎭 SANDBOX MODE:</strong>
      <span style="color:#e5e7eb;margin-left:0.5rem;">
        All data is synthetic. Use this space to demo logging, critical incident workflows and analysis safely.
      </span>
    </div>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div style="text-align:center;padding:2rem 1rem;margin-bottom:1.5rem;">
        <div style="font-size:3rem;margin-bottom:0.5rem;">📊✨</div>
        <h1 style="font-size:2.25rem;font-weight:800;margin-bottom:0.25rem;">
            Behaviour Support & Data Analysis
        </h1>
        <p style="margin:0.25rem 0;color:#9ca3af;">
            Track incidents, identify patterns and connect responses to CPI, SMART, Berry Street and the Australian Curriculum capabilities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 Select Program")
    st.caption("Choose a program to view students, log incidents and access analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎨 Junior Primary (R–2)")
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='JP')
    with col2:
        st.markdown("#### 📖 Primary Years (3–6)")
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='PY')
    with col3:
        st.markdown("#### 🎓 Senior Years (7–12)")
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='SY')

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    col_quick1, col_quick2 = st.columns(2)

    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        all_active_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected = st.selectbox(
            "Select Student",
            options=options,
            format_func=lambda x: x['name'],
            label_visibility="collapsed",
            key="quick_log_student"
        )
        if selected and selected['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to('direct_log_form', student_id=selected['id'])

    with col_quick2:
        st.markdown("#### 🔐 Admin Portal (Sandbox)")
        st.caption("Manage mock staff and students – no changes affect live systems.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Access Admin Portal", key="admin_btn", use_container_width=True, type="primary"):
            navigate_to('admin_portal')

# ------------------ PROGRAM STUDENTS PAGE ------------------ #

@handle_errors("Unable to load program students page")
def render_program_students():
    program = st.session_state.get('selected_program', 'JP')

    col_title, col_back = st.columns([4, 1])
    with col_title:
        program_names = {'JP': 'Junior Primary', 'PY': 'Primary Years', 'SY': 'Senior Years'}
        st.title(f"{program_names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')

    st.markdown("---")

    tab1, tab2 = st.tabs(["📚 Current Students", "📦 Archived Students"])

    with tab1:
        current_students = [s for s in st.session_state.students_list
                            if s.get('program') == program and not s.get('archived', False)]
        if not current_students:
            st.info(f"No current students in {program}.")
        else:
            st.markdown(f"### Current Students ({len(current_students)})")

            cols_per_row = 3
            for i in range(0, len(current_students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, student in enumerate(current_students[i:i+cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {student['name']}")
                            st.markdown(f"**Grade:** {student['grade']}")
                            st.caption(f"EDID: {student.get('edid', 'N/A')}")
                            incident_count = len([inc for inc in st.session_state.incidents
                                                  if inc.get('student_id') == student['id']])
                            st.metric("Incidents", incident_count)
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button("👁️ View", key=f"view_{student['id']}", use_container_width=True):
                                    navigate_to('student_analysis', student_id=student['id'])
                            with col_log:
                                if st.button("📝 Log", key=f"log_{student['id']}", use_container_width=True):
                                    navigate_to('direct_log_form', student_id=student['id'])

    with tab2:
        archived_students = [s for s in st.session_state.students_list
                             if s.get('program') == program and s.get('archived', False)]
        if not archived_students:
            st.info(f"No archived students in {program}.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**EDID:** {student.get('edid', 'N/A')}")
                    incident_count = len([inc for inc in st.session_state.incidents
                                          if inc.get('student_id') == student['id']])
                    st.metric("Total Incidents", incident_count)
                    if st.button("View Historical Data", key=f"view_arch_{student['id']}"):
                        navigate_to('student_analysis', student_id=student['id'])

# ------------------ DIRECT INCIDENT LOG ------------------ #

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
                "Date of Incident (DD/MM/YYYY)",
                value=datetime.now().date(),
                format="DD/MM/YYYY"
            )
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)
        with col2:
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True
            )

        st.markdown("### Behaviour Information")
        col3, col4 = st.columns(2)
        with col3:
            behaviour_type = st.selectbox(
                "Behaviour Type",
                options=["--- Select behaviour ---"] + BEHAVIOURS
            )
            antecedent = st.selectbox("Antecedent (Trigger)", options=ANTECEDENTS_NEW)
        with col4:
            intervention = st.selectbox("Adult Action / Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)

        severity_level = st.slider("Severity Level (1=Low, 5=High/Critical)", 1, 5, 2)

        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional contextual information about the incident...",
            height=100
        )

        submitted = st.form_submit_button("Submit Incident Report", type="primary", use_container_width=True)

        if submitted:
            if reported_by and reported_by.get('name_missing'):
                st.error("Please enter the name for the selected staff type (TRT or External SSO).")
                return

            validate_incident_form(
                location, reported_by, behaviour_type,
                severity_level, incident_date, incident_time
            )

            # Build new incident record
            incident_time_str = incident_time.strftime('%H:%M')
            session = (
                "Morning (9:00am - 11:00am)" if time(9, 0) <= incident_time <= time(11, 0)
                else "Middle (11:01am - 1:00pm)" if time(11, 0, 1) <= incident_time <= time(13, 0)
                else "Afternoon (1:01pm - 2:45pm)" if time(13, 0, 1) <= incident_time <= time(14, 45)
                else "Outside School Hours (N/A)"
            )

            inc_id = str(uuid.uuid4())
            is_critical = severity_level >= 3  # key rule for routing

            new_incident = {
                'id': inc_id,
                'student_id': student_id,
                'student_name': student['name'],
                'incident_date': incident_date.strftime('%Y-%m-%d'),
                'date': incident_date.strftime('%Y-%m-%d'),
                'incident_time': incident_time_str,
                'time': incident_time_str,
                'day_of_week': incident_date.strftime('%A'),
                'day': incident_date.strftime('%A'),
                'session': session,
                'location': location,
                'reported_by_name': reported_by['name'],
                'reported_by_id': None if reported_by.get('is_special') else reported_by['id'],
                'reported_by_role': reported_by['role'],
                'is_special_staff': reported_by.get('is_special', False),
                'behaviour_type': behaviour_type,
                'antecedent': antecedent,
                'intervention': intervention,
                'support_type': support_type,
                'severity': severity_level,
                'description': description,
                'is_critical': is_critical,
                'incident_type': 'Critical' if is_critical else 'Quick',
                # ABCH fields initially blank
                'abch_location': '',
                'abch_context': '',
                'abch_behaviour': '',
                'abch_consequence': '',
                'abch_hypothesis': '',
                # Outcomes
                'outcome_send_home': False,
                'outcome_leave_grounds': False,
                'outcome_student_injury': False,
                'outcome_staff_injury': False,
                'outcome_property_damage': False,
                'outcome_sexualised_behaviour': False,
                'sapol_contacted': False,
                'sapol_reason': '',
                'ambulance_contacted': False,
                'taken_to_hospital': False,
                'line_manager_notified': is_critical,
                'parent_notified': True,
            }

            st.session_state.incidents.append(new_incident)
            st.success("✅ Incident report submitted successfully!")

            if is_critical:
                st.warning("⚠️ Severity ≥ 3 – launching Critical Incident ABCH form.")
                # move straight to critical incident page
                navigate_to('critical_incident_abch',
                            student_id=student_id,
                            incident_id=inc_id)
            else:
                col_another, col_return = st.columns(2)
                with col_another:
                    if st.button("➕ Log Another Incident", use_container_width=True):
                        st.rerun()
                with col_return:
                    if st.button("↩️ Return to Student List", use_container_width=True):
                        navigate_to('program_students', program=student['program'])

# ------------------ CRITICAL INCIDENT ABCH FORM ------------------ #

@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    student_id = st.session_state.get('selected_student_id')
    incident_id = st.session_state.get('selected_incident_id')
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return

    incident = None
    for inc in st.session_state.incidents:
        if inc['id'] == incident_id:
            incident = inc
            break

    if not incident:
        st.error("Critical incident record not found.")
        if st.button("Return to Student"):
            navigate_to('student_analysis', student_id=student_id)
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"🚨 Critical Incident ABCH: {student['name']}")
        st.caption(
            f"Date: {incident['date']} | Time: {incident['time']} | Location: {incident['location']} "
            f"| Severity: {incident['severity']} (Critical)"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('student_analysis', student_id=student_id)

    st.markdown("This section aligns with **ABCH** (Antecedent, Behaviour, Consequence, Hypothesis) "
                "and supports CPI, SMART, Berry Street and trauma-informed documentation.")

    st.markdown("### ABCH Summary")

    # ABCH row across the page
    col_loc, col_ctx, col_time, col_beh, col_conseq, col_hyp = st.columns([1.2, 2.2, 1, 2.2, 2.2, 2])
    with col_loc:
        abch_location = st.text_input(
            "Location",
            value=incident.get('abch_location') or incident['location'],
            key="abch_location"
        )
    with col_ctx:
        abch_context = st.text_area(
            "Context (What was happening just before the behaviour?)",
            value=incident.get('abch_context', ''),
            height=100,
            key="abch_context"
        )
    with col_time:
        st.write("Time")
        abch_time = st.text_input(
            " ",
            value=incident['time'],
            label_visibility="collapsed",
            key="abch_time"
        )
    with col_beh:
        abch_behaviour = st.text_area(
            "Behaviour (What did the student do – observed)",
            value=incident.get('abch_behaviour') or incident['behaviour_type'],
            height=100,
            key="abch_behaviour"
        )
    with col_conseq:
        abch_consequence = st.text_area(
            "Consequences (What happened after / how did people respond?)",
            value=incident.get('abch_consequence', ''),
            height=100,
            key="abch_consequence"
        )
    with col_hyp:
        abch_hypothesis = st.text_area(
            "Hypothesis (Best guess of behaviour function – get/avoid, sensory, attention, activity)",
            value=incident.get('abch_hypothesis', ''),
            height=100,
            key="abch_hypothesis"
        )

    st.markdown("---")
    st.markdown("### Intended Outcomes & Immediate Responses")

    col_left, col_mid, col_right = st.columns([2, 2, 1.3])

    with col_left:
        st.markdown("#### Outcomes (School-based)")
        outcome_send_home = st.checkbox("Send home – parent/caregiver notified & documented",
                                        value=incident.get('outcome_send_home', False))
        outcome_leave_grounds = st.checkbox("Student leaving supervised areas / school grounds",
                                            value=incident.get('outcome_leave_grounds', False))
        outcome_property_damage = st.checkbox("Property damage",
                                              value=incident.get('outcome_property_damage', False))
        outcome_sexualised = st.checkbox("Sexualised behaviour",
                                         value=incident.get('outcome_sexualised_behaviour', False))
        outcome_staff_injury = st.checkbox("ED155: Staff injury (submit with report)",
                                           value=incident.get('outcome_staff_injury', False))
        outcome_student_injury = st.checkbox("ED155: Student injury (submit with report)",
                                             value=incident.get('outcome_student_injury', False))

    with col_mid:
        st.markdown("#### Emergency Services")
        sapol_contacted = st.checkbox("SAPOL contacted",
                                      value=incident.get('sapol_contacted', False))
        sapol_reason = st.multiselect(
            "If SAPOL contacted – reason",
            options=[
                "Drug possession",
                "Absconding",
                "Removal from site",
                "Call out",
                "Stealing",
                "Vandalism",
                "Other"
            ],
            default=[incident.get('sapol_reason')] if incident.get('sapol_reason') else []
        )
        st.markdown("#### SA Ambulance")
        ambulance_contacted = st.checkbox("Ambulance call out",
                                          value=incident.get('ambulance_contacted', False))
        taken_to_hospital = st.checkbox("Student taken to hospital",
                                        value=incident.get('taken_to_hospital', False))

    with col_right:
        st.markdown("#### Notifications")
        line_manager_notified = st.checkbox("Line manager notified of critical incident",
                                            value=incident.get('line_manager_notified', True))
        parent_notified = st.checkbox("Parent / caregiver notified",
                                      value=incident.get('parent_notified', True))
        st.markdown("---")
        report_number = st.text_input("Report number (if required)",
                                      value=incident.get('report_number', ''),
                                      key="report_number")

    st.markdown("---")
    st.markdown("### Administration Only")
    line_manager_sig = st.text_input("Line Manager Signature / Name",
                                     value=incident.get('line_manager_sig', ''),
                                     key="line_manager_sig")
    manager_sig = st.text_input("Manager Signature / Name",
                                value=incident.get('manager_sig', ''),
                                key="manager_sig")
    safety_plan = st.text_area(
        "Safety & Risk Plan – to be developed / reviewed",
        value=incident.get('safety_plan', ''),
        height=120,
        key="safety_plan"
    )
    other_outcomes = st.text_area(
        "Other outcomes to be pursued by Cowandilla Learning Centre Management",
        value=incident.get('other_outcomes', ''),
        height=120,
        key="other_outcomes"
    )

    if st.button("💾 Save Critical Incident ABCH", type="primary", use_container_width=True):
        # update incident in session_state
        for inc in st.session_state.incidents:
            if inc['id'] == incident_id:
                inc['abch_location'] = abch_location
                inc['abch_context'] = abch_context
                inc['abch_behaviour'] = abch_behaviour
                inc['abch_consequence'] = abch_consequence
                inc['abch_hypothesis'] = abch_hypothesis
                inc['outcome_send_home'] = outcome_send_home
                inc['outcome_leave_grounds'] = outcome_leave_grounds
                inc['outcome_property_damage'] = outcome_property_damage
                inc['outcome_sexualised_behaviour'] = outcome_sexualised
                inc['outcome_staff_injury'] = outcome_staff_injury
                inc['outcome_student_injury'] = outcome_student_injury
                inc['sapol_contacted'] = sapol_contacted
                inc['sapol_reason'] = ", ".join(sapol_reason) if sapol_reason else ""
                inc['ambulance_contacted'] = ambulance_contacted
                inc['taken_to_hospital'] = taken_to_hospital
                inc['line_manager_notified'] = line_manager_notified
                inc['parent_notified'] = parent_notified
                inc['report_number'] = report_number
                inc['line_manager_sig'] = line_manager_sig
                inc['manager_sig'] = manager_sig
                inc['safety_plan'] = safety_plan
                inc['other_outcomes'] = other_outcomes
                break
        st.success("✅ Critical incident ABCH details saved (sandbox).")
        if st.button("📊 Go to Analysis for this Student", use_container_width=True):
            navigate_to('student_analysis', student_id=student_id)

# ------------------ STUDENT ANALYSIS ------------------ #

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
        st.caption(
            f"Grade {student['grade']} | {student['program']} Program | "
            f"EDID: {student.get('edid', 'N/A')}"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])

    st.markdown("---")

    student_incidents = [inc for inc in st.session_state.incidents
                         if inc.get('student_id') == student_id]

    if not student_incidents:
        st.info("No incident data available for this student yet.")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to('direct_log_form', student_id=student_id)
        return

    df = pd.DataFrame(student_incidents)
    df['incident_date'] = pd.to_datetime(df['date'])
    df['Critical?'] = df['is_critical'].map({True: 'Critical', False: 'Quick'})
    df['Severity Band'] = df['severity'].apply(
        lambda s: 'Low (1–2)' if s <= 2 else 'Critical (3–5)'
    )

    # Summary metrics
    st.markdown("### 📈 Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    total_inc = len(df)
    critical_count = df['is_critical'].sum()
    avg_sev = df['severity'].mean()
    days_span = (df['incident_date'].max() - df['incident_date'].min()).days + 1
    inc_per_week = (total_inc / days_span) * 7 if days_span > 0 else 0

    with col1:
        st.metric("Total Incidents", total_inc)
    with col2:
        critical_pct = (critical_count / total_inc * 100) if total_inc else 0
        st.metric("Critical Incidents", critical_count, f"{critical_pct:.0f}%")
    with col3:
        st.metric("Average Severity", f"{avg_sev:.1f}")
    with col4:
        st.metric("Days Tracked", days_span)
    with col5:
        st.metric("Incidents Per Week", f"{inc_per_week:.1f}")

    st.markdown("---")

    # =========== GRAPHS =========== #

    st.markdown("### 🔍 Patterns Over Time & Context")

    gcol1, gcol2 = st.columns(2)

    # 1) Timeline – critical vs quick
    with gcol1:
        timeline = df.groupby(['incident_date', 'Critical?'])['id'].count().reset_index()
        timeline.rename(columns={'id': 'Count'}, inplace=True)
        fig = px.line(
            timeline,
            x='incident_date',
            y='Count',
            color='Critical?',
            markers=True,
            title='Incidents Over Time (Quick vs Critical)'
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of incidents")
        st.plotly_chart(fig, use_container_width=True)

    # 2) Day-of-week & session heatmap
    with gcol2:
        heat = df.groupby(['day', 'session'])['id'].count().reset_index()
        if not heat.empty:
            fig_heat = px.density_heatmap(
                heat,
                x='session',
                y='day',
                z='id',
                color_continuous_scale='RdBu',
                title='Incidents by Day & Session'
            )
            fig_heat.update_layout(xaxis_title="Session", yaxis_title="Day of week")
            st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("### 🧩 Antecedents, Behaviour Types & Locations")

    g2col1, g2col2 = st.columns(2)

    # 3) Antecedents – separated by critical vs quick
    with g2col1:
        ant = df.groupby(['antecedent', 'Critical?'])['id'].count().reset_index()
        ant.rename(columns={'id': 'Count'}, inplace=True)
        fig_ant = px.bar(
            ant,
            x='Count',
            y='antecedent',
            color='Critical?',
            orientation='h',
            title='Top Antecedents (Triggers)'
        )
        fig_ant.update_layout(yaxis_title="Antecedent / trigger")
        st.plotly_chart(fig_ant, use_container_width=True)

    # 4) Locations – with critical overlay
    with g2col2:
        loc = df.groupby(['location', 'Critical?'])['id'].count().reset_index()
        loc.rename(columns={'id': 'Count'}, inplace=True)
        fig_loc = px.bar(
            loc,
            x='location',
            y='Count',
            color='Critical?',
            title='Incident Locations (Quick vs Critical)'
        )
        fig_loc.update_layout(xaxis_title="Location")
        st.plotly_chart(fig_loc, use_container_width=True)

    st.markdown("### 🧑‍🏫 Adult Responses & What Worked")

    g3col1, g3col2 = st.columns(2)

    # 5) Adult interventions frequency and severity
    with g3col1:
        interv = df.groupby(['intervention', 'Critical?'])['id'].count().reset_index()
        interv.rename(columns={'id': 'Count'}, inplace=True)
        fig_int = px.bar(
            interv,
            x='Count',
            y='intervention',
            color='Critical?',
            orientation='h',
            title='Adult Actions / Interventions Used'
        )
        fig_int.update_layout(yaxis_title="Intervention")
        st.plotly_chart(fig_int, use_container_width=True)

    # 6) Which interventions are associated with lower severity?
    with g3col2:
        eff = df.groupby('intervention')['severity'].mean().reset_index()
        eff.sort_values('severity', inplace=True)
        fig_eff = px.bar(
            eff,
            x='severity',
            y='intervention',
            orientation='h',
            title='Average Severity After Different Adult Responses'
        )
        fig_eff.update_layout(
            xaxis_title="Average severity (1–5)",
            yaxis_title="Intervention"
        )
        st.plotly_chart(fig_eff, use_container_width=True)

    # ------------------ NARRATIVE ANALYSIS & RECOMMENDATIONS ------------------ #

    st.markdown("---")
    st.markdown("### 🧠 Interpretation & Trauma-Informed Recommendations")

    # Key patterns
    top_antecedent = df['antecedent'].value_counts().idxmax()
    top_location = df['location'].value_counts().idxmax()
    top_session = df['session'].value_counts().idxmax()
    top_intervention = df['intervention'].value_counts().idxmax()

    critical_subset = df[df['is_critical']]
    critical_top_antecedent = critical_subset['antecedent'].value_counts().idxmax() if not critical_subset.empty else None
    critical_top_location = critical_subset['location'].value_counts().idxmax() if not critical_subset.empty else None

    st.markdown("#### Snapshot of Patterns")
    st.markdown(f"- **Most frequent antecedent overall:** `{top_antecedent}`")
    st.markdown(f"- **Most common location:** `{top_location}`")
    st.markdown(f"- **Most common time window:** `{top_session}`")
    st.markdown(f"- **Most used adult response:** `{top_intervention}`")

    if critical_top_antecedent:
        st.markdown(f"- **Critical incidents most often follow:** `{critical_top_antecedent}`")
    if critical_top_location:
        st.markdown(f"- **Critical incidents most often occur in:** `{critical_top_location}`")

    st.markdown("#### Trauma-Informed, Berry Street, SMART & CPI-Aligned Suggestions")

    st.markdown("""
- **Regulate – Relate – Reason (Trauma-informed & Berry Street Education Model):**  
  - Pre-empt incidents where the data shows spikes (for example in the **top session** or at the **top antecedent**).  
  - Build in co-regulation routines at those times: predictable greetings, movement/sensory breaks, and visual schedules that reduce uncertainty.
- **SMART & CPI – Safety First:**  
  - For patterns that become **critical** (severity ≥ 3), prioritise **environmental adjustments** before student-focused consequences (positioning, exits, proximity, access to regulation spaces).  
  - Continue to use the CPI emphasis on **calm, low-stimulus language** and **supportive stance**, particularly in locations flagged as higher risk.
- **Strengthening Adult Responses:**  
  - Interventions that are associated with **lower average severity** in the chart above can be named as “go-to” strategies for this student.  
  - Pair these with explicit scripts so all staff respond in similar ways (Berry Street consistency, CPI “team response”).
- **Re-designing Antecedents (Teaching for Transfer):**  
  - For high-frequency antecedents such as transitions or academic demands, explicitly teach **coping scripts** and **help-seeking behaviours** during calm times.  
  - Connect these to **Australian Curriculum General Capabilities** (e.g. Personal & Social Capability – self-management, Ethical Understanding – considering impact on others).
- **Post-Incident Repair & Learning:**  
  - Use the ABCH hypothesis section to capture the likely **function** of behaviour (to get/avoid attention, tasks, sensations or people).  
  - After regulation, complete a brief restorative check-in focused on: *what happened, who was impacted, and what needs to happen to make things safer next time*.  
  - Link goals back into the student’s **ILP / One Plan** so that behavioural learning is valued alongside literacy and numeracy.
- **Monitoring Change Over Time:**  
  - Revisit these graphs each review cycle to see whether critical incidents are moving towards quick, well-managed incidents, and whether certain antecedents or locations are becoming less risky.  
  - Use the data as evidence when planning reverse transitions, staffing, and when communicating with families and outside agencies.
""")

# ------------------ ADMIN PORTAL (SANDBOX, LIGHT) ------------------ #

@handle_errors("Unable to load admin portal")
def render_admin_portal():
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal – Sandbox")
        st.caption("Manage mock staff and students. Changes apply only in this sandbox session.")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')

    st.markdown("---")

    tab_staff, tab_students = st.tabs(["👥 Staff", "🎓 Students"])

    with tab_staff:
        st.markdown("### Current Staff")
        df_staff = pd.DataFrame(get_active_staff())
        if not df_staff.empty:
            st.dataframe(df_staff[['name', 'email', 'role']], use_container_width=True, hide_index=True)
        else:
            st.info("No staff loaded (sandbox).")

    with tab_students:
        st.markdown("### Current Students")
        df_students = pd.DataFrame([s for s in st.session_state.students_list if not s.get('archived', False)])
        if not df_students.empty:
            df_students_disp = df_students[['name', 'program', 'grade', 'edid', 'dob']]
            st.dataframe(df_students_disp, use_container_width=True, hide_index=True)
        else:
            st.info("No students loaded (sandbox).")

# =========================================================
# 9. MAIN
# =========================================================

def main():
    initialize_session_state()

    if not st.session_state.get('logged_in', False):
        render_login_page()
        return

    page = st.session_state.get('current_page', 'landing')

    if page == 'login':
        render_login_page()
    elif page == 'landing':
        render_landing_page()
    elif page == 'program_students':
        render_program_students()
    elif page == 'direct_log_form':
        render_direct_log_form()
    elif page == 'critical_incident_abch':
        render_critical_incident_abch_form()
    elif page == 'student_analysis':
        render_student_analysis()
    elif page == 'admin_portal':
        render_admin_portal()
    else:
        st.error("Unknown page – returning home.")
        st.session_state.current_page = 'landing'
        st.rerun()

if __name__ == "__main__":
    main()
