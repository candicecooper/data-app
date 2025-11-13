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
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    div[data-testid="stTextArea"] textarea {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        transition: background-color 0.2s, transform 0.1s;
    }
    
    /* Primary Button Customization */
    .stButton > button[kind="primary"] {
        background-color: #2563EB; /* Blue-700 */
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #3B82F6; /* Blue-500 */
        transform: translateY(-1px);
    }
    
    /* Secondary Button Customization */
    .stButton > button[kind="secondary"] {
        background-color: #334155; /* Slate-700 */
        color: #94A3B8; /* Slate-400 */
        border: 1px solid #475569;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #475569; /* Slate-600 */
        color: #F1F5F9;
        transform: translateY(-1px);
    }

    /* Metric Boxes (Card styling) */
    [data-testid="stMetricValue"] {
        font-size: 2.0rem; /* Large value */
        color: #3B82F6;
    }

    .student-card {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 10px;
        cursor: pointer;
        transition: border-color 0.2s, background-color 0.2s;
    }
    .student-card:hover {
        border-color: #2563EB;
        background-color: #15202E;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# --- Initial Data & Mocks (Expanded for Detailed Log) ---

STUDENTS = [
    {'id': 'S001', 'name': 'Alex Johnson', 'year': 9, 'gender': 'M', 'grade_level': 'MY'},
    {'id': 'S002', 'name': 'Maya Patel', 'year': 11, 'gender': 'F', 'grade_level': 'SY'},
    {'id': 'S003', 'name': 'Ethan Chan', 'year': 7, 'gender': 'M', 'grade_level': 'PY'},
    {'id': 'S004', 'name': 'Chloe Davis', 'year': 12, 'gender': 'F', 'grade_level': 'SY'},
    {'id': 'S005', 'name': 'Liam Smith', 'year': 8, 'gender': 'M', 'grade_level': 'MY'},
]

# NEW MOCK STAFF data for detailed reporter selection
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (PY)', 'role': 'PY', 'active': True},
    {'id': 's2', 'name': 'Daniel Lee (MY)', 'role': 'MY', 'active': True},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True},
    {'id': 's_trt', 'name': 'Temporary Relief Teacher (TRT)', 'role': 'TRT', 'active': True},
    {'id': 's_sso', 'name': 'School Support Officer (SSO)', 'role': 'SSO', 'active': True},
]

# NEW FBA and Data Constants
BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 
    'Self-Injurious Behaviour', 'Out of Area (Unauthorised)', 'Screaming/Crying'
]
ANTECEDENTS_FBA = [
    'Task Demand/Instruction', 'Transition', 'Waiting (Alone)', 'Peer Attention', 
    'Teacher Attention (Denied)', 'Sensory Overload', 'Unstructured Time'
]
# Updated from old INCIDENT_TYPES/ABC_CATEGORIES
CONSEQUENCES_FBA = [
    'Verbal Redirection', 'Physical Redirection', 'Time-out (In-Class)', 'Sent to Office',
    'Restorative Conversation', 'Task Removed/Avoided', 'Access to Preferred Activity'
]
# Detailed location categories
LOCATION_CATEGORIES = [
    'Classroom', 'Yard/Playground', 'Library', 'Canteen', 'Hallway/Corridor', 'Office', 'Specialist Room (Art/Science)'
]
# Detailed WOT levels
WOT_LEVELS = [
    'Green - Calm/Present', 'Yellow - Hyper-arousal (Agitated)', 'Red - Fight/Flight/Freeze (Crisis)', 'Blue - Hypo-arousal (Withdrawn)'
]

# Critical Incident Outcomes (Used in Step 2)
CRITICAL_INCIDENT_OUTCOMES = {
    'o_a_send_home': 'Student sent home (Exclusion)',
    'o_b_left_area': 'Student left school grounds/unsupervised area (Elopement)',
    'o_c_assault': 'Assault (Physical or Sexual)',
    'o_d_property_damage': 'Significant property damage',
    'o_e_staff_injury': 'Staff member sustained injury',
    'o_f_sapol_callout': 'SAPOL/Police call-out',
    'o_g_restraint': 'Physical restraint used',
    'o_r_call_out_amb': 'Ambulance called',
    'o_j_first_aid_amb': 'First aid administered (Serious)',
    'o_k_weapon_use': 'Weapon or dangerous object used',
    'o_l_substance_abuse': 'Drug/Alcohol incident'
}

# Helper to get staff name from ID
def get_staff_name(staff_id):
    return next((s['name'] for s in MOCK_STAFF if s['id'] == staff_id), staff_id)

# Function to generate realistic dummy incidents (updated to include all new fields)
def generate_incidents():
    incidents = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(250):
        student = random.choice(STUDENTS)
        date_time = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(8, 16), minutes=random.randint(0, 59))
        
        # New detailed fields
        behavior = random.choice(BEHAVIORS_FBA)
        antecedent = random.choice(ANTECEDENTS_FBA)
        consequence = random.choice(CONSEQUENCES_FBA)
        wot = random.choice(WOT_LEVELS)
        reporter_id = random.choice([s['id'] for s in MOCK_STAFF])
        
        # Simple/Default values for the new detailed fields
        is_abch_completed = True
        context = "Mock general context."
        how_to_respond = "Mock response plan: De-escalate and redirect."
        
        incidents.append({
            'id': str(uuid.uuid4()),
            'student_id': student['id'],
            'date_time': date_time,
            'type': behavior, # Using the main behavior as the type for now
            'staff_reporter': get_staff_name(reporter_id),
            'location': random.choice(LOCATION_CATEGORIES),
            'antecedent': antecedent,
            'behavior': behavior,
            'consequence': consequence,
            'description': f"Brief log of {behavior.lower()} following {antecedent.lower()}. Staff: {get_staff_name(reporter_id)}.",
            'follow_up_needed': random.choice([True, False, False]),
            # NEW DETAILED LOG FIELDS (MOCKING DEFAULTS)
            'is_abch_completed': is_abch_completed,
            'window_of_tolerance': wot,
            'context': context,
            'how_to_respond': how_to_respond,
            # Critical incident flags (mostly False for mock)
            'outcome_send_home': False,
            'outcome_left_area': False,
            'outcome_assault': False,
            'outcome_property_damage': False,
            'outcome_staff_injury': False,
            'outcome_sapol_callout': False,
            'outcome_restraint': False,
            'outcome_ambulance': False,
            'outcome_weapon_use': False,
            'outcome_substance_abuse': False,
        })
    return pd.DataFrame(incidents)


# --- State and Data Management Functions ---

def initialize_state():
    if 'data' not in st.session_state:
        st.session_state.data = generate_incidents()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    # Add state for the multi-step log form
    if 'log_step' not in st.session_state:
        st.session_state.log_step = 1
    if 'prelim_log_data' not in st.session_state:
        st.session_state.prelim_log_data = {}

def navigate_to(page, role=None, student=None):
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student:
        st.session_state.student = student
    # Reset log step when navigating away from log
    if page != 'quick_log':
        st.session_state.log_step = 1
        st.session_state.prelim_log_data = {}
    st.rerun()

@st.cache_data
def get_student_by_id(student_id):
    return next((s for s in STUDENTS if s['id'] == student_id), None)

def get_incidents_by_student(student_id):
    return st.session_state.data[st.session_state.data['student_id'] == student_id]

def get_all_incidents():
    return st.session_state.data

# EXPANDED: Now handles all the new detailed fields from the multi-step form
def log_incident(student_id, data):
    new_incident = {
        'id': str(uuid.uuid4()),
        'student_id': student_id,
        'date_time': datetime.combine(data['date'], data['time']),
        'type': data['behavior'], # Use the specific behavior as the primary type
        'staff_reporter': data['reporter'],
        'location': data['location'],
        
        # ABCH Core
        'antecedent': data['antecedent'],
        'behavior': data['behavior'],
        'consequence': data['consequence'],
        'context': data['context'],
        'description': data['description'],
        'follow_up_needed': data['follow_up'],
        
        # Detailed FBA/WOT/Critical Fields
        'is_abch_completed': data.get('is_abch_completed', True),
        'window_of_tolerance': data.get('window_of_tolerance', 'Green - Calm/Present'),
        'how_to_respond': data.get('how_to_respond', 'Not provided'),

        # Critical Incident Outcomes (Mapping from form keys)
        'outcome_send_home': data.get('o_a_send_home', False),
        'outcome_left_area': data.get('o_b_left_area', False),
        'outcome_assault': data.get('o_c_assault', False),
        'outcome_property_damage': data.get('o_d_property_damage', False),
        'outcome_staff_injury': data.get('o_e_staff_injury', False),
        'outcome_sapol_callout': data.get('o_f_sapol_callout', False),
        'outcome_restraint': data.get('o_g_restraint', False),
        'outcome_ambulance': data.get('o_r_call_out_amb', False) or data.get('o_j_first_aid_amb', False),
        'outcome_weapon_use': data.get('o_k_weapon_use', False),
        'outcome_substance_abuse': data.get('o_l_substance_abuse', False),
    }
    
    # Append the new incident to the DataFrame
    new_df = pd.DataFrame([new_incident])
    st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)


# --- Component Functions ---

def staff_header(title):
    """Renders a consistent header with logo/title and back button."""
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(f"🛠️ {title}")
    with col2:
        if st.session_state.page != 'landing' and st.button("🚪 Logout/Change Role", key="logout_btn", use_container_width=True):
            navigate_to('landing')

# NEW: Replaces the old render_incident_log_form with a detailed multi-step process
def render_detailed_incident_log_form(student):
    """
    Renders the detailed two-step ABCH incident logging form 
    with critical incident flagging.
    """
    
    st.subheader(f"Detailed Incident Log: {student['name']} (Year {student['year']})")
    st.markdown(f"**Step {st.session_state.log_step} of 2**")
    
    # --- STEP 1: INITIAL LOG (ABCH) ---
    if st.session_state.log_step == 1:
        with st.form(key='incident_log_step1', clear_on_submit=False):
            st.markdown("### Step 1: Initial Log & ABCH")
            
            col_date, col_time = st.columns(2)
            with col_date:
                log_date = st.date_input("Date", datetime.now().date(), key='s1_date')
            with col_time:
                log_time = st.time_input("Time", datetime.now().time().replace(second=0, microsecond=0), key='s1_time')

            col_reporter, col_loc = st.columns(2)
            with col_reporter:
                # Use active staff list for selection
                reporter_options = [s['name'] for s in MOCK_STAFF if s['active']]
                staff_reporter = st.selectbox("Staff Reporter", reporter_options, key='s1_reporter')
                
            with col_loc:
                location = st.selectbox("Location", LOCATION_CATEGORIES, key='s1_location')

            st.markdown("---")
            st.markdown("**A**ntecedent, **B**ehavior, **C**onsequence")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                antecedent = st.selectbox("A - Antecedent (What triggered the behavior?)", ANTECEDENTS_FBA, key='s1_antecedent')
            with col_b:
                behavior = st.selectbox("B - Behavior (The primary behavior observed)", BEHAVIORS_FBA, key='s1_behavior')
            with col_c:
                consequence = st.selectbox("C - Consequence (What happened immediately after?)", CONSEQUENCES_FBA, key='s1_consequence')

            
            description = st.text_area("Detailed Description (Mandatory)", 
                                        placeholder="Describe the context, the behavior's intensity, and the staff's initial response.",
                                        key='s1_description')
            
            # The 'H' for Hypothesis is moved to Step 2 as 'Context' and 'How to Respond'

            submitted_step1 = st.form_submit_button("Continue to Step 2: Analysis & Review", type="primary", use_container_width=True)

            if submitted_step1:
                if not description:
                    st.error("Please provide a detailed description to proceed.")
                else:
                    # Store preliminary data in session state
                    st.session_state.prelim_log_data = {
                        'date': log_date,
                        'time': log_time,
                        'reporter': staff_reporter,
                        'location': location,
                        'antecedent': antecedent,
                        'behavior': behavior,
                        'consequence': consequence,
                        'description': description,
                        'follow_up': True, # Assume follow up is needed until checked in step 2
                        'staff_id': next(s['id'] for s in MOCK_STAFF if s['name'] == staff_reporter)
                    }
                    st.session_state.log_step = 2
                    st.rerun()
    
    # --- STEP 2: ANALYSIS & CRITICAL REVIEW ---
    elif st.session_state.log_step == 2:
        preliminary_data = st.session_state.prelim_log_data
        st.markdown("### Step 2: Functional Analysis, WOT & Critical Review")
        
        # Display summary of Step 1 data
        st.info(f"**Incident Summary:** **{preliminary_data['behavior']}** occurred following **{preliminary_data['antecedent']}** at **{preliminary_data['location']}**.")
        
        with st.form(key='incident_log_step2', clear_on_submit=False):
            
            # 1. Window of Tolerance (WOT) Refinement
            st.markdown("---")
            st.markdown("#### **Window of Tolerance (WOT) Assessment**")
            refined_wot = st.selectbox(
                "Student's WOT state during the peak of the behavior:",
                WOT_LEVELS,
                key='s2_wot'
            )
            
            # 2. Hypothesis (Context and Intervention Plan)
            st.markdown("---")
            st.markdown("#### **H - Hypothesis / Context (FBA)**")
            
            final_context = st.text_area(
                "Context (Hypothesized Function of Behavior)",
                placeholder="E.g., Behavior occurs to EITHER Escape a task (Avoidance) OR Gain Access to peer/staff attention (Gain).",
                key='s2_context'
            )

            how_to_respond_plan = st.text_area(
                "How to Respond (Initial De-escalation Plan)",
                placeholder="What de-escalation/support strategies were effective or could be used next time?",
                key='s2_response'
            )
            
            # 3. Critical Incident Section
            st.markdown("---")
            st.markdown("#### **Critical Incident Outcomes (Check all that apply)**")
            
            is_critical = False
            col_crit1, col_crit2 = st.columns(2)
            
            outcome_data = {}
            critical_keys = list(CRITICAL_INCIDENT_OUTCOMES.keys())
            
            for i, (key, label) in enumerate(CRITICAL_INCIDENT_OUTCOMES.items()):
                # Assign to columns based on index
                col = col_crit1 if i < len(critical_keys) / 2 else col_crit2
                with col:
                    # Use unique session state keys for reliable retrieval
                    checked = st.checkbox(label, key=key) 
                    outcome_data[key] = checked
                    if checked:
                        is_critical = True

            st.markdown("---")
            
            st.markdown("#### **Final Follow-up Required?**")
            follow_up = st.checkbox("Requires follow-up by Administration or Head of House", value=True, key='s2_follow_up')
            
            submitted_step2 = st.form_submit_button("Finalize and Submit Incident", type="primary", use_container_width=True)

            if submitted_step2:
                # Merge preliminary data with final analysis and outcomes
                final_log_entry = preliminary_data.copy()
                final_log_entry.update({
                    'is_abch_completed': True,
                    'window_of_tolerance': refined_wot,
                    'context': final_context,
                    'how_to_respond': how_to_respond_plan,
                    'follow_up': follow_up,
                    **outcome_data # Spread the collected outcome data
                })
                
                # Log the final incident
                log_incident(student['id'], final_log_entry)
                
                # Display success message and critical warning if needed
                if is_critical:
                    st.error("⚠️ CRITICAL INCIDENT LOGGED! Administration has been alerted.")
                st.success(f"Detailed incident logged successfully for {student['name']}!")
                
                # Clean up and navigate back
                navigate_to('staff_area', role=st.session_state.role)
                

def render_student_analysis(student, role):
    """Renders the detailed data analysis view for a selected student."""
    
    # 1. Header and Navigation
    staff_header(f"Data Analysis: {student['name']}")

    # 2. Key Metrics
    incidents = get_incidents_by_student(student['id'])
    num_incidents = len(incidents)
    
    st.markdown(f"**Student ID:** `{student['id']}` | **Year:** `{student['year']}` | **Grade Level:** `{student['grade_level']}`")
    
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(label="Total Incidents Logged", value=num_incidents)
    
    if num_incidents > 0:
        # Calculate recent incidents (last 30 days)
        last_30_days = datetime.now() - timedelta(days=30)
        recent_incidents = incidents[incidents['date_time'] >= last_30_days]
        with col_b:
            st.metric(label="Incidents (Last 30 Days)", value=len(recent_incidents), delta=f"{num_incidents - len(recent_incidents)} previous")

        # Most frequent type
        most_frequent_type = incidents['type'].mode().iloc[0]
        with col_c:
            st.metric(label="Most Frequent Incident", value=most_frequent_type)

        st.markdown("---")
        
        # New Metric: Critical Incidents
        critical_outcomes_cols = [col for col in incidents.columns if col.startswith('outcome_')]
        critical_incidents = incidents[incidents[critical_outcomes_cols].any(axis=1)]
        
        st.metric(label="Critical Incidents Logged (Requires Admin Follow-up)", value=len(critical_incidents), delta=f"{len(incidents) - len(critical_incidents)} Standard Incidents")
        
        st.markdown("---")

        # 3. Data Visualization (updated to include Location and Reporter charts)
        st.subheader("Visual Summary")
        
        # Row 1: Time of Day and ABC Breakdown
        chart1, chart2 = st.columns(2)
        
        # Chart 1: Incidents by Time of Day
        with chart1:
            st.markdown("#### Incidents by Time of Day")
            incidents['hour'] = incidents['date_time'].dt.hour
            hour_counts = incidents['hour'].value_counts().sort_index().reindex(range(8, 17), fill_value=0).reset_index()
            hour_counts.columns = ['Hour', 'Count']
            
            fig_time = px.bar(
                hour_counts, 
                x='Hour', 
                y='Count', 
                title='Incident Frequency by Hour of Day (8am - 4pm)',
                color_discrete_sequence=['#3B82F6']
            )
            fig_time.update_layout(xaxis_tickmode='linear', xaxis_dtick=1, xaxis_title='Hour', yaxis_title='Count', template="plotly_dark")
            st.plotly_chart(fig_time, use_container_width=True)

        # Chart 2: ABC Category Breakdown
        with chart2:
            st.markdown("#### ABCH Breakdown (Behavior and WOT)")
            
            # Combine Behavior and WOT for a deeper visualization
            behavior_wot_df = incidents.groupby(['behavior', 'window_of_tolerance']).size().reset_index(name='Count')
            
            fig_abc = px.sunburst(
                behavior_wot_df,
                path=['behavior', 'window_of_tolerance'],
                values='Count',
                color='window_of_tolerance',
                color_discrete_map={
                    'Green - Calm/Present':'#10B981', 
                    'Yellow - Hyper-arousal (Agitated)':'#F59E0B', 
                    'Red - Fight/Flight/Freeze (Crisis)':'#EF4444',
                    'Blue - Hypo-arousal (Withdrawn)':'#3B82F6'
                },
                title='Behavior vs. Window of Tolerance State'
            )
            fig_abc.update_layout(margin=dict(t=30, l=0, r=0, b=0), template="plotly_dark")
            st.plotly_chart(fig_abc, use_container_width=True)
            
        st.markdown("---")
        
        # Row 2: Location and Staff Reporter Breakdown (NEW CHARTS)
        chart3, chart4 = st.columns(2)

        # Chart 3 (NEW): Incidents by Location
        with chart3:
            st.markdown("#### Incidents by Location Hotspot")
            fig_location = px.pie(
                incidents, 
                names='location', 
                title='Distribution by Location',
                color_discrete_sequence=px.colors.sequential.Electric
            )
            fig_location.update_layout(template="plotly_dark", showlegend=True, margin=dict(t=30, l=0, r=0, b=0))
            fig_location.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_location, use_container_width=True)
            
        # Chart 4 (NEW): Incidents by Staff Reporter
        with chart4:
            st.markdown("#### Incidents by Reporting Staff")
            fig_reporter = px.bar(
                incidents['staff_reporter'].value_counts().reset_index(),
                x='index',
                y='staff_reporter',
                title='Incidents Reported by Staff Member',
                labels={'index': 'Staff Reporter', 'staff_reporter': 'Incident Count'},
                color='index',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_reporter.update_layout(template="plotly_dark", xaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_reporter, use_container_width=True)


        st.markdown("---")

        # 4. Detailed Incident Table 
        st.subheader("Detailed Incident Log")
        
        # Select columns to display, including the new detailed fields
        display_cols = [
            'date_time', 'behavior', 'location', 'antecedent', 'consequence', 
            'window_of_tolerance', 'how_to_respond', 'staff_reporter', 'follow_up_needed', 
            'context', 'description'
        ]
        
        display_df = incidents[display_cols].copy()
        display_df.rename(columns={
            'date_time': 'Date/Time', 'behavior': 'Behavior', 'location': 'Location', 
            'staff_reporter': 'Reporter', 'follow_up_needed': 'Follow-Up?',
            'window_of_tolerance': 'WOT State', 'how_to_respond': 'Response Plan', 
            'context': 'FBA Context', 'description': 'Description'
        }, inplace=True)
        
        st.dataframe(
            display_df, 
            use_container_width=True,
            # Enable column sorting and searching
            hide_index=True,
            column_config={
                "Date/Time": st.column_config.DatetimeColumn(
                    "Date/Time",
                    format="YYYY-MM-DD HH:mm:ss",
                    step=60,
                ),
                "Description": st.column_config.TextColumn("Description", help="Full details of the incident", width="large"),
                "FBA Context": st.column_config.TextColumn("FBA Context", help="Hypothesized function/setting event", width="medium"),
                "WOT State": st.column_config.TextColumn("WOT State", help="Student's emotional state", width="small"),
                "Follow-Up?": st.column_config.CheckboxColumn("Follow-Up?", default=False),
            }
        )

    # 5. Navigation
    st.markdown("---")
    if st.button("⬅ Back to Student List", key="back_from_analysis", type="secondary"):
        navigate_to('staff_area', role=role)
    
    # Optional: Direct log button for this student 
    if role in ['ADM', 'SY', 'MY', 'PY']:
        if st.button(f"➕ Log New Incident for {student['name']}", key="direct_log_btn", type="primary"):
            navigate_to('quick_log', student=student)


def render_staff_area_home(role):
    """Renders the main dashboard for staff to select a student."""
    
    staff_header(f"Staff Dashboard ({role})")
    
    # Calculate overall metrics
    all_incidents = get_all_incidents()
    
    if all_incidents.empty:
        st.warning("No incidents have been logged yet.")
        student_data = pd.DataFrame(STUDENTS)
    else:
        # Filter students based on role/grade level if needed (optional logic, showing all for now)
        if role != 'ADM':
            filtered_students = [s for s in STUDENTS if s['grade_level'] == role]
        else:
            filtered_students = STUDENTS

        # Convert to DataFrame for easier analysis
        student_data = pd.DataFrame(filtered_students)
        
        # Calculate incident count per student
        incident_counts = all_incidents.groupby('student_id').size().reset_index(name='Incident Count')
        student_data = student_data.merge(incident_counts, left_on='id', right_on='student_id', how='left').fillna(0)
        student_data['Incident Count'] = student_data['Incident Count'].astype(int)
        
        # Sort students by incident count
        student_data = student_data.sort_values(by='Incident Count', ascending=False)
        
        # --- 1. Summary Statistics ---
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Incidents Logged", len(all_incidents))
        with col_m2:
            st.metric("Unique Students Logged", all_incidents['student_id'].nunique())
        with col_m3:
            st.metric("Students in View", len(student_data))

    st.markdown("---")
    st.subheader("Student Quick View")
    
    # Student Search/Filter
    search_query = st.text_input("Search by Name or ID", key="student_search", placeholder="e.g., Alex or S001")
    
    if not student_data.empty:
        if search_query:
            student_data = student_data[
                student_data['name'].str.contains(search_query, case=False) |
                student_data['id'].str.contains(search_query, case=False)
            ]
            
        # --- 2. Refined Student Card Display ---
        # Display students in columns
        students_per_row = 3
        rows = int(np.ceil(len(student_data) / students_per_row))
        
        for i in range(rows):
            cols = st.columns(students_per_row)
            for j in range(students_per_row):
                index = i * students_per_row + j
                if index < len(student_data):
                    student_row = student_data.iloc[index]
                    student_obj = get_student_by_id(student_row['id'])
                    
                    with cols[j]:
                        # Create an interactive card using st.markdown and an embedded button
                        with st.container():
                            # Use a unique key for the button within the card
                            key = f"select_student_{student_row['id']}"
                            
                            # Custom styling for the card content (using markdown)
                            st.markdown(
                                f"""
                                <div class="student-card">
                                    <h3 style='margin-bottom: 0.2rem;'>{student_row['name']}</h3>
                                    <p style='margin-top: 0; color: #94A3B8;'>ID: {student_row['id']} | Year: {student_row['year']}</p>
                                    <p style='font-size: 1.1em; font-weight: bold; color: #3B82F6;'>
                                        Incidents: {student_row['Incident Count']}
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Streamlit doesn't allow a button *inside* a custom markdown container 
                            # to trigger an action easily, so we use the button right below it 
                            # for functional clarity.
                            if st.button("View Analysis / Log", key=key, use_container_width=True):
                                navigate_to('student_detail', student=student_obj)
    else:
        st.info("No students match your current filter or role selection.")
    

# --- Page Rendering Functions (The "Router" Destination) ---

def render_landing_page():
    """The initial landing page for role selection and quick access."""
    st.title("Welcome to the Student Support Data Tool")
    st.subheader("Select your Staff Role to continue:")
    
    col_py, col_my, col_sy, col_adm = st.columns(4)
    
    # Primary Years (PY)
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
            
    # Middle Years (MY)
    with col_my:
        if st.button("Middle Years (MY)", key="role_my", type="primary", use_container_width=True):
            navigate_to('staff_area', role='MY')
            
    # Senior Years (SY)
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
            
    # Admin (ADM)
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


def render_quick_log(role, student):
    """Page to render the log form after selecting a student from the dashboard."""
    staff_header("Incident Quick Log")
    
    # Call the new detailed log form
    render_detailed_incident_log_form(student)
    
    if st.session_state.log_step == 1:
        if st.button("⬅ Cancel and Return to List", key="back_from_log", type="secondary"):
            navigate_to('staff_area', role=role)
    elif st.session_state.log_step == 2:
        if st.button("⬅ Back to Step 1", key="back_to_step1", type="secondary"):
            st.session_state.log_step = 1
            st.rerun()


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
            render_staff_area_home(current_role)
        else:
            st.error("Role missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == "__main__":
    main()
