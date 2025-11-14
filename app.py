import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np

# --- Configuration and Aesthetics (High-Contrast Dark Look) ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define Plotly Theme for Dark Mode Consistency
PLOTLY_THEME = 'plotly_dark'

# --- Behaviour Profile Plan and Data Constants ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    # Special roles that require manual name input (e.g., external staff)
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

MOCK_STUDENTS = [
    {'id': 'st1', 'name': 'Izack P.', 'class': 'JP-1', 'profile_status': 'Complete'},
    {'id': 'st2', 'name': 'Chloe T.', 'class': 'PY-3', 'profile_status': 'Drafting'},
    {'id': 'st3', 'name': 'Marcus A.', 'class': 'SY-5', 'profile_status': 'N/A'},
]

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)',
    'Self-Injurious Behaviour', 'Out of Area', 'Verbal Aggression (Staff)',
    'Sexualised Behaviour', 'Defiance/Non-Compliance'
]

OUTCOMES_MAP = {
    'o_a_send_home': 'Send Home / Parent Notified',
    'o_b_left_area': 'Student Left Supervised Area',
    'o_c_assault': 'Assault',
    'o_d_property_damage': 'Property Damage',
    'o_e_staff_injury': 'ED155: Staff Injury',
    'o_f_sapol_callout': 'SAPOL Callout',
    'o_g_restorative_session': 'Restorative Session',
    'o_h_community_service': 'Community Service',
    'o_i_make_up_time': 'Make-up Time',
    'o_j_first_aid_amb': 'ED155: Student Injury (First Aid / Amb)',
    'o_k_drug_possession': 'Drug Possession',
    'o_l_absconding': 'Absconding',
    'o_m_removal': 'Removal',
    'o_n_stealing': 'Stealing',
    'o_o_vandalism': 'Vandalism',
    'o_p_internal_manage': 'Incident Internally Managed',
    'o_q_re_entry': 'Re-Entry',
    'o_r_call_out_amb': 'SA Ambulance Call Out',
    'o_s_taken_to_hospital': 'Taken to Hospital'
}

# --- Utility Functions ---

def initialise_state():
    """Initialises or resets Streamlit session state variables."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
    if 'current_role' not in st.session_state:
        st.session_state.current_role = None
    if 'selected_student_id' not in st.session_state:
        st.session_state.selected_student_id = None
    if 'incident_log' not in st.session_state:
        st.session_state.incident_log = []
    if 'temp_incident_data' not in st.session_state:
        st.session_state.temp_incident_data = None
    if 'abch_chronology' not in st.session_state:
        st.session_state.abch_chronology = []

def navigate_to(page_name):
    """Sets the application's current page."""
    st.session_state.current_page = page_name

def get_active_staff(role):
    """Filters MOCK_STAFF for active staff in a given role (or all non-special)."""
    if role == 'ADM':
        # Admin can log for everyone
        return [s for s in MOCK_STAFF if s['active'] and not s['special']]
    # Everyone else can only log for themselves
    return [s for s in MOCK_STAFF if s['active'] and s['role'] == role and not s['special']]

def get_student_by_id(student_id):
    """Retrieves student object by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_staff_name_by_id(staff_id):
    """Retrieves staff name by ID."""
    staff = next((s for s in MOCK_STAFF if s['id'] == staff_id), None)
    return staff['name'] if staff else 'Unknown Staff'

def get_color_for_role(role):
    """Maps roles to a color for styling."""
    colors = {
        'JP': '#4F46E5',  # Indigo
        'PY': '#F97316',  # Orange
        'SY': '#10B981',  # Emerald
        'TRT': '#EF4444', # Red
        'SSO': '#0EA5E9', # Sky
        'ADM': '#A855F7', # Purple
        None: '#64748B'   # Slate
    }
    return colors.get(role, '#64748B')

def add_log_entry(log_entry):
    """Mock function to add a final log entry to the session state."""
    log_entry['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry['incident_id'] = str(uuid.uuid4())
    st.session_state.incident_log.append(log_entry)
    st.toast("✅ Incident Logged Successfully!", icon="🎉")

# --- Submission Handlers ---

def submit_preliminary_log(preliminary_data, role):
    """Handles the submission of the first step (Prelim Log) and transitions to ABCH."""
    
    # 1. Validate data
    required_fields = ['student_name', 'staff_id', 'date', 'start_time', 'duration_minutes', 'primary_behavior', 'area', 'severity']
    for field in required_fields:
        if preliminary_data.get(field) is None or preliminary_data.get(field) == '':
            st.error(f"Please fill out the required field: {field.replace('_', ' ').title()}")
            return

    # 2. Store data and transition state
    st.session_state.temp_incident_data = preliminary_data
    st.session_state.temp_incident_data['role_at_submission'] = role
    st.session_state.current_page = 'abch_form'

    # 3. Initialize ABCH-specific state
    st.session_state.abch_chronology = []

def submit_abch_log(preliminary_data):
    """Handles the submission of the final ABCH form."""

    # Retrieve data from session state
    refined_wot = st.session_state.get('wot_refined', 'No refined WOT provided.')
    final_context = st.session_state.get('context_refined', 'No context provided.')
    how_to_respond_plan = st.session_state.get('how_to_respond_refined', 'No "How to respond" plan provided.')

    # Validation (quick check for ABCH fields)
    if not st.session_state.abch_chronology:
         st.error("Please add at least one entry to the A-B-C Chronology.")
         return

    # Construct the final log entry
    final_log_entry = preliminary_data.copy()
    final_log_entry.update({
        'is_abch_completed': True,
        'chronology': st.session_state.abch_chronology,
        'window_of_tolerance': refined_wot,
        'context': final_context,
        'how_to_respond': how_to_respond_plan,
        'outcomes': {k: st.session_state.get(k, False) for k in OUTCOMES_MAP.keys()},
    })

    # Save the final entry
    add_log_entry(final_log_entry)

    # Clean up temporary session state data after final save
    st.session_state.temp_incident_data = None
    st.session_state.abch_chronology = []

    # Navigate back to the landing page
    navigate_to('landing')

# --- Form Rendering ---

def render_incident_log_form(student):
    """Renders the main multi-step incident logging form."""
    col_main = st.columns([1])[0]

    with col_main:
        # --- Step 1: Preliminary Log (If not completed) ---
        if st.session_state.temp_incident_data is None:
            st.markdown("### Preliminary Log - What, When, Who")

            # Initialize form data container
            preliminary_data = {}

            # Set static fields
            preliminary_data['student_id'] = student['id']
            preliminary_data['student_name'] = student['name']

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                st.write(f"**Student:** {student['name']} ({student['class']})")
                preliminary_data['staff_id'] = st.selectbox(
                    "Primary Logging Staff",
                    options=[s['id'] for s in get_active_staff(st.session_state.current_role)],
                    format_func=get_staff_name_by_id,
                    key="log_staff_id",
                    help="The staff member primarily logging this incident."
                )
                preliminary_data['area'] = st.text_input("Area of Incident", "Classroom")
            
            with col2:
                current_date = datetime.now().date()
                preliminary_data['date'] = st.date_input("Date", current_date)
                
                # Get a default time close to now for convenience
                current_dt = datetime.now()
                default_time = time(current_dt.hour, current_dt.minute)
                preliminary_data['start_time'] = st.time_input("Start Time", default_time)
                
                # Default duration to 5 mins
                preliminary_data['duration_minutes'] = st.number_input(
                    "Duration (minutes)",
                    min_value=1,
                    max_value=360,
                    value=5,
                    step=1
                )
            
            with col3:
                preliminary_data['primary_behavior'] = st.selectbox(
                    "Primary Behavior",
                    options=BEHAVIORS_FBA,
                    key="log_primary_behavior",
                    help="The most prominent challenging behavior observed."
                )
                preliminary_data['severity'] = st.select_slider(
                    'Severity Rating (1=Low, 5=Extreme)',
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    help="Rate the intensity/risk of the incident."
                )
            
            st.markdown("---")
            
            if st.button("Continue to ABCH Details (Step 2)", use_container_width=True, type="primary"):
                submit_preliminary_log(preliminary_data, st.session_state.current_role)

        # --- Step 2: ABCH Form (If preliminary log is completed) ---
        else:
            preliminary_data = st.session_state.temp_incident_data
            st.markdown(f"### ABCH Analysis for {preliminary_data['student_name']} - Step 2/2")

            st.info(
                f"**Incident Summary:** {preliminary_data['primary_behavior']} "
                f"at {preliminary_data['start_time'].strftime('%H:%M')} on {preliminary_data['date'].strftime('%Y-%m-%d')} "
                f"in the {preliminary_data['area']} for {preliminary_data['duration_minutes']} minutes. "
                f"(Severity: {preliminary_data['severity']}/5)"
            )

            # ABCH Chronology Helper
            st.markdown("#### A-B-C Chronology (Antecedent - Behavior - Consequence)")
            with st.expander("Add New Chronology Entry", expanded=False):
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    chrono_time = st.time_input("Time", datetime.now().time(), key="chrono_time")
                with col_c2:
                    chrono_description = st.text_area("Description of Event", key="chrono_desc")
                with col_c3:
                    chrono_type = st.selectbox(
                        "Event Type",
                        options=['Antecedent', 'Behavior', 'Consequence', 'Intervention'],
                        key="chrono_type"
                    )

                if st.button("Add Entry to Chronology", key="add_chrono_btn"):
                    if chrono_description:
                        st.session_state.abch_chronology.append({
                            'time': chrono_time.strftime('%H:%M'),
                            'type': chrono_type,
                            'description': chrono_description,
                            'id': str(uuid.uuid4())
                        })
                        st.session_state.chrono_desc = "" # Clear the text area
                        st.experimental_rerun() # Rerun to clear the text area and update list
                    else:
                        st.warning("Please provide a description for the event.")
            
            # Display Chronology
            if st.session_state.abch_chronology:
                chrono_df = pd.DataFrame(st.session_state.abch_chronology)
                st.dataframe(
                    chrono_df.sort_values(by='time'),
                    use_container_width=True,
                    hide_index=True,
                    column_order=("time", "type", "description"),
                    column_config={
                        "time": st.column_config.TextColumn("Time", width="small"),
                        "type": st.column_config.TextColumn("Type", width="small"),
                        "description": st.column_config.TextColumn("Description"),
                    }
                )
            else:
                st.info("No chronology entries added yet.")

            st.markdown("---")

            # --- Remaining ABCH Fields ---
            col_wot, col_context = st.columns(2)
            with col_wot:
                st.markdown("#### Window of Tolerance (WOT)")
                st.text_area(
                    "Refined WOT Check & Summary",
                    value="Refined WOT statement (e.g., Izack was in the hyper-arousal zone due to...)",
                    key="wot_refined",
                    height=150
                )
            with col_context:
                st.markdown("#### Environmental/Physiological Context")
                st.text_area(
                    "Refined Context Summary (e.g., Medication changes, lack of sleep, class noise level)",
                    value="No context provided.",
                    key="context_refined",
                    height=150
                )
            
            st.markdown("---")
            st.markdown("#### Post-Incident 'How to Respond' & Outcomes")

            st.text_area(
                "How to Respond (Immediate Follow-Up Plan for this situation)",
                value="The agreed plan for staff response next time is...",
                key="how_to_respond_refined",
                height=100
            )

            st.markdown("##### Intended Outcomes/Consequences")
            cols = st.columns(3)
            # Use columns to display outcomes as checkboxes
            outcome_keys = list(OUTCOMES_MAP.keys())
            for i, key in enumerate(outcome_keys):
                cols[i % 3].checkbox(OUTCOMES_MAP[key], key=key)

            st.markdown("---")

            col_submit, col_cancel = st.columns([4, 1])

            with col_submit:
                if st.button("Finalize and Save Incident Log", use_container_width=True, type="primary"):
                    submit_abch_log(preliminary_data)

            with col_cancel:
                if st.button("Cancel Log", use_container_width=True, type="secondary", help="Discard all temporary data and return to landing."):
                    st.session_state.temp_incident_data = None
                    st.session_state.abch_chronology = []
                    navigate_to('landing')

# --- Page Rendering Functions ---

def render_landing_page():
    """The initial page where the user selects their role and navigates."""
    
    st.title("Behaviour Support & Incident Logger")
    st.markdown("---")

    col_role, col_action = st.columns([1, 2])

    with col_role:
        st.markdown("#### Select Your Role")
        
        # Use staff roles as options
        role_options = sorted(list(set(s['role'] for s in MOCK_STAFF)))
        selected_role = st.selectbox(
            "Current Staff Role",
            options=role_options,
            index=role_options.index('ADM') if 'ADM' in role_options else 0,
            key='landing_role_select'
        )
        st.session_state.current_role = selected_role
        
        # Simple status indicator
        st.markdown(f"Current Role: **<span style='color:{get_color_for_role(selected_role)};'>{selected_role}</span>**", unsafe_allow_html=True)
        
        if selected_role == 'ADM':
            st.markdown("*(Admin access grants full data visibility.)*")
        else:
             st.markdown("*(Logging is generally restricted to your area.)*")

    with col_action:
        st.markdown("#### Primary Actions")
        
        # Action 1: Log an incident directly
        if st.button("➕ Quick Log Incident", use_container_width=True, type="primary"):
            navigate_to('select_student_for_direct_log')

        # Action 2: Go to data dashboard (for Admins or authorized staff)
        if selected_role == 'ADM':
             if st.button("📊 View Data Dashboard", use_container_width=True):
                 navigate_to('dashboard')

        # Action 3: Go to staff-specific area (e.g., viewing profiles for their students)
        if st.button("👤 Go to My Area", use_container_width=True, type="secondary"):
            navigate_to('staff_area')
            
    st.markdown("---")
    
    # Display recent incidents (for demo purposes)
    st.markdown("#### Recent Incidents Logged (Demo View)")
    if st.session_state.incident_log:
        log_df = pd.DataFrame(st.session_state.incident_log).sort_values(by='timestamp', ascending=False)
        
        # Select and rename columns for display
        display_cols = [
            'timestamp', 'student_name', 'primary_behavior', 'severity', 
            'duration_minutes', 'area', 'staff_id', 'is_abch_completed'
        ]
        
        # Map staff ID back to name for display clarity
        log_df['Staff'] = log_df['staff_id'].apply(get_staff_name_by_id)
        
        # Prepare final display DataFrame
        display_df = log_df[display_cols].rename(columns={
            'timestamp': 'Time',
            'student_name': 'Student',
            'primary_behavior': 'Behavior',
            'severity': 'Severity',
            'duration_minutes': 'Duration (min)',
            'area': 'Area',
            'staff_id': 'Logged By (ID)',
            'is_abch_completed': 'ABCH Complete'
        })

        st.dataframe(display_df.head(10), use_container_width=True, hide_index=True)
        
    else:
        st.info("No incidents have been logged yet. Click 'Quick Log Incident' to start.")

def render_select_student_for_direct_log():
    """Renders the student selection page before the log form."""
    st.markdown("## Quick Incident Log - Select Student")
    st.markdown("---")
    
    col_select, col_back = st.columns([3, 1])

    with col_select:
        student_names = [s['name'] for s in MOCK_STUDENTS]
        selected_name = st.selectbox("Select Student to Log Incident For", options=student_names)
        
        # Map back to ID for state
        selected_student = next(s for s in MOCK_STUDENTS if s['name'] == selected_name)
        st.session_state.selected_student_id = selected_student['id']
        
        st.markdown(f"**Profile Status:** {selected_student['profile_status']}")

        if st.button("Start Log", use_container_width=True, type="primary"):
            # Set the role context to ADM for the log submission step
            # Note: The actual logging staff ID is selected within the form.
            st.session_state.current_role = 'ADM' 
            navigate_to('direct_log_form')

    with col_back:
        st.markdown("##") # Spacer
        if st.button("⬅ Back to Home", key="back_from_student_select"):
            navigate_to('landing')
        
def render_direct_log_form():
    """Renders the incident log form directly after selection from the landing page."""
    student = get_student_by_id(st.session_state.selected_student_id)
    if student:
        col_title, col_back = st.columns([4, 1])
        with col_title:
            # Title updates based on which step we are on
            title_text = "Quick Incident Log (Step 1)" if st.session_state.temp_incident_data is None else "Quick Incident Log (Step 2)"
            st.markdown(f"## {title_text}")
        with col_back:
            # If navigating back, clear the temporary direct log state
            if st.button("⬅ Change Student", key="back_to_direct_select_form"):
                st.session_state.temp_incident_data = None
                st.session_state.abch_chronology = []
                st.session_state.current_role = None # Clear temporary role context
                navigate_to('landing')
                
        st.markdown("---")
        
        # We pass the role as 'ADM' as this path is initiated from the Quick Log.
        # The actual logging staff role doesn't matter here, only the staff_id is used for the log.
        render_incident_log_form(student)
    else:
        st.error("No student selected. Returning to home.")
        navigate_to('landing')

def render_staff_area():
    """Placeholder for staff-specific content like student profiles or alerts."""
    st.title(f"My {st.session_state.current_role} Area")
    st.markdown("---")
    st.markdown("This area would typically show alerts, student profiles relevant to your role, and case management tasks.")

    st.markdown("### My Students")
    staff_students = [s for s in MOCK_STUDENTS if st.session_state.current_role in s['class']]
    if staff_students:
        for student in staff_students:
            st.info(f"**{student['name']}** - Class: {student['class']} - Profile Status: {student['profile_status']}")
    else:
        st.warning("No students currently assigned to this role's area in mock data.")
        
    if st.button("⬅ Back to Home", key="back_from_staff_area"):
        navigate_to('landing')
        
def render_data_dashboard():
    """Placeholder for the data analysis dashboard."""
    st.title("Data Analysis Dashboard")
    st.markdown("---")
    
    if not st.session_state.incident_log:
        st.warning("Log some incidents first to view the dashboard!")
        if st.button("⬅ Back to Home", key="back_from_empty_dashboard"):
            navigate_to('landing')
        return

    log_df = pd.DataFrame(st.session_state.incident_log)
    
    col_chart, col_metric = st.columns([3, 1])
    
    # 1. Total Incidents Metric
    with col_metric:
        st.metric("Total Incidents Logged", len(log_df))
        avg_severity = log_df['severity'].mean() if 'severity' in log_df.columns else 0
        st.metric("Average Severity", f"{avg_severity:.1f}/5")
        
    # 2. Behavior Frequency Chart
    with col_chart:
        behavior_counts = log_df['primary_behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        
        fig = px.bar(
            behavior_counts, 
            x='Behavior', 
            y='Count', 
            title='Top Behaviors Logged',
            template=PLOTLY_THEME,
            color_discrete_sequence=[get_color_for_role(st.session_state.current_role)]
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")

    # 3. Time of Day Analysis (Example)
    st.markdown("### Incident Trend: Time of Day")
    
    # Mock time data from start_time object
    if 'start_time' in log_df.columns and not log_df['start_time'].empty:
        log_df['hour'] = log_df['start_time'].apply(lambda x: x.hour)
        time_counts = log_df['hour'].value_counts().sort_index().reset_index()
        time_counts.columns = ['Hour', 'Incidents']
        
        fig_time = px.line(
            time_counts,
            x='Hour',
            y='Incidents',
            title='Incidents by Hour of Day',
            template=PLOTLY_THEME,
            markers=True
        )
        fig_time.update_traces(line=dict(color=get_color_for_role(st.session_state.current_role), width=3))
        fig_time.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")
    if st.button("⬅ Back to Home", key="back_from_dashboard"):
        navigate_to('landing')

# --- Main App Execution ---
def main():
    """The main function to drive the Streamlit application logic."""
    
    # Ensure all state variables are initialized
    initialise_state()
    
    # Main routing logic
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'select_student_for_direct_log':
        render_select_student_for_direct_log()
    elif st.session_state.current_page == 'direct_log_form':
        render_direct_log_form()
    elif st.session_state.current_page == 'abch_form':
        # This path is taken after Step 1 of a direct log, 
        # so render the form with the temporary data populated
        student = get_student_by_id(st.session_state.selected_student_id)
        if student:
             col_title, col_back = st.columns([4, 1])
             with col_title:
                 st.markdown(f"## Quick Incident Log (Step 2)")
             with col_back:
                 if st.button("⬅ Start Over", key="start_over_from_abch_btn"):
                     st.session_state.temp_incident_data = None
                     st.session_state.abch_chronology = []
                     navigate_to('landing')
             st.markdown("---")
             # Use the role stored during preliminary submission
             render_incident_log_form(student) 
        else:
            st.error("Error retrieving student data for ABCH form.")
            navigate_to('landing')
    elif st.session_state.current_page == 'staff_area':
        render_staff_area()
    elif st.session_state.current_page == 'dashboard':
        render_data_dashboard()

if __name__ == '__main__':
    main()
