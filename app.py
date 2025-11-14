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

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
]
MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'profile_status': 'Complete', 'program': 'SY', 'archived': False},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'profile_status': 'Draft', 'program': 'PY', 'archived': False},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'profile_status': 'Pending', 'program': 'SY', 'archived': False},
    {'id': 'stu_004', 'name': 'Emma T.', 'grade': 'R', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_005', 'name': 'Oliver S.', 'grade': 'Y2', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_006', 'name': 'Sophie M.', 'grade': 'Y5', 'profile_status': 'Complete', 'program': 'PY', 'archived': False},
    # Archived students
    {'id': 'stu_arch_001', 'name': 'Jackson P.', 'grade': 'Y10', 'profile_status': 'Complete', 'program': 'SY', 'archived': True},
    {'id': 'stu_arch_002', 'name': 'Ava L.', 'grade': 'Y6', 'profile_status': 'Complete', 'program': 'PY', 'archived': True},
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

VALID_PAGES = ['landing', 'program_students', 'direct_log_form', 'critical_incident_abch', 'student_analysis', 'admin_portal']

# --- MOCK DATA GENERATION ---

def generate_mock_incidents():
    """Generates mock incident data for testing the analysis section."""
    incidents = []
    
    # Generate 15 incidents for Izack N. (high frequency student)
    for i in range(15):
        incident_date = (datetime.now() - timedelta(days=random.randint(1, 45))).strftime('%Y-%m-%d')
        incident_time = datetime.now().replace(
            hour=random.randint(8, 14),
            minute=random.choice([0, 15, 30, 45]),
            second=0
        ).time()
        
        # Calculate session
        if time(9, 0) <= incident_time <= time(11, 0):
            session = 'Morning (9:00am - 11:00am)'
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = 'Middle (11:01am - 1:00pm)'
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = 'Afternoon (1:01pm - 2:45pm)'
        else:
            session = 'Outside School Hours (N/A)'
        
        is_critical = random.choice([True, True, False])
        severity = random.choice([4, 5]) if is_critical else random.choice([1, 2, 3])
        
        incident = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_001',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M:%S'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': session,
            'location': random.choice(['JP Classroom', 'Yard', 'Gate', 'Playground', 'JP Spill Out']),
            'reported_by_name': 'Emily Jones (JP)',
            'reported_by_id': 's1',
            'behavior_type': random.choice(['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)']),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(SUPPORT_TYPES),
            'severity': severity,
            'description': f"Incident {i+1}: {'Critical incident requiring detailed follow-up.' if is_critical else 'Standard incident log.'}",
            'is_critical': is_critical,
        }
        incidents.append(incident)
    
    # Generate 5 incidents for Mia K.
    for i in range(5):
        incident_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        incident_time = datetime.now().replace(
            hour=random.randint(8, 14),
            minute=random.choice([0, 15, 30, 45]),
            second=0
        ).time()
        
        if time(9, 0) <= incident_time <= time(11, 0):
            session = 'Morning (9:00am - 11:00am)'
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = 'Middle (11:01am - 1:00pm)'
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = 'Afternoon (1:01pm - 2:45pm)'
        else:
            session = 'Outside School Hours (N/A)'
        
        incident = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_002',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M:%S'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': session,
            'location': random.choice(['PY Classroom', 'Library', 'Yard']),
            'reported_by_name': 'Daniel Lee (PY)',
            'reported_by_id': 's2',
            'behavior_type': random.choice(['Verbal Refusal', 'Out of Seat', 'Non-Compliance']),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(SUPPORT_TYPES),
            'severity': random.choice([1, 2, 3]),
            'description': f"Incident {i+1}: Standard log.",
            'is_critical': False,
        }
        incidents.append(incident)
    
    # Generate 3 incidents for Liam B.
    for i in range(3):
        incident_date = (datetime.now() - timedelta(days=random.randint(1, 20))).strftime('%Y-%m-%d')
        incident_time = datetime.now().replace(
            hour=random.randint(8, 14),
            minute=random.choice([0, 15, 30, 45]),
            second=0
        ).time()
        
        if time(9, 0) <= incident_time <= time(11, 0):
            session = 'Morning (9:00am - 11:00am)'
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = 'Middle (11:01am - 1:00pm)'
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = 'Afternoon (1:01pm - 2:45pm)'
        else:
            session = 'Outside School Hours (N/A)'
        
        incident = {
            'id': str(uuid.uuid4()),
            'student_id': 'stu_003',
            'date': incident_date,
            'time': incident_time.strftime('%H:%M:%S'),
            'day': datetime.strptime(incident_date, '%Y-%m-%d').strftime('%A'),
            'session': session,
            'location': random.choice(['SY Classroom', 'Yard', 'Admin']),
            'reported_by_name': 'Sarah Chen (SY)',
            'reported_by_id': 's3',
            'behavior_type': random.choice(['Verbal Refusal', 'Property Destruction']),
            'antecedent': random.choice(ANTECEDENTS_NEW),
            'intervention': random.choice(INTERVENTIONS),
            'support_type': random.choice(SUPPORT_TYPES),
            'severity': random.choice([2, 3]),
            'description': f"Incident {i+1}: Standard log.",
            'is_critical': random.choice([True, False]),
        }
        incidents.append(incident)
    
    return incidents

# Initialize incidents in session state
if 'incidents' not in st.session_state:
    st.session_state.incidents = generate_mock_incidents()

# --- 2. GLOBAL HELPERS & CORE LOGIC FUNCTIONS ---

def navigate_to(page: str, student_id: Optional[str] = None, program: Optional[str] = None):
    """Changes the current page in session state with error handling."""
    try:
        if page not in VALID_PAGES:
            raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")
        
        st.session_state.current_page = page
        if student_id:
            st.session_state.selected_student_id = student_id
        if program:
            st.session_state.selected_program = program
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
        
        if any(word in context_lower for word in ['demand', 'instruction', 'asked to', 'told to', 'transition', 'task']):
            return "Escape/Avoidance (escaping demand or task)"
        
        if any(word in context_lower for word in ['ignored', 'attention', 'staff away', 'peer', 'alone']):
            return "Access to Attention (seeking staff or peer attention)"
        
        if any(word in context_lower for word in ['denied', 'wanted', 'preferred', 'item', 'activity']):
            return "Access to Tangible (obtaining item/activity)"
        
        if any(word in context_lower for word in ['sensory', 'noise', 'loud', 'crowded', 'stimulation']):
            return "Sensory (seeking or escaping sensory input)"
        
        return "Function unclear - requires more observation"
    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return "Unable to determine function"

def send_line_manager_notification(incident_data: dict, student: dict):
    """Simulates sending email notification to Line Manager."""
    try:
        line_manager_email = "candice.cooper330@schools.sa.edu.au"
        staff_name = incident_data.get('staff_certified_by', 'Staff Member')
        student_name = student.get('name', 'Student')
        incident_date = incident_data.get('date', 'Unknown Date')
        incident_id = incident_data.get('id', 'N/A')
        
        logger.info(f"EMAIL NOTIFICATION SENT TO LINE MANAGER:")
        logger.info(f"To: {line_manager_email}")
        logger.info(f"Subject: CRITICAL INCIDENT REPORT - {student_name} - {incident_date}")
        logger.info(f"Incident ID: {incident_id}")
        logger.info(f"Reported by: {staff_name}")
        
        email_body = f"""
        CRITICAL INCIDENT REPORT - ACTION REQUIRED
        
        A Critical Incident Report has been submitted and requires your review and approval.
        
        Student: {student_name}
        Date of Incident: {incident_date}
        Reported By: {staff_name}
        Incident ID: {incident_id}
        Submission Time: {incident_data.get('staff_certification_timestamp', 'N/A')}
        
        REQUIRED ACTIONS:
        1. Review the attached Critical Incident Report
        2. Amend any details if necessary
        3. Complete the Administration Only section (Safety Plan, Other Outcomes)
        4. Sign off with your name in the Manager Signature field
        5. Confirm final approval
        
        Please log into the Behaviour Support System to review and approve this report.
        
        This is an automated notification. Please do not reply to this email.
        """
        
        logger.info(f"Email Body: {email_body}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending line manager notification: {e}", exc_info=True)
        return False

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

def validate_abch_form(context, location, behavior_desc, consequence, manager_notify, parent_notify):
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

def get_time_slot(t):
    """Converts time to the nearest half-hour slot for heatmap."""
    if isinstance(t, str):
        t = datetime.strptime(t, '%H:%M').time()
    minutes = t.minute
    hour = t.hour
    if minutes < 30:
        return f"{hour:02d}:00"
    else:
        return f"{hour:02d}:30"

def generate_bpp_report_content(student, latest_plan_incident, df):
    """Generates the structured text content for the full BPP report."""
    total_incidents = len(df)
    critical_incidents = df.get('is_critical', pd.Series([False])).sum() if not df.empty else 0
    most_freq_behaviour = df['behavior_type'].mode().iloc[0] if not df.empty and 'behavior_type' in df.columns else 'N/A'
    peak_risk = df['severity'].max() if not df.empty and 'severity' in df.columns else 'N/A'
    
    if most_freq_behaviour in ['Physical Aggression', 'Property Destruction'] or peak_risk >= 4:
        cpi_stage = "High-Risk: Acting Out (Danger)"
        cpi_response = "Nonviolent Physical Crisis Intervention (where appropriate) followed by Therapeutic Rapport."
    elif peak_risk == 3:
        cpi_stage = "Peak Risk: Defensive"
        cpi_response = "Use Paraverbal Communication to reduce tension. Offer choices and avoid power struggles."
    else:
        cpi_stage = "Low-Risk: Questioning / Refusal"
        cpi_response = "Use Supportive language and provide clear direction."
    
    content = f'''
# BEHAVIOUR PROFILE PLAN
## Student: {student['name']}
**Grade:** {student['grade']}
**Date Generated:** {datetime.now().strftime('%Y-%m-%d')}

---

## 1. Summary of Key Behavioural Data

| Metric | Value |
| :--- | :--- |
| **Total Incidents (Last 60 Days)** | {total_incidents} |
| **Critical Incidents** | {critical_incidents} |
| **Most Frequent Behaviour** | {most_freq_behaviour} |
| **Highest Risk Level** | {peak_risk} |

---

## 2. Crisis Prevention Institute (CPI) Protocol
**Current Stage:** {cpi_stage}
**Recommended Response:** {cpi_response}

---

## 3. Proactive Strategies (Berry Street Education Model)

### A. Body (Regulation)
Implement Mindfulness exercises for 3 minutes before transitions.

### B. Brain (Skill-Building)
Teach social scripts to manage primary triggers.

### C. Belonging (Relational)
Implement Check-in/Check-out system with designated Safe Adult.

### D. Gifting (Purpose)
Provide responsibility that allows positive contribution.

---

*This Behaviour Profile Plan is a dynamic document and must be reviewed after any critical incident.*
'''
    return content

def render_data_analysis(student, df):
    """Renders comprehensive data analysis with Plotly charts."""
    st.subheader(f"📊 Comprehensive Data Analysis for: **{student['name']}**")
    
    if df.empty:
        st.info("No incident data to analyze yet.")
        return
    
    # Preprocessing
    if 'time' in df.columns:
        df['time_obj'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.time
        df['time_slot'] = df['time_obj'].apply(get_time_slot)
        df['hour'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.hour
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if 'day' in df.columns:
        df['day'] = pd.Categorical(df['day'], categories=day_order, ordered=True)
    
    # Metrics
    total_incidents = len(df)
    critical_incidents = df.get('is_critical', pd.Series([False])).sum()
    
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.metric("Total Incidents Logged", total_incidents)
    col_t2.metric("Critical Incidents", critical_incidents)
    col_t3.metric("Criticality Rate", f"{critical_incidents / total_incidents * 100:.1f}%" if total_incidents > 0 else "0.0%")
    
    st.markdown("---")
    st.markdown("#### Key Incident Tracking Visualizations")
    
    # Time Slot Heatmap
    if 'time_slot' in df.columns:
        st.markdown("##### 🕰️ Incident Frequency by Time Slot")
        time_slot_counts = df.groupby('time_slot').size().reset_index(name='Count')
        all_time_slots = [f"{h:02d}:{m:02d}" for h in range(8, 15) for m in [0, 30]] + ["15:00"]
        time_slot_counts_full = pd.DataFrame({'time_slot': all_time_slots}).merge(time_slot_counts, on='time_slot', how='left').fillna(0)
        
        fig_heatmap = px.bar(
            time_slot_counts_full,
            x='time_slot',
            y='Count',
            title='Incidents by Half-Hour Time Slot',
            template=PLOTLY_THEME,
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_heatmap.update_layout(xaxis={'tickangle': -45})
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Severity Breakdown
    col_graph2, col_graph3 = st.columns(2)
    
    with col_graph2:
        if 'severity' in df.columns:
            st.markdown("##### ⭐ Severity Breakdown")
            severity_counts = df['severity'].value_counts().reset_index()
            severity_counts.columns = ['Severity', 'Count']
            fig_severity = px.bar(
                severity_counts,
                x='Severity',
                y='Count',
                title='Incidents by Severity Level',
                template=PLOTLY_THEME,
                color_discrete_sequence=['#FF5733']
            )
            st.plotly_chart(fig_severity, use_container_width=True)
    
    with col_graph3:
        if 'location' in df.columns:
            st.markdown("##### 📍 Incidents by Location")
            location_counts = df['location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Count']
            fig_location = px.bar(
                location_counts,
                x='Location',
                y='Count',
                title='Incident Frequency by Location',
                template=PLOTLY_THEME,
                color_discrete_sequence=['#8E44AD']
            )
            fig_location.update_layout(xaxis={'tickangle': -45})
            st.plotly_chart(fig_location, use_container_width=True)
    
    # Day of Week
    if 'day' in df.columns:
        st.markdown("##### 📅 Incidents by Day of the Week")
        day_counts = df.groupby('day').size().reset_index(name='Count')
        fig_day = px.bar(
            day_counts,
            x='day',
            y='Count',
            title='Incident Frequency by Day',
            template=PLOTLY_THEME,
            color_discrete_sequence=['#3498DB']
        )
        st.plotly_chart(fig_day, use_container_width=True)
    
    # Clinical Analysis
    st.markdown("---")
    st.markdown("## 🧠 Clinical Analysis and Recommendations")
    
    most_freq_behaviour = df['behavior_type'].mode().iloc[0] if 'behavior_type' in df.columns and not df.empty else 'N/A'
    peak_risk = df['severity'].max() if 'severity' in df.columns and not df.empty else 'N/A'
    
    st.markdown("### 1. Key Patterns and Findings")
    st.markdown(f"""
    Based on analysis of **{total_incidents}** incidents:
    * **Core Behaviour:** {most_freq_behaviour}
    * **Peak Risk Level:** {peak_risk}
    * **Critical Incidents:** {critical_incidents} ({critical_incidents / total_incidents * 100:.1f}% of total)
    """)
    
    st.markdown("### 2. Trauma-Informed Practice (Berry Street Model)")
    st.markdown("""
    * **Body:** Implement sensory check-ins and calm down signals
    * **Brain:** Teach replacement behaviours explicitly  
    * **Belonging:** Daily check-in/check-out with safe adult
    * **Gifting:** Identify contribution opportunities
    """)

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
            location = st.selectbox("Location", options=LOCATIONS, key="location_input")
        
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
            behavior_type = st.selectbox("Primary Behavior Type", options=["--- Select Behavior ---"] + BEHAVIORS_FBA, key="behavior_type_input")

        st.markdown("### 2. Context & Intervention Data")
        
        col_ant, col_int, col_sup = st.columns(3)
        with col_ant:
            antecedent = st.selectbox("Antecedent (What happened IMMEDIATELY before?)", options=["--- Select Antecedent ---"] + ANTECEDENTS_NEW, key="antecedent_input")
        with col_int:
            intervention = st.selectbox("Intervention Applied (Staff action)", options=["--- Select Intervention ---"] + INTERVENTIONS, key="intervention_input")
        with col_sup:
            type_of_support = st.selectbox("Type of Support Student was Receiving", options=SUPPORT_TYPES, key="support_type_input")
            
        st.markdown("---")
        severity_level = st.slider("Severity Level (1: Minor, 5: Extreme/Critical)", min_value=1, max_value=5, value=1, step=1, key="severity_level")
        
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
                validate_incident_form(location, reported_by, behavior_type, severity_level, incident_date, incident_time)
                
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
    
    with st.form("critical_incident_form_unique"):
        if 'behavior_chain_count' not in st.session_state:
            st.session_state.behavior_chain_count = 1
        
        for chain_idx in range(st.session_state.behavior_chain_count):
            st.markdown(f"### Behavior Episode {chain_idx + 1}")
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown("#### **Antecedent**")
                st.markdown("##### Location")
                if chain_idx == 0:
                    st.text_input("Location", value=preliminary_data['location'], key=f"abch_location_{chain_idx}", label_visibility="collapsed")
                else:
                    st.text_input("Location", key=f"abch_location_{chain_idx}", placeholder="Enter location", label_visibility="collapsed")
            
            with col2:
                st.markdown("#### **(Trigger)**")
                st.markdown("##### Context")
                context_text = st.text_area("Context", key=f"abch_context_{chain_idx}", height=200, placeholder="What was happening? Student's state/mood?", label_visibility="collapsed")
            
            with col3:
                st.markdown("#### **Behaviour**")
                st.markdown("##### Time")
                if chain_idx == 0:
                    st.time_input("Time", value=datetime.strptime(preliminary_data['time'], "%I:%M:%S %p").time(), key=f"abch_time_{chain_idx}", label_visibility="collapsed")
                else:
                    st.time_input("Time", key=f"abch_time_{chain_idx}", label_visibility="collapsed")
            
            with col4:
                st.markdown("#### ** **")
                st.markdown("##### What did student do?")
                behavior_desc = st.text_area("Behavior", key=f"abch_behavior_{chain_idx}", height=200, placeholder="Observable behavior (what you saw/heard)", label_visibility="collapsed")
            
            with col5:
                st.markdown("#### **Consequences**")
                st.markdown("##### What happened after?")
                st.text_area("Consequences", key=f"abch_consequence_{chain_idx}", height=200, placeholder="How did people react? What changed?", label_visibility="collapsed")
            
            with col6:
                st.markdown("#### **Hypothesis**")
                st.markdown("##### Best guess function")
                
                if context_text and behavior_desc:
                    hypothesis_text = generate_hypothesis_from_context(context_text, behavior_desc)
                    st.info(f"{hypothesis_text}", icon="💡")
                
                st.text_area("Hypothesis", key=f"abch_hypothesis_{chain_idx}", height=150, placeholder="Function of behavior", label_visibility="collapsed")
            
            if chain_idx < st.session_state.behavior_chain_count - 1:
                st.markdown("---")
        
        if st.form_submit_button("➕ Add Another Behavior Episode"):
            st.session_state.behavior_chain_count += 1
            st.rerun()
        
        st.markdown("---")
        st.markdown("---")
        
        st.markdown("### INTENDED OUTCOMES")
        
        st.markdown("#### Time-Stamped Outcomes")
        st.markdown("*Only fill in the time for outcomes you select with the checkbox*")
        outcome_time_col1, outcome_time_col2, outcome_time_col3 = st.columns([1, 4, 1])
        
        with outcome_time_col1:
            st.markdown("**TIME**")
        with outcome_time_col2:
            st.markdown("**OUTCOMES**")
        with outcome_time_col3:
            st.markdown("**Select**")
        
        outcome_options = [
            "Send Home. Parent / Caregiver notified via Phone Call. Conversation documented in file",
            "Student Leaving supervised areas / leaving school grounds",
            "Sexualised behaviour",
            "Incident – student to student",
            "Complaint by co-located school / member of public",
            "Property damage",
            "Stealing",
            "Toileting issue",
            "ED155: Staff Injury (submit with report)",
            "ED155: Student injury (submit with report)"
        ]
        
        for idx, outcome in enumerate(outcome_options):
            col_t, col_o, col_c = st.columns([1, 4, 1])
            with col_t:
                st.time_input(f"Time {idx}", key=f"outcome_time_{idx}", label_visibility="collapsed", value=None)
            with col_o:
                st.markdown(outcome)
            with col_c:
                st.checkbox("", key=f"outcome_check_{idx}", label_visibility="collapsed")
        
        st.markdown("---")
        
        col_emergency, col_internal = st.columns(2)
        
        with col_emergency:
            st.markdown("#### Emergency Services")
            st.markdown("**SAPOL**")
            sapol_col1, sapol_col2 = st.columns([3, 1])
            with sapol_col1:
                st.checkbox("Drug possession", key="sapol_drug")
                st.checkbox("Assault", key="sapol_assault")
                st.checkbox("Absconding", key="sapol_absconding")
                st.checkbox("Removal", key="sapol_removal")
                st.checkbox("Call Out", key="sapol_callout")
                st.checkbox("Stealing", key="sapol_stealing")
                st.checkbox("Vandalism", key="sapol_vandalism")
            with sapol_col2:
                st.text_input("Report number:", key="sapol_report_number")
            
            st.markdown("**SA Ambulance Services**")
            st.checkbox("Call out", key="ambulance_callout")
            st.checkbox("Taken to Hospital", key="ambulance_hospital")
        
        with col_internal:
            st.markdown("#### Incident Internally Managed")
            st.checkbox("Restorative Session", key="internal_restorative")
            st.checkbox("Community Service", key="internal_community")
            st.checkbox("Re-Entry", key="internal_reentry")
            st.text_area("Re-Entry Details:", key="internal_reentry_details", placeholder="E.g., A TAC meeting will be held to discuss solutions to support the student.", height=80)
            st.checkbox("Case Review", key="internal_case_review")
            st.checkbox("Make-up Time", key="internal_makeup")
            st.text_input("Other", key="internal_other")
        
        st.markdown("---")
        
        st.markdown("#### Mandatory Notifications")
        notif_col1, notif_col2, notif_col3 = st.columns(3)
        
        with notif_col1:
            st.checkbox("**Notified Line Manager of Critical Incident** (Required)", key="abch_manager_notify")
        with notif_col2:
            st.checkbox("**Notified Parent/Caregiver of Critical Incident** (Required)", key="abch_parent_notify")
        with notif_col3:
            st.checkbox("**Copy of Critical Incident in student file**", key="abch_file_copy")
        
        st.markdown("---")
        st.markdown("#### Staff Certification")
        
        reporting_staff_name = preliminary_data.get('reported_by_name', 'Staff Member')
        st.info(f"**Completing Staff Member:** {reporting_staff_name}")
        
        st.markdown("""
        By checking the box below, I certify that:
        - All information provided in this Critical Incident Report is accurate to the best of my knowledge
        - All mandatory notifications have been completed
        - I have documented the incident according to school policy
        """)
        
        st.checkbox(f"**I, {reporting_staff_name}, certify that all information is correct and complete**", key="staff_certification_check")
        
        if st.session_state.get('staff_certification_check', False):
            st.success("✓ Form certified by staff member")
        
        st.markdown("---")
        
        st.markdown("#### ADMINISTRATION ONLY")
        st.info("📝 This section is completed by Line Manager/Manager during review process")
        admin_col1, admin_col2 = st.columns(2)
        
        with admin_col1:
            st.text_input("Line Manager Signature:", key="admin_line_manager_sig", placeholder="To be completed by Line Manager")
            st.text_input("Manager Signature:", key="admin_manager_sig", placeholder="To be completed by Manager")
        
        with admin_col2:
            st.text_area("Safety and Risk Plan: To be developed / reviewed:", key="admin_safety_plan", height=100, placeholder="To be completed during management review")
            st.text_area("Other outcomes to be pursued by Management:", key="admin_other_outcomes", height=100, placeholder="To be completed during management review")
        
        st.markdown("---")
        st.markdown("### Submit Report")
        
        col_cancel, col_space, col_submit = st.columns([1, 1, 2])
        
        with col_cancel:
            cancel_clicked = st.form_submit_button("❌ Cancel & Go Back", use_container_width=True)
                
        with col_submit:
            submit_clicked = st.form_submit_button("📧 Send to Line Manager & Log Incident", type="primary", use_container_width=True)
        
        if cancel_clicked:
            st.session_state.preliminary_abch_data = None
            st.session_state.behavior_chain_count = 1
            navigate_to('landing')
        
        if submit_clicked:
            can_submit = (
                st.session_state.get('abch_manager_notify', False) and 
                st.session_state.get('abch_parent_notify', False) and
                st.session_state.get('staff_certification_check', False)
            )
            
            if not can_submit:
                st.error("⚠️ Please complete all mandatory requirements")
            
            if can_submit:
                try:
                    validate_abch_form(
                        st.session_state.get('abch_context_0', ''),
                        st.session_state.get('abch_location_0', ''),
                        st.session_state.get('abch_behavior_0', ''),
                        st.session_state.get('abch_consequence_0', ''),
                        True, True
                    )
                    
                    final_log_entry = preliminary_data.copy()
                    behavior_chains = []
                    for chain_idx in range(st.session_state.get('behavior_chain_count', 1)):
                        behavior_chains.append({
                            "location": st.session_state.get(f'abch_location_{chain_idx}', ''),
                            "context": st.session_state.get(f'abch_context_{chain_idx}', ''),
                            "time": str(st.session_state.get(f'abch_time_{chain_idx}', '')),
                            "behavior": st.session_state.get(f'abch_behavior_{chain_idx}', ''),
                            "consequence": st.session_state.get(f'abch_consequence_{chain_idx}', ''),
                            "hypothesis": st.session_state.get(f'abch_hypothesis_{chain_idx}', '')
                        })
                    
                    final_log_entry.update({
                        "is_critical": True,
                        "behavior_chains": behavior_chains,
                        "staff_certified_by": reporting_staff_name,
                        "staff_certification_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "Pending Line Manager Review"
                    })
                    
                    send_line_manager_notification(final_log_entry, student)
                    
                    st.success(f"✅ Critical Incident Report LOGGED!")
                    st.info("📧 Email sent to candice.cooper330@schools.sa.edu.au")
                    st.balloons()
                    
                    st.session_state.preliminary_abch_data = None
                    st.session_state.behavior_chain_count = 1
                    
                except ValidationError as e:
                    st.error(e.user_message)
                except Exception as e:
                    logger.error(f"Error: {e}", exc_info=True)
                    st.error("An error occurred. Please try again.")

@handle_errors("Unable to load landing page")
def render_landing_page():
    """Renders the main selection page."""
    
    # Custom CSS for sleek landing page
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #888;
        margin-bottom: 3rem;
    }
    .program-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .program-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    .program-card h2 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    .program-card p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .quick-action-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .quick-action-card:hover {
        transform: translateY(-3px);
    }
    .admin-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .admin-card:hover {
        transform: translateY(-3px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title
    st.markdown('<h1 class="main-title">Behaviour Support & Data Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Select a program to view students or access quick actions</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Program Selection Cards
    st.markdown("### 📚 Select Program")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="program-card">
            <h2>JP</h2>
            <p>Junior Primary</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='JP')
    
    with col2:
        st.markdown("""
        <div class="program-card">
            <h2>PY</h2>
            <p>Primary Years</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='PY')
    
    with col3:
        st.markdown("""
        <div class="program-card">
            <h2>SY</h2>
            <p>Senior Years</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='SY')
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col_quick1, col_quick2 = st.columns(2)
    
    with col_quick1:
        st.markdown("""
        <div class="quick-action-card">
            <h3 style="color: white; margin: 0;">📝 Quick Incident Log</h3>
            <p style="color: rgba(255, 255, 255, 0.9); margin-top: 0.5rem;">Log an incident without program navigation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick log selection
        all_active_students = [s for s in MOCK_STUDENTS if not s.get('archived', False)]
        student_options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x['name'],
            key="quick_log_student",
            label_visibility="collapsed"
        )
        
        if selected_student and selected_student['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to('direct_log_form', student_id=selected_student['id'])
    
    with col_quick2:
        st.markdown("""
        <div class="admin-card">
            <h3 style="color: white; margin: 0;">🔐 Admin Portal</h3>
            <p style="color: rgba(255, 255, 255, 0.9); margin-top: 0.5rem;">System administration and reports</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Access Admin Portal", key="admin_btn", use_container_width=True, type="primary"):
            navigate_to('admin_portal')

@handle_errors("Unable to load program students")
def render_program_students():
    """Renders the student list for a selected program."""
    program = st.session_state.get('selected_program', 'JP')
    
    # Header with back button
    col_title, col_back = st.columns([4, 1])
    with col_title:
        program_names = {'JP': 'Junior Primary', 'PY': 'Primary Years', 'SY': 'Senior Years'}
        st.title(f"{program_names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back to Home", key="back_to_home"):
            navigate_to('landing')
    
    st.markdown("---")
    
    # Tabs for Current and Archived students
    tab1, tab2 = st.tabs(["📚 Current Students", "📦 Archived Students"])
    
    with tab1:
        current_students = [s for s in MOCK_STUDENTS if s.get('program') == program and not s.get('archived', False)]
        
        if not current_students:
            st.info(f"No current students in the {program} program.")
        else:
            st.markdown(f"### Current Students ({len(current_students)})")
            
            # Display students in a grid
            cols_per_row = 3
            for i in range(0, len(current_students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, student in enumerate(current_students[i:i+cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {student['name']}")
                            st.markdown(f"**Grade:** {student['grade']}")
                            
                            # Get incident count
                            incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                            st.metric("Incidents", incident_count)
                            
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button("👁️ View", key=f"view_{student['id']}", use_container_width=True):
                                    navigate_to('student_analysis', student_id=student['id'])
                            with col_log:
                                if st.button("📝 Log", key=f"log_{student['id']}", use_container_width=True):
                                    navigate_to('direct_log_form', student_id=student['id'])
    
    with tab2:
        archived_students = [s for s in MOCK_STUDENTS if s.get('program') == program and s.get('archived', False)]
        
        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("These students have completed the program and their records are read-only.")
            
            # Display archived students
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**Profile Status:** {student.get('profile_status', 'N/A')}")
                    
                    incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                    st.metric("Total Incidents", incident_count)
                    
                    if st.button("View Historical Data", key=f"view_arch_{student['id']}"):
                        navigate_to('student_analysis', student_id=student['id'])

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
        st.markdown("Select a student to view their behavior profile and data analysis.")
        
        options = [{'id': None, 'name': '--- Select a Student ---'}] + MOCK_STUDENTS
        selected_student_for_view = st.selectbox(
            "Select Student for Analysis",
            options=options,
            format_func=lambda x: x['name'],
            key="student_view_select"
        )
        
        if selected_student_for_view and selected_student_for_view['id']:
            if st.button(f"View Profile & Data for {selected_student_for_view['name']}"):
                navigate_to('student_analysis', selected_student_for_view['id'])

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

@handle_errors("Unable to load student analysis")
def render_student_analysis():
    """Renders the student analysis page with data and BPP."""
    student_id = st.session_state.get('selected_student_id')
    
    if not student_id:
        st.error("No student selected.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return
    
    student = get_student_by_id(student_id)
    
    if not student:
        st.error("Student not found.")
        if st.button("Return to Main Page"):
            navigate_to('landing')
        return
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"Student Profile: {student['name']}")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')
    
    st.markdown("---")
    
    # Get student incidents
    incidents = [i for i in st.session_state.get('incidents', []) if i.get('student_id') == student_id]
    
    if not incidents:
        st.info("No incident data logged for this student yet.")
        return
    
    df = pd.DataFrame(incidents)
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📊 Data Analysis", "📄 Behaviour Profile Plan"])
    
    with tab1:
        render_data_analysis(student, df)
    
    with tab2:
        st.markdown("### Behaviour Profile Plan")
        
        # Find latest critical incident
        critical_incidents = [i for i in incidents if i.get('is_critical', False)]
        latest_plan_incident = critical_incidents[-1] if critical_incidents else None
        
        if latest_plan_incident and not df.empty:
            bpp_content = generate_bpp_report_content(student, latest_plan_incident, df)
            st.markdown(bpp_content)
            
            st.markdown("---")
            # Download button
            filename = f"BPP_Plan_{student['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            st.download_button(
                label="⬇ Download Full Behaviour Profile Plan",
                data=bpp_content,
                file_name=filename,
                mime="text/plain"
            )
        else:
            st.warning("A Behaviour Profile Plan requires at least one Critical Incident to generate detailed analysis.")

def main():
    """The main function to drive the Streamlit application logic."""
    
    try:
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'landing'
            
        current_page = st.session_state.get('current_page', 'landing')
        
        if current_page == 'landing':
            render_landing_page()
        elif current_page == 'program_students':
            render_program_students()
        elif current_page == 'direct_log_form':
            render_direct_log_form()
        elif current_page == 'critical_incident_abch':
            render_critical_incident_abch_form()
        elif current_page == 'student_analysis':
            render_student_analysis()
        elif current_page == 'admin_portal':
            st.title("🔐 Admin Portal")
            st.info("Admin portal functionality - to be discussed and implemented next")
            if st.button("⬅ Back to Home"):
                navigate_to('landing')
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
