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
    div[data-testid="stSelectbox"] > div > div > div > input {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #4C51BF; /* Indigo */
        color: #F1F5F9;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    div.stButton > button:hover {
        background-color: #6366F1;
    }
    .quick-log-button {
        background-color: #10B981 !important; /* Emerald */
    }
    .quick-log-button:hover {
        background-color: #34D399 !important;
    }

    /* Expander / Summary Details */
    .streamlit-expanderHeader {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 10px;
        color: #94A3B8;
        border: 1px solid #334155;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] > div {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #6366F1;
    }

    /* Info Alerts */
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

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

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst - General', 'Non-Compliance', 'Disrespectful Language']
LOCATIONS = ['Classroom', 'Playground', 'Library', 'Gym/Hall', 'Specialist Room', 'Outside Yard', 'Office Area', 'Bus/Transition']
CONSEQUENCES = ['Verbal Redirection', 'Time Out (In-Class)', 'Time Out (Withdrawal)', 'Loss of Privilege', 'Restorative Chat', 'Parent Contact', 'Referral to Leadership', 'No Consequence Applied']

# Mock student data (including a focus student for analysis)
MOCK_STUDENTS = [
    {'id': 'st_1', 'name': 'Izack N.', 'year': 9, 'plan': 'BSP-Tier 3', 'status': 'Active'},
    {'id': 'st_2', 'name': 'Chloe T.', 'year': 8, 'plan': 'BSP-Tier 2', 'status': 'Active'},
    {'id': 'st_3', 'name': 'Ryan P.', 'year': 10, 'plan': 'None', 'status': 'Active'},
    {'id': 'st_4', 'name': 'Mia V.', 'year': 7, 'plan': 'None', 'status': 'Active'},
]

# Mock incident data for the focus student (Izack N.)
def generate_mock_data(student_id):
    """Generates mock incident data for a student."""
    if student_id != 'st_1':
        return pd.DataFrame()

    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    current_date = start_date

    while current_date <= end_date:
        # Generate 0 to 3 incidents per day
        num_incidents = np.random.choice([0, 1, 2, 3], p=[0.7, 0.15, 0.1, 0.05])
        
        for _ in range(num_incidents):
            incident_time = datetime.combine(current_date.date(), time(random.randint(9, 15), random.randint(0, 59)))
            staff_id = random.choice([s['id'] for s in MOCK_STAFF if not s['special']])
            
            # Select 1 or 2 behaviours
            behaviors = random.sample(BEHAVIORS_FBA, k=random.randint(1, 2))
            
            data.append({
                'id': str(uuid.uuid4()),
                'student_id': student_id,
                'date_time': incident_time,
                'location': random.choice(LOCATIONS),
                'staff_id': staff_id,
                'behaviors': ', '.join(behaviors),
                'antecedent': random.choice(['Demand made', 'Transition', 'Peer conflict', 'Task too difficult']),
                'consequence': random.choice(CONSEQUENCES),
                'intensity': random.choice(['Low', 'Medium', 'High']),
                'duration_min': random.randint(1, 20),
                'is_abch_completed': random.choice([True, False]),
                'outcome_send_home': random.choice([True, False]),
                'outcome_assault': random.choice([True, False]),
            })
        
        current_date += timedelta(days=1)
        
    df = pd.DataFrame(data)
    df['date'] = df['date_time'].dt.date
    df = df.sort_values(by='date_time', ascending=False).reset_index(drop=True)
    return df

# --- Helper Functions ---

def get_active_staff(include_special=False):
    """Returns a list of staff names for dropdowns."""
    return [s for s in MOCK_STAFF if s['active'] and (include_special or not s['special'])]

def get_staff_name_from_id(staff_id):
    """Looks up staff name from ID."""
    try:
        return next(s['name'] for s in MOCK_STAFF if s['id'] == staff_id)
    except StopIteration:
        return f"Unknown Staff ({staff_id})"

def initialize_state():
    """Initializes Streamlit session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'incident_data' not in st.session_state:
        # Load mock data for the focus student
        st.session_state.incident_data = generate_mock_data('st_1')

def navigate_to(page, **kwargs):
    """Changes the page view and updates state context."""
    st.session_state.page = page
    if 'role' in kwargs:
        st.session_state.role = kwargs['role']
    if 'student' in kwargs:
        st.session_state.student = kwargs['student']
    
    # Rerun the app to reflect the page change
    st.rerun()

def save_log_to_db(preliminary_data):
    """
    MOCK function to save the completed log to the database/session state.
    In a real app, this would be an async DB write.
    """
    
    # 1. Capture the remaining data from the advanced ABCH form (session state)
    refined_wot = st.session_state.get('wot_refine', 'No additional context provided.')
    final_context = st.session_state.get('context_refine', 'No additional context provided.')
    how_to_respond_plan = st.session_state.get('how_to_respond_plan', 'No plan developed yet.')
    
    final_log_entry = preliminary_data.copy()
    final_log_entry.update({
        'is_abch_completed': True,
        'window_of_tolerance': refined_wot,
        'context': final_context,
        'how_to_respond': how_to_respond_plan,
        # Outcomes mapping here (using keys from the original quick log context)
        'outcome_send_home': st.session_state.get('o_a_send_home', False),
        'outcome_leave_area': st.session_state.get('o_b_left_area', False),
        'outcome_assault': st.session_state.get('o_c_assault', False),
        'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
        'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
        'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
        'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False) or st.session_state.get('o_j_first_aid_amb', False),
    })
    
    # Clean up temporary session state data after final save
    keys_to_delete = ['wot_refine', 'context_refine', 'how_to_respond_plan',
                      'o_a_send_home', 'o_b_left_area', 'o_c_assault', 'o_d_property_damage', 
                      'o_e_staff_injury', 'o_f_sapol_callout', 'o_r_call_out_amb', 'o_j_first_aid_amb']
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
            
    # 2. Add to mock data
    new_df = pd.DataFrame([final_log_entry])
    st.session_state.incident_data = pd.concat([new_df, st.session_state.incident_data], ignore_index=True)
    st.session_state.incident_data['date'] = st.session_state.incident_data['date_time'].dt.date
    
    st.success("✅ Critical Incident Log Saved Successfully!")
    st.info(f"Returning to Dashboard in 3 seconds.")
    # Use a simple rerun instead of time.sleep
    navigate_to('staff_area', role=st.session_state.role)


# --- Page Rendering Functions ---

def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Portal")
    st.subheader("Select your user role to continue")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Primary Years Staff (PY)", use_container_width=True):
            navigate_to('staff_area', role='PY')
    with col2:
        if st.button("Junior Primary Staff (JP)", use_container_width=True):
            navigate_to('staff_area', role='JP')
    with col3:
        if st.button("Admin / Leadership (ADM)", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application provides real-time data analysis and structured logging tools for proactive behaviour support.")


def render_staff_area(current_role):
    """Renders the main staff dashboard."""
    
    st.title(f"Staff Dashboard: {current_role} Area")
    st.subheader("Student Quick Select")

    # Filter students based on role (simple mock filter)
    filtered_students = MOCK_STUDENTS
    if current_role in ['JP', 'PY']:
        # JP/PY staff only see students in their 'area'
        filtered_students = [s for s in MOCK_STUDENTS if s['year'] <= 8 and current_role == 'JP' or s['year'] > 8 and current_role == 'PY']
    
    student_options = {s['name']: s['id'] for s in filtered_students}
    
    if not student_options:
        st.warning("No students assigned to your area.")
        return

    selected_name = st.selectbox(
        "Select Student for Action or Analysis",
        options=list(student_options.keys()),
        index=0,
        placeholder="Select a student..."
    )
    
    selected_id = student_options.get(selected_name)
    selected_student = next((s for s in MOCK_STUDENTS if s['id'] == selected_id), None)
    
    if selected_student:
        st.markdown(f"**Selected Student:** {selected_student['name']} (Year {selected_student['year']})")
        st.markdown(f"**Support Plan:** :blue[{selected_student['plan']}]")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Review Student Analysis", use_container_width=True):
                navigate_to('student_detail', student=selected_student, role=current_role)
        with col2:
            if st.button("Start Quick Incident Log", use_container_width=True, help="Record new incident data immediately"):
                navigate_to('quick_log', student=selected_student, role=current_role)

    st.markdown("---")
    st.caption("Admin/Leadership: All students are visible for a full system overview.")

def render_student_analysis(student, current_role):
    """Renders the detailed analysis page for a selected student."""
    st.title(f"Data Analysis: {student['name']} (Year {student['year']})")
    
    st.sidebar.button("← Back to Dashboard", on_click=navigate_to, args=('staff_area',), kwargs={'role':current_role})
    
    df = st.session_state.incident_data
    
    if df.empty:
        st.info("No incident data available for this student.")
        return

    # --- Key Metrics ---
    col1, col2, col3 = st.columns(3)
    total_incidents = len(df)
    incidents_90_days = len(df[df['date_time'] > (datetime.now() - timedelta(days=90))])
    avg_duration = df['duration_min'].mean().round(1) if total_incidents > 0 else 0
    
    col1.metric("Total Incidents (90 Days)", incidents_90_days)
    col2.metric("Average Duration (min)", avg_duration)
    col3.metric("Most Frequent Behavior", df['behaviors'].str.split(', ').explode().mode().iloc[0] if not df['behaviors'].empty else 'N/A')

    st.markdown("---")

    # --- Charts ---
    st.subheader("Incident Trends and Patterns")

    # 1. Frequency Trend over time
    incidents_over_time = df.groupby('date').size().reset_index(name='Count')
    fig_trend = px.line(incidents_over_time, x='date', y='Count', title='Daily Incident Frequency (Last 90 Days)', 
                        labels={'date':'Date', 'Count':'Incidents'}, template="plotly_dark")
    st.plotly_chart(fig_trend, use_container_width=True)

    col_loc, col_beh = st.columns(2)
    
    # 2. Location Distribution (Pie Chart)
    location_counts = df['location'].value_counts().reset_index(name='Count')
    fig_loc = px.pie(location_counts, names='location', values='Count', title='Incidents by Location', 
                     template="plotly_dark")
    col_loc.plotly_chart(fig_loc, use_container_width=True)

    # 3. Behavior Frequency (Bar Chart)
    behavior_counts = df['behaviors'].str.split(', ').explode().value_counts().reset_index(name='Count')
    behavior_counts.columns = ['Behavior', 'Count']
    fig_beh = px.bar(behavior_counts.head(5), x='Behavior', y='Count', title='Top 5 Behaviors', 
                     template="plotly_dark")
    col_beh.plotly_chart(fig_beh, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Incident Log History")
    
    # Display log table
    display_df = df[['date_time', 'behaviors', 'antecedent', 'consequence', 'location', 'intensity', 'duration_min']].copy()
    display_df.columns = ['Time', 'Behaviors', 'Antecedent', 'Consequence', 'Location', 'Intensity', 'Duration (min)']
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_quick_log(current_role, student):
    """Renders the detailed ABCH Quick Log form."""
    
    st.title(f"Quick Incident Log: :blue[{student['name']} (Year {student['year']})]")
    st.sidebar.button("← Back to Dashboard", on_click=navigate_to, args=('staff_area',), kwargs={'role':current_role})

    # Initialize preliminary log data structure
    preliminary_log_data = {
        'id': str(uuid.uuid4()),
        'student_id': student['id'],
        'staff_id': None, # To be filled by the form
        'date_time': None, # To be filled by the form
        'location': None,
        'behaviors': [],
        'antecedent': None,
        'consequence': None,
        'intensity': None,
        'duration_min': 0,
    }

    with st.form("abch_quick_log", clear_on_submit=False):
        
        # --- Section 1: Initial Context (Required for all logs) ---
        st.subheader("1. Initial Incident Context (A-B-C)")
        
        col_staff, col_date, col_time = st.columns([2, 1, 1])
        
        # Staff logged in is pre-selected for convenience
        staff_options = get_active_staff(include_special=True)
        staff_names = [s['name'] for s in staff_options]
        default_staff_index = next((i for i, s in enumerate(staff_options) if s['role'] == current_role), 0)
        
        selected_staff_name = col_staff.selectbox(
            "Staff Logging Incident",
            options=staff_names,
            index=default_staff_index,
            key='log_staff'
        )
        preliminary_log_data['staff_id'] = next(s['id'] for s in staff_options if s['name'] == selected_staff_name)
        
        incident_date = col_date.date_input("Date", value=datetime.now().date(), key='log_date')
        incident_time = col_time.time_input("Time", value=datetime.now().time(), step=timedelta(minutes=1), key='log_time')
        
        # Combine date and time
        preliminary_log_data['date_time'] = datetime.combine(incident_date, incident_time)
        
        st.markdown("---")
        
        col_loc, col_int = st.columns(2)
        preliminary_log_data['location'] = col_loc.selectbox("Location", options=LOCATIONS, key='log_loc')
        
        # Behavior (B)
        behaviors_selected = st.multiselect("Behaviour(s) Observed (B)", options=BEHAVIORS_FBA, max_selections=3, key='log_behaviors')
        preliminary_log_data['behaviors'] = behaviors_selected
        
        # Antecedent (A)
        preliminary_log_data['antecedent'] = st.text_area(
            "Antecedent / Trigger (A)", 
            placeholder="What happened immediately before the behaviour? (e.g., Peer proximity, demand made, non-preferred task)",
            key='log_antecedent'
        )
        
        # Consequence (C)
        consequence_applied = st.multiselect(
            "Immediate Consequence / Response (C)", 
            options=CONSEQUENCES,
            max_selections=2,
            key='log_consequence'
        )
        preliminary_log_data['consequence'] = consequence_applied
        
        # Intensity and Duration
        preliminary_log_data['intensity'] = col_int.select_one("Intensity Level", options=['Low', 'Medium', 'High', 'Critical'], key='log_intensity', index=2 if 'Critical' in BEHAVIORS_FBA else 1)
        preliminary_log_data['duration_min'] = st.slider("Duration of Incident (minutes)", 0, 60, 5, key='log_duration')
        
        # --- Section 2: ABCH Details (Optional but Recommended) ---
        st.markdown("---")
        st.subheader("2. Detailed ABCH / Critical Incident Context (Refinement)")
        
        # Refined Antecedent / Window of Tolerance (WOT)
        with st.expander("Window of Tolerance (WOT) Refinement"):
            st.markdown("Use this to describe the student's **emotional state** leading up to the incident.")
            st.text_area(
                "WOT Status:",
                placeholder="Was the student hyper-aroused (anxious, angry), hypo-aroused (withdrawn, low energy), or regulated? What signs were present?",
                key='wot_refine'
            )
            
        # Refined Context
        with st.expander("Detailed Context / Function of Behaviour"):
            st.markdown("Use this for complex factors, sensory information, or to hypothesize the function (Why did they do it?).")
            st.text_area(
                "Context Details:",
                placeholder="e.g., Sensory overload in gym; seeking adult attention; escape from writing task.",
                key='context_refine'
            )
        
        # Forward Planning
        with st.expander("Future Plan / 'How To Respond'"):
            st.markdown("What adjustments, supports, or responses are needed next time?")
            st.text_area(
                "Proactive Response Plan:",
                placeholder="e.g., Provide noise-cancelling headphones for gym; use a visual timetable for transitions; provide 'break' card.",
                key='how_to_respond_plan'
            )
            
        # --- Section 3: Outcomes and Formal Actions ---
        st.markdown("---")
        st.subheader("3. Formal Outcomes and Actions")
        st.markdown("**Check all relevant outcomes.**")
        
        col_out1, col_out2, col_out3 = st.columns(3)
        
        # Simple outcomes derived from the original ABCH log structure
        col_out1.checkbox("A - Student Sent Home", key='o_a_send_home')
        col_out1.checkbox("B - Student Left Supervised Area/Eloped", key='o_b_left_area')
        
        col_out2.checkbox("C - Assault/Serious Aggression", key='o_c_assault')
        col_out2.checkbox("D - Property Damage", key='o_d_property_damage')
        
        col_out3.checkbox("E - Staff Injury (ED155 required)", key='o_e_staff_injury')
        col_out3.checkbox("F - SAPOL Callout", key='o_f_sapol_callout')
        col_out3.checkbox("Ambulance Callout / Student Injury", key='o_r_call_out_amb')

        st.markdown("---")
        
        # --- Form Submission ---
        col_submit, col_cancel = st.columns([3, 1])
        
        submitted = col_submit.form_submit_button(
            "💾 Finalize and Save Critical Incident Log", 
            use_container_width=True, 
            type="primary"
        )
        
        if col_cancel.button("Cancel & Discard", use_container_width=True):
            st.warning("Incident log discarded. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)
            
        if submitted:
            if not preliminary_log_data['behaviors']:
                st.error("Please select at least one Behaviour Observed (B) before saving.")
            elif not preliminary_log_data['antecedent']:
                st.error("Please provide details for the Antecedent / Trigger (A).")
            else:
                save_log_to_db(preliminary_log_data)


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
            navigate_to('landing')

if __name__ == '__main__':
    main()
