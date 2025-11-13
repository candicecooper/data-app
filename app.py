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
# Corrected #F1F5N9 to #F1F5F9 for valid hex color
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
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] > div > input,
    div[data-testid="stTimeInput"] > div > input
    {
        background-color: #334155;
        color: #F1F5F9;
        border-radius: 8px;
        border: 1px solid #475569;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4C51BF; /* Indigo primary color */
        color: #F1F5F9;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #4338CA; /* Darker indigo on hover */
    }
    .stButton > button:disabled {
        background-color: #334155;
        color: #94A3B8;
    }
    
    /* Primary Button (Submit Log) */
    .stButton[data-testid="stFormSubmitButton"] > button {
        background-color: #10B981; /* Emerald green */
        color: #0F172A;
        font-weight: bold;
    }
    .stButton[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #059669;
    }

    /* Expander/Info Boxes */
    div[data-testid="stAlert"] { border-radius: 12px; }
    
    /* Multiselect/Checkbox appearance */
    .stMultiSelect, .stCheckbox { color: #E2E8F0; }

    /* Custom Header for Student Profile */
    .student-header {
        background-color: #334155;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    /* Fix column gaps */
    div[data-testid="stColumn"] {
        padding-top: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS (FROM UPLOADED FILE) ---
# NOTE: This data is included for the staff selection logic in the forms. 
# You should replace 'MOCK_STAFF' and the staff-related helper functions
# (`get_active_staff`) with your application's actual data fetching logic.
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- FBA and Data Constants (FROM UPLOADED FILE) ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)', 'Minor Physical Contact', 'Other: Specify in Description']
ANTECEDENTS_FBA = ['Request/Demand', 'Transition', 'Change in Routine', 'Peer Interaction (Conflict)', 'Task Difficulty', 'Attention Withdrawn/Denied', 'Sensory Overload', 'Unstructured Time (Recess/Break)', 'Other: Specify in Description']
CONSEQUENCES_FBA = ['Restorative Conversation', 'Time Out (In Class/Area)', 'Loss of Privileges', 'Removal from Activity', 'Parent Contact (Informal)', 'Peer Mediation', 'Other: Specify in Description', 'No Consequence (De-escalation)']
LOCATIONS = ['Classroom (Main)', 'Playground (Oval)', 'Specific Learning Area (Art/Science)', 'Office/Admin', 'Corridor', 'Bathroom', 'Library', 'Canteen/Cafeteria', 'Out of School Grounds']

# Used for the referral outcomes section (Outcomes/Actions)
REFERRAL_OUTCOMES = {
    'Emergency': [
        ('o_c_assault', 'Assault/Threats (Staff/Student)'),
        ('o_d_property_damage', 'Significant Property Damage'),
        ('o_e_staff_injury', 'Staff Injury'),
        ('o_f_sapol_callout', 'SAPOL Callout'),
        ('o_r_call_out_amb', 'Ambulance Callout'),
    ],
    'Internal Actions': [
        ('o_a_send_home', 'Student Sent Home/Exclusion'),
        ('o_b_left_area', 'Student Left Area/Eloped'),
        ('o_g_detention', 'Detention Issued'),
        ('o_h_formal_warning', 'Formal Warning Issued'),
        ('o_i_restorative_process', 'Formal Restorative Process'),
    ],
    'Medical/Support': [
        ('o_j_first_aid_amb', 'First Aid administered (Non-Ambulance)'),
        ('o_k_psych_support', 'Referral to Psychologist/Counsellor'),
        ('o_l_leadership_meeting', 'Leadership/Team Meeting Held'),
    ],
    'Parent/External Communication': [
        ('o_m_parent_formal', 'Formal Parent Meeting Scheduled'),
        ('o_n_sso_referral', 'SSO/Welfare Follow-up'),
        ('o_p_external_referral', 'External Agency Referral'),
    ]
}

# --- Helper Functions for Staff and Data (FROM UPLOADED FILE) ---

def get_active_staff():
    """Returns a list of active staff names for use in dropdowns."""
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_staff_name_from_id(staff_id):
    """Mocks fetching a staff member's name from their ID."""
    try:
        return next(s['name'] for s in MOCK_STAFF if s['id'] == staff_id)
    except StopIteration:
        return "Unknown Staff"


# --- MOCK STUDENT DATA ---
MOCK_STUDENTS = [
    {'id': 'S001', 'name': 'Alex Johnson', 'grade': 5, 'plan_status': 'Current FBA/BSP', 'risk_level': 'High'},
    {'id': 'S002', 'name': 'Ben Carter', 'grade': 4, 'plan_status': 'Low Risk Monitoring', 'risk_level': 'Low'},
    {'id': 'S003', 'name': 'Chloe Davis', 'grade': 6, 'plan_status': 'In Review', 'risk_level': 'Medium'},
]

# --- State Management and Navigation ---

def initialize_state():
    """Initializes session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'log_history' not in st.session_state:
        st.session_state.log_history = []
    if 'last_log_id' not in st.session_state:
        st.session_state.last_log_id = None

def navigate_to(page_name, role=None, student=None):
    """Handles application navigation and state updates."""
    st.session_state.page = page_name
    if role:
        st.session_state.role = role
    if student:
        st.session_state.student = student
    st.rerun()

# --- Quick Log Submission Logic (FROM UPLOADED FILE) ---

def save_incident_log(preliminary_data):
    """
    Handles the submission and final processing of the quick incident log data.
    In a real app, this would push data to a database (e.g., Firestore).
    """
    # 1. Gather all data from Session State (which holds the results of the form)
    # This logic assumes the form fields are keyed in st.session_state as defined in render_quick_log
    
    # 2. Process free-text data
    refined_wot = st.session_state.get('wot_text', 'No Window of Tolerance details provided.')
    final_context = st.session_state.get('context_text', 'No contextual details provided.')
    how_to_respond_plan = st.session_state.get('response_plan_text', 'No specific response plan provided.')

    # 3. Compile final log entry
    final_log_entry = preliminary_data.copy()
    final_log_entry.update({
        'is_abch_completed': True,
        'window_of_tolerance': refined_wot,
        'context': final_context,
        'how_to_respond': how_to_respond_plan,
        
        # Outcomes mapping here (use st.session_state to retrieve checkbox values)
        'outcome_send_home': st.session_state.get('o_a_send_home', False),
        'outcome_leave_area': st.session_state.get('o_b_left_area', False),
        'outcome_assault': st.session_state.get('o_c_assault', False),
        'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
        'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
        'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
        'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False) or st.session_state.get('o_j_first_aid_amb', False),
        
        # Other fields from the ABCH form would need to be saved in your target app's database structure
        'location': st.session_state.get('log_location'),
        'antecedent': st.session_state.get('log_antecedent'),
        'behavior': st.session_state.get('log_behavior'),
        'consequence': st.session_state.get('log_consequence'),
        'incident_date': st.session_state.get('log_date'),
        'start_time': st.session_state.get('log_start_time'),
        'end_time': st.session_state.get('log_end_time'),
        'duration_minutes': st.session_state.get('log_duration'),
        'staff_involved': st.session_state.get('log_staff_involved'),
        'staff_witness': st.session_state.get('log_staff_witnesses'),
    })
    
    # 4. Mock Database Save
    st.session_state.last_log_id = str(uuid.uuid4())
    st.session_state.log_history.append(final_log_entry)

    # 5. Clean up temporary session state data after final save
    # Note: For a real app, you would only clear state after a confirmed successful DB write.
    for key in list(st.session_state.keys()):
        if key.startswith(('log_', 'wot_text', 'context_text', 'response_plan_text', 'o_')):
            if key in st.session_state:
                del st.session_state[key]
    
    st.success(f"Quick Incident Log submitted successfully! (ID: {st.session_state.last_log_id[:8]}...)")
    
    # Navigate back to student detail page after successful save
    navigate_to('student_detail', student=final_log_entry['student_id'], role=final_log_entry['reporter_role'])


# --- Page Render Functions ---

def render_landing_page():
    """Renders the initial role selection page."""
    st.title("Welcome to the Behaviour Support & Data Analysis Tool")
    st.subheader("Please select your role to proceed.")

    roles = [('Junior Primary (JP)', 'JP'), ('Primary (PY)', 'PY'), ('Senior Years (SY)', 'SY'), ('Admin/Leadership', 'ADM')]

    col = st.columns(len(roles))
    
    for i, (label, role_key) in enumerate(roles):
        with col[i]:
            if st.button(label, key=f'role_button_{role_key}', use_container_width=True, type='secondary'):
                navigate_to('staff_area', role=role_key)

    st.markdown("---")
    st.info("This tool supports evidence-based Functional Behaviour Assessment (FBA) by enabling quick, contextual logging and detailed analysis of student behaviour.")


def render_student_analysis(student, role):
    """Renders the detailed student analysis dashboard."""
    
    # Ensure student is a dictionary object
    if isinstance(student, str):
        student_obj = next((s for s in MOCK_STUDENTS if s['id'] == student), None)
        if not student_obj:
            st.error("Student not found. Returning to staff area.")
            navigate_to('staff_area', role=role)
            return
        student = student_obj

    st.markdown(f'<div class="student-header"><h1>📊 Behaviour Analysis: {student["name"]}</h1>'
                f'<p style="font-size: 1.1em; margin: 0;">Grade: <b>{student["grade"]}</b> | Risk Level: <b><span style="color: {"red" if student["risk_level"] == "High" else "orange" if student["risk_level"] == "Medium" else "green"};">{student["risk_level"]}</span></b> | Plan: <b>{student["plan_status"]}</b></p></div>', 
                unsafe_allow_html=True)
    
    st.subheader("Quick Actions")
    col_actions = st.columns(3)
    
    if col_actions[0].button("📝 Log Incident", key='nav_log_incident', use_container_width=True, type='primary'):
        navigate_to('quick_log', student=student['id'], role=role)
        
    if col_actions[1].button("📋 View Plan/FBA", key='view_plan', use_container_width=True):
        st.info("Mock feature: Displaying detailed FBA/BSP content.")
        
    if col_actions[2].button("📞 Contact Parents", key='contact_parents', use_container_width=True):
        st.info("Mock feature: Preparing parent contact template.")
        
    st.markdown("---")
    
    st.subheader("Incident History")

    # Filter logs for the current student
    student_logs = [log for log in st.session_state.log_history if log['student_id'] == student['id']]

    if student_logs:
        df_logs = pd.DataFrame(student_logs)
        
        st.caption(f"Total Logs: **{len(df_logs)}**")
        
        # --- Visualization Section ---
        viz_cols = st.columns(2)
        
        # 1. Behavior Frequency
        behavior_counts = df_logs['behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig_behavior = px.bar(
            behavior_counts, 
            x='Behavior', 
            y='Count', 
            title='Top Behaviours',
            color='Count',
            color_continuous_scale=px.colors.sequential.Plasma,
            template="plotly_dark"
        )
        viz_cols[0].plotly_chart(fig_behavior, use_container_width=True)

        # 2. ABC Scatter Plot (Mocking data for visualization)
        df_abc = df_logs[['antecedent', 'behavior', 'consequence']].copy()
        df_abc['x'] = df_abc['antecedent'].apply(lambda x: ANTECEDENTS_FBA.index(x))
        df_abc['y'] = df_abc['behavior'].apply(lambda x: BEHAVIORS_FBA.index(x))
        df_abc['z'] = df_abc['consequence'].apply(lambda x: CONSEQUENCES_FBA.index(x))
        
        fig_scatter = px.scatter(
            df_abc,
            x='antecedent', 
            y='behavior', 
            color='consequence', 
            title='Antecedent vs. Behavior (Colored by Consequence)',
            template="plotly_dark",
            height=400
        )
        viz_cols[1].plotly_chart(fig_scatter, use_container_width=True)

        # --- Detailed Log Table ---
        st.subheader("Recent Logs")
        df_logs_display = df_logs.sort_values(by='timestamp_logged', ascending=False).head(10)
        
        df_display = df_logs_display[[
            'incident_date', 'start_time', 'duration_minutes', 'location', 
            'antecedent', 'behavior', 'consequence', 'context'
        ]]
        
        st.dataframe(
            df_display, 
            column_config={
                "incident_date": st.column_config.DateColumn("Date", format="YYYY/MM/DD"),
                "start_time": st.column_config.TimeColumn("Time", format="HH:mm"),
                "duration_minutes": st.column_config.NumberColumn("Duration (min)"),
                "context": st.column_config.Column("Narrative", width="large")
            },
            hide_index=True,
            use_container_width=True
        )

    else:
        st.info(f"No incident logs recorded yet for {student['name']}.")
        
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Staff Area", key='nav_back_staff_from_detail'):
        navigate_to('staff_area', role=role)


def render_staff_area(role):
    """Renders the main staff dashboard for selecting students."""
    st.title(f"{get_staff_name_from_id(role)} Staff Dashboard")
    st.subheader("Select a Student for Behaviour Support or Logging")
    
    col_back, col_role = st.columns([1, 4])
    if col_back.button("← Change Role", key='nav_back_landing'):
        navigate_to('landing')
    
    col_role.markdown(f"**Current Role:** :orange[{get_staff_name_from_id(role)}]")
    
    st.markdown("---")

    # Display student list in a data-driven table
    df_students = pd.DataFrame(MOCK_STUDENTS)
    
    # --- FIX: Replaced ButtonColumn with standard Selectbox for compatibility ---
    
    student_names = df_students['name'].tolist()
    
    # Use st.selectbox for selection
    selected_name = st.selectbox(
        "Choose a Student to View Details:",
        options=["-- Select a Student --"] + student_names,
        key="student_selector"
    )

    selected_student_id = None
    
    if selected_name != "-- Select a Student --":
        # Find the ID of the selected student
        selected_student_row = df_students[df_students['name'] == selected_name].iloc[0]
        selected_student_id = selected_student_row['id']
        
        st.markdown("---")
        # Use a primary button to trigger navigation
        if st.button(f"View Analysis for {selected_name}", type="primary", use_container_width=True):
            navigate_to('student_detail', student=selected_student_id, role=role)

    st.subheader("Full Student Directory")
    
    # Display the directory for reference
    st.dataframe(
        df_students[['id', 'name', 'grade', 'plan_status', 'risk_level']],
        column_config={
            "id": "Student ID",
            "name": "Name",
            "grade": "Grade",
            # We keep standard column_config elements as they are supported
            "plan_status": st.column_config.Column("Plan Status", width="medium"),
            "risk_level": st.column_config.Column("Risk Level", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


# --- Page Render Function (Quick Log) (FROM UPLOADED FILE) ---

def render_quick_log(role, student):
    """Renders the comprehensive quick incident logging form."""
    
    # Initialize log date/time defaults if not present
    today = datetime.now().date()
    now_time = datetime.now().time()
    
    if 'log_date' not in st.session_state:
        st.session_state.log_date = today
    if 'log_start_time' not in st.session_state:
        st.session_state.log_start_time = now_time
    if 'log_end_time' not in st.session_state:
        st.session_state.log_end_time = (datetime.combine(today, now_time) + timedelta(minutes=10)).time()
        
    # --- FIX APPLIED HERE: Ensure default staff involved is a list of strings (names) ---
    if 'log_staff_involved' not in st.session_state:
        # Find the staff object corresponding to the current role (e.g., 'JP')
        staff_match = next((s for s in MOCK_STAFF if s['role'] == role), None)
        
        # Extract the name (string) to use as the default value in the multiselect
        if staff_match:
            default_name = staff_match['name']
        else:
            default_name = 'Admin User (ADM)' # Fallback name
            
        # Set the default value as a list of strings
        st.session_state.log_staff_involved = [default_name] 

    if 'log_staff_witnesses' not in st.session_state:
        st.session_state.log_staff_witnesses = []

    st.title(f"Quick Incident Log for {student['name']}")
    st.caption(f"Role: **{role}** | Student ID: **{student['id']}** | Reporting: **{get_staff_name_from_id(role)}**")

    st.markdown("---")

    # --- Start of Incident Log Form ---
    with st.form(key='quick_incident_log_form', clear_on_submit=False):
        
        # --- Section 1: Incident Details (Date, Time, Location) ---
        st.subheader("1. Incident Core Details")
        col1, col2, col3 = st.columns([1.5, 1, 1])

        # Date
        st.session_state.log_date = col1.date_input(
            "Incident Date", 
            value=st.session_state.log_date, 
            key='log_date_widget'
        )

        # Start Time
        st.session_state.log_start_time = col2.time_input(
            "Start Time", 
            value=st.session_state.log_start_time, 
            step=timedelta(minutes=1),
            key='log_start_time_widget'
        )

        # End Time
        st.session_state.log_end_time = col3.time_input(
            "End Time", 
            value=st.session_state.log_end_time, 
            step=timedelta(minutes=1),
            key='log_end_time_widget'
        )
        
        # Calculate Duration (in minutes) for display and storage
        try:
            start_dt = datetime.combine(st.session_state.log_date, st.session_state.log_start_time)
            end_dt = datetime.combine(st.session_state.log_date, st.session_state.log_end_time)
            if end_dt < start_dt:
                # Handle incidents crossing midnight (rare for school, but robust)
                end_dt += timedelta(days=1) 
            duration = (end_dt - start_dt).total_seconds() / 60
            st.session_state.log_duration = round(duration, 1)
            st.markdown(f"**Calculated Duration:** :green[{st.session_state.log_duration} minutes]")
        except Exception:
            st.error("Error calculating duration. Check date/time inputs.")
            st.session_state.log_duration = 0


        # Location
        st.session_state.log_location = st.selectbox(
            "Incident Location",
            options=LOCATIONS,
            key='log_location_widget',
            index=LOCATIONS.index(st.session_state.get('log_location')) if st.session_state.get('log_location') in LOCATIONS else 0,
            help="Where did the core incident occur?"
        )
        
        st.markdown("---")

        # --- Section 2: ABC-H Data ---
        st.subheader("2. ABC-H Data Collection")
        st.caption("Complete the Antecedent, Behavior, and Consequence fields. The 'H' (Hypothesis) is derived from this data over time.")
        
        col_abc1, col_abc2, col_abc3 = st.columns(3)
        
        # Antecedent
        st.session_state.log_antecedent = col_abc1.selectbox(
            "Antecedent (Trigger)",
            options=ANTECEDENTS_FBA,
            key='log_antecedent_widget',
            index=ANTECEDENTS_FBA.index(st.session_state.get('log_antecedent')) if st.session_state.get('log_antecedent') in ANTECEDENTS_FBA else 0,
            help="What immediately preceded the behavior?"
        )

        # Behavior
        st.session_state.log_behavior = col_abc2.selectbox(
            "Behavior (Observed Action)",
            options=BEHAVIORS_FBA,
            key='log_behavior_widget',
            index=BEHAVIORS_FBA.index(st.session_state.get('log_behavior')) if st.session_state.get('log_behavior') in BEHAVIORS_FBA else 0,
            help="The specific action(s) the student engaged in."
        )
        
        # Consequence
        st.session_state.log_consequence = col_abc3.selectbox(
            "Consequence (Staff Response)",
            options=CONSEQUENCES_FBA,
            key='log_consequence_widget',
            index=CONSEQUENCES_FBA.index(st.session_state.get('log_consequence')) if st.session_state.get('log_consequence') in CONSEQUENCES_FBA else 0,
            help="What staff did immediately following the behavior."
        )
        
        st.markdown("---")

        # --- Section 3: Staff Involvement ---
        st.subheader("3. Staff and Witnesses")
        staff_options = get_active_staff()

        # Staff Directly Involved
        st.session_state.log_staff_involved = st.multiselect(
            "Staff Directly Involved/Responding (Mandatory)",
            options=staff_options,
            default=st.session_state.log_staff_involved, # Now correctly a list of strings
            key='log_staff_involved_widget',
            help="Which staff member(s) were actively responding to the incident?"
        )
        
        # Staff Witnesses
        st.session_state.log_staff_witnesses = st.multiselect(
            "Staff Witnesses (Optional)",
            options=[s for s in staff_options if s not in st.session_state.log_staff_involved],
            default=st.session_state.log_staff_witnesses,
            key='log_staff_witnesses_widget',
            help="Other staff who observed the incident."
        )

        st.markdown("---")

        # --- Section 4: Narrative and Context ---
        st.subheader("4. Narrative and Contextual Details")
        
        # Window of Tolerance
        st.markdown("**Window of Tolerance (Pre-Incident)**")
        st.session_state.wot_text = st.text_area(
            "Describe the student's regulation state leading up to the event (e.g., signs of dysregulation, calm/hyper-arousal level).",
            value=st.session_state.get('wot_text', ''),
            key='wot_text_widget',
            height=100
        )
        
        # Context/Description
        st.markdown("**Incident Description/Context**")
        st.session_state.context_text = st.text_area(
            "Provide a detailed, objective description of the incident, including what the student said/did. Include any relevant environmental factors or peer interactions.",
            value=st.session_state.get('context_text', ''),
            key='context_text_widget',
            height=150
        )
        
        st.markdown("---")

        # --- Section 5: Follow-up and Outcomes ---
        st.subheader("5. Follow-up Actions and Outcomes")

        # How to respond (Future planning)
        st.markdown("**Future Response Planning**")
        st.session_state.response_plan_text = st.text_area(
            "What was learned from this incident? What specific strategies will be implemented immediately and in the future to prevent or respond to this behavior?",
            value=st.session_state.get('response_plan_text', ''),
            key='response_plan_text_widget',
            height=100
        )
        
        # Referral Outcomes (Checkboxes grouped by category)
        st.markdown("**Outcomes/Required Referrals (Check all that apply)**")
        
        # Create 4 columns for the outcomes
        cols_outcome = st.columns(4)
        
        # Iterate through the defined outcomes and place them in the columns
        col_index = 0
        for category, outcomes in REFERRAL_OUTCOMES.items():
            cols_outcome[col_index].markdown(f"**{category}**")
            for key, label in outcomes:
                # Use st.session_state to manage the state of the checkboxes across re-runs
                st.session_state[key] = cols_outcome[col_index].checkbox(
                    label, 
                    value=st.session_state.get(key, False), 
                    key=f'outcome_check_{key}'
                )
            col_index = (col_index + 1) % 4 # Move to the next column


        st.markdown("---")

        # --- Form Submission ---
        
        # Check required fields before submission (Staff Involved and Context are critical)
        staff_check = len(st.session_state.get('log_staff_involved', [])) > 0
        context_check = len(st.session_state.get('context_text', '').strip()) > 10
        
        can_submit = staff_check and context_check
        
        if not staff_check:
            st.error("Please select at least one staff member directly involved/responding.")
        if not context_check:
            st.warning("Please provide a detailed objective description of the incident (Section 4).")


        submitted = st.form_submit_button(
            label="💾 Submit Quick Incident Log",
            disabled=not can_submit,
            type="primary"
        )
        
        if submitted and can_submit:
            # Prepare preliminary data before calling the save function
            preliminary_data = {
                'id': str(uuid.uuid4()),
                'student_id': student['id'],
                'student_name': student['name'],
                'reporter_role': role,
                'timestamp_logged': datetime.now().isoformat(),
            }
            save_incident_log(preliminary_data)


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
        # Need to fetch student object from ID if only ID is stored
        student_data = next((s for s in MOCK_STUDENTS if s['id'] == current_student), None) if isinstance(current_student, str) else current_student
        
        if student_data and current_role:
             render_quick_log(current_role, student_data) 
        else:
            st.error("Missing context. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)


    elif st.session_state.page == 'student_detail':
        # Need to fetch student object from ID if only ID is stored
        student_data = next((s for s in MOCK_STUDENTS if s['id'] == current_student), None) if isinstance(current_student, str) else current_student

        if student_data and current_role:
            render_student_analysis(student_data, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)

    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area(current_role)
        else:
            navigate_to('landing')

if __name__ == '__main__':
    main()
