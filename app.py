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
# Assuming this code is inserted within def render_incident_log_form(student):

# --- ABCH CHRONOLOGY SECTION START ---

if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []

st.markdown("### 2. Critical Incident Chronology (A-B-C-H)")
st.markdown("""
    **Log the sequence of events chronologically.**
    Each entry details the time and the Antecedent (A), Behavior (B), or Consequence (C) that occurred.
""")

col_add, col_sort_label = st.columns([1, 4])
with col_add:
    # Button to add a new event entry
    if st.button("➕ Add Entry", key="add_chronology_entry", type="primary"):
        # Add a new entry with a unique ID and current time default
        st.session_state.abch_chronology.append({
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().strftime("%H:%M"),
            'type': 'Antecedent',
            'detail': '',
            'staff_response': '',
            'staff_id': None
        })

# Reverse the list for display so the latest entry is at the top,
# but keep the internal list chronological for sorting before saving.
chronology_display = sorted(st.session_state.abch_chronology, key=lambda x: x['timestamp'], reverse=True)

if not chronology_display:
    st.info("No chronology entries added yet. Use 'Add Entry' to start logging the sequence.")

# Retrieve all staff names for the selectbox (using MOCK_STAFF assumed to be in scope)
all_staff_names = [s['name'] for s in MOCK_STAFF] 

# Loop through entries for editing
for i, entry in enumerate(chronology_display):
    # Find the original index in the session state list to safely update/delete
    original_index = next((j for j, item in enumerate(st.session_state.abch_chronology) if item['id'] == entry['id']), -1)

    if original_index == -1:
        continue 

    st.markdown(f"#### Event Log Entry {len(st.session_state.abch_chronology) - original_index}")
    
    # Use a unique key based on the original index/ID to allow editing and deletion
    key_prefix = f"abch_{original_index}_{entry['id'][:4]}"
    
    col_time, col_type, col_staff, col_delete = st.columns([2, 3, 4, 1])

    # Time Input (HH:MM)
    with col_time:
        current_time_str = st.text_input(
            "Time (HH:MM)", 
            value=st.session_state.abch_chronology[original_index]['timestamp'], 
            key=f"{key_prefix}_time",
            max_chars=5,
            help="E.g., 11:15"
        )
        st.session_state.abch_chronology[original_index]['timestamp'] = current_time_str

    # Type of Event (A, B, or C)
    with col_type:
        type_options = ['Antecedent', 'Behaviour', 'Consequence', 'Staff Intervention']
        current_type = st.session_state.abch_chronology[original_index]['type']
        new_type = st.selectbox(
            "Event Type",
            options=type_options,
            index=type_options.index(current_type) if current_type in type_options else 0,
            key=f"{key_prefix}_type"
        )
        st.session_state.abch_chronology[original_index]['type'] = new_type

    # Staff Involved in this specific step
    with col_staff:
        current_staff_id = st.session_state.abch_chronology[original_index]['staff_id']
        current_staff_name = next((s['name'] for s in MOCK_STAFF if s['id'] == current_staff_id), None)
        
        staff_index = all_staff_names.index(current_staff_name) if current_staff_name in all_staff_names else 0
        selected_staff_name = st.selectbox(
            "Staff Involved",
            options=all_staff_names,
            index=staff_index,
            key=f"{key_prefix}_staff"
        )
        # Map the selected name back to the ID for storage
        selected_staff_id = next((s['id'] for s in MOCK_STAFF if s['name'] == selected_staff_name), None)
        st.session_state.abch_chronology[original_index]['staff_id'] = selected_staff_id

    # Delete Button
    with col_delete:
        st.write(" ") # Spacer
        if st.button("🗑️", key=f"{key_prefix}_delete", help="Delete this entry"):
            st.session_state.abch_chronology.pop(original_index)
            st.rerun() # Rerun to update the display

    # Detail Text Area
    detail_key = f"{key_prefix}_detail"
    current_detail = st.session_state.abch_chronology[original_index]['detail']
    st.session_state.abch_chronology[original_index]['detail'] = st.text_area(
        f"Description of the {new_type}", 
        value=current_detail, 
        key=detail_key, 
        height=70
    )
    
    # Staff Response Text Area (if applicable)
    if new_type in ['Consequence', 'Staff Intervention']:
         response_key = f"{key_prefix}_response"
         current_response = st.session_state.abch_chronology[original_index]['staff_response']
         st.session_state.abch_chronology[original_index]['staff_response'] = st.text_area(
            "Staff Action/Response", 
            value=current_response, 
            key=response_key, 
            height=50
        )

    st.divider() # Visual separator between entries

# Final chronological sort before the form completes
st.session_state.abch_chronology = sorted(
    st.session_state.abch_chronology, 
    key=lambda x: datetime.strptime(x['timestamp'], "%H:%M") if len(x['timestamp']) == 5 else datetime.min
)
# --- ABCH CHRONOLOGY SECTION END ---

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

