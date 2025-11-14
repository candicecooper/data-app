import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from functools import wraps
import traceback

# --- ERROR HANDLING SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(AppError):
    """Raised when data validation fails"""
    pass

def handle_errors(user_message: str = "An error occurred"):
    """Decorator to catch and handle errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{func.__name__}: {e.message}", exc_info=True)
                st.error(e.user_message)
                return None
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                st.error(f"{user_message}. Please try again or contact support.")
                with st.expander("Error Details"):
                    st.code(str(e))
                return None
        return wrapper
    return decorator

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

VALID_PAGES = ['landing', 'direct_log_form', 'critical_incident_abch']

# --- 2. GLOBAL HELPERS & CORE LOGIC FUNCTIONS ---

def navigate_to(page: str, student_id: Optional[str] = None):
    """Changes the current page in session state with error handling."""
    try:
        if page not in VALID_PAGES:
            raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")
        
        st.session_state.current_page = page
        if student_id:
            st.session_state.selected_student_id = student_id
        st.rerun()
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        st.error("Navigation failed. Returning to main page.")
        st.session_state.current_page = 'landing'
        st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, str]]:
    """Safely retrieves student data."""
    try:
        if not student_id:
            logger.warning("get_student_by_id called with empty student_id")
            return None
        
        student = next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)
        
        if not student:
            logger.warning(f"Student not found: {student_id}")
        
        return student
    except Exception as e:
        logger.error(f"Error retrieving student {student_id}: {e}")
        return None

def get_active_staff(include_special=False) -> List[Dict[str, Any]]:
    """Returns a list of active staff for selection."""
    try:
        return [s for s in MOCK_STAFF if s['active'] and not s['special']]
    except Exception as e:
        logger.error(f"Error retrieving staff list: {e}")
        return []

def get_staff_name_by_id(staff_id: str) -> str:
    """Returns staff name based on ID."""
    try:
        staff = next((s for s in MOCK_STAFF if s['id'] == staff_id), None)
        return staff['name'] if staff else "Unknown Staff"
    except Exception as e:
        logger.error(f"Error retrieving staff name: {e}")
        return "Unknown Staff"

def get_session_window(incident_time: time) -> str:
    """Calculates the Session window based on the incident time."""
    try:
        T_MORNING_START = time(9, 0, 0)
        T_MORNING_END = time(11, 0, 0)
        T_MIDDLE_START = time(11, 0, 1)
        T_MIDDLE_END = time(13, 0, 0)
        T_AFTERNOON_START = time(13, 0, 1)
        T_AFTERNOON_END = time(14, 45, 0)

        if T_MORNING_START <= incident_time <= T_MORNING_END:
            return "Morning (9:00am - 11:00am)"
        elif T_MIDDLE_START <= incident_time <= T_MIDDLE_END:
            return "Middle (11:01am - 1:00pm)"
        elif T_AFTERNOON_START <= incident_time <= T_AFTERNOON_END:
            return "Afternoon (1:01pm - 2:45pm)"
        else:
            return "Outside School Hours (N/A)"
    except Exception as e:
        logger.error(f"Error calculating session window: {e}")
        return "Unknown Session"

def generate_hypothesis_from_context(context: str, behavior: str) -> str:
    """Generates hypothesis based on context and behavior description."""
    try:
        context_lower = context.lower()
        behavior_lower = behavior.lower()
        
        # Escape-related keywords
        if any(word in context_lower for word in ['demand', 'instruction', 'asked to', 'told to', 'transition', 'task']):
            return "Escape/Avoidance (escaping demand or task)"
        
        # Attention-related keywords
        if any(word in context_lower for word in ['ignored', 'attention', 'staff away', 'peer', 'alone']):
            return "Access to Attention (seeking staff or peer attention)"
        
        # Tangible-related keywords
        if any(word in context_lower for word in ['denied', 'wanted', 'preferred', 'item', 'activity']):
            return "Access to Tangible (obtaining item/activity)"
        
        # Sensory-related keywords
        if any(word in context_lower for word in ['sensory', 'noise', 'loud', 'crowded', 'stimulation']):
            return "Sensory (seeking or escaping sensory input)"
        
        return "Function unclear - requires more observation"
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return "Unable to determine function"

def generate_hypothesis(antecedent: str, support_type: str) -> str:
    """Generates a preliminary hypothesis for low-severity incidents."""
    try:
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
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return "Unable to generate hypothesis at this time."

# --- VALIDATION FUNCTIONS ---

def validate_incident_form(location, reported_by, behavior_type, severity_level, incident_date, incident_time):
    """Validates incident log form data."""
    errors = []
    
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    
    if not isinstance(reported_by, dict) or reported_by.get('id') is None:
        errors.append("Please select a Staff Member")
    
    if behavior_type == "--- Select Behavior ---":
        errors.append("Please select a Behavior Type")
    
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    
    if not incident_date:
        errors.append("Date is required")
    
    if not incident_time:
        errors.append("Time is required")
    
    if errors:
        raise ValidationError(
            "Form validation failed",
            "Please correct the following:\n" + "\n".join([f"• {e}" for e in errors])
        )

def validate_abch_form(context, location, behavior_desc, consequence,
                       manager_notify, parent_notify):
    """Validates critical incident ABCH form."""
    errors = []
    
    if not location or location.strip() == "":
        errors.append("Location is required")
    
    if not context or context.strip() == "":
        errors.append("Context is required")
    
    if not behavior_desc or behavior_desc.strip() == "":
        errors.append("Behavior Description (What did the student do?) is required")
    
    if not consequence or consequence.strip() == "":
        errors.append("Consequences (What happened after?) is required")
    
    if not manager_notify:
        errors.append("Line Manager notification must be confirmed")
    
    if not parent_notify:
        errors.append("Emergency Contact notification must be confirmed")
    
    if errors:
        raise ValidationError(
            "ABCH form validation failed",
            "Please correct the following:\n" + "\n".join([f"• {e}" for e in errors])
        )

# --- 3. FORM RENDERING FUNCTIONS ---

@handle_errors("Unable to load incident log form")
def render_enhanced_log_form(student: Dict[str, str]):
    """Renders the comprehensive, single-step incident log form."""
    
    st.markdown(f"## Quick Incident Log (Student: **{student['name']}**)")
    st.markdown("---")

    with st.form("enhanced_incident_log_form"):
        st.markdown("### 1. Incident Details")
        
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
        
        session_window = get_session_window(incident_time)
        st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 20px; border-radius: 6px; background-color: #333; color: #fff;">
                <span style="font-weight: bold;">Calculated Session:</span> {session_window}
            </div>
        """, unsafe_allow_html=True)
        
        col_staff, col_behavior = st.columns(2)
        with col_staff:
            reported_by = st.selectbox(
                "Reported By (Staff Member)",
                options=[{'id': None, 'name': '--- Select Staff ---'}] + get_active_staff(),
                format_func=lambda x: x['name'],
                key="reported_by_obj"
            )

        with col_behavior:
            behavior_type = st.selectbox(
                "Primary Behavior Type", 
                options=["--- Select Behavior ---"] + BEHAVIORS_FBA,
                key="behavior_type_input"
            )

        st.markdown("### 2. Context & Intervention Data")
        
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
            
        st.markdown("---")
        severity_level = st.slider(
            "Severity Level (1: Minor, 5: Extreme/Critical)",
            min_value=1, max_value=5, value=1, step=1,
            key="severity_level"
        )
        
        st.text_area("Any Additional Information (Optional):", key="description_input", height=150)

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
            try:
                # Validate form
                validate_incident_form(
                    location, reported_by, behavior_type, 
                    severity_level, incident_date, incident_time
                )
                
                # Build preliminary data
                time_str = incident_time.strftime("%I:%M:%S %p")
                
                preliminary_data = {
                    "id": str(uuid.uuid4()),
                    "student_id": student['id'],
                    "date": incident_date.strftime("%Y-%m-%d"),
                    "time": time_str, 
                    "session": session_window,
                    "location": location,
                    "reported_by_name": reported_by['name'],
                    "reported_by_id": reported_by['id'],
                    "behavior_type": behavior_type,
                    "antecedent": antecedent,
                    "intervention": intervention,
                    "support_type": type_of_support,
                    "severity": severity_level,
                    "description": st.session_state.description_input,
                }
                
                if severity_level >= 3:
                    st.session_state.preliminary_abch_data = preliminary_data
                    navigate_to('critical_incident_abch', student['id'])
                else:
                    log_entry = preliminary_data.copy()
                    log_entry["is_critical"] = False
                    
                    st.success(f"Incident Log for {student['name']} saved successfully! Time recorded as: {time_str}")
                    st.balloons()
                    st.json(log_entry)
                    
            except ValidationError as e:
                st.error(e.user_message)
            except Exception as e:
                logger.error(f"Error submitting incident form: {e}", exc_info=True)
                st.error("An unexpected error occurred while saving the log. Please try again.")

@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    """Renders the detailed Critical Incident (ABCH) form with data continuity."""
    
    preliminary_data = st.session_state.get('preliminary_abch_data')
    student = get_student_by_id(st.session_state.get('selected_student_id', ''))
    
    if not preliminary_data:
        st.error("Error: Critical incident data not found. Returning to log selection.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return
    
    if not student:
        st.error("Error: Student data not found. Returning to log selection.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return

    st.title(f"🚨 Critical Incident Report (ABCH) - {student['name']}")

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
    st.markdown("## Critical Incident Form (A → B → C → H)")
    
    with st.form("abch_detailed_form"):
        # Initialize behavior chain counter if not exists
        if 'behavior_chain_count' not in st.session_state:
            st.session_state.behavior_chain_count = 1
        
        # Render behavior chains
        for chain_idx in range(st.session_state.behavior_chain_count):
            st.markdown(f"### Behavior Episode {chain_idx + 1}")
            
            # Row 1: Antecedent (Trigger) - Location and Context
            st.markdown("#### **Antecedent (Trigger)**")
            ant_col1, ant_col2 = st.columns(2)
            
            with ant_col1:
                st.markdown("##### Location")
                if chain_idx == 0:
                    # First chain uses preliminary data
                    location_display = st.text_input(
                        "Location",
                        value=preliminary_data['location'],
                        key=f"abch_location_{chain_idx}",
                        label_visibility="collapsed"
                    )
                else:
                    location_display = st.text_input(
                        "Location",
                        key=f"abch_location_{chain_idx}",
                        placeholder="Enter location for this episode",
                        label_visibility="collapsed"
                    )
            
            with ant_col2:
                st.markdown("##### Context")
                context_text = st.text_area(
                    "Context",
                    key=f"abch_context_{chain_idx}",
                    height=100,
                    placeholder="What was happening? Student's state/mood? Setting/activity?",
                    label_visibility="collapsed"
                )
            
            # Row 2: Behaviour - Time and What Student Did
            st.markdown("#### **Behaviour**")
            beh_col1, beh_col2 = st.columns(2)
            
            with beh_col1:
                st.markdown("##### Time")
                if chain_idx == 0:
                    # First chain uses preliminary data but is amendable
                    time_display = st.time_input(
                        "Time",
                        value=datetime.strptime(preliminary_data['time'], "%I:%M:%S %p").time(),
                        key=f"abch_time_{chain_idx}",
                        label_visibility="collapsed"
                    )
                else:
                    time_display = st.time_input(
                        "Time",
                        key=f"abch_time_{chain_idx}",
                        label_visibility="collapsed"
                    )
            
            with beh_col2:
                st.markdown("##### What did the student do?")
                behavior_desc = st.text_area(
                    "Behavior",
                    key=f"abch_behavior_{chain_idx}",
                    height=100,
                    placeholder="Observable description of the behavior (what you saw/heard)",
                    label_visibility="collapsed"
                )
            
            # Row 3: Consequences and Hypothesis
            cons_hyp_col1, cons_hyp_col2 = st.columns(2)
            
            with cons_hyp_col1:
                st.markdown("#### **Consequences**")
                st.markdown("##### What happened after the behaviour? How did people react?")
                consequence_text = st.text_area(
                    "Consequences",
                    key=f"abch_consequence_{chain_idx}",
                    height=100,
                    placeholder="Staff response, peer reactions, environmental changes",
                    label_visibility="collapsed"
                )
            
            with cons_hyp_col2:
                st.markdown("#### **Hypothesis**")
                st.markdown("##### Best guess behaviour function")
                
                # Auto-generate hypothesis based on context if available
                if context_text and behavior_desc:
                    # Simple function determination based on keywords
                    hypothesis_text = generate_hypothesis_from_context(context_text, behavior_desc)
                    st.info(f"**Suggested Function:** {hypothesis_text}")
                
                hypothesis_override = st.text_area(
                    "Hypothesis",
                    key=f"abch_hypothesis_{chain_idx}",
                    height=100,
                    placeholder="Best guess at why the behavior occurred (function)",
                    label_visibility="collapsed"
                )
            
            if chain_idx < st.session_state.behavior_chain_count - 1:
                st.markdown("---")
        
        # Add another behavior episode button
        if st.form_submit_button("➕ Add Another Behavior Episode"):
            st.session_state.behavior_chain_count += 1
            st.rerun()
        
        st.markdown("---")
        st.markdown("---")
        
        # Outcomes & Review Section (below chronology)
        st.markdown("### Outcomes & Review (H)")
        
        outcome_col1, outcome_col2 = st.columns(2)
        
        with outcome_col1:
            st.text_area(
                "Follow-up / Post-Incident Reflection",
                key="abch_follow_up",
                height=150,
                placeholder="Debrief held, action plans, scheduled meetings, support provided"
            )
        
        with outcome_col2:
            st.markdown("##### Mandatory Notifications/Outcomes")
            st.checkbox("Line Manager Notified (Required)", key="abch_manager_notify")
            st.checkbox("Emergency Contact Notified (Required)", key="abch_parent_notify")
            st.checkbox("Physical Restraint Used/Reported", key="abch_restraint_used")
            st.checkbox("External Agency (e.g., SAPOL/Ambulance) Contacted", key="abch_external_contact")

        st.markdown("---")
        
        col_cancel, col_submit = st.columns([1, 3])
        with col_cancel:
            if st.form_submit_button("Cancel & Go Back"):
                st.session_state.preliminary_abch_data = None
                navigate_to('landing')
                
        with col_submit:
            if st.form_submit_button("Finalize Critical Incident Report (ABCH)", type="primary"):
                try:
                    # Validate ABCH form - now checking first behavior chain
                    validate_abch_form(
                        st.session_state.get('abch_context_0', ''),
                        st.session_state.get('abch_location_0', ''),
                        st.session_state.get('abch_behavior_0', ''),
                        st.session_state.get('abch_consequence_0', ''),
                        st.session_state.get('abch_manager_notify', False),
                        st.session_state.get('abch_parent_notify', False)
                    )
                    
                    # Build final log entry with behavior chains
                    final_log_entry = preliminary_data.copy()
                    
                    # Collect all behavior chains
                    behavior_chains = []
                    for chain_idx in range(st.session_state.get('behavior_chain_count', 1)):
                        chain_data = {
                            "location": st.session_state.get(f'abch_location_{chain_idx}', ''),
                            "context": st.session_state.get(f'abch_context_{chain_idx}', ''),
                            "time": st.session_state.get(f'abch_time_{chain_idx}', ''),
                            "behavior": st.session_state.get(f'abch_behavior_{chain_idx}', ''),
                            "consequence": st.session_state.get(f'abch_consequence_{chain_idx}', ''),
                            "hypothesis": st.session_state.get(f'abch_hypothesis_{chain_idx}', '')
                        }
                        behavior_chains.append(chain_data)
                    
                    final_log_entry.update({
                        "is_critical": True,
                        "behavior_chains": behavior_chains,
                        "abch_follow_up": st.session_state.get('abch_follow_up', ''),
                        "outcome_manager_notified": st.session_state.abch_manager_notify,
                        "outcome_parent_notified": st.session_state.abch_parent_notify,
                        "outcome_restraint_used": st.session_state.get('abch_restraint_used', False),
                        "outcome_external_contact": st.session_state.get('abch_external_contact', False),
                    })
                    
                    st.success(f"Critical Incident Report for {student['name']} FINALIZED and Saved!")
                    st.balloons()
                    st.json(final_log_entry)
                    
                    # Clear session state
                    st.session_state.preliminary_abch_data = None
                    st.session_state.behavior_chain_count = 1
                    
                except ValidationError as e:
                    st.error(e.user_message)
                except Exception as e:
                    logger.error(f"Error finalizing ABCH report: {e}", exc_info=True)
                    st.error("An unexpected error occurred while saving the report. Please try again.")

# --- 4. NAVIGATION AND PAGE STRUCTURE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    """Renders the main selection page."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")

    col_log, col_view = st.columns(2)

    with col_log:
        st.subheader("1. Quick Incident Log Entry")
        st.markdown("Select a student below to start the enhanced incident log.")
        
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

@handle_errors("Unable to load incident log form")
def render_direct_log_form():
    """Renders the enhanced log form directly after student selection."""
    student_id = st.session_state.get('selected_student_id')
    
    if not student_id:
        st.error("No student selected.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return
    
    student = get_student_by_id(student_id)
    
    if not student:
        st.error("Student not found. Please return to the main page and try again.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return
        
    col_title, col_back = st.columns([4, 1])
    with col_back:
        if st.button("⬅ Change Student", key="back_to_direct_select_form"):
            navigate_to('landing')
    
    render_enhanced_log_form(student)

# --- 5. MAIN APP EXECUTION ---

def main():
    """The main function to drive the Streamlit application logic."""
    
    try:
        # Initialize session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'landing'
            
        # Main routing logic
        current_page = st.session_state.get('current_page', 'landing')
        
        if current_page == 'landing':
            render_landing_page()
        elif current_page == 'direct_log_form':
            render_direct_log_form()
        elif current_page == 'critical_incident_abch':
            render_critical_incident_abch_form()
        else:
            logger.warning(f"Unknown page: {current_page}")
            st.error("Unknown page. Returning to main page.")
            st.session_state.current_page = 'landing'
            st.rerun()
            
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        st.error("A critical error occurred. Please refresh the page.")
        with st.expander("Error Details"):
            st.code(str(e))

if __name__ == '__main__':
    main()
