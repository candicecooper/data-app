import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np
import time as time_module

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
    div[data-testid="stSelectbox"] > div[role="combobox"] {
        background-color: #0F172A;
        border: 1px solid #334155;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4C51BF; /* Indigo */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #4338CA;
    }

    /* Primary Button (Quick Log/Save) */
    .st-emotion-cache-nahz7x {
        background-color: #10B981; /* Emerald Green */
    }
    .st-emotion-cache-nahz7x:hover {
        background-color: #059669;
    }

    /* Metric/Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #6366F1;
    }
    
    /* Streamlit Containers/Columns for better visual separation */
    .st-emotion-cache-z5ttm3 { /* Specific selector for column content */
        padding-top: 0;
    }

    /* Footer/Info Bar */
    .st-emotion-cache-1c9vcm4 {
        border-top: 1px solid #334155;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- MOCK DATA and CONFIGURATION ---

# Staff roles and names
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones', 'role': 'JP', 'active': True, 'email': 'emily@school.edu'},
    {'id': 's2', 'name': 'Daniel Lee', 'role': 'PY', 'active': True, 'email': 'daniel@school.edu'},
    {'id': 's3', 'name': 'Sarah Chen', 'role': 'SY', 'active': True, 'email': 'sarah@school.edu'},
    {'id': 's4', 'name': 'Admin User', 'role': 'ADM', 'active': True, 'email': 'admin@school.edu'},
]

# Student Data
MOCK_STUDENTS = [
    {'id': 'stu1', 'name': 'Izack P.', 'grade': '7', 'primary_staff_id': 's2', 'plan_summary': 'Sensory-seeking, requires frequent movement breaks and clear visual schedules.'},
    {'id': 'stu2', 'name': 'Maya R.', 'grade': '10', 'primary_staff_id': 's3', 'plan_summary': 'Avoidance behaviour related to literacy tasks. Use choice boards and peer support.'},
    {'id': 'stu3', 'name': 'Noah K.', 'grade': '4', 'primary_staff_id': 's1', 'plan_summary': 'Low frustration tolerance. Implement Check-In/Check-Out system and explicit teaching of emotional regulation.'},
]

# Navigation Options per role
nav_options = {
    'ADM': {
        'Dashboard': ('staff_area', None),
        'All Students': ('staff_area', 'All Students'),
        'Reports': ('staff_area', 'Reports'),
        'Settings': ('staff_area', 'Settings'),
    },
    'PY': { # Primary Year
        'Dashboard': ('staff_area', None),
        'My Students': ('staff_area', 'My Students'),
        'Quick Log': ('quick_log', None),
    },
    'SY': { # Secondary Year
        'Dashboard': ('staff_area', None),
        'My Students': ('staff_area', 'My Students'),
        'Quick Log': ('quick_log', None),
    },
    'JP': { # Junior Primary
        'Dashboard': ('staff_area', None),
        'My Students': ('staff_area', 'My Students'),
        'Quick Log': ('quick_log', None),
    },
}


# FBA and Data Constants
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Vocal/Physical)']
ANTECEDENTS = ['Task Demand', 'Transition', 'Unstructured Time', 'Sensory Overload', 'Peer Conflict', 'Attention from Adult/Peer']
CONSEQUENCES = ['Task Escape', 'Access to Tangible/Activity', 'Staff Attention', 'Peer Attention', 'Sensory Input']
LOCATIONS = ['Classroom', 'Yard', 'Specialist Room', 'Corridor', 'Office']

# --- Helper Functions ---

def get_active_staff():
    """Returns a list of active staff names for dropdowns."""
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_student_by_id(student_id):
    """Finds student data by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_staff_by_id(staff_id):
    """Finds staff data by ID."""
    return next((s for s in MOCK_STAFF if s['id'] == staff_id), None)

def get_student_name(student_id):
    """Returns student name from ID."""
    student = get_student_by_id(student_id)
    return student['name'] if student else 'Unknown Student'

def navigate_to(page_key, **kwargs):
    """Updates session state for page routing."""
    st.session_state.page = page_key
    for key, value in kwargs.items():
        st.session_state[key] = value

def initialize_state():
    """Ensures necessary session state keys exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'incident_logs' not in st.session_state:
        # Mock incident data for charting
        data = {
            'date': [datetime.now().date() - timedelta(days=i % 30) for i in range(100)],
            'student_id': [random.choice([s['id'] for s in MOCK_STUDENTS]) for _ in range(100)],
            'student_name': [get_student_name(random.choice([s['id'] for s in MOCK_STUDENTS])) for _ in range(100)],
            'antecedent': [random.choice(ANTECEDENTS) for _ in range(100)],
            'behaviour': [random.choice(BEHAVIORS_FBA) for _ in range(100)],
            'intensity': [random.randint(1, 5) for _ in range(100)],
            'staff_id': [random.choice([s['id'] for s in MOCK_STAFF]) for _ in range(100)],
        }
        st.session_state.incident_logs = pd.DataFrame(data)

def save_log_entry(data):
    """Saves a new incident log entry to the session state."""
    
    # Ensure all columns exist, fill with None/default if missing from the form
    required_cols = st.session_state.incident_logs.columns
    for col in required_cols:
        if col not in data:
            data[col] = None
            
    # Convert data dictionary to DataFrame row
    new_row_df = pd.DataFrame([data])
    
    # Ensure column order matches existing DataFrame before concatenation
    new_row_df = new_row_df[required_cols]

    # Append the new log entry
    st.session_state.incident_logs = pd.concat(
        [st.session_state.incident_logs, new_row_df], 
        ignore_index=True
    )
    st.success("Log Entry Saved Successfully!")


# --- UI Components ---

# FIX APPLIED HERE (Around line 840)
def staff_header(role):
    """Renders the navigation menu based on the user's role."""
    
    st.title("Data-Driven Behaviour Support")
    
    nav_opts = nav_options.get(role, {})
    num_cols = len(nav_opts)

    # --- FIX FOR StreamlitInvalidColumnSpecError ---
    if num_cols == 0:
        st.warning(f"No navigation options configured for role: **{role}**.")
        return
    # -----------------------------------------------

    cols = st.columns(num_cols) # This will now be > 0
    
    # Create navigation buttons
    for i, (label, (page_key, sub_page)) in enumerate(nav_opts.items()):
        with cols[i]:
            if st.button(label, key=f"nav_{page_key}_{sub_page or ''}"):
                navigate_to(page_key, staff_sub_page=sub_page, role=role)
                st.rerun()

def staff_selector_sidebar():
    """Allows mock login for testing different roles."""
    st.sidebar.title("Login / Role Selector")
    
    # Map staff names to their IDs for the dropdown
    staff_map = {s['name']: s['id'] for s in MOCK_STAFF}
    staff_options = list(staff_map.keys())
    
    selected_name = st.sidebar.selectbox(
        "Select your Staff Profile:", 
        options=[''] + staff_options, 
        index=0,
        key='login_staff_name'
    )
    
    if st.sidebar.button("Log In"):
        if selected_name:
            staff_id = staff_map[selected_name]
            staff_data = get_staff_by_id(staff_id)
            if staff_data:
                navigate_to('staff_area', role=staff_data['role'])
                st.rerun()
        else:
            st.sidebar.error("Please select a staff profile.")

def student_selector(role):
    """Renders a dropdown to select a student for quick log or detail view."""
    
    # Filter students based on role (ADM sees all, others see only their primary students)
    if role != 'ADM':
        # Find the current staff ID
        current_staff = next((s for s in MOCK_STAFF if s['role'] == role), None)
        if current_staff:
            filtered_students = [
                s for s in MOCK_STUDENTS if s['primary_staff_id'] == current_staff['id']
            ]
        else:
             filtered_students = []
    else:
        filtered_students = MOCK_STUDENTS

    # Map student names to their IDs for the dropdown
    student_map = {f"{s['name']} (Gr {s['grade']})": s['id'] for s in filtered_students}
    student_options = list(student_map.keys())
    
    st.subheader("Student Context")
    
    selected_name = st.selectbox(
        "Select a Student for Action or Analysis:", 
        options=[''] + student_options, 
        index=0,
        key='selected_student_for_action'
    )
    
    if selected_name:
        student_id = student_map[selected_name]
        st.session_state.student = student_id
        
        # Display buttons for actions once a student is selected
        col_log, col_detail = st.columns(2)
        with col_log:
            if st.button("Quick Log Incident", use_container_width=True, key='go_quick_log'):
                navigate_to('quick_log', student=student_id, role=role)
                st.rerun()
        with col_detail:
            if st.button("View Student Analysis", use_container_width=True, key='go_student_detail'):
                navigate_to('student_detail', student=student_id, role=role)
                st.rerun()
    else:
        st.session_state.student = None
        st.info("Please select a student to enable actions.")


# --- Page Rendering Functions ---

def render_landing_page():
    """Initial page for role selection."""
    staff_selector_sidebar()
    
    st.markdown("## Welcome to the Behaviour Data & Support Tool")
    st.markdown("---")
    st.info("Please select your staff profile from the sidebar to access the dashboard and support features.")

def render_quick_log(role, student_id):
    """Renders the simplified ABC Quick Log form."""
    
    student_data = get_student_by_id(student_id)
    student_name = student_data['name']
    
    staff_header(role)
    st.markdown("---")
    st.header(f"Quick Log: Incident for {student_name}")

    with st.form(key='quick_log_form'):
        st.subheader("Incident Details")
        
        # Time and Location
        col1, col2, col3 = st.columns(3)
        with col1:
            incident_date = st.date_input("Date", datetime.now().date())
        with col2:
            incident_time = st.time_input("Time", datetime.now().time())
        with col3:
            location = st.selectbox("Location", options=LOCATIONS)

        st.subheader("A - Antecedent (What happened right before?)")
        antecedent = st.selectbox("Primary Antecedent", options=ANTECEDENTS)
        context = st.text_area("Specific Context/Notes (What exactly was happening?)", key='log_context')
        
        st.subheader("B - Behaviour (What behaviour was observed?)")
        behaviour = st.multiselect("Behaviour(s) Observed", options=BEHAVIORS_FBA)
        intensity = st.slider("Intensity (1=Low, 5=High)", min_value=1, max_value=5, value=3)
        
        st.subheader("C - Consequence/Intervention (What happened right after?)")
        consequence_action = st.selectbox("Primary Consequence/Intervention", options=CONSEQUENCES)
        
        incident_description = st.text_area("Detailed Incident Summary (mandatory for high intensity)", key='log_summary')
        
        submitted = st.form_submit_button("Submit Log Entry")
        
        if submitted:
            if not behaviour or not incident_description:
                st.error("Please select at least one Behaviour and provide a Detailed Incident Summary.")
            else:
                log_data = {
                    'date': incident_date,
                    'time': incident_time.strftime("%H:%M:%S"),
                    'student_id': student_id,
                    'student_name': student_name,
                    'antecedent': antecedent,
                    'behaviour': ", ".join(behaviour),
                    'intensity': intensity,
                    'consequence': consequence_action,
                    'location': location,
                    'context': context,
                    'description': incident_description,
                    'staff_id': next((s['id'] for s in MOCK_STAFF if s['role'] == role), 'unknown_staff_id'),
                    'log_id': str(uuid.uuid4())
                }
                save_log_entry(log_data)
                # Navigate back to staff area after saving
                navigate_to('staff_area', role=role)
                st.rerun()

def render_student_analysis(student_id, role):
    """Renders the data analysis dashboard for a selected student."""
    
    student_data = get_student_by_id(student_id)
    if not student_data:
        st.error("Student data not found.")
        navigate_to('staff_area', role=role)
        st.rerun()
        return

    student_name = student_data['name']
    
    staff_header(role)
    st.markdown("---")
    st.header(f"Data Analysis: {student_name}")
    
    # Filter logs for the selected student
    student_logs = st.session_state.incident_logs[
        st.session_state.incident_logs['student_id'] == student_id
    ]
    
    # 1. Summary Metrics
    st.subheader("Summary Metrics (Last 90 Days)")
    
    # Filter logs to last 90 days
    cutoff_date = datetime.now().date() - timedelta(days=90)
    recent_logs = student_logs[student_logs['date'] >= cutoff_date]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Incidents", recent_logs.shape[0])
    
    with col2:
        avg_intensity = recent_logs['intensity'].mean() if not recent_logs.empty else 0
        st.metric("Avg. Intensity", f"{avg_intensity:.1f}")
        
    with col3:
        top_behaviour = recent_logs['behaviour'].mode().iloc[0] if not recent_logs.empty else "N/A"
        st.metric("Most Frequent Behaviour", top_behaviour)

    # 2. Incident Trend Chart
    st.subheader("Incident Trend Over Time")
    if not recent_logs.empty:
        # Group by date and count incidents
        trend_data = recent_logs.groupby('date').size().reset_index(name='Incident Count')
        fig_trend = px.line(
            trend_data, 
            x='date', 
            y='Incident Count', 
            title=f"Incident Count for {student_name}",
            color_discrete_sequence=['#6366F1']
        )
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Count", plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No recent log data available for this student.")


    # 3. ABC Analysis Charts
    st.subheader("ABC Frequency Analysis")
    
    if not recent_logs.empty:
        col_ant, col_beh, col_con = st.columns(3)
        
        with col_ant:
            ant_counts = recent_logs['antecedent'].value_counts().reset_index(name='Count')
            fig_ant = px.pie(ant_counts, values='Count', names='antecedent', title='Antecedent Distribution', color_discrete_sequence=px.colors.sequential.Sunset)
            fig_ant.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
            st.plotly_chart(fig_ant, use_container_width=True)

        with col_beh:
            # Need to handle the multiselect behaviour column correctly for analysis
            all_behaviours = [b.strip() for sublist in recent_logs['behaviour'].str.split(', ') for b in sublist]
            beh_counts = pd.Series(all_behaviours).value_counts().reset_index(name='Count')
            beh_counts.columns = ['Behaviour', 'Count']
            fig_beh = px.bar(beh_counts.head(5), x='Behaviour', y='Count', title='Top 5 Behaviours', color='Behaviour', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_beh.update_layout(xaxis_title="", yaxis_title="Count", plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
            st.plotly_chart(fig_beh, use_container_width=True)
            
        with col_con:
            con_counts = recent_logs['consequence'].value_counts().reset_index(name='Count')
            fig_con = px.pie(con_counts, values='Count', names='consequence', title='Consequence Distribution', color_discrete_sequence=px.colors.sequential.Plasma)
            fig_con.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
            st.plotly_chart(fig_con, use_container_width=True)

    # 4. Intervention Plan Summary
    st.subheader(f"Current Behaviour Support Plan Summary")
    st.success(student_data['plan_summary'])

    # 5. Raw Data (optional)
    if role == 'ADM':
        st.subheader("Raw Incident Data (Admin View)")
        st.dataframe(student_logs, use_container_width=True)

    # Button to go back to dashboard
    if st.button("← Back to Dashboard", key='back_from_detail'):
        navigate_to('staff_area', role=role)
        st.rerun()

def render_staff_area():
    """Renders the main staff dashboard."""
    
    role = st.session_state.get('role')
    sub_page = st.session_state.get('staff_sub_page')
    
    staff_header(role)
    st.markdown("---")
    
    st.subheader(f"Welcome, {role} User. Current View: {sub_page or 'Dashboard'}")
    
    if sub_page is None or sub_page in ['My Students', 'All Students']:
        # Dashboard or Student Selection View
        student_selector(role)
        
    elif sub_page == 'Reports':
        st.header("School-Wide Data Reports (ADM Only)")
        st.markdown("**Placeholder for Aggregated School-Wide Reports/Heatmaps.**")
        
        # Example: Overall behaviour frequency
        all_logs = st.session_state.incident_logs
        if not all_logs.empty:
            all_behaviours = [b.strip() for sublist in all_logs['behaviour'].str.split(', ') for b in sublist]
            beh_counts = pd.Series(all_behaviours).value_counts().reset_index(name='Count')
            beh_counts.columns = ['Behaviour', 'Count']
            fig_all = px.bar(beh_counts.head(10), x='Behaviour', y='Count', title='Top 10 School-Wide Behaviours', color='Behaviour', color_discrete_sequence=px.colors.qualitative.Vivid)
            fig_all.update_layout(xaxis_title="", yaxis_title="Total Count", plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
            st.plotly_chart(fig_all, use_container_width=True)
            
        
    elif sub_page == 'Settings':
        st.header("User and System Settings")
        st.markdown("**Placeholder for User Management, Constant Configuration, etc.**")
        st.info(f"Your current email is: {next((s['email'] for s in MOCK_STAFF if s['role'] == role), 'N/A')}")
        
    
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
            render_staff_area()
        else:
            # Should not happen if authenticated, but route back to landing for safety
            navigate_to('landing')
            st.rerun()

if __name__ == "__main__":
    main()
