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

# --- ERROR HANDLING SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_errors.log'),
        logging.StreamHandler()
    ]
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
    """Decorator to catch and handle errors"""
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

# --- 1. CONFIGURATION AND CONSTANTS ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PLOTLY_THEME = 'plotly_dark'

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
]

MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'profile_status': 'Complete', 'program': 'SY', 'archived': False},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'profile_status': 'Draft', 'program': 'PY', 'archived': False},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'profile_status': 'Pending', 'program': 'SY', 'archived': False},
    {'id': 'stu_004', 'name': 'Emma T.', 'grade': 'R', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_005', 'name': 'Oliver S.', 'grade': 'Y2', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_006', 'name': 'Sophie M.', 'grade': 'Y5', 'profile_status': 'Complete', 'program': 'PY', 'archived': False},
    {'id': 'stu_arch_001', 'name': 'Jackson P.', 'grade': 'Y10', 'profile_status': 'Complete', 'program': 'SY', 'archived': True},
    {'id': 'stu_arch_002', 'name': 'Ava L.', 'grade': 'Y6', 'profile_status': 'Complete', 'program': 'PY', 'archived': True},
]

BEHAVIOR_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Other - Specify'] 

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
    "Used planned ignoring of minor behavior",
    "Staff de-escalation script/Verbal coaching",
    "Applied physical intervention",
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

VALID_PAGES = ['landing', 'program_students', 'direct_log_form', 'critical_incident_abch', 'student_analysis', 'admin_portal']

# --- MOCK DATA GENERATION ---

def generate_mock_incidents():
    """Generates mock incident data for testing."""
    incidents = []
    
    for i in range(15):
        incident_date = (datetime.now() - timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d')
        incident_time = datetime.now().replace(hour=random.randint(8, 14), minute=random.choice([0, 15, 30, 45]), second=0).time()
        
        if time(9, 0) <= incident_time <= time(11, 0):
            session = 'Morning (9:00am - 11:00am)'
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = 'Middle (11:01am - 1:00pm)'
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = 'Afternoon (1:01pm - 2:45pm)'
        else:
            session = 'Outside School Hours (N/A)'
        
        is_critical = random.choice([True, True, False])
        severity = random.choice([4, 5]) if is_critical else random.choice([1, 2, 3])
        
        incident = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_001',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M:%S'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': session,
            'location': random.choice(['JP Classroom', 'Yard', 'Gate', 'Playground', 'JP Spill Out']),
            'reported_by_name': 'Emily Jones (JP)',
            'reported_by_id': 's1',
            'behavior_type': random.choice(['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)']),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(SUPPORT_TYPES),
            'severity': severity,
            'description': f"Incident {i+1}",
            'is_critical': is_critical,
        }
        incidents.append(incident)
    
    for i in range(5):
        incident_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        incident_time = datetime.now().replace(hour=random.randint(8, 14), minute=random.choice([0, 15, 30, 45]), second=0).time()
        
        if time(9, 0) <= incident_time <= time(11, 0):
            session = 'Morning (9:00am - 11:00am)'
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = 'Middle (11:01am - 1:00pm)'
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = 'Afternoon (1:01pm - 2:45pm)'
        else:
            session = 'Outside School Hours (N/A)'
        
        incident = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_002',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M:%S'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': session,
            'location': random.choice(['PY Classroom', 'Library', 'Yard']),
            'reported_by_name': 'Daniel Lee (PY)',
            'reported_by_id': 's2',
            'behavior_type': random.choice(['Verbal Refusal', 'Out of Seat', 'Non-Compliance']),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(SUPPORT_TYPES),
            'severity': random.choice([1, 2, 3]),
            'description': f"Incident {i+1}",
            'is_critical': False,
        }
        incidents.append(incident)
    
    return incidents

if 'incidents' not in st.session_state:
    st.session_state.incidents = generate_mock_incidents()

# --- 2. GLOBAL HELPERS & CORE LOGIC FUNCTIONS ---

def navigate_to(page: str, student_id: Optional[str] = None, program: Optional[str] = None):
    """Changes the current page in session state."""
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
    """Safely retrieves student data."""
    try:
        if not student_id:
            return None
        return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None

def get_active_staff() -> List[Dict[str, Any]]:
    """Returns active staff."""
    try:
        return [s for s in MOCK_STAFF if s['active']]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []

def get_session_window(incident_time: time) -> str:
    """Calculates session window."""
    try:
        if time(9, 0) <= incident_time <= time(11, 0):
            return "Morning (9:00am - 11:00am)"
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            return "Middle (11:01am - 1:00pm)"
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            return "Afternoon (1:01pm - 2:45pm)"
        else:
            return "Outside School Hours (N/A)"
    except Exception as e:
        return "Unknown Session"

# --- VALIDATION FUNCTIONS ---

def validate_incident_form(location, reported_by, behavior_type, severity_level, incident_date, incident_time):
    """Validates incident form."""
    errors = []
    
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or reported_by.get('id') is None:
        errors.append("Please select a Staff Member")
    if behavior_type == "--- Select Behavior ---":
        errors.append("Please select a Behavior Type")
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")
    
    if errors:
        raise ValidationError("Form validation failed", "Please correct: " + ", ".join(errors))

def validate_abch_form(context, location, behavior_desc, consequence, manager_notify, parent_notify):
    """Validates ABCH form."""
    errors = []
    
    if not location or location.strip() == "":
        errors.append("Location is required")
    if not context or context.strip() == "":
        errors.append("Context is required")
    if not behavior_desc or behavior_desc.strip() == "":
        errors.append("Behavior description is required")
    if not consequence or consequence.strip() == "":
        errors.append("Consequences are required")
    if not manager_notify:
        errors.append("Line Manager notification required")
    if not parent_notify:
        errors.append("Parent notification required")
    
    if errors:
        raise ValidationError("ABCH validation failed", "Please correct: " + ", ".join(errors))

# --- LANDING PAGE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    """Renders sleek landing page."""
    
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #888;
        margin-bottom: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">Behaviour Support & Data Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Select a program to view students or access quick actions</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📚 Select Program")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Junior Primary")
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='JP')
    
    with col2:
        st.markdown("#### Primary Years")
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='PY')
    
    with col3:
        st.markdown("#### Senior Years")
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='SY')
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col_quick1, col_quick2 = st.columns(2)
    
    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        all_active_students = [s for s in MOCK_STUDENTS if not s.get('archived', False)]
        student_options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x['name'],
            key="quick_log_student"
        )
        
        if selected_student and selected_student['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to('direct_log_form', student_id=selected_student['id'])
    
    with col_quick2:
        st.markdown("#### 🔐 Admin Portal")
        st.markdown("System administration and reports")
        if st.button("Access Admin Portal", key="admin_btn", use_container_width=True, type="primary"):
            navigate_to('admin_portal')

# --- PROGRAM STUDENTS PAGE ---

@handle_errors("Unable to load program students")
def render_program_students():
    """Renders student list for selected program."""
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
        current_students = [s for s in MOCK_STUDENTS if s.get('program') == program and not s.get('archived', False)]
        
        if not current_students:
            st.info(f"No current students in the {program} program.")
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
                            
                            incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                            st.metric("Incidents", incident_count)
                            
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button("👁️ View", key=f"view_{student['id']}", use_container_width=True):
                                    navigate_to('student_analysis', student_id=student['id'])
                            with col_log:
                                if st.button("📝 Log", key=f"log_{student['id']}", use_container_width=True):
                                    navigate_to('direct_log_form', student_id=student['id'])
    
    with tab2:
        archived_students = [s for s in MOCK_STUDENTS if s.get('program') == program and s.get('archived', False)]
        
        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("Students who have completed the program - read-only")
            
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**Profile Status:** {student.get('profile_status', 'N/A')}")
                    
                    incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                    st.metric("Total Incidents", incident_count)
                    
                    if st.button("View Historical Data", key=f"view_arch_{student['id']}"):
                        navigate_to('student_analysis', student_id=student['id'])

# --- Placeholder for other render functions (keeping structure minimal for now) ---

def render_direct_log_form():
    st.title("Direct Log Form")
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)
    
    if student:
        st.markdown(f"## Logging incident for: **{student['name']}**")
        if st.button("⬅ Back"):
            navigate_to('landing')
        st.info("Incident log form will be rendered here")
    else:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')

def render_critical_incident_abch_form():
    st.title("Critical Incident Form")
    if st.button("⬅ Back"):
        navigate_to('landing')
    st.info("Critical incident ABCH form rendered here")

def render_student_analysis():
    st.title("Student Analysis")
    if st.button("⬅ Back"):
        navigate_to('landing')
    st.info("Student analysis and data will be shown here")

# --- MAIN ---

def main():
    """Main application logic."""
    
    try:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'landing'
            
        current_page = st.session_state.get('current_page', 'landing')
        
        if current_page == 'landing':
            render_landing_page()
        elif current_page == 'program_students':
            render_program_students()
        elif current_page == 'direct_log_form':
            render_direct_log_form()
        elif current_page == 'critical_incident_abch':
            render_critical_incident_abch_form()
        elif current_page == 'student_analysis':
            render_student_analysis()
        elif current_page == 'admin_portal':
            st.title("🔐 Admin Portal")
            st.info("Admin portal - to be implemented")
            if st.button("⬅ Back"):
                navigate_to('landing')
        else:
            st.error("Unknown page")
            navigate_to('landing')
            
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        st.error("A critical error occurred.")

if __name__ == '__main__':
    main()
