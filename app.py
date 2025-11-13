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
    div[data-testid="stSelectbox"] > div > div > div,
    div[data-testid="stTimeInput"] > div > input,
    div[data-testid="stDateInput"] > div > input {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0F5E6B; /* A vibrant teal */
        color: #F1F5F9;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #0B4B55;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    /* Info and Warning boxes */
    [data-testid="stAlert"] {
        border-radius: 10px;
        border: none;
    }
    .st-emotion-cache-1cypcdb { /* Info alert styling */
        background-color: #1E3A8A !important; 
    }
    .st-emotion-cache-1g83s4g { /* Warning alert styling */
        background-color: #78350F !important;
    }
    
    /* Centered Text for Headers */
    .centered-header {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS ---
# This data is included for the staff selection logic in the forms. 
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 
                  'Self-Injurious Behaviour', 'Outburst (Verbal)', 'Outburst (Physical)', 
                  'Aggression (Staff)', 'Non-Compliance', 'Other (Please specify)']

TRIGGERS = [
    'Academic demand (difficult task)', 'Academic demand (easy task)', 'Transition (expected)', 
    'Transition (unexpected)', 'Peer conflict/attention', 'Adult attention (positive)', 
    'Adult attention (negative/redirection)', 'Unstructured time/boredom', 
    'Sensory overload (noise, light, crowds)', 'Change in routine', 'Internal state (hungry, tired, unwell)', 
    'Access to preferred item/activity denied', 'Other (Please specify)'
]

FUNCTIONS = ['Gain Tangibles/Activity', 'Gain Attention (Adult)', 'Gain Attention (Peer)', 
             'Escape/Avoid Task/Demand', 'Escape/Avoid Sensory Input', 'Automatic/Sensory']

INTERVENTION_STRATEGIES = [
    'Prompting (Verbal/Visual/Physical)', 'Redirection/Distraction', 'Planned Ignoring', 
    'Differential Reinforcement (DRA/DRO)', 'Proximity Control', 'Non-contingent reinforcement', 
    'Offering Choice', 'Use of Calming Strategy (e.g., breathing, deep pressure)', 
    'Sensory Break', 'Crisis Management Procedure (CM)', 'Restorative Conversation',
    'Time Out/Cool Down', 'Other (Please specify)'
]

DE_ESCALATION_TOOLS = [
    'Deep Breathing Prompts', 'Sensory Kit/Box', 'Weighted Blanket/Vest', 'Fidget Toy', 
    'Safe Space (e.g., chill out zone, retreat)', 'Grounding Techniques', 
    'First/Then Chart', 'Visual Schedule', 'Calm Voice/Low Tone', 'Silence/Non-verbal cueing', 
    'Other (Please specify)'
]

WINDOW_OF_TOLERANCE_OPTIONS = [
    "Optimum (Calm, engaged, receptive)",
    "Hypoarousal (Disengaged, quiet, withdrawn, frozen)",
    "Hyperarousal (Agitated, highly reactive, overwhelmed, defensive)"
]

EMOTIONAL_STATES = [
    'Calm', 'Frustrated', 'Angry', 'Anxious', 'Sad', 'Excited (overstimulated)', 'Withdrawn', 'Confused', 'Tired'
]

# --- MOCK STUDENT & LOG DATA (for a runnable application) ---
MOCK_STUDENT_DATA = pd.DataFrame([
    {'id': 'stu_a', 'name': 'Alex Johnson', 'year': 'JP', 'profile': 'Has an FBA, moderate support needs.'},
    {'id': 'stu_b', 'name': 'Beth Smith', 'year': 'PY', 'profile': 'Minimal support needed, focus on social skills.'},
    {'id': 'stu_c', 'name': 'Charlie Brown', 'year': 'SY', 'profile': 'High support needs, has an SSO.'},
])

MOCK_LOGS = pd.DataFrame([
    {'id': 'log1', 'student_id': 'stu_a', 'date': '2025-10-20', 'time': '10:30', 'behavior': 'Verbal Refusal', 'duration_min': 5, 'staff_id': 's1', 'is_critical': False, 'details': 'Refused to start math task.', 'trigger': 'Academic demand (difficult task)', 'function': 'Escape/Avoid Task/Demand', 'intervention': 'Offering Choice', 'outcome_send_home': False, 'outcome_assault': False, 'context': 'Classroom, Math lesson.'},
    {'id': 'log2', 'student_id': 'stu_a', 'date': '2025-10-21', 'time': '14:15', 'behavior': 'Elopement', 'duration_min': 15, 'staff_id': 's2', 'is_critical': True, 'details': 'Ran out of classroom during transition.', 'trigger': 'Transition (expected)', 'function': 'Escape/Avoid Sensory Input', 'intervention': 'Crisis Management Procedure (CM)', 'outcome_send_home': True, 'outcome_assault': False, 'context': 'Hallway, moving to library.'},
    {'id': 'log3', 'student_id': 'stu_b', 'date': '2025-10-22', 'time': '09:00', 'behavior': 'Aggression (Peer)', 'duration_min': 2, 'staff_id': 's3', 'is_critical': False, 'details': 'Pushed a peer during morning lining up.', 'trigger': 'Peer conflict/attention', 'function': 'Gain Attention (Peer)', 'intervention': 'Restorative Conversation', 'outcome_send_home': False, 'outcome_assault': False, 'context': 'Outside, lining up.'},
])

# --- HELPER FUNCTIONS ---

def navigate_to(page_name, student=None, role=None):
    """Sets the session state to navigate to a new page."""
    if student:
        st.session_state.student = student
        st.session_state.student_details = get_student_details(student)
    if role:
        st.session_state.role = role
    st.session_state.page = page_name

def get_active_staff():
    """Retrieves a list of currently active staff names."""
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_staff_id(staff_name):
    """Retrieves the ID of a staff member by name."""
    for s in MOCK_STAFF:
        if s['name'] == staff_name:
            return s['id']
    return None

def get_student_details(student_name):
    """Mocks fetching student details by name."""
    details = MOCK_STUDENT_DATA[MOCK_STUDENT_DATA['name'] == student_name].to_dict('records')
    return details[0] if details else None

def get_student_analysis_data(student_name):
    """Mocks fetching log data for a specific student for analysis."""
    student_id = MOCK_STUDENT_DATA[MOCK_STUDENT_DATA['name'] == student_name]['id'].iloc[0]
    return MOCK_LOGS[MOCK_LOGS['student_id'] == student_id]

def save_log_to_db(preliminary_data, is_critical=False):
    """
    Saves the log entry to the mock database (MOCK_LOGS DataFrame).
    This includes the detailed logic for ABCH form completion if applicable.
    """
    global MOCK_LOGS
    
    # 1. ABCH Completion Logic
    if is_critical:
        # Critical incidents mandate full ABCH completion
        refined_wot = st.session_state.get('wot_level', 'Not provided.')
        final_context = st.session_state.get('critical_context', 'No context provided.')
        how_to_respond_plan = st.session_state.get('critical_response', 'No response plan provided.')
        is_abch_completed = True
        
        # Outcomes mapping (uses st.session_state for critical form checkboxes)
        outcome_data = {
            'outcome_send_home': st.session_state.get('o_a_send_home', False),
            'outcome_leave_area': st.session_state.get('o_b_left_area', False),
            'outcome_assault': st.session_state.get('o_c_assault', False),
            'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
            'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
            'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
            'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False) or st.session_state.get('o_j_first_aid_amb', False),
        }
    else:
        # Quick log may not complete full ABCH
        refined_wot = preliminary_data.get('window_of_tolerance', 'Not provided.')
        final_context = preliminary_data.get('context', 'No context provided.')
        how_to_respond_plan = preliminary_data.get('intervention', 'No response plan provided.')
        is_abch_completed = preliminary_data.get('is_abch_completed', False)

        # Quick log only tracks primary outcome (Is critical determines full outcome mapping)
        outcome_data = {
            'outcome_send_home': preliminary_data.get('primary_outcome') == 'Sent Home',
            'outcome_leave_area': preliminary_data.get('primary_outcome') == 'Left Area',
            'outcome_assault': preliminary_data.get('primary_outcome') == 'Assault (Peer/Staff)',
            'outcome_property_damage': preliminary_data.get('primary_outcome') == 'Property Damage',
            'outcome_staff_injury': False,
            'outcome_sapol_callout': False,
            'outcome_ambulance': False,
        }

    final_log_entry = preliminary_data.copy()
    final_log_entry.update({
        'id': str(uuid.uuid4()),
        'is_abch_completed': is_abch_completed,
        'window_of_tolerance': refined_wot,
        'context': final_context,
        'how_to_respond': how_to_respond_plan,
        'is_critical': is_critical,
        **outcome_data,
    })
    
    # 2. Add to Mock Database (DataFrame)
    new_log_df = pd.DataFrame([final_log_entry])
    MOCK_LOGS = pd.concat([MOCK_LOGS, new_log_df], ignore_index=True)
    
    # 3. Clean up temporary session state data after final save (only for critical form)
    if is_critical:
        keys_to_delete = ['wot_level', 'critical_context', 'critical_response']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        # Delete outcome checkbox states
        for key in st.session_state.keys():
            if key.startswith('o_'):
                del st.session_state[key]

    st.success(f"Incident Log recorded successfully! (Type: {'Critical' if is_critical else 'Quick'})")
    
    # Navigate back to staff area after successful logging
    current_role = st.session_state.get('role', 'ADM')
    navigate_to('staff_area', role=current_role)
    

# --- RENDERING FUNCTIONS ---

def render_landing_page():
    st.markdown("<h1 class='centered-header'>Welcome to the Behaviour Support Tool</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("Select your staff role to access the dashboard and student logs.")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Admin (ADM)"):
            navigate_to('staff_area', role='ADM')
    with col2:
        if st.button("PY Staff (PY)"):
            navigate_to('staff_area', role='PY')
    with col3:
        if st.button("JP Staff (JP)"):
            navigate_to('staff_area', role='JP')

def render_staff_area(role):
    st.markdown(f"<h1 class='centered-header'>Staff Dashboard: {role}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_log, col_crit = st.columns(2)

    with col_log:
        st.subheader("Quick Incident Log")
        st.info("Select a student to log a quick incident.")
        student_names = MOCK_STUDENT_DATA['name'].tolist()
        selected_student = st.selectbox("Select Student for Quick Log:", student_names, key='quick_log_student_select')
        
        if st.button(f"Start Quick Log for {selected_student}"):
            navigate_to('quick_log', student=selected_student, role=role)

    with col_crit:
        st.subheader("Critical Incident Form")
        st.warning("⚠️ Use this form for incidents requiring **Principal notification** (e.g., self-harm, serious aggression, police involvement).")
        critical_student = st.selectbox("Select Student for Critical Incident:", student_names, key='critical_log_student_select')
        
        if st.button(f"Start Critical Incident Form for {critical_student}"):
            navigate_to('critical_incident', student=critical_student, role=role)
            
    st.markdown("---")
    st.subheader("Student Data Analysis")
    st.info("Select a student to view their FBA data, trends, and intervention efficacy.")
    
    analysis_student = st.selectbox("Select Student for Detailed Analysis:", student_names, key='analysis_student_select')
    
    if st.button(f"View Analysis for {analysis_student}"):
        navigate_to('student_detail', student=analysis_student, role=role)
        

def render_student_analysis(student_name, role):
    st.markdown(f"<h1 class='centered-header'>FBA & Trend Analysis: {student_name}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    details = get_student_details(student_name)
    log_data = get_student_analysis_data(student_name)
    
    st.subheader(f"Profile: {details['profile']}")

    # Display raw data for context
    st.markdown("### Incident Log History")
    st.dataframe(
        log_data[['date', 'time', 'behavior', 'duration_min', 'trigger', 'intervention', 'is_critical', 'details']], 
        use_container_width=True,
        hide_index=True
    )

    if not log_data.empty:
        # Time-based analysis (e.g., behaviors per week)
        log_data['datetime'] = pd.to_datetime(log_data['date'] + ' ' + log_data['time'])
        log_data['week'] = log_data['datetime'].dt.to_period('W')
        weekly_counts = log_data.groupby('week').size().reset_index(name='Count')
        weekly_counts['Week Start'] = weekly_counts['week'].astype(str).apply(lambda x: x.split('/')[0])

        st.markdown("### Trend: Incidents Per Week")
        fig = px.bar(weekly_counts, x='Week Start', y='Count', title='Total Incidents Over Time', 
                     color_discrete_sequence=['#4ADE80'])
        st.plotly_chart(fig, use_container_width=True)

        # Scatter plot for time of day
        st.markdown("### Trend: Incident Time of Day")
        log_data['hour'] = log_data['datetime'].dt.hour
        time_counts = log_data['hour'].value_counts().sort_index().reset_index()
        time_counts.columns = ['Hour', 'Incidents']

        fig_time = px.bar(time_counts, x='Hour', y='Incidents', 
                          title='Incidents by Hour of Day (0-23)', 
                          color_discrete_sequence=['#3B82F6'])
        fig_time.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig_time, use_container_width=True)

    else:
        st.info("No incident logs available for this student to generate analysis.")

    st.markdown("---")
    if st.button("← Back to Dashboard"):
        navigate_to('staff_area', role=role)


def render_quick_log(role, student_name):
    """
    Renders the Quick Incident Log form (ABCH Lite).
    This function is now based on the isolated code provided by the user.
    """
    st.markdown(f"<h1 class='centered-header'>Quick Incident Log: {student_name}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("Use this form to quickly log minor incidents and behaviours of concern.")

    student_details = get_student_details(student_name)
    
    with st.form("quick_incident_log_form", clear_on_submit=True):
        st.subheader("A. Context & Staff")
        
        # Row 1: Date, Time, Staff
        col1, col2, col3 = st.columns(3)
        with col1:
            log_date = st.date_input("Date of Incident", datetime.today())
        with col2:
            log_time = st.time_input("Time of Incident", datetime.now().time())
        with col3:
            staff_name = st.selectbox("Staff Logging Incident", get_active_staff(), index=get_active_staff().index([s['name'] for s in MOCK_STAFF if s['role'] == role][0]))
            staff_id = get_staff_id(staff_name)

        # Row 2: Location
        location = st.text_input("Location of Incident (e.g., Classroom, Oval, Hallway)")

        st.subheader("B. Behaviour and ABC Data (Lite)")

        # Row 3: Behavior, Duration, Intensity
        col4, col5, col6 = st.columns(3)
        with col4:
            behavior = st.selectbox("Primary Behavior of Concern", BEHAVIORS_FBA)
        with col5:
            duration_min = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=5)
        with col6:
            intensity = st.slider("Intensity (1-5)", 1, 5, 3, help="1=Minor disruption, 5=Crisis/Extreme")

        # Row 4: Trigger and Function (Quick Log selects primary)
        col7, col8 = st.columns(2)
        with col7:
            trigger = st.selectbox("Antecedent/Trigger (Primary)", TRIGGERS)
        with col8:
            function = st.selectbox("Hypothesised Function (Primary)", FUNCTIONS)

        # Row 5: Intervention and Outcome
        intervention = st.selectbox("Intervention/Response Used", INTERVENTION_STRATEGIES)
        
        st.markdown("---")
        st.subheader("C. Detailed Description & Outcome")
        details = st.text_area("Detailed Description of Incident (What happened?)", height=150)
        
        # Primary Outcome
        primary_outcome = st.selectbox("Primary Outcome/Resolution", 
                                      ['Resolved', 'Time Out/Cool Down', 'Sent Home', 
                                       'Left Area', 'Assault (Peer/Staff)', 'Property Damage', 
                                       'Other (See details)'])

        # Window of Tolerance (WOT) Check (Quick log uses simplified version)
        wot_level = st.selectbox("Student's Arousal Level (WOT)", WINDOW_OF_TOLERANCE_OPTIONS, 
                                 index=0, help="Estimate the student's arousal state during the incident.")

        st.markdown("---")
        
        submitted = st.form_submit_button("Submit Quick Log")

    if submitted:
        if not details or not location:
            st.error("Please ensure the Location and Detailed Description fields are filled.")
        else:
            preliminary_data = {
                'student_id': student_details['id'],
                'student_name': student_name,
                'date': log_date.isoformat(),
                'time': log_time.isoformat(),
                'staff_id': staff_id,
                'location': location,
                'behavior': behavior,
                'duration_min': duration_min,
                'intensity': intensity,
                'trigger': trigger,
                'function': function,
                'intervention': intervention,
                'details': details,
                'primary_outcome': primary_outcome,
                'window_of_tolerance': wot_level,
                'is_abch_completed': True, # Assume basic ABCH is met by the form fields
            }
            save_log_to_db(preliminary_data, is_critical=False)
            
    if st.button("← Back to Dashboard"):
        navigate_to('staff_area', role=role)

# CRITICAL INCIDENT FORM - Full ABCH Structure
def render_critical_incident_form(role, student_name):
    """
    Renders the Critical Incident Form (Full ABCH).
    This function is now based on the isolated code provided by the user.
    """
    st.markdown(f"<h1 class='centered-header'>Critical Incident Form (Full ABCH): {student_name}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.warning("⚠️ This log requires complete data for mandatory reporting and Principal review.")

    student_details = get_student_details(student_name)

    # 1. Preliminary Details (Date, Staff, Core Incident) - Stored in session state before final save
    if 'preliminary_data' not in st.session_state:
        st.session_state.preliminary_data = {}
        st.session_state.form_step = 1 # Start at step 1

    # --- Step 1: Preliminary Details and Incident Description ---
    if st.session_state.form_step == 1:
        st.subheader("Step 1: Incident Description and Staff")
        with st.form("critical_incident_step_1", clear_on_submit=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                log_date = st.date_input("Date of Incident", datetime.today())
            with col2:
                log_time = st.time_input("Time of Incident", datetime.now().time())
            with col3:
                staff_name = st.selectbox("Staff Logging Incident", get_active_staff(), index=get_active_staff().index([s['name'] for s in MOCK_STAFF if s['role'] == role][0]))
                staff_id = get_staff_id(staff_name)

            col4, col5, col6 = st.columns(3)
            with col4:
                location = st.text_input("Location", key='critical_location')
            with col5:
                behavior = st.selectbox("Primary Behavior", BEHAVIORS_FBA, key='critical_behavior')
            with col6:
                duration_min = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=15, key='critical_duration')

            details = st.text_area("Detailed Narrative of the Incident", height=200, key='critical_details')
            
            if st.form_submit_button("Continue to Step 2 (Full ABCH)"):
                if not location or not details:
                    st.error("Location and Detailed Narrative are mandatory fields.")
                else:
                    # Store preliminary data in session state
                    st.session_state.preliminary_data = {
                        'student_id': student_details['id'],
                        'student_name': student_name,
                        'date': log_date.isoformat(),
                        'time': log_time.isoformat(),
                        'staff_id': staff_id,
                        'location': location,
                        'behavior': behavior,
                        'duration_min': duration_min,
                        'details': details,
                    }
                    st.session_state.form_step = 2
                    st.experimental_rerun()
            
            if st.button("← Back to Dashboard", key='back_step1'):
                navigate_to('staff_area', role=role)

    # --- Step 2: Full ABCH and Response/Outcomes ---
    elif st.session_state.form_step == 2:
        st.subheader("Step 2: Full ABCH Analysis & Incident Management")

        st.markdown("### A. Antecedent (What happened right before?)")
        trigger = st.multiselect("Triggers/Antecedents Present", TRIGGERS, key='critical_trigger')
        
        st.markdown("### B. Behavior (Student Arousal State)")
        st.warning("Assess the student's level of distress/arousal before, during, and after the peak.")
        col_wot_1, col_wot_2 = st.columns(2)
        with col_wot_1:
            st.session_state.wot_level = st.selectbox("Primary Arousal State (WOT)", WINDOW_OF_TOLERANCE_OPTIONS, key='wot_level', help="Critical incidents usually involve Hyperarousal.")
        with col_wot_2:
            st.multiselect("Observed Emotional State(s)", EMOTIONAL_STATES, key='critical_emotions')
            
        st.text_area("Additional Context/Environmental Factors", key='critical_context', height=100)
        
        st.markdown("### C. Consequence & Function")
        col_c_1, col_c_2 = st.columns(2)
        with col_c_1:
            st.multiselect("Hypothesised Function(s)", FUNCTIONS, key='critical_function')
        with col_c_2:
            st.selectbox("Intervention Strategy Used (Primary)", INTERVENTION_STRATEGIES, key='critical_intervention')
        
        st.text_area("Staff Response & De-escalation Sequence", key='critical_response', height=150, help="Detail the step-by-step response used by staff. Include de-escalation tools.")
        st.multiselect("De-escalation Tools Used", DE_ESCALATION_TOOLS, key='critical_de_escalation')

        st.markdown("### H. Outcomes (MANDATORY Reporting Indicators)")
        st.markdown("_Check all that apply. Checking any of these triggers mandatory Principal notification._")
        
        col_o_1, col_o_2, col_o_3 = st.columns(3)
        with col_o_1:
            st.checkbox("A. Sent Home/Family Contacted", key='o_a_send_home')
            st.checkbox("D. Property Damage/Vandalism", key='o_d_property_damage')
            st.checkbox("G. Police Call-out (SAPOL)", key='o_f_sapol_callout')

        with col_o_2:
            st.checkbox("B. Student left school grounds (Elopement)", key='o_b_left_area')
            st.checkbox("E. Staff Injury (First Aid applied)", key='o_e_staff_injury')
            st.checkbox("H. Ambulance called", key='o_r_call_out_amb')
            
        with col_o_3:
            st.checkbox("C. Assault (Physical Aggression towards Peer/Staff)", key='o_c_assault')
            st.checkbox("F. First Aid applied to student (not injury related)", key='o_j_first_aid_amb')
            
        st.markdown("---")
        
        col_nav_2_1, col_nav_2_2 = st.columns(2)
        with col_nav_2_1:
            if st.button("← Back to Step 1"):
                st.session_state.form_step = 1
                st.experimental_rerun()
        with col_nav_2_2:
            if st.button("Finalise and Submit Critical Incident Log", type='primary'):
                if not st.session_state.get('critical_response') or not st.session_state.get('critical_context'):
                    st.error("Please fill in the Context and Staff Response fields.")
                else:
                    save_log_to_db(st.session_state.preliminary_data, is_critical=True)
                    st.session_state.form_step = 1 # Reset form
                    st.session_state.preliminary_data = {}
                    st.experimental_rerun()
                    
    st.markdown("---")
    st.info("Ensure all details are accurate before submission, as this is a formal reporting requirement.")


# --- Application State and Flow Control ---

def initialize_state():
    """Initializes the session state variables for navigation and data."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'student_details' not in st.session_state:
        st.session_state.student_details = None

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

    elif st.session_state.page == 'critical_incident':
        if current_student and current_role:
             render_critical_incident_form(current_role, current_student) 
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
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
