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
    div[data-testid="stSelectbox"] div.st-emotion-cache-18rdzq9 {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }

    /* Slider styling for Severity Gauge */
    /* Slider Track */
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
    }
    div[data-testid="stSlider"] div[data-testid="stHorizontalBlock"] {
        background: #475569;
    }
    /* Slider highlight (needs custom coloring based on value) - will use Streamlit's default color for fill */

    /* Buttons */
    .stButton>button {
        background-color: #0F172A;
        color: #93C5FD;
        border: 1px solid #1D4ED8;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: #FFFFFF;
    }
    /* Custom style for the CRITICAL button */
    .st-emotion-cache-1cpx6a9 button { /* Targetting button in the column container */
        background-color: #B91C1C !important;
        border-color: #EF4444 !important;
        color: #FFFFFF !important;
        font-weight: bold;
    }
    .st-emotion-cache-1cpx6a9 button:hover {
        background-color: #DC2626 !important;
    }
    
    /* Expander/Containers */
    .st-emotion-cache-1ky9p07 {
        border: 1px solid #334155;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FBA and Data Constants ---

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 
    'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)',
    'Running Away from Area', 'Disruptive Noise/Sound', 'Inappropriate Language'
]

# Refined Terminology for Student State (Replaces 'Arousal')
STUDENT_STATES = [
    'Calm/Focused', 'Rumbling/Agitated', 'Dissociation/Withdrawn', 'Rage/Panic', 'Meltdown/Shut-down'
]

# Refined Terminology for Support Type (Replaces 'Intervention')
SUPPORT_TYPES = [
    'Re-Engagement/Instructional', 'Emotional/Regulation', 'Physical/Safety', 'No Support Required'
]

ANTECEDENTS = [
    'Transition to Non-Preferred Activity', 'Instruction/Demand Given', 'Change in Routine',
    'Peer Conflict/Attention', 'Sensory Overload', 'Physical Discomfort (Hunger, Fatigue)',
    'Task Difficulty/Escape', 'Attention Seeking (Staff)'
]

OUTCOMES_NON_CRITICAL = [
    'Task Completion', 'Student Self-Regulated', 'Staff De-escalation Success',
    'Peer Conflict Resolved', 'Moved to Safe Space', 'No Further Action'
]

# --- Critical Incident Outcomes (Based on intended outcomes.docx) ---
CRITICAL_OUTCOMES = {
    'safety': {
        'o_c_assault': 'Assault / Aggression towards Staff or Peer',
        'o_d_property_damage': 'Significant Property Damage',
        'o_e_staff_injury': 'ED155: Staff Injury (requires report)',
        'o_j_student_injury': 'ED155: Student Injury (requires report)',
        'o_b_leave_area': 'Student Leaving supervised area / school grounds',
        'o_g_stealing': 'Stealing',
        'o_k_sexual_behaviour': 'Sexualised behaviour',
    },
    'emergency_response': {
        'o_f_sapol_callout': 'Emergency Services: SAPOL Call Out',
        'o_r_ambulance_callout': 'Emergency Services: SA Ambulance Call Out',
        'o_s_taken_to_hospital': 'Taken to Hospital by Staff/Ambulance',
    }
}

CRITICAL_ADMIN_FOLLOW_UP = {
    'admin_manager_notified': 'Line Manager Notified of Critical Incident',
    'admin_parent_notified': 'Parent / Caregiver Notified of Critical Incident',
    'admin_copy_filed': 'Copy of Critical Incident in student file',
    'admin_restorative_session': 'Restorative Session Scheduled',
    'admin_re_entry_tac': 'Re-Entry/TAC Meeting Scheduled',
    'admin_case_review': 'Case Review Scheduled',
    'admin_safety_plan_review': 'Safety and Risk Plan to be Developed/Reviewed',
}


# --- Mock Data and Utility Functions ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

def get_active_staff():
    return [s for s in MOCK_STAFF if s['active']]

# ... (rest of utility functions like navigate_to, initialize_state, save_log_entry remain the same)
def navigate_to(page, **kwargs):
    """Sets the application page and updates necessary context in session state."""
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun()

def initialize_state():
    """Initializes session state variables if they do not exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'log_data' not in st.session_state:
        # Initial mock data for demonstration
        st.session_state.log_data = pd.DataFrame(columns=[
            'log_id', 'timestamp', 'student_id', 'staff_id', 'staff_name',
            'behavior', 'antecedent', 'severity', 'duration_min',
            'support_provided', 'outcome', 'notes'
        ])
    if 'student' not in st.session_state:
        st.session_state.student = 'Izack M' # Default student
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'critical_data' not in st.session_state:
        st.session_state.critical_data = None


def save_log_entry(data):
    """Saves a log entry to the mock DataFrame and returns to the staff area."""
    # Convert data dictionary to a DataFrame row
    new_entry_df = pd.DataFrame([data])
    
    # Prepend the new entry to the existing DataFrame
    st.session_state.log_data = pd.concat([new_entry_df, st.session_state.log_data], ignore_index=True)
    
    # Clear critical data if it exists
    if 'critical_data' in st.session_state:
        del st.session_state['critical_data']
    
    st.success("Incident Logged Successfully!")
    st.balloons()
    
    # Navigate back to the staff area to see the data update
    navigate_to('staff_area', role=st.session_state.get('role'))


# --- Page Rendering Functions ---

# ... (render_landing_page, render_staff_area, render_student_analysis remain the same)
def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.subheader("Welcome to the Student Behavior Data Logging System")

    st.markdown("---")

    st.info("Select your role to access the appropriate dashboard and logging tools.")

    col1, col2, col3 = st.columns(3)

    if col1.button("Staff Member (Teacher/JP/PY/SY)"):
        navigate_to('staff_area', role='STAFF')
    if col2.button("Admin / Leadership (ADM)"):
        navigate_to('staff_area', role='ADM')
    
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")

def render_staff_area(current_role):
    """Renders the dashboard for staff members and administrators."""
    st.title(f"Staff Dashboard ({current_role})")
    
    # Mock Student Selector
    # In a real app, this list would come from a database query
    STUDENTS = ['Izack M', 'Chloe T', 'Liam R', 'New Student (Unlisted)']
    
    st.sidebar.selectbox(
        "Select Student for Context:", STUDENTS,
        key='student_selector',
        index=STUDENTS.index(st.session_state.student) if st.session_state.student in STUDENTS else 0,
        on_change=lambda: st.session_state.update(student=st.session_state.student_selector)
    )
    
    current_student = st.session_state.student
    
    st.markdown(f"## Context: **{current_student}**")
    
    col_log, col_analyze = st.columns(2)
    
    with col_log:
        st.header("Quick Log Incident")
        if st.button(f"Start Quick Log for {current_student}", key='start_log'):
            navigate_to('quick_log', student=current_student)
            
    with col_analyze:
        st.header("Student Analysis")
        if st.button(f"View Detailed Analysis for {current_student}", key='view_analysis'):
            navigate_to('student_detail', student=current_student)

    st.markdown("---")
    st.subheader("Recent Incidents Logged")
    
    if not st.session_state.log_data.empty:
        # Display the most recent 10 logs
        st.dataframe(
            st.session_state.log_data.head(10).sort_values(by='timestamp', ascending=False),
            use_container_width=True,
            column_order=['timestamp', 'student_id', 'behavior', 'antecedent', 'severity', 'duration_min', 'outcome']
        )
    else:
        st.info("No incidents have been logged yet.")

def render_student_analysis(current_student, current_role):
    """Renders detailed FBA data analysis for a selected student."""
    st.title(f"Detailed Analysis: {current_student}")
    
    if st.button("← Back to Staff Dashboard"):
        navigate_to('staff_area', role=current_role)
    
    st.markdown("---")
    
    df = st.session_state.log_data
    student_logs = df[df['student_id'] == current_student]

    if student_logs.empty:
        st.warning(f"No log data found for {current_student}. Please log an incident first.")
        return

    st.subheader("Incident Summary Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", student_logs.shape[0])
    col2.metric("Avg Severity (1-5)", f"{student_logs['severity'].mean():.1f}")
    col3.metric("Total Duration (min)", f"{student_logs['duration_min'].sum():.0f}")

    st.markdown("---")

    col_charts, col_data = st.columns(2)

    with col_charts:
        st.subheader("Behavior Frequencies")
        behavior_counts = student_logs['behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig_b = px.bar(behavior_counts, x='Behavior', y='Count', 
                       title='Most Common Behaviors', color='Count',
                       color_continuous_scale=px.colors.sequential.Sunsetdark)
        st.plotly_chart(fig_b, use_container_width=True)

        st.subheader("Antecedent-Behavior Correlation")
        ab_pivot = student_logs.groupby(['antecedent', 'behavior']).size().reset_index(name='Count')
        fig_ab = px.treemap(ab_pivot, path=['antecedent', 'behavior'], values='Count',
                            title='Antecedent-Behavior Relationship Map')
        st.plotly_chart(fig_ab, use_container_width=True)

    with col_data:
        st.subheader("Severity Over Time")
        # Ensure timestamp is datetime and set as index for rolling average
        student_logs['timestamp'] = pd.to_datetime(student_logs['timestamp'])
        time_series = student_logs.set_index('timestamp')['severity'].resample('D').mean().fillna(0)
        
        # Calculate a 7-day rolling average
        rolling_avg = time_series.rolling(window=7, min_periods=1).mean()

        fig_s = px.line(rolling_avg, y='severity', title='7-Day Rolling Average Severity',
                        labels={'severity': 'Average Severity', 'timestamp': 'Date'},
                        color_discrete_sequence=['#4C78A8'])
        st.plotly_chart(fig_s, use_container_width=True)
        
        st.subheader("Support Effectiveness")
        # Outcome success proxy: assuming 'Student Self-Regulated' or 'Staff De-escalation Success' are positive
        # This is a very rough mock and needs better data structure in a real app
        student_logs['Success'] = student_logs['outcome'].apply(lambda x: 1 if any(o in str(x) for o in ['Self-Regulated', 'De-escalation Success']) else 0)
        support_success = student_logs.groupby('support_provided')['Success'].mean().reset_index()
        support_success.columns = ['Support Type', 'Success Rate']
        
        fig_support = px.bar(support_success, x='Support Type', y='Success Rate', 
                             title='Success Rate by Support Type', 
                             color='Success Rate',
                             color_continuous_scale=px.colors.sequential.Plotly3)
        st.plotly_chart(fig_support, use_container_width=True)
        
    st.markdown("---")
    st.subheader("Raw Data Table (All Logs)")
    st.dataframe(student_logs.sort_values(by='timestamp', ascending=False), use_container_width=True)


def render_quick_log(current_role, current_student):
    """Renders the quick log form (ABCH style) with conditional navigation."""
    st.title(f"Quick Incident Log: {current_student}")
    st.caption("Complete the A-B-C-H steps quickly. Severity 3+ will redirect to the Critical Incident Form.")
    
    if st.button("← Back to Dashboard"):
        navigate_to('staff_area', role=current_role)
    
    st.markdown("---")
    
    staff_options = [s['name'] for s in get_active_staff()]
    staff_map = {s['name']: s['id'] for s in get_active_staff()}

    # Check for existing preliminary data (in case of a back button press)
    preliminary_data = st.session_state.critical_data if st.session_state.critical_data else {}

    # --- A: Antecedent (What happened right before?) ---
    st.subheader("1. Antecedent (A)")
    antecedent = st.selectbox(
        "Immediate Trigger:", ANTECEDENTS,
        index=ANTECEDENTS.index(preliminary_data.get('antecedent', ANTECEDENTS[0])),
        key='quick_log_antecedent'
    )

    # --- B: Behavior (What did the student do?) ---
    st.subheader("2. Behavior (B)")
    col_b1, col_b2 = st.columns([3, 1])
    
    with col_b1:
        behavior = st.selectbox(
            "Target Behavior Observed:", BEHAVIORS_FBA,
            index=BEHAVIORS_FBA.index(preliminary_data.get('behavior', BEHAVIORS_FBA[0])),
            key='quick_log_behavior'
        )
    with col_b2:
        duration_min = st.number_input(
            "Duration (mins):", min_value=1, max_value=120, value=preliminary_data.get('duration_min', 5),
            key='quick_log_duration'
        )

    # --- C: Consequence / Context (How was the student feeling & how did staff respond?) ---
    st.subheader("3. Consequence & Context (C)")
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        student_state = st.selectbox(
            "Student State (Pre-escalation/Peak):", STUDENT_STATES,
            index=STUDENT_STATES.index(preliminary_data.get('student_state', STUDENT_STATES[0])),
            key='quick_log_state'
        )
        
    with col_c2:
        support_provided = st.selectbox(
            "Support Provided:", SUPPORT_TYPES,
            index=SUPPORT_TYPES.index(preliminary_data.get('support_provided', SUPPORT_TYPES[0])),
            key='quick_log_support'
        )

    with col_c3:
        # Interactive Severity Slider/Gauge (0 to 5)
        severity = st.slider(
            "Severity / Impact (1=Low, 5=Extreme)", 
            min_value=1, max_value=5, step=1, 
            value=preliminary_data.get('severity', 1),
            key='quick_log_severity'
        )
        # Display the severity visually
        severity_color = {1: 'blue', 2: 'green', 3: 'orange', 4: 'red', 5: 'darkred'}.get(severity, 'gray')
        st.markdown(f"<p style='color:{severity_color}; font-weight:bold;'>Current Severity: {severity}</p>", unsafe_allow_html=True)


    # --- CONDITIONAL FLOW BASED ON SEVERITY ---
    
    if severity >= 3:
        # CRITICAL INCIDENT FLOW (Severity 3, 4, or 5)
        st.markdown("---")
        st.error(f"**CRITICAL INCIDENT DETECTED (Severity {severity})**")
        st.warning("The severity level indicates a high-risk situation. You must complete the **Critical Incident Form**.")
        
        # Save preliminary data to session state for the next page to retrieve
        st.session_state.critical_data = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'student_id': current_student,
            'behavior': behavior,
            'antecedent': antecedent,
            'severity': severity,
            'duration_min': duration_min,
            'student_state': student_state,
            'support_provided': support_provided,
            # Placeholder for staff selection, will be mandatory on critical form
            'staff_id': 'unknown',
            'staff_name': 'Unknown Staff'
        }
        
        if st.button("Proceed to Critical Incident Form (Mandatory)", type='primary'):
            navigate_to('critical_incident_form', student=current_student, role=current_role)
        
    else:
        # NON-CRITICAL INCIDENT FLOW (Severity 1 or 2)
        st.markdown("---")
        st.subheader("4. Outcomes & Follow-up (H) - Non-Critical")

        # Hypothesized function / goal (simple mock based on antecedent/behavior)
        hypothesis = f"Hypothesis: Student was attempting to **{antecedent.split(' ')[0].lower()}** by engaging in **{behavior.lower()}**."
        st.info(hypothesis)

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            outcome = st.selectbox("Primary Outcome:", OUTCOMES_NON_CRITICAL, key='quick_log_outcome')

        with col_h2:
            staff_name = st.selectbox("Staff Logging Incident:", staff_options, key='quick_log_staff_name')
            staff_id = staff_map.get(staff_name, 'unknown')
        
        notes = st.text_area("Additional Notes/Context (Optional):", key='quick_log_notes')

        if st.button("Submit Non-Critical Quick Log", type='primary'):
            log_data = {
                'log_id': str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'student_id': current_student,
                'staff_id': staff_id,
                'staff_name': staff_name,
                'behavior': behavior,
                'antecedent': antecedent,
                'severity': severity,
                'duration_min': duration_min,
                'support_provided': support_provided,
                'outcome': outcome,
                'notes': notes,
                'student_state': student_state,
            }
            save_log_entry(log_data)


def render_critical_incident_form(current_role, current_student):
    """Renders the detailed Critical Incident Form for severity 3+ incidents."""
    st.title(f"Critical Incident Form: {current_student}")
    st.caption("Severity Level 3 or higher requires mandatory completion of this form.")
    
    preliminary_data = st.session_state.get('critical_data')

    if not preliminary_data:
        st.error("No preliminary incident data found. Please start a Quick Log first.")
        if st.button("Go to Quick Log"):
            navigate_to('quick_log', student=current_student, role=current_role)
        return

    # Display preliminary data captured in the quick log
    st.markdown("---")
    st.subheader("1. Preliminary Incident Data (From Quick Log)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Antecedent", preliminary_data.get('antecedent'))
    col2.metric("Behavior", preliminary_data.get('behavior'))
    col3.metric("Severity", preliminary_data.get('severity'), delta="CRITICAL", delta_color='inverse')
    col4.metric("Duration (min)", preliminary_data.get('duration_min'))
    st.info(f"Student State: **{preliminary_data.get('student_state')}** | Support Provided: **{preliminary_data.get('support_provided')}**")
    st.markdown("---")
    
    # --- Form Start ---
    with st.form("critical_incident_details", clear_on_submit=True):
        st.subheader("2. Detailed Narrative & Context")

        incident_context = st.text_area(
            "Full Description of Context (What was happening in the environment?):",
            height=150,
            required=True,
            key='ci_context'
        )

        de_escalation = st.text_area(
            "Staff De-escalation Steps Taken (Specific actions and when they occurred):",
            height=150,
            required=True,
            key='ci_de_escalation'
        )

        col_staff, col_notes = st.columns(2)
        with col_staff:
            staff_options = [s['name'] for s in get_active_staff()]
            staff_map = {s['name']: s['id'] for s in get_active_staff()}
            
            # Staff logging the incident (required)
            logger_name = st.selectbox(
                "Staff Logging Incident:", staff_options, 
                index=staff_options.index(preliminary_data.get('staff_name', staff_options[0])) if preliminary_data.get('staff_name') in staff_options else 0,
                required=True,
                key='ci_logger_name'
            )
            
            # Other staff involved (optional, multi-select)
            other_staff = st.multiselect(
                "Other Staff Involved (Directly or Witnessing):", 
                [name for name in staff_options if name != logger_name],
                key='ci_other_staff'
            )

        with col_notes:
             witness_details = st.text_area(
                "Witnesses (Student or External) and Contact Details:",
                height=150,
                key='ci_witnesses'
            )

        st.markdown("---")
        st.subheader("3. Critical Outcomes & Emergency Response")
        
        st.warning("Check ALL applicable outcomes. These trigger further administrative review.")
        
        col_safety, col_emergency = st.columns(2)

        with col_safety:
            st.markdown("**Safety and Injury Outcomes**")
            safety_outcomes = {}
            for key, label in CRITICAL_OUTCOMES['safety'].items():
                safety_outcomes[key] = st.checkbox(label, key=f'ci_out_{key}')

        with col_emergency:
            st.markdown("**Emergency and Property Outcomes**")
            emergency_outcomes = {}
            for key, label in CRITICAL_OUTCOMES['emergency_response'].items():
                emergency_outcomes[key] = st.checkbox(label, key=f'ci_out_{key}')
                
            report_number = st.text_input("SAPOL / Emergency Report Number (if applicable):", key='ci_report_num')
            
            
        st.markdown("---")
        st.subheader("4. Administrative & Follow-up Actions")
        
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            st.markdown("**Mandatory Notifications**")
            admin_notified_lm = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_manager_notified'], key='ci_admin_lm')
            admin_notified_parent = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_parent_notified'], key='ci_admin_parent')
            admin_copy = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_copy_filed'], key='ci_admin_copy')

        with col_admin2:
            st.markdown("**Required Follow-up**")
            follow_up_restorative = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_restorative_session'], key='ci_follow_restorative')
            follow_up_reentry = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_re_entry_tac'], key='ci_follow_reentry')
            follow_up_case = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_case_review'], key='ci_follow_case')
            follow_up_plan = st.checkbox(CRITICAL_ADMIN_FOLLOW_UP['admin_safety_plan_review'], key='ci_follow_plan')
            
        final_outcome_summary = st.text_area(
            "Final Outcome Summary / Next Steps:",
            height=100,
            key='ci_final_outcome',
            placeholder="e.g., Student sent home. Parent contacted. TAC meeting scheduled for tomorrow."
        )


        submitted = st.form_submit_button("Submit Critical Incident Report", type='primary')

        if submitted:
            # Check for minimum required fields for a critical report
            if not incident_context or not de_escalation or not final_outcome_summary:
                st.error("Please complete the detailed narrative fields (Context, De-escalation, and Final Outcome Summary) before submitting.")
            elif not admin_notified_lm or not admin_notified_parent:
                st.error("Mandatory: Please confirm Line Manager and Parent/Caregiver notification.")
            else:
                # Combine preliminary and critical data
                final_critical_log = preliminary_data.copy()
                final_critical_log.update({
                    'log_type': 'CRITICAL',
                    'staff_id': staff_map.get(logger_name),
                    'staff_name': logger_name,
                    'other_staff_involved': other_staff,
                    'witness_details': witness_details,
                    'incident_context': incident_context,
                    'de_escalation_steps': de_escalation,
                    'outcome_summary': final_outcome_summary,
                    'report_number': report_number,
                    
                    # Merge all checkbox outcomes
                    'critical_outcomes': {**safety_outcomes, **emergency_outcomes},
                    'admin_follow_up': {
                        'lm_notified': admin_notified_lm,
                        'parent_notified': admin_notified_parent,
                        'copy_filed': admin_copy,
                        'restorative_session': follow_up_restorative,
                        're_entry_tac': follow_up_reentry,
                        'case_review': follow_up_case,
                        'safety_plan_review': follow_up_plan,
                    }
                })
                
                # In a real application, you would save final_critical_log to a separate
                # database table, often with email notification triggers.
                # For this mock, we'll save a condensed version to the main log_data table.
                condensed_log = {
                    'log_id': final_critical_log['log_id'],
                    'timestamp': final_critical_log['timestamp'],
                    'student_id': final_critical_log['student_id'],
                    'staff_id': final_critical_log['staff_id'],
                    'staff_name': final_critical_log['staff_name'],
                    'behavior': final_critical_log['behavior'],
                    'antecedent': final_critical_log['antecedent'],
                    'severity': final_critical_log['severity'],
                    'duration_min': final_critical_log['duration_min'],
                    'support_provided': final_critical_log['support_provided'],
                    'outcome': f"CRITICAL INCIDENT: {final_critical_log['outcome_summary']}",
                    'notes': final_critical_log['incident_context']
                }
                
                save_log_entry(condensed_log)
                # Success message and navigation handled by save_log_entry


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
            st.error("Critical Incident context missing. Returning to dashboard.")
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

if __name__ == "__main__":
    main()
