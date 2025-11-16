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

# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    """Returns a cached Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

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

# Apply Professional Blue Theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: #1e3a8a;
    font-weight: 600;
}

h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 1.5rem;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    transition: all 0.3s ease;
    border: none;
    text-transform: none;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
}

.stButton > button[kind="secondary"] {
    background: white;
    color: #3b82f6;
    border: 2px solid #3b82f6;
}

.stButton > button[kind="secondary"]:hover {
    background: #eff6ff;
    border-color: #2563eb;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

div[data-testid="stMetric"] label {
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1e40af;
    font-size: 2rem;
    font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: white;
    padding: 0.5rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    color: #64748b;
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
}

.stTextInput input, .stSelectbox select, .stTextArea textarea, .stDateInput input, .stTimeInput input {
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    font-family: 'Inter', sans-serif;
    transition: border-color 0.2s ease;
}

.stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: #1e40af;
    background: #f0f9ff;
    border-radius: 8px;
    padding: 1rem;
}

.dataframe {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.dataframe thead tr {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
}

.stSuccess {
    background: #d1fae5;
    color: #065f46;
    border-left: 4px solid #10b981;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    padding: 1rem;
}

.stError {
    background: #fee2e2;
    color: #991b1b;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    padding: 1rem;
}

.stWarning {
    background: #fef3c7;
    color: #92400e;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    padding: 1rem;
}

.stInfo {
    background: #dbeafe;
    color: #1e40af;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

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

VALID_PAGES = ['landing', 'program_students', 'direct_log_form', 'critical_incident_abch', 'student_analysis', 'admin_portal']

# --- DATA LOADING FUNCTIONS (SUPABASE) ---

def load_students_from_db() -> List[Dict[str, Any]]:
    """Load all students from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('students').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error loading students: {e}")
        return []

def load_staff_from_db() -> List[Dict[str, Any]]:
    """Load all staff from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('staff').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error loading staff: {e}")
        return []

def load_incidents_from_db() -> List[Dict[str, Any]]:
    """Load all incidents from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('incidents').select('*').execute()
        
        # Normalize field names for backward compatibility
        incidents = []
        if response.data:
            for inc in response.data:
                # Create a copy with both old and new field names
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
    """Load system settings from Supabase."""
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

# --- SESSION STATE INITIALIZATION ---

def initialize_session_state():
    """Initialize all session state variables from Supabase"""
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data from database..."):
            # Load from Supabase
            st.session_state.students_list = load_students_from_db()
            st.session_state.staff_list = load_staff_from_db()
            st.session_state.incidents = load_incidents_from_db()
            st.session_state.system_settings = load_system_settings()
            st.session_state.data_loaded = True
    
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
    """Adds a new staff member to Supabase."""
    try:
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty", "Please enter a staff name")
        
        if not role or role == "--- Select Role ---":
            raise ValidationError("Role must be selected", "Please select a role")
        
        # Check for duplicate names in current session
        existing = [s for s in st.session_state.staff_list if s['name'].lower() == name.strip().lower() and not s.get('archived', False)]
        if existing:
            raise ValidationError("Duplicate staff name", "A staff member with this name already exists")
        
        new_staff = {
            'name': name.strip(),
            'role': role,
            'active': True,
            'archived': False
        }
        
        # Insert into Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').insert(new_staff).execute()
        
        if response.data:
            # Update session state
            st.session_state.staff_list.append(response.data[0])
            logger.info(f"Added staff member: {name} ({role})")
            return True
        else:
            raise AppError("Database insert failed", "Could not add staff member")
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding staff: {e}")
        raise AppError("Failed to add staff member", "Could not add staff member. Please try again.")

def archive_staff_member(staff_id: str) -> bool:
    """Archives a staff member in Supabase."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot archive: staff member not found")
        
        # Update in Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').update({
            'archived': True,
            'active': False,
            'archived_date': datetime.now().isoformat()
        }).eq('id', staff_id).execute()
        
        if response.data:
            # Update session state
            staff['archived'] = True
            staff['active'] = False
            staff['archived_date'] = datetime.now().isoformat()
            
            logger.info(f"Archived staff member: {staff['name']}")
            return True
        else:
            raise AppError("Database update failed", "Could not archive staff member")
        
    except Exception as e:
        logger.error(f"Error archiving staff: {e}")
        raise AppError("Failed to archive staff member", "Could not archive staff member. Please try again.")

def unarchive_staff_member(staff_id: str) -> bool:
    """Unarchives a staff member in Supabase."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot unarchive: staff member not found")
        
        # Update in Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').update({
            'archived': False,
            'active': True
        }).eq('id', staff_id).execute()
        
        if response.data:
            # Update session state
            staff['archived'] = False
            staff['active'] = True
            
            logger.info(f"Unarchived staff member: {staff['name']}")
            return True
        else:
            raise AppError("Database update failed", "Could not unarchive staff member")
        
    except Exception as e:
        logger.error(f"Error unarchiving staff: {e}")
        raise AppError("Failed to unarchive staff member", "Could not unarchive staff member. Please try again.")

def add_student(name: str, dob: datetime.date, program: str, grade: str, edid: str) -> bool:
    """Adds a new student to Supabase."""
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
        
        # Check for duplicate EDID in current session
        existing_edid = [s for s in st.session_state.students_list if s.get('edid', '').upper() == edid.strip().upper() and not s.get('archived', False)]
        if existing_edid:
            raise ValidationError("Duplicate EDID", f"A student with EDID {edid} already exists")
        
        # Validate DOB is not in the future
        if dob > datetime.now().date():
            raise ValidationError("Invalid date of birth", "Date of birth cannot be in the future")
        
        new_student = {
            'name': name.strip(),
            'dob': dob.strftime('%Y-%m-%d'),
            'program': program,
            'grade': grade,
            'edid': edid.strip().upper(),
            'profile_status': 'Draft',
            'archived': False
        }
        
        # Insert into Supabase
        supabase = get_supabase_client()
        response = supabase.table('students').insert(new_student).execute()
        
        if response.data:
            # Update session state
            st.session_state.students_list.append(response.data[0])
            logger.info(f"Added student: {name} (EDID: {edid}, Program: {program})")
            return True
        else:
            raise AppError("Database insert failed", "Could not add student")
        
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

def generate_student_report(student: Dict[str, Any], incidents: List[Dict[str, Any]]) -> Optional[str]:
    """Generates a comprehensive Word document report with charts and analysis."""
    try:
        import subprocess
        
        # Check if Node.js is available
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("Node.js not available - cannot generate reports")
            return None
        
        # Create temporary directory for charts
        chart_dir = "/home/claude/report_charts"
        subprocess.run(['mkdir', '-p', chart_dir], check=True)
        
        # Generate and save charts as images
        chart_files = {}
        
        # 1. Timeline chart
        timeline_data = pd.DataFrame([{
            'Date': inc['date'],
            'Count': 1
        } for inc in incidents])
        timeline_data['Date'] = pd.to_datetime(timeline_data['Date'])
        daily_counts = timeline_data.groupby('Date').size().reset_index(name='Count')
        
        fig = px.line(daily_counts, x='Date', y='Count', title='Incidents Over Time', markers=True)
        fig.write_image(f"{chart_dir}/timeline.png", width=800, height=400)
        chart_files['timeline'] = f"{chart_dir}/timeline.png"
        
        # 2. Behavior frequency chart
        behavior_counts = pd.DataFrame(incidents)['behavior_type'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig = px.bar(behavior_counts, x='Count', y='Behavior', orientation='h', title='Behavior Frequency')
        fig.write_image(f"{chart_dir}/behaviors.png", width=800, height=400)
        chart_files['behaviors'] = f"{chart_dir}/behaviors.png"
        
        # 3. Day of week chart
        day_counts = pd.DataFrame(incidents)['day'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Count']
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
        day_counts = day_counts.sort_values('Day')
        fig = px.bar(day_counts, x='Day', y='Count', title='Incidents by Day of Week')
        fig.write_image(f"{chart_dir}/days.png", width=800, height=400)
        chart_files['days'] = f"{chart_dir}/days.png"
        
        # 4. Location chart
        location_counts = pd.DataFrame(incidents)['location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        fig = px.bar(location_counts.head(10), x='Count', y='Location', orientation='h', title='Top 10 Incident Locations')
        fig.write_image(f"{chart_dir}/locations.png", width=800, height=400)
        chart_files['locations'] = f"{chart_dir}/locations.png"
        
        # Calculate key statistics
        avg_severity = sum([inc.get('severity', 0) for inc in incidents]) / len(incidents)
        critical_count = len([inc for inc in incidents if inc.get('is_critical', False)])
        critical_rate = (critical_count / len(incidents) * 100) if len(incidents) > 0 else 0
        
        behavior_counts_dict = pd.DataFrame(incidents)['behavior_type'].value_counts()
        top_behavior = behavior_counts_dict.index[0] if len(behavior_counts_dict) > 0 else "N/A"
        top_behavior_count = behavior_counts_dict.iloc[0] if len(behavior_counts_dict) > 0 else 0
        
        antecedent_counts = pd.DataFrame(incidents)['antecedent'].value_counts()
        top_antecedent = antecedent_counts.index[0] if len(antecedent_counts) > 0 else "N/A"
        
        location_counts_stat = pd.DataFrame(incidents)['location'].value_counts()
        top_location = location_counts_stat.index[0] if len(location_counts_stat) > 0 else "N/A"
        
        day_counts_stat = pd.DataFrame(incidents)['day'].value_counts()
        top_day = day_counts_stat.index[0] if len(day_counts_stat) > 0 else "N/A"
        
        session_counts = pd.DataFrame(incidents)['session'].value_counts()
        top_session = session_counts.index[0] if len(session_counts) > 0 else "N/A"
        
        behavior_pct = (top_behavior_count/len(incidents)*100) if len(incidents) > 0 else 0
        
        # Create Node.js script for document generation (continued in next part due to length)
        script_content = """const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, 
        AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType, LevelFormat } = require('docx');
const fs = require('fs');

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: "2C3E50", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: "34495E", font: "Arial" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "5D6D7E", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "7B8794", font: "Arial" },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [{
      reference: "bullet-list",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Student Behavior Analysis Report")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "%STUDENT_NAME%", size: 32, bold: true, color: "2C3E50" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 },
        children: [new TextRun({ text: "Grade %GRADE% | %PROGRAM% Program", size: 24, color: "7B8794" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
        children: [new TextRun({ text: "Report Generated: %DATE%", size: 20, color: "95A5A6" })] }),
      new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, children: [new TextRun("Executive Summary")] }),
      new Paragraph({ spacing: { after: 120 },
        children: [new TextRun("This report analyzes behavioral incidents and provides evidence-based recommendations.")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key Statistics")] }),
      new Table({ columnWidths: [3120, 3120, 3120], margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Total Incidents", bold: true })] })] }),
            new TableCell({ width: { size: 3120, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Critical Incidents", bold: true })] })] }),
            new TableCell({ width: { size: 3120, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Average Severity", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "%TOTAL_INCIDENTS%", size: 28, bold: true, color: "2C3E50" })] })] }),
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "%CRITICAL_COUNT% (%CRITICAL_RATE%)", size: 28, bold: true, color: "E74C3C" })] })] }),
            new TableCell({ width: { size: 3120, type: WidthType.DXA },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "%AVG_SEVERITY%/5", size: 28, bold: true, color: "F39C12" })] })] })
          ]})
        ]
      }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key Patterns")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Primary Behavior: ", bold: true }), new TextRun("%TOP_BEHAVIOR% (%BEHAVIOR_COUNT% incidents, %BEHAVIOR_PCT%)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Most Common Trigger: ", bold: true }), new TextRun("%TOP_ANTECEDENT%")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Highest Risk Time: ", bold: true }), new TextRun("%TOP_DAY%, %TOP_SESSION%")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 },
        children: [new TextRun({ text: "Highest Risk Location: ", bold: true }), new TextRun("%TOP_LOCATION%")] }),
      new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, children: [new TextRun("Data Visualizations")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Incident Timeline")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
        children: [new ImageRun({ type: "png", data: fs.readFileSync("%CHART_TIMELINE%"),
          transformation: { width: 600, height: 300 }, altText: { title: "Timeline", description: "Timeline", name: "Timeline" } })] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Behavior Frequency")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
        children: [new ImageRun({ type: "png", data: fs.readFileSync("%CHART_BEHAVIORS%"),
          transformation: { width: 600, height: 300 }, altText: { title: "Behaviors", description: "Behaviors", name: "Behaviors" } })] }),
      new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_2, children: [new TextRun("Incidents by Day")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
        children: [new ImageRun({ type: "png", data: fs.readFileSync("%CHART_DAYS%"),
          transformation: { width: 600, height: 300 }, altText: { title: "Days", description: "Days", name: "Days" } })] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Top Locations")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 },
        children: [new ImageRun({ type: "png", data: fs.readFileSync("%CHART_LOCATIONS%"),
          transformation: { width: 600, height: 300 }, altText: { title: "Locations", description: "Locations", name: "Locations" } })] }),
      new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, children: [new TextRun("Evidence-Based Recommendations")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("CPI Framework")] }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun("Based on CPI's Nonviolent Crisis Intervention model:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Use empathic listening and validate feelings")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Provide choices to restore control")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Set clear limits using SETM approach")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun("Maintain safe distance and use paraverbal communication")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Trauma-Informed Practice")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Safety: ", bold: true }), new TextRun("Review %TOP_LOCATION% for triggers")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Trustworthiness: ", bold: true }), new TextRun("Explain interventions in advance")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Peer Support: ", bold: true }), new TextRun("Facilitate positive relationships")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun({ text: "Empowerment: ", bold: true }), new TextRun("Offer structured choices")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Berry Street Education Model")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Body: ", bold: true }), new TextRun("Movement breaks, sensory tools, breathing")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Relationship: ", bold: true }), new TextRun("2x10 strategy, repair & reconnect")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Stamina: ", bold: true }), new TextRun("Task chunking, progress charts")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Engagement: ", bold: true }), new TextRun("Student interests, voice & agency")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun({ text: "Character: ", bold: true }), new TextRun("SEL lessons, restorative practices")] }),
      new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_2, children: [new TextRun("SMART Training")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Square breathing (4-4-4-4)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Mindfulness at transitions")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun("5-4-3-2-1 grounding technique")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Australian Curriculum Integration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Self-Awareness: ", bold: true }), new TextRun("Emotional vocabulary, identify strengths")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Self-Management: ", bold: true }), new TextRun("Impulse control, behavioral goals")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 360 }, children: [new TextRun({ text: "Social Management: ", bold: true }), new TextRun("Assertive communication, conflict resolution")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Action Plan")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Immediate (1-2 Weeks)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Review %TOP_LOCATION% for triggers")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Daily 2-minute connections")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun("Introduce 3 regulation strategies")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Short-Term (1 Month)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Apply CPI strategies for %TOP_BEHAVIOR%")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("BSEM Body & Relationship focus")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 240 }, children: [new TextRun("Weekly data review")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Long-Term (Term/Semester)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Full Trauma-Informed environment")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("BSEM across all 5 domains")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 360 }, children: [new TextRun("Gradual fading of support")] }),
      new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { before: 240 },
        children: [new TextRun({ text: "End of Report", italics: true, color: "95A5A6" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Generated by Behaviour Support & Data Analysis Tool", size: 18, color: "95A5A6" })] })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('%OUTPUT_PATH%', buffer);
  console.log('Report generated');
});
"""
        
        # Replace placeholders
        replacements = {
            '%STUDENT_NAME%': student['name'],
            '%GRADE%': student['grade'],
            '%PROGRAM%': student['program'],
            '%DATE%': datetime.now().strftime('%B %d, %Y'),
            '%TOTAL_INCIDENTS%': str(len(incidents)),
            '%CRITICAL_COUNT%': str(critical_count),
            '%CRITICAL_RATE%': f"{critical_rate:.1f}%",
            '%AVG_SEVERITY%': f"{avg_severity:.1f}",
            '%TOP_BEHAVIOR%': top_behavior,
            '%BEHAVIOR_COUNT%': str(top_behavior_count),
            '%BEHAVIOR_PCT%': f"{behavior_pct:.1f}%",
            '%TOP_ANTECEDENT%': top_antecedent,
            '%TOP_DAY%': top_day,
            '%TOP_SESSION%': top_session,
            '%TOP_LOCATION%': top_location,
            '%CHART_TIMELINE%': chart_files['timeline'],
            '%CHART_BEHAVIORS%': chart_files['behaviors'],
            '%CHART_DAYS%': chart_files['days'],
            '%CHART_LOCATIONS%': chart_files['locations'],
            '%OUTPUT_PATH%': f"/mnt/user-data/outputs/{student['name'].replace(' ', '_')}_Analysis_Report.docx"
        }
        
        for placeholder, value in replacements.items():
            script_content = script_content.replace(placeholder, value)
        
        # Write and execute
        script_path = f"{chart_dir}/generate_report.js"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        result = subprocess.run(['node', script_path], capture_output=True, text=True, check=True)
        
        output_path = f"/mnt/user-data/outputs/{student['name'].replace(' ', '_')}_Analysis_Report.docx"
        
        # Clean up
        subprocess.run(['rm', '-rf', chart_dir], check=False)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return None

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
                    'student_id': student_id,
                    'incident_date': incident_date.strftime('%Y-%m-%d'),
                    'incident_time': incident_time.strftime('%H:%M:%S'),
                    'day_of_week': incident_date.strftime('%A'),
                    'session': session,
                    'location': location,
                    'reported_by_name': reported_by['name'],
                    'reported_by_id': reported_by['id'] if not reported_by.get('is_special', False) else None,
                    'reported_by_role': reported_by['role'],
                    'is_special_staff': reported_by.get('is_special', False),
                    'behavior_type': behavior_type,
                    'antecedent': antecedent,
                    'intervention': intervention,
                    'support_type': support_type,
                    'severity': severity_level,
                    'description': description,
                    'is_critical': severity_level >= 4
                }
                
                # Save to Supabase
                supabase = get_supabase_client()
                response = supabase.table('incidents').insert(new_incident).execute()
                
                if response.data:
                    # Update session state with the returned record (includes DB-generated ID)
                    saved_incident = response.data[0]
                    # Convert DB field names back to app field names for backward compatibility
                    saved_incident['date'] = saved_incident['incident_date']
                    saved_incident['time'] = saved_incident['incident_time']
                    saved_incident['day'] = saved_incident['day_of_week']
                    st.session_state.incidents.append(saved_incident)
                    
                    st.success("✅ Incident report submitted successfully!")
                    
                    if severity_level >= 4:
                        st.warning("⚠️ This is a critical incident (Severity 4-5). Please complete a Critical Incident ABCH form.")
                else:
                    st.error("Failed to save incident to database")
                    return
                
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Timeline", 
        "📊 Behavior Analysis", 
        "🕒 Time Patterns", 
        "📍 Location Analysis",
        "📋 Incident Log",
        "🎯 Analysis & Recommendations"
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
    
    # TAB 6: ANALYSIS & RECOMMENDATIONS
    with tab6:
        st.markdown("### 🎯 Data-Driven Analysis & Recommendations")
        st.caption("Evidence-based recommendations informed by CPI, Trauma-Informed Practice, SMART Training, Berry Street Education Model & Australian Curriculum")
        
        # Generate insights
        behavior_counts = pd.DataFrame(student_incidents)['behavior_type'].value_counts()
        top_behavior = behavior_counts.index[0] if len(behavior_counts) > 0 else "N/A"
        top_behavior_count = behavior_counts.iloc[0] if len(behavior_counts) > 0 else 0
        
        antecedent_counts = pd.DataFrame(student_incidents)['antecedent'].value_counts()
        top_antecedent = antecedent_counts.index[0] if len(antecedent_counts) > 0 else "N/A"
        
        location_counts = pd.DataFrame(student_incidents)['location'].value_counts()
        top_location = location_counts.index[0] if len(location_counts) > 0 else "N/A"
        
        day_counts = pd.DataFrame(student_incidents)['day'].value_counts()
        top_day = day_counts.index[0] if len(day_counts) > 0 else "N/A"
        
        session_counts = pd.DataFrame(student_incidents)['session'].value_counts()
        top_session = session_counts.index[0] if len(session_counts) > 0 else "N/A"
        
        critical_count = len([inc for inc in student_incidents if inc.get('is_critical', False)])
        critical_rate = (critical_count / len(student_incidents) * 100) if len(student_incidents) > 0 else 0
        
        # Key Patterns Identified
        st.markdown("### 📌 Key Patterns Identified")
        
        with st.container(border=True):
            col_pat1, col_pat2 = st.columns(2)
            
            with col_pat1:
                st.markdown("**Primary Behavior Concern:**")
                st.markdown(f"- **{top_behavior}** ({top_behavior_count} incidents, {(top_behavior_count/len(student_incidents)*100):.1f}%)")
                
                st.markdown("**Most Common Trigger:**")
                st.markdown(f"- {top_antecedent}")
                
                st.markdown("**Highest Risk Time:**")
                st.markdown(f"- {top_day}, {top_session}")
            
            with col_pat2:
                st.markdown("**Highest Risk Location:**")
                st.markdown(f"- {top_location}")
                
                st.markdown("**Critical Incident Rate:**")
                if critical_rate > 40:
                    st.markdown(f"- 🔴 **High:** {critical_rate:.1f}% (Immediate intervention needed)")
                elif critical_rate > 20:
                    st.markdown(f"- 🟡 **Moderate:** {critical_rate:.1f}% (Enhanced support recommended)")
                else:
                    st.markdown(f"- 🟢 **Low:** {critical_rate:.1f}% (Preventative strategies in place)")
        
        st.markdown("---")
        
        # Evidence-Based Recommendations
        st.markdown("### 💡 Evidence-Based Recommendations")
        
        # CPI Recommendations
        with st.expander("🛡️ **Crisis Prevention Institute (CPI) Framework**", expanded=True):
            st.markdown("""
            **Based on CPI's Nonviolent Crisis Intervention® model:**
            
            **1. Crisis Development Model Response:**
            """)
            
            if avg_severity < 2.5:
                st.success("""
                - **Anxiety Level:** Focus on supportive approaches
                - Use **empathic listening** and validate feelings
                - Provide choices to restore sense of control
                - Maintain calm, non-threatening body language
                """)
            elif avg_severity < 3.5:
                st.warning("""
                - **Defensive Level:** Implement de-escalation strategies
                - Set clear, simple limits using CPI's SETM (Set limit, Explain reason, offer choices, Time to decide)
                - Maintain safe distance (1.5-3 arm lengths)
                - Use **paraverbal communication** (tone, pace, volume)
                - Avoid power struggles
                """)
            else:
                st.error("""
                - **Risk Behavior/Crisis Level:** Priority on safety
                - Follow **Crisis Management Plan**
                - Ensure team support is available
                - Remove others from the area if needed to ensure safety
                - Post-crisis therapeutic rapport rebuilding essential
                """)
            
            st.markdown(f"""
            **2. Pattern-Specific CPI Strategies for "{top_behavior}":**
            """)
            
            if "Verbal Refusal" in top_behavior or "Non-Compliance" in top_behavior:
                st.markdown("""
                - **Directive vs. Choice:** Replace demands with structured choices
                - "You need to complete this work" → "Would you like to start with question 1 or 3?"
                - Use **proxemics** (personal space zones) - approach from side, not head-on
                - Apply **Wait Time** - allow 5-10 seconds for processing
                """)
            elif "Elopement" in top_behavior or "Attempt to Leave" in top_behavior:
                st.markdown("""
                - **Prevention:** Implement environmental modifications (clear sightlines, secured perimeters)
                - **Early Warning Signs:** Document precursor behaviors (pacing, looking at exits)
                - **Rational Detachment:** Staff remain calm, use invitational language
                - Develop **Safety Plan** with clear roles for team members
                """)
            elif "Aggression" in top_behavior or "Property Destruction" in top_behavior:
                st.markdown("""
                - **Staff Safety First:** Maintain safe distance, position near exits
                - **Environmental Assessment:** Remove potential weapons/projectiles
                - **Team Response:** Two-person minimum for high-risk situations
                - **Verbal De-escalation:** Use low, calm tone; simple phrases; avoid questions
                - **Postvention:** Therapeutic rapport re-building within 24 hours
                """)
            else:
                st.markdown("""
                - Apply **Integrated Experience** - meet student's needs holistically
                - Focus on **Care, Welfare, Safety, and Security™** principles
                - Document and analyze behavior patterns for prevention
                """)
        
        # Trauma-Informed Practice
        with st.expander("🧠 **Trauma-Informed Practice (TIP)**", expanded=True):
            st.markdown("""
            **Applying the 6 Key Principles of TIP:**
            
            **1. Safety (Physical & Psychological):**
            """)
            st.info(f"""
            - **Environmental Safety:** Review {top_location} for sensory triggers
            - Create predictable routines, especially during {top_session}
            - Establish visual schedules and clear expectations
            - Provide a designated 'safe space' for regulation
            """)
            
            st.markdown("""
            **2. Trustworthiness & Transparency:**
            """)
            st.info("""
            - Explain all interventions and consequences in advance
            - Follow through consistently on promises
            - Avoid surprises or sudden changes in routine
            - Use "we" language to build collaborative relationship
            """)
            
            st.markdown("""
            **3. Peer Support & Connection:**
            """)
            st.info("""
            - Facilitate positive peer relationships in structured activities
            - Consider peer mentoring program
            - Use restorative practices after incidents
            - Build sense of belonging in school community
            """)
            
            st.markdown(f"""
            **4. Collaboration & Mutuality:**
            - Develop **Student Voice Plan** - involve student in behavior goal setting
            - Given pattern shows triggers around "{top_antecedent}", collaborate on coping strategies
            - Regular check-ins: "What's working? What's not?"
            - Share power appropriately through meaningful choices
            """)
            
            st.markdown("""
            **5. Empowerment & Choice:**
            """)
            st.info("""
            - Offer structured choices throughout the day
            - Teach and practice self-advocacy skills
            - Recognize and celebrate small successes
            - Build on student's strengths and interests
            """)
            
            st.markdown("""
            **6. Cultural, Historical & Gender Responsiveness:**
            """)
            st.info("""
            - Consider cultural background in intervention selection
            - Acknowledge historical trauma if relevant
            - Respect identity and individual needs
            - Engage family in culturally responsive ways
            """)
        
        # Berry Street Education Model (BSEM)
        with st.expander("🌱 **Berry Street Education Model (BSEM)**", expanded=True):
            st.markdown("""
            **Implementing BSEM's 5 Domains:**
            
            **Domain 1: Body** *(Regulate the body to access learning)*
            """)
            st.success(f"""
            - **Movement Breaks:** Given incidents peak at {top_session}, schedule regular movement breaks
            - **Sensory Tools:** Provide fidgets, wobble cushions, weighted items
            - **Breathing Techniques:** Teach "Breathe, Relax, Feel, Watch, Listen"
            - **Physical Activity:** Start day with 10-15 min movement
            - **Regulation Stations:** Create designated areas with regulation tools
            """)
            
            st.markdown("""
            **Domain 2: Relationship** *(Build positive relationships)*
            """)
            st.success("""
            - **Morning Welcome:** Personalized greeting to start each day
            - **2x10 Strategy:** 2 minutes per day for 10 days discussing student's interests
            - **Repair & Reconnect:** After incidents, prioritize relationship repair
            - **Key Adult Connection:** Ensure consistent, trusted adult available
            - **Relationship Mapping:** Identify safe, supportive adults in student's life
            """)
            
            st.markdown(f"""
            **Domain 3: Stamina** *(Build persistence and work capacity)*
            - **Task Chunking:** Given {top_behavior}, break tasks into 5-10 minute segments
            - **Success Tracking:** Visual progress charts
            - **Growth Mindset:** Reframe failures as learning opportunities
            - **Incremental Goals:** Set achievable daily targets
            - **Celebrate Effort:** Acknowledge persistence over outcomes
            """)
            
            st.markdown("""
            **Domain 4: Engagement** *(Foster intrinsic motivation)*
            """)
            st.success("""
            - **Student Interests:** Embed preferred topics into learning
            - **Real-World Connections:** Link curriculum to student's life
            - **Positive Priming:** Start sessions with success activities
            - **Flow Experiences:** Balance challenge with skill level
            - **Voice & Agency:** Student input on learning activities
            """)
            
            st.markdown("""
            **Domain 5: Character** *(Develop ethical thinking & agency)*
            """)
            st.success("""
            - **Values Education:** Teach and model BSEM values (respect, courage, trust, etc.)
            - **Social-Emotional Learning:** Explicit SEL lessons 3x weekly
            - **Restorative Practices:** Focus on harm repair, not punishment
            - **Leadership Opportunities:** Give student responsibility roles
            - **Community Contribution:** Connect to wider school community
            """)
        
        # SMART Training
        with st.expander("🎓 **SMART (Stress Management and Resilience Training)**", expanded=True):
            st.markdown("""
            **SMART Program Integration:**
            
            **1. Self-Regulation Skills:**
            """)
            st.info("""
            - **Square Breathing:** Teach 4-4-4-4 breathing pattern
            - **Mindful Moments:** 2-3 minute mindfulness at transitions
            - **Body Scan:** Help identify early warning signs of stress
            - **Grounding Techniques:** 5-4-3-2-1 sensory exercise
            - **Progressive Muscle Relaxation:** For high-stress periods
            """)
            
            st.markdown(f"""
            **2. Cognitive Strategies:**
            - **Thought Stopping:** Interrupt negative thought patterns
            - **Positive Self-Talk:** Co-develop affirming phrases
            - **Reframing:** Practice seeing situations differently
            - **Problem-Solving Steps:** Teach structured approach to challenges
            - **Emotional Literacy:** Build vocabulary for feelings (given pattern with {top_antecedent})
            """)
            
            st.markdown("""
            **3. Building Resilience:**
            """)
            st.info("""
            - **Strengths Focus:** Weekly identification of personal strengths
            - **Gratitude Practice:** Daily "3 good things" reflection
            - **Social Support:** Identify and strengthen support network
            - **Hope & Optimism:** Set and visualize achievable goals
            - **Stress Awareness:** Create personalized "stress thermometer"
            """)
            
            st.markdown(f"""
            **4. Environmental Management:**
            - **Trigger Awareness:** Document and plan for {top_antecedent}
            - **Predictability:** Consistent routines, especially {top_day}s
            - **Warning Systems:** Develop escalation/de-escalation plans
            - **Coping Card:** Portable reminder of strategies
            - **Support Signal:** Non-verbal way to request help
            """)
        
        # Australian Curriculum Integration
        with st.expander("📚 **Australian Curriculum Integration**", expanded=True):
            st.markdown("""
            **Personal & Social Capability (General Capability):**
            
            **Self-Awareness:**
            """)
            st.success(f"""
            - **Identify Emotions:** Explicitly teach emotional vocabulary
            - **Recognize Strengths:** Student identifies their own strengths weekly
            - **Understand Impacts:** Reflect on how behavior affects others
            - **Development Focus:** Age-appropriate for Grade {student['grade']}
            """)
            
            st.markdown("""
            **Self-Management:**
            """)
            st.success("""
            - **Express Emotions Appropriately:** Teach communication skills
            - **Develop Self-Discipline:** Practice impulse control strategies
            - **Set Goals:** Weekly achievable behavioral goals
            - **Work Independently:** Build stamina with scaffolded independence
            - **Become Resilient:** Frame setbacks as learning opportunities
            """)
            
            st.markdown("""
            **Social Awareness:**
            """)
            st.success("""
            - **Appreciate Diversity:** Value differences in others
            - **Understand Relationships:** Teach healthy relationship skills
            - **Contribute to Groups:** Structured collaborative activities
            - **Perspective-Taking:** "How might others feel?" discussions
            """)
            
            st.markdown("""
            **Social Management:**
            """)
            st.success("""
            - **Communicate Effectively:** Practice assertive (not aggressive) communication
            - **Work Collaboratively:** Structured partner/group work
            - **Make Decisions:** Teach decision-making framework
            - **Negotiate & Resolve Conflict:** Restorative circles after incidents
            - **Develop Leadership:** Assign meaningful leadership roles
            """)
            
            st.markdown("""
            **Cross-Curriculum Priority Links:**
            """)
            st.info("""
            - **Aboriginal & Torres Strait Islander Histories/Cultures:** If relevant, incorporate cultural connections
            - **Asia & Australia's Engagement:** Cultural awareness activities
            - **Sustainability:** Build connection to environment/community
            """)
            
            st.markdown(f"""
            **Health & Physical Education (HPE) Links:**
            - **Movement & Physical Activity:** Daily structured movement (addressing {top_session} patterns)
            - **Personal, Social & Community Health:**
              - Emotional regulation skills
              - Help-seeking behaviors
              - Positive relationships
              - Mental health awareness
            - **Communicating & Interacting:** Social skills practice
            """)
        
        st.markdown("---")
        
        # Recommended Action Plan
        st.markdown("### 📋 Recommended Action Plan")
        
        with st.container(border=True):
            st.markdown("#### Immediate Actions (Next 1-2 Weeks):")
            st.markdown(f"""
            1. **Environmental Modification:** Review {top_location} for triggers and implement changes
            2. **Relationship Building:** Initiate daily 2-minute connection conversations
            3. **Regulation Tools:** Introduce 3 self-regulation strategies aligned with SMART training
            4. **Visual Supports:** Create visual schedule and expectations chart
            5. **Team Meeting:** Brief key staff on patterns and consistent response strategies
            """)
            
            st.markdown(f"""
            #### Short-Term Goals (1 Month):
            1. **CPI Strategy Implementation:** Apply de-escalation techniques for "{top_behavior}"
            2. **BSEM Domain Focus:** Prioritize "Body" and "Relationship" domains
            3. **Functional Behavior Assessment (FBA):** Consider formal FBA given {len(student_incidents)} incidents
            4. **Positive Behavior Support Plan:** Develop/refine PBS plan with student input
            5. **Data Review:** Weekly check of incident trends to monitor effectiveness
            6. **Family Engagement:** Share progress and strategies with family
            """)
            
            st.markdown("""
            #### Long-Term Goals (Term/Semester):
            1. **Skill Development:** Explicitly teach Australian Curriculum Personal & Social Capabilities
            2. **Trauma-Informed Environment:** Full implementation of TIP across all settings
            3. **Berry Street Domains:** Progressive implementation across all 5 domains
            4. **Peer Relationships:** Facilitate positive peer connections and social skills
            5. **Independence Building:** Gradual fading of support as skills develop
            6. **Transition Planning:** Prepare for next grade level with continuity of supports
            """)
        
        st.markdown("---")
        
        # Success Indicators
        st.markdown("### ✅ Success Indicators to Monitor")
        
        col_suc1, col_suc2 = st.columns(2)
        
        with col_suc1:
            st.markdown("**Leading Indicators (Early Signs):**")
            st.markdown("""
            - ⬆️ Increased use of regulation strategies
            - ⬆️ Requesting breaks before escalation
            - ⬆️ Positive peer interactions
            - ⬆️ Time on task/engagement
            - ⬇️ Frequency of antecedent exposure
            """)
        
        with col_suc2:
            st.markdown("**Lagging Indicators (Outcome Measures):**")
            st.markdown("""
            - ⬇️ Total incident frequency
            - ⬇️ Incident severity levels
            - ⬇️ Critical incidents
            - ⬆️ Academic achievement
            - ⬆️ School attendance/connection
            """)
        
        st.markdown("---")
        
        # Resources
        with st.expander("📖 **Additional Resources & References**"):
            st.markdown("""
            **Crisis Prevention Institute (CPI):**
            - Nonviolent Crisis Intervention® Training Manual
            - CPI's Crisis Development Model℠
            - www.crisisprevention.com
            
            **Trauma-Informed Practice:**
            - SAMHSA's Six Key Principles of Trauma-Informed Approach
            - "Helping Traumatized Children Learn" (Cole et al.)
            - Australian Childhood Foundation trauma resources
            
            **Berry Street Education Model:**
            - Berry Street Education Model Handbook
            - Domain-specific teaching strategies
            - www.berrystreet.org.au/bsem
            
            **SMART Training:**
            - Stress Management and Resilience Training for Educators
            - Mindfulness-based stress reduction resources
            - Penn Resilience Program materials
            
            **Australian Curriculum:**
            - Personal and Social Capability learning continuum
            - Health and Physical Education curriculum documents
            - www.australiancurriculum.edu.au
            
            **Additional Evidence-Based Resources:**
            - Positive Behaviour for Learning (PBL) Australia
            - Zones of Regulation®
            - The Incredible Years® programs
            - Social Thinking® methodology
            - Collaborative & Proactive Solutions (CPS/Think:Kids)
            """)
    
    # Action buttons at bottom
    st.markdown("---")
    st.markdown("### Actions")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("📝 Log New Incident", type="primary", use_container_width=True):
            navigate_to('direct_log_form', student_id=student_id)
    
    with col_act2:
        if st.button("📊 Generate Report", use_container_width=True, type="secondary"):
            with st.spinner("Generating comprehensive report..."):
                try:
                    report_path = generate_student_report(student, student_incidents)
                    if report_path:
                        st.success("✅ Report generated successfully!")
                        with open(report_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Report",
                                data=f,
                                file_name=f"{student['name'].replace(' ', '_')}_Analysis_Report.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                    else:
                        st.info("📋 Report generation is not available in this environment.")
                        st.markdown("""
                        **To generate reports locally:**
                        1. Install Node.js from nodejs.org
                        2. Run: `npm install -g docx`
                        3. Run the app locally with `streamlit run behaviour_support_app.py`
                        
                        **Alternative:** You can export your data as CSV for now.
                        """)
                except Exception as e:
                    logger.error(f"Error generating report: {e}")
                    st.error("Report generation unavailable in this environment. Please use local installation for reports.")
    
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
