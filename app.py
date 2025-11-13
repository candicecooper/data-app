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
    .stSelectbox div[role="listbox"],
    .stDateInput input, .stTimeInput input {
        background-color: #0F172A !important;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9 !important;
        padding: 10px;
    }

    /* Primary Button Styling (Used for role selection and submission) */
    .stButton>button {
        background-color: #3B82F6; /* Blue 500 */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 20px;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #2563EB; /* Blue 600 */
    }
    
    /* Headers and Dividers */
    .stHorizontalSeparator { border-top: 2px solid #334155; }
    
    /* Custom form styling for better visual grouping */
    .form-section {
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1E293B;
    }

    /* Metric/Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3B82F6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MOCK DATA AND UTILITY FUNCTIONS (RESTORED ORIGINAL STRUCTURE) ---

# Detailed Constants for the ABCH Form (FBA data)
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst', 'Vocalisation/Noise', 'Other']
ANTECEDENTS = ['Transition/Change in Routine', 'Demand/Instruction Given', 'Peer Interaction/Conflict', 'Preferred Item Denied/Removed', 'Unstructured Time (Play)', 'Environmental Noise/Stimuli', 'Illness/Pain', 'No Clear Antecedent', 'Other']
BEHAVIOR_FUNCTIONS = ['Attention (Peer)', 'Attention (Staff)', 'Access to Tangible/Preferred Activity', 'Escape/Avoidance (Task/Demand)', 'Escape/Avoidance (Sensory)', 'Automatic/Sensory', 'Other/Unknown']
CONSEQUENCES = ['Redirection/Prompt', 'Ignored/Withdrawn Attention', 'Time-Out/Exclusion', 'Restorative Practice', 'Loss of Privilege', 'Contact Home', 'First Aid Required', 'No Consequence Applied', 'Other']
WINDOW_OF_TOLERANCE_OPTIONS = ['Regulation: Proactive/Green Zone', 'Escalation: Amber Zone', 'Crisis: Red Zone']
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True},
]

# Student Data used for Dashboard filtering
MOCK_STUDENTS = {
    'S001': {'name': 'Liam O’Connell', 'program': 'JP', 'risk': 'High', 'fba_status': 'Complete'},
    'S002': {'name': 'Olivia Chen', 'program': 'PY', 'risk': 'Medium', 'fba_status': 'In Progress'},
    'S003': {'name': 'Noah Smith', 'program': 'SY', 'risk': 'Low', 'fba_status': 'N/A'},
    'S004': {'name': 'Ava Wilson', 'program': 'JP', 'risk': 'High', 'fba_status': 'Complete'},
    'S005': {'name': 'Elijah Brown', 'program': 'PY', 'risk': 'Medium', 'fba_status': 'N/A'},
    'S006': {'name': 'Sophia Davis', 'program': 'SY', 'risk': 'Low', 'fba_status': 'Complete'},
}

# Generate mock data for the analysis (more robust history)
def generate_mock_logs(student_id):
    """Generates a DataFrame of mock incident logs for a student."""
    logs = []
    
    # Define a set of possible ABC fields for context
    locations = ['Classroom', 'Playground', 'Library', 'Canteen', 'Oval']
    
    # Generate 50-100 entries spread over the last year
    num_entries = random.randint(50, 100)
    
    for _ in range(num_entries):
        incident_date = datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(1, 24), minutes=random.randint(1, 60))
        
        behavior = random.choice(BEHAVIORS_FBA)
        function = random.choice(BEHAVIOR_FUNCTIONS)
        
        logs.append({
            'log_id': str(uuid.uuid4())[:8],
            'student_id': student_id,
            'date': incident_date.date(),
            'time': incident_date.strftime('%H:%M'),
            'location': random.choice(locations),
            'antecedent': random.choice(ANTECEDENTS),
            'behavior': behavior,
            'duration_min': random.uniform(1, 15),
            'severity': random.choice(['Low', 'Medium', 'High']),
            'consequence': random.choice(CONSEQUENCES),
            'hypothesized_function': function,
            'logged_by': random.choice([s['name'] for s in MOCK_STAFF]),
        })

    df = pd.DataFrame(logs)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values(by='date', ascending=False).reset_index(drop=True)

# Helper function to get students for a specific program area
def get_students_for_area(role):
    """Filters mock students based on staff role/program area."""
    program_code = role.split('/')[0] if '/' in role else role
    
    # SSO/TRT and ADM see all students
    if role in ['SSO/TRT', 'ADM']:
        return list(MOCK_STUDENTS.items())
        
    return [(k, v) for k, v in MOCK_STUDENTS.items() if v['program'] == program_code]

def get_active_staff_names():
    """Returns a list of names of all active staff members."""
    return sorted([staff['name'] for staff in MOCK_STAFF if staff['active']])

def find_staff_name_by_role(role_code):
    """Finds a representative staff name for a given role code."""
    for staff in MOCK_STAFF:
        if staff['role'] == role_code:
            return staff['name']
    return 'Unknown Staff'

def find_staff_role(staff_name):
    """Finds the role code based on the selected staff name."""
    for staff in MOCK_STAFF:
        if staff['name'] == staff_name:
            return staff['role']
    return 'UNKNOWN'

# --- State Management and Navigation ---

def initialize_state():
    """Initializes necessary session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'logs' not in st.session_state:
        # Generate and store all mock logs once
        all_logs = {}
        for student_id in MOCK_STUDENTS.keys():
            all_logs[student_id] = generate_mock_logs(student_id)
        st.session_state.logs = all_logs
    if 'quick_log_data' not in st.session_state:
        st.session_state.quick_log_data = {}

def navigate_to(page, role=None, student=None):
    """Sets session state to navigate to a new page."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
        st.session_state.staff_name = find_staff_name_by_role(role) # Set staff name based on role
    if student:
        st.session_state.student = student
    st.rerun()

# --- Analysis Functions (Data Viz) ---

def plot_incident_rate(df):
    """Plots the weekly incident rate over time."""
    df_weekly = df.set_index('date').resample('W-MON').size().reset_index(name='incident_count')
    fig = px.line(
        df_weekly, 
        x='date', 
        y='incident_count', 
        title='Weekly Incident Rate Over Time',
        template='plotly_dark'
    )
    fig.update_layout(xaxis_title="Week Start Date", yaxis_title="Incident Count", plot_bgcolor='#1E293B', paper_bgcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)

def plot_behavior_distribution(df):
    """Plots the distribution of behaviors as a bar chart."""
    behavior_counts = df['behavior'].value_counts().reset_index()
    behavior_counts.columns = ['Behavior', 'Count']
    fig = px.bar(
        behavior_counts, 
        x='Behavior', 
        y='Count', 
        title='Distribution of Behaviors',
        template='plotly_dark'
    )
    fig.update_layout(xaxis_title="Behavior", yaxis_title="Total Count", plot_bgcolor='#1E293B', paper_bgcolor='#1E293B')
    st.plotly_chart(fig, use_container_width=True)
    
def plot_function_distribution(df):
    """Plots the hypothesized function distribution as a pie chart."""
    function_counts = df['hypothesized_function'].value_counts().reset_index()
    function_counts.columns = ['Function', 'Count']
    fig = px.pie(
        function_counts, 
        names='Function', 
        values='Count', 
        title='Hypothesized Function Distribution',
        template='plotly_dark',
        hole=0.3
    )
    fig.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Page Rendering Functions (RESTORED BUTTONS) ---

def render_landing_page():
    """Renders the initial landing page for role selection using buttons."""
    st.title("Behaviour Support & Data Analysis Tool")

    st.markdown("### Welcome, please select your user role/program area to proceed.")
    st.markdown("---")

    # RESTORED: Five button layout
    roles = {
        "Junior Primary (JP)": 'JP',
        "Primary (PY)": 'PY',
        "Senior (SY)": 'SY',
        "Support Staff (SSO/TRT)": 'SSO/TRT',
        "Administrator (ADM)": 'ADM'
    }

    cols = st.columns(5)
    for i, (display_name, role_code) in enumerate(roles.items()):
        with cols[i]:
            if st.button(display_name, key=f"role_{role_code}", use_container_width=True, type="primary"):
                navigate_to('staff_area', role=role_code)
                
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")

def render_staff_area(role):
    """Renders the dashboard/student selection area for staff."""
    st.title(f"{role} Staff Dashboard")
    st.subheader(f"Area Focus: {role}")
    st.markdown("---")

    students_in_area = get_students_for_area(role)
    
    if not students_in_area:
        st.warning("No students are currently assigned to this program area.")
        return

    st.markdown("### Select a Student for Quick Log or Analysis")

    # Display students in cards
    cols = st.columns(3)
    
    for i, (student_id, data) in enumerate(students_in_area):
        student_name = data['name']
        student_program = data['program']
        student_risk = data['risk']
        fba_status = data['fba_status']
        
        # Get incident count for display
        incident_count = len(st.session_state.logs.get(student_id, pd.DataFrame()))

        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{student_name}** ({student_id})")
                st.markdown(f"Program: **{student_program}** | Risk: **{student_risk}**")
                st.markdown(f"Logs: **{incident_count}** | FBA Status: *{fba_status}*")
                
                # Group buttons for logging and viewing
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button("Log Incident", key=f"log_{student_id}", use_container_width=True):
                        navigate_to('quick_log', student=student_id)
                
                with btn_col2:
                    if st.button("View Analysis", key=f"view_{student_id}", use_container_width=True, type="secondary"):
                        navigate_to('student_detail', student=student_id)
                        
    st.markdown("---")
    # Quick navigation back home
    if st.button("← Change Role / Log Out", key='logout_button'):
        navigate_to('landing')

def render_quick_log(current_role, current_student):
    """
    RESTORED: Renders the detailed ABCH Quick Log form.
    """
    
    student = MOCK_STUDENTS.get(current_student)
    student_name = student['name'] if student else "Unknown Student"
    
    st.header(f"✍️ Quick Incident Log for: {student_name}")
    st.subheader(f"Data Capture for Functional Behaviour Assessment (ABCH Log)")
    
    # Navigation Buttons
    col_nav_a, col_nav_b, col_nav_c = st.columns([1, 1, 4])
    col_nav_a.button("↩ Dashboard", on_click=navigate_to, args=('staff_area',), kwargs={'role': current_role}, key='nav_ql_dash')
    col_nav_b.button("View Analysis", on_click=navigate_to, args=('student_detail',), kwargs={'student': current_student, 'role': current_role}, key='nav_ql_detail')

    st.markdown("---")
    
    # --- FORM START ---
    
    with st.form(key='abch_quick_log_form', clear_on_submit=False):
        
        # 1. INCIDENT DETAILS (Header Section)
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 1. Incident Details (When & Who)")
        
        details_col1, details_col2, details_col3 = st.columns(3)

        log_date = details_col1.date_input("Date of Incident", value=datetime.now().date())
        log_time = details_col2.time_input("Time of Incident", value=datetime.now().time())
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
            options=get_active_staff_names(),
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
        submitted = st.form_submit_button("💾 Save Detailed Incident Log", type="primary", use_container_width=True)
        
        if submitted:
            # In a real app, you would save this comprehensive data to your database (e.g., Firestore)
            # For this mock, we will only save minimal data to the mock logs for analysis
            
            # 1. Compile minimal log entry for the analysis DataFrame
            new_log = {
                'log_id': str(uuid.uuid4())[:8],
                'student_id': current_student,
                'date': log_date,
                'time': log_time.strftime('%H:%M'),
                'location': 'Recorded in context',
                'antecedent': antecedent,
                'behavior': behavior,
                'duration_min': 5.0, # Placeholder for analysis
                'severity': 'Medium', # Placeholder for analysis
                'consequence': consequences[0] if consequences else 'None Recorded',
                'hypothesized_function': function,
                'logged_by': logged_by_name,
            }
            
            # 2. Add log entry to the mock data and navigate back
            try:
                df = st.session_state.logs[current_student]
                new_row_df = pd.DataFrame([new_log])
                new_row_df['date'] = pd.to_datetime(new_row_df['date']) 
                st.session_state.logs[current_student] = pd.concat([new_row_df, df], ignore_index=True)
                
                st.success(f"Log entry for {student_name} submitted successfully! Only key fields saved to analysis data.")
                
                # Clear checkbox states for next entry (needed for persistent state between reruns)
                for key in ['o_a_send_home', 'o_b_left_area', 'o_c_assault', 'o_d_property_damage', 'o_e_staff_injury', 'o_f_sapol_callout', 'o_g_first_aid_self', 'o_r_call_out_amb', 'o_h_formal_susp']:
                    if key in st.session_state:
                        st.session_state[key] = False 
                
                navigate_to('staff_area', role=current_role)
                
            except Exception as e:
                st.error(f"Error saving log: {e}")

def render_student_analysis(student_id, role):
    """Renders the detailed analysis page for a selected student."""
    student_info = MOCK_STUDENTS.get(student_id)
    if not student_info:
        st.error("Student information not found.")
        navigate_to('staff_area', role=role)
        return

    st.title(f"Data Analysis for {student_info['name']} ({student_id})")
    st.subheader(f"Risk: {student_info['risk']} | FBA Status: {student_info['fba_status']}")
    st.markdown("---")
    
    df = st.session_state.logs.get(student_id)
    
    if df is None or df.empty:
        st.warning("No incident logs available for this student to generate analysis.")
        if st.button("← Back to Staff Dashboard"):
            navigate_to('staff_area', role=role)
        return

    # --- Key Metrics ---
    total_incidents = len(df)
    last_incident = df['date'].max().strftime('%Y-%m-%d') if total_incidents > 0 else "N/A"
    
    # Calculate average duration for a key metric
    avg_duration = df['duration_min'].mean()
    
    # Get the most common behavior
    most_common_behavior = df['behavior'].mode()[0]
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Incidents (12M)", total_incidents, help="Total number of recorded incidents in the last 12 months.")
    col_m2.metric("Last Incident Date", last_incident)
    col_m3.metric("Avg Duration (min)", f"{avg_duration:.1f}", help="Average duration of recorded incidents.")
    col_m4.metric("Most Common Behavior", most_common_behavior)
    
    st.markdown("---")

    # --- Data Visualizations ---
    
    st.markdown("### Incident Trends and Distribution")
    
    tab1, tab2, tab3 = st.tabs(["Incident Rate", "Behavior Frequency", "Function Analysis"])
    
    with tab1:
        plot_incident_rate(df)
    
    with tab2:
        plot_behavior_distribution(df)

    with tab3:
        plot_function_distribution(df)
        
    st.markdown("---")

    # --- Raw Data View ---
    
    with st.expander("View Raw Incident Log Data"):
        st.dataframe(df.drop(columns=['student_id']).head(20), use_container_width=True) # Show top 20 logs

    st.markdown("---")
    if st.button("← Back to Staff Dashboard", key='back_to_dashboard_from_detail'):
        navigate_to('staff_area', role=role)

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
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
