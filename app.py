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
    div[data-testid="stTextArea"] > div > textarea,
    div[data-testid="stSelectbox"] > div > div > div {
        background-color: #0F172A;
        border: 1px solid #334155;
        color: #F1F5F9;
        border-radius: 8px;
    }

    /* Standard Button */
    .stButton > button {
        background-color: #3B82F6; /* Blue for primary actions */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: background-color 0.2s, transform 0.1s;
    }
    .stButton > button:hover {
        background-color: #2563EB;
        transform: translateY(-1px);
    }
    
    /* Critical Incident Button Style */
    /* Target the Critical Incident button specifically using a unique key or wrapper if needed, 
       but for now we rely on the specific content/primary styling where possible. 
       We will use an explicit `primary` color for the Critical Incident button's background 
       if we decide to override the standard primary button.
    */
    .critical-incident-btn button {
        background-color: #EF4444 !important; /* Red/Alert for critical */
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        transition: background-color 0.3s !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.4) !important;
    }
    .critical-incident-btn button:hover {
        background-color: #DC2626 !important;
    }


    /* Secondary/Navigation Buttons */
    .st-emotion-cache-nahz7x button {
        background-color: #334155; /* Darker secondary */
        color: #94A3B8;
    }
    .st-emotion-cache-nahz7x button:hover {
        background-color: #475569;
        color: #F1F5F9;
    }
    
    /* Dataframe and Table Styling */
    .stDataFrame {
        border-radius: 8px;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Custom Card/Container Style */
    .dashboard-card {
        padding: 20px;
        border-radius: 12px;
        background-color: #1E293B;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    </style>
    """
, unsafe_allow_html=True)


# --- Mock Data and Utilities ---

MOCK_STUDENTS = [
    {'id': 's101', 'name': 'Alex Johnson', 'year': 7, 'role': 'PY', 'plan_tier': 2},
    {'id': 's102', 'name': 'Beth Smith', 'year': 8, 'role': 'PY', 'plan_tier': 1},
    {'id': 's103', 'name': 'Charlie Davis', 'year': 7, 'role': 'JP', 'plan_tier': 3},
    {'id': 's201', 'name': 'Daniel Lee', 'year': 10, 'role': 'SY', 'plan_tier': 2},
]

MOCK_STAFF = [
    {'id': 'staff1', 'name': 'Emily Jones (JP)', 'role': 'JP'},
    {'id': 'staff2', 'name': 'Daniel Lee (PY)', 'role': 'PY'},
    {'id': 'staff3', 'name': 'Sarah Chen (SY)', 'role': 'SY'},
    {'id': 'staff4', 'name': 'Admin User (ADM)', 'role': 'ADM'},
]

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Screaming)', 'Physical Aggression (Staff)']
MOTIVATIONS = ['Gain Attention', 'Escape Demand/Task', 'Access Tangible', 'Sensory Regulation/Automatic']
CONTEXTS = ['Classroom Activity', 'Transition', 'Recess/Lunch', 'Specific Staff Interaction', 'Peer Conflict', 'Non-Structured Time']
WOT_LABELS = ['Baseline', 'Alert', 'High Alert', 'Shutdown', 'Crisis']
role_map = {'JP': 'Junior Primary', 'PY': 'Primary', 'SY': 'Secondary', 'ADM': 'Admin/Leadership'}
SETTING_FBA = ['Classroom (Main)', 'Playground (Recess/Lunch)', 'Specialist Lesson (Art/Gym)', 'Hallway/Transition', 'Office/Sick Bay', 'Library', 'Outside School Grounds']
CONSEQUENCES_FBA = ['Redirection/Prompt', 'Ignored/Withdrawn', 'Preferred Task/Item Given', 'Time Out/Seclusion', 'Restraint/Physical Support', 'Verbal Reprimand', 'Sent to Leadership/Manager', 'Parent Contact/Sent Home']


# Mock Log Generation (for demo data)
def generate_mock_log(student_id, date, hour, minute):
    timestamp = datetime.combine(date, time(hour, minute))
    
    behavior = random.choice(BEHAVIORS_FBA)
    antecedent = random.choice(CONTEXTS)
    consequence = random.choice(CONSEQUENCES_FBA)
    motivation = random.choice(MOTIVATIONS)
    wot_start = random.choice(WOT_LABELS[:-1])
    wot_end = random.choice(WOT_LABELS[WOT_LABELS.index(wot_start):])
    
    is_critical = random.random() < 0.15 or behavior == 'Physical Aggression (Staff)'
    
    return {
        'log_id': str(uuid.uuid4()),
        'student_id': student_id,
        'timestamp': timestamp,
        'date': date,
        'time': time(hour, minute),
        'staff_id': random.choice(MOCK_STAFF)['id'],
        'behavior': behavior,
        'antecedent': antecedent,
        'consequence': consequence,
        'motivation': motivation,
        'duration_min': random.randint(1, 15),
        'wot_start': wot_start,
        'wot_end': wot_end,
        'is_critical': is_critical,
        'notes': f"Quick log entry for {behavior} after {antecedent}. Resolved with {consequence}.",
        'setting': random.choice(SETTING_FBA)
    }

def initialize_state():
    """Initializes session state variables if they don't exist."""
    if 'students' not in st.session_state:
        st.session_state.students = MOCK_STUDENTS
    if 'log_data' not in st.session_state:
        logs = []
        today = datetime.now().date()
        for _ in range(100):
            date = today - timedelta(days=random.randint(0, 30))
            hour = random.randint(9, 15)
            minute = random.randint(0, 59)
            logs.append(generate_mock_log(random.choice(MOCK_STUDENTS)['id'], date, hour, minute))
        st.session_state.log_data = pd.DataFrame(logs)
        st.session_state.log_data['date'] = pd.to_datetime(st.session_state.log_data['date'])
        
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        # Set a default student for easier testing if navigating directly to staff area
        st.session_state.student = MOCK_STUDENTS[0]
    if 'incident_type' not in st.session_state:
        st.session_state.incident_type = 'standard'
        
def navigate_to(page: str, student=None, role=None, incident_type='standard'):
    """Handles page navigation by setting session state variables."""
    st.session_state.page = page
    if student:
        st.session_state.student = student
    if role:
        st.session_state.role = role
    st.session_state.incident_type = incident_type
    st.rerun()
    
def get_student_logs(student_id):
    """Retrieves all logs for a specific student."""
    return st.session_state.log_data[st.session_state.log_data['student_id'] == student_id]

def get_staff_name(staff_id):
    """Mocks retrieval of staff name."""
    return next((s['name'] for s in MOCK_STAFF if s['id'] == staff_id), "Unknown Staff")

# --- Page Rendering Functions ---

def render_landing_page():
    st.title("Welcome to the Behaviour Support Dashboard")
    st.markdown("---")
    
    st.subheader("Select Your Access Role")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Junior Primary (JP)", use_container_width=True):
            navigate_to('staff_area', role='JP')
            
    with col2:
        if st.button("Primary (PY)", use_container_width=True):
            navigate_to('staff_area', role='PY')

    with col3:
        if st.button("Secondary (SY)", use_container_width=True):
            navigate_to('staff_area', role='SY')

    with col4:
        if st.button("Admin/Leadership (ADM)", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")

def render_staff_area(role):
    """Renders the main dashboard for a specific staff role."""
    
    st.title(f"Behaviour Support Dashboard: {role_map.get(role, role)}")
    st.markdown("---")
    
    if st.button('↩ Return to Role Select', key='back_to_landing', use_container_width=False):
        navigate_to('landing')
        
    st.subheader("Action Center")

    col_log_container, col_data_info = st.columns([1, 2])
    
    with col_log_container:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Incident Logging")
        st.markdown("Select a student to log an incident.")
        
        # Filter students relevant to the staff role (or all for ADM)
        all_students = st.session_state.students
        
        if role != 'ADM':
            area_students = [s for s in all_students if s['role'] == role]
        else:
            area_students = all_students
            
        student_options = ['-- Select --'] + sorted([s['name'] for s in area_students])
        
        selected_name = st.selectbox(
            'Select Student:',
            options=student_options,
            key='log_student_select'
        )
        
        selected_student_obj = None
        if selected_name != '-- Select --':
            selected_student_obj = next(s for s in area_students if s['name'] == selected_name)
            
            st.markdown("---")
            
            col_log_btns = st.columns(2)
            
            # Button 1: Standard ABCH Quick Log
            with col_log_btns[0]:
                if st.button('ABCH Quick Log', key='start_quick_log_abch', use_container_width=True):
                    # Pass the 'abch_quick' flag
                    navigate_to('quick_log', student=selected_student_obj, role=role, incident_type='abch_quick')
                    
            # Button 2: Dedicated Critical Incident Log Button (styled using custom CSS)
            with col_log_btns[1]:
                # Wrap the button in a div with the custom class for styling
                st.markdown('<div class="critical-incident-btn">', unsafe_allow_html=True)
                if st.button('Critical Incident', key='start_quick_log_critical', use_container_width=True):
                    # Pass the 'critical' flag
                    navigate_to('quick_log', student=selected_student_obj, role=role, incident_type='critical')
                st.markdown('</div>', unsafe_allow_html=True)

        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_data_info:
        st.subheader("Data Access & Support")
        st.info(
            "Use the dashboard below to analyse trends in your area, or scroll down to select a student "
            "for detailed Functional Behaviour Assessment (FBA) analysis."
        )

    # --- Dashboard Metrics and Analysis ---
    
    st.markdown("## Data Overview")
    
    df_all = st.session_state.log_data
    
    # Filter by role for dashboard view
    if role != 'ADM':
        role_ids = [s['id'] for s in st.session_state.students if s['role'] == role]
        df_filtered = df_all[df_all['student_id'].isin(role_ids)].copy()
    else:
        df_filtered = df_all.copy()
        
    df_display = df_filtered.copy()

    col_metrics = st.columns(4)
    
    # Metric 1: Total Incidents
    col_metrics[0].metric(label="Total Incidents", value=len(df_display))
    
    # Metric 2: Critical Incidents
    critical_count = df_display['is_critical'].sum()
    col_metrics[1].metric(label="Critical Incidents", value=critical_count)
    
    # Metric 3: Students Involved
    unique_students = df_display['student_id'].nunique()
    col_metrics[2].metric(label="Unique Students Logged", value=unique_students)
    
    # Metric 4: Average Duration
    avg_duration = df_display['duration_min'].mean()
    col_metrics[3].metric(label="Average Duration (min)", value=f"{avg_duration:.1f}")

    # --- Charts ---
    
    st.markdown("### Top Behaviours & Functions")

    col_charts = st.columns(2)
    
    if not df_display.empty:
        with col_charts[0]:
            fig_behaviors = px.bar(
                df_display['behavior'].value_counts().head(5).reset_index(),
                x='count', y='behavior', orientation='h', 
                title='Top 5 Behaviors', template='plotly_dark'
            )
            fig_behaviors.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_behaviors, use_container_width=True)
            
        with col_charts[1]:
            fig_motivations = px.pie(
                df_display['motivation'].value_counts().reset_index(),
                names='motivation', values='count', 
                title='Hypothesized Functions', template='plotly_dark'
            )
            st.plotly_chart(fig_motivations, use_container_width=True)
    else:
        st.info("No data available for charting in this area.")

    st.markdown("---")
    
    # Student Detail View Trigger
    st.subheader("View Detailed Student Analysis")
    
    student_map = {s['id']: s['name'] for s in st.session_state.students}
    df_display['student_name'] = df_display['student_id'].map(student_map)
    
    analysis_options = df_display[['student_name', 'student_id']].drop_duplicates().sort_values('student_name')
    
    analysis_name = st.selectbox(
        'Select Student for Detailed Analysis:',
        options=['-- Select --'] + analysis_options['student_name'].tolist(),
        key='analysis_student_select'
    )
    
    if analysis_name != '-- Select --':
        selected_row = next(s for s in st.session_state.students if s['name'] == analysis_name)
        
        if st.button(f'View Analysis for {analysis_name}', key='view_analysis', use_container_width=True):
            navigate_to('student_detail', student=selected_row, role=role)

def render_quick_log(current_role, current_student):
    """Renders the comprehensive ABCH log form."""
    
    incident_type = st.session_state.get('incident_type', 'standard')

    # Display dynamic header based on navigation
    st.header(f"Incident Log for {current_student['name']}")

    # FIX: Displaying the correct banner based on the navigation flag
    if incident_type == 'critical':
        st.error("🚨 CRITICAL INCIDENT REPORT 🚨 (Requires full completion and immediate follow-up)")
    elif incident_type == 'abch_quick':
        st.info("✍️ ABCH Quick Log (Focus on Antecedent, Behavior, Consequence, and Hypothesis)")
    else:
        st.subheader("Standard Log Entry")

    if st.button('↩ Back to Dashboard', key='back_to_dashboard', use_container_width=False):
        navigate_to('staff_area', role=current_role)
        
    st.markdown("---")

    with st.form(key='quick_log_form', clear_on_submit=True):
        
        st.subheader("1. Incident Details")
        
        col_dt, col_t, col_duration = st.columns(3)
        with col_dt:
            incident_date = st.date_input("Date of Incident", datetime.now().date())
        with col_t:
            incident_time = st.time_input("Time of Incident", datetime.now().time().replace(second=0, microsecond=0))
        with col_duration:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=5)

        col_loc, col_staff = st.columns(2)
        with col_loc:
            location = st.selectbox("Location/Setting", options=SETTING_FBA)
        with col_staff:
            default_staff_name = next((s['name'] for s in MOCK_STAFF if s['role'] == current_role), MOCK_STAFF[0]['name'])
            staff_list = [s['name'] for s in MOCK_STAFF]
            staff_involved = st.selectbox("Staff Recording/Witnessing", options=staff_list, index=staff_list.index(default_staff_name))

        st.subheader("2. ABCH Log")
        
        col_abc = st.columns(3)
        with col_abc[0]:
            antecedent = st.selectbox("Antecedent (A)", options=CONTEXTS)
        with col_abc[1]:
            behavior = st.selectbox("Observed Behavior (B)", options=BEHAVIORS_FBA)
        with col_abc[2]:
            consequence = st.selectbox("Consequence (C)", options=CONSEQUENCES_FBA)
            
        hypothesis = st.selectbox("Hypothesis (H): Potential Motivation/Function", options=MOTIVATIONS)

        st.subheader("3. De-escalation & Context")

        wot_start = st.select_slider("Window of Tolerance (WOT) - Start", options=WOT_LABELS, value='Alert')
        wot_end = st.select_slider("Window of Tolerance (WOT) - End", options=WOT_LABELS, value='High Alert')
        
        staff_response = st.text_area("Staff Response/De-escalation Steps Taken", height=150, placeholder="Describe the steps taken to de-escalate or respond to the behaviour.")

        # --- Outcomes Section (Crucial for critical incidents) ---
        st.subheader("4. Outcomes/Mandatory Reporting Flags")
        
        col_o1, col_o2, col_o3 = st.columns(3)
        
        with col_o1:
            st.checkbox("Student sent home/Suspension", key='o_a_send_home')
            st.checkbox("Student left immediate area (Elopement)", key='o_b_left_area')
        with col_o2:
            st.checkbox("Assault/Physical Aggression on Peer", key='o_c_assault')
            st.checkbox("Property Damage (Significant)", key='o_d_property_damage')
        with col_o3:
            st.checkbox("Staff Injury requiring First Aid", key='o_e_staff_injury')
            st.checkbox("SAPOL Callout", key='o_f_sapol_callout')

        submitted = st.form_submit_button("Submit Incident Log", type="primary", use_container_width=True)
        
        if submitted:
            if not behavior or not antecedent:
                st.warning("Please select a Behavior and Antecedent.")
                return

            staff_id = next(s['id'] for s in MOCK_STAFF if s['name'] == staff_involved)
            
            is_critical_flag = (incident_type == 'critical' or 
                                st.session_state.get('o_a_send_home', False) or 
                                st.session_state.get('o_e_staff_injury', False) or 
                                st.session_state.get('o_f_sapol_callout', False))
            
            new_log = {
                'log_id': str(uuid.uuid4()),
                'student_id': current_student['id'],
                'timestamp': datetime.combine(incident_date, incident_time),
                'date': incident_date,
                'time': incident_time,
                'staff_id': staff_id,
                'behavior': behavior,
                'antecedent': antecedent,
                'consequence': consequence,
                'motivation': hypothesis,
                'duration_min': duration,
                'wot_start': wot_start,
                'wot_end': wot_end,
                'is_critical': is_critical_flag,
                'notes': f"Staff Response: {staff_response}. Location: {location}",
                'setting': location
            }

            new_log_df = pd.DataFrame([new_log])
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_log_df], ignore_index=True)
            
            st.success(f"Log recorded successfully for {current_student['name']}!")
            
            navigate_to('staff_area', role=current_role)


def render_student_analysis(student, role):
    st.title(f"Analysis Dashboard: {student['name']}")
    st.subheader(f"Year {student['year']} | Support Tier {student['plan_tier']}")
    st.markdown("---")
    
    if st.button("← Back to Staff Dashboard"):
        navigate_to('staff_area', role=role)

    log_data = get_student_logs(student['id'])
    
    if log_data.empty:
        st.warning("No incident logs available for this student.")
        return

    # --- Metrics ---
    st.header("Key Metrics (Last 30 Days)")
    
    total_logs = len(log_data)
    critical_logs = log_data['is_critical'].sum()
    avg_duration = log_data['duration_min'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logs", total_logs)
    col2.metric("Critical Incidents", critical_logs, delta=f"{critical_logs/total_logs:.1%}" if total_logs > 0 else None, delta_color="inverse")
    col3.metric("Avg. Duration (min)", f"{avg_duration:.1f}")
    
    # --- Data Visualizations ---
    
    st.header("Behaviour Patterns")
    
    fig_behaviors = px.bar(
        log_data['behavior'].value_counts().reset_index(),
        x='behavior', y='count',
        title='Frequency of Observed Behaviours',
        labels={'behavior': 'Behaviour', 'count': 'Count'},
        color='behavior'
    )
    st.plotly_chart(fig_behaviors, use_container_width=True)
    
    fig_motivation = px.pie(
        log_data['motivation'].value_counts().reset_index(),
        names='motivation', values='count',
        title='Hypothesized Motivation/Function of Behaviour',
    )
    st.plotly_chart(fig_motivation, use_container_width=True)

    # --- Raw Data ---
    st.header("Raw Incident Log History")
    log_data_display = log_data.copy()
    log_data_display['Staff'] = log_data_display['staff_id'].apply(get_staff_name)
    log_data_display['Date/Time'] = log_data_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(
        log_data_display[['Date/Time', 'behavior', 'antecedent', 'consequence', 'motivation', 'duration_min', 'wot_start', 'wot_end', 'is_critical', 'Staff']], 
        use_container_width=True,
        hide_index=True
    )

# --- Main Application Loop ---

def main():
    """Controls the main application flow based on session state."""
    
    initialize_state()

    current_role = st.session_state.get('role')
    current_student = st.session_state.get('student')

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
            navigate_to('landing')

if __name__ == '__main__':
    main()
