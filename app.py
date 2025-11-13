import streamlit as st
import pandas as pd
from datetime import datetime, time
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
    
    /* Custom style for the critical alert */
    .stAlert.stWarning {
        background-color: #433800 !important; /* Darker yellow/brown background */
        color: #FACC15 !important; /* Bright yellow text */
        border-left: 5px solid #FACC15;
    }

    /* Radio button label color fix */
    div[data-testid="stRadio"] label p {
        color: #F1F5F9 !important;
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
    {'id': 'st5', 'name': 'Specialist SSO', 'role': 'SSO'},
    {'id': 'st6', 'name': 'Relief Teacher (TRT)', 'role': 'TRT'},
]

# --- FBA and Data Constants ---

WOT_OPTIONS = [
    'Settled/Focused (Coping)', 
    'Stressed/Anxious (Pre-Escalation)', 
    'Aggitated/Disregulated (Escalation)', 
    'Escalated/Crisis (High Arousal)'
]

LOCATION_OPTIONS = [
    'JP room', 'JP spill out', 'PY room', 'PY spill out', 'SY room', 
    'SY spill out', 'Playground', 'Toilets', 'Student Kitchen', 'Yard', 
    'Admin', 'Gate', 'Van/Kia', 'Swimming', 'Excursion', 'Library'
]

SEVERITY_OPTIONS = [
    'Minor (Staff Managed)', 
    'Moderate (Leadership/Specialist Input)', 
    'Major (Parent Contact/Formal Action)', 
    'Critical (External Contact/Mandatory Reporting)'
]

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

SUPPORT_TYPES = ['Independent', '1:1', 'Small Group', 'Large Group']

BEHAVIOR_OPTIONS = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst']

# List of all staff names for the new multiselect
ALL_STAFF_NAMES = [s['name'] for s in MOCK_STAFF]


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
    
    # Reset critical state when navigating away from log pages
    if page not in ['quick_log', 'critical_log']:
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
        # Added 'involved_staff' column
        st.session_state.incident_logs = pd.DataFrame(columns=['id', 'student_id', 'datetime', 'staff_role', 'involved_staff', 'severity', 'behavior', 'location', 'antecedent', 'staff_response', 'wot', 'support_type', 'context'])
    if 'critical_alert' not in st.session_state:
        st.session_state.critical_alert = False


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
    """
    staff_header("🚨 Mandatory Critical Incident Log", role, student)
    
    st.info("Since a **Critical** severity was selected, this detailed mandatory reporting screen must be completed before saving.")
    
    # Use key data from the quick log session state as context
    severity = st.session_state.get('quick_log_severity_local_check', 'Critical (Not logged)')
    location = st.session_state.get('quick_log_location_local_check', 'Unknown Location')
    
    st.markdown(f"**Initial Context Captured:**")
    st.markdown(f"- **Severity:** `{severity}` | **Location:** `{location}`")
    st.markdown("---")
    
    with st.form("critical_incident_log_form"):
        st.subheader("Detailed Reporting Requirements")
        
        st.text_area("Detailed Account of Events", height=200, help="Provide a step-by-step account of the entire incident, including all staff and student actions.")
        st.text_area("External Contacts Made (e.g., SAPOL, Ambulance, Senior Leadership, Parents)", help="Document who was contacted, when, and the outcome of the contact.")
        
        # Simple placeholder submission
        if st.form_submit_button("Finalise Critical Incident Report", type="primary", use_container_width=True):
            # In a real app, this is where the detailed critical log would be saved
            st.toast("✅ Critical Incident Report Finalised and Submitted!")
            # Navigate back to the staff area dashboard, resetting the critical flag
            navigate_to('staff_area', role=role)
            st.rerun()
            

def render_quick_log(role, student):
    """Renders the ABCH-based Quick Log Form (Prior Version)."""
    staff_header("Quick Incident Log (ABCH)", role, student)

    staff_name = get_staff_name(role)
    
    # Ensure current logger's name is not in the list of "other" staff
    staff_options_for_multiselect = [name for name in ALL_STAFF_NAMES if name != staff_name]


    # Use a persistent key for the form
    with st.form("quick_incident_log_form"):
        
        # Row 1: Date, Time, Staff Logging, and Other Staff Involved (NEW COLUMN ADDED)
        col_date, col_time, col_staff_log, col_staff_involved = st.columns([1.5, 1.5, 2, 3])
        
        with col_date:
            # Widget values stored in local variables
            date = st.date_input("Date of Incident", value=datetime.now().date())
        with col_time:
            # Widget values stored in local variables
            time_of_incident = st.time_input("Time of Incident", value=datetime.now().time())
        with col_staff_log:
            st.markdown("Staff Logging Incident")
            st.caption(f"**{staff_name}** (Automatically assigned)")
        
        with col_staff_involved:
            # NEW FIELD FOR OTHER STAFF
            involved_staff = st.multiselect(
                "Other Staff Involved/Witnessed",
                options=staff_options_for_multiselect,
                default=[],
                help="Select any other staff members who were involved or witnessed the incident."
            )

        st.markdown("---")
        
        # Row 2: Severity, Location, and Type of Support
        col_sev, col_loc, col_support = st.columns(3)

        with col_sev:
            # Severity requires a key so the warning below can check its current value immediately
            severity = st.selectbox(
                "Severity/Impact Level",
                options=SEVERITY_OPTIONS,
                key="quick_log_severity_local_check", 
                index=SEVERITY_OPTIONS.index('Minor (Staff Managed)'),
                help="Select the level of impact/severity of the incident."
            )
            
        with col_loc:
            # Widget values stored in local variables
            location = st.selectbox(
                "Location of Incident",
                options=LOCATION_OPTIONS, 
                index=None,
                help="Where did the incident occur?"
            )
            # Store location in state for critical log context
            st.session_state['quick_log_location_local_check'] = location

        with col_support:
            # Widget values stored in local variables
            support_type = st.radio(
                "**Type of Support/Group**",
                SUPPORT_TYPES,
                index=None,
                horizontal=True,
                help="Select the context in which the incident occurred."
            )

        # Alert Display
        current_severity_selection = st.session_state.get('quick_log_severity_local_check')
        if current_severity_selection == 'Critical (External Contact/Mandatory Reporting)':
            st.warning("⚠️ **CRITICAL INCIDENT FLAGGED** ⚠️\n\nSubmitting this log will immediately route you to the **Critical Incident Reporting** screen.")
            
        st.markdown("---")

        # Row 3: Behavior and WOT
        col_behaviors, col_wot = st.columns(2)
        with col_behaviors:
            # Widget values stored in local variables
            behavior = st.multiselect(
                "Target Behavior(s) Displayed (B)",
                options=BEHAVIOR_OPTIONS,
                help="Select all relevant behaviors."
            )
        with col_wot:
            # Widget values stored in local variables
            wot = st.selectbox(
                "Student's Regulatory State (WOT)",
                options=WOT_OPTIONS, 
                index=None,
                help="Estimate the student's emotional state when the incident began."
            )

        st.markdown("---")

        # Row 4: Antecedent and Staff Response (C)
        col_ant, col_response = st.columns(2)
        with col_ant:
            # Widget values stored in local variables
            antecedent = st.selectbox(
                "Antecedent (What happened immediately BEFORE?) (A)",
                options=ANTECEDENT_OPTIONS,
                index=None,
                help="Select the trigger event."
            )
        with col_response:
            # Widget values stored in local variables
            staff_response = st.selectbox(
                "Staff Response/Intervention Used (C)",
                options=STAFF_RESPONSE_OPTIONS,
                index=None,
                help="What was the primary staff action taken?"
            )

        st.markdown("---")

        # Row 5: Optional Context/Description (at the bottom)
        st.markdown(
            """
            <div style='background-color: #2F3E50; padding: 10px; border-radius: 8px; margin-bottom: 5px;'>
                <p style='color: #94A3B8; font-weight: bold; font-size: 1.1em;'>
                    Optional: Description / Context of Incident
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Widget values stored in local variables
        context = st.text_area(
            "Detailed Observation:",
            value="",
            placeholder="Type optional description here...",
            height=100,
            label_visibility="collapsed"
        )


        # Submission Button and Logic (Inline - NOT using callback)
        col_submit, col_back_spacer = st.columns([1, 4])
        with col_submit:
            # Submission logic is contained entirely inside the if block
            if st.form_submit_button("Submit Incident Log", type="primary", use_container_width=True):
                
                current_role = st.session_state.get('role')
                current_student = st.session_state.get('student')
                
                # 1. Validation Check using local variables
                required_fields = [date, time_of_incident, severity, location, support_type, wot, antecedent, staff_response]
                if not all(required_fields) or not behavior:
                    st.error("Please ensure all required fields are completed before submission.")
                    # Use st.stop() or return to prevent proceeding to save/navigate
                    st.stop()
                
                # 2. Critical Incident Routing Logic
                is_critical = severity == 'Critical (External Contact/Mandatory Reporting)'
                
                if is_critical:
                    # This navigation is the part that typically causes the StreamlitInvalidFormCallbackError
                    st.session_state.critical_alert = True
                    st.toast("⚠️ Routing to Critical Incident Log...")
                    navigate_to('critical_log', role=current_role, student_id=current_student['id'])
                    st.rerun()
                else:
                    # 3. Standard Quick Log Save Logic
                    try:
                        # Combine date and time objects into a single datetime object
                        incident_datetime = datetime.combine(date, time_of_incident)

                        new_log = {
                            'id': str(uuid.uuid4()),
                            'student_id': current_student['id'],
                            'datetime': incident_datetime,
                            'staff_role': current_role,
                            'involved_staff': ", ".join(involved_staff), # NEW FIELD SAVED HERE
                            'severity': severity,
                            'behavior': ", ".join(behavior),
                            'location': location,
                            'antecedent': antecedent,
                            'staff_response': staff_response,
                            'wot': wot,
                            'support_type': support_type,
                            'context': context,
                        }
                        
                        # Append new log to DataFrame
                        new_df = pd.DataFrame([new_log])
                        st.session_state.incident_logs = pd.concat([st.session_state.incident_logs, new_df], ignore_index=True)

                        st.toast("✅ Quick Incident Log Submitted!")
                        # Navigate back to the staff area dashboard
                        navigate_to('staff_area', role=current_role)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error submitting log: {e}")
            
    # Button outside the form to navigate back (so it doesn't try to submit the form)
    if st.button("⬅ Back to Staff Dashboard", key="back_from_quick_log"):
        navigate_to('staff_area', role=role)
        st.rerun()
            
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
        if st.button("Log Incident Now", key="log_now_from_analysis"):
             navigate_to('quick_log', role=role, student_id=student['id'])
             st.rerun()
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
    # Exclude the new column 'involved_staff' from the drop list, as we want to see it
    columns_to_drop = ['id', 'student_id', 'datetime']
    
    st.dataframe(
        # Convert datetime column to date-only string for cleaner display in the dataframe
        student_incidents.assign(Date=lambda x: x['datetime'].dt.strftime('%Y-%m-%d'))
                         .sort_values(by='datetime', ascending=False)
                         .drop(columns=columns_to_drop),
        use_container_width=True
    )
    
    if st.button("⬅ Back to Staff Dashboard", key="back_from_analysis", type="secondary"):
         navigate_to('staff_area', role=role)
         st.rerun()


def render_staff_area(role):
    """Renders the dashboard for staff to select students and actions."""
    staff_header(f"{role} Staff Dashboard", role)
    
    students_in_area = get_student_list_by_role(role)
    
    # Map student names to IDs for the selectbox
    student_options = {s['name']: s['id'] for s in students_in_area}
    student_names = list(student_options.keys())
    
    if not student_options:
        st.info("No students are currently assigned to this area in the mock data.")
        st.session_state.student = None # Clear student state if no students
        return

    # 1. Determine the index: Try to maintain the currently selected student in state, otherwise default to 0.
    default_index = 0
    if st.session_state.student and st.session_state.student['name'] in student_names:
        default_index = student_names.index(st.session_state.student['name'])
    
    # 2. Render the selectbox with the dynamic key
    selected_name = st.selectbox(
        "Select Student for Logging or Analysis",
        options=student_names,
        index=default_index,
        key=f"selected_student_for_action_{role}" # DYNAMIC KEY to prevent stale state on role switch
    )
    
    # 3. Update the student state based on the selection
    selected_id = student_options[selected_name]
    selected_student = get_student_by_id(selected_id)
    
    # Ensure the session state student object is always up-to-date with the current selection
    st.session_state.student = selected_student 
    
    st.markdown("---")
    
    # Action Buttons
    col_log, col_analyze = st.columns(2)
    
    with col_log:
        if st.button(f"➕ Log Incident for {selected_student['name']}", key="action_log", type="primary", use_container_width=True):
            # Navigate to quick log, passing student context
            navigate_to('quick_log', role=role, student_id=selected_id)
            st.rerun()
            
    with col_analyze:
        if st.button(f"📈 Analyze Data for {selected_student['name']}", key="action_analyze", use_container_width=True):
            # Navigate to student detail/analysis view
            navigate_to('student_detail', role=role, student_id=selected_id)
            st.rerun()


def render_landing_page():
    """Renders the initial role selection screen."""
    st.title("📚 Behaviour Support & Data Analysis Tool")
    st.subheader("Select your area to begin.")
    
    col_jp, col_py, col_sy, col_adm = st.columns(4)
    
    with col_jp:
        if st.button("Junior Primary (JP)", key="role_jp", type="primary", use_container_width=True):
            navigate_to('staff_area', role='JP')
            st.rerun()
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
            st.rerun()
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
            st.rerun()
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            st.rerun()
            
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
            st.rerun()
            
    # Critical Log Routing
    elif st.session_state.page == 'critical_log':
        if current_student and current_role:
            render_critical_log_form(current_role, current_student)
        else:
            st.error("Missing context for Critical Log. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)
            st.rerun()

    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)
            st.rerun()


    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role)
        else:
            st.error("Role not set.")
            navigate_to('landing')
            st.rerun()

    
# Run the main function
if __name__ == "__main__":
    main()
