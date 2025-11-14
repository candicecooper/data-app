import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
import base64 
import os 
from typing import List, Dict, Any, Optional

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
    # Special roles that require manual name input (included from isolated log)
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'profile_status': 'Complete'},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'profile_status': 'Draft'},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'profile_status': 'Pending'},
]

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 
    'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)', 'Aggression (Staff)',
    'Sexualised Behaviour', 'Other - Specify'
]

ANTECEDENTS = [
    'Task Demand/Transition', 'Unstructured Time (Recess/Lunch)', 
    'Peer Conflict', 'Staff Direction', 'Unpredictable Change', 'Sensory Overload',
    'Illness/Fatigue', 'Other - Specify'
]

CONSEQUENCES = [
    'Removal from Area/Time-out', 'Redirection/Re-engagement', 
    'Loss of Privilege', 'Support Plan Implemented', 'Staff Injury', 'Property Damage',
    'Other - Specify'
]

BEHAVIOR_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']

# Outcomes mapped from intended outcomes.docx snippet
OUTCOME_OPTIONS = {
    'Send Home': 'o_a_send_home',
    'Left Supervised Area/Grounds': 'o_b_left_area',
    'Sexualised Behaviour': 'o_c_assault', # Using 'assault' as a general critical incident
    'Property Damage': 'o_d_property_damage',
    'Staff Injury (ED155)': 'o_e_staff_injury',
    'SAPOL Callout (Report)': 'o_f_sapol_callout',
    'Ambulance Callout': 'o_r_call_out_amb',
    'First Aid / Taken to Hospital': 'o_j_first_aid_amb',
    'Restorative Session': 'o_g_restorative',
    'Re-Entry Meeting': 'o_h_reentry',
    'Other': 'o_i_other_outcome',
}


# --- Global Helpers (for navigation and data lookup) ---

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'
if 'selected_student_id' not in st.session_state:
    st.session_state.selected_student_id = None
if 'temp_incident_data' not in st.session_state:
    st.session_state.temp_incident_data = None
if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []

def navigate_to(page: str, student_id: Optional[str] = None):
    """Changes the current page in session state."""
    st.session_state.current_page = page
    if student_id:
        st.session_state.selected_student_id = student_id
    st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, str]]:
    """Mocks fetching student data."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_active_staff(include_special=True) -> List[Dict[str, Any]]:
    """Returns a list of active staff for selection."""
    if include_special:
        return [s for s in MOCK_STAFF if s['active']]
    return [s for s in MOCK_STAFF if s['active'] and not s['special']]

def get_staff_name(staff_id: str) -> str:
    """Returns staff name by ID."""
    staff = next((s for s in MOCK_STAFF if s['id'] == staff_id), None)
    return staff['name'] if staff else 'Unknown Staff'

# --- MOCK LOG DATA (for dashboard) ---
def generate_mock_log_data(student_id: str) -> pd.DataFrame:
    """Generates mock incident log data for a student."""
    if student_id not in ['stu_001', 'stu_002']:
        return pd.DataFrame()

    data = {
        'Timestamp': [datetime.now() - timedelta(days=d, hours=h, minutes=m) 
                      for d, h, m in zip(
                          random.choices(range(1, 30), k=15), 
                          random.choices(range(0, 24), k=15), 
                          random.choices(range(0, 60), k=15)
                      )],
        'Behavior': random.choices(BEHAVIORS_FBA, k=15),
        'Level': random.choices(BEHAVIOR_LEVELS, k=15),
        'Duration (min)': random.choices(range(1, 15), k=15),
        'Reported By': random.choices([s['name'] for s in MOCK_STAFF if not s['special']], k=15)
    }
    df = pd.DataFrame(data)
    df['Date'] = df['Timestamp'].dt.date
    df = df.sort_values('Timestamp', ascending=False)
    return df

# --- Incident Logging Form Functions (The Quick Log) ---

def process_abch_step_one(student: Dict[str, str], form_data: Dict[str, Any]):
    """Saves the preliminary data and navigates to the ABCH chronology step."""
    
    # Store preliminary data
    preliminary_data = {
        'id': str(uuid.uuid4()),
        'student_id': student['id'],
        'student_name': student['name'],
        'date': form_data['log_date'],
        'start_time': form_data['start_time'],
        'end_time': form_data['end_time'],
        # Duration calculation using time objects combined with a dummy date
        'duration_minutes': (datetime.combine(datetime.min, form_data['end_time']) - datetime.combine(datetime.min, form_data['start_time'])).seconds / 60,
        'location': form_data['location'],
        'reported_by_id': form_data['reported_by_id'],
        'behavior_type': form_data['behavior_type'],
        'behavior_level': form_data['behavior_level'],
        'abch_log': [], # To hold chronology
        'is_abch_completed': False,
    }
    
    st.session_state.temp_incident_data = preliminary_data
    st.session_state.abch_chronology = [] # Initialize chronology list
    
    # Navigate to the next step
    st.session_state.temp_incident_data['current_abch_step'] = 'start'
    st.rerun()

def render_abch_step_two_form(student: Dict[str, str]):
    """Renders the step 2 form for Chronology, Context, WOT, Plan, and Outcomes."""
    
    incident_data = st.session_state.temp_incident_data
    
    st.markdown(f"### Chronology & Analysis (Step 2)")
    st.markdown(f"**Incident:** {incident_data['behavior_type']} (Level {incident_data['behavior_level'].split('-')[0].strip()}) on **{incident_data['date'].strftime('%Y-%m-%d')}**")

    # --- ABCH Chronology Section ---
    with st.expander("📝 **ABCH Chronology Log** (A: Antecedent, B: Behavior, C: Consequence)", expanded=True):
        
        # Chronology Input Form
        with st.form("abch_entry_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                antecedent = st.selectbox("Antecedent (A)", options=ANTECEDENTS, key="chron_a")
            with col_b:
                behavior = st.selectbox("Behavior (B)", options=BEHAVIORS_FBA, key="chron_b")
            with col_c:
                consequence = st.selectbox("Consequence (C)", options=CONSEQUENCES, key="chron_c")
            
            description = st.text_area("Specific Description / Narrative:", key="chron_desc")
            
            if st.form_submit_button("➕ Add Chronology Step"):
                if description and antecedent and behavior and consequence:
                    st.session_state.abch_chronology.append({
                        'A': antecedent, 
                        'B': behavior, 
                        'C': consequence,
                        'Description': description,
                        'Time_Added': datetime.now().strftime('%H:%M:%S')
                    })
                    st.success("Chronology step added.")
                    st.rerun()
                else:
                    st.error("Please fill in all chronology fields.")

        st.markdown("#### Logged Chronology Steps")
        if st.session_state.abch_chronology:
            chron_df = pd.DataFrame(st.session_state.abch_chronology)
            st.dataframe(chron_df, use_container_width=True, hide_index=True)
            if st.button("Clear Chronology", key="clear_chronology_btn"):
                st.session_state.abch_chronology = []
                st.rerun()
        else:
            st.info("No chronology steps logged yet. Start adding the sequence of events.")
            
    # --- Analysis and Final Plan Section ---
    st.markdown("---")
    
    with st.form("abch_analysis_form"):
        col_wot, col_context = st.columns(2)
        
        with col_wot:
            st.markdown("#### 1. Window of Tolerance (WOT) Refinement")
            refined_wot = st.text_area(
                "Refined WOT Plan Description (H):", 
                value="[e.g., Izack was outside his Window of Tolerance; we used the calming corner and 5-point self-regulation strategy.]",
                key="refined_wot_input",
                height=150
            )
            
        with col_context:
            st.markdown("#### 2. Underlying Context / Function")
            final_context = st.text_area(
                "Final Context/Analysis (H):", 
                value="[e.g., The likely function was Escape from an academic demand. The trigger was a group work task.]",
                key="final_context_input",
                height=150
            )

        st.markdown("---")
        st.markdown("#### 3. How to Respond Plan (Next Steps)")
        how_to_respond_plan = st.text_area(
            "Future Plan / How to Respond (H):",
            value="[e.g., Next time, provide a 5-minute verbal warning before group work and offer an independent alternative task.]",
            key="how_to_respond_plan_input",
            height=150
        )
        
        st.markdown("---")
        st.markdown("#### 4. Intended Outcomes / Critical Incident Details")
        
        # Outcomes Checkboxes (using the logic from the isolated file)
        col_a, col_b, col_c = st.columns(3)
        cols = [col_a, col_b, col_c]
        
        st.markdown("<p style='font-size: 14px; margin-top: 10px; margin-bottom: 5px;'>**Select all relevant outcomes:**</p>", unsafe_allow_html=True)

        for i, (label, key) in enumerate(OUTCOME_OPTIONS.items()):
            cols[i % 3].checkbox(label, value=False, key=key)

        st.markdown("---")

        if st.form_submit_button("✅ Finalize and Log Incident"):
            
            # 1. Validation
            if not st.session_state.abch_chronology:
                st.error("Please log at least one Chronology Step (A-B-C) before finalizing.")
                st.stop()
            
            if not refined_wot or not final_context or not how_to_respond_plan:
                 st.error("Please fill in the Window of Tolerance, Context, and How to Respond fields.")
                 st.stop()
                 
            # 2. Final Data Structuring
            final_log_entry = incident_data.copy()
            final_log_entry.update({
                'is_abch_completed': True,
                'abch_log': st.session_state.abch_chronology,
                'window_of_tolerance_plan': refined_wot,
                'context_analysis': final_context,
                'how_to_respond_plan': how_to_respond_plan,
                # Outcomes mapping
                'outcome_send_home': st.session_state.get('o_a_send_home', False),
                'outcome_leave_area': st.session_state.get('o_b_left_area', False),
                'outcome_assault': st.session_state.get('o_c_assault', False),
                'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
                'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
                'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
                'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False),
                'outcome_first_aid_hospital': st.session_state.get('o_j_first_aid_amb', False),
                'outcome_restorative': st.session_state.get('o_g_restorative', False),
                'outcome_reentry': st.session_state.get('o_h_reentry', False),
                'outcome_other': st.session_state.get('o_i_other_outcome', False),
            })
            
            # --- MOCK SAVE SUCCESS (Replace this with your actual DB/storage logic) ---
            
            st.success(f"Incident Log for {student['name']} successfully completed and saved.")
            st.json(final_log_entry) # Display saved data for confirmation

            # 3. Clean up and navigate
            del st.session_state.temp_incident_data
            del st.session_state.abch_chronology
            navigate_to('landing')

# The main wrapper function for the logging process
def render_incident_log_form(student: Dict[str, str]):
    """Renders the appropriate step of the incident log form."""
    
    # Check if preliminary data is present (Step 1 is complete)
    if st.session_state.get('temp_incident_data') and st.session_state.get('temp_incident_data', {}).get('is_abch_completed') == False:
        render_abch_step_two_form(student)
    else:
        # Step 1: Preliminary Data Collection
        st.markdown("### 1. Preliminary Incident Data")
        with st.form("incident_step_one_form"):
            col1, col2 = st.columns(2)
            
            # Calculate default end time 5 minutes from now for the fix
            default_end_time = (datetime.now() + timedelta(minutes=5)).time()

            # Date and Time
            with col1:
                log_date = st.date_input("Date of Incident", value=datetime.today(), key="log_date_input")
                reported_by = st.selectbox(
                    "Reported By (Staff Member)",
                    options=get_active_staff(include_special=True),
                    format_func=lambda x: x['name'],
                    key="reported_by_id_input"
                )
                start_time = st.time_input("Incident Start Time", value=datetime.now().time(), key="start_time_input")
                
            with col2:
                # FIX APPLIED HERE: Added datetime.now() to timedelta to get a proper datetime object first.
                end_time = st.time_input("Incident End Time", value=default_end_time, key="end_time_input")
                location = st.text_input("Location (e.g., Classroom 7, Oval, Yard)", key="location_input")
                
                behavior_type = st.selectbox(
                    "Primary Behavior Type", 
                    options=BEHAVIORS_FBA,
                    key="behavior_type_input"
                )
                behavior_level = st.selectbox(
                    "Behavior Level / Risk", 
                    options=BEHAVIOR_LEVELS,
                    key="behavior_level_input"
                )
            
            st.markdown("---")
            
            if st.form_submit_button("Continue to Step 2: ABCH Analysis"):
                form_data = {
                    'log_date': log_date,
                    'start_time': start_time,
                    'end_time': end_time,
                    'location': location,
                    'reported_by_id': reported_by['id'] if reported_by else None,
                    'behavior_type': behavior_type,
                    'behavior_level': behavior_level
                }
                
                # Basic Validation
                if not (location and reported_by and behavior_type and behavior_level):
                    st.error("Please ensure all fields are selected/entered.")
                else:
                    process_abch_step_one(student, form_data)
                    

def render_direct_log_form():
    """Renders the incident log form directly after student selection."""
    student = get_student_by_id(st.session_state.selected_student_id)
    if student:
        col_title, col_back = st.columns([4, 1])
        with col_title:
            st.markdown(f"## Quick Incident Log (Student: **{student['name']}**)")
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


# --- Page Rendering Functions ---

def render_student_profile(student: Dict[str, str]):
    """Renders the detailed student profile and history."""
    st.title(f"Student Profile: {student['name']}")
    st.markdown(f"**Grade:** {student['grade']} | **Profile Status:** {student['profile_status']}")
    st.markdown("---")

    # Mock Data Dashboard
    log_df = generate_mock_log_data(student['id'])
    
    if not log_df.empty:
        st.subheader("Incident Data Overview")
        
        # 1. Incident Count by Day
        incident_counts = log_df['Date'].value_counts().rename('Count').reset_index()
        incident_counts.columns = ['Date', 'Count']
        fig_count = px.bar(
            incident_counts, 
            x='Date', 
            y='Count', 
            title='Incidents by Date',
            template=PLOTLY_THEME
        )
        st.plotly_chart(fig_count, use_container_width=True)

        # 2. Behavior Type Frequency
        behavior_counts = log_df['Behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig_behav = px.pie(
            behavior_counts, 
            names='Behavior', 
            values='Count', 
            title='Behavior Type Frequency',
            template=PLOTLY_THEME
        )
        st.plotly_chart(fig_behav, use_container_width=True)

        st.subheader("Recent Incident Log")
        st.dataframe(log_df[['Timestamp', 'Behavior', 'Level', 'Duration (min)', 'Reported By']], use_container_width=True)
    else:
        st.info("No mock incident data available for this student. Use the Quick Incident Log to start tracking.")

    st.markdown("---")
    if st.button("⬅ Back to Landing", key="back_from_profile"):
        navigate_to('landing')

def render_landing_page():
    """Renders the main selection page."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")

    col_log, col_view = st.columns(2)

    with col_log:
        st.subheader("1. Quick Incident Log Entry")
        st.markdown("Select a student below to start a two-step ABCH incident log.")
        
        # Student Selection for Quick Log
        selected_student_for_log_name = st.selectbox(
            "Select Student for Log",
            options=[{'id': None, 'name': '--- Select a Student ---'}] + MOCK_STUDENTS,
            format_func=lambda x: x['name'],
            key="student_log_select"
        )
        
        if selected_student_for_log_name and selected_student_for_log_name['id']:
            if st.button(f"Start Log for {selected_student_for_log_name['name']}"):
                navigate_to('direct_log_form', selected_student_for_log_name['id'])

    with col_view:
        st.subheader("2. View Profiles & Data")
        st.markdown("Access profiles, intervention plans, and detailed data dashboards.")
        
        # Student Selection for Profile View
        selected_student_for_profile_name = st.selectbox(
            "Select Student for Profile View",
            options=[{'id': None, 'name': '--- Select a Student ---'}] + MOCK_STUDENTS,
            format_func=lambda x: x['name'],
            key="student_profile_select"
        )
        
        if selected_student_for_profile_name and selected_student_for_profile_name['id']:
            if st.button(f"View Profile for {selected_student_for_profile_name['name']}"):
                navigate_to('student_profile', selected_student_for_profile_name['id'])
                
    st.markdown("---")
    st.subheader("3. Staff Area / Admin")
    if st.button("Go to Staff Resources/Reports"):
        navigate_to('staff_area')
        
def render_staff_area():
    """Renders the staff/admin area (Placeholder)."""
    st.title("Staff & Admin Area")
    st.markdown("---")
    st.info("This section would contain global reports, staff management tools, and settings.")
    if st.button("⬅ Back to Landing", key="back_from_staff"):
        navigate_to('landing')


# --- Main App Execution ---
def main():
    """The main function to drive the Streamlit application logic."""
    
    # Initialize session state for navigation if not present
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
        
    # Main routing logic
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'student_profile':
        if st.session_state.selected_student_id:
            student = get_student_by_id(st.session_state.selected_student_id)
            if student:
                render_student_profile(student)
            else:
                st.error("Student not found.")
                navigate_to('landing')
        else:
            navigate_to('landing')
    elif st.session_state.current_page == 'direct_log_form':
        # This is the new incident log page
        render_direct_log_form()
    elif st.session_state.current_page == 'staff_area':
        render_staff_area()
    else:
        st.error("Page not found. Returning to landing.")
        navigate_to('landing')

if __name__ == '__main__':
    main()
