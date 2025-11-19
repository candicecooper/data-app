import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
from typing import List, Dict, Any, Optional
import logging
from functools import wraps

# --------------------------------------------------
# 1. BASIC CONFIG & LOGGING
# --------------------------------------------------

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool - SANDBOX",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(AppError):
    """Raised when data validation fails"""
    pass

def handle_errors(user_message: str = "An error occurred"):
    """Decorator to catch and handle errors and show friendly messages in the UI."""
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
                st.error(f"{user_message}. Please try again.")
                with st.expander("Error details"):
                    st.code(str(e))
                return None
        return wrapper
    return decorator

PLOTLY_THEME = "plotly"
VALID_PAGES = [
    "login",
    "landing",
    "program_students",
    "direct_log_form",
    "critical_incident_abch",
    "student_analysis",
    "admin_portal",
]

# --------------------------------------------------
# 2. CONSTANTS & MOCK DATA
# --------------------------------------------------

STAFF_ROLES = ['JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO']

PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

GRADE_OPTIONS = {
    'JP': ['R', 'Y1', 'Y2'],
    'PY': ['Y3', 'Y4', 'Y5', 'Y6'],
    'SY': ['Y7', 'Y8', 'Y9', 'Y10', 'Y11', 'Y12'],
}

BEHAVIOUR_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']
BEHAVIOURS_FBA = [
    'Verbal Refusal',
    'Elopement',
    'Property Destruction',
    'Aggression (Peer)',
    'Other - Specify',
]

ANTECEDENTS_NEW = [
    "Requested to transition activity",
    "Given instruction/demand (Academic)",
    "Given instruction/demand (Non-Academic)",
    "Peer conflict/Teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory over-stimulation (Noise/Lights)",
    "Access to preferred item/activity denied",
]

INTERVENTIONS = [
    "Prompted use of coping skill (e.g., breathing)",
    "Proximity control/Non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break/Choice of task",
    "Used planned ignoring of minor behaviour",
    "Staff de-escalation script/Verbal coaching",
    "Removed other students from area for safety",
    "Called for staff support/Backup",
]

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class/assembly)",
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
    "Other",
]


def generate_mock_students() -> List[Dict[str, Any]]:
    """Generate mock students for SANDBOX."""
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
    """Generate mock staff for SANDBOX."""
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


def generate_mock_incidents() -> List[Dict[str, Any]]:
    """Generate ~60 mock incidents with realistic patterns for SANDBOX."""
    incidents = []
    student_ids = [
        'student_JP001', 'student_JP002', 'student_JP003',
        'student_PY001', 'student_PY002', 'student_PY003',
        'student_SY001', 'student_SY002', 'student_SY003',
    ]
    staff_names = [
        'Sarah Johnson', 'Michael Lee', 'Jessica Williams',
        'David Martinez', 'Emily Brown', 'James Wilson',
    ]
    behaviours = [
        'Verbal Refusal',
        'Elopement',
        'Property Destruction',
        'Aggression (Peer)',
        'Physical Aggression (Staff)',
    ]
    locations = [
        'JP Classroom', 'PY Classroom', 'SY Classroom',
        'Yard', 'Playground', 'Library',
    ]

    base_date = datetime.now() - timedelta(days=90)

    for i in range(65):
        student_id = random.choice(student_ids)
        inc_date = base_date + timedelta(days=random.randint(0, 85))

        # bias times towards school hours
        hour = random.choices(
            [9, 10, 11, 12, 13, 14],
            weights=[2, 3, 2, 1, 2, 3],
        )[0]
        minute = random.randint(0, 59)
        inc_time = time(hour=hour, minute=minute)

        # numeric severity (1–5) but weighted to milder
        severity = random.choices(
            [1, 2, 3, 4, 5],
            weights=[5, 3, 2, 1, 0.5],
        )[0]

        def session_window(t: time) -> str:
            if time(9, 0) <= t <= time(11, 0):
                return "Morning (9:00am - 11:00am)"
            elif time(11, 0, 1) <= t <= time(13, 0):
                return "Middle (11:01am - 1:00pm)"
            elif time(13, 0, 1) <= t <= time(14, 45):
                return "Afternoon (1:01pm - 2:45pm)"
            else:
                return "Outside School Hours (N/A)"

        incidents.append({
            'id': f'inc_{i+1}',
            'student_id': student_id,
            'student_name': next(
                s['name'] for s in generate_mock_students() if s['id'] == student_id
            ),
            'incident_date': inc_date.strftime('%Y-%m-%d'),
            'date': inc_date.strftime('%Y-%m-%d'),
            'incident_time': inc_time.strftime('%H:%M:%S'),
            'time': inc_time.strftime('%H:%M:%S'),
            'day_of_week': inc_date.strftime('%A'),
            'day': inc_date.strftime('%A'),
            'session': session_window(inc_time),
            'location': random.choice(locations),
            'reported_by_name': random.choice(staff_names),
            'reported_by_role': random.choice(['JP', 'PY', 'SY']),
            'behaviour_type': random.choice(behaviours),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(['1:1 (Individual Support)', 'Small Group (3-5 students)']),
            'severity': severity,
            'description': 'Mock incident for SANDBOX demo.',
            'is_critical': severity >= 3,  # threshold for critical in sandbox
        })

    return incidents


# --------------------------------------------------
# 3. SESSION STATE INITIALISATION
# --------------------------------------------------

def initialize_session_state():
    """Set up all session_state for SANDBOX mode."""
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading SANDBOX data..."):
            st.session_state.students_list = generate_mock_students()
            st.session_state.staff_list = generate_mock_staff()
            st.session_state.incidents = generate_mock_incidents()
            st.session_state.system_settings = {}
            st.session_state.data_loaded = True

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'critical_abch_records' not in st.session_state:
        st.session_state.critical_abch_records = []
    if 'current_incident_for_abch' not in st.session_state:
        st.session_state.current_incident_for_abch = None


# --------------------------------------------------
# 4. HELPERS
# --------------------------------------------------

def navigate_to(page: str, student_id: Optional[str] = None, program: Optional[str] = None):
    """Simple page navigation via session_state."""
    if page not in VALID_PAGES:
        raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")

    st.session_state.current_page = page
    if student_id:
        st.session_state.selected_student_id = student_id
    if program:
        st.session_state.selected_program = program
    st.rerun()


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    try:
        return next((s for s in st.session_state.students_list if s['id'] == student_id), None)
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None


def get_active_staff() -> List[Dict[str, Any]]:
    try:
        return [s for s in st.session_state.staff_list if s['active'] and not s.get('archived', False)]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []


def get_students_by_program(program: str, include_archived: bool = False) -> List[Dict[str, Any]]:
    try:
        students = [s for s in st.session_state.students_list if s.get('program') == program]
        if not include_archived:
            students = [s for s in students if not s.get('archived', False)]
        return students
    except Exception as e:
        logger.error(f"Error retrieving students by program: {e}")
        return []


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


# --------------------------------------------------
# 5. AUTH (SANDBOX)
# --------------------------------------------------

def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    SANDBOX login:
    - email must match a mock staff email
    - password must be 'demo'
    """
    try:
        if not email or not email.strip():
            return None
        if password != "demo":
            return None

        email = email.strip().lower()
        staff_member = next(
            (s for s in generate_mock_staff()
             if s.get('email', '').lower() == email and not s.get('archived', False)),
            None
        )
        return staff_member
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None


# --------------------------------------------------
# 6. VALIDATION
# --------------------------------------------------

def validate_incident_form(location, reported_by, behaviour_type, severity_level, incident_date, incident_time):
    errors = []
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or reported_by.get('id') is None:
        errors.append("Please select a Staff Member")
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


def validate_abch_form(context, location, behaviour_desc, consequence, hypothesis, manager_notify, parent_notify):
    """Validates ABCH form row."""
    errors = []
    if not location or location.strip() == "":
        errors.append("Location is required")
    if not context or context.strip() == "":
        errors.append("Context is required")
    if not behaviour_desc or behaviour_desc.strip() == "":
        errors.append("Behaviour description is required")
    if not consequence or consequence.strip() == "":
        errors.append("Consequences are required")
    if not hypothesis or hypothesis.strip() == "":
        errors.append("Hypothesis (behaviour function) is required")
    if not manager_notify:
        errors.append("Line Manager notification must be ticked")
    if not parent_notify:
        errors.append("Parent/Carer notification must be ticked")

    if errors:
        raise ValidationError("ABCH validation failed", "Please correct: " + ", ".join(errors))


# --------------------------------------------------
# 7. SMALL COMPONENTS
# --------------------------------------------------

def render_staff_selector(label: str = "Staff Member", key: str = "staff_selector", include_special_options: bool = True):
    """
    Staff dropdown with optional TRT / External SSO options.
    Returns a dict describing the selected staff.
    """
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
        format_func=lambda x: f"{x['name']}" + (f" ({x['role']})" if x['role'] and not x.get('special') else ""),
        key=key
    )

    if selected and selected.get('special'):
        st.markdown(f"**{selected['name']} selected** – please enter their name:")
        specific_name = st.text_input(
            f"Enter {selected['role']} Name",
            key=f"{key}_specific_name",
            placeholder=f"Full name of {selected['role']}",
        )
        if specific_name and specific_name.strip():
            return {
                'id': selected['id'],
                'name': specific_name.strip(),
                'role': selected['role'],
                'is_special': True,
            }
        else:
            return {
                'id': selected['id'],
                'name': f"{selected['role']} (Name Required)",
                'role': selected['role'],
                'is_special': True,
                'name_missing': True,
            }

    return selected


# --------------------------------------------------
# 8. PAGES
# --------------------------------------------------

# --- LOGIN PAGE ---

@handle_errors("Unable to load login page")
def render_login_page():
    st.markdown("""
<div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            padding: 1rem; border-radius: 10px; text-align: center;
            margin-bottom: 1rem; color: white;">
  <h2 style="margin:0;">🎭 SANDBOX MODE – Sample Data Only</h2>
  <p style="margin:0.4rem 0 0 0;">This environment uses synthetic data only. No real student information is stored.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">🔐</div>
        <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
        <p class="hero-subtitle">Staff Login</p>
        <p class="hero-tagline">Use your demo email and password <b>demo</b> to access the sandbox.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### 🔑 Login")

            email = st.text_input(
                "Email Address",
                placeholder="sarah.johnson@demo.edu.au",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="demo",
                key="login_password",
            )

            if st.button("🚀 Login", type="primary", use_container_width=True):
                if email and password:
                    staff_member = verify_login(email, password)
                    if staff_member:
                        st.session_state.logged_in = True
                        st.session_state.current_user = staff_member
                        st.session_state.current_page = "landing"
                        st.success(f"✅ Welcome back, {staff_member['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password for SANDBOX (password is 'demo').")
                else:
                    st.warning("⚠️ Please enter both email and password")


# --- LANDING PAGE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        cu = st.session_state.get("current_user", {})
        st.markdown(f"### 👋 Welcome, {cu.get('name', 'User')}!")
        st.caption(f"Role: {cu.get('role', 'N/A')} | {cu.get('email', 'N/A')}")
    with col_logout:
        st.markdown("##")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = "login"
            st.rerun()

    st.markdown("---")

    st.markdown("""
    <div style="text-align:center; padding:2rem; border-radius:20px;
                background:rgba(255,255,255,0.15); backdrop-filter:blur(16px);
                box-shadow:0 20px 40px rgba(0,0,0,0.25); margin-bottom:2rem;">
      <div style="font-size:4rem; margin-bottom:0.5rem;">📊✨</div>
      <h1 style="font-size:2.4rem; margin:0;">Behaviour Support & Data Analysis</h1>
      <p style="margin:0.5rem 0 0 0;">Track incidents, analyse patterns, and record ABCH data – safely in SANDBOX mode.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 Select Your Program")
    st.caption("Choose a program to view students, log incidents, and access analytics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎨 Junior Primary")
        st.caption("Reception – Year 2")
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to("program_students", program="JP")

    with col2:
        st.markdown("#### 📖 Primary Years")
        st.caption("Year 3 – Year 6")
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to("program_students", program="PY")

    with col3:
        st.markdown("#### 🎓 Senior Years")
        st.caption("Year 7 – Year 12")
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to("program_students", program="SY")

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    st.caption("Fast access to common tasks")

    col_quick1, col_quick2 = st.columns(2)
    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        all_active_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        student_options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x['name'],
            key="quick_log_student",
            label_visibility="collapsed",
        )
        if selected_student and selected_student['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to("direct_log_form", student_id=selected_student['id'])

    with col_quick2:
        st.markdown("#### 🔐 Admin Portal")
        st.caption("View sandbox staff and student lists")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Access Admin Portal", key="admin_btn", use_container_width=True, type="primary"):
            navigate_to("admin_portal")


# --- PROGRAM STUDENT LIST ---

@handle_errors("Unable to load program students")
def render_program_students():
    program = st.session_state.get("selected_program", "JP")

    col_title, col_back = st.columns([4, 1])
    with col_title:
        names = {'JP': 'Junior Primary', 'PY': 'Primary Years', 'SY': 'Senior Years'}
        st.title(f"{names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to("landing")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📚 Current Students", "📦 Archived Students"])
    with tab1:
        current_students = get_students_by_program(program, include_archived=False)
        if not current_students:
            st.info(f"No current students in the {program} program.")
        else:
            st.markdown(f"### Current Students ({len(current_students)})")
            cols_per_row = 3
            for i in range(0, len(current_students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, stu in enumerate(current_students[i:i+cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {stu['name']}")
                            st.markdown(f"**Grade:** {stu['grade']}")
                            st.caption(f"EDID: {stu.get('edid', 'N/A')}")
                            inc_count = len([inc for inc in st.session_state.incidents if inc.get('student_id') == stu['id']])
                            st.metric("Incidents", inc_count)

                            col_v, col_l = st.columns(2)
                            with col_v:
                                if st.button("👁️ View", key=f"view_{stu['id']}", use_container_width=True):
                                    navigate_to("student_analysis", student_id=stu['id'])
                            with col_l:
                                if st.button("📝 Log", key=f"log_{stu['id']}", use_container_width=True):
                                    navigate_to("direct_log_form", student_id=stu['id'])

    with tab2:
        archived = [s for s in st.session_state.students_list if s.get('program') == program and s.get('archived', False)]
        if not archived:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived)})")
            for stu in archived:
                with st.expander(f"📦 {stu['name']} – Grade {stu['grade']}"):
                    st.markdown(f"**Profile Status:** {stu.get('profile_status', 'N/A')}")
                    st.markdown(f"**EDID:** {stu.get('edid', 'N/A')}")
                    inc_count = len([inc for inc in st.session_state.incidents if inc.get('student_id') == stu['id']])
                    st.metric("Total Incidents", inc_count)
                    if st.button("View Historical Data", key=f"view_arch_{stu['id']}"):
                        navigate_to("student_analysis", student_id=stu['id'])


# --- ADMIN PORTAL (read-only-ish in sandbox) ---

@handle_errors("Unable to load admin portal")
def render_admin_portal():
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal (SANDBOX)")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to("landing")

    st.markdown("---")
    tab1, tab2 = st.tabs(["👥 Staff", "🎓 Students"])

    with tab1:
        st.markdown("### Current Staff (mock)")
        df = pd.DataFrame([
            {
                "Name": s['name'],
                "Email": s['email'],
                "Role": s['role'],
                "Active": s['active'],
            }
            for s in st.session_state.staff_list
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Current Students (mock)")
        df = pd.DataFrame([
            {
                "Name": s['name'],
                "Program": s['program'],
                "Grade": s['grade'],
                "EDID": s['id'],
                "DOB": s['dob'],
                "Age": calculate_age(s['dob']),
            }
            for s in st.session_state.students_list
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)


# --- DIRECT INCIDENT LOG ---

@handle_errors("Unable to load incident form")
def render_direct_log_form():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student not found.")
        if st.button("Return Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student['program'])

    st.markdown("---")

    with st.form("incident_form"):
        st.markdown("### Incident Details")
        col1, col2 = st.columns(2)
        with col1:
            incident_date = st.date_input("Date of Incident (DD/MM/YYYY)", value=datetime.now(), format="DD/MM/YYYY")
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)
        with col2:
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True,
            )

        st.markdown("### Behaviour Information")
        col3, col4 = st.columns(2)
        with col3:
            behaviour_type = st.selectbox(
                "Behaviour Type",
                options=["--- Select behaviour ---"] + BEHAVIOURS_FBA,
            )
            antecedent = st.selectbox("Antecedent", options=ANTECEDENTS_NEW)
        with col4:
            intervention = st.selectbox("Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)

        severity_level = st.slider("Severity Level", 1, 5, 2)
        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional context about the incident...",
            height=100,
        )

        submitted = st.form_submit_button("Submit Incident Report", type="primary", use_container_width=True)

        if submitted:
            if reported_by and reported_by.get('name_missing'):
                st.error("Please enter the name for the selected staff type (TRT or External SSO).")
                return

            validate_incident_form(
                location, reported_by, behaviour_type,
                severity_level, incident_date, incident_time,
            )

            new_incident = {
                'id': f"sandbox_{uuid.uuid4().hex[:8]}",
                'student_id': student_id,
                'student_name': student['name'],
                'incident_date': incident_date.strftime('%Y-%m-%d'),
                'date': incident_date.strftime('%Y-%m-%d'),
                'incident_time': incident_time.strftime('%H:%M:%S'),
                'time': incident_time.strftime('%H:%M:%S'),
                'day_of_week': incident_date.strftime('%A'),
                'day': incident_date.strftime('%A'),
                'session': "N/A",  # could re-use the session window logic if you like
                'location': location,
                'reported_by_name': reported_by['name'],
                'reported_by_role': reported_by['role'],
                'behaviour_type': behaviour_type,
                'antecedent': antecedent,
                'intervention': intervention,
                'support_type': support_type,
                'severity': severity_level,
                'description': description,
                'is_critical': severity_level >= 3,   # <=— SANDBOX CRITICAL THRESHOLD
            }

            # Save to sandbox "DB" (session state)
            st.session_state.incidents.append(new_incident)

            if severity_level >= 3:
                st.session_state.current_incident_for_abch = new_incident
                st.warning("⚠️ Severity is 3 or above – opening Critical Incident ABCH form.")
                navigate_to("critical_incident_abch", student_id=student_id)
            else:
                st.success("✅ Incident report submitted (non-critical).")
                col_another, col_return = st.columns(2)
                with col_another:
                    if st.button("➕ Log Another Incident", use_container_width=True):
                        st.rerun()
                with col_return:
                    if st.button("↩️ Return to Student List", use_container_width=True):
                        navigate_to("program_students", program=student['program'])


# --- CRITICAL INCIDENT ABCH FORM ---

@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    incident = st.session_state.get("current_incident_for_abch")
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id) if student_id else None

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🚨 Critical Incident ABCH Form")
        if student:
            st.caption(f"Student: {student['name']} | Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            if student:
                navigate_to("student_analysis", student_id=student_id)
            else:
                navigate_to("landing")

    st.markdown("---")

    if not incident:
        st.info("No triggering incident found in context. Please log a critical incident first.")
        return

    with st.expander("📌 Incident Snapshot", expanded=True):
        st.markdown(f"**Date:** {incident.get('incident_date')}")
        st.markdown(f"**Time:** {incident.get('incident_time')}")
        st.markdown(f"**Location:** {incident.get('location')}")
        st.markdown(f"**Reported by:** {incident.get('reported_by_name')} ({incident.get('reported_by_role')})")
        st.markdown(f"**Behaviour:** {incident.get('behaviour_type')}")
        st.markdown(f"**Severity:** {incident.get('severity')}")
        if incident.get('description'):
            st.markdown(f"**Description:** {incident.get('description')}")

    st.markdown("### ABCH Row (matches your paper template)")
    st.caption("Fill each column from left to right – this is one row: Location | Context | Time | Behaviour | Consequences | Hypothesis")

    default_time = None
    try:
        if incident.get('incident_time'):
            default_time = datetime.strptime(incident['incident_time'], '%H:%M:%S').time()
    except Exception:
        pass
    if default_time is None:
        default_time = datetime.now().time()

    with st.form("abch_form"):
        col_loc, col_ctx, col_time, col_beh, col_conseq, col_hyp = st.columns([1.1, 2.2, 0.9, 2.2, 2.2, 2.2])

        with col_loc:
            location = st.text_input(
                "Location",
                value=incident.get('location', ''),
                help="Where did the behaviour occur? e.g. Student Gate, Yard, JP Classroom",
            )

        with col_ctx:
            context = st.text_area(
                "Context (what was going on before the behaviour? What was being said and done?)",
                height=120,
            )

        with col_time:
            time_of_behaviour = st.time_input(
                "Time",
                value=default_time,
                help="Approximate time of the behaviour",
            )

        with col_beh:
            behaviour_desc = st.text_area(
                "What did the student do? (Observed behaviour)",
                height=120,
            )

        with col_conseq:
            consequence = st.text_area(
                "What happened after the behaviour? How did people react?",
                height=120,
            )

        with col_hyp:
            hypothesis = st.text_area(
                "Hypothesis – best guess of behaviour function\n(To Get or Avoid → tangible / request / activity / sensory / attention / other)",
                height=120,
            )

        st.markdown("---")
        col_flags1, col_flags2 = st.columns(2)
        with col_flags1:
            manager_notify = st.checkbox("Line Manager notified")
        with col_flags2:
            parent_notify = st.checkbox("Parent/Carer notified")

        submitted = st.form_submit_button("Save ABCH Record", type="primary", use_container_width=True)

        if submitted:
            validate_abch_form(
                context=context,
                location=location,
                behaviour_desc=behaviour_desc,
                consequence=consequence,
                hypothesis=hypothesis,
                manager_notify=manager_notify,
                parent_notify=parent_notify,
            )

            abch_record = {
                'id': f"abch_{uuid.uuid4().hex[:8]}",
                'incident_id': incident.get('id'),
                'student_id': student_id,
                'location': location,
                'context': context,
                'time': time_of_behaviour.strftime('%H:%M:%S'),
                'behaviour_desc': behaviour_desc,
                'consequence': consequence,
                'hypothesis': hypothesis,
                'manager_notify': manager_notify,
                'parent_notify': parent_notify,
                'created_at': datetime.now().isoformat(),
            }

            st.session_state.critical_abch_records.append(abch_record)
            st.success("✅ Critical Incident ABCH record saved.")
            st.info("This ABCH row matches your paper layout: Location | Context | Time | Behaviour | Consequences | Hypothesis.")


# --- STUDENT ANALYSIS ---

@handle_errors("Unable to load student analysis")
def render_student_analysis():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found.")
        if st.button("Return Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student['program'])

    st.markdown("---")

    student_incidents = [inc for inc in st.session_state.incidents if inc.get('student_id') == student_id]
    if not student_incidents:
        st.info("No incident data available for this student yet.")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to("direct_log_form", student_id=student_id)
        return

    # Summary metrics
    st.markdown("### 📈 Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Incidents", len(student_incidents))
    with col2:
        critical_count = len([inc for inc in student_incidents if inc.get('is_critical', False)])
        perc = (critical_count / len(student_incidents) * 100) if student_incidents else 0
        st.metric("Critical (≥3)", critical_count, f"{perc:.0f}%")
    with col3:
        avg_sev = sum(inc.get('severity', 0) for inc in student_incidents) / len(student_incidents)
        st.metric("Avg Severity", f"{avg_sev:.1f}")
    with col4:
        dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in student_incidents]
        span = (max(dates) - min(dates)).days + 1 if dates else 1
        st.metric("Days Tracked", span)
    with col5:
        per_week = (len(student_incidents) / span) * 7 if span > 0 else 0
        st.metric("Incidents / Week", f"{per_week:.1f}")

    st.markdown("---")
    df = pd.DataFrame(student_incidents)

    # Ensure Date column
    if 'incident_date' in df.columns:
        df['Date'] = pd.to_datetime(df['incident_date'])
    else:
        df['Date'] = pd.to_datetime(df['date'])

    # Charts
    st.markdown("### Visual Patterns")

    # 1. Timeline
    with st.container():
        daily = df.groupby('Date').size().reset_index(name='Count')
        fig = px.line(daily, x='Date', y='Count', title="Incidents Over Time", template=PLOTLY_THEME, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Behaviour frequency
        if 'behaviour_type' in df.columns:
            beh_counts = df['behaviour_type'].value_counts().reset_index()
            beh_counts.columns = ['Behaviour', 'Count']
            fig = px.bar(
                beh_counts,
                x='Count',
                y='Behaviour',
                orientation='h',
                title="Behaviour Frequency",
                template=PLOTLY_THEME,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Day of week
        if 'day' in df.columns or 'day_of_week' in df.columns:
            if 'day' in df.columns:
                df['Day'] = df['day']
            else:
                df['Day'] = df['day_of_week']
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts = df['Day'].value_counts().reindex(day_order).dropna().reset_index()
            day_counts.columns = ['Day', 'Count']
            fig = px.bar(day_counts, x='Day', y='Count', title="Incidents by Day of Week", template=PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)

    # Locations
    if 'location' in df.columns:
        loc_counts = df['location'].value_counts().reset_index()
        loc_counts.columns = ['Location', 'Count']
        fig = px.bar(
            loc_counts.head(10),
            x='Count',
            y='Location',
            orientation='h',
            title="Top Incident Locations",
            template=PLOTLY_THEME,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### ABCH Rows for this Student (if completed)")
    abch_rows = [r for r in st.session_state.critical_abch_records if r.get('student_id') == student_id]
    if not abch_rows:
        st.info("No ABCH rows recorded yet for this student.")
    else:
        df_abch = pd.DataFrame([
            {
                "Location": r['location'],
                "Context": r['context'],
                "Time": r['time'],
                "Behaviour": r['behaviour_desc'],
                "Consequences": r['consequence'],
                "Hypothesis": r['hypothesis'],
                "Manager Notified": "Yes" if r['manager_notify'] else "No",
                "Parent Notified": "Yes" if r['parent_notify'] else "No",
                "Recorded": r['created_at'].split("T")[0],
            }
            for r in abch_rows
        ])
        st.dataframe(df_abch, use_container_width=True, hide_index=True)


# --------------------------------------------------
# 9. MAIN
# --------------------------------------------------

def main():
    initialize_session_state()

    if not st.session_state.get("logged_in", False):
        render_login_page()
        return

    page = st.session_state.get("current_page", "landing")

    if page == "login":
        render_login_page()
    elif page == "landing":
        render_landing_page()
    elif page == "program_students":
        render_program_students()
    elif page == "direct_log_form":
        render_direct_log_form()
    elif page == "critical_incident_abch":
        render_critical_incident_abch_form()
    elif page == "student_analysis":
        render_student_analysis()
    elif page == "admin_portal":
        render_admin_portal()
    else:
        st.error("Unknown page.")
        navigate_to("landing")


if __name__ == "__main__":
    main()
