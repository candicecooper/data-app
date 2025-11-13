import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np

# --- Configuration and Aesthetics (High-Contrast Dark Look) ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a sleek, high-contrast, dark-mode inspired UI
st.markdown(
    """
    <style>
    /* High-Contrast Dark Theme for Accessibility and Modern Look */
    
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    h1, h2, h3, .stMarkdown, .st-emotion-cache-1jm69h1 { color: #F1F5F9 !important; }
    
    /* Widget Backgrounds */
    .stForm, .stContainer, .stAlert, .stSelectbox, .stTextInput, .stTextArea,
    .st-emotion-cache-6qob1p { background-color: #1E293B; border-radius: 12px; color: #F1F5F9; }
    
    /* Input Fields */
    div[data-testid="stTextInput"] > div > input,
    div[data-testid="stTextArea"] > div > textarea,
    div[data-testid="stSelectbox"] > div > div,
    .stDateInput, .stTimeInput {
        background-color: #0F172A !important;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9 !important;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #3B82F6; /* Blue 500 */
        color: white;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #2563EB; /* Blue 600 */
    }
    
    /* Sidebar styling for collapsed state */
    .st-emotion-cache-18j2hkn { /* Target sidebar background */
        background-color: #1E293B;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Ensure markdown links and info blocks stand out */
    .stAlert p {
        color: #F1F5F9 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- MOCK DATA ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# MOCK STUDENT DATA (In a real app, this would be fetched from a database)
STUDENT_DATA = [
    {'id': 'stu001', 'name': 'Liam Smith', 'grade': 5, 'fba_plan': True},
    {'id': 'stu002', 'name': 'Olivia Brown', 'grade': 4, 'fba_plan': False},
    {'id': 'stu003', 'name': 'Noah Williams', 'grade': 6, 'fba_plan': True},
    {'id': 'stu004', 'name': 'Emma Davis', 'grade': 5, 'fba_plan': False},
]

# --- Helper Functions ---

def initialize_state():
    """Initializes necessary session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing' # Default view
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'data_log' not in st.session_state:
        st.session_state.data_log = pd.DataFrame(columns=[
            'log_id', 'timestamp', 'student_id', 'student_name', 'staff_role', 'incident_type', 
            'antecedent', 'behavior', 'consequence', 'intensity', 'duration_min', 'context', 
            'is_abch_completed'
        ])

def get_active_staff(role=None):
    """Returns a list of active staff names, optionally filtered by role."""
    staff_list = [s for s in MOCK_STAFF if s['active'] and (role is None or s['role'] == role)]
    return [s['name'] for s in staff_list]

def get_all_students_data():
    """Returns the mock student data."""
    return STUDENT_DATA

# The corrected navigation function
def navigate_to(page, **kwargs):
    """
    Sets the page and any additional state variables, then forces a rerun.
    FIXED: st.experimental_rerun() changed to st.rerun() to prevent AttributeError.
    """
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun() # Replaced st.experimental_rerun()

# Placeholder rendering functions (must be defined for main() to run)

def render_quick_log(role, student):
    st.header(f"Quick Incident Log for {student['name']}")
    st.subheader(f"Logged in as {role} Staff")
    st.warning("Implement the full ABCH Quick Log form here.")
    if st.button("Back to Staff Area"):
        navigate_to('staff_area', student=None)

def render_student_analysis(student, role):
    st.header(f"Data Analysis for {student['name']}")
    st.subheader(f"Logged in as {role} Staff")
    st.info("Implement charts, summaries, and FBA details here.")
    if st.button("Back to Staff Area"):
        navigate_to('staff_area', student=None)

def render_staff_area(role):
    st.header(f"{role} Staff Dashboard")
    st.info("Implement student selection and overall data view here.")
    
    st.markdown("### Student List")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Select Student for Action")
        student_names = [s['name'] for s in STUDENT_DATA]
        selected_name = st.selectbox("Choose a student:", student_names, key="staff_student_select")
        
        if st.button(f"View Data for {selected_name}"):
            selected_student = next(s for s in STUDENT_DATA if s['name'] == selected_name)
            navigate_to('student_detail', student=selected_student)
            
    with col2:
        st.subheader("Quick Log a new incident")
        if st.button(f"Start Quick Log for {selected_name}", type="primary"):
            selected_student = next(s for s in STUDENT_DATA if s['name'] == selected_name)
            navigate_to('quick_log', student=selected_student)
    
    if st.button("Logout"):
        navigate_to('landing', role=None, student=None)
# --- Page Render Functions ---

def render_landing_page():
    """Renders the initial login/role selection page."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")
    st.subheader("Select Your Role to Continue")

    st.warning("This is a mock login to route you to the correct dashboard role.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Junior Primary (JP) Access", use_container_width=True):
            navigate_to('staff_area', role='JP') # Line 183 in original traceback
            
    with col2:
        if st.button("Primary (PY) Access", use_container_width=True):
            navigate_to('staff_area', role='PY')

    with col3:
        if st.button("Admin/Leadership (ADM) Access", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


# --- Main Application Loop ---

def main():
    """Controls the main application flow based on session state."""
    
    # 1. Initialize data and state
    initialize_state()

    current_role = st.session_state.get('role')
    current_student = st.session_state.get('student')

    # 2. Page Routing Logic
    if st.session_state.page == 'landing':
        render_landing_page() # Line 508

    elif st.session_state.page == 'quick_log':
        if current_student and current_role:
             render_quick_log(current_role, current_student) 
        else:
            st.error("Missing context. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)


    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)

    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role) # Line 528
        else:
            st.error("Role context missing. Please log in.")
            navigate_to('landing')

if __name__ == '__main__':
    main() # Line 533
