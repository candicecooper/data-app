import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS ---
MOCK_STUDENTS = [
    {'id': 'st1', 'name': 'Izack P.', 'year': 7, 'cohort': 'JP', 'plan': 'WOT', 'active': True},
    {'id': 'st2', 'name': 'Hannah B.', 'year': 5, 'cohort': 'PY', 'plan': 'ABC', 'active': True},
    {'id': 'st3', 'name': 'Javier M.', 'year': 9, 'cohort': 'SY', 'plan': 'WOT', 'active': False},
]

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- New Constants for Support & Setting ---
SUPPORT_TYPES = ['1:1', 'Independent', 'Small Group', 'Large Group', 'Other']
SETTINGS = [
    'Classroom (General)',
    'Specialist Program (e.g., JP)',
    'Spill Out/Withdrawal Area',
    'Playground/Yard',
    'Transition (e.g., from recess)',
    'Outside School Grounds',
    'Office/Admin Area'
]

# --- FBA and Data Constants (Expanded for context) ---
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out of Seat/Area', 'Vocal Disruption', 'Other']
ANTECEDENTS_FBA = ['Demand/Instruction Given', 'Transition Time', 'Peer Conflict', 'Attention Withdrawn', 'Unstructured Time', 'Sensory Overload', 'Task Too Difficult', 'Other']
CONSEQUENCES_FBA = ['Attention Given (Positive)', 'Attention Given (Negative)', 'Task Removed/Delayed', 'Access to Preferred Item/Activity', 'Escape from Demand', 'Sensory Input Provided', 'Other']

# --- Helper Functions ---

def get_active_students():
    return sorted([s['name'] for s in MOCK_STUDENTS if s['active']])

def get_active_staff(exclude_staff_name=None):
    """Returns a list of active staff names, optionally excluding the current log-in staff."""
    staff_names = [f"{s['name']} ({s['role']})" for s in MOCK_STAFF if s['active'] and s['name'] != exclude_staff_name]
    return sorted(staff_names)

def get_staff_roles():
    return sorted(list(set([s['role'] for s in MOCK_STAFF])))

def get_student_detail(student_name):
    return next((s for s in MOCK_STUDENTS if s['name'] == student_name), None)

def navigate_to(page, student=None, role=None):
    st.session_state.page = page
    if student: st.session_state.student = student
    if role: st.session_state.role = role
    st.rerun()

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
    div[data-testid="stSelectbox"] div[role="combobox"] {
        background-color: #2D3748 !important;
        border: 1px solid #4A5568;
        color: #F1F5F9 !important;
        border-radius: 8px;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #4C51BF; /* Indigo */
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s, transform 0.1s;
    }
    .stButton>button:hover {
        background-color: #6B46C1; /* Darker Indigo */
        transform: translateY(-1px);
    }

    /* Primary Button (Submit) */
    .stButton>button:nth-child(1) {
        background-color: #38A169; /* Green for primary action */
    }
    .stButton>button:nth-child(1):hover {
        background-color: #2F855A;
    }

    /* Streamlit Sidebar/Nav - Hidden for 'collapsed' */
    /* If we used a sidebar, we'd style it here */
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #2D3748;
        color: #F1F5F9;
        border-radius: 8px;
        border: 1px solid #4A5568;
    }
    </style>
    """
, unsafe_allow_html=True)


# --- Data Storage Initialization (Mock Database) ---
def initialize_state():
    if 'data_log' not in st.session_state:
        st.session_state.data_log = []
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None

# --- Quick Log Form Logic ---
def submit_quick_log(staff_name, staff_role, student_name):
    """Handles the form submission and saves the data to the log."""
    
    # Required fields check
    if not st.session_state.incident_date:
        st.error("Please select the incident date.")
        return
    if not st.session_state.incident_time: # New time field
        st.error("Please enter the incident time.")
        return
    if not st.session_state.behavior_observed:
        st.error("Please select at least one behaviour.")
        return
    
    # 1. Primary data structure for the incident
    log_entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'reporter_name': staff_name,
        'reporter_role': staff_role,
        'student_name': student_name,
        
        # New & Updated Fields
        'incident_date': st.session_state.incident_date.isoformat(),
        'incident_time': st.session_state.incident_time.isoformat(),
        'support_type': st.session_state.support_type, # New field
        'setting': st.session_state.setting, # New field
        'other_staff_involved': st.session_state.other_staff_involved, # New field
        
        # Core ABCH Fields
        'behavior_observed': st.session_state.behavior_observed,
        'antecedent': st.session_state.antecedent,
        'consequence': st.session_state.consequence,
        'intensity': st.session_state.intensity,
        'duration_minutes': st.session_state.duration_minutes,
        
        # Qualitative / Description
        'context_notes': st.session_state.context_notes,
        'response_notes': st.session_state.response_notes,
        
        # ABCH Status (for future refinement)
        'is_abch_completed': False, # Quick log starts as simple ABC, not full ABCH
        'window_of_tolerance': None,
        'how_to_respond': None,
        
        # Outcomes (Simplified)
        'outcome_reported': st.session_state.outcome_reported,
        'follow_up_required': st.session_state.follow_up_required
    }
    
    # 2. Append to log and provide feedback
    st.session_state.data_log.append(log_entry)
    st.success(f"Incident log for {student_name} submitted successfully! ({len(st.session_state.data_log)} total entries)")

    # 3. Clear the form elements (using keys)
    st.session_state.incident_date = datetime.now().date()
    st.session_state.incident_time = datetime.now().time()
    st.session_state.support_type = SUPPORT_TYPES[0]
    st.session_state.setting = SETTINGS[0]
    st.session_state.other_staff_involved = []
    st.session_state.behavior_observed = []
    st.session_state.antecedent = ANTECEDENTS_FBA[0]
    st.session_state.consequence = CONSEQUENCES_FBA[0]
    st.session_state.intensity = 1
    st.session_state.duration_minutes = 0
    st.session_state.context_notes = ""
    st.session_state.response_notes = ""
    st.session_state.outcome_reported = ""
    st.session_state.follow_up_required = False
    
    st.rerun() # Rerun to show success message and clear form


# --- Page Render Functions ---

def render_landing_page():
    st.title("Student Support System: Login")
    
    st.subheader("Select Your Role and Student Context")
    
    with st.form("login_form"):
        role_options = get_staff_roles()
        selected_role = st.selectbox("Your Staff Role:", role_options, index=role_options.index('ADM'))
        
        student_options = get_active_students()
        selected_student = st.selectbox("Student Context (Who is this log for?):", student_options, index=0)
        
        if st.form_submit_button("Start Quick Log"):
            navigate_to('quick_log', student=selected_student, role=selected_role)
            
    st.markdown("---")
    st.info("This application facilitates context-rich data collection for student behaviour analysis.")

def render_staff_area(staff_role):
    st.header(f"Staff Dashboard - Role: {staff_role}")
    
    st.subheader("Select Student for Analysis or Logging")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Log New Incident")
        student_options = get_active_students()
        selected_student = st.selectbox("Select Student to Log Incident:", student_options)
        if st.button(f"Go to Quick Log for {selected_student}"):
             navigate_to('quick_log', student=selected_student, role=staff_role)

    with col2:
        st.markdown("#### View Student Data")
        if st.session_state.data_log:
            logged_students = sorted(list(set([d['student_name'] for d in st.session_state.data_log])))
            if logged_students:
                analysis_student = st.selectbox("Select Student for Analysis:", logged_students)
                if st.button(f"View Data for {analysis_student}"):
                    navigate_to('student_detail', student=analysis_student, role=staff_role)
            else:
                st.info("No incident data logged yet.")
        else:
            st.info("No incident data logged yet.")
            
    st.markdown("---")

    # Display a summary of all logged data
    if st.session_state.data_log:
        st.subheader("Recent Incident History Summary")
        df = pd.DataFrame(st.session_state.data_log)
        
        # Simplify display columns
        display_df = df[['incident_date', 'incident_time', 'student_name', 'reporter_name', 'behavior_observed', 'intensity', 'setting']]
        # Convert list of behaviors to string for cleaner display
        display_df['behavior_observed'] = display_df['behavior_observed'].apply(lambda x: ', '.join(x))
        
        st.dataframe(display_df.tail(10), use_container_width=True, height=350)

def render_quick_log(staff_role, student_name):
    student_detail = get_student_detail(student_name)
    staff_name = next(s['name'] for s in MOCK_STAFF if s['role'] == staff_role)
    
    st.title(f"Quick Incident Log for {student_name}")
    st.subheader(f"Reported by: {staff_name} ({staff_role})")
    
    # Back button
    if st.button("⬅ Back to Dashboard"):
        navigate_to('staff_area', role=staff_role)

    st.markdown("---")

    # --- Incident Log Form ---
    with st.form("abch_quick_log"):
        
        st.markdown("### :calendar: Incident Context")
        
        # Get active staff names excluding the current reporter
        available_staff = get_active_staff(exclude_staff_name=staff_name)

        colA, colB, colC = st.columns(3)
        
        with colA:
            st.date_input("Date of Incident", value=datetime.now().date(), key='incident_date')
            
        with colB:
            # New Time Input (Start Time of Incident)
            st.time_input("Time of Incident (Start)", value=datetime.now().time(), key='incident_time')

        with colC:
            # New Support Type Dropdown
            st.selectbox(
                "Type of Support Provided", 
                SUPPORT_TYPES, 
                key='support_type', 
                index=SUPPORT_TYPES.index('1:1') if '1:1' in SUPPORT_TYPES else 0
            )

        # New Setting Dropdown
        st.selectbox(
            "Setting/Location", 
            SETTINGS, 
            key='setting', 
            index=SETTINGS.index('Classroom (General)') if 'Classroom (General)' in SETTINGS else 0,
            help="Where did the incident occur?"
        )

        # New Other Staff Involved Dropdown
        st.multiselect(
            "Other Staff Involved (Select all that apply)", 
            available_staff, 
            key='other_staff_involved',
            help="Select staff who were actively involved in managing the incident."
        )

        st.markdown("### :warning: The ABC Chain")

        # A: Antecedent
        st.selectbox("Antecedent (What happened immediately *before*?)", ANTECEDENTS_FBA, key='antecedent')
        
        # B: Behavior
        st.multiselect("Behaviour Observed (Select all that apply)", BEHAVIORS_FBA, key='behavior_observed')
        
        colD, colE = st.columns(2)
        with colD:
            st.slider("Intensity (1=Low, 5=Severe)", 1, 5, value=1, key='intensity', help="How disruptive/severe was the behaviour?")
        with colE:
            st.number_input("Duration (Minutes)", min_value=0, max_value=120, value=0, key='duration_minutes', help="Approximate length of the incident.")

        # C: Consequence
        st.selectbox("Consequence (What happened immediately *after*?)", CONSEQUENCES_FBA, key='consequence')
        
        st.markdown("---")

        st.markdown("### :page_with_curl: Notes & Outcomes")
        
        st.text_area("Contextual Notes / Description of Incident", key='context_notes', height=100, help="Provide a brief narrative of the full event.")
        
        st.text_area("Staff Response", key='response_notes', height=100, help="What intervention strategies were used?")
        
        st.text_area("Outcome Reported", key='outcome_reported', height=100, help="e.g., Student returned to task, Student removed to office, Sent home.")

        st.checkbox("Follow-up required (e.g., Parent contact, TAC Meeting, Plan Review)?", key='follow_up_required')
        
        st.markdown("---")
        
        # --- Submission ---
        st.form_submit_button(
            "Submit Incident Log", 
            on_click=submit_quick_log, 
            args=(staff_name, staff_role, student_name), 
            type="primary"
        )
        
def render_student_analysis(student_name, staff_role):
    st.title(f"Data Analysis for {student_name}")
    student_data = get_student_detail(student_name)
    
    # Filter logs for the selected student
    student_logs = [log for log in st.session_state.data_log if log['student_name'] == student_name]
    
    if st.button("⬅ Back to Dashboard"):
        navigate_to('staff_area', role=staff_role)
    
    st.markdown("---")

    if not student_logs:
        st.info(f"No incident logs available for {student_name} yet.")
        return

    df = pd.DataFrame(student_logs)
    df['incident_date'] = pd.to_datetime(df['incident_date'])
    df['week'] = df['incident_date'].dt.isocalendar().week.astype(str)
    
    st.subheader(f"Total Incidents Logged: {len(df)}")
    
    # 1. Intensity over Time (Line Chart)
    st.markdown("#### Incident Intensity Trend")
    # Using the row index as a proxy for 'time' for a simple trend
    df['event_index'] = range(1, len(df) + 1)
    fig_intensity = px.line(df, x='event_index', y='intensity', title='Intensity per Incident',
                            labels={'event_index': 'Incident Number', 'intensity': 'Intensity (1-5)'},
                            markers=True, template="plotly_dark")
    st.plotly_chart(fig_intensity, use_container_width=True)

    # 2. Behavior Frequency (Bar Chart)
    st.markdown("#### Behaviour Frequency")
    # Explode the list of behaviours into separate rows
    behavior_counts = df.explode('behavior_observed')['behavior_observed'].value_counts().reset_index()
    behavior_counts.columns = ['Behaviour', 'Count']
    fig_behavior = px.bar(behavior_counts, x='Behaviour', y='Count', title='Frequency of Observed Behaviours',
                          template="plotly_dark", color='Count')
    st.plotly_chart(fig_behavior, use_container_width=True)

    # 3. Antecedent Distribution (Pie Chart)
    st.markdown("#### Antecedent Distribution")
    antecedent_counts = df['antecedent'].value_counts().reset_index()
    antecedent_counts.columns = ['Antecedent', 'Count']
    fig_antecedent = px.pie(antecedent_counts, values='Count', names='Antecedent', title='Antecedent Breakdown',
                            template="plotly_dark")
    st.plotly_chart(fig_antecedent, use_container_width=True)
    
    # 4. New: Setting Distribution (Bar Chart)
    st.markdown("#### Incident Setting Distribution")
    setting_counts = df['setting'].value_counts().reset_index()
    setting_counts.columns = ['Setting', 'Count']
    fig_setting = px.bar(setting_counts, x='Setting', y='Count', title='Where Incidents Occur',
                          template="plotly_dark", color='Count')
    st.plotly_chart(fig_setting, use_container_width=True)

    # 5. Raw Data (Expander)
    with st.expander("View Raw Data Logs"):
        # Select key columns including the newly added ones
        cols_to_show = [
            'incident_date', 'incident_time', 'setting', 'support_type', 'other_staff_involved',
            'reporter_name', 'behavior_observed', 'antecedent', 'consequence', 'intensity', 
            'duration_minutes', 'context_notes', 'response_notes', 'outcome_reported'
        ]
        
        display_raw_df = df[cols_to_show].copy()
        display_raw_df['behavior_observed'] = display_raw_df['behavior_observed'].apply(lambda x: ', '.join(x))
        display_raw_df['other_staff_involved'] = display_raw_df['other_staff_involved'].apply(lambda x: ', '.join(x) if x else 'None')
        
        st.dataframe(display_raw_df, use_container_width=True)


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


    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)

    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role)
        else:
            st.error("Role context missing. Please log in.")
            navigate_to('landing')

# --- Start App ---
if __name__ == "__main__":
    main()
