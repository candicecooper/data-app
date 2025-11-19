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

# --- RUNTIME MODE SWITCH ---

SANDBOX_MODE = True  # 🔁 Set to False for live Supabase mode, True for demo/sandbox

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
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

# SANDBOX BANNER
if SANDBOX_MODE:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                padding: 1rem; 
                border-radius: 8px; 
                text-align: center; 
                margin-bottom: 1rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">
            🎭 SANDBOX MODE - Using Mock Data Only
        </h2>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            All students, staff and incidents are synthetic. Nothing is written to Supabase in this mode.
        </p>
    </div>
    """, unsafe_allow_html=True)

PLOTLY_THEME = 'plotly'

# Staff roles available
STAFF_ROLES = ['JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO']

# Program options
PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

# Grade options by program
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

# --- DATA LOADING FUNCTIONS (SUPABASE, LIVE MODE) ---

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

# --- SANDBOX MOCK DATA GENERATORS ---

def generate_mock_students() -> List[Dict[str, Any]]:
    """Generate mock students for sandbox mode."""
    students = [
        # JP Program
        {'id': 'student_JP001', 'first_name': 'Emma', 'last_name': 'Thompson', 'name': 'Emma Thompson',
         'grade': 'R', 'dob': '2018-03-15', 'edid': 'JP001', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_JP002', 'first_name': 'Oliver', 'last_name': 'Martinez', 'name': 'Oliver Martinez',
            'grade': 'Y1', 'dob': '2017-07-22', 'edid': 'JP002', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_JP003', 'first_name': 'Sophia', 'last_name': 'Wilson', 'name': 'Sophia Wilson',
            'grade': 'Y2', 'dob': '2016-11-08', 'edid': 'JP003', 'program': 'JP', 'profile_status': 'Complete', 'archived': False},

        # PY Program
        {'id': 'student_PY001', 'first_name': 'Liam', 'last_name': 'Chen', 'name': 'Liam Chen',
            'grade': 'Y3', 'dob': '2015-05-30', 'edid': 'PY001', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_PY002', 'first_name': 'Ava', 'last_name': 'Rodriguez', 'name': 'Ava Rodriguez',
            'grade': 'Y4', 'dob': '2014-09-12', 'edid': 'PY002', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_PY003', 'first_name': 'Noah', 'last_name': 'Brown', 'name': 'Noah Brown',
            'grade': 'Y6', 'dob': '2012-01-25', 'edid': 'PY003', 'program': 'PY', 'profile_status': 'Complete', 'archived': False},

        # SY Program
        {'id': 'student_SY001', 'first_name': 'Isabella', 'last_name': 'Garcia', 'name': 'Isabella Garcia',
            'grade': 'Y7', 'dob': '2011-04-17', 'edid': 'SY001', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_SY002', 'first_name': 'Ethan', 'last_name': 'Davis', 'name': 'Ethan Davis',
            'grade': 'Y9', 'dob': '2009-12-03', 'edid': 'SY002', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
        {'id': 'student_SY003', 'first_name': 'Mia', 'last_name': 'Anderson', 'name': 'Mia Anderson',
            'grade': 'Y11', 'dob': '2007-08-20', 'edid': 'SY003', 'program': 'SY', 'profile_status': 'Complete', 'archived': False},
    ]
    return students

def generate_mock_staff() -> List[Dict[str, Any]]:
    """Generate mock staff for sandbox mode."""
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
    """Generate mock incidents for sandbox mode with realistic patterns."""
    students = generate_mock_students()
    student_ids = [s['id'] for s in students]
    staff_names = [s['name'] for s in generate_mock_staff()]

    behaviours = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Physical Aggression (Staff)']
    locations = ['JP Classroom', 'PY Classroom', 'SY Classroom', 'Yard', 'Playground', 'Library']
    antecedents = [
        'Requested to transition activity',
        'Given instruction/demand (Academic)',
        'Peer conflict/Teasing',
        'Unstructured free time (Recess/Lunch)'
    ]
    interventions = [
        'Prompted use of coping skill (e.g., breathing)',
        'Redirection to a preferred activity',
        'Offered a break/Choice of task',
        'Staff de-escalation script/Verbal coaching'
    ]

    base_date = datetime.now() - timedelta(days=90)
    incidents = []

    for i in range(70):
        student_id = random.choice(student_ids)
        inc_date = base_date + timedelta(days=random.randint(0, 85))

        # More incidents in school hours
        hour = random.choices([9, 10, 11, 12, 13, 14], weights=[2, 3, 2, 1, 2, 3])[0]
        minute = random.randint(0, 59)
        inc_time = time(hour=hour, minute=minute)

        severity = random.choices([1, 2, 3, 4, 5], weights=[4, 3, 2, 1, 0.5])[0]
        is_critical = severity >= 3  # 🔴 Your threshold

        incident = {
            'id': f'mock_inc_{i+1}',
            'student_id': student_id,
            'incident_date': inc_date.strftime('%Y-%m-%d'),
            'incident_time': inc_time.strftime('%H:%M:%S'),
            'day_of_week': inc_date.strftime('%A'),
            'session': (
                "Morning (9:00am - 11:00am)" if time(9, 0) <= inc_time <= time(11, 0) else
                "Middle (11:01am - 1:00pm)" if time(11, 0, 1) <= inc_time <= time(13, 0) else
                "Afternoon (1:01pm - 2:45pm)" if time(13, 0, 1) <= inc_time <= time(14, 45) else
                "Outside School Hours (N/A)"
            ),
            'location': random.choice(locations),
            'reported_by_name': random.choice(staff_names),
            'reported_by_id': None,
            'reported_by_role': None,
            'is_special_staff': False,
            'behaviour_type': random.choice(behaviours),
            'antecedent': random.choice(antecedents),
            'intervention': random.choice(interventions),
            'support_type': random.choice(['1:1 (Individual Support)', 'Small Group (3-5 students)']),
            'severity': severity,
            'description': 'Mock incident for demo purposes.',
            'is_critical': is_critical,
        }
        incident['date'] = incident['incident_date']
        incident['time'] = incident['incident_time']
        incident['day'] = incident['day_of_week']

        incidents.append(incident)

    return incidents

# --- SESSION STATE INITIALIZATION ---

def initialize_session_state():
    """Initialize all session state variables from Supabase or sandbox."""
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data..."):
            if SANDBOX_MODE:
                st.session_state.students_list = generate_mock_students()
                st.session_state.staff_list = generate_mock_staff()
                st.session_state.incidents = generate_mock_incidents()
                st.session_state.system_settings = {}
            else:
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

    if 'critical_abch_records' not in st.session_state:
        st.session_state.critical_abch_records = []

    if 'current_incident_for_abch' not in st.session_state:
        st.session_state.current_incident_for_abch = None

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
        return [s for s in st.session_state.staff_list if s.get('active', False) and not s.get('archived', False)]
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

def add_staff_member(first_name: str, last_name: str, email: str, role: str) -> bool:
    """Adds a new staff member (Supabase in live, memory-only in sandbox)."""
    try:
        if not first_name or not first_name.strip():
            raise ValidationError("First name cannot be empty", "Please enter a first name")
        if not last_name or not last_name.strip():
            raise ValidationError("Last name cannot be empty", "Please enter a last name")
        if not email or not email.strip():
            raise ValidationError("Email cannot be empty", "Please enter an email address")
        if '@' not in email and not SANDBOX_MODE:
            raise ValidationError("Invalid email", "Please enter a valid email address")
        if not role or role == "--- Select Role ---":
            raise ValidationError("Role must be selected", "Please select a role")
        
        full_name = f"{first_name.strip()} {last_name.strip()}"
        
        existing_email = [
            s for s in st.session_state.staff_list
            if s.get('email', '').lower() == email.strip().lower() and not s.get('archived', False)
        ]
        if existing_email:
            raise ValidationError("Duplicate email", "A staff member with this email already exists")
        
        email_clean = email.strip().lower()
        staff_id = 'staff_' + email_clean.replace('@', '_').replace('.', '_') if email_clean else f'staff_{uuid.uuid4().hex[:8]}'
        
        new_staff = {
            'id': staff_id,
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'name': full_name,
            'email': email_clean,
            'role': role,
            'active': True,
            'archived': False
        }
        
        if SANDBOX_MODE:
            st.session_state.staff_list.append(new_staff)
            logger.info(f"[SANDBOX] Added staff member: {full_name} ({email}, {role})")
            return True
        else:
            supabase = get_supabase_client()
            response = supabase.table('staff').insert(new_staff).execute()
            if response.data:
                st.session_state.staff_list.append(response.data[0])
                logger.info(f"Added staff member: {full_name} ({email}, {role})")
                return True
            else:
                raise AppError("Database insert failed", "Could not add staff member")
        
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
        
        if SANDBOX_MODE:
            staff['archived'] = True
            staff['active'] = False
            staff['archived_date'] = datetime.now().isoformat()
            logger.info(f"[SANDBOX] Archived staff member: {staff['name']}")
            return True
        else:
            supabase = get_supabase_client()
            response = supabase.table('staff').update({
                'archived': True,
                'active': False,
                'archived_date': datetime.now().isoformat()
            }).eq('id', staff_id).execute()
            
            if response.data:
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
    """Unarchives a staff member."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot unarchive: staff member not found")
        
        if SANDBOX_MODE:
            staff['archived'] = False
            staff['active'] = True
            logger.info(f"[SANDBOX] Unarchived staff member: {staff['name']}")
            return True
        else:
            supabase = get_supabase_client()
            response = supabase.table('staff').update({
                'archived': False,
                'active': True
            }).eq('id', staff_id).execute()
            
            if response.data:
                staff['archived'] = False
                staff['active'] = True
                logger.info(f"Unarchived staff member: {staff['name']}")
                return True
            else:
                raise AppError("Database update failed", "Could not unarchive staff member")
        
    except Exception as e:
        logger.error(f"Error unarchiving staff: {e}")
        raise AppError("Failed to unarchive staff member", "Could not unarchive staff member. Please try again.")

def add_student(first_name: str, last_name: str, dob: datetime.date, program: str, grade: str, edid: str) -> bool:
    """Adds a new student."""
    try:
        if not first_name or not first_name.strip():
            raise ValidationError("First name cannot be empty", "Please enter a first name")
        if not last_name or not last_name.strip():
            raise ValidationError("Last name cannot be empty", "Please enter a last name")
        if not program or program == "--- Select Program ---":
            raise ValidationError("Program must be selected", "Please select a program")
        if not grade or grade == "--- Select Grade ---":
            raise ValidationError("Grade must be selected", "Please select a grade")
        if not dob:
            raise ValidationError("Date of birth is required", "Please enter date of birth")
        if not edid or not edid.strip():
            raise ValidationError("EDID is required", "Please enter EDID")
        
        full_name = f"{first_name.strip()} {last_name.strip()}"
        
        existing_edid = [
            s for s in st.session_state.students_list
            if s.get('edid', '').upper() == edid.strip().upper() and not s.get('archived', False)
        ]
        if existing_edid:
            raise ValidationError("Duplicate EDID", f"A student with EDID {edid} already exists")
        
        if dob > datetime.now().date():
            raise ValidationError("Invalid date of birth", "Date of birth cannot be in the future")
        
        student_id = 'student_' + edid.strip().upper().replace(' ', '_')
        
        new_student = {
            'id': student_id,
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'name': full_name,
            'dob': dob.strftime('%Y-%m-%d'),
            'program': program,
            'grade': grade,
            'edid': edid.strip().upper(),
            'profile_status': 'Draft',
            'archived': False
        }
        
        if SANDBOX_MODE:
            st.session_state.students_list.append(new_student)
            logger.info(f"[SANDBOX] Added student: {full_name} (EDID: {edid}, Program: {program})")
            return True
        else:
            supabase = get_supabase_client()
            response = supabase.table('students').insert(new_student).execute()
            
            if response.data:
                st.session_state.students_list.append(response.data[0])
                logger.info(f"Added student: {full_name} (EDID: {edid}, Program: {program})")
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

# --- AUTHENTICATION FUNCTIONS ---

def verify_login(email: str) -> Optional[Dict[str, Any]]:
    """Verifies if email exists in staff database (or mock staff in sandbox)."""
    try:
        if not email or not email.strip():
            return None
        
        email = email.strip().lower()
        
        # Sandbox shortcut: "demo" logs in as Admin
        if SANDBOX_MODE and email in ("demo", "demo@demo.edu.au"):
            staff = [s for s in st.session_state.staff_list if s.get('role') == 'ADM']
            return staff[0] if staff else None
        
        staff_member = next(
            (s for s in st.session_state.staff_list
             if s.get('email', '').lower() == email and not s.get('archived', False)),
            None
        )
        
        return staff_member
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None

# --- VALIDATION FUNCTIONS ---

def validate_incident_form(location, reported_by, behaviour_type, severity_level, incident_date, incident_time):
    """Validates incident form."""
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

def validate_abch_form(context, location, behaviour_desc, consequence, manager_notify, parent_notify):
    """Validates ABCH form."""
    errors = []
    
    if not location or location.strip() == "":
        errors.append("Location is required")
    if not context or context.strip() == "":
        errors.append("Context is required")
    if not behaviour_desc or behaviour_desc.strip() == "":
        errors.append("behaviour description is required")
    if not consequence or consequence.strip() == "":
        errors.append("Consequences are required")
    if not manager_notify:
        errors.append("Line Manager notification required")
    if not parent_notify:
        errors.append("Parent notification required")
    
    if errors:
        raise ValidationError("ABCH validation failed", "Please correct: " + ", ".join(errors))

# --- LOGIN PAGE ---

@handle_errors("Unable to load login page")
def render_login_page():
    """Renders the login page with email authentication."""
    
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
        with st.container(border=True):
            st.markdown("### 🔑 Login")
            
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com (or 'demo' in sandbox)",
                key="login_email"
            )
            
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
            
            st.markdown("---")
            st.caption("💡 **Note:** Only registered staff members can access this system. In Sandbox, use email 'demo' to log in as Admin.")

# --- LANDING PAGE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    """Renders sleek landing page."""
    
    # User info and logout button at top
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
    
    # Spectacular animated header
    st.markdown("""
    <style>
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        background: rgba(255, 255, 255, 0.15);
        -webkit-backdrop-filter: blur(20px);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
    }
    
    .hero-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: gradient-shift 5s ease infinite;
        letter-spacing: -0.03em;
        line-height: 1.2;
        text-shadow: 0 0 40px rgba(167, 139, 250, 0.5);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .hero-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .feature-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        margin: 0.5rem;
        font-size: 0.9rem;
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .divider-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        margin: 3rem 0;
        border-radius: 2px;
    }
    </style>
    
    <div class="hero-section">
        <div class="hero-icon">📊✨</div>
        <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
        <p class="hero-subtitle">Transform Student Outcomes with Evidence-Based Insights</p>
        <p class="hero-tagline">Comprehensive incident tracking, powerful analytics, and AI-driven recommendations aligned with CPI, Trauma-Informed Practice, BSEM, and the Australian Curriculum</p>
        <div style="margin-top: 2rem;">
            <span class="feature-badge">📈 Real-time Analytics</span>
            <span class="feature-badge">🎯 Evidence-Based</span>
            <span class="feature-badge">🔒 Secure Database</span>
            <span class="feature-badge">📱 Cloud-Based</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📚 Select Your Program")
    st.caption("Choose a program to view students, log incidents, and access analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎨 Junior Primary")
        st.caption("Reception - Year 2")
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='JP')
    
    with col2:
        st.markdown("#### 📖 Primary Years")
        st.caption("Year 3 - Year 6")
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='PY')
    
    with col3:
        st.markdown("#### 🎓 Senior Years")
        st.caption("Year 7 - Year 12")
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='SY')
    
    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    st.caption("Fast access to common tasks")
    
    col_quick1, col_quick2 = st.columns(2)
    
    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        st.caption("Select a student and immediately log a new incident")
        all_active_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        student_options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x['name'],
            key="quick_log_student",
            label_visibility="collapsed"
        )
        
        if selected_student and selected_student['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to('direct_log_form', student_id=selected_student['id'])
    
    with col_quick2:
        st.markdown("#### 🔐 Admin Portal")
        st.caption("Manage staff, students, and system settings")
        st.markdown("<br>", unsafe_allow_html=True)
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
                            
                            incident_count = len([
                                inc for inc in st.session_state.get('incidents', [])
                                if inc.get('student_id') == student['id']
                            ])
                            st.metric("Incidents", incident_count)
                            
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button("👁️ View", key=f"view_{student['id']}", use_container_width=True):
                                    navigate_to('student_analysis', student_id=student['id'])
                            with col_log:
                                if st.button("📝 Log", key=f"log_{student['id']}", use_container_width=True):
                                    navigate_to('direct_log_form', student_id=student['id'])
    
    with tab2:
        archived_students = [
            s for s in st.session_state.students_list
            if s.get('program') == program and s.get('archived', False)
        ]
        
        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("Students who have completed the program - read-only")
            
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**Profile Status:** {student.get('profile_status', 'N/A')}")
                    st.markdown(f"**EDID:** {student.get('edid', 'N/A')}")
                    
                    incident_count = len([
                        inc for inc in st.session_state.get('incidents', [])
                        if inc.get('student_id') == student['id']
                    ])
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
        st.caption(f"Current mode: {'SANDBOX' if SANDBOX_MODE else 'LIVE'}")
        st.info("Settings functionality - to be implemented")

@handle_errors("Unable to load staff management")
def render_staff_management():
    """Renders staff management section."""
    
    st.markdown("## 👥 Staff Management")
    st.markdown("---")
    
    staff_tab1, staff_tab2 = st.tabs(["✅ Active Staff", "📦 Archived Staff"])
    
    with staff_tab1:
        st.markdown("### Add New Staff Member")
        
        col_add1, col_add2, col_add3, col_add4 = st.columns([2, 2, 3, 2])
        
        with col_add1:
            new_staff_first_name = st.text_input("First Name", key="new_staff_first_name", placeholder="First name")
        
        with col_add2:
            new_staff_last_name = st.text_input("Last Name", key="new_staff_last_name", placeholder="Last name")
        
        with col_add3:
            new_staff_email = st.text_input("Email", key="new_staff_email", placeholder="email@example.com")
        
        with col_add4:
            new_staff_role = st.selectbox(
                "Role",
                options=["--- Select Role ---"] + STAFF_ROLES,
                key="new_staff_role"
            )
        
        col_add_btn = st.columns([4, 1])
        with col_add_btn[1]:
            if st.button("➕ Add Staff", type="primary", use_container_width=True):
                try:
                    if add_staff_member(new_staff_first_name, new_staff_last_name, new_staff_email, new_staff_role):
                        st.success(f"✅ Added {new_staff_first_name} {new_staff_last_name}")
                        st.rerun()
                except (ValidationError, AppError) as e:
                    st.error(e.user_message)
        
        st.markdown("---")
        st.markdown("### Current Active Staff")
        
        active_staff = [s for s in st.session_state.staff_list if not s.get('archived', False)]
        
        if not active_staff:
            st.info("No active staff members")
        else:
            staff_by_role = {}
            for staff in active_staff:
                role = staff.get('role', 'Unknown')
                staff_by_role.setdefault(role, []).append(staff)
            
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
                                staff_key = staff.get('id') or staff.get('email') or f"staff_{staff['name']}"
                                if st.button("🗄️ Archive", key=f"archive_{staff_key}", use_container_width=True):
                                    try:
                                        if archive_staff_member(staff.get('id')):
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
                    
                    staff_key = staff.get('id') or staff.get('email') or f"staff_{staff['name']}"
                    if st.button("♻️ Restore Staff Member", key=f"restore_{staff_key}"):
                        try:
                            if unarchive_staff_member(staff.get('id')):
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
    
    col_add1, col_add2, col_add3, col_add4, col_add5 = st.columns([2, 2, 1.5, 1, 1])
    
    with col_add1:
        new_student_first_name = st.text_input("First Name", key="new_student_first_name", placeholder="First name")
    
    with col_add2:
        new_student_last_name = st.text_input("Last Name", key="new_student_last_name", placeholder="Last name")
    
    with col_add3:
        new_student_dob = st.date_input(
            "Date of Birth (DD/MM/YYYY)",
            key="new_student_dob",
            min_value=datetime(1990, 1, 1).date(),
            max_value=datetime.now().date(),
            value=datetime(2015, 1, 1).date(),
            format="DD/MM/YYYY"
        )
    
    with col_add4:
        new_student_program = st.selectbox(
            "Program",
            options=["--- Select Program ---"] + PROGRAM_OPTIONS,
            key="new_student_program"
        )
    
    with col_add5:
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
        st.markdown("##")
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            try:
                if add_student(
                    new_student_first_name,
                    new_student_last_name,
                    new_student_dob,
                    new_student_program,
                    new_student_grade,
                    new_student_edid
                ):
                    st.success(f"✅ Added {new_student_first_name} {new_student_last_name} to {new_student_program} Program")
                    st.rerun()
            except (ValidationError, AppError) as e:
                st.error(e.user_message)
    
    st.markdown("---")
    st.markdown("### Current Students by Program")
    
    program_tabs = st.tabs(["📘 Junior Primary", "📗 Primary Years", "📙 Senior Years", "📚 All Students"])
    
    programs = ['JP', 'PY', 'SY']
    
    for idx, program in enumerate(programs):
        with program_tabs[idx]:
            students_in_program = get_students_by_program(program, include_archived=False)
            
            if not students_in_program:
                st.info(f"No students currently in {program} program")
            else:
                st.markdown(f"**Total Students:** {len(students_in_program)}")
                
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
    
    with program_tabs[3]:
        all_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        
        if not all_students:
            st.info("No students in the system")
        else:
            st.markdown(f"**Total Students Across All Programs:** {len(all_students)}")
            
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
    """Placeholder: report generation (left as-is)."""
    try:
        logger.info("Report generation not implemented in this sandbox/live toggle version.")
        return None
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
    
    options = [{'id': None, 'name': '--- Select Staff ---', 'role': None, 'special': False}]
    
    if include_special_options:
        options.append({'id': 'TRT', 'name': 'TRT (Relief Teacher)', 'role': 'TRT', 'special': True})
        options.append({'id': 'External_SSO', 'name': 'External SSO', 'role': 'External SSO', 'special': True})
        options.append({'id': 'divider', 'name': '─────────────────', 'role': None, 'special': False})
    
    options.extend([{**s, 'special': False} for s in active_staff])
    selectable_options = [opt for opt in options if opt['id'] != 'divider']
    
    selected = st.selectbox(
        label,
        options=selectable_options,
        format_func=lambda x: f"{x['name']}" + (f" ({x['role']})" if x['role'] and not x.get('special') else ""),
        key=key
    )
    
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
            incident_date = st.date_input("Date of Incident (DD/MM/YYYY)", value=datetime.now(), format="DD/MM/YYYY")
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)
        
        with col2:
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True
            )
        
        st.markdown("### behaviour Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            behaviour_type = st.selectbox(
                "behaviour Type",
                options=["--- Select behaviour ---"] + behaviourS_FBA
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
                if reported_by and reported_by.get('name_missing'):
                    st.error("Please enter the name for the selected staff type (TRT or External SSO)")
                    return
                
                validate_incident_form(
                    location, reported_by, behaviour_type,
                    severity_level, incident_date, incident_time
                )
                
                incident_time_obj = datetime.combine(incident_date, incident_time)
                session = get_session_window(incident_time)
                is_critical = severity_level >= 3  # 🔴 Threshold you requested
                
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
                    'behaviour_type': behaviour_type,
                    'antecedent': antecedent,
                    'intervention': intervention,
                    'support_type': support_type,
                    'severity': severity_level,
                    'description': description,
                    'is_critical': is_critical
                }
                
                # Save incident
                if SANDBOX_MODE:
                    saved_incident = new_incident.copy()
                    saved_incident['id'] = saved_incident.get('id') or f"local_{uuid.uuid4().hex[:8]}"
                    saved_incident['date'] = saved_incident['incident_date']
                    saved_incident['time'] = saved_incident['incident_time']
                    saved_incident['day'] = saved_incident['day_of_week']
                    st.session_state.incidents.append(saved_incident)
                else:
                    supabase = get_supabase_client()
                    response = supabase.table('incidents').insert(new_incident).execute()
                    if response.data:
                        saved_incident = response.data[0]
                        saved_incident['date'] = saved_incident['incident_date']
                        saved_incident['time'] = saved_incident['incident_time']
                        saved_incident['day'] = saved_incident['day_of_week']
                        st.session_state.incidents.append(saved_incident)
                    else:
                        st.error("Failed to save incident to database")
                        return

                st.success("✅ Incident report submitted successfully!")
                
                # 🔴 If severity >= 3, immediately go to Critical Incident ABCH form
                if is_critical:
                    st.warning("⚠️ This incident meets the Critical Incident threshold (Severity 3–5). Opening ABCH form...")
                    st.session_state.current_incident_for_abch = saved_incident
                    st.session_state.selected_student_id = student_id
                    navigate_to('critical_incident_abch', student_id=student_id)
                    return
                
                col_another, col_return = st.columns(2)
                with col_another:
                    if st.button("➕ Log Another Incident", use_container_width=True):
                        st.rerun()
                with col_return:
                    if st.button("↩️ Return to Student List", use_container_width=True):
                        navigate_to('program_students', program=student['program'])
                        
            except ValidationError as e:
                st.error(e.user_message)

# --- CRITICAL INCIDENT ABCH FORM ---

@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    """Render a simple Critical Incident ABCH form fed by the triggering incident."""
    incident = st.session_state.get('current_incident_for_abch')
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id) if student_id else None
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🚨 Critical Incident ABCH Form")
        if student:
            st.caption(f"Student: {student['name']} | Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            if student:
                navigate_to('student_analysis', student_id=student_id)
            else:
                navigate_to('landing')
    
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
            st.markdown(f"**Brief Description:** {incident.get('description')}")
    
    st.markdown("### ABCH Details")
    
    with st.form("abch_form"):
        context = st.text_area("Antecedent / Context", height=100)
        behaviour_desc = st.text_area("Behaviour Description (detailed)", height=120)
        consequence = st.text_area("Consequence / Response", height=120)
        location = st.text_input("Location (confirm or update)", value=incident.get('location', ''), max_chars=100)
        
        manager_notify = st.checkbox("Line Manager notified")
        parent_notify = st.checkbox("Parent/Carer notified")
        
        submitted = st.form_submit_button("Save ABCH Record", type="primary", use_container_width=True)
        
        if submitted:
            try:
                validate_abch_form(context, location, behaviour_desc, consequence, manager_notify, parent_notify)
                
                abch_record = {
                    'id': f"abch_{uuid.uuid4().hex[:8]}",
                    'incident_id': incident.get('id'),
                    'student_id': student_id,
                    'context': context,
                    'location': location,
                    'behaviour_desc': behaviour_desc,
                    'consequence': consequence,
                    'manager_notify': manager_notify,
                    'parent_notify': parent_notify,
                    'created_at': datetime.now().isoformat()
                }
                
                # For now, keep ABCH records in memory only (even in live mode)
                st.session_state.critical_abch_records.append(abch_record)
                
                st.success("✅ Critical Incident ABCH record saved.")
                st.info("ABCH records are currently stored in memory. You can later connect this to a Supabase 'abch_records' table if desired.")
                
            except ValidationError as e:
                st.error(e.user_message)

# --- STUDENT ANALYSIS ---

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
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])
    
    st.markdown("---")
    
    student_incidents = [
        inc for inc in st.session_state.incidents
        if inc.get('student_id') == student_id
    ]
    
    if not student_incidents:
        st.info("No incident data available for this student yet.")
        st.markdown("### Actions")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to('direct_log_form', student_id=student_id)
        return
    
    st.markdown("### 📈 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Incidents", len(student_incidents))
    
    with col2:
        critical_count = len([inc for inc in student_incidents if inc.get('is_critical', False)])
        critical_rate = (critical_count / len(student_incidents) * 100) if student_incidents else 0
        st.metric("Critical Incidents", critical_count, delta=None if critical_count == 0 else f"{critical_rate:.0f}%")
    
    with col3:
        avg_severity = sum([inc.get('severity', 0) for inc in student_incidents]) / len(student_incidents)
        st.metric("Avg Severity", f"{avg_severity:.1f}")
    
    with col4:
        dates = [
            datetime.strptime(inc['date'], '%Y-%m-%d')
            for inc in student_incidents if inc.get('date')
        ]
        days_span = (max(dates) - min(dates)).days + 1 if len(dates) > 0 else 1
        st.metric("Days Tracked", days_span)
    
    with col5:
        incidents_per_week = (len(student_incidents) / days_span) * 7 if days_span > 0 else 0
        st.metric("Incidents/Week", f"{incidents_per_week:.1f}")
    
    st.markdown("---")
    
    df = pd.DataFrame(student_incidents)
    
    # Timeline
    if 'date' in df.columns:
        df['date_parsed'] = pd.to_datetime(df['date'])
        timeline = df.groupby('date_parsed').size().reset_index(name='Count')
        fig_timeline = px.line(
            timeline,
            x='date_parsed',
            y='Count',
            markers=True,
            title="Incidents Over Time"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        if 'behaviour_type' in df.columns:
            behaviour_counts = df['behaviour_type'].value_counts().reset_index()
            behaviour_counts.columns = ['Behaviour', 'Count']
            fig_beh = px.bar(
                behaviour_counts,
                x='Count',
                y='Behaviour',
                orientation='h',
                title="Behaviour Frequency"
            )
            st.plotly_chart(fig_beh, use_container_width=True)
    
    with col_right:
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Count']
            fig_loc = px.bar(
                location_counts,
                x='Count',
                y='Location',
                orientation='h',
                title="Incidents by Location"
            )
            st.plotly_chart(fig_loc, use_container_width=True)
    
    st.markdown("---")
    st.info("📊 Additional analytics (session windows, day of week, staff, etc.) can be added here as you extend the tool.")

# --- MAIN ---

def main():
    """Main application logic."""
    
    try:
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
