import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
from typing import List, Dict, Any, Optional

# --- 1. CONFIGURATION AND CONSTANTS ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PLOTLY_THEME = 'plotly_dark'

# Existing Mock Data
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
]
MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'profile_status': 'Complete'},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'profile_status': 'Draft'},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'profile_status': 'Pending'},
]
BEHAVIOR_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']
BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Other - Specify'] 


# CONSTANTS FOR ENHANCED LOG
ANTECEDENTS_NEW = [
    "Requested to transition activity",
    "Given instruction/demand (Academic)",
    "Given instruction/demand (Non-Academic)",
    "Peer conflict/Teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory over-stimulation (Noise/Lights)",
    "Access to preferred item/activity denied"
]

INTERVENTIONS = [
    "Prompted use of coping skill (e.g., breathing)",
    "Proximity control/Non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break/Choice of task",
    "Used planned ignoring of minor behavior",
    "Staff de-escalation script/Verbal coaching",
    "Applied physical intervention",
    "Called for staff support/Backup"
]

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class/assembly)"
]

# LOCATION CONSTANTS
LOCATIONS = [
    "--- Select Location ---",
    "JP Classroom",
    "JP Spill Out",
    "PY Classroom",
    "PY Spill Out",
    "SY Classroom",
    "SY Spill Out",
    "Student Kitchen",
    "Admin",
    "Gate",
    "Library",
    "Van/Kia",
    "Swimming",
    "Yard",
    "Playground",
    "Toilets",
    "Excursion",
    "Other"
]


# --- 2. GLOBAL HELPERS & CORE LOGIC FUNCTIONS ---

def navigate_to(page: str, student_id: Optional[str] = None):
    """Changes the current page in session state."""
    st.session_state.current_page = page
    if student_id:
        st.session_state.selected_student_id = student_id
    st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, str]]:
    """Mocks fetching student data."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_active_staff(include_special=False) -> List[Dict[str, Any]]:
    """Returns a list of active staff for selection."""
    return [s for s in MOCK_STAFF if s['active'] and not s['special']]

def get_staff_name_by_id(staff_id: str) -> str:
    """Returns staff name based on ID."""
    staff = next((s for s in MOCK_STAFF if s['id'] == staff_id), None)
    return staff['name'] if staff else "Unknown Staff"

def get_session_window(incident_time: time) -> str:
    """Calculates the Session window based on the incident time."""
    T_MORNING_START = time(9, 0, 0)
    T_MORNING_END = time(11, 0, 0)      # 11:00:00
    T_MIDDLE_START = time(11, 0, 1)     # 11:00:01
    T_MIDDLE_END = time(13, 0, 0)       # 1:00 PM
    T_AFTERNOON_START = time(13, 0, 1)  # 1:00:01 PM
    T_AFTERNOON_END = time(14, 45, 0)   # 2:45 PM

    if T_MORNING_START <= incident_time <= T_MORNING_END:
        return "Morning (9:00am - 11:00am)"
    elif T_MIDDLE_START <= incident_time <= T_MIDDLE_END:
        return "Middle (11:01am - 1:00pm)"
    elif T_AFTERNOON_START <= incident_time <= T_AFTERNOON_END:
        return "Afternoon (1:01pm - 2:45pm)"
    else:
        return "Outside School Hours (N/A)"

def generate_hypothesis(antecedent: str, support_type: str) -> str:
    """Generates a preliminary hypothesis for low-severity incidents."""

    # FBA Function mapping
    function_map = {
        "Requested to transition activity": "Escape from a demand",
        "Given instruction/demand (Academic)": "Escape from a demand",
        "Given instruction/demand (Non-Academic)": "Escape from a demand",
        "Peer conflict/Teasing": "Access to Tangible or Attention",
        "Staff attention shifted away": "Access to Attention (Staff)",
        "Unstructured free time (Recess/Lunch)": "Sensory Stimulation/Automatic Reinforcement",
        "Sensory over-stimulation (Noise/Lights)": "Escape from sensory input",
        "Access to preferred item/activity denied": "Access to Tangible (Item/Activity)"
    }
    
    function = function_map.get(antecedent, "Unknown Function")

    hypothesis = (
        f"The preliminary hypothesis suggests the behavior was primarily driven by **{function}**. "
        f"The student was in a **{support_type}** setting when the antecedent, **'{antecedent}'**, occurred. "
        "This indicates a need to reinforce replacement skills during similar conditions."
    )
    return hypothesis

# --- 3. FORM RENDERING FUNCTIONS (FIXED) ---

def render_enhanced_log_form(student: Dict[str, str]):
    """Renders the comprehensive, single-step incident log form."""
    
    st.markdown(f"## Quick Incident Log (Student: **{student['name']}**)")
    st.markdown("---")

    with st.form("enhanced_incident_log_form"):
        st.markdown("### 1. Incident Details")
        
        # Date, Time, and Location (NOW DROPDOWN)
        col_date, col_time, col_loc = st.columns(3)
        with col_date:
            incident_date = st.date_input("Date of Incident", datetime.now().date(), key="incident_date")
        with col_time:
            default_time = datetime.now().time()
            incident_time = st.time_input("Time of Incident (e.g., 2:30 PM)", default_time, key="incident_time")
        with col_loc:
            location = st.selectbox(
                "Location", 
                options=LOCATIONS, 
                key="location_input"
            )
        
        # Calculate and display Session
        session_window = get_session_window(incident_time)
        st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 20px; border-radius: 6px; background-color: #333; color: #fff;">
                <span style="font-weight: bold;">Calculated Session:</span> {session_window}
            </div>
        """, unsafe_allow_html=True)
        
        # Staff and Behavior
        col_staff, col_behavior = st.columns(2)
        with col_staff:
            # FIX: Removed the on_change callback and temporary state manipulation
            reported_by = st.selectbox(
                "Reported By (Staff Member)",
                options=[{'id': None, 'name': '--- Select Staff ---'}] + get_active_staff(),
                format_func=lambda x: x['name'],
                key="reported_by_obj" # The returned value is the selected dictionary object
            )

        with col_behavior:
            behavior_type = st.selectbox(
                "Primary Behavior Type", 
                options=["--- Select Behavior ---"] + BEHAVIORS_FBA,
                key="behavior_type_input"
            )

        st.markdown("### 2. Context & Intervention Data")
        
        # New Dropdowns: Antecedent, Intervention, Support Type
        col_ant, col_int, col_sup = st.columns(3)
        with col_ant:
            antecedent = st.selectbox(
                "Antecedent (What happened IMMEDIATELY before?)",
                options=["--- Select Antecedent ---"] + ANTECEDENTS_NEW,
                key="antecedent_input"
            )
        with col_int:
            intervention = st.selectbox(
                "Intervention Applied (Staff action)",
                options=["--- Select Intervention ---"] + INTERVENTIONS,
                key="intervention_input"
            )
        with col_sup:
            type_of_support = st.selectbox(
                "Type of Support Student was Receiving",
                options=SUPPORT_TYPES,
                key="support_type_input"
            )
            
        # Severity Level (Drives Conditional Logic)
        st.markdown("---")
        severity_level = st.slider(
            "Severity Level (1: Minor, 5: Extreme/Critical)",
            min_value=1, max_value=5, value=1, step=1,
            key="severity_level"
        )
        
        # Optional Additional Information
        st.text_area("Any Additional Information (Optional):", key="description_input", height=150)

        # --- Conditional Logic Section for display ONLY (actual flow handled on submit) ---
        st.markdown("---")

        if severity_level >= 3:
            st.warning(f"⚠️ **CRITICAL INCIDENT TRIGGERED (Severity Level {severity_level})**")
            st.info("Upon submission, you will be taken to the detailed ABCH Critical Incident Report form.")
            
        elif severity_level in [1, 2]:
            st.info(f"✅ **Moderate Incident (Severity Level {severity_level})**")
            st.markdown("#### Automated Preliminary Hypothesis")

            if antecedent != "--- Select Antecedent ---" and type_of_support:
                hypothesis = generate_hypothesis(antecedent, type_of_support)
                st.markdown(f"""
                    <div style="padding: 15px; border-radius: 8px; border: 1px solid #1e88e5; background-color: #2a3a4c; color: #fff;">
                    <p style="font-weight: bold; color: #64b5f6;">Suggested Hypothesis:</p>
                    <p>{hypothesis}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("— *Select an Antecedent to generate a preliminary FBA hypothesis.*")
        
        st.markdown("---")

        submit_button = st.form_submit_button("Submit Incident Log / Proceed to Critical Report")
        
        if submit_button:
            # UPDATED VALIDATION CHECK for dropdowns
            # We now use the 'reported_by' variable directly, which holds the selected dictionary object
            if location == "--- Select Location ---" or reported_by['id'] is None or behavior_type == "--- Select Behavior ---":
                 st.error("Please select a valid Location, Staff Member, and Behavior Type before submitting.")
            else:
                # --- PRELIMINARY DATA CAPTURE ---
                time_str = incident_time.strftime("%I:%M:%S %p")
                
                preliminary_data = {
                    "id": str(uuid.uuid4()),
                    "student_id": student['id'],
                    "date": incident_date.strftime("%Y-%m-%d"),
                    "time": time_str, 
                    "session": session_window,
                    "location": location,
                    "reported_by_name": reported_by['name'], # Capture name for display
                    "reported_by_id": reported_by['id'],
                    "behavior_type": behavior_type,
                    "antecedent": antecedent,
                    "intervention": intervention,
                    "support_type": type_of_support,
                    "severity": severity_level,
                    "description": st.session_state.description_input,
                }
                
                if severity_level >= 3:
                    # CRITICAL INCIDENT FLOW: Save data to state and navigate to ABCH form
                    st.session_state.preliminary_abch_data = preliminary_data
                    navigate_to('critical_incident_abch', student['id'])
                else:
                    # MODERATE/MINOR INCIDENT FLOW: Save immediately
                    log_entry = preliminary_data.copy()
                    log_entry["is_critical"] = False
                    
                    st.success(f"Incident Log for {student['name']} saved successfully! Time recorded as: {time_str}")
                    st.balloons()
                    st.json(log_entry)
                    # navigate_to('landing') # Optional: uncomment to return to landing page

def render_critical_incident_abch_form():
    """Renders the detailed Critical Incident (ABCH) form with data continuity."""
    
    preliminary_data = st.session_state.get('preliminary_abch_data')
    student = get_student_by_id(st.session_state.selected_student_id)
    
    if not preliminary_data or not student:
        st.error("Error: Critical incident data not found. Returning to log selection.")
        navigate_to('landing')
        return

    st.title(f"🚨 Critical Incident Report (ABCH) - {student['name']}")

    # --- Preliminary Data Panel (Top) ---
    st.markdown("### Preliminary Incident Data (From Quick Log)")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Date & Time", f"{preliminary_data['date']} @ {preliminary_data['time']}")
    with col2:
        st.metric("Location", preliminary_data['location'])
    with col3:
        st.metric("Reported By", preliminary_data['reported_by_name'])
    with col4:
        st.metric("Severity", f"Level {preliminary_data['severity']}", delta="CRITICAL", delta_color="inverse")
    with col5:
        st.metric("Initial Antecedent", preliminary_data['antecedent'])
        
    st.markdown("---")
    st.markdown("## ABCH Chronology & Detailed Narrative (A → B → C → H)")
    
    with st.form("abch_detailed_form"):
        # --- ABCH Columns (Left to Right Flow) ---
        abch_col_a, abch_col_b, abch_col_c, abch_col_h = st.columns(4)

        with abch_col_a:
            st.markdown("#### 1. Context & Antecedent (A)")
            st.markdown(f"**Initial Antecedent:** `{preliminary_data['antecedent']}`")
            st.text_area(
                "Context: State/Mood of Student Prior to Incident (required)",
                key="abch_context_prior",
                height=150,
                placeholder="E.g., Visibly agitated after lunch, requested alone time, had a minor peer argument 5 minutes prior."
            )
            st.text_area(
                "Specific Antecedent/Trigger (A): What was the *final* trigger?",
                key="abch_antecedent_final",
                height=150,
                placeholder="E.g., Staff member asked student to put phone away. No warning signs were noted."
            )

        with abch_col_b:
            st.markdown("#### 2. Behavior Episode (B)")
            st.markdown(f"**Primary Behavior:** `{preliminary_data['behavior_type']}`")
            st.text_area(
                "Observable Description (B): What the behavior looked like (required)",
                key="abch_behavior_description",
                height=350,
                placeholder="E.g., Student slammed hands on desk, yelled 'No!', grabbed the nearest textbook and threw it 5m across the room, then ran out the door. Duration: ~4 minutes."
            )
            
        with abch_col_c:
            st.markdown("#### 3. Intervention & Consequence (C)")
            st.markdown(f"**Initial Intervention:** `{preliminary_data['intervention']}`")
            st.text_area(
                "Detailed Staff Response (C): Step-by-step actions taken (required)",
                key="abch_staff_response",
                height=200,
                placeholder="E.g., Step 1: Staff member stood 3m away and lowered voice. Step 2: Offered a choice (break card vs. quiet work). Step 3: When behavior escalated, staff calmly exited room and called for support. Support staff arrived 2 minutes later."
            )
            st.text_area(
                "Immediate Consequence: How was the situation resolved/concluded?",
                key="abch_immediate_consequence",
                height=120,
                placeholder="E.g., Student returned to room after 10 minutes and apologized. Student was required to clean up damaged property."
            )

        with abch_col_h:
            st.markdown("#### 4. Outcomes & Review (H)")
            st.text_area(
                "Follow-up / History (H): Post-Incident Reflection/Action Plan",
                key="abch_follow_up",
                height=100,
                placeholder="E.g., Debrief held with student and staff member. Behaviour Support Coordinator was informed. Scheduled a follow-up meeting with parents."
            )
            st.markdown("##### Mandatory Notifications/Outcomes")
            st.checkbox("Line Manager Notified (Required)", key="abch_manager_notify")
            st.checkbox("Emergency Contact Notified (Required)", key="abch_parent_notify")
            st.checkbox("Physical Restraint Used/Reported", key="abch_restraint_used")
            st.checkbox("External Agency (e.g., SAPOL/Ambulance) Contacted", key="abch_external_contact")

        st.markdown("---")
        
        # Final Action Row
        col_cancel, col_submit = st.columns([1, 3])
        with col_cancel:
            # We use a button press to clear temporary data and navigate back
            if st.form_submit_button("Cancel & Go Back"):
                st.session_state.preliminary_abch_data = None
                navigate_to('landing')
                
        with col_submit:
            if st.form_submit_button("Finalize Critical Incident Report (ABCH)", type="primary"):
                # --- FINAL ABCH SAVE LOGIC ---
                if not all([st.session_state.get('abch_context_prior'), 
                            st.session_state.get('abch_antecedent_final'), 
                            st.session_state.get('abch_behavior_description'), 
                            st.session_state.get('abch_staff_response')]):
                    st.error("Please fill out all required fields (marked 'required' in sections 1, 2, and 3).")
                elif not (st.session_state.abch_manager_notify and st.session_state.abch_parent_notify):
                    st.error("You must confirm Line Manager and Emergency Contact notification to finalize this Critical Incident Report.")
                else:
                    final_log_entry = preliminary_data.copy()
                    final_log_entry.update({
                        "is_critical": True,
                        "abch_context_prior": st.session_state.abch_context_prior,
                        "abch_antecedent_final": st.session_state.abch_antecedent_final,
                        "abch_behavior_description": st.session_state.abch_behavior_description,
                        "abch_staff_response": st.session_state.abch_staff_response,
                        "abch_immediate_consequence": st.session_state.abch_immediate_consequence,
                        "abch_follow_up": st.session_state.abch_follow_up,
                        "outcome_manager_notified": st.session_state.abch_manager_notify,
                        "outcome_parent_notified": st.session_state.abch_parent_notify,
                        "outcome_restraint_used": st.session_state.abch_restraint_used,
                        "outcome_external_contact": st.session_state.abch_external_contact,
                    })
                    
                    st.success(f"Critical Incident Report for {student['name']} FINALIZED and Saved!")
                    st.balloons()
                    st.json(final_log_entry)
                    # Clear temporary data and return to landing
                    st.session_state.preliminary_abch_data = None
                    navigate_to('landing')


# --- 4. NAVIGATION AND PAGE STRUCTURE ---

def render_landing_page():
    """Renders the main selection page."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")

    col_log, col_view = st.columns(2)

    with col_log:
        st.subheader("1. Quick Incident Log Entry")
        st.markdown("Select a student below to start the enhanced incident log.")
        
        # Student Selection for Quick Log
        options = [{'id': None, 'name': '--- Select a Student ---'}] + MOCK_STUDENTS
        selected_student_for_log = st.selectbox(
            "Select Student for Log",
            options=options,
            format_func=lambda x: x['name'],
            key="student_log_select"
        )
        
        if selected_student_for_log and selected_student_for_log['id']:
            if st.button(f"Start Enhanced Log for {selected_student_for_log['name']}"):
                navigate_to('direct_log_form', selected_student_for_log['id'])

    with col_view:
        st.subheader("2. View Profiles & Data")
        st.info("Profiles & Data visualization not implemented in this version.")

def render_direct_log_form():
    """Renders the enhanced log form directly after student selection."""
    student = get_student_by_id(st.session_state.selected_student_id)
    if student:
        col_title, col_back = st.columns([4, 1])
        with col_back:
            if st.button("⬅ Change Student", key="back_to_direct_select_form"):
                navigate_to('landing')
        
        # Call the new enhanced form
        render_enhanced_log_form(student)
        
    else:
        st.error("No student selected.")
        navigate_to('landing')


# --- 5. MAIN APP EXECUTION ---

def main():
    """The main function to drive the Streamlit application logic."""
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'landing'
        
    # Main routing logic
    if st.session_state.current_page == 'landing':
        render_landing_page()
    elif st.session_state.current_page == 'direct_log_form':
        render_direct_log_form()
    elif st.session_state.current_page == 'critical_incident_abch':
        render_critical_incident_abch_form()

if __name__ == '__main__':
    main()
