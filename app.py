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
    div[data-testid="stTextArea"] > div > textarea,
    .st-emotion-cache-1gcs6de {
        background-color: #0F172A;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3B82F6; /* Blue for primary action */
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: background-color 0.3s;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }

    /* Warning (Critical Incident) - Yellow Box */
    div[data-testid="stAlert"] > div {
        background-color: #433E0B !important; /* Darker yellow/brown background */
        border-left: 6px solid #FBBF24 !important; /* Bright yellow border */
        color: #F1F5F9 !important;
        border-radius: 12px;
    }
    .st-emotion-cache-121p009 { /* Specific style for warning text */
        color: #F1F5F9 !important; 
    }
    
    /* Dataframe Styling */
    .stDataFrame { border-radius: 12px; }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #60A5FA; /* Light Blue for metrics */
    }
    [data-testid="stMetricLabel"] {
        color: #E2E8F0;
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
    """, unsafe_allow_html=True
)

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Verbal/Noise)', 'Task Avoidance', 'Defiance/Non-Compliance']
CONSEQUENCES_FBA = ['Redirection/Prompt', 'Ignored/Withdrawn', 'Preferred Task/Item Given', 'Time Out/Seclusion', 'Restraint/Physical Support', 'Verbal Reprimand', 'Sent to Leadership/Manager', 'Parent Contact/Sent Home']
SETTING_FBA = ['Classroom (Main)', 'Playground (Recess/Lunch)', 'Specialist Lesson (Art/Gym)', 'Hallway/Transition', 'Office/Sick Bay', 'Library', 'Outside School Grounds']
ANTECEDENTS_FBA = ['Demand/Instruction Given', 'Transition Time', 'Peer Conflict/Teasing', 'Independent Work', 'High Noise/Stimulation', 'Seating Arrangement Change', 'Interrupted Activity', 'No Antecedent Identified']
FUNCTIONS_FBA = ['Attention (Peer/Staff)', 'Escape (Task/Activity)', 'Access (Preferred Item/Activity)', 'Sensory (Automatic Reinforcement)']

# --- Mock Data Generation ---

def generate_mock_data(n_logs=1000):
    """Generates a large, realistic-looking DataFrame of behaviour logs."""
    
    # Static list of mock students with associated roles (JP, PY, SY)
    students = [
        {'id': 'S101', 'name': 'Alex Johnson', 'role': 'JP'},
        {'id': 'S102', 'name': 'Bella Smith', 'role': 'JP'},
        {'id': 'S201', 'name': 'Charlie Brown', 'role': 'PY'},
        {'id': 'S202', 'name': 'Daisy Miller', 'role': 'PY'},
        {'id': 'S301', 'name': 'Ethan Davis', 'role': 'SY'},
        {'id': 'S302', 'name': 'Fiona Wilson', 'role': 'SY'},
    ]
    
    # Mock staff for observer dropdown
    MOCK_STAFF = [
        {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP'},
        {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY'},
        {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY'},
        {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM'},
        {'id': 's_trt', 'name': 'TRT', 'role': 'TRT'},
    ]
    
    data = []
    
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 11, 12)
    
    for _ in range(n_logs):
        student = random.choice(students)
        staff = random.choice(MOCK_STAFF)
        
        # Random date/time
        days_diff = (end_date - start_date).days
        random_day = start_date + timedelta(days=random.randint(0, days_diff))
        random_time = time(random.randint(8, 15), random.randint(0, 59))
        dt = datetime.combine(random_day.date(), random_time)
        
        # Behaviour, Antecedent, Consequence, Setting
        behaviour = random.choice(BEHAVIORS_FBA)
        antecedent = random.choice(ANTECEDENTS_FBA)
        consequence = random.choice(CONSEQUENCES_FBA)
        setting = random.choice(SETTING_FBA)
        
        # Function (often linked to behaviour/antecedent, but random for mock)
        function = random.choice(FUNCTIONS_FBA)
        
        # Intensity (Mock rating 1-5)
        intensity = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 30, 15, 5], k=1)[0]

        # Critical Incident Flag
        is_critical = True if intensity >= 4 and random.random() < 0.3 else False
        
        data.append({
            'log_id': str(uuid.uuid4()),
            'student_id': student['id'],
            'student_name': student['name'],
            'student_role': student['role'],
            'timestamp': dt,
            'date': dt.date(),
            'time': dt.time(),
            'observer_name': staff['name'],
            'observer_id': staff['id'],
            'antecedent': antecedent,
            'behaviour': behaviour,
            'consequence': consequence,
            'setting': setting,
            'function_hypothesis': function,
            'intensity': intensity,
            'duration_minutes': random.randint(1, 15),
            'notes': f"Log entry for {student['name']} showing {behaviour.lower()}.",
            'is_abch_completed': True,
            'is_critical': is_critical,
        })

    df = pd.DataFrame(data)
    
    # Add a 'month' column for filtering
    df['month'] = df['date'].apply(lambda x: x.strftime('%Y-%m'))
    
    # Sort by date
    df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
    
    return df

# --- Navigation and State Management ---

def initialize_state():
    """Initializes Streamlit session state variables."""
    if 'log_data' not in st.session_state:
        st.session_state.log_data = generate_mock_data()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None # Current student object for detail view

def navigate_to(page, role=None, student=None):
    """Handles navigation and state updates."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student:
        st.session_state.student = student
    st.rerun()

# --- Helper Functions ---

def get_filtered_data(df, role=None, student_id=None, month=None):
    """Filters the log data based on role, student, and time period."""
    filtered_df = df.copy()
    
    if student_id:
        filtered_df = filtered_df[filtered_df['student_id'] == student_id]
        
    elif role and role != 'ADM': # ADM sees all data
        filtered_df = filtered_df[filtered_df['student_role'] == role]
        
    if month:
        filtered_df = filtered_df[filtered_df['month'] == month]
        
    return filtered_df

def create_bar_chart(df, column, title, color_map=None):
    """Creates a standardized Plotly bar chart."""
    if df.empty:
        return st.warning("No data available for charting.")
        
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, 'Count']
    
    fig = px.bar(
        counts, 
        x='Count', 
        y=column, 
        orientation='h', 
        title=f'{title} Distribution ({len(df)} logs)',
        color=column, # Use column itself for color mapping
        color_discrete_map=color_map,
        template='plotly_dark' # Use dark theme
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=None,
        yaxis_title=None,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Page Rendering Functions ---

def render_landing_page():
    """Renders the initial landing page for role selection."""
    
    st.title("Behaviour Support & Data Analysis Tool")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Select Your Role")
        st.markdown("Please choose your staff area to access relevant data and logging tools.")
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        # JP Role Button
        if st.button('JP (Junior Primary) Staff Area', key='role_jp', use_container_width=True):
            navigate_to('staff_area', role='JP')

        # PY Role Button
        if st.button('PY (Primary) Staff Area', key='role_py', use_container_width=True):
            navigate_to('staff_area', role='PY')
        
        # SY Role Button (NEWLY ADDED)
        if st.button('SY (Senior Years) Staff Area', key='role_sy', use_container_width=True):
            navigate_to('staff_area', role='SY')

        # ADM Role Button
        if st.button('ADM (Administration/Leadership) Dashboard', key='role_adm', use_container_width=True):
            navigate_to('staff_area', role='ADM')
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.subheader("About the Tool")
        st.info(
            "This application enables staff to quickly log student behaviour incidents (ABCH Quick Log) "
            "and view real-time data analysis specific to their area (JP/PY/SY) or for the whole school (ADM)."
        )
        st.image("https://placehold.co/600x300/1E293B/F1F5F9?text=Data+Visualisation+Placeholder", caption="Example data trends for targeted support.")

def render_staff_area(role):
    """Renders the main dashboard for a specific staff role."""
    
    # Setup Header and Navigation
    st.header(f"Staff Dashboard: {role} Area")
    st.markdown("---")
    
    col_nav, col_title = st.columns([1, 4])
    with col_nav:
        if st.button('↩ Return to Role Select', key='back_to_landing', use_container_width=True):
            navigate_to('landing')
    with col_title:
        st.subheader("Overview & Quick Actions")
        
    # --- Critical Incident Warning ---
    # The Principal has been replaced with Manager, and examples have been removed.
    col_warn, col_log = st.columns([2, 1])
    
    with col_warn:
        with st.container(border=True):
            st.warning(
                """
                **Critical Incident Reporting Instructions:**

                1.  **Safety First:** Ensure all immediate safety concerns have been addressed.
                2.  **Immediate Notification:** Verbally notify the **Manager** or a member of the leadership team immediately if the incident involves:
                    * High-risk behaviours.
                    * Any incident requiring external support (Police, Ambulance).
                    * Any incident resulting in serious injury or property damage.
                3.  **Complete Log:** Complete the Quick Log (ABCH) form for data collection, then follow up with a formal Critical Incident Form (external system) within 24 hours.
                """
            )
            
    with col_log:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Quick Log")
        st.markdown("Select a student to log an incident now.")
        
        # Filter students relevant to the staff role (or all for ADM)
        all_students = st.session_state.log_data[['student_id', 'student_name', 'student_role']].drop_duplicates().sort_values('student_name')
        
        if role != 'ADM':
            area_students = all_students[all_students['student_role'] == role]
        else:
            area_students = all_students
            
        student_options = area_students['student_name'].tolist()
        
        selected_name = st.selectbox(
            'Select Student to Log Incident:',
            options=['-- Select --'] + student_options,
            key='log_student_select'
        )
        
        if selected_name != '-- Select --':
            selected_student_row = area_students[area_students['student_name'] == selected_name].iloc[0]
            selected_student_obj = {
                'id': selected_student_row['student_id'],
                'name': selected_name,
                'role': selected_student_row['student_role']
            }
            if st.button(f'Start Quick Log for {selected_name}', key='start_quick_log', use_container_width=True):
                navigate_to('quick_log', student=selected_student_obj)
        st.markdown('</div>', unsafe_allow_html=True)


    # --- Dashboard Metrics and Analysis ---
    
    st.markdown("## Data Overview")
    
    df_all = st.session_state.log_data
    df_filtered = get_filtered_data(df_all, role=role)
    
    # Time filter
    available_months = ['All Time'] + sorted(df_filtered['month'].unique(), reverse=True)
    selected_month = st.selectbox("Filter Data By Month:", options=available_months, index=0)

    if selected_month != 'All Time':
        df_display = get_filtered_data(df_filtered, month=selected_month)
    else:
        df_display = df_filtered

    col_metrics = st.columns(4)
    
    # Metric 1: Total Incidents
    col_metrics[0].metric(label=f"Total Incidents ({selected_month})", value=len(df_display))
    
    # Metric 2: Critical Incidents
    critical_count = df_display['is_critical'].sum()
    col_metrics[1].metric(label="Critical Incidents", value=critical_count)
    
    # Metric 3: Students Involved
    unique_students = df_display['student_id'].nunique()
    col_metrics[2].metric(label="Unique Students Logged", value=unique_students)
    
    # Metric 4: Average Intensity
    avg_intensity = df_display['intensity'].mean()
    col_metrics[3].metric(label="Average Intensity (1-5)", value=f"{avg_intensity:.2f}")

    # --- Charts ---
    
    st.markdown("### Top Behaviours & Functions")

    col_charts = st.columns(2)
    with col_charts[0]:
        create_bar_chart(df_display, 'behaviour', 'Behaviour Types')
        
    with col_charts[1]:
        create_bar_chart(df_display, 'function_hypothesis', 'Hypothesised Functions')

    st.markdown("### Log Detail & Student Selection")
    
    # Display recent logs
    st.dataframe(
        df_display[['timestamp', 'student_name', 'behaviour', 'antecedent', 'consequence', 'setting', 'intensity', 'is_critical', 'duration_minutes']]
        .head(20)
        .rename(columns={
            'timestamp': 'Date/Time', 
            'student_name': 'Student',
            'is_critical': 'Critical',
            'intensity': 'Int.',
            'antecedent': 'Antecedent',
            'consequence': 'Consequence',
            'behaviour': 'Behaviour',
            'setting': 'Setting',
            'duration_minutes': 'Duration (min)', # Duration remains visible in the data display
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Student Detail View Trigger
    st.markdown("---")
    st.subheader("View Detailed Student Analysis")
    
    analysis_options = df_display[['student_name', 'student_id']].drop_duplicates().sort_values('student_name')
    
    analysis_name = st.selectbox(
        'Select Student for Detailed Analysis:',
        options=['-- Select --'] + analysis_options['student_name'].tolist(),
        key='analysis_student_select'
    )
    
    if analysis_name != '-- Select --':
        selected_row = analysis_options[analysis_options['student_name'] == analysis_name].iloc[0]
        selected_student_obj = {
            'id': selected_row['student_id'],
            'name': analysis_name,
            'role': df_all[df_all['student_id'] == selected_row['student_id']]['student_role'].iloc[0]
        }
        if st.button(f'View Analysis for {analysis_name}', key='view_analysis', use_container_width=True):
            navigate_to('student_detail', student=selected_student_obj, role=role)

def render_quick_log(role, student):
    """Renders the streamlined ABCH Quick Log form."""
    
    st.header(f"ABCH Quick Log - {student['name']} ({student['role']})")
    
    col_nav, col_title = st.columns([1, 4])
    with col_nav:
        if st.button('↩ Back to Dashboard', key='back_to_dashboard', use_container_width=True):
            navigate_to('staff_area', role=role)
    with col_title:
        st.subheader("Record a Behaviour Incident")
        
    st.markdown("---")

    # The actual log form logic is highly simplified here, but mimics the structure.
    with st.form("quick_log_form", clear_on_submit=True):
        
        # --- Incident Details ---
        st.subheader("Incident Timing and Location")
        col_time, col_date, col_setting = st.columns(3)
        
        current_dt = datetime.now()
        
        with col_date:
            log_date = st.date_input("Date of Incident", current_dt.date())
        with col_time:
            log_time = st.time_input("Time of Incident", current_dt.time())
        with col_setting:
            setting = st.selectbox("Setting", options=SETTING_FBA)

        st.markdown("---")
        
        # --- ABCH Components ---
        st.subheader("Antecedent, Behaviour, Consequence")
        
        col_abc = st.columns(3)
        with col_abc[0]:
            antecedent = st.selectbox("Antecedent (A)", options=ANTECEDENTS_FBA, help="What happened immediately before the behaviour?")
            
        with col_abc[1]:
            behaviour = st.selectbox("Behaviour (B)", options=BEHAVIORS_FBA, help="The behaviour observed.")
            
        with col_abc[2]:
            consequence = st.selectbox("Consequence (C)", options=CONSEQUENCES_FBA, help="What happened immediately after the behaviour?")
            
        st.markdown("---")
        
        # --- Severity and Notes ---
        st.subheader("Severity and Context")
        
        # Removed the 'Duration' column, now just 2 columns
        col_sev, col_crit = st.columns(2) 
        
        with col_sev:
            intensity = st.slider("Intensity (1 = Low to 5 = High)", 1, 5, 3)
            
        with col_crit:
            is_critical = st.checkbox("Critical Incident?", value=(intensity >= 4)) # Pre-check if intensity is high
            st.markdown(
                f"""<div style='font-size: 12px; color: #94A3B8; margin-top: -10px;'>
                {":red[Check if this requires immediate Manager notification.]" if is_critical else "Low risk incident."}
                </div>""",
                unsafe_allow_html=True
            )

        notes = st.text_area("Additional Notes/Context (H)", max_chars=500, help="Human context, hypotheses, or general notes.")
        
        submitted = st.form_submit_button("Submit Quick Log", use_container_width=True)

    if submitted:
        # Create new log entry
        new_log = {
            'log_id': str(uuid.uuid4()),
            'student_id': student['id'],
            'student_name': student['name'],
            'student_role': student['role'],
            'timestamp': datetime.combine(log_date, log_time),
            'date': log_date,
            'time': log_time,
            'observer_name': next((s['name'] for s in [{'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP'}, {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY'}, {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY'}, {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM'}] if s['role'] == role), f'Unknown Staff ({role})'), # Simplified observer logic
            'observer_id': 's_mock',
            'antecedent': antecedent,
            'behaviour': behaviour,
            'consequence': consequence,
            'setting': setting,
            'function_hypothesis': random.choice(FUNCTIONS_FBA), # Mock function for quick log
            'intensity': intensity,
            # Setting a default duration since it was removed from the input form
            'duration_minutes': 5, 
            'notes': notes,
            'is_abch_completed': True,
            'is_critical': is_critical,
            'month': log_date.strftime('%Y-%m')
        }
        
        # Append to the session state DataFrame
        new_df = pd.DataFrame([new_log])
        st.session_state.log_data = pd.concat([st.session_state.log_data, new_df], ignore_index=True)
        st.session_state.log_data = st.session_state.log_data.sort_values('timestamp', ascending=False).reset_index(drop=True)
        
        st.success(f"Log submitted successfully for {student['name']}! Returning to dashboard.")
        
        # Clear student context and navigate back
        st.session_state.student = None
        navigate_to('staff_area', role=role)
        

def render_student_analysis(student, role):
    """Renders the detailed behaviour analysis for a specific student."""
    
    st.header(f"Detailed Behaviour Analysis: {student['name']} ({student['role']})")
    
    col_nav, col_title = st.columns([1, 4])
    with col_nav:
        if st.button('↩ Back to Dashboard', key='back_to_dashboard_detail', use_container_width=True):
            navigate_to('staff_area', role=role)
    with col_title:
        st.subheader(f"Insights for Targeted Support Planning")
        
    st.markdown("---")
    
    df_student = get_filtered_data(st.session_state.log_data, student_id=student['id'])
    
    if df_student.empty:
        st.warning(f"No log data found for {student['name']}.")
        return

    # --- Student Metrics ---
    col_metrics = st.columns(4)
    col_metrics[0].metric("Total Logs", len(df_student))
    col_metrics[1].metric("Avg. Intensity", f"{df_student['intensity'].mean():.2f}")
    col_metrics[2].metric("Critical Incidents", df_student['is_critical'].sum())
    
    # Calculate most common behaviour
    most_common_b = df_student['behaviour'].mode().iloc[0] if not df_student['behaviour'].mode().empty else 'N/A'
    col_metrics[3].metric("Most Frequent Behaviour", most_common_b)
    
    st.markdown("## ABC Functional Analysis")
    
    # --- ABC Charts ---
    col_charts_abc = st.columns(3)
    
    with col_charts_abc[0]:
        create_bar_chart(df_student, 'antecedent', 'Antecedent (A)')
        
    with col_charts_abc[1]:
        create_bar_chart(df_student, 'behaviour', 'Behaviour (B)')
        
    with col_charts_abc[2]:
        create_bar_chart(df_student, 'consequence', 'Consequence (C)')
        
    # --- Function & Setting Analysis ---
    st.markdown("## Hypotheses & Settings")
    col_hyp, col_set = st.columns(2)
    
    with col_hyp:
        create_bar_chart(df_student, 'function_hypothesis', 'Hypothesised Function')
        
    with col_set:
        create_bar_chart(df_student, 'setting', 'Setting of Incidents')
        
    st.markdown("## Trend Over Time")
    
    # Prepare data for time series
    df_trend = df_student.copy()
    df_trend.set_index('timestamp', inplace=True)
    
    # Resample daily and sum/mean
    daily_count = df_trend.resample('D')['log_id'].count().rename('Daily Logs')
    daily_intensity = df_trend.resample('D')['intensity'].mean().rename('Avg. Intensity')

    # Combine data for plotting
    df_combined = pd.concat([daily_count, daily_intensity], axis=1).fillna(0)
    
    # Plotting daily log counts
    fig_count = px.line(
        df_combined, 
        y='Daily Logs', 
        title='Incident Count Over Time',
        template='plotly_dark'
    )
    fig_count.update_layout(xaxis_title="Date", yaxis_title="Number of Logs")
    st.plotly_chart(fig_count, use_container_width=True)

    # Plotting average intensity
    fig_intensity = px.line(
        df_combined, 
        y='Avg. Intensity', 
        title='Average Incident Intensity Over Time',
        template='plotly_dark'
    )
    fig_intensity.update_layout(xaxis_title="Date", yaxis_title="Average Intensity (1-5)", yaxis_range=[1, 5])
    st.plotly_chart(fig_intensity, use_container_width=True)
    
    st.markdown("---")
    st.info("This analysis provides the foundation for developing a targeted Behaviour Support Plan.")
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


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
            st.error("Role context missing. Returning to landing.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
