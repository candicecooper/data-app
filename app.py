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
            'grade': 'Y7', 'dob': '2011-04-17', 'edid': 'SY001', 'program': 'SY', 'profile_status': '_
