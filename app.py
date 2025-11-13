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
    div[data-testid="stTextArea"] > textarea,
    div[data-testid="stSelectbox"] > div[role="button"],
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input,
    div[data-testid="stRadio"] label {
        background-color: #334155;
        color: #F1F5F9;
        border: 1px solid #475569;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #16A34A; /* Emerald Green */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #15803D; /* Darker Green */
    }

    /* Radio/Checkbox Labels */
    .stRadio label, .stCheckbox label {
        color: #E2E8F0;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #3B82F6; /* Blue indicator */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS ---
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out of Seat', 'Non-Compliance', 'Swearing/Verbal Abuse', 'Defiance', 'Inappropriate Language']
ANTECEDENTS_FBA = ['Transition (Activity/Area)', 'Demand/Instruction Given', 'Peer Conflict', 'Staff Attention (Positive/Negative)', 'Non-Preferred Activity', 'Waiting', 'Sensory Overload', 'Unstructured Time']
CONSEQUENCES_FBA = ['Time Out/Removal (Area)', 'Staff Redirection/Verbal Prompt', 'Ignored/Withdrawn Attention', 'Access to Preferred Item/Activity', 'Restorative Chat', 'Sent to Leadership']
WOT_CATEGORIES = ['Highly Regulated (Calm/Focused)', 'Slightly Dysregulated (Fidgeting/Frustrated)', 'Moderately Dysregulated (Elevated Voice/Refusal)', 'Highly Dysregulated (Meltdown/Physical Aggression)']
LOCATIONS = ['Classroom 1 (JP)', 'Classroom 2 (PY)', 'Library', 'Yard (Recess/Lunch)', 'Office Area', 'Hallway', 'Specialist (Art/PE)']

# MOCK DATA for Students
MOCK_STUDENTS = [
    {'id': 's001', 'name': 'Alex Johnson', 'cohort': 'JP', 'risk_level': 'High', 'recent_incidents': 5, 'fba_plan': True},
    {'id': 's002', 'name': 'Taylor Smith', 'cohort': 'PY', 'risk_level': 'Medium', 'recent_incidents': 2, 'fba_plan': False},
    {'id': 's003', 'name': 'Izack Brown', 'cohort': 'SY', 'risk_level': 'Extreme', 'recent_incidents': 12, 'fba_plan': True},
    {'id': 's004', 'name': 'Casey Williams', 'cohort': 'JP', 'risk_level': 'Low', 'recent_incidents': 0, 'fba_plan': False},
]

# --- Helper Functions for Navigation & Data ---

def get_active_staff(role):
    """Filters staff for the logging dropdowns."""
    # Ensure current user is always available
    active_staff = [s['name'] for s in MOCK_STAFF if s['active'] or s['role'] == role]
    # Simple way to make the ADM user selectable by default if they are the user
    if role == 'ADM' and 'Admin User (ADM)' not in active_staff:
        active_staff.insert(0, 'Admin User (ADM)')
    return active_staff

def navigate_to(page, **kwargs):
    """Simple function to update the page state and rerun."""
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun()

def navigate_to_quick_log(role, student_id, student_name):
    """Initiates a new quick log session."""
    st.session_state.page = 'quick_log'
    st.session_state.role = role
    st.session_state.student = {'id': student_id, 'name': student_name}
    st.session_state.log_id = str(uuid.uuid4()) # Start a new log
    st.rerun()

def _map_abch_fields(preliminary_data):
    """Refines ABCH fields into a final context and a response plan based on input."""
    
    # A - Antecedent
    antecedent_summary = f"A: {preliminary_data['antecedent_fba']}. Details: {preliminary_data.get('antecedent_detail', 'No details provided.')}"
    
    # B - Behaviour
    behavior_summary = f"B: {preliminary_data['behavior_fba']}. Details: {preliminary_data.get('behavior_detail', 'No details provided.')}"
    
    # C - Consequence
    consequence_summary = f"C: {preliminary_data['consequence_fba']}. Details: {preliminary_data.get('consequence_detail', 'No details provided.')}"
    
    # H - Context/Hypothesis (General Context)
    incident_context = (
        f"Time: {preliminary_data['start_time'].strftime('%H:%M')} - {preliminary_data['end_time'].strftime('%H:%M')}, "
        f"Location: {preliminary_data['location']}. "
        f"Context Details: {preliminary_data.get('context_notes', 'N/A')}"
    )
    
    # Combine everything for a full log context
    final_context = f"**ABCH Log for {preliminary_data['student']['name']} on {preliminary_data['date'].strftime('%Y-%m-%d')}**\n\n" \
                    f"**Context:** {incident_context}\n" \
                    f"**Sequence:** \n* {antecedent_summary}\n* {behavior_summary}\n* {consequence_summary}\n"
    
    # Simple response plan based on the consequence
    how_to_respond_plan = f"Immediate Response Taken: {preliminary_data['consequence_fba']}. Staff to follow up based on listed outcomes."
    
    # Window of Tolerance refinement - Simple mapping for storage
    refined_wot = preliminary_data['window_of_tolerance']
    
    return refined_wot, final_context, how_to_respond_plan

# --- Initialisation and State Management ---

def initialize_state():
    """Initializes session state variables if they don't exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'mock_incident_logs' not in st.session_state:
        st.session_state.mock_incident_logs = []

# --- Render Functions ---

def render_landing_page():
    """Renders the initial role selection and login screen."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")
    st.subheader("Select Your Role to Access the Dashboard")

    roles = [s['role'] for s in MOCK_STAFF if s['active']]
    role_mapping = {r: f"{r} - {s['name']}" for r, s in zip(roles, MOCK_STAFF) if s['active']}

    # Dropdown for role selection
    selected_role_label = st.selectbox("Your Role/Area", options=list(role_mapping.values()))
    selected_role = selected_role_label.split(' - ')[0] if selected_role_label else None

    # Login button
    if st.button("Enter Dashboard", type='primary') and selected_role:
        navigate_to('staff_area', role=selected_role)
    
    st.markdown("---")
    st.info("This application is a proof-of-concept for a comprehensive, data-driven student support system.")


def render_student_card(student_data, role):
    """Renders a card summary for a student."""
    
    risk_color = {'High': '#F87171', 'Medium': '#FBBF24', 'Low': '#4ADE80', 'Extreme': '#EF4444'}.get(student_data['risk_level'], '#94A3B8')

    with st.container(border=True):
        col_icon, col_details = st.columns([1, 4])
        
        with col_icon:
            st.markdown(f'<div style="font-size: 3em; color: {risk_color}; margin-top: 10px;">👤</div>', unsafe_allow_html=True)
        
        with col_details:
            st.markdown(f"**{student_data['name']}** - Cohort: `{student_data['cohort']}`")
            st.markdown(f"Risk Level: <span style='color: {risk_color}; font-weight: bold;'>{student_data['risk_level']}</span>", unsafe_allow_html=True)
            st.markdown(f"FBA Plan: {'✅ Yes' if student_data['fba_plan'] else '❌ No'}")
            
            # Action buttons
            col_log, col_view = st.columns(2)
            
            with col_log:
                if st.button("Log Incident (Quick)", key=f"log_{student_data['id']}", type='secondary'):
                    navigate_to_quick_log(role, student_data['id'], student_data['name'])
            
            with col_view:
                if st.button("View Analysis", key=f"view_{student_data['id']}", type='secondary'):
                    navigate_to('student_detail', role=role, student={'id': student_data['id'], 'name': student_data['name']})

def render_staff_area(user_role):
    """Renders the main staff dashboard with student quick actions."""
    st.title(f"{user_role} Staff Dashboard")
    st.subheader("Quick Log & Student Overview")
    st.markdown("---")

    # Get incident count for the current user's role (mock count)
    log_count = len(st.session_state.mock_incident_logs)
    
    # Filter students for the cohort (JP, PY, SY) or show all for ADM
    if user_role in ['JP', 'PY', 'SY']:
        filtered_students = [s for s in MOCK_STUDENTS if s['cohort'] == user_role]
        st.subheader(f"Students in {user_role} Cohort")
    else:
        filtered_students = MOCK_STUDENTS
        st.subheader("All Students Overview")
    
    # Metrics
    col_metrics_1, col_metrics_2, col_metrics_3 = st.columns(3)
    col_metrics_1.metric("Students Monitored", len(filtered_students))
    col_metrics_2.metric("Total Logs Today (Mock)", f"{random.randint(1, 4)}") # Mock data for "today"
    col_metrics_3.metric("Total Logs This Session", log_count)


    # Student Cards
    st.markdown("---")
    st.subheader("Student Quick Action Cards")
    
    num_students = len(filtered_students)
    if num_students > 0:
        # Create columns dynamically (max 3 columns)
        cols = st.columns(min(3, num_students))
        
        for i, student in enumerate(filtered_students):
            with cols[i % min(3, num_students)]:
                render_student_card(student, user_role)
    else:
        st.info("No students assigned to this cohort in the mock data.")
    
    st.markdown("---")
    if st.button("Switch Role / Logout"):
        navigate_to('landing')
    
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


def render_student_analysis(student, user_role):
    """Renders detailed FBA data analysis and incident history for a selected student."""
    st.title(f"Student Analysis: {student['name']}")
    st.subheader("Functional Behaviour Assessment (FBA) Data")
    st.markdown("---")

    # Filter logs for the selected student
    student_logs = [log for log in st.session_state.mock_incident_logs if log['student']['id'] == student['id']]
    log_df = pd.DataFrame(student_logs)

    if log_df.empty:
        st.info(f"No incident logs recorded for {student['name']} in this session.")
        if st.button("Log First Incident"):
            navigate_to_quick_log(user_role, student['id'], student['name'])
        st.markdown("---")
        if st.button("← Back to Staff Area"):
            navigate_to('staff_area', role=user_role)
        return

    # Mock Data for Analysis (Combine actual logs with mock history for better visuals)
    mock_history = [
        {'behavior_fba': random.choice(BEHAVIORS_FBA), 'antecedent_fba': random.choice(ANTECEDENTS_FBA), 'consequence_fba': random.choice(CONSEQUENCES_FBA)}
        for _ in range(20)
    ]
    
    analysis_data = pd.DataFrame(student_logs)[['behavior_fba', 'antecedent_fba', 'consequence_fba']]
    analysis_data = pd.concat([analysis_data, pd.DataFrame(mock_history)]).reset_index(drop=True)

    
    st.markdown("##### Incident Count & Key Trends")
    col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)
    col_kpi_1.metric("Total Incidents (Session + Mock)", len(analysis_data))
    col_kpi_2.metric("Most Frequent Behavior", analysis_data['behavior_fba'].mode().iloc[0] if not analysis_data['behavior_fba'].empty else 'N/A')
    col_kpi_3.metric("Most Frequent Antecedent", analysis_data['antecedent_fba'].mode().iloc[0] if not analysis_data['antecedent_fba'].empty else 'N/A')

    st.markdown("---")

    st.markdown("##### Antecedent-Behavior-Consequence (ABC) Analysis Visuals")

    # 1. Behavior Frequency
    st.subheader("1. Behavior Frequency")
    behaviors = analysis_data['behavior_fba'].value_counts().reset_index()
    behaviors.columns = ['Behavior', 'Count']
    fig_b = px.bar(behaviors, x='Behavior', y='Count', title='Observed Behavior Frequency', color='Count', color_continuous_scale=px.colors.sequential.Bluered)
    st.plotly_chart(fig_b, use_container_width=True)

    # 2. Antecedent-Behavior Scatter/Matrix (Simple pairing frequency)
    st.subheader("2. Antecedent-Behavior Correlation")
    ab_counts = analysis_data.groupby(['antecedent_fba', 'behavior_fba']).size().reset_index(name='Frequency')
    
    fig_ab = px.density_heatmap(
        ab_counts, 
        x='antecedent_fba', 
        y='behavior_fba', 
        z='Frequency',
        title='Antecedent vs. Behavior Frequency',
        color_continuous_scale="Viridis",
        labels={'antecedent_fba': 'Antecedent (A)', 'behavior_fba': 'Behavior (B)'}
    )
    st.plotly_chart(fig_ab, use_container_width=True)

    st.markdown("---")
    st.subheader("Raw Incident History (Current Session Logs)")
    
    # Display the current session logs in a clean table format
    display_logs = log_df[['date', 'start_time', 'end_time', 'location', 'antecedent_fba', 'behavior_fba', 'consequence_fba', 'staff_logging', 'window_of_tolerance_refined']]
    display_logs.columns = ['Date', 'Start', 'End', 'Location', 'Antecedent', 'Behavior', 'Consequence', 'Logged By', 'WOT']
    st.dataframe(display_logs, use_container_width=True)

    st.markdown("---")
    if st.button("← Back to Staff Area"):
        navigate_to('staff_area', role=user_role)

def render_quick_log(user_role, student):
    """Renders the comprehensive quick incident log form (ABCH format)."""

    st.header(f"Quick Incident Log for {student['name']}")
    st.info("Please fill out all sections accurately to ensure high-quality data for FBA analysis.")

    # Check if a log ID is initialized (for ensuring log is only submitted once)
    log_id = st.session_state.get('log_id')
    if not log_id:
        st.warning("No active log session found. Please return to the Staff Area and select a student to start a new log.")
        return

    # --- FORM START ---
    with st.form(key='quick_log_form', clear_on_submit=False):

        st.subheader("1. Incident Details (When, Where, Who)")
        col1, col2, col3 = st.columns(3)

        # 1. Date/Time/Location/Staff
        with col1:
            log_date = st.date_input("Date of Incident", datetime.now().date(), key='log_date')
            location = st.selectbox("Location", options=LOCATIONS, key='log_location')
            # Set default staff logging user based on session role
            active_staff_options = get_active_staff(user_role)
            default_staff_index = 0
            # Attempt to find the index of the logged-in role's name for default selection
            try:
                # Assuming ADM user is named 'Admin User (ADM)' for default
                default_name = 'Admin User (ADM)' if user_role == 'ADM' else f"{user_role} User ({user_role})"
                # Fallback to a guaranteed name if mock data is inconsistent
                if user_role == 'ADM' and 'Admin User (ADM)' in active_staff_options:
                    default_staff_index = active_staff_options.index('Admin User (ADM)')
                elif 'Emily Jones (JP)' in active_staff_options:
                     default_staff_index = active_staff_options.index('Emily Jones (JP)') # General default if above fails
            except ValueError:
                pass # Use index 0 if specific name is not found
                
            staff_logging = st.selectbox("Staff Logging Incident", options=active_staff_options, index=default_staff_index)
        
        with col2:
            start_time_default = time(datetime.now().hour, datetime.now().minute) # Current time
            start_time = st.time_input("Start Time", start_time_default, step=timedelta(minutes=1), key='log_start_time')
            
            # Default end time 5 minutes after start time
            end_dt_default = datetime.combine(datetime.today(), start_time) + timedelta(minutes=5)
            end_time = st.time_input("End Time", end_dt_default.time(), step=timedelta(minutes=1), key='log_end_time')
            
        with col3:
            # Calculate duration
            if start_time and end_time:
                # Convert time objects to timedelta relative to midnight to calculate difference
                start_dt = datetime.combine(datetime.min, start_time)
                end_dt = datetime.combine(datetime.min, end_time)

                if end_dt < start_dt:
                    duration_td = (end_dt + timedelta(days=1)) - start_dt
                else:
                    duration_td = end_dt - start_dt

                # Format duration
                total_seconds = int(duration_td.total_seconds())
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                st.metric("Duration", f"{minutes}m {seconds}s")
            else:
                st.metric("Duration", "N/A")

            # Window of Tolerance
            wot = st.radio("Window of Tolerance", options=WOT_CATEGORIES, index=0, key='log_wot')
            st.markdown(f'<div style="color: #64748B; font-size: 0.8em; margin-top: -10px;">Select the child\'s state at the peak of the incident.</div>', unsafe_allow_html=True)


        st.markdown("---")

        # 2. ABCH Log
        st.subheader("2. ABCH Log")
        
        col_abch1, col_abch2, col_abch3 = st.columns(3)

        with col_abch1:
            st.markdown("##### Antecedent (A)")
            antecedent_fba = st.selectbox("What happened *immediately* before?", options=ANTECEDENTS_FBA, key='log_a_fba')
            antecedent_detail = st.text_area("A-Detail: Describe the specific event/trigger", key='log_a_detail', height=100)

        with col_abch2:
            st.markdown("##### Behavior (B)")
            behavior_fba = st.selectbox("What was the primary observable action?", options=BEHAVIORS_FBA, key='log_b_fba')
            behavior_detail = st.text_area("B-Detail: Describe the child's action (What did they do?)", key='log_b_detail', height=100)
            
        with col_abch3:
            st.markdown("##### Consequence (C)")
            consequence_fba = st.selectbox("What happened *immediately* after the behavior?", options=CONSEQUENCES_FBA, key='log_c_fba')
            consequence_detail = st.text_area("C-Detail: Describe the staff/peer response and immediate outcome", key='log_c_detail', height=100)

        # Context (H)
        st.markdown("##### Hypothesis/Context (H)")
        context_notes = st.text_area("H-Detail: Broader context, setting, staff present, and child's general mood leading up to A.", 
                                     key='log_h_context', height=100)

        st.markdown("---")

        # 3. Outcomes and Follow-up (Check all that apply)
        st.subheader("3. Outcomes and Follow-up (Check all that apply)")

        col_outcomes_1, col_outcomes_2 = st.columns(2)
        
        with col_outcomes_1:
            # Block 1 - Critical/Mandatory Reporting
            st.markdown("**Critical Incidents / Required Reporting**")
            st.checkbox("A: Send Home. Parent / Caregiver notified.", key='o_a_send_home', help="Incident resulted in student being sent home.")
            st.checkbox("B: Student Leaving supervised areas / school grounds (Elopement)", key='o_b_left_area')
            st.checkbox("C: Assault/Serious Physical Harm", key='o_c_assault')
            st.checkbox("D: Property Damage (Major)", key='o_d_property_damage')
            st.checkbox("E: ED155: Staff Injury (submit separate report)", key='o_e_staff_injury')
            st.checkbox("F: SAPOL Callout", key='o_f_sapol_callout')
            
        with col_outcomes_2:
            # Block 2 - Other Outcomes / Internal Management
            st.markdown("**Internal Management / Follow-up**")
            st.checkbox("G: Incident – student to student", key='o_g_st_to_st')
            st.checkbox("H: Incident Internally Managed (No external reporting needed)", key='o_h_managed_internally')
            st.checkbox("I: Restorative Session Scheduled", key='o_i_restorative')
            st.checkbox("J: ED155: Student injury (submit separate report)", key='o_j_first_aid_amb')
            st.checkbox("K: TAC meeting to be developed/reviewed", key='o_k_tac_meeting')
            st.checkbox("L: Other outcome / follow-up required (Describe in notes)", key='o_l_other_followup')
            st.checkbox("M: SA Ambulance Services Call out", key='o_r_call_out_amb')


        # Notes for Administration
        st.markdown("---")
        st.subheader("4. Administrative Notes (For Leadership/Case Managers)")
        admin_notes = st.text_area("Additional Notes for Leadership / Case Manager / Debriefing", key='admin_notes', height=150)

        # --- SUBMISSION ---
        st.markdown("---")
        submit_button = st.form_submit_button(label='Submit Final Incident Log', type='primary')

        if submit_button:
            # 1. Collect Preliminary Data
            preliminary_data = {
                'log_id': log_id,
                'student': student,
                'date': log_date,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'staff_logging': staff_logging,
                'window_of_tolerance': wot,
                'antecedent_fba': antecedent_fba,
                'antecedent_detail': antecedent_detail,
                'behavior_fba': behavior_fba,
                'behavior_detail': behavior_detail,
                'consequence_fba': consequence_fba,
                'consequence_detail': consequence_detail,
                'context_notes': context_notes,
                'admin_notes': admin_notes,
                'logged_by_role': user_role,
            }

            # 2. Map and Refine ABCH fields
            refined_wot, final_context, how_to_respond_plan = _map_abch_fields(preliminary_data)

            # 3. Create Final Log Entry with Outcomes
            final_log_entry = preliminary_data.copy()
            final_log_entry.update({
                'is_abch_completed': True,
                'window_of_tolerance_refined': refined_wot,
                'full_abch_context': final_context,
                'immediate_response_plan': how_to_respond_plan,
                # Outcomes mapping here (use st.session_state to retrieve checkbox values)
                'outcome_send_home': st.session_state.get('o_a_send_home', False),
                'outcome_leave_area': st.session_state.get('o_b_left_area', False),
                'outcome_assault': st.session_state.get('o_c_assault', False),
                'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
                'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
                'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
                'outcome_st_to_st': st.session_state.get('o_g_st_to_st', False),
                'outcome_managed_internally': st.session_state.get('o_h_managed_internally', False),
                'outcome_restorative': st.session_state.get('o_i_restorative', False),
                'outcome_student_injury': st.session_state.get('o_j_first_aid_amb', False),
                'outcome_tac_meeting': st.session_state.get('o_k_tac_meeting', False),
                'outcome_other_followup': st.session_state.get('o_l_other_followup', False),
                'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False),
                
            })

            # 4. Save/Append Log Entry (In a real app, you'd save to a database here)
            if 'mock_incident_logs' not in st.session_state:
                st.session_state.mock_incident_logs = []
            
            # Prepare log for storage/display (convert date/time objects to strings)
            log_to_save = final_log_entry.copy() 
            log_to_save['date'] = log_to_save['date'].strftime('%Y-%m-%d')
            log_to_save['start_time'] = log_to_save['start_time'].strftime('%H:%M')
            log_to_save['end_time'] = log_to_save['end_time'].strftime('%H:%M')
            
            # Append the log to the session state for mock data
            st.session_state.mock_incident_logs.append(log_to_save)
            
            # 5. Provide Feedback and Navigate
            st.success(f"Incident Log ({log_id[:8]}...) for {student['name']} submitted successfully! Redirecting to dashboard...")

            # Clean up temporary session state data after final save
            keys_to_delete = ['log_id', 'log_date', 'log_location', 'log_start_time', 'log_end_time', 'log_wot', 
                              'log_a_fba', 'log_a_detail', 'log_b_fba', 'log_b_detail', 'log_c_fba', 'log_c_detail', 
                              'log_h_context', 'admin_notes']
            
            # Also clean up all outcome checkboxes
            for key in list(st.session_state.keys()):
                 if key.startswith('o_'):
                    keys_to_delete.append(key)

            for key in set(keys_to_delete):
                if key in st.session_state:
                    del st.session_state[key]
            
            navigate_to('staff_area', role=user_role) # Redirect to main dashboard

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
            navigate_to('staff_area', role=current_role if current_role else 'ADM')


    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role if current_role else 'ADM')

    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role)
        else:
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
