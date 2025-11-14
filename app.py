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
    {'id': 's1', 'name': 'Emily Jones', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's2', 'name': 'Daniel Lee', 'role': 'PY', 'active': True, 'archived': False},
    {'id': 's3', 'name': 'Sarah Chen', 'role': 'SY', 'active': True, 'archived': False},
    {'id': 's4', 'name': 'Admin User', 'role': 'ADM', 'active': True, 'archived': False},
    {'id': 's5', 'name': 'Michael Torres', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's6', 'name': 'Jessica Williams', 'role': 'PY', 'active': True, 'archived': False},
]

# Staff roles available
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

# Program options
PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

# Grade options by program
GRADE_OPTIONS = {
    'JP': ['R', 'Y1', 'Y2'],
    'PY': ['Y3', 'Y4', 'Y5', 'Y6'],
    'SY': ['Y7', 'Y8', 'Y9', 'Y10', 'Y11', 'Y12']
}

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
            'reported_by_name': 'Emily Jones',
            'reported_by_id': 's1',
            'reported_by_role': 'JP',
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
            'reported_by_name': 'Daniel Lee',
            'reported_by_id': 's2',
            'reported_by_role': 'PY',
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

# --- SESSION STATE INITIALIZATION ---

def initialize_session_state():
    """Initialize all session state variables"""
    if 'incidents' not in st.session_state:
        st.session_state.incidents = generate_mock_incidents()
    
    if 'staff_list' not in st.session_state:
        st.session_state.staff_list = MOCK_STAFF.copy()
    
    if 'students_list' not in st.session_state:
        st.session_state.students_list = MOCK_STUDENTS.copy()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'

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
        return next((s for s in st.session_state.students_list if s['id'] == student_id), None)
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None

def get_active_staff() -> List[Dict[str, Any]]:
    """Returns active, non-archived staff."""
    try:
        return [s for s in st.session_state.staff_list if s['active'] and not s.get('archived', False)]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []

def get_staff_by_id(staff_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves staff member by ID."""
    try:
        if not staff_id:
            return None
        return next((s for s in st.session_state.staff_list if s['id'] == staff_id), None)
    except Exception as e:
        logger.error(f"Error retrieving staff member: {e}")
        return None

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

def add_staff_member(name: str, role: str) -> bool:
    """Adds a new staff member."""
    try:
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty", "Please enter a staff name")
        
        if not role or role == "--- Select Role ---":
            raise ValidationError("Role must be selected", "Please select a role")
        
        # Check for duplicate names
        existing = [s for s in st.session_state.staff_list if s['name'].lower() == name.strip().lower() and not s.get('archived', False)]
        if existing:
            raise ValidationError("Duplicate staff name", "A staff member with this name already exists")
        
        new_staff = {
            'id': f"s_{uuid.uuid4().hex[:8]}",
            'name': name.strip(),
            'role': role,
            'active': True,
            'archived': False,
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        st.session_state.staff_list.append(new_staff)
        logger.info(f"Added staff member: {name} ({role})")
        return True
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding staff: {e}")
        raise AppError("Failed to add staff member", "Could not add staff member. Please try again.")

def archive_staff_member(staff_id: str) -> bool:
    """Archives a staff member."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot archive: staff member not found")
        
        staff['archived'] = True
        staff['active'] = False
        staff['archived_date'] = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Archived staff member: {staff['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Error archiving staff: {e}")
        raise AppError("Failed to archive staff member", "Could not archive staff member. Please try again.")

def unarchive_staff_member(staff_id: str) -> bool:
    """Unarchives a staff member."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot unarchive: staff member not found")
        
        staff['archived'] = False
        staff['active'] = True
        
        logger.info(f"Unarchived staff member: {staff['name']}")
        return True
        
    except Exception as e:
        logger.error(f"Error unarchiving staff: {e}")
        raise AppError("Failed to unarchive staff member", "Could not unarchive staff member. Please try again.")

def add_student(name: str, dob: datetime.date, program: str, grade: str, edid: str) -> bool:
    """Adds a new student."""
    try:
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty", "Please enter a student name")
        
        if not program or program == "--- Select Program ---":
            raise ValidationError("Program must be selected", "Please select a program")
        
        if not grade or grade == "--- Select Grade ---":
            raise ValidationError("Grade must be selected", "Please select a grade")
        
        if not dob:
            raise ValidationError("Date of birth is required", "Please enter date of birth")
        
        if not edid or not edid.strip():
            raise ValidationError("EDID is required", "Please enter EDID")
        
        # Check for duplicate EDID
        existing_edid = [s for s in st.session_state.students_list if s.get('edid', '').upper() == edid.strip().upper() and not s.get('archived', False)]
        if existing_edid:
            raise ValidationError("Duplicate EDID", f"A student with EDID {edid} already exists")
        
        # Validate DOB is not in the future
        if dob > datetime.now().date():
            raise ValidationError("Invalid date of birth", "Date of birth cannot be in the future")
        
        new_student = {
            'id': f"stu_{uuid.uuid4().hex[:8]}",
            'name': name.strip(),
            'dob': dob.strftime('%Y-%m-%d'),
            'program': program,
            'grade': grade,
            'edid': edid.strip().upper(),
            'profile_status': 'Draft',
            'archived': False,
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        st.session_state.students_list.append(new_student)
        logger.info(f"Added student: {name} (EDID: {edid}, Program: {program})")
        return True
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        raise AppError("Failed to add student", "Could not add student. Please try again.")

def get_students_by_program(program: str, include_archived: bool = False) -> List[Dict[str, Any]]:
    """Gets all students for a specific program."""
    try:
        students = st.session_state.students_list
        filtered = [s for s in students if s.get('program') == program]
        
        if not include_archived:
            filtered = [s for s in filtered if not s.get('archived', False)]
        
        return filtered
    except Exception as e:
        logger.error(f"Error retrieving students by program: {e}")
        return []

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
        all_active_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
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
        current_students = get_students_by_program(program, include_archived=False)
        
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
                            st.caption(f"EDID: {student.get('edid', 'N/A')}")
                            
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
        archived_students = [s for s in st.session_state.students_list if s.get('program') == program and s.get('archived', False)]
        
        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("Students who have completed the program - read-only")
            
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**Profile Status:** {student.get('profile_status', 'N/A')}")
                    st.markdown(f"**EDID:** {student.get('edid', 'N/A')}")
                    
                    incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                    st.metric("Total Incidents", incident_count)
                    
                    if st.button("View Historical Data", key=f"view_arch_{student['id']}"):
                        navigate_to('student_analysis', student_id=student['id'])

# --- ADMIN PORTAL ---

@handle_errors("Unable to load admin portal")
def render_admin_portal():
    """Renders the admin portal with staff management."""
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')
    
    st.markdown("---")
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Staff Management", "🎓 Student Management", "📊 Reports", "⚙️ Settings"])
    
    with tab1:
        render_staff_management()
    
    with tab2:
        render_student_management()
    
    with tab3:
        st.markdown("### 📊 System Reports")
        st.info("Reports functionality - to be implemented")
    
    with tab4:
        st.markdown("### ⚙️ System Settings")
        st.info("Settings functionality - to be implemented")

@handle_errors("Unable to load staff management")
def render_staff_management():
    """Renders staff management section."""
    
    st.markdown("## 👥 Staff Management")
    st.markdown("---")
    
    # Sub-tabs for active and archived staff
    staff_tab1, staff_tab2 = st.tabs(["✅ Active Staff", "📦 Archived Staff"])
    
    with staff_tab1:
        st.markdown("### Add New Staff Member")
        
        col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
        
        with col_add1:
            new_staff_name = st.text_input("Staff Name", key="new_staff_name", placeholder="Enter full name")
        
        with col_add2:
            new_staff_role = st.selectbox(
                "Role",
                options=["--- Select Role ---"] + STAFF_ROLES,
                key="new_staff_role"
            )
        
        with col_add3:
            st.markdown("##")  # Spacing
            if st.button("➕ Add Staff", type="primary", use_container_width=True):
                try:
                    if add_staff_member(new_staff_name, new_staff_role):
                        st.success(f"✅ Added {new_staff_name} ({new_staff_role})")
                        st.rerun()
                except (ValidationError, AppError) as e:
                    st.error(e.user_message)
        
        st.markdown("---")
        st.markdown("### Current Active Staff")
        
        active_staff = [s for s in st.session_state.staff_list if not s.get('archived', False)]
        
        if not active_staff:
            st.info("No active staff members")
        else:
            # Group staff by role
            staff_by_role = {}
            for staff in active_staff:
                role = staff.get('role', 'Unknown')
                if role not in staff_by_role:
                    staff_by_role[role] = []
                staff_by_role[role].append(staff)
            
            # Display by role
            for role in STAFF_ROLES:
                if role in staff_by_role:
                    with st.expander(f"**{role}** ({len(staff_by_role[role])} staff)", expanded=True):
                        for staff in staff_by_role[role]:
                            col_staff1, col_staff2, col_staff3 = st.columns([3, 2, 1])
                            
                            with col_staff1:
                                st.markdown(f"**{staff['name']}**")
                            
                            with col_staff2:
                                if staff.get('created_date'):
                                    st.caption(f"Added: {staff['created_date']}")
                            
                            with col_staff3:
                                if st.button("🗄️ Archive", key=f"archive_{staff['id']}", use_container_width=True):
                                    try:
                                        if archive_staff_member(staff['id']):
                                            st.success(f"Archived {staff['name']}")
                                            st.rerun()
                                    except AppError as e:
                                        st.error(e.user_message)
    
    with staff_tab2:
        st.markdown("### Archived Staff Members")
        st.caption("These staff members are no longer active but remain in the system for historical records")
        
        archived_staff = [s for s in st.session_state.staff_list if s.get('archived', False)]
        
        if not archived_staff:
            st.info("No archived staff members")
        else:
            for staff in archived_staff:
                with st.expander(f"📦 {staff['name']} - {staff.get('role', 'N/A')}"):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.markdown(f"**Role:** {staff.get('role', 'N/A')}")
                        if staff.get('created_date'):
                            st.markdown(f"**Added:** {staff['created_date']}")
                    
                    with col_info2:
                        if staff.get('archived_date'):
                            st.markdown(f"**Archived:** {staff['archived_date']}")
                    
                    if st.button("♻️ Restore Staff Member", key=f"restore_{staff['id']}"):
                        try:
                            if unarchive_staff_member(staff['id']):
                                st.success(f"Restored {staff['name']}")
                                st.rerun()
                        except AppError as e:
                            st.error(e.user_message)

@handle_errors("Unable to load student management")
def render_student_management():
    """Renders student management section."""
    
    st.markdown("## 🎓 Student Management")
    st.markdown("---")
    
    st.markdown("### Add New Student")
    
    col_add1, col_add2, col_add3, col_add4 = st.columns([2, 1.5, 1, 1])
    
    with col_add1:
        new_student_name = st.text_input("Student Name", key="new_student_name", placeholder="Enter full name")
    
    with col_add2:
        new_student_dob = st.date_input(
            "Date of Birth",
            key="new_student_dob",
            min_value=datetime(1990, 1, 1).date(),
            max_value=datetime.now().date(),
            value=datetime(2015, 1, 1).date()
        )
    
    with col_add3:
        new_student_program = st.selectbox(
            "Program",
            options=["--- Select Program ---"] + PROGRAM_OPTIONS,
            key="new_student_program"
        )
    
    with col_add4:
        # Dynamic grade options based on selected program
        if new_student_program and new_student_program != "--- Select Program ---":
            grade_options = ["--- Select Grade ---"] + GRADE_OPTIONS.get(new_student_program, [])
        else:
            grade_options = ["--- Select Grade ---"]
        
        new_student_grade = st.selectbox(
            "Grade",
            options=grade_options,
            key="new_student_grade"
        )
    
    col_edid, col_add_btn = st.columns([3, 1])
    
    with col_edid:
        new_student_edid = st.text_input(
            "EDID (Education Department ID)",
            key="new_student_edid",
            placeholder="e.g., ED12345",
            help="Unique identifier from Education Department"
        )
    
    with col_add_btn:
        st.markdown("##")  # Spacing
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            try:
                if add_student(
                    new_student_name,
                    new_student_dob,
                    new_student_program,
                    new_student_grade,
                    new_student_edid
                ):
                    st.success(f"✅ Added {new_student_name} to {new_student_program} Program")
                    st.rerun()
            except (ValidationError, AppError) as e:
                st.error(e.user_message)
    
    st.markdown("---")
    st.markdown("### Current Students by Program")
    
    # Group students by program
    program_tabs = st.tabs(["📘 Junior Primary", "📗 Primary Years", "📙 Senior Years", "📚 All Students"])
    
    programs = ['JP', 'PY', 'SY']
    
    for idx, program in enumerate(programs):
        with program_tabs[idx]:
            students_in_program = get_students_by_program(program, include_archived=False)
            
            if not students_in_program:
                st.info(f"No students currently in {program} program")
            else:
                st.markdown(f"**Total Students:** {len(students_in_program)}")
                
                # Create a dataframe for better display
                student_data = []
                for student in students_in_program:
                    age = calculate_age(student.get('dob', ''))
                    student_data.append({
                        'Name': student['name'],
                        'Grade': student['grade'],
                        'EDID': student.get('edid', 'N/A'),
                        'Age': age,
                        'DOB': student.get('dob', 'N/A'),
                        'Status': student.get('profile_status', 'Draft'),
                        'Added': student.get('created_date', 'N/A')
                    })
                
                df = pd.DataFrame(student_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    # All students view
    with program_tabs[3]:
        all_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        
        if not all_students:
            st.info("No students in the system")
        else:
            st.markdown(f"**Total Students Across All Programs:** {len(all_students)}")
            
            # Summary by program
            col_jp, col_py, col_sy = st.columns(3)
            with col_jp:
                jp_count = len(get_students_by_program('JP', include_archived=False))
                st.metric("JP Students", jp_count)
            with col_py:
                py_count = len(get_students_by_program('PY', include_archived=False))
                st.metric("PY Students", py_count)
            with col_sy:
                sy_count = len(get_students_by_program('SY', include_archived=False))
                st.metric("SY Students", sy_count)
            
            st.markdown("---")
            
            # Full student list
            student_data = []
            for student in sorted(all_students, key=lambda x: (x.get('program', ''), x.get('name', ''))):
                age = calculate_age(student.get('dob', ''))
                student_data.append({
                    'Name': student['name'],
                    'Program': student['program'],
                    'Grade': student['grade'],
                    'EDID': student.get('edid', 'N/A'),
                    'Age': age,
                    'DOB': student.get('dob', 'N/A'),
                    'Status': student.get('profile_status', 'Draft'),
                })
            
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def calculate_age(dob_str: str) -> str:
    """Calculate age from date of birth string."""
    try:
        if not dob_str:
            return "N/A"
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return str(age)
    except Exception as e:
        logger.error(f"Error calculating age: {e}")
        return "N/A"

# --- STAFF SELECTOR COMPONENT ---

def render_staff_selector(label: str = "Staff Member", key: str = "staff_selector", include_special_options: bool = True):
    """
    Renders a staff selector with optional TRT and External SSO options.
    Returns a dict with staff info, or special options if selected.
    """
    
    active_staff = get_active_staff()
    
    # Build options list
    options = [{'id': None, 'name': '--- Select Staff ---', 'role': None, 'special': False}]
    
    # Add special options if enabled
    if include_special_options:
        options.append({'id': 'TRT', 'name': 'TRT (Relief Teacher)', 'role': 'TRT', 'special': True})
        options.append({'id': 'External_SSO', 'name': 'External SSO', 'role': 'External SSO', 'special': True})
        options.append({'id': 'divider', 'name': '─────────────────', 'role': None, 'special': False})
    
    # Add active staff
    options.extend([{**s, 'special': False} for s in active_staff])
    
    # Filter out divider from actual selection
    selectable_options = [opt for opt in options if opt['id'] != 'divider']
    
    selected = st.selectbox(
        label,
        options=selectable_options,
        format_func=lambda x: f"{x['name']}" + (f" ({x['role']})" if x['role'] and not x.get('special') else ""),
        key=key
    )
    
    # If TRT or External SSO selected, prompt for name
    if selected and selected.get('special'):
        st.markdown(f"**{selected['name']} selected** - Please enter their name:")
        specific_name = st.text_input(
            f"Enter {selected['role']} Name",
            key=f"{key}_specific_name",
            placeholder=f"Full name of {selected['role']}"
        )
        
        if specific_name and specific_name.strip():
            return {
                'id': selected['id'],
                'name': specific_name.strip(),
                'role': selected['role'],
                'is_special': True
            }
        else:
            # Return with placeholder until name is entered
            return {
                'id': selected['id'],
                'name': f"{selected['role']} (Name Required)",
                'role': selected['role'],
                'is_special': True,
                'name_missing': True
            }
    
    return selected

# --- DIRECT LOG FORM ---

@handle_errors("Unable to load incident form")
def render_direct_log_form():
    """Renders the incident logging form."""
    
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
            incident_date = st.date_input("Date of Incident", value=datetime.now())
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)
        
        with col2:
            # Use the staff selector component
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True
            )
        
        st.markdown("### Behavior Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            behavior_type = st.selectbox(
                "Behavior Type",
                options=["--- Select Behavior ---"] + BEHAVIORS_FBA
            )
            antecedent = st.selectbox("Antecedent", options=ANTECEDENTS_NEW)
        
        with col4:
            intervention = st.selectbox("Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)
        
        severity_level = st.slider("Severity Level", 1, 5, 2)
        
        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional context about the incident...",
            height=100
        )
        
        submitted = st.form_submit_button("Submit Incident Report", type="primary", use_container_width=True)
        
        if submitted:
            try:
                # Check if special staff needs name
                if reported_by and reported_by.get('name_missing'):
                    st.error("Please enter the name for the selected staff type (TRT or External SSO)")
                    return
                
                # Validate form
                validate_incident_form(
                    location, reported_by, behavior_type,
                    severity_level, incident_date, incident_time
                )
                
                # Create incident record
                incident_time_obj = datetime.combine(incident_date, incident_time)
                session = get_session_window(incident_time)
                
                new_incident = {
                    'id': str(uuid.uuid4()),
                    'student_id': student_id,
                    'date': incident_date.strftime('%Y-%m-%d'),
                    'time': incident_time.strftime('%H:%M:%S'),
                    'day': incident_date.strftime('%A'),
                    'session': session,
                    'location': location,
                    'reported_by_name': reported_by['name'],
                    'reported_by_id': reported_by['id'],
                    'reported_by_role': reported_by['role'],
                    'is_special_staff': reported_by.get('is_special', False),
                    'behavior_type': behavior_type,
                    'antecedent': antecedent,
                    'intervention': intervention,
                    'support_type': support_type,
                    'severity': severity_level,
                    'description': description,
                    'is_critical': severity_level >= 4,
                    'created_at': datetime.now().isoformat()
                }
                
                st.session_state.incidents.append(new_incident)
                
                st.success("✅ Incident report submitted successfully!")
                
                if severity_level >= 4:
                    st.warning("⚠️ This is a critical incident (Severity 4-5). Please complete a Critical Incident ABCH form.")
                
                # Option to add another or return
                col_another, col_return = st.columns(2)
                with col_another:
                    if st.button("➕ Log Another Incident", use_container_width=True):
                        st.rerun()
                with col_return:
                    if st.button("↩️ Return to Student List", use_container_width=True):
                        navigate_to('program_students', program=student['program'])
                        
            except ValidationError as e:
                st.error(e.user_message)

# --- Placeholder for other render functions ---

def render_critical_incident_abch_form():
    st.title("Critical Incident Form")
    if st.button("⬅ Back"):
        navigate_to('landing')
    st.info("Critical incident ABCH form rendered here")

@handle_errors("Unable to load student analysis")
def render_student_analysis():
    """Renders comprehensive student analysis with data visualizations."""
    
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)
    
    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return
    
    # Header
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])
    
    st.markdown("---")
    
    # Get all incidents for this student
    student_incidents = [inc for inc in st.session_state.incidents if inc.get('student_id') == student_id]
    
    if not student_incidents:
        st.info("No incident data available for this student yet.")
        st.markdown("### Actions")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to('direct_log_form', student_id=student_id)
        return
    
    # Summary Metrics
    st.markdown("### 📈 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Incidents", len(student_incidents))
    
    with col2:
        critical_count = len([inc for inc in student_incidents if inc.get('is_critical', False)])
        st.metric("Critical Incidents", critical_count, delta=None if critical_count == 0 else f"{(critical_count/len(student_incidents)*100):.0f}%")
    
    with col3:
        avg_severity = sum([inc.get('severity', 0) for inc in student_incidents]) / len(student_incidents)
        st.metric("Avg Severity", f"{avg_severity:.1f}")
    
    with col4:
        # Get date range
        dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in student_incidents]
        days_span = (max(dates) - min(dates)).days + 1 if len(dates) > 0 else 1
        st.metric("Days Tracked", days_span)
    
    with col5:
        incidents_per_week = (len(student_incidents) / days_span) * 7 if days_span > 0 else 0
        st.metric("Incidents/Week", f"{incidents_per_week:.1f}")
    
    st.markdown("---")
    
    # Create tabs for different analysis views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Timeline", 
        "📊 Behavior Analysis", 
        "🕒 Time Patterns", 
        "📍 Location Analysis",
        "📋 Incident Log"
    ])
    
    # TAB 1: TIMELINE
    with tab1:
        st.markdown("### Incident Timeline")
        
        # Prepare data for timeline
        timeline_data = []
        for inc in student_incidents:
            timeline_data.append({
                'Date': inc['date'],
                'Severity': inc['severity'],
                'Behavior': inc['behavior_type'],
                'Location': inc['location'],
                'Critical': 'Critical' if inc.get('is_critical', False) else 'Standard'
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        df_timeline['Date'] = pd.to_datetime(df_timeline['Date'])
        df_timeline = df_timeline.sort_values('Date')
        
        # Incidents over time chart
        daily_counts = df_timeline.groupby('Date').size().reset_index(name='Count')
        
        fig_timeline = px.line(
            daily_counts, 
            x='Date', 
            y='Count',
            title='Incidents Over Time',
            markers=True,
            template=PLOTLY_THEME
        )
        fig_timeline.update_traces(line_color='#667eea')
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Severity over time
        fig_severity_time = px.scatter(
            df_timeline,
            x='Date',
            y='Severity',
            color='Critical',
            size='Severity',
            hover_data=['Behavior', 'Location'],
            title='Severity Levels Over Time',
            template=PLOTLY_THEME,
            color_discrete_map={'Critical': '#ff4b4b', 'Standard': '#4b7bff'}
        )
        st.plotly_chart(fig_severity_time, use_container_width=True)
    
    # TAB 2: BEHAVIOR ANALYSIS
    with tab2:
        st.markdown("### Behavior Type Analysis")
        
        col_beh1, col_beh2 = st.columns(2)
        
        with col_beh1:
            # Behavior frequency
            behavior_counts = pd.DataFrame(student_incidents)['behavior_type'].value_counts().reset_index()
            behavior_counts.columns = ['Behavior', 'Count']
            
            fig_behavior = px.bar(
                behavior_counts,
                x='Count',
                y='Behavior',
                orientation='h',
                title='Most Common Behaviors',
                template=PLOTLY_THEME,
                color='Count',
                color_continuous_scale='Purples'
            )
            st.plotly_chart(fig_behavior, use_container_width=True)
        
        with col_beh2:
            # Behavior severity
            behavior_severity = []
            for inc in student_incidents:
                behavior_severity.append({
                    'Behavior': inc['behavior_type'],
                    'Severity': inc['severity']
                })
            df_beh_sev = pd.DataFrame(behavior_severity)
            avg_severity_by_behavior = df_beh_sev.groupby('Behavior')['Severity'].mean().reset_index()
            avg_severity_by_behavior.columns = ['Behavior', 'Avg Severity']
            
            fig_beh_sev = px.bar(
                avg_severity_by_behavior,
                x='Avg Severity',
                y='Behavior',
                orientation='h',
                title='Average Severity by Behavior',
                template=PLOTLY_THEME,
                color='Avg Severity',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_beh_sev, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### Antecedent Analysis")
        
        # Antecedent frequency
        antecedent_counts = pd.DataFrame(student_incidents)['antecedent'].value_counts().reset_index()
        antecedent_counts.columns = ['Antecedent', 'Count']
        
        fig_antecedent = px.pie(
            antecedent_counts,
            values='Count',
            names='Antecedent',
            title='Common Antecedents (Triggers)',
            template=PLOTLY_THEME
        )
        st.plotly_chart(fig_antecedent, use_container_width=True)
        
        # Intervention effectiveness
        st.markdown("### Intervention Analysis")
        intervention_counts = pd.DataFrame(student_incidents)['intervention'].value_counts().reset_index()
        intervention_counts.columns = ['Intervention', 'Count']
        
        fig_intervention = px.bar(
            intervention_counts,
            x='Count',
            y='Intervention',
            orientation='h',
            title='Most Used Interventions',
            template=PLOTLY_THEME,
            color='Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_intervention, use_container_width=True)
    
    # TAB 3: TIME PATTERNS
    with tab3:
        st.markdown("### Time Pattern Analysis")
        
        col_time1, col_time2 = st.columns(2)
        
        with col_time1:
            # Day of week analysis
            day_counts = pd.DataFrame(student_incidents)['day'].value_counts().reset_index()
            day_counts.columns = ['Day', 'Count']
            
            # Order days properly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
            day_counts = day_counts.sort_values('Day')
            
            fig_day = px.bar(
                day_counts,
                x='Day',
                y='Count',
                title='Incidents by Day of Week',
                template=PLOTLY_THEME,
                color='Count',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig_day, use_container_width=True)
        
        with col_time2:
            # Session analysis
            session_counts = pd.DataFrame(student_incidents)['session'].value_counts().reset_index()
            session_counts.columns = ['Session', 'Count']
            
            fig_session = px.pie(
                session_counts,
                values='Count',
                names='Session',
                title='Incidents by Session',
                template=PLOTLY_THEME,
                hole=0.4
            )
            st.plotly_chart(fig_session, use_container_width=True)
        
        # Heatmap: Day vs Session
        st.markdown("### Day & Session Heatmap")
        
        heatmap_data = []
        for inc in student_incidents:
            heatmap_data.append({
                'Day': inc['day'],
                'Session': inc['session']
            })
        
        df_heatmap = pd.DataFrame(heatmap_data)
        heatmap_pivot = df_heatmap.groupby(['Day', 'Session']).size().reset_index(name='Count')
        heatmap_pivot_wide = heatmap_pivot.pivot(index='Day', columns='Session', values='Count').fillna(0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot_wide = heatmap_pivot_wide.reindex([day for day in day_order if day in heatmap_pivot_wide.index])
        
        fig_heatmap = px.imshow(
            heatmap_pivot_wide,
            title='Incident Frequency: Day vs Session',
            template=PLOTLY_THEME,
            color_continuous_scale='YlOrRd',
            labels=dict(x="Session", y="Day", color="Incidents")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # TAB 4: LOCATION ANALYSIS
    with tab4:
        st.markdown("### Location Analysis")
        
        col_loc1, col_loc2 = st.columns(2)
        
        with col_loc1:
            # Location frequency
            location_counts = pd.DataFrame(student_incidents)['location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Count']
            
            fig_location = px.bar(
                location_counts,
                x='Count',
                y='Location',
                orientation='h',
                title='Incidents by Location',
                template=PLOTLY_THEME,
                color='Count',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_location, use_container_width=True)
        
        with col_loc2:
            # Support type analysis
            support_counts = pd.DataFrame(student_incidents)['support_type'].value_counts().reset_index()
            support_counts.columns = ['Support Type', 'Count']
            
            fig_support = px.pie(
                support_counts,
                values='Count',
                names='Support Type',
                title='Support Type Distribution',
                template=PLOTLY_THEME
            )
            st.plotly_chart(fig_support, use_container_width=True)
        
        # Location vs Severity
        st.markdown("### Location Risk Analysis")
        
        location_severity = []
        for inc in student_incidents:
            location_severity.append({
                'Location': inc['location'],
                'Severity': inc['severity']
            })
        
        df_loc_sev = pd.DataFrame(location_severity)
        avg_sev_by_loc = df_loc_sev.groupby('Location')['Severity'].mean().reset_index()
        avg_sev_by_loc.columns = ['Location', 'Avg Severity']
        avg_sev_by_loc = avg_sev_by_loc.sort_values('Avg Severity', ascending=False)
        
        fig_loc_sev = px.bar(
            avg_sev_by_loc,
            x='Avg Severity',
            y='Location',
            orientation='h',
            title='Average Severity by Location (High Risk Areas)',
            template=PLOTLY_THEME,
            color='Avg Severity',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_loc_sev, use_container_width=True)
    
    # TAB 5: INCIDENT LOG
    with tab5:
        st.markdown("### Complete Incident Log")
        
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=[1, 2, 3, 4, 5],
                default=[1, 2, 3, 4, 5],
                key="severity_filter"
            )
        
        with col_filter2:
            behavior_types = list(set([inc['behavior_type'] for inc in student_incidents]))
            behavior_filter = st.multiselect(
                "Filter by Behavior",
                options=behavior_types,
                default=behavior_types,
                key="behavior_filter"
            )
        
        with col_filter3:
            show_critical_only = st.checkbox("Show Critical Only", key="critical_filter")
        
        # Apply filters
        filtered_incidents = student_incidents
        
        if severity_filter:
            filtered_incidents = [inc for inc in filtered_incidents if inc['severity'] in severity_filter]
        
        if behavior_filter:
            filtered_incidents = [inc for inc in filtered_incidents if inc['behavior_type'] in behavior_filter]
        
        if show_critical_only:
            filtered_incidents = [inc for inc in filtered_incidents if inc.get('is_critical', False)]
        
        st.markdown(f"**Showing {len(filtered_incidents)} of {len(student_incidents)} incidents**")
        
        # Display incidents
        for inc in sorted(filtered_incidents, key=lambda x: x['date'], reverse=True):
            severity_color = '🔴' if inc['severity'] >= 4 else '🟡' if inc['severity'] == 3 else '🟢'
            critical_badge = ' 🚨 **CRITICAL**' if inc.get('is_critical', False) else ''
            
            with st.expander(f"{severity_color} {inc['date']} - {inc['behavior_type']}{critical_badge}"):
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.markdown(f"**Date:** {inc['date']}")
                    st.markdown(f"**Time:** {inc['time']}")
                    st.markdown(f"**Day:** {inc['day']}")
                    st.markdown(f"**Session:** {inc['session']}")
                    st.markdown(f"**Severity:** {inc['severity']}/5")
                
                with col_detail2:
                    st.markdown(f"**Location:** {inc['location']}")
                    st.markdown(f"**Reported By:** {inc.get('reported_by_name', 'N/A')}")
                    st.markdown(f"**Support Type:** {inc['support_type']}")
                    st.markdown(f"**Behavior:** {inc['behavior_type']}")
                
                st.markdown("---")
                st.markdown(f"**Antecedent:** {inc['antecedent']}")
                st.markdown(f"**Intervention:** {inc['intervention']}")
                
                if inc.get('description'):
                    st.markdown(f"**Notes:** {inc['description']}")
    
    # Action buttons at bottom
    st.markdown("---")
    st.markdown("### Actions")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("📝 Log New Incident", type="primary", use_container_width=True):
            navigate_to('direct_log_form', student_id=student_id)
    
    with col_act2:
        if st.button("📊 Export Data", use_container_width=True):
            st.info("Export functionality - to be implemented")
    
    with col_act3:
        if st.button("↩️ Back to Program", use_container_width=True):
            navigate_to('program_students', program=student['program'])

# --- MAIN ---

def main():
    """Main application logic."""
    
    try:
        # Initialize session state
        initialize_session_state()
        
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
            render_admin_portal()
        else:
            st.error("Unknown page")
            navigate_to('landing')
            
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        st.error("A critical error occurred.")

if __name__ == '__main__':
    main()
