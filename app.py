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
    div[data-testid="stSelectbox"] > div > div > div > input,
    div[data-testid="stDateInput"] > div > input,
    div[data-testid="stTimeInput"] > div > input,
    .stTextArea textarea {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #4C1D95; /* Deep Purple */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #6D28D9;
    }
    .stButton > button:active {
        background-color: #5B21B6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    
    /* Metric/Info Boxes */
    .stMetric, .stAlert {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stAlert.info { background-color: #1E3A8A; border-left: 5px solid #3B82F6; }
    .stAlert.success { background-color: #065F46; border-left: 5px solid #10B981; }

    /* Multiselect checkboxes */
    div[data-baseweb="checkbox"] > label {
        color: #E2E8F0;
    }

    /* Severity Slider Style (to look like a gauge) */
    .stSlider > div[data-baseweb="slider"] {
        background-color: #334155;
        border-radius: 12px;
        padding: 10px;
    }
    .stSlider > div[data-baseweb="slider"] > div:nth-child(2) > div:nth-child(1) {
        background: linear-gradient(to right, #10B981 0%, #FCD34D 50%, #EF4444 100%);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- FBA and Data Constants ---

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)',
    'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)', 'Aggression (Staff)',
    'Non-compliance', 'Other'
]

# UPDATED: Student State/WOT terminology
STUDENT_STATES = ['Coping', 'Hyperarousal', 'Hypoarousal']

# NEW: Support Types
SUPPORT_TYPES = ['1:1', 'Independent', 'Small Group', 'Large Group']

# UPDATED: Antecedent list (for dropdown)
ANTECEDENTS = [
    'Demand/Request Made', 'Transition (Activity/Location)', 'Unstructured Time (e.g., recess)',
    'Denied Access (to item/activity)', 'Peer Conflict', 'Academic Difficulty',
    'Sensory Overload', 'Change in Routine', 'No Observable Antecedent', 'Other'
]

# NEW: Non-Critical Outcomes
OUTCOMES_NON_CRITICAL = [
    'Verbal Redirection', 'Reteach Expected Behaviour', 'Brief Time Out (In class)',
    'Planned Ignore/Extinction', 'Access to Preferred Activity (Post-compliance)', 
    'Student Self-Corrected', 'Other'
]

# Incident Locations
INCIDENT_LOCATIONS = [
    'jp program', 'py program', 'sy program',
    'jp spill out', 'py spill out', 'sy spill out',
    'gate', 'admin', 'playground', 'toilets',
    'student kitchen', 'excursion', 'library', 'swimming',
    'van/kia', 'other'
]

# Mock Staff Data
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# Mock Student Data
STUDENTS_DATA = {
    'stu-101': {'name': 'Alex Johnson', 'class': 'JP-B', 'year': 5, 'logs': []},
    'stu-102': {'name': 'Ben Carter', 'class': 'PY-A', 'year': 8, 'logs': [
        {'id': str(uuid.uuid4()), 'date': datetime(2025, 10, 20).date(), 'time': time(10, 30), 'behavior': 'Verbal Refusal', 'location': 'jp program', 'student_state': 'Hyperarousal', 'severity': 3, 'duration': 15, 'antecedent': 'Transition (Activity/Location)', 'responder': 'Emily Jones (JP)', 'consequence': 'Student sent to office.', 'outcome': 'Other', 'support_type': '1:1'},
        {'id': str(uuid.uuid4()), 'date': datetime(2025, 10, 25).date(), 'time': time(14, 0), 'behavior': 'Non-compliance', 'location': 'playground', 'student_state': 'Coping', 'severity': 1, 'duration': 5, 'antecedent': 'Unstructured Time (e.g., recess)', 'responder': 'Daniel Lee (PY)', 'consequence': 'Verbal redirection.', 'outcome': 'Verbal Redirection', 'support_type': 'Large Group'},
    ]},
    'stu-103': {'name': 'Chloe Davis', 'class': 'SY-C', 'year': 11, 'logs': []},
}

# --- Utility Functions ---

def get_staff_names(role=None):
    """Returns a list of staff names, optionally filtered by role."""
    if role:
        return [s['name'] for s in MOCK_STAFF if s['role'] == role or s['special']]
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_all_student_names():
    """Returns a dictionary of student IDs mapped to their full names."""
    return {uid: data['name'] for uid, data in STUDENTS_DATA.items()}

def generate_hypothesis(antecedent, behavior, state):
    """Generates a simplified FBA hypothesis based on core incident data."""
    # Simplified FBA Function determination
    escape_antecedents = [
        'Demand/Request Made', 'Transition (Activity/Location)', 
        'Academic Difficulty', 'Sensory Overload', 'Unstructured Time (e.g., recess)'
    ]
    
    if antecedent in escape_antecedents:
        function = "escape or avoid the demand/activity/situation"
    else:
        function = "gain access to attention or a tangible item/preferred activity"
        
    return (
        f"**Hypothesis (Auto-generated):** When **{antecedent}** occurred, the student "
        f"displayed **{behavior}** (State: {state}) in order to likely **{function}**."
    )

# --- State Management and Navigation ---

def initialize_state():
    """Initializes session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'log_data' not in st.session_state:
        st.session_state.log_data = STUDENTS_DATA
    if 'prelim_log_data' not in st.session_state:
        st.session_state.prelim_log_data = {}

def navigate_to(page, role=None, student_id=None):
    """Handles navigation and state updates."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student_id:
        st.session_state.student = student_id
    st.rerun() 

def get_logs_dataframe(student_id):
    """Returns the incident logs for a student as a DataFrame."""
    logs = st.session_state.log_data.get(student_id, {}).get('logs', [])
    if not logs:
        return pd.DataFrame()
    df = pd.DataFrame(logs)
    # Ensure date and time are combined correctly
    df['datetime'] = df.apply(lambda row: datetime.combine(row['date'], row['time']), axis=1)
    df = df.sort_values('datetime', ascending=False)
    return df

# --- Render Functions ---

def render_landing_page():
    """Renders the initial page for role selection."""
    st.title("Welcome to the Behaviour Support & Data Analysis Tool")
    st.markdown("Please select your role to proceed.")

    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("JP Staff", use_container_width=True):
        navigate_to('staff_area', role='JP')
    if col2.button("PY Staff", use_container_width=True):
        navigate_to('staff_area', role='PY')
    if col3.button("SY Staff", use_container_width=True):
        navigate_to('staff_area', role='SY')
    if col4.button("Admin", use_container_width=True):
        navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application features conditional logging: Severity 1-2 uses a Quick Log; Severity 3-5 redirects to a Critical Incident Form.")

def render_staff_area(role):
    """Renders the main staff dashboard."""
    role_map = {'JP': 'Junior Program', 'PY': 'Primary Program', 'SY': 'Senior Program', 'ADM': 'Administration'}
    st.title(f"{role_map.get(role, 'Staff')} Dashboard")
    
    if st.sidebar.button("⬅️ Logout"):
        navigate_to('landing', role=None)

    st.subheader("Select Student for Logging or Review")
    
    student_options = get_all_student_names()
    student_names = list(student_options.values())
    
    selected_name = st.selectbox(
        "Choose a Student:",
        options=["Select a student..."] + student_names,
        key="staff_select_student"
    )

    selected_id = None
    if selected_name != "Select a student...":
        selected_id = next((uid for uid, name in student_options.items() if name == selected_name), None)

    col_btn1, col_btn2 = st.columns(2)

    if selected_id:
        if col_btn1.button(f"📝 Start Quick Log for {selected_name}", use_container_width=True, type="primary"):
            navigate_to('quick_log', student_id=selected_id)
        
        if col_btn2.button(f"📊 View Analysis for {selected_name}", use_container_width=True):
            navigate_to('student_detail', student_id=selected_id)
    else:
        col_btn1.button("📝 Start Quick Log", disabled=True, use_container_width=True, type="primary")
        col_btn2.button("📊 View Analysis", disabled=True, use_container_width=True)

    st.markdown("---")
    
    st.subheader(f"{role_map.get(role, 'Program')} Overview (Live Incidents)")
    st.info("This area would show a live feed of active incidents or recent high-priority logs.")

def render_critical_incident_form(current_role, student_id):
    """
    NEW PAGE: Placeholder for the critical incident form (Severity 3-5).
    """
    student_name = STUDENTS_DATA.get(student_id, {}).get('name', 'Unknown Student')
    prelim_data = st.session_state.get('prelim_log_data', {})
    
    st.title(f"🚨 Critical Incident Report for {student_name}")
    st.caption(f"Logged by **{current_role}** Staff")
    
    st.warning(f"Severity was {prelim_data.get('severity', 'N/A')}. This page requires mandatory detailed reporting for compliance.")

    if st.sidebar.button("⬅️ Back to Dashboard"):
        # Clear preliminary data and return
        st.session_state.prelim_log_data = {}
        navigate_to('staff_area', role=current_role)

    st.markdown("---")
    st.subheader("Preliminary Data from Quick Log:")
    
    col_p1, col_p2 = st.columns(2)
    col_p1.markdown(f"**Date/Time:** {prelim_data.get('date')} at {prelim_data.get('time')}")
    col_p1.markdown(f"**Location:** {prelim_data.get('location')}")
    col_p1.markdown(f"**State:** {prelim_data.get('student_state')}")
    
    col_p2.markdown(f"**Behavior:** {prelim_data.get('behavior')}")
    col_p2.markdown(f"**Antecedent:** {prelim_data.get('antecedent')}")
    col_p2.markdown(f"**Support Type:** {prelim_data.get('support_type')}")
    
    st.markdown("---")
    
    with st.form("critical_incident_form"):
        st.subheader("Mandatory Critical Details")
        st.info("The next task will focus on building out these required compliance fields.")
        
        st.text_area("Detailed Narrative of Incident (Step-by-Step, including staff actions)", height=200, key="crit_narrative")
        st.multiselect("Injuries/Damage Sustained (Check all that apply)", options=['Staff Injury', 'Peer Injury', 'Student Injury', 'Major Property Damage'], key="crit_injuries")
        
        # Allow staff to cancel and return to quick log if they made an error
        if st.form_submit_button("Submit Full Critical Report (Placeholder)", type="primary"):
            # In a real app, this would save the full report to the database.
            st.success("Critical Report Submitted (Mock Save).")
            st.session_state.prelim_log_data = {}
            navigate_to('student_detail', student_id=student_id)
        
    if st.button("Cancel & Return to Quick Log (if severity chosen incorrectly)", type="secondary"):
        st.session_state.prelim_log_data = {}
        navigate_to('quick_log', student_id=student_id)


def render_quick_log(current_role, student_id):
    """Renders the Quick Incident Log form with conditional navigation."""
    student_name = STUDENTS_DATA.get(student_id, {}).get('name', 'Unknown Student')
    
    st.title(f"Quick Incident Log for {student_name}")
    st.caption(f"Logged by **{current_role}** Staff")

    if st.sidebar.button("⬅️ Back to Dashboard"):
        navigate_to('staff_area', role=current_role)

    # --- Incident Log Core Details (Collected immediately) ---
    st.subheader("1. Incident Core Details")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        log_date = st.date_input("Date of Incident *", datetime.now().date(), key="log_date")
        log_time = st.time_input("Start Time of Incident *", datetime.now().time().replace(second=0, microsecond=0), key="log_time")
        
    with col2:
        duration = st.number_input("Duration (minutes) *", min_value=1, max_value=180, value=5, key="log_duration")
        incident_location = st.selectbox("Incident Location *", options=INCIDENT_LOCATIONS, key="log_location")

    with col3:
        behavior = st.selectbox("Primary Behavior Displayed *", options=BEHAVIORS_FBA, key="log_behavior")
        responder_options = get_staff_names(current_role)
        default_responder = next((name for name in responder_options if f"({current_role})" in name), responder_options[0] if responder_options else "N/A")
        responder = st.selectbox("Primary Staff Responder *", options=responder_options, index=responder_options.index(default_responder) if default_responder in responder_options else 0, key="log_responder")
    
    st.markdown("---")

    st.subheader("2. Context, Support, and Severity")
    
    col4, col5 = st.columns(2)
    with col4:
        # ANTECEDENT/CONTEXT (Dropdown)
        antecedent = st.selectbox("Antecedent/Context *", options=ANTECEDENTS, key="log_antecedent_select")
        
        # STUDENT STATE (Coping/Hyperarousal/Hypoarousal)
        student_state = st.radio("Student State During Escalation *", options=STUDENT_STATES, key="log_student_state")
    
    with col5:
        # TYPE OF SUPPORT (Dropdown)
        support_type = st.selectbox("Type of Support *", options=SUPPORT_TYPES, key="log_support_type")
        
        # SEVERITY (Slider/Gauge)
        severity = st.slider("Severity (1=Low, 5=Critical) *", min_value=1, max_value=5, value=1, step=1, key="log_severity")
    
    st.markdown("---")

    # --- CRITICAL INCIDENT CHECK (Immediate Navigation) ---
    if severity >= 3:
        st.error(f"🚨 Severity is {severity}. This is considered a **Critical Incident** and requires a dedicated report.")
        
        # Save preliminary data to session state for the Critical Form to use
        st.session_state['prelim_log_data'] = {
            'date': log_date, 'time': log_time, 'duration': duration, 'location': incident_location,
            'behavior': behavior, 'responder': responder, 'antecedent': antecedent,
            'student_state': student_state, 'support_type': support_type, 'severity': severity,
            'student_id': student_id
        }
        
        if st.button(f"**Proceed to Critical Incident Form** (Severity {severity})", type="primary"):
             navigate_to('critical_incident_form', student_id=student_id)
        
        st.stop() # Stop rendering the rest of the Quick Log form
    
    # --- LOW/MODERATE INCIDENT CONCLUSION (Severity 1 or 2) ---
    st.subheader("3. Low/Moderate Incident Conclusion (Severity 1 or 2)")

    with st.form("low_moderate_log_form"):
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            # OUTCOME DROPDOWN
            outcome = st.selectbox(
                "Primary Outcome/Intervention *",
                options=OUTCOMES_NON_CRITICAL,
                key="log_outcome_select"
            )
        with col_c2:
            # CONSEQUECE TEXT AREA
            consequence_detail = st.text_area(
                "Consequence/Staff Action Description *",
                height=100,
                key="log_consequence_detail"
            )
            
        # PREPOPULATED HYPOTHESIS
        hypothesis = generate_hypothesis(antecedent, behavior, student_state)
        st.markdown(hypothesis)
        
        submit_button = st.form_submit_button("✅ Log Incident (Severity 1 or 2)", type="primary")
        
        if submit_button:
            # Simple mandatory field check (only for S1/S2 submission fields)
            if not all([outcome, consequence_detail]):
                st.error("Please fill in the Outcome and Consequence description fields.")
            else:
                # 1. Compile log entry
                new_log_entry = {
                    'id': str(uuid.uuid4()),
                    'date': log_date,
                    'time': log_time,
                    'behavior': behavior,
                    'location': incident_location,
                    'student_state': student_state,
                    'severity': severity,
                    'duration': duration,
                    'antecedent': antecedent,
                    'responder': responder,
                    'support_type': support_type,
                    'outcome': outcome,
                    'consequence': consequence_detail,
                    'hypothesis': hypothesis # Store for reference
                }

                # 2. Save log entry to student data (Mock save)
                if student_id in st.session_state.log_data:
                    st.session_state.log_data[student_id]['logs'].append(new_log_entry)
                    st.success(f"Low/Moderate Log for {student_name} saved successfully!")
                    
                    # 3. Navigate back to student detail page after saving
                    navigate_to('student_detail', student_id=student_id)
                else:
                    st.error("Error: Could not find student to save log against.")

def render_student_analysis(student_id, current_role):
    """Renders the analysis page for a specific student."""
    student_data = STUDENTS_DATA.get(student_id, {})
    student_name = student_data.get('name', 'N/A')
    
    st.title(f"Analysis for {student_name}")
    st.header(f"Class: {student_data.get('class', 'N/A')} | Year: {student_data.get('year', 'N/A')}")
    
    if st.sidebar.button("⬅️ Back to Dashboard"):
        navigate_to('staff_area', role=current_role)
    
    df_logs = get_logs_dataframe(student_id)

    if df_logs.empty:
        st.info("No incident logs available for this student yet. Start a Quick Log now!")
        if st.button("📝 Start Quick Log"):
            navigate_to('quick_log', student_id=student_id)
        return

    st.markdown("---")
    st.subheader(f"Total Incidents Logged: {len(df_logs)}")

    tab1, tab2 = st.tabs(["Data Visualizations", "Raw Log History"])

    with tab1:
        st.subheader("Key Incident Trends")
        
        col_viz1, col_viz2 = st.columns(2)

        # 1. Behavior Frequency
        behavior_counts = df_logs['behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig_behavior = px.bar(
            behavior_counts, 
            x='Count', 
            y='Behavior', 
            orientation='h',
            title='Top Behaviors Displayed',
            color='Count',
            color_continuous_scale=px.colors.sequential.Plotly3
        )
        fig_behavior.update_layout(template="plotly_dark")
        col_viz1.plotly_chart(fig_behavior, use_container_width=True)

        # 2. Antecedent Frequency
        antecedent_counts = df_logs['antecedent'].value_counts().reset_index()
        antecedent_counts.columns = ['Antecedent', 'Count']
        fig_antecedent = px.bar(
            antecedent_counts, 
            x='Count', 
            y='Antecedent', 
            orientation='h',
            title='Antecedent Triggers',
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_antecedent.update_layout(template="plotly_dark")
        col_viz2.plotly_chart(fig_antecedent, use_container_width=True)

        st.markdown("---")

        col_viz3, col_viz4 = st.columns(2)

        # 3. Student State Distribution
        state_counts = df_logs['student_state'].value_counts().reindex(STUDENT_STATES).fillna(0).reset_index()
        state_counts.columns = ['Student State', 'Count']
        fig_state = px.pie(
            state_counts, 
            names='Student State', 
            values='Count',
            title='Student State Distribution',
            color_discrete_map={
                "Coping": "#10B981", 
                "Hyperarousal": "#EF4444",    
                "Hypoarousal": "#3B82F6" 
            }
        )
        fig_state.update_layout(template="plotly_dark")
        col_viz3.plotly_chart(fig_state, use_container_width=True)

        # 4. Severity Distribution
        severity_counts = df_logs['severity'].value_counts().sort_index().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        fig_severity = px.bar(
            severity_counts, 
            x='Severity', 
            y='Count', 
            title='Incident Severity Breakdown',
            color='Severity',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_severity.update_layout(template="plotly_dark")
        col_viz4.plotly_chart(fig_severity, use_container_width=True)


    with tab2:
        st.subheader("Detailed Incident History")
        # Display the log data, selecting relevant columns for clarity
        display_df = df_logs[['date', 'time', 'location', 'behavior', 'antecedent', 'student_state', 'severity', 'duration', 'responder', 'outcome', 'consequence']].copy()
        display_df.columns = ['Date', 'Time', 'Location', 'Behavior', 'Antecedent', 'State', 'Severity', 'Duration (min)', 'Responder', 'Outcome', 'Consequence Detail']
        
        st.dataframe(display_df, use_container_width=True)


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

    elif st.session_state.page == 'critical_incident_form':
        if current_student and current_role:
            render_critical_incident_form(current_role, current_student)
        else:
            st.error("Missing context for Critical Incident. Returning to dashboard.")
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
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
