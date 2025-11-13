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
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #F1F5F9;
    }

    /* Checkbox/Radio/Button Styling */
    .stCheckbox > label, .stRadio > label { color: #CBD5E1; }
    .stButton > button {
        border-radius: 8px;
        color: #F1F5F9;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stButton button:hover { background-color: #334155; }
    
    /* Primary Button */
    .stButton button[kind="primary"] { background-color: #3B82F6; border: none; }
    .stButton button[kind="primary"]:hover { background-color: #2563EB; }

    /* Custom Box Styling for Sections */
    .incident-section {
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1E293B;
    }
    .incident-section h3 {
        color: #93C5FD !important;
        margin-top: 0;
        margin-bottom: 15px;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- State Management and Navigation ---

def initialize_state():
    """Sets up initial session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing' # Default page
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'data' not in st.session_state:
        st.session_state.data = {
            'students': MOCK_STUDENTS,
            'incidents': MOCK_INCIDENTS
        }

def navigate_to(page, role=None, student_id=None):
    """Manages page navigation and state updates."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
    
    if student_id:
        student = get_student_by_id(student_id)
        st.session_state.student = student
    elif page in ['landing', 'staff_area']:
        st.session_state.student = None # Clear student context on return to main areas

    st.rerun()

# --- MOCK DATA ---

MOCK_STUDENTS = [
    {'id': 's_001', 'name': 'Alex Johnson', 'year': 5, 'teacher': 'Ms. Davies'},
    {'id': 's_002', 'name': 'Riley Chen', 'year': 8, 'teacher': 'Mr. Evans'},
    {'id': 's_003', 'name': 'Jordan Smith', 'year': 11, 'teacher': 'Dr. White'},
    {'id': 's_004', 'name': 'Mia Rodriguez', 'year': 2, 'teacher': 'Ms. Jones'},
]

MOCK_INCIDENTS = pd.DataFrame([
    {'id': uuid.uuid4(), 'student_id': 's_001', 'date_time': datetime(2025, 10, 15, 10, 30), 'behavior': 'Verbal Refusal', 'antecedent': 'Work Demand Placed', 'consequence': 'Staff Support', 'role': 'PY', 'notes': 'Refused to start math task.'},
    {'id': uuid.uuid4(), 'student_id': 's_001', 'date_time': datetime(2025, 10, 16, 14, 00), 'behavior': 'Aggression (Peer)', 'antecedent': 'Loud Environment', 'consequence': 'Time Out', 'role': 'JP', 'notes': 'Pushed a peer during recess.'},
    {'id': uuid.uuid4(), 'student_id': 's_002', 'date_time': datetime(2025, 10, 17, 9, 15), 'behavior': 'Elopement', 'antecedent': 'Transition (Area to Area)', 'consequence': 'Recovery', 'role': 'SY', 'notes': 'Left classroom during transition to library.'},
    {'id': uuid.uuid4(), 'student_id': 's_004', 'date_time': datetime(2025, 10, 18, 11, 45), 'behavior': 'Property Destruction', 'antecedent': 'Frustrated/Angry', 'consequence': 'Parent Contact', 'role': 'JP', 'notes': 'Tore up paper after failing a task.'},
])

# --- ABCH QUICK LOG CONSTANTS & MOCK STAFF ---

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Out-of-Area', 'Non-Compliance', 'Aggression (Staff)', 'Verbal Abuse', 'Defiance', 'Inappropriate Language', 'Other']

CONTEXTS = {
    'Routine Contexts': ['Arrival/Departure', 'Morning Session', 'Break Time', 'Transition (Class to Class)', 'Transition (Area to Area)', 'Specialist Lesson', 'Lunch Time', 'Recess Time', 'Independent Work', 'Small Group Work', 'Large Group Instruction', 'Free Choice Time', 'End of Day'],
    'Environmental Contexts': ['Loud Environment', 'Busy Area', 'Specific Staff Member Present', 'Specific Peer Present', 'Work Demand Placed', 'Change in Schedule', 'Unstructured Time'],
    'Physical/Emotional States': ['Tired/Fatigued', 'Hungry', 'Ill/Pain', 'Anxious/Overwhelmed', 'Excited/Overstimulated', 'Frustrated/Angry'],
    'Other': ['Undefined', 'Not Applicable']
}

WINDOW_OF_TOLERANCE_OPTS = {
    'Optimal': ['Engaged and calm', 'Participating in learning', 'Using coping skills effectively'],
    'Hyperarousal (Fight/Flight/Fright)': ['High energy, fidgeting, unable to settle', 'Agitated, irritable, or aggressive', 'Loud, hyper-vigilant, panicked'],
    'Hypoarousal (Freeze/Submit)': ['Withdrawn, quiet, disengaged', 'Slowed response, lethargic, sleepy', 'Blank expression, dissociating, avoiding eye contact']
}

HOW_TO_RESPOND_PLAN = {
    'Verbal De-escalation': ['Low-tone, slow voice', 'Use non-directive language', 'Offer choices (limited options)', 'Use humor (cautiously)'],
    'Physical/Environmental Strategies': ['Reduce noise/stimuli', 'Offer quiet space/break card', 'Proximity control', 'Visual supports/schedule check'],
    'Safety & Containment': ['Remove audience/peers', 'Safeguard property/others', 'Call for support (Walkie/Admin)'],
    'Post-Incident': ['Re-establish connection', 'Restitution/Repair', 'Return to planned activity']
}

CRITICAL_INCIDENT_OUTCOMES = {
    'Immediate Safety Actions': [
        ('o_a_send_home', 'Student sent home'),
        ('o_b_left_area', 'Student left school grounds/area (Elopement)'),
        ('o_c_assault', 'Assault on Staff/Peer'),
        ('o_d_property_damage', 'Significant Property Damage'),
        ('o_e_staff_injury', 'Staff Injury Requiring Medical Attention'),
        ('o_f_sapol_callout', 'SAPOL Call-Out'),
    ],
    'Medical/First Aid': [
        ('o_g_no_injury', 'No Injury Sustained'),
        ('o_h_minor_injury', 'Minor Injury Sustained (Band-Aid/Ice)'),
        ('o_i_first_aid_nurse', 'Required First Aid by Nurse/Staff'),
        ('o_j_first_aid_amb', 'Ambulance Called (Student)'),
        ('o_k_amb_staff', 'Ambulance Called (Staff)'),
    ],
    'Follow Up & Resolution': [
        ('o_l_debrief_staff', 'Staff Debrief Completed'),
        ('o_m_debrief_student', 'Student Debrief Completed'),
        ('o_n_contact_parent', 'Parent/Caregiver Contacted'),
        ('o_o_counsellor', 'Referral to School Counsellor'),
        ('o_p_admin_followup', 'Required Admin Follow-Up Meeting'),
        ('o_q_no_followup', 'No Further Follow-Up Required'),
    ],
    'Staff Intervention Level': [
        ('o_r_call_out_amb', 'Required Call-Out to Ambulance (Staff Decision)'), # Duplicates ambulance if needed
        ('o_s_restraint', 'Physical Restraint Used (Formal Training Required)'),
        ('o_t_containment', 'Contained to Area (Isolation/Seclusion)'),
        ('o_u_passive', 'Passive Blocking/Proximity Only'),
    ]
}

# --- Data Helpers ---

def get_student_by_id(student_id):
    """Retrieves student dictionary by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_incidents_by_student(student_id):
    """Retrieves all incidents for a given student."""
    return st.session_state.data['incidents'][st.session_state.data['incidents']['student_id'] == student_id].sort_values(by='date_time', ascending=False)

def add_incident(incident_data):
    """Adds a new incident to the mock data store."""
    incident_df = pd.DataFrame([incident_data])
    st.session_state.data['incidents'] = pd.concat([st.session_state.data['incidents'], incident_df], ignore_index=True)

def get_active_staff():
    """Returns a list of active staff names for dropdowns."""
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_staff_by_id(staff_id):
    """Retrieves staff member by ID (MOCK function)."""
    return next((s for s in MOCK_STAFF if s['id'] == staff_id), None)

# --- Components and Pages ---

def staff_header(title):
    """Renders a consistent page header with a back button."""
    col_btn, col_title = st.columns([1, 6])
    
    with col_btn:
        if st.button("⬅ Back to Dashboard", key="back_to_staff_area"):
            navigate_to('staff_area', role=st.session_state.get('role'))
            
    with col_title:
        st.title(title)
    
    st.markdown("---")

def render_abch_quick_log_form(student):
    """Renders the detailed ABCH-style Quick Log form."""
    
    st.markdown(f"## Logging Incident for **{student['name']}** (Year {student['year']})")
    
    incident_id = str(uuid.uuid4())
    preliminary_data = {
        'id': incident_id,
        'student_id': student['id'],
        'role': st.session_state.get('role'),
    }

    with st.form(key=f"abch_quick_log_form_{incident_id}", clear_on_submit=False):
        
        # --- 1. TIME & LOCATION ---
        st.markdown('<div class="incident-section"><h3><i class="fas fa-clock"></i> Time & Location</h3>', unsafe_allow_html=True)
        col_date, col_time, col_staff = st.columns(3)
        
        with col_date:
            log_date = st.date_input("Incident Date", datetime.now().date())
        with col_time:
            log_time = st.time_input("Incident Time", datetime.now().time().replace(second=0, microsecond=0))
        with col_staff:
            logged_by = st.selectbox("Staff Logging Incident", options=get_active_staff(), index=0)

        # --- ANTECEDENT & BEHAVIOR ---
        st.markdown('</div><div class="incident-section"><h3><i class="fas fa-exclamation-triangle"></i> Antecedent & Behavior</h3>', unsafe_allow_html=True)
        
        col_antecedent, col_behavior = st.columns(2)
        
        with col_antecedent:
            st.markdown("#### **Antecedent/Context**")
            antecedents = []
            
            # Grouped Checkboxes for Context
            for header, options in CONTEXTS.items():
                with st.expander(f"**{header}**"):
                    for i, opt in enumerate(options):
                        # Use session state for persistent tracking of checkboxes
                        key = f"a_{opt.replace(' ', '_')}"
                        if st.checkbox(opt, key=key):
                            antecedents.append(opt)
            
            st.session_state.antecedents = antecedents # Save to state for submission
        
        with col_behavior:
            st.markdown("#### **Specific Behavior**")
            behaviors = st.multiselect(
                "Select one or more specific behaviors demonstrated:",
                options=BEHAVIORS_FBA,
                default=[]
            )
            
            # Critical Incident Flag (Focus of the next section)
            is_critical = st.checkbox("🚩 **CRITICAL INCIDENT** (Requires Admin/Mandatory Reporting)", key='is_critical_incident')
            
        # --- BEHAVIOR DETAIL & CONSEQUENCE/RESPONSE ---
        st.markdown('</div><div class="incident-section"><h3><i class="fas fa-feather-alt"></i> Detail & Response</h3>', unsafe_allow_html=True)

        col_detail, col_response = st.columns(2)
        
        with col_detail:
            st.markdown("#### **Description / Observation**")
            behavior_detail = st.text_area(
                "Describe the incident (what happened, duration, intensity, staff present):",
                placeholder="Student ran out of class (Elopement) after a work demand was placed (Antecedent). Staff member Emily Jones followed and recovered the student near the oval after 5 minutes.",
                height=250
            )

        with col_response:
            st.markdown("#### **Consequence / Staff Response**")
            
            # Window of Tolerance (WOT) - Refined Assessment
            st.markdown("**1. Student's State (Window of Tolerance)**")
            refined_wot = st.radio(
                "Which WOT state best describes the student *during* the incident?",
                options=list(WINDOW_OF_TOLERANCE_OPTS.keys()),
                index=0,
                key='wot_state'
            )
            st.info(f"WOT State Description: {', '.join(WINDOW_OF_TOLERANCE_OPTS[refined_wot])}")

            # Planned Response (Check all that apply)
            st.markdown("**2. Staff Intervention Used**")
            how_to_respond_plan = []
            
            for header, options in HOW_TO_RESPOND_PLAN.items():
                with st.expander(f"**{header}**"):
                    for i, opt in enumerate(options):
                        key = f"r_{opt.replace(' ', '_')}"
                        if st.checkbox(opt, key=key):
                            how_to_respond_plan.append(opt)

        st.session_state.how_to_respond_plan = how_to_respond_plan # Save to state for submission
        
        # --- CRITICAL INCIDENT OUTCOMES (Conditional) ---
        if is_critical:
            st.markdown('</div><div class="incident-section incident-critical"><h3><i class="fas fa-exclamation-circle"></i> CRITICAL INCIDENT OUTCOMES</h3>', unsafe_allow_html=True)
            st.warning("Please tick **ALL** relevant outcomes. This data is critical for mandatory reporting.")
            
            col_a, col_b, col_c = st.columns(3)
            
            cols = [col_a, col_b, col_c, col_a] # Cycle through columns
            col_index = 0
            
            for header, options in CRITICAL_INCIDENT_OUTCOMES.items():
                with cols[col_index]:
                    st.markdown(f"#### **{header}**")
                    for key, label in options:
                        st.checkbox(label, key=key)
                    
                    st.markdown("---")
                col_index = (col_index + 1) % 3

        st.markdown("</div>") # Close the last incident-section div

        # --- SUBMIT BUTTON ---
        if st.form_submit_button("✅ Submit Quick Log", type="primary", use_container_width=True):
            
            if not behaviors:
                st.error("Please select at least one **Specific Behavior** before submitting.")
                st.stop()
            
            log_datetime = datetime.combine(log_date, log_time)

            final_log_entry = preliminary_data.copy()
            final_log_entry.update({
                'date_time': log_datetime,
                'logged_by_staff': logged_by,
                'behavior': ', '.join(behaviors),
                'antecedent': ' / '.join(st.session_state.antecedents) if st.session_state.antecedents else 'No Antecedent Provided.',
                'notes': behavior_detail,
                'consequence': ' / '.join(st.session_state.how_to_respond_plan) if st.session_state.how_to_respond_plan else 'No Response Provided.',
                'is_critical': is_critical,
                'window_of_tolerance': refined_wot,
            })
            
            # If critical, add outcomes to the log entry
            if is_critical:
                critical_outcomes = {k: st.session_state.get(k, False) for group in CRITICAL_INCIDENT_OUTCOMES.values() for k, _ in group}
                final_log_entry.update(critical_outcomes)
                
            # Log the incident
            add_incident(final_log_entry)
            
            # Clear temporary session state data after final save
            keys_to_delete = [k for k in st.session_state if k.startswith(('a_', 'r_', 'o_')) or k in ['wot_state', 'is_critical_incident', 'antecedents', 'how_to_respond_plan']]
            for key in keys_to_delete:
                del st.session_state[key]
                
            st.success(f"Log for {student['name']} submitted successfully! Navigate to their analysis page to view.")
            
            # Automatically navigate to the student detail page after successful log
            navigate_to('student_detail', role=st.session_state.get('role'), student_id=student['id'])


def render_quick_log(role, student):
    """Renders the main Quick Log page for a selected student."""
    staff_header(f"Quick Incident Log for {student['name']}")
    st.markdown(f"**Logged by Role:** `{role}`")
    st.markdown("---")
    render_abch_quick_log_form(student)


def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.subheader("Select your role to proceed to the staff area.")

    col_jp, col_py, col_sy, col_adm = st.columns(4)
    
    with col_jp:
        if st.button("Junior Primary (JP)", key="role_jp", type="primary", use_container_width=True):
            navigate_to('staff_area', role='JP')
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


def render_staff_area(role):
    """Renders the staff dashboard based on selected role."""
    st.title(f"{role} Staff Dashboard")
    st.markdown(f"### Quick Actions for {role} Team")

    col_title, col_search = st.columns([3, 2])
    
    with col_title:
        st.subheader("Student Quick Selection")
    
    # Simple search/filter for mock data
    search_term = st.text_input("Search Student by Name or Year", key="student_search_input", placeholder="e.g., Alex or Year 8")
    
    filtered_students = MOCK_STUDENTS
    if search_term:
        term = search_term.lower()
        filtered_students = [
            s for s in MOCK_STUDENTS 
            if term in s['name'].lower() or term.replace('year ', '').strip() == str(s['year'])
        ]

    st.markdown("---")

    # Display list of students
    if not filtered_students:
        st.info("No students match your search criteria.")
    else:
        st.markdown(f"**Showing {len(filtered_students)} Student(s):**")
        
        # Display students in a grid
        cols = st.columns(4)
        for i, student in enumerate(filtered_students):
            col = cols[i % 4]
            with col:
                with st.container(border=True):
                    st.markdown(f"**{student['name']}**")
                    st.markdown(f"Year: `{student['year']}` | Teacher: `{student['teacher']}`")
                    
                    # Quick Log button
                    if st.button("⚡ Quick Log", key=f"log_{student['id']}", use_container_width=True, type="primary"):
                        navigate_to('quick_log', role=role, student_id=student['id'])
                    
                    # Analysis button (Admin can see analysis, others can't yet in this simplified view)
                    if role == 'ADM':
                        if st.button("📊 View Analysis", key=f"analysis_{student['id']}", use_container_width=True):
                            navigate_to('student_detail', role=role, student_id=student['id'])


def render_student_analysis(student, role):
    """Renders a simple analysis view for the selected student."""
    staff_header(f"Data Analysis: {student['name']} (Year {student['year']})")
    
    incidents = get_incidents_by_student(student['id'])

    if incidents.empty:
        st.info(f"No incidents recorded yet for {student['name']}.")
        if st.button("Log First Incident", key="log_from_analysis", type="primary"):
            navigate_to('quick_log', role=role, student_id=student['id'])
        return
    
    st.markdown(f"### Incident Summary ({len(incidents)} Total Logs)")
    
    col_kpi_1, col_kpi_2, col_kpi_3 = st.columns(3)
    
    with col_kpi_1:
        critical_count = incidents['is_critical'].sum() if 'is_critical' in incidents.columns else 0
        st.metric("Critical Incidents", critical_count)
    with col_kpi_2:
        top_behavior = incidents['behavior'].str.split(', ').explode().mode()[0] if not incidents.empty else 'N/A'
        st.metric("Most Frequent Behavior", top_behavior)
    with col_kpi_3:
        first_log = incidents['date_time'].min().strftime('%d %b %Y')
        st.metric("First Log Date", first_log)

    st.markdown("---")
    
    # Behavior Frequency Chart (using plotly for better visualization)
    st.subheader("Behavior Frequency")
    behavior_counts = incidents['behavior'].str.split(', ', expand=True).stack().value_counts().reset_index()
    behavior_counts.columns = ['Behavior', 'Count']
    fig = px.bar(behavior_counts, x='Behavior', y='Count', 
                 title='Count of Observed Behaviors',
                 color_discrete_sequence=['#3B82F6'])
    fig.update_layout(xaxis={'categoryorder':'total descending'}, plot_bgcolor='#1E293B', paper_bgcolor='#1E293B', font_color='#E2E8F0')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Detailed Incident History (Last 10 Logs)")
    st.dataframe(
        incidents.head(10).drop(columns=['student_id', 'id'], errors='ignore').rename(columns={'date_time': 'Date/Time', 'behavior': 'Behavior', 'antecedent': 'Antecedent', 'consequence': 'Response', 'notes': 'Details', 'role': 'Role'}),
        use_container_width=True,
        hide_index=True
    )

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
            # Should not happen, but safe fallback
            st.error("Role missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == "__main__":
    main()
