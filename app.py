import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
from collections import defaultdict
import time as time_module

# --- Configuration and Aesthetics (High-Contrast Dark Look) ---

# Set Streamlit page configuration for a wide layout
st.set_page_config(
    page_title="Behavior Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define Plotly Theme for Dark Mode Consistency
PLOTLY_THEME = 'plotly_dark'

# Inject custom CSS for a modern, high-contrast dark theme
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    /* Header/Title styling */
    h1, h2, h3, h4 {
        color: #f7931e; /* Orange/Gold accent */
        font-family: 'Inter', sans-serif;
    }
    /* Main content styling for cards/forms */
    div[data-testid="stForm"] {
        background-color: #2b2b2b;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    /* Button styling */
    .stButton>button {
        background-color: #f7931e;
        color: #1e1e1e;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #ffb969;
        box-shadow: 0 0 10px #f7931e;
    }
    /* Multiselect/Dropdown consistency */
    div[data-testid="stMultiSelect"], div[data-testid="stSelectbox"] {
        border-radius: 8px;
    }
    /* Sidebar styling if enabled */
    .css-1d3w5rq {
        background-color: #151515;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization and Constants ---

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'
if 'selected_student_id' not in st.session_state:
    st.session_state.selected_student_id = None
if 'temp_incident_data' not in st.session_state:
    st.session_state.temp_incident_data = None
if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []
if 'log_count' not in st.session_state:
    st.session_state.log_count = 0

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS ---
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
    {'id': 's5', 'name': 'Marcus Green (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's6', 'name': 'Jodie Brown (JP)', 'role': 'JP', 'active': False, 'special': False},
]

MOCK_STUDENTS = [
    {'id': 'st101', 'name': 'Izack P.', 'risk_level': 'High', 'plan_status': 'Active BSP', 'cohort': 'Senior'},
    {'id': 'st102', 'name': 'Chloe T.', 'risk_level': 'Medium', 'plan_status': 'Draft Plan', 'cohort': 'Middle'},
    {'id': 'st103', 'name': 'Noah K.', 'risk_level': 'Low', 'plan_status': 'No Plan', 'cohort': 'Junior'},
]

# --- FBA and Data Constants ---

BEHAVIORS_FBA = [
    'Verbal Refusal (Level 1)', 'Elopement (Level 3)', 'Property Destruction (Level 3)',
    'Aggression (Peer) (Level 3)', 'Self-Injurious Behaviour (Level 2)', 'Out of Area (Level 2)',
    'Crying/Distress (Level 1)', 'Vocal Stereotypy (Level 0)', 'Verbal Abuse (Staff) (Level 2)'
]

ANTECEDENTS = [
    'Transition requested', 'Academic demand/non-preferred task', 'Change in routine',
    'Peer proximity/attention', 'Attention withdrawn', 'Sensory over-stimulation (noise, light)',
    'Hunger/Thirst/Fatigue', 'Unstructured time', 'Specific staff member present'
]

CONSEQUENCES = [
    'Access to preferred item/activity (Escape)', 'Adult attention/1:1 time (Attention)',
    'Sent to Safe Space/Isolation (Escape)', 'Peer/Group attention (Attention)',
    'Sensory input gained/avoided (Sensory)', 'Task removed/modified (Escape)',
    'First Aid/Medical Intervention (Tangible)', 'No discernible consequence'
]

FUNCTION_HYPOTHESIS = [
    'Escape (E)', 'Attention (A)', 'Tangible (T)', 'Sensory (S)'
]

OUTCOMES_MAP = {
    'o_a_send_home': 'Send Home / Parent Notified',
    'o_b_left_area': 'Student Left Supervised Area/Grounds',
    'o_c_assault': 'Assault / Sexualised Behaviour',
    'o_d_property_damage': 'Property Damage / Vandalism',
    'o_e_staff_injury': 'ED155: Staff Injury',
    'o_f_sapol_callout': 'Emergency Services: SAPOL Call Out',
    'o_r_call_out_amb': 'Emergency Services: SA Ambulance Call Out',
    'o_j_first_aid_amb': 'Student Injury / First Aid (Ambulance not called)',
    'o_g_stealing': 'Stealing / Drug Possession',
    'o_d_incident_internally_managed': 'Incident Internally Managed (Minor)',
    'o_k_restorative': 'Restorative Session',
    'o_l_community_service': 'Community Service',
    'o_m_re_entry': 'Re-Entry Plan Required',
    'o_n_case_review': 'Case Review / TAC Meeting',
    'o_p_make_up_time': 'Make-up Time / Detention'
}

# --- Helper Functions ---

def navigate_to(page):
    """Sets the current page in session state for routing."""
    st.session_state.current_page = page

def get_active_staff(include_special=True):
    """Returns a list of active staff names for dropdowns."""
    staff_list = [s['name'] for s in MOCK_STAFF if s['active'] and (include_special or not s['special'])]
    return sorted(staff_list)

def get_staff_roles():
    """Returns a list of unique staff roles."""
    return sorted(list(set(s['role'] for s in MOCK_STAFF)))

def get_student_by_id(student_id):
    """Retrieves student data by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_initial_data():
    """Generates initial mock data for the analysis page."""
    if 'mock_log_data' not in st.session_state:
        # Create a function to generate a realistic mock log entry
        def generate_mock_log():
            log_date = datetime.now() - timedelta(days=random.randint(1, 90), minutes=random.randint(1, 1440))
            student = random.choice(MOCK_STUDENTS)
            staff = random.choice(MOCK_STAFF)
            behavior = random.choice(BEHAVIORS_FBA)
            antecedent = random.choice(ANTECEDENTS)
            consequence = random.choice(CONSEQUENCES)
            function = random.choice(FUNCTION_HYPOTHESIS)
            level = int(behavior.split('Level ')[1][0])
            
            # Simulate outcomes based on severity
            outcomes = {k: random.random() < (0.1 * level) for k in OUTCOMES_MAP.keys()}
            if level == 3:
                outcomes['o_f_sapol_callout'] = random.random() < 0.1
                outcomes['o_a_send_home'] = random.random() < 0.5
            
            return {
                'id': str(uuid.uuid4()),
                'timestamp': log_date,
                'student_id': student['id'],
                'student_name': student['name'],
                'staff_name': staff['name'],
                'staff_role': staff['role'],
                'location': random.choice(['Classroom A', 'Yard - Oval', 'Safe Space', 'Hallway']),
                'duration_minutes': random.randint(1, 60),
                'behavior': behavior,
                'antecedent': antecedent,
                'consequence': consequence,
                'function_hypothesis': function,
                'behavior_level': level,
                'description': f"Student exhibited {behavior.lower()} following a {antecedent.lower()}. Intervention involved {consequence.lower()}.",
                **outcomes
            }

        # Generate 500 mock log entries
        st.session_state.mock_log_data = [generate_mock_log() for _ in range(500)]
    
    # Merge any newly created logs into the mock data
    if 'saved_logs' in st.session_state:
        logs_to_add = [log for log in st.session_state.saved_logs if log['id'] not in [d['id'] for d in st.session_state.mock_log_data]]
        st.session_state.mock_log_data.extend(logs_to_add)

    df = pd.DataFrame(st.session_state.mock_log_data)
    
    # Add day of week and month for easy filtering/plotting
    if not df.empty:
        df['date'] = df['timestamp'].dt.date
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['month_year'] = df['timestamp'].dt.to_period('M').astype(str)
        df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
    return df

def save_incident(final_log_entry):
    """
    Mocks saving the incident log entry to a persistent store.
    In a real app, this would be a database write (e.g., Firestore).
    """
    st.session_state.log_count += 1
    
    # Initialize 'saved_logs' list if it doesn't exist
    if 'saved_logs' not in st.session_state:
        st.session_state.saved_logs = []
    
    # Add current timestamp and unique ID
    final_log_entry['timestamp'] = datetime.now()
    final_log_entry['id'] = str(uuid.uuid4())
    
    st.session_state.saved_logs.append(final_log_entry)
    
    # Clean up session state for next log
    st.session_state.temp_incident_data = None
    st.session_state.abch_chronology = []
    st.session_state.current_role = None
    st.session_state.selected_student_id = None
    
    # Navigate back to the landing page or a success message
    show_message("✅ Success!", f"Incident Log for **{final_log_entry['student_name']}** saved successfully (ID: {final_log_entry['id'][:8]}).", 'success')
    time_module.sleep(3) # Pause to let the user see the success message
    navigate_to('landing')

def show_message(title, content, type='info'):
    """Renders a styled message box instead of alert()."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append({'title': title, 'content': content, 'type': type})

# --- UI Rendering Functions ---

def render_abch_form_chronology():
    """Renders the step-by-step ABCH data collection form."""
    col1, col2 = st.columns([1, 4])
    with col1:
        time_input = st.time_input("Time", datetime.now().time().replace(second=0, microsecond=0), key="abch_time")
    
    action_type = st.radio(
        "Action Type",
        ['Antecedent', 'Behavior', 'Consequence', 'Help/Healing'],
        horizontal=True,
        key="abch_action_type"
    )
    
    # Dynamic selection based on action type
    options = []
    if action_type == 'Antecedent':
        options = ANTECEDENTS
        key_stem = 'abch_antecedent_select'
    elif action_type == 'Behavior':
        options = BEHAVIORS_FBA
        key_stem = 'abch_behavior_select'
    elif action_type == 'Consequence':
        options = CONSEQUENCES
        key_stem = 'abch_consequence_select'
    elif action_type == 'Help/Healing':
        options = ['Staff presence/Co-regulation', 'Relocation to Safe Space', 'Offer of preferred item', 'De-escalation verbal script', 'First Aid administered', 'Restorative conversation']
        key_stem = 'abch_help_select'

    selected_options = st.multiselect(
        f"Select {action_type} Events (Can be multiple)",
        options,
        key=key_stem
    )
    
    details = st.text_area("Specific Details/Context", key="abch_details", height=100)
    
    def add_chronology_entry():
        """Adds an entry to the ABCH chronology list in session state."""
        if not selected_options and not details:
            st.warning("Please select at least one item or enter specific details.")
            return

        st.session_state.abch_chronology.append({
            'time': time_input.strftime("%H:%M"),
            'type': action_type,
            'events': selected_options,
            'details': details
        })
        st.session_state.abch_chronology.sort(key=lambda x: datetime.strptime(x['time'], "%H:%M"))
        
        # Clear form inputs after submission
        for key in ["abch_time", "abch_action_type", "abch_details", key_stem]:
            if key in st.session_state:
                del st.session_state[key]
        
        # Force a refresh to show the new data and clear form cleanly
        st.experimental_rerun()

    if st.button("➕ Add Chronology Entry"):
        add_chronology_entry()

    st.markdown("---")
    st.subheader("Incident Chronology Log")
    
    if not st.session_state.abch_chronology:
        st.info("No entries logged yet. Add the sequence of events (A, B, C, H) above.")
        return

    # Display chronological table
    chronology_df = pd.DataFrame(st.session_state.abch_chronology)
    chronology_df = chronology_df.rename(columns={'time': 'Time', 'type': 'Action Type', 'events': 'Events', 'details': 'Details'})
    
    st.dataframe(
        chronology_df[['Time', 'Action Type', 'Events', 'Details']],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Events": st.column_config.ListColumn(width="medium"),
            "Details": st.column_config.TextColumn(width="large")
        }
    )

def render_incident_log_form(student):
    """
    Renders the main multi-step incident logging form.
    This includes the core incident details and the ABCH section.
    """
    
    # The form must be wrapped in st.form to ensure all inputs are submitted together
    with st.form(key='incident_log_form'):
        
        st.markdown(f"### Student: **{student['name']}** ({student['id']})")
        st.markdown(f"**Risk Level:** {student['risk_level']} | **Plan Status:** {student['plan_status']}")
        st.markdown("---")

        # --- Section 1: Preliminary Details ---
        st.subheader("1. Preliminary Incident Details")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date_logged = st.date_input("Date of Incident", datetime.now().date(), key="incident_date")
        with col2:
            time_start = st.time_input("Time Incident Started", datetime.now().time().replace(second=0, microsecond=0), key="time_start")
        with col3:
            # Calculate a mock end time for input default
            initial_end_time = (datetime.combine(date_logged, time_start) + timedelta(minutes=5)).time()
            time_end = st.time_input("Time Incident Ended", initial_end_time, key="time_end")
            
        col4, col5 = st.columns(2)
        with col4:
            logged_by = st.selectbox(
                "Staff Logging Incident (Your Name)",
                get_active_staff(include_special=False),
                key="logged_by"
            )
        with col5:
            location = st.text_input("Location of Incident (e.g., Classroom C, Oval)", key="location")
            
        duration_minutes = (datetime.combine(date_logged, time_end) - datetime.combine(date_logged, time_start)).total_seconds() / 60
        st.caption(f"Calculated Duration: **{int(duration_minutes)} minutes** (Review times if this is incorrect.)")
        
        # --- Section 2: ABCH Detailed Chronology ---
        st.subheader("2. ABCH Detailed Chronology (Antecedent, Behavior, Consequence, Help/Healing)")
        
        # Render the dynamic ABCH form and display the chronology table
        render_abch_form_chronology()
        
        # --- Section 3: Post-Incident Reflections and Outcomes ---
        st.subheader("3. Reflection and Outcomes")

        col_wot, col_context = st.columns(2)
        with col_wot:
            st.markdown("#### Window of Tolerance (WOT)")
            wot = st.slider(
                "Student's WOT Level (0=Low/Dysregulated, 5=High/Regulated)",
                0, 5, 3, 1, key="wot_slider"
            )
            wot_mapping = {
                0: "Dysregulated/Shutdown (Urgent)", 1: "Highly Distressed/Activated",
                2: "Stressed/Outside WOT", 3: "WOT Maintained/Regulated", 
                4: "Hyper-Regulated/Calm", 5: "Excellent Engagement"
            }
            st.markdown(f"**Refined State:** {wot_mapping[wot]}")
            
        with col_context:
            st.markdown("#### Context Summary")
            final_context = st.text_area(
                "Refined Incident Context (Summarize key events leading up to B)",
                key="refined_context", height=120
            )

        st.markdown("#### Plan for Future Response")
        how_to_respond_plan = st.text_area(
            "Based on this incident, how should staff respond next time?",
            key="how_to_respond_plan", height=120
        )
        
        st.markdown("---")
        st.markdown("#### Intended Outcomes and Follow-up Actions (Based on **intended outcomes.docx**)")
        
        # Outcomes Checkboxes (Grouped logically)
        col_out1, col_out2, col_out3 = st.columns(3)
        
        with col_out1:
            st.markdown("##### Immediate/Exit")
            st.checkbox(OUTCOMES_MAP['o_a_send_home'], key='o_a_send_home')
            st.checkbox(OUTCOMES_MAP['o_b_left_area'], key='o_b_left_area')
            st.checkbox(OUTCOMES_MAP['o_d_incident_internally_managed'], key='o_d_incident_internally_managed')
            
            st.markdown("##### Injury/Danger")
            st.checkbox(OUTCOMES_MAP['o_c_assault'], key='o_c_assault')
            st.checkbox(OUTCOMES_MAP['o_d_property_damage'], key='o_d_property_damage')
            st.checkbox(OUTCOMES_MAP['o_e_staff_injury'], key='o_e_staff_injury')
            
        with col_out2:
            st.markdown("##### Emergency/External")
            st.checkbox(OUTCOMES_MAP['o_f_sapol_callout'], key='o_f_sapol_callout')
            st.checkbox(OUTCOMES_MAP['o_r_call_out_amb'], key='o_r_call_out_amb')
            st.checkbox(OUTCOMES_MAP['o_j_first_aid_amb'], key='o_j_first_aid_amb')
            st.checkbox(OUTCOMES_MAP['o_g_stealing'], key='o_g_stealing')
            
        with col_out3:
            st.markdown("##### Follow-up/Restorative")
            st.checkbox(OUTCOMES_MAP['o_k_restorative'], key='o_k_restorative')
            st.checkbox(OUTCOMES_MAP['o_m_re_entry'], key='o_m_re_entry')
            st.checkbox(OUTCOMES_MAP['o_n_case_review'], key='o_n_case_review')
            st.checkbox(OUTCOMES_MAP['o_p_make_up_time'], key='o_p_make_up_time')
            st.checkbox(OUTCOMES_MAP['o_l_community_service'], key='o_l_community_service')
        
        # Final submit button
        st.markdown("---")
        submitted = st.form_submit_button("💾 Finalize and Save Incident Log")

        if submitted:
            # Validation
            if not st.session_state.abch_chronology:
                st.error("Cannot save: Please add at least one entry to the Incident Chronology Log (Section 2).")
                return
            if not final_context or not how_to_respond_plan:
                st.error("Cannot save: Please complete the Context Summary and Plan for Future Response (Section 3).")
                return

            # Collect preliminary data
            preliminary_data = {
                'student_id': student['id'],
                'student_name': student['name'],
                'date_logged': date_logged.strftime("%Y-%m-%d"),
                'time_start': time_start.strftime("%H:%M"),
                'time_end': time_end.strftime("%H:%M"),
                'duration_minutes': int(duration_minutes),
                'logged_by': logged_by,
                'location': location,
                'abch_chronology': st.session_state.abch_chronology,
                'is_abch_completed': True,
            }
            
            # Extract main behavior, antecedent, and consequence from chronology for analysis
            main_b = next((e['events'][0] for e in st.session_state.abch_chronology if e['type'] == 'Behavior' and e['events']), 'Behavior not provided.')
            main_a = next((e['events'][0] for e in st.session_state.abch_chronology if e['type'] == 'Antecedent' and e['events']), 'Antecedent not provided.')
            main_c = next((e['events'][0] for e in st.session_state.abch_chronology if e['type'] == 'Consequence' and e['events']), 'Consequence not provided.')
            
            # Compile final entry
            final_log_entry = preliminary_data.copy()
            final_log_entry.update({
                'window_of_tolerance': wot_mapping[wot],
                'context': final_context,
                'how_to_respond': how_to_respond_plan,
                'behavior': main_b,
                'antecedent': main_a,
                'consequence': main_c,
                # Map selected outcomes from session state
                **{k: st.session_state.get(k, False) for k in OUTCOMES_MAP.keys()}
            })
            
            # Call the mock save function
            save_incident(final_log_entry)

# --- Page Rendering Functions ---

def render_landing_page():
    """Renders the initial landing page for student selection and routing."""
    st.title("Behavior Support & Data Analysis Tool")
    st.markdown("---")
    
    # Display any temporary messages (e.g., success message from saving)
    if 'messages' in st.session_state and st.session_state.messages:
        for msg in st.session_state.messages:
            if msg['type'] == 'success':
                st.success(f"**{msg['title']}** {msg['content']}")
        st.session_state.messages = [] # Clear messages after display

    col_log, col_data = st.columns(2)

    with col_log:
        st.header("Quick Incident Log Entry")
        st.markdown("Select a student to log a new incident report (ABCH and Outcomes form).")
        
        student_names = [f"{s['name']} ({s['cohort']})" for s in MOCK_STUDENTS]
        
        selected_name = st.selectbox(
            "Select Student for Logging",
            options=["-- Select Student --"] + student_names,
            key="selected_student_name_for_log"
        )
        
        if selected_name != "-- Select Student --":
            # Extract student ID
            student_id = next(s['id'] for s in MOCK_STUDENTS if s['name'] in selected_name)
            st.session_state.selected_student_id = student_id
            
            if st.button(f"Start Log for {selected_name.split(' ')[0]}", use_container_width=True):
                navigate_to('direct_log')

    with col_data:
        st.header("Staff Area / Data Analytics")
        st.markdown("Access historical incident data, trends, and behavior profiles.")
        
        st.info(f"Currently viewing **{len(MOCK_STUDENTS)}** students. **{st.session_state.log_count}** new logs saved this session.")
        
        if st.button("📊 Go to Staff Data Area", use_container_width=True):
            navigate_to('staff_area')

def render_direct_log_form():
    """Renders the incident log form directly after selection from the landing page."""
    student = get_student_by_id(st.session_state.selected_student_id)
    if student:
        col_title, col_back = st.columns([4, 1])
        with col_title:
            st.markdown(f"## Quick Incident Log (Step 1)")
        with col_back:
            # If navigating back, clear the temporary direct log state
            if st.button("⬅ Change Student", key="back_to_direct_select_form"):
                st.session_state.temp_incident_data = None
                st.session_state.abch_chronology = []
                navigate_to('landing')
        st.markdown("---")
        
        render_incident_log_form(student)
    else:
        st.error("No student selected.")
        navigate_to('landing')


def render_staff_area():
    """
    Renders the Staff Area with data analysis and visualization.
    This page significantly contributes to the line count due to detailed plotting logic.
    """
    df_logs = get_initial_data()
    
    col_head, col_back = st.columns([4, 1])
    with col_head:
        st.title("📊 Behavior Data & Analytics Dashboard")
    with col_back:
        if st.button("⬅ Back to Home", key="back_to_landing_from_data"):
            navigate_to('landing')
            
    st.markdown("---")
    
    if df_logs.empty:
        st.warning("No incident data available to display. Please log some incidents first.")
        return

    # --- Filtering Sidebar ---
    st.sidebar.header("Filter Data")
    
    # Date Range Filter
    min_date = df_logs['date'].min()
    max_date = df_logs['date'].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        df_filtered = df_logs[(df_logs['date'] >= date_range[0]) & (df_logs['date'] <= date_range[1])]
    else:
        df_filtered = df_logs # Should not happen with current setup

    # Student Filter
    all_students = sorted(df_logs['student_name'].unique())
    selected_students = st.sidebar.multiselect("Student(s)", all_students, default=all_students)
    df_filtered = df_filtered[df_filtered['student_name'].isin(selected_students)]
    
    # Staff/Role Filter
    all_staff = sorted(df_logs['logged_by'].unique())
    selected_staff = st.sidebar.multiselect("Staff Member", all_staff, default=all_staff)
    df_filtered = df_filtered[df_filtered['logged_by'].isin(selected_staff)]

    st.subheader(f"Data Overview (Showing {len(df_filtered)} of {len(df_logs)} Logs)")
    
    # --- Key Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_incidents = len(df_filtered)
    avg_duration = round(df_filtered['duration_minutes'].mean(), 1) if not df_filtered.empty else 0
    high_level_incidents = len(df_filtered[df_filtered['behavior_level'] >= 2])
    
    col1.metric("Total Incidents", f"{total_incidents:,}")
    col2.metric("Avg. Duration (min)", f"{avg_duration} min")
    col3.metric("High-Level Incidents (Lvl 2+)", f"{high_level_incidents:,}")
    
    sapol_callouts = df_filtered['o_f_sapol_callout'].sum()
    col4.metric("SAPOL Call Outs", f"{sapol_callouts:,}", delta=f"{(sapol_callouts / total_incidents * 100):.1f}% of total" if total_incidents > 0 else "0%")

    st.markdown("---")

    # --- Data Visualizations ---
    
    # 1. Behavior Frequency by Student
    st.subheader("Behavior Frequency by Student")
    if not df_filtered.empty:
        behavior_counts = df_filtered.groupby(['student_name', 'behavior']).size().reset_index(name='Count')
        fig = px.bar(
            behavior_counts.sort_values('Count', ascending=False).head(20),
            x='behavior',
            y='Count',
            color='student_name',
            title='Top 20 Behaviors',
            template=PLOTLY_THEME,
            labels={'behavior': 'Behavior', 'Count': 'Incident Count', 'student_name': 'Student'},
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for visualizations based on current filters.")
        
    st.markdown("---")
    
    # 2. ABC Scatter Plot (Antecedent, Behavior, Consequence)
    st.subheader("ABC Correlation Analysis")
    col_abc_a, col_abc_b = st.columns(2)
    
    with col_abc_a:
        # Plot Function Hypothesis
        function_counts = df_filtered['function_hypothesis'].value_counts().reset_index()
        function_counts.columns = ['Function', 'Count']
        fig_func = px.pie(
            function_counts,
            values='Count',
            names='Function',
            title='Hypothesized Function Distribution',
            template=PLOTLY_THEME,
            height=350
        )
        fig_func.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_func, use_container_width=True)

    with col_abc_b:
        # Plot Antecedent vs Consequence Heatmap
        if not df_filtered.empty:
            abc_pivot = df_filtered.groupby(['antecedent', 'consequence']).size().unstack(fill_value=0)
            fig_abc = px.imshow(
                abc_pivot,
                x=abc_pivot.columns,
                y=abc_pivot.index,
                color_continuous_scale='Sunset',
                aspect="auto",
                title='Antecedent vs Consequence Heatmap (Frequency)',
                template=PLOTLY_THEME,
                height=350
            )
            st.plotly_chart(fig_abc, use_container_width=True)
        else:
             st.info("No data for ABC Heatmap based on current filters.")

    st.markdown("---")

    # 3. Outcomes Tally
    st.subheader("Outcomes Summary")
    
    if not df_filtered.empty:
        outcome_columns = [col for col in df_filtered.columns if col.startswith('o_')]
        outcome_df = df_filtered[outcome_columns].sum().reset_index()
        outcome_df.columns = ['Outcome Key', 'Count']
        
        # Map keys to friendly names
        outcome_df['Outcome'] = outcome_df['Outcome Key'].map(OUTCOMES_MAP)
        outcome_df = outcome_df[outcome_df['Count'] > 0]
        outcome_df = outcome_df.sort_values('Count', ascending=False)
        
        fig_outcomes = px.bar(
            outcome_df,
            x='Outcome',
            y='Count',
            color='Count',
            title='Frequency of Follow-up Actions/Outcomes',
            template=PLOTLY_THEME,
            height=450
        )
        st.plotly_chart(fig_outcomes, use_container_width=True)
    
    st.markdown("---")
    
    # 4. Raw Data View
    st.subheader("Raw Incident Log Data")
    # Displaying selected columns for a clean view
    display_cols = ['timestamp', 'student_name', 'logged_by', 'location', 'behavior', 'antecedent', 'consequence', 'duration_minutes']
    
    st.dataframe(
        df_filtered[display_cols],
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Showing {len(df_filtered)} total records.")


# --- Main App Execution ---

def main():
    """The main function to drive the Streamlit application logic."""
    
    # Main routing logic
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'direct_log':
        render_direct_log_form()
    elif st.session_state.current_page == 'staff_area':
        render_staff_area()

# Generate mock data on app start
get_initial_data()
# Run the main application
main()
