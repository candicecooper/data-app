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
    div[data-testid="stTextArea"] > div > textarea,
    div[data-testid="stSelectbox"] div.st-emotion-cache-1c7v0s4 {
        background-color: #0F172A; /* Darker background for inputs */
        color: #F1F5F9;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    /* Primary Button Styling */
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
    
    /* Streamlit's expander */
    .streamlit-expanderHeader {
        background-color: #334155;
        border-radius: 8px;
        color: #F1F5F9;
        font-weight: bold;
    }
    .streamlit-expanderContent {
        background-color: #1E293B;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        border: 1px solid #334155;
        border-top: none;
    }
    
    /* DataFrame Styling */
    .stDataFrame {
        border-radius: 12px;
        border: 1px solid #334155;
    }
    /* Metric/Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3B82F6;
    }
    
    /* Ensure markdown text within columns is visible */
    div[data-testid="stVerticalBlock"] .stMarkdown {
        color: #E2E8F0;
    }

    /* Center plot titles */
    .plot-container div[data-testid="stBlock"] > div > div > h3 {
        text-align: center;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# --- Mock Data and Utility Functions ---

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
    antecedents = ['Transition request', 'Peer denied request', 'Noise level high', 'Independent work']
    behaviors = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)']
    consequences = ['Redirection', 'Time-out', 'Loss of privilege', 'Check-in with staff']
    functions = ['Access to Tangibles', 'Escape/Avoidance', 'Attention', 'Sensory']
    
    # Generate 50-100 entries spread over the last year
    num_entries = random.randint(50, 100)
    
    for _ in range(num_entries):
        incident_date = datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(1, 24), minutes=random.randint(1, 60))
        
        # Determine behavior and function logic
        behavior = random.choice(behaviors)
        
        # Simulate function correlation (e.g., Elopement often linked to Escape/Avoidance)
        function = random.choice(functions)
        if behavior == 'Elopement':
            function = 'Escape/Avoidance'
        elif behavior == 'Property Destruction':
            function = 'Access to Tangibles'

        logs.append({
            'log_id': str(uuid.uuid4())[:8],
            'student_id': student_id,
            'date': incident_date.date(),
            'time': incident_date.strftime('%H:%M'),
            'location': random.choice(locations),
            'antecedent': random.choice(antecedents),
            'behavior': behavior,
            'duration_min': random.uniform(1, 15),
            'severity': random.choice(['Low', 'Medium', 'High']),
            'consequence': random.choice(consequences),
            'hypothesized_function': function,
            'logged_by': random.choice(['Emily Jones (JP)', 'Daniel Lee (PY)', 'Sarah Chen (SY)', 'Admin User (ADM)']),
        })

    df = pd.DataFrame(logs)
    # Ensure date column is datetime objects for plotting
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values(by='date', ascending=False).reset_index(drop=True)

# Helper function to get students for a specific program area
def get_students_for_area(role):
    """Filters mock students based on staff role/program area."""
    # ADM sees all students
    if role == 'ADM':
        return list(MOCK_STUDENTS.items())
    
    # SSO/TRT sees all students
    if role == 'SSO/TRT':
        return list(MOCK_STUDENTS.items())
        
    # Standard roles see only their program area students
    program_area = role.split('/')[0] # Handles 'JP', 'PY', 'SY'
    return [(k, v) for k, v in MOCK_STUDENTS.items() if v['program'] == program_area]

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
        st.session_state.quick_log_data = {} # Temporary storage for quick log form

def navigate_to(page, role=None, student=None):
    """Sets session state to navigate to a new page."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
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

# --- Page Rendering Functions ---

def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Tool")

    st.markdown("### Welcome, please select your user role/program area to proceed.")
    st.markdown("---")

    roles = {
        "Junior Primary (JP)": 'JP',
        "Primary (PY)": 'PY',
        "Senior (SY)": 'SY',
        "Support Staff (SSO/TRT)": 'SSO/TRT',
        "Administrator (ADM)": 'ADM'
    }

    # Use a selectbox for a single, consolidated program/role selection
    selected_display_role = st.selectbox(
        "Select your **Role / Program Area**:",
        options=list(roles.keys()),
        index=None,
        placeholder="Choose your access level...",
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if selected_display_role:
            selected_role_code = roles[selected_display_role]
            if st.button(f"Access Dashboard as {selected_display_role}", use_container_width=True, type="primary"):
                navigate_to('staff_area', role=selected_role_code)
        else:
            st.info("Please select a role/area from the dropdown above to continue.")

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

        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{student_name}** ({student_id})")
                st.markdown(f"Area: **{student_program}** | Risk: **{student_risk}**")
                st.markdown(f"FBA Status: *{fba_status}*")
                
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


# --- Quick Log Form (Simplified ABCH) ---

# Note: This is a streamlined version for the dashboard.
# A full ABCH log would require many more fields (staff involved, outcome checklist, etc.)

def render_quick_log(role, student_id):
    """Renders a quick log form for a selected student."""
    student_info = MOCK_STUDENTS.get(student_id)
    if not student_info:
        st.error("Student information not found.")
        navigate_to('staff_area', role=role)
        return

    st.title(f"Quick Incident Log for {student_info['name']} ({student_id})")
    st.subheader(f"Program Area: {student_info['program']}")
    st.markdown("---")
    
    # Store preliminary data
    preliminary_data = st.session_state.quick_log_data.get('preliminary', {})

    with st.form("quick_log_form", clear_on_submit=False):
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            log_date = st.date_input("Date of Incident", value=datetime.now().date())
            
        with col2:
            log_time = st.time_input("Time of Incident", value=datetime.now().time())
            
        with col3:
            location = st.selectbox("Location", options=['Classroom', 'Playground', 'Library', 'Canteen', 'Oval', 'Other'], index=0)

        st.markdown("---")

        st.markdown("### A: Antecedent (What happened right before the behavior?)")
        antecedent = st.text_area("Describe the events, triggers, or setting conditions (e.g., transition request, peer interaction, demand, lack of attention).", height=100)
        
        st.markdown("### B: Behavior (What specific, observable action did the student take?)")
        behavior_options = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst', 'Other']
        behavior = st.selectbox("Observed Behavior", options=behavior_options, index=0)
        if behavior == 'Other':
            behavior_other = st.text_input("Specify the behavior:")
            behavior = behavior_other or "Other Specified Behavior"

        # Duration and Severity
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            duration = st.slider("Approximate Duration (minutes)", min_value=0.5, max_value=30.0, value=2.0, step=0.5)
        with col_b2:
            severity = st.radio("Severity", options=['Low (Minor disruption)', 'Medium (Requires staff intervention)', 'High (Safety Risk/Major disruption)'], index=1)
            
        st.markdown("### C: Consequence (What happened immediately after the behavior? How did staff respond?)")
        consequence = st.text_area("Describe the staff response and the immediate outcome for the student/environment.", height=100)
        
        st.markdown("---")
        
        st.markdown("### H: Hypothesized Function (Why do you think the behavior occurred?)")
        function_options = [
            'Access to Tangibles/Activity',
            'Escape/Avoidance of Demand/Task',
            'Attention (Peer or Adult)',
            'Sensory/Automatic Reinforcement',
            'Communication/Cry for Help'
        ]
        function = st.radio("Primary Hypothesized Function", options=function_options, index=1)
        
        # Save Button
        log_submitted = st.form_submit_button("Submit Quick Log Entry", type="primary", use_container_width=True)

    if log_submitted:
        # 1. Compile log entry
        new_log = {
            'log_id': str(uuid.uuid4())[:8],
            'student_id': student_id,
            'date': log_date,
            'time': log_time.strftime('%H:%M'),
            'location': location,
            'antecedent': antecedent,
            'behavior': behavior,
            'duration_min': duration,
            'severity': severity.split(' ')[0], # Just save 'Low', 'Medium', or 'High'
            'consequence': consequence,
            'hypothesized_function': function,
            'logged_by': st.session_state.role, # Use the user's role/area for simplicity
        }
        
        # 2. Add log entry to the mock data and navigate back
        try:
            # Ensure the logs DataFrame exists and is up to date
            df = st.session_state.logs[student_id]
            # Convert new log to a DataFrame row
            new_row_df = pd.DataFrame([new_log])
            new_row_df['date'] = pd.to_datetime(new_row_df['date']) # Ensure date is datetime
            
            # Prepend the new log to the existing DataFrame
            st.session_state.logs[student_id] = pd.concat([new_row_df, df], ignore_index=True)
            
            st.success(f"Log entry for {student_info['name']} submitted successfully!")
            # Clear temporary form data after successful submission (optional, but good practice)
            st.session_state.quick_log_data = {}
            # Wait a moment, then return to the staff dashboard
            # Note: st.rerun() is immediate, but we use success message first.
            navigate_to('staff_area', role=role)
            
        except Exception as e:
            st.error(f"Error saving log: {e}")

    st.markdown("---")
    if st.button("← Back to Staff Dashboard", key='back_to_dashboard'):
        navigate_to('staff_area', role=role)

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
