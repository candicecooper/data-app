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
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    div[data-testid="stTextArea"] textarea {
        background-color: #0F172A; /* Darker background for input fields */
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Primary Button (Use a bright accent color) */
    .stButton>button[data-testid="baseButton-primary"] {
        background-color: #6366F1; /* Indigo */
        color: white;
    }
    .stButton>button[data-testid="baseButton-primary"]:hover {
        background-color: #4F46E5;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    }
    
    /* Secondary Button */
    .stButton>button[data-testid="baseButton-secondary"] {
        background-color: #334155; /* Slate */
        color: #F1F5F9;
    }
    .stButton>button[data-testid="baseButton-secondary"]:hover {
        background-color: #475569;
    }
    
    /* Expander/Sidebar styling */
    .stExpander, .stSidebar {
        border-radius: 12px;
        background-color: #1E293B;
    }
    
    /* Metric/Info Boxes */
    div[data-testid="stMetric"], .stAlert {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 1rem;
    }

    /* Streamlit's default header fix for better dark mode contrast */
    [data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.8); /* Semi-transparent dark blue */
    }
    
    /* Custom style for the critical alert */
    .stAlert.stWarning {
        background-color: #433800 !important; /* Darker yellow/brown background */
        color: #FACC15 !important; /* Bright yellow text */
        border-left: 5px solid #FACC15;
    }

    </style>
    """
, unsafe_allow_html=True)


# --- MOCK DATA FOR APPLICATION ---

MOCK_STUDENTS = [
    {'id': 's101', 'name': 'Alex Johnson', 'role': 'JP', 'focus': 'Communication'},
    {'id': 's102', 'name': 'Riley Smith', 'role': 'PY', 'focus': 'Self-Regulation'},
    {'id': 's103', 'name': 'Kai Li', 'role': 'SY', 'focus': 'Task Completion'},
]

MOCK_STAFF = [
    {'id': 'st1', 'name': 'Emily Jones (JP)', 'role': 'JP'},
    {'id': 'st2', 'name': 'Daniel Lee (PY)', 'role': 'PY'},
    {'id': 'st3', 'name': 'Sarah Chen (SY)', 'role': 'SY'},
    {'id': 'st4', 'name': 'Admin User (ADM)', 'role': 'ADM'},
]

# --- FBA and Data Constants (UPDATED) ---

# 1. WOT Options (Removed 'Calm')
WOT_OPTIONS = [
    'Settled/Focused', 
    'Stressed/Anxious', 
    'Aggitated/Disregulated', 
    'Escalated/Crisis'
]

# 2. Location Options (New List)
LOCATION_OPTIONS = [
    'JP room', 'JP spill out', 'PY room', 'PY spill out', 'SY room', 
    'SY spill out', 'Playground', 'Toilets', 'Student Kitchen', 'Yard', 
    'Admin', 'Gate', 'Van/Kia', 'Swimming', 'Excursion', 'Library'
]

# 3. Severity Options (For the Critical check)
SEVERITY_OPTIONS = [
    'Minor (Staff Managed)', 
    'Moderate (Leadership/Specialist Input)', 
    'Major (Parent Contact/Formal Action)', 
    'Critical (External Contact/Mandatory Reporting)'
]

# 5. Antecedent and Staff Response Options
ANTECEDENT_OPTIONS = [
    'Transition/Change in Routine', 
    'Demand/Task Presentation (Academic)', 
    'Demand/Task Presentation (Non-Academic)', 
    'Peer Interaction/Conflict', 
    'Staff Interaction/Instruction', 
    'Sensory Overload (Noise/Lights)', 
    'Lack of Attention/Boredom', 
    'Unsure/Unknown'
]

STAFF_RESPONSE_OPTIONS = [
    'Proximity/Non-verbal cue', 
    'Verbal Redirection/Reminder', 
    'Cool-down/Take a break (Voluntary)', 
    'Cool-down/Take a break (Mandated)', 
    'Removed from setting (Peer/Resource)', 
    'Ignored/Extinguished', 
    'Physical intervention (Safety)', 
    'De-escalation procedure applied'
]

# MOCK BEHAVIORS (Used in Quick Log)
BEHAVIOR_OPTIONS = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst']


# --- Helper Functions ---

def get_staff_name(role):
    """Retrieves the mock staff name based on role."""
    return next((s['name'] for s in MOCK_STAFF if s['role'] == role), f"Staff ({role})")

def get_student_by_id(student_id):
    """Finds a student by their ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_student_list_by_role(role):
    """Filters students by staff role (JP/PY/SY) or returns all for Admin."""
    if role == 'ADM':
        return MOCK_STUDENTS
    return [s for s in MOCK_STUDENTS if s['role'] == role]

def navigate_to(page, role=None, student_id=None):
    """Manages application navigation state."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student_id:
        st.session_state.student = get_student_by_id(student_id)
    else:
        st.session_state.student = None
    
    # Reset critical state when navigating away from log pages
    if page != 'quick_log':
        st.session_state.critical_alert = False


def initialize_state():
    """Initializes session state variables if they do not exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'incident_logs' not in st.session_state:
        st.session_state.incident_logs = pd.DataFrame(columns=['id', 'student_id', 'datetime', 'staff_role', 'severity', 'behavior', 'location', 'antecedent', 'staff_response', 'context'])
    # New state variables for Critical Incident Logic
    if 'log_submit_mode' not in st.session_state:
        st.session_state.log_submit_mode = 'quick'
    if 'critical_alert' not in st.session_state:
        st.session_state.critical_alert = False


# --- Callbacks ---

def handle_severity_change():
    """Checks severity selection and flags for critical incident, updating alert state."""
    # Check if the current severity selection is 'Critical'
    if st.session_state.quick_log_severity == 'Critical (External Contact/Mandatory Reporting)':
        # 3. Alert user of Critical Incident screen
        st.session_state.critical_alert = True
    else:
        st.session_state.critical_alert = False
    
    # Also reset the submission mode when severity changes
    st.session_state.log_submit_mode = 'quick'


# --- View Functions ---

def staff_header(title, role=None, student=None):
    """Reusable header component for staff areas."""
    st.header(title)
    if role and student:
        st.caption(f"Logged in as: **{get_staff_name(role)}** | Logging for: **{student['name']}** ({student['role']})")
    elif role:
        st.caption(f"Logged in as: **{get_staff_name(role)}**")
    st.markdown("---")


def render_critical_log_form(role, student):
    """
    Renders the mandatory critical incident log screen. 
    This is triggered if 'Critical' severity is selected on the quick log form.
    """
    staff_header("🚨 Mandatory Critical Incident Log", role, student)
    
    st.info("Since a **Critical** severity was selected, this detailed mandatory reporting screen must be completed before saving.")
    
    # Pre-populate key data from the quick log session state
    severity = st.session_state.get('quick_log_severity', 'Critical (External Contact/Mandatory Reporting)')
    location = st.session_state.get('quick_log_location', 'Yard')
    
    st.markdown(f"**Quick Log Data Captured:**")
    st.markdown(f"- **Severity:** `{severity}` | **Location:** `{location}`")
    st.markdown("---")
    
    with st.form("critical_incident_log_form"):
        st.subheader("Detailed Reporting Requirements")
        
        st.text_area("Detailed Account of Events", height=200, help="Provide a step-by-step account of the entire incident, including all staff and student actions.")
        st.text_area("External Contacts Made (e.g., SAPOL, Ambulance, Senior Leadership, Parents)", help="Document who was contacted, when, and the outcome of the contact.")
        
        # Simple placeholder submission
        if st.form_submit_button("Finalise Critical Incident Report", type="primary", use_container_width=True):
            # In a real app, this would save the critical log data (which is separate from the quick log)
            st.toast("✅ Critical Incident Report Finalised and Submitted!")
            # Navigate back to the staff area dashboard
            navigate_to('staff_area', role=role)
            st.experimental_rerun()
            

def render_quick_log(role, student):
    """Renders the ABCH-based Quick Log Form."""
    staff_header("Quick Incident Log (ABCH)", role, student)

    # Initialize log submission mode (in case user switches severity)
    if 'log_submit_mode' not in st.session_state:
        st.session_state.log_submit_mode = 'quick'

    with st.form("quick_incident_log_form", clear_on_submit=False):
        
        col_date, col_time = st.columns(2)
        with col_date:
            date = st.date_input("Date of Incident", value=datetime.now().date(), key="quick_log_date")
        with col_time:
            time_of_incident = st.time_input("Time of Incident", value=datetime.now().time(), key="quick_log_time")

        # Row 2: Behavior Type
        behavior = st.multiselect(
            "Target Behavior(s) Displayed",
            options=BEHAVIOR_OPTIONS,
            key="quick_log_behavior",
            help="Select all relevant behaviors. If 'Other', include details in the context."
        )

        # Row 3: Severity and Location
        col_sev, col_loc = st.columns(2)
        with col_sev:
            # 3. Severity with handler for Critical Incident alert and routing
            severity = st.selectbox(
                "Severity/Impact Level",
                options=SEVERITY_OPTIONS,
                key="quick_log_severity",
                index=SEVERITY_OPTIONS.index('Minor (Staff Managed)') if 'Minor (Staff Managed)' in SEVERITY_OPTIONS else 0,
                on_change=handle_severity_change, # Trigger callback on change
                help="Select the level of impact/severity of the incident."
            )

        with col_loc:
            # 2. Location (Updated options)
            location = st.selectbox(
                "Location of Incident",
                options=LOCATION_OPTIONS, # Updated list
                key="quick_log_location",
                help="Where did the incident occur?"
            )
        
        # 3. Alert Display for Critical Incident
        if st.session_state.get('critical_alert'):
            st.warning("⚠️ **CRITICAL INCIDENT FLAGGED** ⚠️\n\nSubmitting this log will take you *directly* to the **Critical Incident Reporting** screen, bypassing the quick log save.")
            # Ensure the submission mode is set to critical
            st.session_state.log_submit_mode = 'critical'
        else:
            st.session_state.log_submit_mode = 'quick'
            
        # Row 4: Antecedent and WOT
        col_ant, col_wot = st.columns(2)
        with col_ant:
            # 5. Antecedent choices
            antecedent = st.selectbox(
                "Antecedent (What happened immediately BEFORE?)",
                options=ANTECEDENT_OPTIONS,
                key="quick_log_antecedent",
                help="Select the trigger event that occurred right before the behavior."
            )
        with col_wot:
            # 1. WOT (Window of Tolerance) - Calm removed
            wot = st.selectbox(
                "Student's Window of Tolerance (WOT) at Time of Incident",
                options=WOT_OPTIONS, # Updated list
                key="quick_log_wot",
                help="Estimate the student's emotional state when the incident began."
            )
            
        # Row 5: Staff Response
        # 5. Staff Response choices
        staff_response = st.selectbox(
            "Staff Response/Intervention Used",
            options=STAFF_RESPONSE_OPTIONS,
            key="quick_log_staff_response",
            help="What was the primary staff action taken?"
        )

        # Row 6: Description
        # 4. Remove Blurb from Description (set value to empty string)
        context = st.text_area(
            f"Context/Description of Incident (Must be objective and factual: Who, What, Where, When, What was done)",
            value="", # Blurb removed
            height=150,
            key="quick_log_context",
            help="Describe the incident objectively. Start the log where the antecedent occurred."
        )

        # Submission Button
        submitted = st.form_submit_button(
            "Submit Incident Log", 
            type="primary", 
            use_container_width=True
        )

        if submitted:
            # 4. Critical Incident Routing Logic
            if st.session_state.log_submit_mode == 'critical':
                # Route directly to the critical log screen
                st.toast("⚠️ Routing to Critical Incident Log...")
                navigate_to('critical_log', role=role, student_id=student['id'])
                st.experimental_rerun()
            else:
                # Original Quick Log Save Logic
                try:
                    new_log = {
                        'id': str(uuid.uuid4()),
                        'student_id': student['id'],
                        'datetime': datetime.combine(date, time_of_incident),
                        'staff_role': role,
                        'severity': severity,
                        'behavior': ", ".join(behavior),
                        'location': location,
                        'antecedent': antecedent,
                        'staff_response': staff_response,
                        'wot': wot,
                        'context': context,
                    }
                    
                    # Append new log to DataFrame
                    new_df = pd.DataFrame([new_log])
                    st.session_state.incident_logs = pd.concat([st.session_state.incident_logs, new_df], ignore_index=True)

                    st.toast("✅ Quick Incident Log Submitted!")
                    navigate_to('staff_area', role=role)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error submitting log: {e}")
                    
def render_student_analysis(student, role):
    """Renders the analysis dashboard for a selected student."""
    staff_header("Student Data Analysis", role, student)
    
    st.subheader(f"Data for: {student['name']} ({student['role']})")
    
    # Filter incidents for the selected student
    student_incidents = st.session_state.incident_logs[
        st.session_state.incident_logs['student_id'] == student['id']
    ]

    if student_incidents.empty:
        st.info(f"No incident data logged yet for {student['name']}.")
        return

    # --- Metrics ---
    total_logs = len(student_incidents)
    critical_logs = len(student_incidents[student_incidents['severity'].str.contains('Critical')])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents Logged", total_logs)
    col2.metric("Critical Incidents", critical_logs)
    col3.metric("Primary Concern", student['focus'])


    # --- Visualizations ---
    st.subheader("Data Visualizations")
    
    # Plot 1: Severity Distribution
    severity_counts = student_incidents['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    fig_sev = px.bar(severity_counts, x='Severity', y='Count', 
                     title='Incident Count by Severity',
                     color='Severity',
                     color_discrete_map={
                         'Minor (Staff Managed)': '#3B82F6', 
                         'Moderate (Leadership/Specialist Input)': '#F59E0B', 
                         'Major (Parent Contact/Formal Action)': '#EF4444',
                         'Critical (External Contact/Mandatory Reporting)': '#DC2626'
                     })
    fig_sev.update_layout(template='plotly_dark')
    st.plotly_chart(fig_sev, use_container_width=True)

    # Plot 2: Antecedent/WOT Relationship
    pivot = student_incidents.groupby(['antecedent', 'wot']).size().reset_index(name='Count')
    fig_pivot = px.sunburst(pivot, path=['antecedent', 'wot'], values='Count', 
                            title='Antecedent to WOT Breakdown',
                            color_continuous_scale=px.colors.sequential.Sunset)
    fig_pivot.update_layout(template='plotly_dark')
    st.plotly_chart(fig_pivot, use_container_width=True)

    # Raw Data View
    st.subheader("Raw Incident Log Data")
    # Display the logs, sorting by date/time
    st.dataframe(
        student_incidents.sort_values(by='datetime', ascending=False).drop(columns=['id', 'student_id']),
        use_container_width=True
    )


def render_staff_area(role):
    """Renders the dashboard for staff to select students and actions."""
    staff_header(f"{role} Staff Dashboard", role)
    
    students_in_area = get_student_list_by_role(role)
    
    # Student Selection
    st.subheader(f"Students Assigned to {role}")
    
    student_options = {s['name']: s['id'] for s in students_in_area}
    
    # If no students, provide feedback
    if not student_options:
        st.info("No students are currently assigned to this area in the mock data.")
        return

    selected_name = st.selectbox(
        "Select Student for Logging or Analysis",
        options=list(student_options.keys()),
        index=0,
        key="selected_student_for_action"
    )
    
    selected_id = student_options[selected_name]
    selected_student = get_student_by_id(selected_id)
    
    st.markdown("---")
    
    # Action Buttons
    col_log, col_analyze = st.columns(2)
    
    with col_log:
        if st.button(f"➕ Log Incident for {selected_student['name']}", key="action_log", type="primary", use_container_width=True):
            # Navigate to quick log, passing student context
            navigate_to('quick_log', role=role, student_id=selected_id)
            st.experimental_rerun()
            
    with col_analyze:
        if st.button(f"📈 Analyze Data for {selected_student['name']}", key="action_analyze", use_container_width=True):
            # Navigate to student detail/analysis view
            navigate_to('student_detail', role=role, student_id=selected_id)
            st.experimental_rerun()


def render_landing_page():
    """Renders the initial role selection screen."""
    st.title("📚 Behaviour Support & Data Analysis Tool")
    st.subheader("Select your area to begin.")
    
    col_jp, col_py, col_sy, col_adm = st.columns(4)
    
    with col_jp:
        if st.button("Junior Primary (JP)", key="role_jp", type="primary", use_container_width=True):
            navigate_to('staff_area', role='JP')
            st.experimental_rerun()
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
            st.experimental_rerun()
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
            st.experimental_rerun()
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            st.experimental_rerun()
            
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
        render_landing_page()

    elif st.session_state.page == 'quick_log':
        if current_student and current_role:
             render_quick_log(current_role, current_student) 
        else:
            st.error("Missing context. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)
            st.experimental_rerun()
            
    # NEW: Critical Log Routing
    elif st.session_state.page == 'critical_log':
        if current_student and current_role:
            render_critical_log_form(current_role, current_student)
        else:
            st.error("Missing context for Critical Log. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)
            st.experimental_rerun()

    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
            if st.button("⬅ Back to Staff Dashboard", key="back_from_analysis", type="secondary"):
                 navigate_to('staff_area', role=current_role)
                 st.experimental_rerun()
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)
            st.experimental_rerun()


    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role)
        else:
            st.error("Role not set.")
            navigate_to('landing')
            st.experimental_rerun()

    
# Run the main function
if __name__ == "__main__":
    main()
