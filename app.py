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
        background-color: #0F172A; 
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        opacity: 0.85;
    }
    
    /* Primary Button Customization */
    .stButton>button[kind="primary"] {
        background-color: #3B82F6; /* Blue 500 */
        color: white;
    }
    
    /* Radio/Checkbox custom styling for better visibility */
    .stRadio p, .stCheckbox p {
        color: #E2E8F0; 
    }
    
    /* Container/Block Styling */
    div[data-testid="stVerticalBlock"] > div:first-child > div:nth-child(2) > div:nth-child(1) {
        /* Apply custom background to the form block */
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# --- Mock Data and State Management (Unchanged) ---

MOCK_STUDENTS = [
    {'id': 's1001', 'name': 'Alex Johnson', 'year': 9, 'class': '9A', 'gender': 'M', 'support_level': 'High'},
    {'id': 's1002', 'name': 'Bella Smith', 'year': 7, 'class': '7B', 'gender': 'F', 'support_level': 'Medium'},
    {'id': 's1003', 'name': 'Chris Lee', 'year': 11, 'class': '11C', 'gender': 'M', 'support_level': 'Low'},
    {'id': 's1004', 'name': 'Dana White', 'year': 8, 'class': '8A', 'gender': 'F', 'support_level': 'High'},
]

MOCK_STAFF = [
    {'id': 'stf1', 'name': 'Ms. Emily Jones (JP)', 'role': 'JP', 'active': True, 'email': 'ejones@school.edu'},
    {'id': 'stf2', 'name': 'Mr. Daniel Lee (PY)', 'role': 'PY', 'active': True, 'email': 'dlee@school.edu'},
    {'id': 'stf3', 'name': 'Ms. Sarah Chen (SY)', 'role': 'SY', 'active': True, 'email': 'schen@school.edu'},
    {'id': 'stf4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'email': 'admin@school.edu'},
    {'id': 'stf5', 'name': 'TRT Staff', 'role': 'TRT', 'active': True, 'email': 'trt@school.edu'},
]

# --- FBA and Data Constants (UPDATED WOT) ---

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 
    'Self-Injurious Behaviour', 'Outburst (Verbal/Loud)', 'Non-Compliance', 
    'Task Avoidance', 'Disruptive Movement', 'Other'
]

# WOT Options updated: 'Optimal' changed to 'Coping'
WOT_OPTIONS = {
    'CALM': "Calm: Safe, regulated, and responsive.",
    'COPING': "Coping: Regulated but requires support/effort.", # UPDATED
    'HYPER_AROUSAL': "Hyper-Arousal: Overly activated, anxious, reactive.",
    'HYPO_AROUSAL': "Hypo-Arousal: Withdrawn, shut down, low energy."
}

# New field options
SUPPORT_TYPES = ['Independent', '1:1', 'Small Group', 'Large Group']


# --- Helper Functions (Unchanged) ---

def initialize_state():
    """Initializes necessary session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'incidents_db' not in st.session_state:
        st.session_state.incidents_db = pd.DataFrame(columns=[
            'id', 'student_id', 'student_name', 'staff_id', 'staff_name', 
            'date', 'time', 'location', 'behavior_type', 'wot_state', 
            'support_type', 'severity', 'description'
        ])

def navigate_to(page, role=None, student=None):
    """Sets the next page and associated context."""
    if role is not None:
        st.session_state.role = role
    if student is not None:
        st.session_state.student = student
    st.session_state.page = page
    st.rerun()

def get_student_by_id(student_id):
    """Retrieves a student dictionary by ID."""
    return next((s for s in MOCK_STUDENTS if s['id'] == student_id), None)

def get_staff_by_role(role):
    """Filters staff list by selected role."""
    if role == 'ADM': # Admin can log as anyone
        return [s['name'] for s in MOCK_STAFF]
    return [s['name'] for s in MOCK_STAFF if s['role'] == role]

def save_incident(incident_data):
    """Saves the incident to the mock database and simulates a successful write."""
    df = st.session_state.incidents_db.copy()
    
    # Ensure all required keys exist, filling missing ones with default/empty values
    required_keys = ['id', 'student_id', 'student_name', 'staff_id', 'staff_name', 
                     'date', 'time', 'location', 'behavior_type', 'wot_state', 
                     'support_type', 'severity', 'description']
    
    clean_data = {key: incident_data.get(key, '') for key in required_keys}
    
    new_df = pd.DataFrame([clean_data])
    st.session_state.incidents_db = pd.concat([df, new_df], ignore_index=True)
    
    # Simulate database write delay
    # time.sleep(0.5) 
    return True

# --- Application Components (Unchanged or Minor) ---

def render_staff_area(role):
    """Renders the staff dashboard for selecting a student or logging directly."""
    st.title(f"{role} Staff Dashboard")
    st.subheader("Select a Student")

    # Filter students for this example (e.g., all students available)
    student_options = MOCK_STUDENTS
    
    # Student selection layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        student_name = st.selectbox(
            "Student Name", 
            options=[s['name'] for s in student_options],
            index=None,
            placeholder="Search or select a student..."
        )

    selected_student = next((s for s in MOCK_STUDENTS if s['name'] == student_name), None)

    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Spacer for alignment
        if st.button("View Student Profile", type="secondary", disabled=selected_student is None, use_container_width=True):
            if selected_student:
                navigate_to('student_detail', student=selected_student)

    st.markdown("---")
    
    # Quick Log button
    st.subheader("Need to quickly log an incident?")
    
    col3, col4 = st.columns([1, 4])
    with col3:
        student_for_log = st.selectbox(
            "Log for:", 
            options=[s['name'] for s in MOCK_STUDENTS],
            index=None,
            placeholder="Select student for Quick Log..."
        )
    
    selected_student_for_log = next((s for s in MOCK_STUDENTS if s['name'] == student_for_log), None)

    with col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Spacer for alignment
        if st.button("🚀 Start Quick Log", type="primary", disabled=selected_student_for_log is None):
            if selected_student_for_log:
                navigate_to('quick_log', student=selected_student_for_log)
        

def render_landing_page():
    """Renders the initial page for role selection."""
    st.title("Behaviour Support Data Logger")
    st.subheader("Welcome! Please select your role to proceed.")
    
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
    st.info("This application uses an enhanced ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


# --- Quick Incident Log Form (UPDATED) ---

def render_quick_log(role, student):
    """Renders the streamlined quick incident log form for a student."""
    st.title("🚀 Quick Incident Log")
    st.subheader(f"Logging for: {student['name']} (Year {student['year']})")
    st.markdown("---")
    
    staff_options = get_staff_by_role(role)

    with st.form(key=f'quick_log_form_{student["id"]}', clear_on_submit=True):
        
        # --- Incident Context (Top Row) ---
        col_date, col_time = st.columns(2)
        with col_date:
            incident_date = st.date_input("**Date**", datetime.now().date(), key=f'date_{student["id"]}')
        with col_time:
            incident_time = st.time_input("**Time**", datetime.now().time(), key=f'time_{student["id"]}')

        col_location, col_staff = st.columns(2)
        with col_location:
            location = st.text_input("**Location/Context**", placeholder="e.g., Maths Class, Playground (Oval)", key=f'loc_{student["id"]}')
        with col_staff:
            staff_logged = st.selectbox("**Staff Logging Incident**", options=staff_options, index=0 if staff_options else None, key=f'staff_{student["id"]}')

        st.markdown("---")

        # --- Support Context & Severity (New Row) ---
        col_support_type, col_severity = st.columns(2)

        with col_support_type:
            support_type = st.radio(
                "**Type of Support/Group**",
                SUPPORT_TYPES,
                key=f'support_type_{student["id"]}',
                index=None,
                help="Select the context in which the incident occurred."
            )

        with col_severity:
            # Use a slider for severity 1-5 for visual distinctiveness and ease of use
            severity = st.slider(
                "**Severity (1=Minor, 5=Critical)**",
                min_value=1,
                max_value=5,
                value=1,
                step=1,
                key=f'severity_{student["id"]}',
                help="Indicate the level of concern/impact of the incident (3+ flags a critical log).",
                label_visibility="visible"
            )

        st.markdown("---")

        # --- A-B-C-H Sections ---

        # Antecedent / Behavior
        col_antecedent, col_behavior = st.columns(2)
        with col_antecedent:
            st.markdown("#### Antecedent (A)")
            antecedent = st.text_area(
                "Triggering Event/Setting", 
                placeholder="What happened immediately before the behaviour?", 
                key=f'ant_{student["id"]}',
                height=150
            )

        with col_behavior:
            st.markdown("#### Behavior (B)")
            behavior_type = st.multiselect(
                "Select one or more key behaviors:", 
                options=BEHAVIORS_FBA,
                key=f'behaviors_{student["id"]}',
                default=[]
            )
            
        st.markdown("---")
        
        # Consequence / Window of Tolerance (WOT)
        col_consequence, col_wot = st.columns(2)
        with col_consequence:
            st.markdown("#### Consequence (C)")
            consequence = st.text_area(
                "Staff Response/Outcome", 
                placeholder="What happened immediately after the behaviour?", 
                key=f'cons_{student["id"]}',
                height=150
            )
        
        with col_wot:
            st.markdown("#### Window of Tolerance (WOT)")
            wot_state = st.selectbox(
                "Student's Regulatory State:", 
                options=list(WOT_OPTIONS.keys()),
                format_func=lambda x: f"{x} - {WOT_OPTIONS[x].split(':')[1].strip()}",
                key=f'wot_{student["id"]}',
                index=None,
                help="Select the student's emotional/physiological state during the incident."
            )

        st.markdown("---")
        
        # --- Observation/Description (Optional and at the bottom) ---
        st.markdown(
            """
            <div style='background-color: #2F3E50; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                <p style='color: #FACC15; font-weight: bold; font-size: 1.1em;'>
                    📝 Description / Observation (Optional)
                </p>
                <p style='color: #D1D5DB; font-size: 0.9em;'>
                    *This section is generally discouraged for quick logs.*
                    Only use this if critical context is needed that the sections above cannot capture.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        description_text = st.text_area(
            "Detailed Observation:",
            height=100,
            key=f'desc_obs_{student["id"]}',
            label_visibility="collapsed",
            placeholder="Type optional description here..."
        )


        # --- Submission Button ---
        col_submit, col_back = st.columns([1, 4])
        with col_submit:
            submitted = st.form_submit_button("✅ Submit Quick Log", type="primary", use_container_width=True)

    if submitted:
        if not all([location, behavior_type, staff_logged, antecedent, consequence, wot_state, support_type]):
            st.error("Please ensure all fields (except the optional Description) are completed.")
        else:
            staff_id = next((s['id'] for s in MOCK_STAFF if s['name'] == staff_logged), 'unknown')
            
            incident_data = {
                'id': str(uuid.uuid4()),
                'student_id': student['id'],
                'student_name': student['name'],
                'staff_id': staff_id,
                'staff_name': staff_logged,
                'date': incident_date.isoformat(),
                'time': incident_time.isoformat(),
                'location': location,
                'behavior_type': ", ".join(behavior_type), # Store list as string
                'wot_state': wot_state,
                'support_type': support_type,
                'severity': severity, # New field
                'description': description_text,
            }
            
            if save_incident(incident_data):
                st.success(f"Log for {student['name']} submitted successfully!")
                
                # --- Critical Incident Flag Logic ---
                if severity >= 3:
                    st.warning(
                        f"🚨 **High Severity Incident (Level {severity}) Logged!** "
                        "A severity of 3 or higher requires completion of the Critical Incident Form. "
                        "Please click the button below to continue the documentation process.",
                        icon="⚠️"
                    )
                    # Placeholder for the segue button
                    if st.button("➡️ Segue to Critical Incident Form", key="segue_critical", type="secondary"):
                        # In a real app, this would change the page state and pass the incident ID
                        st.info("Loading Critical Incident Form with pre-populated data... (Functionality placeholder)")

                st.balloons()
                # Automatically navigate back to the staff dashboard after a brief moment
                # For demonstration, we keep the success message visible, but in a real app, 
                # you'd use st.session_state.submitted = True and re-run to clear the form.
                # For simplicity here, we'll just show the success message.
                
    if st.button("⬅ Back to Staff Dashboard", key="back_from_quick_log"):
        navigate_to('staff_area', role=role)

# --- Analysis & Other Components (Remaining functions unchanged for brevity) ---
def render_student_analysis(student, role):
    st.title(f"Detailed Analysis for: {student['name']}")
    st.subheader(f"Year {student['year']} | Support Level: {student['support_level']}")

    # Filter incidents for the selected student
    student_incidents = st.session_state.incidents_db[
        st.session_state.incidents_db['student_id'] == student['id']
    ]

    if student_incidents.empty:
        st.info("No incident logs available for this student yet.")
        if st.button("Log First Incident", key="log_first_analysis"):
             navigate_to('quick_log', student=student)
        return

    st.markdown("---")

    col_stats, col_logs = st.columns([1, 2])

    with col_stats:
        st.markdown("### Key Metrics")
        total_logs = len(student_incidents)
        st.metric(label="Total Logs", value=total_logs)

        # Behavior Frequency
        behavior_counts = student_incidents['behavior_type'].str.split(', ').explode().str.strip().value_counts().head(3)
        st.markdown("#### Top Behaviors:")
        for behavior, count in behavior_counts.items():
            st.markdown(f"- **{behavior}**: {count} times")

        # WOT Breakdown
        wot_counts = student_incidents['wot_state'].value_counts(normalize=True).mul(100).round(1)
        st.markdown("#### WOT Distribution:")
        for wot, percent in wot_counts.items():
            st.markdown(f"- **{wot}**: {percent}%")
            
        # Average Severity
        avg_severity = student_incidents['severity'].mean().round(2)
        st.metric(label="Average Severity", value=avg_severity)


    with col_logs:
        st.markdown("### Log History Trend")
        
        # Prepare data for time series plot
        df_plot = student_incidents.copy()
        df_plot['datetime'] = pd.to_datetime(df_plot['date'] + ' ' + df_plot['time'])
        df_plot = df_plot.sort_values('datetime')
        
        # Use a rolling average for smoothing the severity trend
        df_plot['severity_smooth'] = df_plot['severity'].rolling(window=3, min_periods=1, center=True).mean()

        fig = px.line(
            df_plot, 
            x='datetime', 
            y='severity_smooth', 
            title='Severity Trend Over Time (3-Log Rolling Average)',
            labels={'datetime': 'Date & Time', 'severity_smooth': 'Smoothed Severity'},
            template="plotly_dark"
        )
        fig.update_traces(mode='lines+markers', line=dict(color='#FACC15'))
        fig.update_layout(
            xaxis_title=None, 
            yaxis_title="Severity Score",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Full Log Data")
    # Display the raw data table
    st.dataframe(student_incidents[['date', 'time', 'location', 'behavior_type', 'wot_state', 'severity', 'support_type', 'description', 'staff_name']], use_container_width=True)


    if st.button("⬅ Back to Staff Dashboard", key="back_from_analysis"):
        navigate_to('staff_area', role=role)
        
        
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
            # Should not happen if state is managed correctly
            st.warning("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == "__main__":
    main()
