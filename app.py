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
        background-color: #334155;
        color: #F1F5F9;
        border: 1px solid #475569;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    /* Primary buttons (Submit/Save) */
    .stButton>button:first-child {
        background-color: #6366F1; /* Indigo */
        color: #FFFFFF;
    }
    
    /* Sidebar Links/Navigation */
    .sidebar .stButton>button {
        background-color: transparent;
        color: #94A3B8;
        border: none;
        text-align: left;
    }
    .sidebar .stButton>button:hover {
        background-color: #334155;
        color: #F1F5F9;
    }
    
    /* Info/Success Alerts */
    div[data-testid="stAlert"] { border-radius: 8px; }
    div[data-testid="stAlert"].stAlert-info { background-color: #1E40AF; border-left: 5px solid #60A5FA; } /* Blue */
    div[data-testid="stAlert"].stAlert-success { background-color: #166534; border-left: 5px solid #4ADE80; } /* Green */

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

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out of Seat/Area', 'Disruption (Noise/Voice)', 'Aggression (Staff)']
FUNCTION_OF_BEHAVIOR = ['Attention (Peer)', 'Attention (Staff)', 'Tangible (Access to Item/Activity)', 'Escape (Task/Demand)', 'Sensory/Automatic']
SETTINGS = ['Classroom (Main Activity)', 'Transition (Between Activities)', 'Recess/Break', 'Lunchtime', 'Outdoor Area', 'Bus/Transport', 'Specialist Lesson', 'Other']
TRIGGERS = ['Demand/Instruction Given', 'Peer Interaction', 'Change in Schedule', 'Transition Time', 'Access to Item Denied', 'Noise/Sensory Overload', 'Unstructured Time', 'Non-Compliance']
WOT_STATES = ['Calm', 'Agitated', 'Meltdown (Non-Critical)', 'Shutdown/Freeze']
RESPONSE_TYPES = ['Co-Regulation (Verbal)', 'Co-Regulation (Non-Verbal)', 'De-escalation Script', 'Physical Support/Intervention', 'Redirection', 'Ignoring', 'Proximity Control']


# --- Helper Functions ---

def get_active_staff():
    """Returns a list of active staff names for selection."""
    return sorted([s['name'] for s in MOCK_STAFF if s['active']])

def navigate_to(page, student=None, role=None):
    """Changes the application page and optionally sets student/role context."""
    if student:
        st.session_state.student = student
    if role:
        st.session_state.role = role
    st.session_state.page = page

def generate_mock_data():
    """Generates mock incident data for display and analysis."""
    # ... (function body remains the same as previous)
    # Placeholder for brevity, assuming existing mock data generation logic is still here
    
    data = []
    end_date = datetime.now()
    
    # Generate 100 mock incidents over the last 90 days
    for i in range(1, 101):
        incident_time = end_date - timedelta(days=random.randint(1, 90), 
                                             minutes=random.randint(1, 1440))
        
        behavior = random.choice(BEHAVIORS_FBA)
        setting = random.choice(SETTINGS)
        trigger = random.choice(TRIGGERS)
        
        # Ensure a critical incident happens occasionally
        is_critical = behavior in ['Aggression (Staff)', 'Self-Injurious Behaviour'] and random.random() < 0.2
        
        entry = {
            'id': str(uuid.uuid4()),
            'date': incident_time.date(),
            'time': incident_time.time(),
            'timestamp': incident_time,
            'log_staff': random.choice(get_active_staff()),
            'involved_staff': random.choice(get_active_staff()),
            'student_id': st.session_state.student['id'],
            'student_name': st.session_state.student['name'],
            'behavior': behavior,
            'function': random.choice(FUNCTION_OF_BEHAVIOR),
            'setting': setting,
            'trigger': trigger,
            'intensity': random.choice(['Low', 'Medium', 'High']),
            'duration_min': random.randint(1, 30),
            'wot_state': random.choice(WOT_STATES),
            'response': random.choice(RESPONSE_TYPES),
            'outcome_send_home': 'Send Home' in random.sample(['None', 'Send Home', 'None'], 1),
            'outcome_staff_injury': 'ED155: Staff Injury' in random.sample(['None', 'None', 'ED155: Staff Injury'], 1) and random.random() < 0.1,
            'is_critical': is_critical,
            'sapol_report': 'REP-' + str(random.randint(1000, 9999)) if is_critical else None
        }
        data.append(entry)
        
    return pd.DataFrame(data)

# --- State Initialization ---

def initialize_state():
    """Sets up the initial session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'data' not in st.session_state or st.session_state.student:
        # Load/Generate data only when a student is selected or on first run
        st.session_state.data = None 

# --- Page Render Functions ---

# ... (render_landing_page, render_staff_area, render_student_analysis remain the same as previous)

def render_landing_page():
    """Renders the initial landing and login simulation page."""
    st.title("Student Behaviour Support & Data Tool")
    st.markdown("---")
    
    st.subheader("Simulated Staff Login")
    
    # Role selection for context and access
    role_options = ['Junior Primary (JP)', 'Primary (PY)', 'Senior Years (SY)', 'Administration (ADM)']
    selected_role_str = st.selectbox(
        "Select your Staff Role to proceed:",
        options=role_options,
        index=None,
        key='login_role'
    )
    
    if st.button("Access Dashboard", use_container_width=True):
        if selected_role_str:
            role_code = selected_role_str.split('(')[1].replace(')', '')
            navigate_to('staff_area', role=role_code)
        else:
            st.error("Please select a role.")
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


def render_staff_area():
    """Renders the staff dashboard, student list, and navigation."""
    st.title(f"Staff Dashboard ({st.session_state.role})")
    st.markdown("---")
    
    st.subheader("Select Student Profile")
    
    # Mock Student List
    mock_students = [
        {'id': 'S1001', 'name': 'Izack N.', 'class': 'PY-4', 'plan_status': 'Active BSP'},
        {'id': 'S1002', 'name': 'Layla D.', 'class': 'JP-2', 'plan_status': 'Draft BSP'},
        {'id': 'S1003', 'name': 'Ethan K.', 'class': 'SY-9', 'plan_status': 'Review Needed'},
    ]
    
    # Display student cards/buttons
    for student in mock_students:
        col1, col2, col3 = st.columns([0.2, 0.6, 0.2])
        
        col1.write(f"**ID:** {student['id']}")
        col2.write(f"**{student['name']}** - {student['class']} ({student['plan_status']})")
        
        if col3.button("View Profile", key=f"view_{student['id']}", use_container_width=True):
            navigate_to('student_detail', student=student, role=st.session_state.role)

    st.markdown("---")
    if st.button("Sign Out", type="secondary"):
        navigate_to('landing', role=None)

def render_student_analysis(student, role):
    """Renders the detailed analysis page for a selected student."""
    
    # Load or generate mock data for the selected student
    if st.session_state.get('data') is None or st.session_state.student['id'] != student['id']:
        st.session_state.student = student
        st.session_state.data = generate_mock_data()
        
    df = st.session_state.data
    
    st.title(f"Behaviour Analysis: {student['name']}")
    st.subheader(f"{student['class']} | Status: {student['plan_status']}")
    st.markdown("---")

    # Navigation buttons
    col_nav_1, col_nav_2, col_nav_3 = st.columns(3)
    if col_nav_1.button("Log New Incident", use_container_width=True, type="primary"):
        navigate_to('quick_log', student=student, role=role)
    if col_nav_2.button("View Raw Log Data", use_container_width=True):
        st.session_state.view_raw = not st.session_state.get('view_raw', False)
    if col_nav_3.button("Back to Staff Dashboard", use_container_width=True):
        navigate_to('staff_area', role=role)
        
    st.markdown("---")
    
    # --- Data Visualization and Analysis ---
    
    # 1. Total Incidents
    st.metric(label="Total Incidents (Last 90 Days)", value=len(df))

    # 2. Behavior Frequency (Top 5)
    st.subheader("Top 5 Behaviours by Frequency")
    behavior_counts = df['behavior'].value_counts().reset_index()
    behavior_counts.columns = ['Behavior', 'Count']
    fig_behavior = px.bar(
        behavior_counts.head(5), 
        x='Behavior', 
        y='Count', 
        title='Most Frequent Behaviours',
        color='Count',
        color_continuous_scale='Plasma'
    )
    st.plotly_chart(fig_behavior, use_container_width=True)

    # 3. Function/Setting Matrix (Example of deeper analysis)
    st.subheader("Function of Behavior by Setting")
    pivot_table = df.groupby(['setting', 'function']).size().unstack(fill_value=0)
    st.dataframe(pivot_table.style.background_gradient(cmap='Blues'), use_container_width=True)
    
    # 4. Critical Incident Summary (Optional, simplified for this example)
    critical_count = df[df['is_critical'] == True].shape[0]
    if critical_count > 0:
        st.error(f"⚠️ **{critical_count} Critical Incidents Logged** - Immediate review required.", icon="🚨")
    else:
        st.success("No Critical Incidents logged in the last 90 days.")

    # Show raw data if requested
    if st.session_state.get('view_raw', False):
        st.markdown("---")
        st.subheader("Raw Incident Data")
        st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)


def render_quick_log(role, student):
    """Renders the detailed Quick ABCH Incident Log form."""
    st.title(f"Quick Incident Log: {student['name']}")
    st.subheader(f"Logged by: {role}")
    st.markdown("---")

    # Function to handle form submission
    def submit_log():
        log_entry = {
            'id': str(uuid.uuid4()),
            'date': st.session_state.pre_a_date,
            'time': st.session_state.pre_a_time,
            'timestamp': datetime.combine(st.session_state.pre_a_date, st.session_state.pre_a_time),
            'log_staff': get_active_staff()[0], # Assumes the current user is the first in the list
            'involved_staff': st.session_state.involved_staff,
            'student_id': student['id'],
            'student_name': student['name'],
            'behavior': st.session_state.pre_a_behaviors[0] if st.session_state.pre_a_behaviors else 'Other',
            'setting': st.session_state.pre_b_setting,
            'trigger': st.session_state.pre_c_trigger,
            'intensity': st.session_state.pre_d_intensity,
            'duration_min': st.session_state.pre_e_duration,
            'wot_state': st.session_state.post_g_wot,
            'response': st.session_state.post_h_response,
            'function': st.session_state.post_f_function,
            'context': st.session_state.context_notes,
            'how_to_respond': st.session_state.how_to_respond_plan,
            'follow_up_plan': st.session_state.follow_up_plan,
            
            # Outcome mapping (Simplified for Quick Log)
            'outcome_send_home': st.session_state.get('o_a_send_home', False),
            'outcome_leave_area': st.session_state.get('o_b_left_area', False),
            'outcome_assault': st.session_state.get('o_c_assault', False),
            'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
            'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
            'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
            'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False),
            'is_critical': st.session_state.get('o_c_assault', False) or st.session_state.get('o_e_staff_injury', False)
        }
        
        # In a real app, this is where you would save to the database (e.g., Firestore)
        if st.session_state.data is not None:
            # Add the new log entry to the mock data for immediate display
            new_df = pd.DataFrame([log_entry])
            st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)

        st.success("Incident Logged Successfully!")
        # Navigate back to student analysis after successful log
        navigate_to('student_detail', student=student, role=role)

    # --- Incident Log Form ---
    with st.form("quick_incident_log", clear_on_submit=False):
        
        # --- 1. INCIDENT DETAILS (When & Who) ---
        st.subheader("1. Incident Details (A - Before)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.date_input("Date of Incident", value=datetime.now().date(), key='pre_a_date')
            st.selectbox("Involved Staff/Reporting Staff", options=get_active_staff(), key='involved_staff', index=get_active_staff().index('Emily Jones (JP)'))
            
        with col2:
            st.time_input("Time of Incident", value=datetime.now().time().replace(second=0, microsecond=0), step=60, key='pre_a_time')
            # Selectbox for main behavior - simplified for quick log
            st.selectbox("Main Behaviour Observed", options=BEHAVIORS_FBA, key='pre_a_behaviors', index=BEHAVIORS_FBA.index('Verbal Refusal'))
            
        st.markdown("---")
        
        # --- 2. CONTEXT (B & C) ---
        st.subheader("2. Context (B - Setting, C - Trigger)")
        col_context_1, col_context_2 = st.columns(2)
        
        with col_context_1:
            st.selectbox("Setting", options=SETTINGS, key='pre_b_setting', index=SETTINGS.index('Classroom (Main Activity)'))
            
        with col_context_2:
            st.selectbox("Trigger", options=TRIGGERS, key='pre_c_trigger', index=TRIGGERS.index('Demand/Instruction Given'))
            
        st.text_area("Detailed Context/Antecedent Notes", key='context_notes', height=100, placeholder="What happened immediately before the behaviour?")
        st.markdown("---")

        # --- 3. BEHAVIOUR DETAILS (D & E) ---
        st.subheader("3. Behaviour Details (D - Intensity, E - Duration)")
        col_details_1, col_details_2 = st.columns(2)
        
        with col_details_1:
            st.selectbox("Intensity", options=['Low', 'Medium', 'High'], key='pre_d_intensity', index=0)
        
        with col_details_2:
            st.number_input("Duration (Minutes)", min_value=1, max_value=120, key='pre_e_duration', value=5)

        st.markdown("---")
        
        # --- 4. FUNCTION & WINDOW OF TOLERANCE (F & G) ---
        st.subheader("4. Function & Student State (F - Function, G - WOT)")
        col_fg_1, col_fg_2 = st.columns(2)
        
        with col_fg_1:
            st.selectbox("Hypothesised Function of Behavior", options=FUNCTION_OF_BEHAVIOR, key='post_f_function', index=0)
            
        with col_fg_2:
            st.selectbox("Student Window of Tolerance (WOT) State", options=WOT_STATES, key='post_g_wot', index=1)
            
        st.markdown("---")

        # --- 5. RESPONSE (H) ---
        st.subheader("5. Staff Response (H)")
        st.selectbox("Staff Response Type Used", options=RESPONSE_TYPES, key='post_h_response', index=RESPONSE_TYPES.index('Co-Regulation (Verbal)'))
        st.text_area("How to Respond Plan (Specific Action Taken)", key='how_to_respond_plan', height=100, placeholder="e.g., Used 3-step calm-down sequence; Provided a choice between Task A and Task B; Escorted student to safe space.")
        
        st.markdown("---")

        # --- 6. OUTCOMES ---
        st.subheader("6. Outcomes & Follow-up")
        
        # Outcome Checkboxes (Quick Log version)
        col_outcomes_a, col_outcomes_b = st.columns(2)

        with col_outcomes_a:
            st.markdown("**Initial Outcomes**")
            st.checkbox("A. Sent Home / Excluded", key='o_a_send_home')
            st.checkbox("B. Student Left Supervised Area / School Grounds", key='o_b_left_area')
            
        with col_outcomes_b:
            st.markdown("**Major/External Outcomes**")
            st.checkbox("C. Assault (Student or Staff)", key='o_c_assault')
            st.checkbox("D. Property Damage", key='o_d_property_damage')
            st.checkbox("E. ED155: Staff Injury (submit with report)", key='o_e_staff_injury')
            st.checkbox("F. SAPOL Callout / Involvement", key='o_f_sapol_callout')
            st.checkbox("R. SA Ambulance Services Callout", key='o_r_call_out_amb')
            
        st.markdown("---")
        
        # --- Follow-up Plan ---
        st.subheader("Follow-up Plan")
        st.text_area(
            "What immediate follow-up actions, restorative sessions, or TAC/Case Review meetings are required?",
            key='follow_up_plan',
            height=100,
            placeholder="e.g., Follow up with student tomorrow morning; Schedule a restorative conversation with the peer involved; TAC meeting to be held on [Date]."
        )
        
        st.markdown("---")
        
        # Submit Button
        if st.form_submit_button("Submit Quick Log", use_container_width=True):
            submit_log()

    st.markdown("---")
    if st.button("Cancel and Return to Profile", type="secondary"):
        navigate_to('student_detail', student=student, role=role)

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
            st.error("Role context missing. Returning to landing.")
            navigate_to('landing')
    
if __name__ == '__main__':
    main()
