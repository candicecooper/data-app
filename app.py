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
    .st-emotion-cache-1c9v605 { /* stSelectbox input area */
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0F172A; /* Darker background */
        color: #F1F5F9; /* Light text */
        border: 2px solid #3B82F6; /* Primary color border */
        border-radius: 12px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #3B82F6; /* Primary color hover */
        color: white;
        border-color: #3B82F6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Primary Button - used for major actions like 'Finalize' */
    .st-emotion-cache-5rimss { /* Target the primary button wrapper */
        background-color: #16A34A; /* Green for Success/Finalize */
        color: white;
    }
    .st-emotion-cache-5rimss:hover {
        background-color: #22C55E;
        box-shadow: 0 4px 15px rgba(22, 163, 74, 0.5);
    }
    
    /* DataFrame/Table styling */
    .stDataFrame { border-radius: 12px; }
    .st-emotion-cache-1n1v0tx { /* Table header background */
        background-color: #334155; 
        color: #F1F5F9;
    }

    /* Expander styling */
    .stExpander {
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 10px;
        background-color: #1E293B;
    }

    /* Metric/KPI Box */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    .st-emotion-cache-1ekfxxs { /* Metric value */
        color: #60A5FA !important; /* Blue for key metrics */
    }

    /* Custom styles for the Narrative Table */
    .narrative-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
        border-radius: 12px;
        background-color: #1E293B;
        border: 1px solid #334155;
    }
    .narrative-header, .narrative-row {
        display: flex;
        gap: 10px;
        padding: 5px 0;
        font-weight: 500;
        text-align: center;
    }
    .narrative-header {
        border-bottom: 2px solid #475569;
        margin-bottom: 10px;
    }
    .col-location { width: 25%; }
    .col-time { width: 10%; }
    .col-behaviour { width: 30%; }
    .col-consequence { width: 25%; }
    .col-function { width: 10%; }
    
    .narrative-row .stTextInput, .narrative-row .stTextArea, .narrative-row .stSelectbox {
        margin: 0;
        padding: 0;
    }
    .narrative-row .stTextInput input, .narrative-row .stTextArea textarea, .narrative-row .stSelectbox input {
        height: auto;
        min-height: 40px;
        padding: 8px;
    }
    
    </style>
    """
    , unsafe_allow_html=True)

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out of Seat/Area', 'Tantrum', 'Non-Compliance', 'Other (Specify)']
ANTECEDENTS_FBA = ['Transition/Change of Activity', 'Request to complete task', 'Request to stop activity', 'Peer conflict', 'Unstructured time (recess/lunch)', 'Non-preferred activity', 'Sensory overload', 'Illness/Fatigue', 'Other (Specify)']
FUNCTIONS_FBA = ['Access to Tangible/Activity (Attention)', 'Access to Sensory Input', 'Escape from Task/Demand', 'Escape from Social Interaction', 'Automatic/Self-Stimulatory', 'Communication Need', 'Unknown/Other']

MOCK_STUDENTS = [
    {'id': 's_izack', 'name': 'Izack N.', 'grade': '7', 'plan_status': 'Tier 3 (Active BSP)'},
    {'id': 's_aisha', 'name': 'Aisha K.', 'grade': '9', 'plan_status': 'Tier 2 (Check-in)'},
    {'id': 's_liam', 'name': 'Liam P.', 'grade': '6', 'plan_status': 'Tier 1 (Universal)'},
    {'id': 's_mia', 'name': 'Mia C.', 'grade': '8', 'plan_status': 'Tier 3 (Drafting BSP)'},
]

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
]

# --- Helper Functions ---

def navigate_to(page: str, **kwargs):
    """Sets the application page in session state."""
    st.session_state.page = page
    for key, value in kwargs.items():
        st.session_state[key] = value
    st.rerun()

def initialize_state():
    """Initializes necessary session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'log_data' not in st.session_state:
        st.session_state.log_data = []
    if 'current_quick_log' not in st.session_state:
        st.session_state.current_quick_log = None # Stores preliminary data for narrative/ABCH
    if 'critical_incident_steps' not in st.session_state:
        st.session_state.critical_incident_steps = []
    
    # Mock data initialization for the selected student
    if 'selected_student_data' not in st.session_state:
        st.session_state.selected_student_data = {
            's_izack': {'name': 'Izack N.', 'logs': []}
        }
    
    # Pre-populate some mock data for Izack (simulated quick logs)
    if not st.session_state.selected_student_data['s_izack']['logs']:
        mock_date = datetime.now().date()
        st.session_state.selected_student_data['s_izack']['logs'] = [
            {'id': str(uuid.uuid4()), 'date': mock_date, 'time': time(10, 15), 'location': 'Library', 'behaviour': 'Verbal Refusal', 'critical': False, 'duration': 5},
            {'id': str(uuid.uuid4()), 'date': mock_date, 'time': time(14, 00), 'location': 'Oval', 'behaviour': 'Aggression (Peer)', 'critical': True, 'duration': 20},
            {'id': str(uuid.uuid4()), 'date': mock_date - timedelta(days=1), 'time': time(9, 30), 'location': 'Classroom 7B', 'behaviour': 'Non-Compliance', 'critical': False, 'duration': 10},
        ]
        st.session_state.log_data.extend(st.session_state.selected_student_data['s_izack']['logs'])

def get_initial_narrative_step(preliminary_data):
    """Generates the initial step for the critical incident narrative from quick log data."""
    if not preliminary_data:
        return {'id': str(uuid.uuid4()), 'location': 'Unknown Area', 'time': datetime.now().time(), 'behaviour': '', 'consequence': '', 'function': FUNCTIONS_FBA[0]}
    
    # Use the quick log data to seed the first narrative step
    return {
        'id': str(uuid.uuid4()),
        'location': preliminary_data.get('location', 'Classroom'),
        'time': preliminary_data.get('start_time', datetime.now().time()),
        'behaviour': preliminary_data.get('behaviour', 'Incident Initiated'),
        'consequence': 'Staff intervened following initial quick log.',
        'function': FUNCTIONS_FBA[0] # Default function
    }

def calculate_incident_duration(steps):
    """Calculates the duration of the incident from the first step's time to the last step's time."""
    if not steps:
        return timedelta(0)
    
    # Convert all times to today's datetime for easy comparison/subtraction
    today = datetime.now().date()
    
    start_dt = datetime.combine(today, steps[0]['time'])
    end_dt = datetime.combine(today, steps[-1]['time'])
    
    # Handle overnight incidents (though typically quick logs are within a day)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        
    return end_dt - start_dt

# --- Page Render Functions ---

# ... (render_landing_page, render_staff_area, render_student_analysis, render_quick_log remain the same with the following crucial change in render_quick_log's button action) ...

def render_landing_page():
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")
    st.header("Welcome, Staff Member!")

    role = st.radio(
        "Select your role to continue:",
        ['ADM (Admin)', 'JP (Junior Primary)', 'SY (Senior Secondary)'],
        index=None,
        key='landing_role_select'
    )

    if st.button("Access Staff Area", type='primary', disabled=(role is None)):
        if role:
            navigate_to('staff_area', role=role.split(' ')[0])

def render_staff_area(role):
    st.title(f"Staff Dashboard: {role}")
    st.markdown("---")
    
    st.subheader("Select a Student")
    
    cols = st.columns(len(MOCK_STUDENTS))
    
    for i, student in enumerate(MOCK_STUDENTS):
        with cols[i]:
            if st.button(f"{student['name']} - {student['grade']} ({student['plan_status']})", key=f"select_student_{student['id']}"):
                navigate_to('student_detail', student=student['id'])

    st.markdown("---")
    st.subheader("Quick Log Incident Entry")
    if st.button("Start New Quick Log Entry", type='secondary'):
        navigate_to('quick_log', student=None) # Start log without pre-selected student

def render_student_analysis(student_id, role):
    student = next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)
    if not student:
        st.error("Student not found.")
        navigate_to('staff_area', role=role)
        return

    st.title(f"Analysis Dashboard for {student['name']}")
    st.subheader(f"Grade: {student['grade']} | Plan Status: {student['plan_status']}")
    st.markdown("---")

    # MOCK DATA VISUALIZATION SECTION
    st.header("Incident Summary (Mock Data)")
    
    student_data = st.session_state.selected_student_data.get(student_id, {'logs': []})
    df_logs = pd.DataFrame(student_data['logs'])

    if df_logs.empty:
        st.info("No incident logs available for this student yet.")
    else:
        # Mocking data analysis
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Incidents", len(df_logs))
        col2.metric("Critical Incidents", len(df_logs[df_logs['critical'] == True]))
        col3.metric("Average Duration", f"{df_logs['duration'].mean():.1f} min")

        # Mock Frequency Plot
        st.subheader("Behaviour Frequency by Type")
        behavior_counts = df_logs['behaviour'].value_counts().reset_index()
        behavior_counts.columns = ['Behaviour', 'Count']
        fig = px.bar(behavior_counts, x='Behaviour', y='Count', 
                     title='Frequency of Logged Behaviours', 
                     color='Behaviour', 
                     color_discrete_sequence=px.colors.sequential.Agsunset)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    if st.button(f"Log New Incident for {student['name']}"):
        navigate_to('quick_log', student=student_id)
    if st.button("Back to Staff Area", type='secondary'):
        navigate_to('staff_area', role=role)

def render_quick_log(role, student_id=None):
    if student_id:
        student = next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)
        student_name = student['name'] if student else "Unknown Student"
    else:
        student_name = st.selectbox("Select Student:", options=[s['name'] for s in MOCK_STUDENTS] + ["Other"], key='ql_student_select')
        student_id = next((s['id'] for s in MOCK_STUDENTS if s['name'] == student_name), None)

    st.title(f"ABCH Quick Log Entry for {student_name}")
    st.markdown("---")
    
    with st.form("quick_log_form", clear_on_submit=False):
        
        col_date, col_time = st.columns(2)
        with col_date:
            log_date = st.date_input("Date of Incident", datetime.now().date())
        with col_time:
            log_time = st.time_input("Start Time", datetime.now().time())
        
        staff_list = [s['name'] for s in MOCK_STAFF]
        staff_name = next((s['name'] for s in MOCK_STAFF if s['role'] == role), staff_list[0])
        staff_logged_by = st.selectbox("Logged By (Staff)", staff_list, index=staff_list.index(staff_name), disabled=True)
        
        # A - Antecedent
        st.subheader("A - Antecedent (What happened right before?)")
        location = st.text_input("Location/Context", value="Classroom", max_chars=100)
        antecedent = st.selectbox("Event/Trigger", ANTECEDENTS_FBA)
        
        # B - Behaviour
        st.subheader("B - Behaviour (What the student did)")
        behaviour = st.selectbox("Observed Behaviour", BEHAVIORS_FBA)
        critical = st.checkbox("🚩 **Critical Incident?** (Requires full narrative/ABCH)", value=False)
        
        # C - Consequence/Contextual Details
        st.subheader("C - Consequence/Context")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=5)
        
        submitted = st.form_submit_button("Finalize Log Entry", type='primary')
        
        if submitted:
            if not student_id:
                 st.error("Please select a valid student before submitting.")
                 return

            # Construct preliminary log data
            preliminary_data = {
                'id': str(uuid.uuid4()),
                'student_id': student_id,
                'student_name': student_name,
                'staff_logged_by': staff_logged_by,
                'date': log_date,
                'start_time': log_time,
                'location': location,
                'antecedent': antecedent,
                'behaviour': behaviour,
                'is_critical': critical,
                'duration': duration, # Quick log duration
                # Add a mock end time for use in narrative/duration calculation if not critical
                'end_time': datetime.combine(log_date, log_time) + timedelta(minutes=duration) if not critical else None
            }
            
            st.session_state.current_quick_log = preliminary_data
            
            # Save the quick log (only if not critical for simplicity, or save a draft)
            if not critical:
                st.session_state.log_data.append(preliminary_data)
                # Save to student specific logs (mock db)
                if student_id in st.session_state.selected_student_data:
                    st.session_state.selected_student_data[student_id]['logs'].append(preliminary_data)
                st.success(f"Quick Log for {student_name} saved successfully!")
                navigate_to('student_detail', student=student_id)
            else:
                # CRITICAL INCIDENT PATH
                st.info("Critical Incident flag set. Moving to detailed Narrative Log.")
                # Seed the narrative steps with the initial event
                initial_step = get_initial_narrative_step(preliminary_data)
                st.session_state.critical_incident_steps = [initial_step]
                navigate_to('critical_incident_narrative', student=student_id)

def render_critical_incident_narrative(student_id):
    preliminary_data = st.session_state.current_quick_log
    
    if not preliminary_data:
        st.error("Preliminary Quick Log data is missing. Please start a new Quick Log.")
        if st.button("Go to Quick Log"):
            navigate_to('quick_log', student=student_id)
        return
        
    student_name = preliminary_data['student_name']
    
    st.title(f"Critical Incident Narrative: {student_name}")
    st.subheader("Step-by-Step Incident Flow")
    
    # Display Preliminary Data Summary
    with st.expander("Preliminary Data from Quick Log"):
        st.markdown(f"""
        - **Student:** {student_name}
        - **Date:** {preliminary_data['date'].strftime('%d %b %Y')}
        - **Location:** {preliminary_data['location']}
        - **Initial Time:** {preliminary_data['start_time'].strftime('%H:%M')}
        - **Initial Antecedent:** {preliminary_data['antecedent']}
        - **Initial Behaviour:** {preliminary_data['behaviour']}
        """)

    st.markdown("---")

    # Form for adding/editing narrative steps
    with st.form("incident_narrative_form"):
        
        st.markdown('<div class="narrative-container">', unsafe_allow_html=True)
        
        # Header Row
        st.markdown("""
            <div class="narrative-header">
                <div class="col-location">LOCATION / CONTEXT</div>
                <div class="col-time">TIME</div>
                <div class="col-behaviour">BEHAVIOUR (What the student did)</div>
                <div class="col-consequence">CONSEQUENCES (Staff Response)</div>
                <div class="col-function">FUNCTION</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Render dynamic steps
        steps = st.session_state.critical_incident_steps
        updated_steps = []
        
        for i, step in enumerate(steps):
            cols = st.columns([0.25, 0.1, 0.3, 0.25, 0.1])
            
            # Column 1: Location/Context
            with cols[0]:
                step['location'] = st.text_area(f"Location_{i}", value=step['location'], height=40, label_visibility="collapsed")
            
            # Column 2: Time
            with cols[1]:
                # Use a specific key for time input
                time_key = f"time_{i}"
                if time_key not in st.session_state:
                    st.session_state[time_key] = step['time']
                
                # Check if the existing time is a datetime.time object before feeding to widget
                if isinstance(step['time'], time):
                    step['time'] = st.time_input(f"Time_{i}", value=step['time'], label_visibility="collapsed", key=time_key)
                else: # Fallback just in case time is stored as string/other
                    step['time'] = st.time_input(f"Time_{i}", value=datetime.now().time(), label_visibility="collapsed", key=time_key)

            # Column 3: Behaviour
            with cols[2]:
                step['behaviour'] = st.text_area(f"Behaviour_{i}", value=step['behaviour'], height=40, placeholder="What the student did...", label_visibility="collapsed")
            
            # Column 4: Consequences
            with cols[3]:
                step['consequence'] = st.text_area(f"Consequence_{i}", value=step['consequence'], height=40, placeholder="Staff response...", label_visibility="collapsed")
                
            # Column 5: Function
            with cols[4]:
                function_index = FUNCTIONS_FBA.index(step['function']) if step['function'] in FUNCTIONS_FBA else 0
                step['function'] = st.selectbox(f"Function_{i}", options=FUNCTIONS_FBA, index=function_index, label_visibility="collapsed")

            updated_steps.append(step)

        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.critical_incident_steps = updated_steps
        
        # Action Buttons
        col_add, col_del, col_nav = st.columns([1, 1, 4])
        
        with col_add:
            add_step = st.form_submit_button("➕ Add Step")
        
        with col_del:
            # Only allow deleting if there's more than the initial step
            del_step = st.form_submit_button("➖ Remove Last Step", disabled=(len(steps) <= 1))
        
        with col_nav:
            # Main navigation button
            submitted = st.form_submit_button("Next: Intended Outcomes", type='primary')

    # Handle button actions after form submission
    if add_step:
        # Get time from the last step, or current time if no steps exist
        new_time = steps[-1]['time'] if steps else datetime.now().time()
        
        # Seed the new step with the location of the previous step
        new_location = steps[-1]['location'] if steps else preliminary_data['location']

        new_step = {
            'id': str(uuid.uuid4()),
            'location': new_location,
            'time': new_time,
            'behaviour': '',
            'consequence': '',
            'function': FUNCTIONS_FBA[0]
        }
        st.session_state.critical_incident_steps.append(new_step)
        st.rerun()

    if del_step and len(st.session_state.critical_incident_steps) > 1:
        st.session_state.critical_incident_steps.pop()
        st.rerun()

    if submitted:
        # Save narrative steps (in a real app, this would be a save to DB)
        # We navigate to the next page
        navigate_to('intended_outcomes', student=student_id)

    # Duration Display
    if st.session_state.critical_incident_steps:
        duration_td = calculate_incident_duration(st.session_state.critical_incident_steps)
        total_seconds = int(duration_td.total_seconds())
        duration_text = f"{total_seconds // 60} minutes and {total_seconds % 60} seconds"
        
        st.markdown("---")
        st.markdown(f"**Total Incident Duration:** :clock1: **{duration_text}**")
        st.markdown("*(Calculated from the time of the first step to the time of the last step.)*")

def render_intended_outcomes(student_id):
    preliminary_data = st.session_state.current_quick_log
    
    if not preliminary_data:
        st.error("Preliminary data is missing. Please complete the Quick Log and Narrative.")
        if st.button("Go to Quick Log"):
            navigate_to('quick_log', student=student_id)
        return
        
    st.title(f"Intended Outcomes & Final Review: {preliminary_data['student_name']}")
    st.markdown("---")

    st.subheader("1. Quick Log & Narrative Review")
    
    # Display the collected data (Mock combined view)
    col_ql, col_narrative = st.columns(2)
    with col_ql:
        st.markdown("#### Preliminary Quick Log Data")
        st.json(preliminary_data, expanded=False)
        
    with col_narrative:
        st.markdown("#### Critical Incident Narrative Steps")
        # Format the narrative steps into a readable dataframe
        narrative_df = pd.DataFrame(st.session_state.critical_incident_steps)
        st.dataframe(narrative_df[['time', 'location', 'behaviour', 'consequence', 'function']].style.set_properties(**{'font-size': '10pt'}), 
                     use_container_width=True, hide_index=True)


    st.subheader("2. Intended Outcomes Form")
    st.markdown("_Based on the provided Word document structure._")

    # The Intended Outcomes form structure based on the uploaded document
    # Note: This is a placeholder section using checkboxes/inputs based on the document's content.
    with st.form("intended_outcomes_form"):
        
        st.markdown("#### Immediate Outcomes")
        col_imm_1, col_imm_2 = st.columns(2)
        with col_imm_1:
            st.checkbox("Send Home. Parent / Caregiver notified.", key='o_send_home')
            st.checkbox("Student Leaving supervised areas / leaving school grounds", key='o_leave_area')
            st.checkbox("Incident – student to student", key='o_st_st')
            st.checkbox("Property damage", key='o_property_damage')
            st.checkbox("ED155: Staff Injury (submit with report)", key='o_staff_injury')
        with col_imm_2:
            st.checkbox("Sexualised behaviour", key='o_sexualised')
            st.checkbox("Complaint by co-located school / member of public", key='o_complaint')
            st.checkbox("Stealing / Toileting issue", key='o_stealing_toilet')
            st.checkbox("ED155: Student injury (submit with report)", key='o_student_injury')

        st.markdown("#### Emergency Services & Follow Up")
        col_em_1, col_em_2 = st.columns(2)
        with col_em_1:
            st.checkbox("Emergency services / SAPOL Call Out", key='o_sapol_callout')
            sapol_report_no = st.text_input("SAPOL Report Number:")
        with col_em_2:
            st.checkbox("SA Ambulance Services Call out", key='o_ambulance_callout')
            st.checkbox("Taken to Hospital", key='o_hospital')

        st.markdown("#### Future Support Actions")
        
        st.checkbox("A TAC meeting will be held to discuss solutions to support the student.", key='o_tac_meeting')
        st.checkbox("Restorative Session", key='o_restorative')
        st.checkbox("Case Review", key='o_case_review')
        st.checkbox("Re-Entry plan required", key='o_re_entry')
        
        st.text_area("Other outcomes to be pursued by Management (Safety and Risk Plan, etc.)")
        
        # Finalization Checkboxes
        st.markdown("---")
        st.checkbox("Notified Line Manager of Critical Incident", value=True)
        st.checkbox("Notified Parent / Caregiver of Critical Incident", value=True)
        st.checkbox("Copy of Critical Incident in student file", value=True)
        
        submitted = st.form_submit_button("Finalize and Save Report", type='primary')

    if submitted:
        # In a real application, you would save all data (quick log, narrative, outcomes) to the database here.
        st.success(f"Critical Incident Report for {preliminary_data['student_name']} finalized and saved successfully!")
        
        # Clear temporary states and navigate back to student detail
        st.session_state.current_quick_log = None
        st.session_state.critical_incident_steps = []
        navigate_to('student_detail', student=student_id)
        
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
        render_quick_log(current_role, current_student) 

    elif st.session_state.page == 'critical_incident_narrative':
        if current_student and current_role:
             render_critical_incident_narrative(current_student)
        else:
            st.error("Missing context. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)
            
    elif st.session_state.page == 'intended_outcomes':
        if current_student and current_role:
             render_intended_outcomes(current_student)
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
            st.error("Role context missing. Please select a role.")
            navigate_to('landing')

if __name__ == "__main__":
    main()
