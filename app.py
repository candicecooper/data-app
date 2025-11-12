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
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input,
    div[data-testid="stTextArea"] textarea {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9;
    }
    
    /* Primary Buttons */
    .stButton>button {
        background-color: #3B82F6; 
        color: white;
        border-radius: 8px;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    
    /* Secondary Buttons */
    .stButton[kind="secondary"]>button {
        background-color: #475569;
        color: #E2E8F0;
    }
    .stButton[kind="secondary"]>button:hover {
        background-color: #334155;
    }
    
    /* Streamlit's default elements for Dataframes and Tables */
    .stTable, .stDataFrame {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Metrics/Info Boxes */
    div[data-testid="stMetric"] label {
        color: #94A3B8;
    }
    div[data-testid="stMetric"] div[data-testid="stMarkdownContainer"] {
        color: #F1F5F9 !important;
        font-size: 1.5rem;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# --- Data Model and Mock Data ---

# Configuration for ABCH Log Categories
INCIDENT_TYPES = [
    "Verbal Aggression", "Physical Aggression", "Property Damage", 
    "Refusal to Comply", "Elopement (Running Away)", "Vocal Disruption", 
    "Self-Injurious Behavior", "Non-Compliance", "Task Avoidance"
]
CONTEXTS = [
    "Classroom - Independent Work", "Classroom - Teacher Instruction", 
    "Transition (Hallway/Yard)", "Recess/Break Time", "Lunch", 
    "Specialist Subject (e.g., Art, PE)", "Arrival/Dismissal"
]
ANTECEDENTS = [
    "Demand/Instruction Given", "Transition Signal", "Denied Access (Item/Activity)", 
    "Peer Interaction/Conflict", "Change in Routine", "Non-Preferred Task Presented",
    "No Observable Antecedent"
]
BEHAVIOUR_FUNCTIONS = [
    "Access to Tangible/Activity", "Escape/Avoidance (Task/Demand)", 
    "Attention (Adult/Peer)", "Sensory/Automatic"
]
CONSEQUENCES = [
    "Redirection/Prompt", "Time-Out/Exclusion", "Loss of Privilege", 
    "Restorative Conversation", "Ignored (Planned)", "Sent to Admin/Leadership"
]
STAFF_ROLES = ["PY", "SY", "ADM"]
YEAR_LEVELS = [f"Year {i}" for i in range(7, 13)]

# Mock Student Data
MOCK_STUDENTS = [
    {'id': 'S001', 'name': 'Alice Johnson', 'year': 'Year 8', 'case_manager': 'PY Lead'},
    {'id': 'S002', 'name': 'Bob Williams', 'year': 'Year 11', 'case_manager': 'SY Lead'},
    {'id': 'S003', 'name': 'Charlie Brown', 'year': 'Year 7', 'case_manager': 'PY Lead'},
    {'id': 'S004', 'name': 'Diana Prince', 'year': 'Year 10', 'case_manager': 'SY Lead'},
    {'id': 'S005', 'name': 'Ethan Hunt', 'year': 'Year 12', 'case_manager': 'SY Lead'},
]

# Mock Incident Data (DataFrame for easy analysis)
# Generating some mock incidents
def generate_mock_incidents():
    data = []
    # Generate 50 incidents for Alice (S001)
    for i in range(50):
        incident_time = datetime.now() - timedelta(days=random.randint(1, 90), hours=random.randint(1, 8), minutes=random.randint(1, 60))
        data.append({
            'id': str(uuid.uuid4()),
            'student_id': 'S001',
            'date_time': incident_time,
            'incident_type': random.choice(INCIDENT_TYPES),
            'context': random.choice(CONTEXTS),
            'antecedent': random.choice(ANTECEDENTS),
            'consequence': random.choice(CONSEQUENCES),
            'function': random.choice(BEHAVIOUR_FUNCTIONS),
            'intensity_rating': random.randint(1, 5),
            'reporter_role': random.choice(STAFF_ROLES),
            'summary': f"Mock summary {i} for S001."
        })
    # Generate 20 incidents for Bob (S002)
    for i in range(20):
        incident_time = datetime.now() - timedelta(days=random.randint(1, 90), hours=random.randint(1, 8), minutes=random.randint(1, 60))
        data.append({
            'id': str(uuid.uuid4()),
            'student_id': 'S002',
            'date_time': incident_time,
            'incident_type': random.choice(INCIDENT_TYPES),
            'context': random.choice(CONTEXTS),
            'antecedent': random.choice(ANTECEDENTS),
            'consequence': random.choice(CONSEQUENCES),
            'function': random.choice(BEHAVIOUR_FUNCTIONS),
            'intensity_rating': random.randint(1, 5),
            'reporter_role': random.choice(STAFF_ROLES),
            'summary': f"Mock summary {i} for S002."
        })
    return pd.DataFrame(data)

# --- State and Data Management Functions ---

def initialize_state():
    """Initializes Streamlit session state variables."""
    if 'data' not in st.session_state:
        st.session_state.data = generate_mock_incidents()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None

def navigate_to(page_name, role=None, student=None):
    """Changes the page view and updates associated state variables."""
    st.session_state.page = page_name
    if role:
        st.session_state.role = role
    if student:
        st.session_state.student = student
    st.rerun()

def get_student_by_id(student_id):
    """Retrieves student details by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_incidents_by_student(student_id):
    """Retrieves all incidents for a specific student."""
    return st.session_state.data[st.session_state.data['student_id'] == student_id].sort_values(by='date_time', ascending=False)

def log_new_incident(incident_data):
    """Adds a new incident to the data state."""
    new_data = pd.DataFrame([incident_data])
    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

# --- Component Functions ---

def staff_header(title, role=None):
    """Renders the standard header for staff areas."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"Behaviour Support: {title}")
    with col2:
        if role:
            st.markdown(f"<div style='background-color: #3B82F6; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold;'>Role: {role}</div>", unsafe_allow_html=True)
        if st.button("⬅ Log Out", key="logout_btn", type="secondary", use_container_width=True):
            navigate_to('landing')

# --- Analysis View Functions ---

def render_analysis_view(student, incidents):
    """Renders data analysis for a selected student."""
    
    st.subheader(f"Data Analysis for {student['name']} ({student['year']})")
    
    if incidents.empty:
        st.warning(f"No incidents recorded for {student['name']} in the system.")
        return

    # 1. Key Metrics
    col1, col2, col3 = st.columns(3)
    total_incidents = len(incidents)
    time_span = (incidents['date_time'].max() - incidents['date_time'].min()).days + 1
    
    with col1:
        st.metric("Total Incidents Logged", total_incidents)
    with col2:
        # Calculate Average Intensity
        avg_intensity = incidents['intensity_rating'].mean()
        st.metric("Avg. Intensity (1-5)", f"{avg_intensity:.1f}")
    with col3:
        # Calculate Incidents per Week
        incidents_per_week = (total_incidents / time_span) * 7 if time_span > 0 else total_incidents
        st.metric("Incidents Per Week", f"{incidents_per_week:.2f}")
        
    st.markdown("---")

    # 2. Charts (Incident Trends)
    st.subheader("Incident Trends")
    
    # Chart 1: Incidents Over Time (Daily Count)
    daily_counts = incidents.set_index('date_time').resample('D').size().reset_index(name='count').fillna(0)
    fig_time = px.bar(daily_counts, x='date_time', y='count', title='Incident Count by Day',
                      color_discrete_sequence=['#4ADE80'])
    fig_time.update_layout(xaxis_title="Date", yaxis_title="Number of Incidents", 
                           plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
    st.plotly_chart(fig_time, use_container_width=True)

    # Chart 2: ABC Analysis (Function of Behaviour)
    st.subheader("ABC Analysis of Behaviour")
    
    col_a, col_b, col_c = st.columns(3)

    # Antecedent Plot
    antecedent_counts = incidents['antecedent'].value_counts().reset_index(name='Count')
    antecedent_counts.columns = ['Antecedent', 'Count']
    fig_ant = px.pie(antecedent_counts, values='Count', names='Antecedent', title='Top Antecedents', 
                     color_discrete_sequence=px.colors.sequential.Agsunset)
    fig_ant.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9', legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    with col_a:
        st.plotly_chart(fig_ant, use_container_width=True)

    # Function Plot
    function_counts = incidents['function'].value_counts().reset_index(name='Count')
    function_counts.columns = ['Function', 'Count']
    fig_func = px.bar(function_counts, x='Function', y='Count', title='Hypothesized Function', 
                      color='Function', color_discrete_sequence=px.colors.qualitative.Bold)
    fig_func.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9')
    with col_b:
        st.plotly_chart(fig_func, use_container_width=True)
        
    # Consequence Plot
    consequence_counts = incidents['consequence'].value_counts().reset_index(name='Count')
    consequence_counts.columns = ['Consequence', 'Count']
    fig_conseq = px.pie(consequence_counts, values='Count', names='Consequence', title='Consequences Applied',
                        color_discrete_sequence=px.colors.sequential.Purples)
    fig_conseq.update_layout(plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#F1F5F9', legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    with col_c:
        st.plotly_chart(fig_conseq, use_container_width=True)

    st.markdown("---")
    
    # 3. Raw Data
    st.subheader("Incident Log (Raw Data)")
    incidents_display = incidents[['date_time', 'incident_type', 'intensity_rating', 'antecedent', 'function', 'consequence', 'summary']]
    # Rename columns for clarity
    incidents_display.columns = ['Date/Time', 'Type', 'Intensity', 'Antecedent (A)', 'Function (F)', 'Consequence (C)', 'Summary']
    st.dataframe(incidents_display, use_container_width=True)


# --- Form Rendering (FIX APPLIED HERE) ---

def render_log_entry_form(student, role):
    """
    Renders the detailed incident log form (ABCH model).
    
    FIX: The value for st.time_input is now calculated FRESHLY 
    on every rerun using datetime.now().time() to prevent stale defaults.
    """
    
    st.info(f"Logging incident for: **{student['name']}** ({student['year']}) | Reported by: **{role}**")

    # Use a unique key for the form to prevent Streamlit internal caching issues
    form_key = f"log_incident_form_{student['id']}_{uuid.uuid4()}"
    
    with st.form(key=form_key):
        st.subheader("1. Incident Details")
        
        # --- Date and Time (FIX APPLIED) ---
        col_date, col_time = st.columns(2)
        with col_date:
            # Default to today's date
            log_date = st.date_input("Log Date", value=datetime.now().date(), key="log_date")
        with col_time:
            # Default to the current time, calculated FRESHLY on form render
            # This is the fix to prevent the stale time from persisting
            log_time = st.time_input("Log Time (approx.)", value=datetime.now().time(), key="log_time")
            
        incident_type = st.multiselect("Incident Type(s)", options=INCIDENT_TYPES, required=True, key="incident_type")
        
        # --- Intensity ---
        intensity_rating = st.slider("Intensity Rating (1=Low, 5=High)", min_value=1, max_value=5, value=3, key="intensity_rating")
        
        st.subheader("2. Context & ABC Analysis")
        
        col_context, col_antecedent = st.columns(2)
        with col_context:
            context = st.selectbox("Context / Location", options=CONTEXTS, required=True, key="context")
        with col_antecedent:
            antecedent = st.selectbox("Antecedent (What happened immediately before?)", options=ANTECEDENTS, required=True, key="antecedent")

        col_consequence, col_function = st.columns(2)
        with col_consequence:
            consequence = st.selectbox("Consequence (What happened immediately after?)", options=CONSEQUENCES, required=True, key="consequence")
        with col_function:
            function = st.selectbox("Hypothesized Function (Why did the behaviour occur?)", options=BEHAVIOUR_FUNCTIONS, required=True, key="function")

        st.subheader("3. Narrative Summary")
        summary = st.text_area("Detailed Narrative Summary (Include staff actions, student response, and outcome)", height=150, key="summary")
        
        submitted = st.form_submit_button("✅ Submit Incident Log")

        if submitted:
            if not incident_type or not summary:
                st.error("Please fill in all required fields (Incident Type and Summary).")
            else:
                # Combine date and time for a single datetime object
                try:
                    incident_datetime = datetime.combine(log_date, log_time)
                except Exception as e:
                    st.error(f"Error combining date and time: {e}")
                    return

                new_incident = {
                    'id': str(uuid.uuid4()),
                    'student_id': student['id'],
                    'date_time': incident_datetime,
                    'incident_type': ', '.join(incident_type),
                    'context': context,
                    'antecedent': antecedent,
                    'consequence': consequence,
                    'function': function,
                    'intensity_rating': intensity_rating,
                    'reporter_role': role,
                    'summary': summary
                }
                
                log_new_incident(new_incident)
                st.success("Incident successfully logged! Returning to student list.")
                # Navigate back to the student list after successful log
                navigate_to('staff_area', role=role, student=None)
                
# --- Page Rendering Functions ---

def render_staff_area(role):
    """Renders the main staff dashboard with student list and actions."""
    staff_header(f"{role} Dashboard", role=role)
    
    st.subheader("Select a Student")
    
    # Filter students based on a mock grouping logic (for demonstration)
    if role == 'PY':
        filtered_students = [s for s in MOCK_STUDENTS if s['year'] in [f'Year {i}' for i in range(7, 10)]]
    elif role == 'SY':
        filtered_students = [s for s in MOCK_STUDENTS if s['year'] in [f'Year {i}' for i in range(10, 13)]]
    else: # ADM sees all
        filtered_students = MOCK_STUDENTS

    if not filtered_students:
        st.warning("No students assigned to this role's oversight for this demonstration.")
        return

    # Create a layout for student cards
    cols = st.columns(3) # 3 cards per row
    
    for i, student in enumerate(filtered_students):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.markdown(f"**{student['name']}**")
                st.markdown(f"*{student['year']}*")
                st.markdown(f"<small>ID: {student['id']}</small>", unsafe_allow_html=True)
                
                col_view, col_log = st.columns(2)
                with col_view:
                    if st.button("📊 View Analysis", key=f"view_{student['id']}", use_container_width=True):
                        navigate_to('student_detail', role=role, student=student)
                with col_log:
                    if st.button("📝 Quick Log", key=f"log_{student['id']}", type="primary", use_container_width=True):
                        navigate_to('quick_log', role=role, student=student)


def render_student_analysis(student, role):
    """Renders the analysis view for a specific student."""
    staff_header(f"Analysis: {student['name']}", role=role)
    incidents = get_incidents_by_student(student['id'])
    
    render_analysis_view(student, incidents)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅ Back to Dashboard", key="back_from_analysis", type="secondary", use_container_width=True):
            navigate_to('staff_area', role=role, student=None)
    with col2:
        if st.button(f"📝 Log New Incident for {student['name']}", key="log_from_analysis", type="primary"):
            navigate_to('quick_log', role=role, student=student)


def render_quick_log(role, student):
    """Renders the quick log page for a selected student."""
    staff_header(f"Quick Incident Log ({student['name']})", role=role)
    render_log_entry_form(student, role)
    
    st.markdown("---")
    if st.button("⬅ Back to Student Dashboard", key="back_from_log", type="secondary"):
         navigate_to('staff_area', role=role, student=None)

def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("## Welcome! Please select your role to continue.")
    
    # Role selection buttons
    col_py, col_sy, col_adm = st.columns(3)
    
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
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
            # Should not happen if role selection is mandatory
            navigate_to('landing')

if __name__ == '__main__':
    main()