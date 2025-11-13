import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS (TO BE REPLACED WITH DB CALLS) ---
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- FBA and Data Constants ---
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst', 'Vocalisation/Noise', 'Other']
ANTECEDENTS = ['Transition/Change in Routine', 'Demand/Instruction Given', 'Peer Interaction/Conflict', 'Preferred Item Denied/Removed', 'Unstructured Time (Play)', 'Environmental Noise/Stimuli', 'Illness/Pain', 'No Clear Antecedent', 'Other']
BEHAVIOR_FUNCTIONS = ['Attention (Peer)', 'Attention (Staff)', 'Access to Tangible/Preferred Activity', 'Escape/Avoidance (Task/Demand)', 'Escape/Avoidance (Sensory)', 'Automatic/Sensory', 'Other/Unknown']
CONSEQUENCES = ['Redirection/Prompt', 'Ignored/Withdrawn Attention', 'Time-Out/Exclusion', 'Restorative Practice', 'Loss of Privilege', 'Contact Home', 'First Aid Required', 'No Consequence Applied', 'Other']
WINDOW_OF_TOLERANCE_OPTIONS = ['Regulation: Proactive/Green Zone', 'Escalation: Amber Zone', 'Crisis: Red Zone']

# --- MOCK STUDENT DATA ---
MOCK_STUDENTS = [
    {'id': 'stu001', 'name': 'Alex Johnson', 'year': 5, 'profile': 'High-needs, Plan A', 'data': {'Verbal Refusal': 12, 'Elopement': 5, 'Aggression (Peer)': 2}},
    {'id': 'stu002', 'name': 'Ben Carter', 'year': 3, 'profile': 'Low-needs, Plan B', 'data': {'Verbal Refusal': 4, 'Outburst': 1}},
    {'id': 'stu003', 'name': 'Chloe Davis', 'year': 7, 'profile': 'Medium-needs, Plan C', 'data': {'Property Destruction': 3, 'Vocalisation/Noise': 8}},
]

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
    div[data-testid="stTextInput"] > div > textarea,
    div[data-testid="stTextArea"] > div > textarea,
    .stSelectbox div[role="listbox"],
    .stDateInput input, .stTimeInput input {
        background-color: #0F172A !important;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9 !important;
        padding: 10px;
    }

    /* Primary Buttons - Action Color */
    .stButton>button {
        background-color: #4C51BF; /* Indigo for action */
        color: #F1F5F9;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #6366F1;
    }
    
    /* Secondary/Navigation Buttons */
    .secondary-nav button {
        background-color: #334155;
        color: #94A3B8;
    }
    .secondary-nav button:hover {
        background-color: #475569;
        color: #F1F5F9;
    }

    /* Info/Success Alerts */
    div[data-testid="stAlert"] > div {
        border-radius: 12px;
        padding: 15px;
    }

    /* Metric Boxes (for Analysis Page) */
    [data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .st-emotion-cache-y32r2b { /* Metric label */
        color: #94A3B8 !important;
    }
    .st-emotion-cache-e3on0p { /* Metric value */
        color: #6366F1 !important;
        font-weight: 700;
    }
    
    /* Multi-select and checkbox styling */
    .stMultiSelect div[role="listbox"] {
        background-color: #1E293B;
    }
    .stMultiSelect div[role="button"] {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    /* Remove Streamlit footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom form styling for better visual grouping */
    .form-section {
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1E293B;
    }
    </style>
    """
, unsafe_allow_html=True)

# --- Helper Functions (Staff/Data) ---

def get_active_staff():
    """Returns a list of names of all active staff members."""
    return sorted([staff['name'] for staff in MOCK_STAFF if staff['active']])

def find_staff_role(staff_name):
    """Finds the role code based on the selected staff name."""
    for staff in MOCK_STAFF:
        if staff['name'] == staff_name:
            return staff['role']
    return 'UNKNOWN'

# --- Navigation & State Management ---

def initialize_state():
    """Initializes necessary session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing' # 'landing', 'staff_area', 'quick_log', 'student_detail'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'mock_logs' not in st.session_state:
        # Initial mock data for analysis
        st.session_state.mock_logs = pd.DataFrame([
            {'id': str(uuid.uuid4()), 'student_id': 'stu001', 'timestamp': datetime.now() - timedelta(hours=3), 'reported_by': 'Emily Jones (JP)', 'behavior': 'Verbal Refusal'},
            {'id': str(uuid.uuid4()), 'student_id': 'stu001', 'timestamp': datetime.now() - timedelta(days=1), 'reported_by': 'Daniel Lee (PY)', 'behavior': 'Elopement'},
            {'id': str(uuid.uuid4()), 'student_id': 'stu003', 'timestamp': datetime.now() - timedelta(days=2), 'reported_by': 'Sarah Chen (SY)', 'behavior': 'Property Destruction'},
            {'id': str(uuid.uuid4()), 'student_id': 'stu001', 'timestamp': datetime.now() - timedelta(days=5), 'reported_by': 'Emily Jones (JP)', 'behavior': 'Verbal Refusal'},
            {'id': str(uuid.uuid4()), 'student_id': 'stu002', 'timestamp': datetime.now() - timedelta(weeks=1), 'reported_by': 'Daniel Lee (PY)', 'behavior': 'Outburst'},
        ])

def navigate_to(page_name, **kwargs):
    """Sets the session state page for navigation."""
    st.session_state.page = page_name
    
    # Update other state variables if provided
    if 'role' in kwargs:
        st.session_state.role = kwargs['role']
    if 'student' in kwargs:
        st.session_state.student = kwargs['student']

# --- Page Renderers ---

def render_landing_page():
    """Renders the initial login/role selection page."""
    
    st.title("🌟 Behaviour Support Data Tool")
    st.subheader("Select Your Role to Access the System")
    
    staff_options = get_active_staff()
    
    with st.form("role_selection_form"):
        selected_staff = st.selectbox(
            "Select your Staff Profile:",
            options=staff_options,
            index=None,
            key='selected_staff_key'
        )
        
        submitted = st.form_submit_button("Access Staff Area")
        
        if submitted and selected_staff:
            role_code = find_staff_role(selected_staff)
            st.session_state.staff_name = selected_staff # Store name for logging
            navigate_to('staff_area', role=role_code)
            st.rerun() # Rerun to navigate
        elif submitted and not selected_staff:
            st.error("Please select a staff profile to proceed.")

    st.markdown("---")
    st.info("This application supports data-driven decision-making for student behaviour support. Your role selection determines your permissions.")

def render_student_analysis(student_id, role):
    """Renders the detailed analysis dashboard for a specific student."""
    
    student = next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)
    if not student:
        st.error("Student profile not found.")
        navigate_to('staff_area', role=role)
        return

    st.header(f"📊 Student Analysis: {student['name']} (Year {student['year']})")
    st.subheader(f"Profile: {student['profile']}")
    
    st.button("↩ Back to Staff Dashboard", on_click=navigate_to, args=('staff_area',), kwargs={'role': role})
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    # Calculate Total Incidents
    student_logs = st.session_state.mock_logs[st.session_state.mock_logs['student_id'] == student_id]
    total_incidents = len(student_logs)
    col1.metric("Total Incidents Logged", total_incidents)

    # Calculate Last Incident Date
    last_incident = student_logs['timestamp'].max()
    last_incident_str = last_incident.strftime('%Y-%m-%d') if pd.notna(last_incident) else "N/A"
    col2.metric("Last Incident Date", last_incident_str)

    # Calculate Top Behavior
    behavior_counts = student_logs['behavior'].value_counts()
    top_behavior = behavior_counts.index[0] if not behavior_counts.empty else "N/A"
    top_behavior_count = behavior_counts.iloc[0] if not behavior_counts.empty else 0
    col3.metric("Top Behavior", f"{top_behavior} ({top_behavior_count} logs)")

    st.markdown("---")

    st.subheader("Incident Trends by Behavior")
    if not student_logs.empty:
        # Group by behavior and count
        df_plot = student_logs.groupby(student_logs['timestamp'].dt.to_period('W'))['behavior'].value_counts().reset_index(name='Count')
        df_plot['Week'] = df_plot['timestamp'].astype(str)
        
        fig = px.bar(
            df_plot,
            x='Week',
            y='Count',
            color='behavior',
            title=f"Weekly Incident Count for {student['name']}",
            labels={'Week': 'Week Starting', 'Count': 'Incident Count', 'behavior': 'Behavior'},
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No incidents logged for this student yet.")
    
    st.markdown("---")
    st.subheader("Raw Log Data (Last 10 Entries)")
    st.dataframe(student_logs[['timestamp', 'reported_by', 'behavior']].sort_values('timestamp', ascending=False).head(10), use_container_width=True)

def render_quick_log(current_role, current_student):
    """
    Renders the detailed ABCH (Antecedent-Behavior-Context-How to Respond) Quick Log form.
    This form captures structured data for Functional Behaviour Assessments (FBA).
    """
    
    student = next((s for s in MOCK_STUDENTS if s['id'] == current_student), None)
    student_name = student['name'] if student else "Unknown Student"
    
    st.header(f"✍️ Quick Incident Log: {student_name}")
    st.subheader(f"Data Capture for Functional Behaviour Assessment (ABCH Log)")
    
    # Navigation Buttons
    col_nav_a, col_nav_b, col_nav_c = st.columns([1, 1, 4])
    col_nav_a.button("↩ Dashboard", on_click=navigate_to, args=('staff_area',), kwargs={'role': current_role}, key='nav_ql_dash')
    col_nav_b.button("Detailed View", on_click=navigate_to, args=('student_detail',), kwargs={'student': current_student, 'role': current_role}, key='nav_ql_detail')

    st.markdown("---")
    
    # --- FORM START ---
    
    with st.form(key='abch_quick_log_form', clear_on_submit=False):
        
        # 1. INCIDENT DETAILS (Header Section)
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 1. Incident Details (When & Who)")
        
        details_col1, details_col2, details_col3 = st.columns(3)

        # Date of Incident
        log_date = details_col1.date_input("Date of Incident", value=datetime.now().date())
        
        # Time of Incident
        log_time = details_col2.time_input("Time of Incident", value=datetime.now().time())
        
        # Staff Logged By (Pre-filled from login state)
        # Note: We use the full name stored during the landing page selection
        logged_by_name = st.session_state.get('staff_name', 'Unknown Staff')
        details_col3.text_input("Logged By", value=logged_by_name, disabled=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. ABCH/FBA DATA
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 2. ABCH Data: Antecedent, Behavior, Consequence, & Function")
        
        fba_col1, fba_col2 = st.columns(2)

        # Antecedent (What happened immediately BEFORE the behavior?)
        antecedent = fba_col1.selectbox(
            "Antecedent (Trigger)",
            options=ANTECEDENTS,
            index=ANTECEDENTS.index('Demand/Instruction Given') if 'Demand/Instruction Given' in ANTECEDENTS else 0,
            help="Select the event that immediately preceded the behavior."
        )

        # Behavior (The Observable Action)
        behavior = fba_col2.selectbox(
            "Observed Behavior (The Action)",
            options=BEHAVIORS_FBA,
            index=BEHAVIORS_FBA.index('Verbal Refusal') if 'Verbal Refusal' in BEHAVIORS_FBA else 0,
            help="Select the specific behavior observed."
        )

        # Consequences (What happened immediately AFTER the behavior?)
        consequences = fba_col1.multiselect(
            "Consequences Applied (What followed the behavior?)",
            options=CONSEQUENCES,
            default=['Redirection/Prompt'],
            help="Select all consequences that followed the behavior."
        )

        # Hypothesized Function (Why did the behavior occur?)
        function = fba_col2.selectbox(
            "Hypothesized Function (Why?)",
            options=BEHAVIOR_FUNCTIONS,
            index=BEHAVIOR_FUNCTIONS.index('Escape/Avoidance (Task/Demand)') if 'Escape/Avoidance (Task/Demand)' in BEHAVIOR_FUNCTIONS else 0,
            help="What purpose did the behavior serve for the student?"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. CONTEXT & ESCALATION
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 3. Context & Escalation Details")
        
        # Staff Who Attended
        attending_staff = st.multiselect(
            "Other Staff Who Attended/Supported:",
            options=get_active_staff(),
            default=[],
            help="Select any other staff who were involved in managing the incident."
        )

        # Window of Tolerance (WOT)
        wot_level = st.radio(
            "Student's Window of Tolerance (WOT) Level at the PEAK of the incident:",
            options=WINDOW_OF_TOLERANCE_OPTIONS,
            index=WINDOW_OF_TOLERANCE_OPTIONS.index('Escalation: Amber Zone'),
            horizontal=True,
            help="Regulation (Green), Escalation (Amber), or Crisis (Red)."
        )

        # Contextual Notes
        context_notes = st.text_area(
            "Detailed Contextual Notes (e.g., location, preceding events, student mood):",
            placeholder="Describe the environment, people present, and student's initial state leading up to the incident.",
            height=150
        )
        
        # How Staff Responded (Intervention)
        response_plan = st.text_area(
            "How Staff Responded (Specific Intervention/Script Used):",
            placeholder="Describe your verbal and non-verbal responses/interventions.",
            height=100
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. OUTCOMES (Checkbox Grid)
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 4. Outcomes and Actions Taken")
        
        st.markdown("**Check all immediate outcomes that resulted from the incident:**")
        
        out_col1, out_col2, out_col3 = st.columns(3)
        
        # Column 1: Major Safety/Exclusion
        out_col1.checkbox("Sent Home", key='o_a_send_home')
        out_col1.checkbox("Left Designated Area (Eloped)", key='o_b_left_area')
        out_col1.checkbox("Physical Assault", key='o_c_assault')

        # Column 2: Damage/Injury
        out_col2.checkbox("Property Damage", key='o_d_property_damage')
        out_col2.checkbox("Staff Injury", key='o_e_staff_injury')
        out_col2.checkbox("Required First Aid", key='o_g_first_aid_self')
        
        # Column 3: External/Formal
        out_col3.checkbox("SAPOL Callout", key='o_f_sapol_callout')
        out_col3.checkbox("Ambulance Callout", key='o_r_call_out_amb')
        out_col3.checkbox("Formal Suspension Issued", key='o_h_formal_susp')


        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit Button
        submitted = st.form_submit_button("💾 Save Detailed Incident Log")
        
        if submitted:
            # Compile the full log entry
            log_entry = {
                'id': str(uuid.uuid4()),
                'student_id': current_student,
                'student_name': student_name,
                'timestamp': datetime.combine(log_date, log_time),
                'reported_by': logged_by_name,
                'role': find_staff_role(logged_by_name),
                
                # FBA Data
                'antecedent': antecedent,
                'behavior': behavior,
                'consequences': consequences, # list
                'function': function,
                
                # Context & Response
                'attending_staff': attending_staff, # list
                'window_of_tolerance': wot_level,
                'context_notes': context_notes,
                'how_to_respond': response_plan,
                
                # Outcomes
                'outcome_send_home': st.session_state.get('o_a_send_home', False),
                'outcome_leave_area': st.session_state.get('o_b_left_area', False),
                'outcome_assault': st.session_state.get('o_c_assault', False),
                'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
                'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
                'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
                'outcome_first_aid_self': st.session_state.get('o_g_first_aid_self', False),
                'outcome_ambulance_callout': st.session_state.get('o_r_call_out_amb', False),
                'outcome_formal_suspension': st.session_state.get('o_h_formal_susp', False),
                
                # Metadata
                'is_abch_completed': True,
                'log_type': 'Detailed ABCH Log'
            }
            
            # Add the new log to the mock data store (In a real app, this is where you'd save to Firestore/DB)
            st.session_state.mock_logs = pd.concat([st.session_state.mock_logs, pd.Series(log_entry).to_frame().T], ignore_index=True)
            
            # Display Success message and clean up
            st.success(f"Log for {student_name} saved successfully! ID: {log_entry['id']}")
            
            # Clear checkboxes state for next submission
            for key in ['o_a_send_home', 'o_b_left_area', 'o_c_assault', 'o_d_property_damage', 'o_e_staff_injury', 'o_f_sapol_callout', 'o_g_first_aid_self', 'o_r_call_out_amb', 'o_h_formal_susp']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Rerun the form to clear all input fields (due to clear_on_submit=False in form definition)
            # A full rerun is sometimes necessary with complex state management
            # To avoid rerunning the whole app, we use a custom method. For simplicity here, we'll allow the success message to stay.

def render_staff_area(current_role):
    """Renders the main dashboard for staff, showing students and quick actions."""
    
    st.title(f"👋 Welcome, {current_role} Staff")
    st.subheader("Select a Student or Initiate a Quick Log")
    
    # 1. Quick Log Button (Top Priority Action)
    st.markdown("---")
    st.markdown("### Quick Log Action")
    
    # Select student for quick log
    student_names = [s['name'] for s in MOCK_STUDENTS]
    selected_student_name = st.selectbox(
        "Select Student for **Quick Incident Log**:",
        options=[''] + student_names,
        index=0,
        key='ql_student_select'
    )
    
    if st.button("Start Quick Log", disabled=not selected_student_name):
        student_id = next(s['id'] for s in MOCK_STUDENTS if s['name'] == selected_student_name)
        navigate_to('quick_log', role=current_role, student=student_id)
        st.rerun()

    # 2. Student List/Analysis Access
    st.markdown("---")
    st.markdown("### Student Management & Analysis")
    
    # Display students in a list/table for easy navigation
    student_data = []
    for s in MOCK_STUDENTS:
        # Get count of incidents for this student
        count = len(st.session_state.mock_logs[st.session_state.mock_logs['student_id'] == s['id']])
        student_data.append({
            'Name': s['name'],
            'Year': s['year'],
            'Profile': s['profile'],
            'Incidents Logged': count,
            'Action': f"Analyze|{s['id']}" # Custom action string for button logic
        })
        
    df = pd.DataFrame(student_data)
    
    # Display the table
    st.dataframe(
        df[['Name', 'Year', 'Profile', 'Incidents Logged']], 
        use_container_width=True,
        hide_index=True
    )

    # Use a separate row for action buttons tied to the list
    st.markdown("---")
    st.subheader("Access Detailed Analysis")

    analysis_col1, analysis_col2 = st.columns([2, 1])

    student_for_analysis_name = analysis_col1.selectbox(
        "Select a student to view their detailed data analysis dashboard:",
        options=[''] + df['Name'].tolist(),
        index=0,
        key='analysis_student_select'
    )

    if analysis_col2.button("View Analysis", disabled=not student_for_analysis_name):
        student_id = next(s['id'] for s in MOCK_STUDENTS if s['name'] == student_for_analysis_name)
        navigate_to('student_detail', role=current_role, student=student_id)
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
            st.warning("Please log in by selecting your role.")
            navigate_to('landing')
            
if __name__ == '__main__':
    main()
