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
    div[data-testid="stSelectbox"] > div > div > div {
        background-color: #0F172A;
        border: 1px solid #334155;
        color: #F1F5F9;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #3B82F6; /* Blue for primary actions */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.2s, transform 0.1s;
    }
    .stButton > button:hover {
        background-color: #2563EB;
        transform: translateY(-1px);
    }
    
    /* Secondary/Navigation Buttons */
    .st-emotion-cache-nahz7x button {
        background-color: #334155; /* Darker secondary */
        color: #94A3B8;
    }
    .st-emotion-cache-nahz7x button:hover {
        background-color: #475569;
        color: #F1F5F9;
    }
    
    /* Dataframe and Table Styling */
    .stDataFrame {
        border-radius: 8px;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """
, unsafe_allow_html=True)


# --- Mock Data and Utilities ---

# MOCK Data for students and staff
MOCK_STUDENTS = [
    {'id': 's101', 'name': 'Alex Johnson', 'year': 7, 'role': 'PY', 'plan_tier': 2},
    {'id': 's102', 'name': 'Beth Smith', 'year': 8, 'role': 'PY', 'plan_tier': 1},
    {'id': 's103', 'name': 'Charlie Davis', 'year': 7, 'role': 'JP', 'plan_tier': 3},
]

MOCK_STAFF = [
    {'id': 'staff1', 'name': 'Emily Jones (JP)', 'role': 'JP'},
    {'id': 'staff2', 'name': 'Daniel Lee (PY)', 'role': 'PY'},
    {'id': 'staff3', 'name': 'Sarah Chen (SY)', 'role': 'SY'},
    {'id': 'staff4', 'name': 'Admin User (ADM)', 'role': 'ADM'},
]

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Screaming)', 'Physical Aggression (Staff)']
MOTIVATIONS = ['Gain Attention', 'Escape Demand/Task', 'Access Tangible', 'Sensory Regulation/Automatic']
CONTEXTS = ['Classroom Activity', 'Transition', 'Recess/Lunch', 'Specific Staff Interaction', 'Peer Conflict', 'Non-Structured Time']
WOT_LABELS = ['Baseline', 'Alert', 'High Alert', 'Shutdown', 'Crisis']
role_map = {'JP': 'Junior Primary', 'PY': 'Primary', 'SY': 'Secondary', 'ADM': 'Admin/Leadership'}

# Mock Log Generation (for demo data)
def generate_mock_log(student_id, date, hour, minute):
    timestamp = datetime.combine(date, time(hour, minute))
    
    behavior = random.choice(BEHAVIORS_FBA)
    antecedent = random.choice(CONTEXTS)
    consequence = random.choice(['Time out', 'Calm down strategy', 'Loss of privilege', 'Restraint (mock)', 'Parent call'])
    motivation = random.choice(MOTIVATIONS)
    wot_start = random.choice(WOT_LABELS[:-1]) # Cannot start at Crisis
    wot_end = random.choice(WOT_LABELS[WOT_LABELS.index(wot_start):]) # WOT can only increase or stay same
    
    # Critical incidents occur only 10% of the time
    is_critical = random.random() < 0.1
    
    return {
        'log_id': str(uuid.uuid4()),
        'student_id': student_id,
        'timestamp': timestamp,
        'date': date,
        'time': time(hour, minute),
        'staff_id': random.choice(MOCK_STAFF)['id'],
        'behavior': behavior,
        'antecedent': antecedent,
        'consequence': consequence,
        'motivation': motivation,
        'duration_min': random.randint(1, 15),
        'wot_start': wot_start,
        'wot_end': wot_end,
        'is_critical': is_critical,
        'notes': f"Quick log entry for {behavior} after {antecedent}. Resolved with {consequence}.",
    }

def initialize_state():
    """Initializes session state variables if they don't exist."""
    if 'students' not in st.session_state:
        st.session_state.students = MOCK_STUDENTS
    if 'log_data' not in st.session_state:
        # Generate 100 mock logs over the last 30 days
        logs = []
        today = datetime.now().date()
        for _ in range(100):
            date = today - timedelta(days=random.randint(0, 30))
            hour = random.randint(9, 15)
            minute = random.randint(0, 59)
            logs.append(generate_mock_log(random.choice(MOCK_STUDENTS)['id'], date, hour, minute))
        st.session_state.log_data = pd.DataFrame(logs)
        st.session_state.log_data['date'] = pd.to_datetime(st.session_state.log_data['date'])
        
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'log_data_to_edit' not in st.session_state:
        st.session_state.log_data_to_edit = None
    # NEW: Initialize incident type for navigation differentiation
    if 'incident_type' not in st.session_state:
        st.session_state.incident_type = 'standard'
        
def navigate_to(page: str, student=None, role=None, log_data=None, incident_type='standard'):
    """
    Handles page navigation by setting session state variables.
    
    CRITICAL FIX: Added incident_type to differentiate between 
    ABCH Quick Log and Critical Incident navigation.
    """
    st.session_state.page = page
    if student:
        st.session_state.student = student
    if role:
        st.session_state.role = role
    if log_data:
        st.session_state.log_data_to_edit = log_data
    st.session_state.incident_type = incident_type
    # Rerun the app to trigger navigation
    st.rerun()
    
def get_student_logs(student_id):
    """Retrieves all logs for a specific student."""
    return st.session_state.log_data[st.session_state.log_data['student_id'] == student_id]

def get_staff_name(staff_id):
    """Mocks retrieval of staff name."""
    return next((s['name'] for s in MOCK_STAFF if s['id'] == staff_id), "Unknown Staff")

# --- Page Rendering Functions ---

def render_landing_page():
    st.title("Welcome to the Behaviour Support Dashboard")
    st.markdown("---")
    
    st.subheader("Select Your Access Role")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Junior Primary (JP)", use_container_width=True):
            navigate_to('staff_area', role='JP')
            
    with col2:
        if st.button("Primary (PY)", use_container_width=True):
            navigate_to('staff_area', role='PY')

    with col3:
        if st.button("Secondary (SY)", use_container_width=True):
            navigate_to('staff_area', role='SY')

    with col4:
        if st.button("Admin/Leadership (ADM)", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")

def render_quick_log(current_role, current_student):
    """Renders the comprehensive ABCH log form."""
    
    incident_type = st.session_state.get('incident_type', 'standard')

    # Display dynamic header based on navigation
    st.header(f"Incident Log for {current_student['name']}")

    if incident_type == 'critical':
        st.error("🚨 CRITICAL INCIDENT REPORT 🚨 (Requires full completion and immediate follow-up)")
    elif incident_type == 'abch_quick':
        st.info("✍️ ABCH Quick Log (Focus on Antecedent, Behavior, Consequence, and Hypothesis)")
    else:
        st.subheader("Standard Log Entry")


    with st.form(key='quick_log_form', clear_on_submit=True):
        st.subheader("1. Incident Details")
        
        col_dt, col_t, col_duration = st.columns(3)
        with col_dt:
            incident_date = st.date_input("Date of Incident", datetime.now().date())
        with col_t:
            incident_time = st.time_input("Time of Incident", datetime.now().time().replace(second=0, microsecond=0))
        with col_duration:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=5)

        col_loc, col_staff = st.columns(2)
        with col_loc:
            location = st.text_input("Location", value="Classroom / Yard / Hallway")
        with col_staff:
            staff_list = [s['name'] for s in MOCK_STAFF]
            staff_involved = st.selectbox("Staff Recording/Witnessing", options=staff_list, index=staff_list.index(get_staff_name(next(s['id'] for s in MOCK_STAFF if s['role'] == current_role))))

        st.subheader("2. ABCH Log")
        
        behavior = st.selectbox("Observed Behavior (B)", options=BEHAVIORS_FBA)
        antecedent = st.selectbox("Antecedent (A): What happened immediately before?", options=CONTEXTS)
        consequence = st.text_area("Consequence (C): What happened immediately after?", height=100, placeholder="E.g., Redirected to task, sent to time-out, peer was removed.")
        hypothesis = st.selectbox("Hypothesis (H): Potential Motivation/Function", options=MOTIVATIONS)

        st.subheader("3. De-escalation & Context")

        wot_start = st.select_slider("Window of Tolerance (WOT) - Start", options=WOT_LABELS, value='Alert')
        wot_end = st.select_slider("Window of Tolerance (WOT) - End", options=WOT_LABELS, value='High Alert')
        
        staff_response = st.text_area("Staff Response/De-escalation Steps Taken", height=150, placeholder="Describe the steps taken to de-escalate or respond to the behaviour.")

        # --- Outcomes Section (More relevant for critical incidents) ---
        st.subheader("4. Outcomes/Mandatory Reporting Flags")
        
        col_o1, col_o2, col_o3 = st.columns(3)
        
        with col_o1:
            st.checkbox("Student sent home/Suspension", key='o_a_send_home')
            st.checkbox("Student left immediate area (Elopement)", key='o_b_left_area')
        with col_o2:
            st.checkbox("Assault/Physical Aggression on Peer", key='o_c_assault')
            st.checkbox("Property Damage (Significant)", key='o_d_property_damage')
        with col_o3:
            st.checkbox("Staff Injury requiring First Aid", key='o_e_staff_injury')
            st.checkbox("SAPOL Callout", key='o_f_sapol_callout')

        submitted = st.form_submit_button("Submit Incident Log")
        
        if submitted:
            # Simple data validation (Streamlit handles required field warnings implicitly)
            if not behavior or not antecedent:
                st.warning("Please select a Behavior and Antecedent.")
                return

            # Find staff ID from name
            staff_id = next(s['id'] for s in MOCK_STAFF if s['name'] == staff_involved)
            
            # Create a new log entry
            new_log = {
                'log_id': str(uuid.uuid4()),
                'student_id': current_student['id'],
                'timestamp': datetime.combine(incident_date, incident_time),
                'date': incident_date,
                'time': incident_time,
                'staff_id': staff_id,
                'behavior': behavior,
                'antecedent': antecedent,
                'consequence': consequence,
                'motivation': hypothesis,
                'duration_min': duration,
                'wot_start': wot_start,
                'wot_end': wot_end,
                'is_critical': incident_type == 'critical' or st.session_state.get('o_a_send_home', False) or st.session_state.get('o_e_staff_injury', False) or st.session_state.get('o_f_sapol_callout', False),
                'notes': f"Staff Response: {staff_response}. Location: {location}",
                # Additional fields from section 4 can be stored here too, e.g., 'outcome_send_home': st.session_state.o_a_send_home
            }

            # Add to the DataFrame
            new_log_df = pd.DataFrame([new_log])
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_log_df], ignore_index=True)
            
            # Clear temporary session state flags after submission
            if 'incident_type' in st.session_state:
                del st.session_state.incident_type
            
            st.success(f"Incident Log recorded successfully for {current_student['name']}!")
            st.balloons()
            # Navigate back to staff area after submission
            navigate_to('staff_area', role=current_role)


def render_student_analysis(student, role):
    st.title(f"Analysis Dashboard: {student['name']}")
    st.subheader(f"Year {student['year']} | Support Tier {student['plan_tier']}")
    st.markdown("---")
    
    if st.button("← Back to Staff Dashboard"):
        navigate_to('staff_area', role=role)

    log_data = get_student_logs(student['id'])
    
    if log_data.empty:
        st.warning("No incident logs available for this student.")
        return

    # --- Metrics ---
    st.header("Key Metrics (Last 30 Days)")
    
    total_logs = len(log_data)
    critical_logs = log_data['is_critical'].sum()
    avg_duration = log_data['duration_min'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Logs", total_logs)
    col2.metric("Critical Incidents", critical_logs, delta=f"{critical_logs/total_logs:.1%}" if total_logs > 0 else None, delta_color="inverse")
    col3.metric("Avg. Duration (min)", f"{avg_duration:.1f}")
    
    # --- Data Visualizations ---
    
    st.header("Behaviour Patterns")
    
    # Chart 1: Behavior Frequency
    fig_behaviors = px.bar(
        log_data['behavior'].value_counts().reset_index(),
        x='behavior', y='count',
        title='Frequency of Observed Behaviours',
        labels={'behavior': 'Behaviour', 'count': 'Count'},
        color='behavior'
    )
    st.plotly_chart(fig_behaviors, use_container_width=True)
    
    # Chart 2: Motivation Hypothesis
    fig_motivation = px.pie(
        log_data['motivation'].value_counts().reset_index(),
        names='motivation', values='count',
        title='Hypothesized Motivation/Function of Behaviour',
    )
    st.plotly_chart(fig_motivation, use_container_width=True)

    # --- Raw Data ---
    st.header("Raw Incident Log History")
    log_data_display = log_data.copy()
    log_data_display['Staff'] = log_data_display['staff_id'].apply(get_staff_name)
    log_data_display['Date/Time'] = log_data_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(
        log_data_display[['Date/Time', 'behavior', 'antecedent', 'consequence', 'motivation', 'duration_min', 'wot_start', 'wot_end', 'is_critical', 'Staff']], 
        use_container_width=True,
        hide_index=True
    )

def render_staff_area(role):
    st.title(f"Behaviour Support Dashboard: {role_map.get(role, role)}")
    st.markdown("---")
    
    if st.button("← Back to Role Select"):
        navigate_to('landing')

    st.subheader("Action Center")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # ABCH Quick Log Button (Standard)
        if st.button("ABCH Quick Log", use_container_width=True, help="Record a non-critical behaviour incident (A-B-C-H model)."):
            # Navigate to quick_log with a standard/abch flag
            # Use the first student as a placeholder for the demo
            navigate_to('quick_log', student=st.session_state.students[0], role=role, incident_type='abch_quick')

    with col2:
        # Critical Incident Log Button (CRITICAL FIX APPLIED HERE)
        if st.button("Critical Incident", use_container_width=True, help="Record a high-level critical incident (requires ABCH completion)."):
            # Navigate to quick_log, but with the 'critical' flag
            # This flag is read in render_quick_log to show the alert.
            navigate_to('quick_log', student=st.session_state.students[0], role=role, incident_type='critical')

    with col3:
        # Student Analysis/Report Button
        if st.button("Student Analysis", use_container_width=True, help="Access detailed data visualizations and history for a student."):
            # Use the first student as a placeholder for the demo
            navigate_to('student_detail', student=st.session_state.students[0], role=role)

    with col4:
        # Placeholder for future action
        if st.button("Tiered Support Plans", use_container_width=True, disabled=True, help="Coming Soon: Manage and view student support plans."):
            pass # navigate_to('plans', role=role)

    st.markdown("---")
    st.subheader("Student List (Mock Data)")
    
    # Filter students relevant to the staff role (simple mock filter)
    if role != 'ADM':
        relevant_students = [s for s in st.session_state.students if s['role'] == role]
    else:
        relevant_students = st.session_state.students

    student_names = [s['name'] for s in relevant_students]
    
    if student_names:
        selected_student_name = st.selectbox(f"Select Student for Action (Currently focused on {st.session_state.student['name'] if st.session_state.student else 'None'})", 
                                             options=student_names)
        
        selected_student = next(s for s in relevant_students if s['name'] == selected_student_name)
        
        # This button lets the user switch the focus for the action center buttons above
        if st.button(f"Set Focus to {selected_student_name}"):
            st.session_state.student = selected_student
            st.success(f"Action Center focus set to {selected_student_name}.")
            st.rerun()

    
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
            # Should not happen, but return to landing if role is somehow lost
            navigate_to('landing')

if __name__ == '__main__':
    main()
