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
    div[data-testid="stSelectbox"] > div > div > div > input,
    div[data-testid="stDateInput"] > div > input,
    div[data-testid="stTimeInput"] > div > input,
    .stTextArea textarea {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #4C1D95; /* Deep Purple */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #6D28D9;
    }
    .stButton > button:active {
        background-color: #5B21B6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    
    /* Metric/Info Boxes */
    .stMetric, .stAlert {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stAlert.info { background-color: #1E3A8A; border-left: 5px solid #3B82F6; }
    .stAlert.success { background-color: #065F46; border-left: 5px solid #10B981; }

    /* Multiselect checkboxes */
    div[data-baseweb="checkbox"] > label {
        color: #E2E8F0;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- FBA and Data Constants ---

BEHAVIORS_FBA = [
    'Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)',
    'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)', 'Aggression (Staff)',
    'Non-compliance', 'Other'
]

WOT_CATEGORIES = {
    "Green Zone (Optimal)": "The student is calm, focused, and able to learn.",
    "Yellow Zone (Caution)": "The student is showing signs of agitation, distraction, or mild distress.",
    "Red Zone (Crisis)": "The student is exhibiting severe distress, aggression, or inability to self-regulate."
}

# NEW CONSTANT: Incident Locations
INCIDENT_LOCATIONS = [
    'jp program', 'py program', 'sy program',
    'jp spill out', 'py spill out', 'sy spill out',
    'gate', 'admin', 'playground', 'toilets',
    'student kitchen', 'excursion', 'library', 'swimming',
    'van/kia', 'other'
]

# Mock Staff Data (for demonstration of roles and assignees)
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# Mock Student Data (including sample logs for analysis)
STUDENTS_DATA = {
    'stu-101': {'name': 'Alex Johnson', 'class': 'JP-B', 'year': 5, 'logs': []},
    'stu-102': {'name': 'Ben Carter', 'class': 'PY-A', 'year': 8, 'logs': [
        {'id': str(uuid.uuid4()), 'date': datetime(2025, 10, 20), 'time': time(10, 30), 'behavior': 'Verbal Refusal', 'location': 'jp program', 'wot': 'Red Zone (Crisis)', 'duration': 15, 'context': 'Transition to Maths.', 'responder': 'Emily Jones (JP)'},
        {'id': str(uuid.uuid4()), 'date': datetime(2025, 10, 25), 'time': time(14, 0), 'behavior': 'Non-compliance', 'location': 'playground', 'wot': 'Yellow Zone (Caution)', 'duration': 5, 'context': 'During free play.', 'responder': 'Daniel Lee (PY)'},
        {'id': str(uuid.uuid4()), 'date': datetime(2025, 11, 1), 'time': time(9, 15), 'behavior': 'Elopement', 'location': 'gate', 'wot': 'Red Zone (Crisis)', 'duration': 20, 'context': 'Drop-off area.', 'responder': 'Admin User (ADM)'},
    ]},
    'stu-103': {'name': 'Chloe Davis', 'class': 'SY-C', 'year': 11, 'logs': []},
}

# --- Utility Functions ---

def get_staff_names(role=None):
    """Returns a list of staff names, optionally filtered by role."""
    if role:
        return [s['name'] for s in MOCK_STAFF if s['role'] == role or s['special']]
    return [s['name'] for s in MOCK_STAFF if s['active']]

def get_all_student_names():
    """Returns a dictionary of student IDs mapped to their full names."""
    return {uid: data['name'] for uid, data in STUDENTS_DATA.items()}

def initialize_state():
    """Initializes session state variables."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'log_data' not in st.session_state:
        st.session_state.log_data = STUDENTS_DATA

def navigate_to(page, role=None, student_id=None):
    """Handles navigation and state updates."""
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student_id:
        st.session_state.student = student_id
    # Rerun the app to effect navigation
    st.experimental_rerun()

def get_logs_dataframe(student_id):
    """Returns the incident logs for a student as a DataFrame."""
    logs = st.session_state.log_data.get(student_id, {}).get('logs', [])
    if not logs:
        return pd.DataFrame()
    df = pd.DataFrame(logs)
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df = df.sort_values('datetime', ascending=False)
    return df

# --- Render Functions ---

def render_landing_page():
    """Renders the initial page for role selection."""
    st.title("Welcome to the Behaviour Support & Data Analysis Tool")
    st.markdown("Please select your role to proceed.")

    roles = ['JP (Junior Program) Staff', 'PY (Primary Program) Staff', 'SY (Senior Program) Staff', 'ADM (Administration)']
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("JP Staff", use_container_width=True):
        navigate_to('staff_area', role='JP')
    if col2.button("PY Staff", use_container_width=True):
        navigate_to('staff_area', role='PY')
    if col3.button("SY Staff", use_container_width=True):
        navigate_to('staff_area', role='SY')
    if col4.button("Admin", use_container_width=True):
        navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")

def render_staff_area(role):
    """Renders the main staff dashboard."""
    role_map = {'JP': 'Junior Program', 'PY': 'Primary Program', 'SY': 'Senior Program', 'ADM': 'Administration'}
    st.title(f"{role_map.get(role, 'Staff')} Dashboard")
    
    # Navigation to Logout
    if st.sidebar.button("⬅️ Logout"):
        navigate_to('landing', role=None)

    # Student Selection Area
    st.subheader("Select Student for Logging or Review")
    
    student_options = get_all_student_names()
    student_names = list(student_options.values())
    
    selected_name = st.selectbox(
        "Choose a Student:",
        options=["Select a student..."] + student_names,
        key="staff_select_student"
    )

    selected_id = None
    if selected_name != "Select a student...":
        selected_id = next((uid for uid, name in student_options.items() if name == selected_name), None)

    col_btn1, col_btn2 = st.columns(2)

    if selected_id:
        if col_btn1.button(f"📝 Start Quick Log for {selected_name}", use_container_width=True):
            navigate_to('quick_log', student_id=selected_id)
        
        if col_btn2.button(f"📊 View Analysis for {selected_name}", use_container_width=True):
            navigate_to('student_detail', student_id=selected_id)
    else:
        col_btn1.button("📝 Start Quick Log", disabled=True, use_container_width=True)
        col_btn2.button("📊 View Analysis", disabled=True, use_container_width=True)

    st.markdown("---")
    
    # Program Overview Placeholder
    st.subheader(f"{role_map.get(role, 'Program')} Overview (Live Incidents)")
    st.warning("Feature not yet implemented: This area would show a real-time feed of active incidents or recent high-priority logs.")

def render_quick_log(current_role, student_id):
    """Renders the multi-step Quick Incident Log form."""
    student_name = STUDENTS_DATA.get(student_id, {}).get('name', 'Unknown Student')
    
    st.title(f"Quick Incident Log for {student_name}")
    st.caption(f"Logged by **{current_role}** Staff")

    if st.sidebar.button("⬅️ Back to Dashboard"):
        navigate_to('staff_area', role=current_role)

    # --- Incident Log Form ---
    with st.form("quick_log_form", clear_on_submit=True):
        
        st.info("Fill out the mandatory fields (marked with *) to save a preliminary log. Complete all sections for a full FBA record.")
        
        # --- Screen 1: Incident Core Details ---
        st.subheader("1. Incident Core Details")
        col1, col2 = st.columns(2)

        # Mandatory fields
        with col1:
            log_date = st.date_input("Date of Incident *", datetime.now().date())
            log_time = st.time_input("Start Time of Incident *", datetime.now().time().replace(second=0, microsecond=0))
            
            # --- UPDATED LOCATION SELECTBOX ---
            incident_location = st.selectbox(
                "Incident Location *",
                options=INCIDENT_LOCATIONS,
                index=INCIDENT_LOCATIONS.index('jp program') if 'jp program' in INCIDENT_LOCATIONS else 0, # Default to 'jp program' if exists
                key="log_location"
            )

        with col2:
            duration = st.number_input("Duration (minutes) *", min_value=1, max_value=180, value=5)
            
            # Staff Responder
            responder_options = get_staff_names()
            default_responder = next((name for name in responder_options if f"({current_role})" in name), responder_options[0] if responder_options else "N/A")
            
            responder = st.selectbox(
                "Primary Staff Responder *",
                options=responder_options,
                index=responder_options.index(default_responder) if default_responder in responder_options else 0,
                key="log_responder"
            )
            
            # Mandatory Behavior
            behavior = st.selectbox(
                "Primary Behavior Displayed *",
                options=BEHAVIORS_FBA,
                key="log_behavior"
            )
        
        st.markdown("---")

        # --- Screen 2: Antecedent, WOT & Context ---
        st.subheader("2. Context & Window of Tolerance (ABCH-A)")
        
        # Window of Tolerance (WOT)
        wot_key = st.radio(
            "Student's Window of Tolerance (WOT) Status *",
            options=list(WOT_CATEGORIES.keys()),
            index=0,
            key="log_wot_key",
            help="Select the student's emotional/arousal state at the time of the incident."
        )

        st.markdown(f"**WOT Description:** {WOT_CATEGORIES.get(wot_key, 'N/A')}")
        
        # Context/Antecedent
        context = st.text_area(
            "What was happening immediately *before* the incident (Antecedent/Context)? *",
            height=100,
            key="log_context"
        )
        
        st.markdown("---")

        # --- Screen 3: Consequence & Outcomes ---
        st.subheader("3. Consequence & Outcome (ABCH-C)")
        
        # Consequence
        consequence = st.text_area(
            "What did staff and peers do *immediately after* the behavior (Consequence)? *",
            height=100,
            key="log_consequence"
        )

        st.markdown("**Incident Outcomes/Referrals (Check all that apply):**")
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            st.checkbox("A. Sent Home", key='o_a_send_home')
            st.checkbox("D. Property Damage", key='o_d_property_damage')
            st.checkbox("G. Restraint Applied (Physical)", key='o_g_restraint_p')
        with col_o2:
            st.checkbox("B. Left Area (Time Out/Exit)", key='o_b_left_area')
            st.checkbox("E. Staff Injury (Reported)", key='o_e_staff_injury')
            st.checkbox("H. Restraint Applied (Chemical)", key='o_h_restraint_c')
        with col_o3:
            st.checkbox("C. Assault (Peer/Staff)", key='o_c_assault')
            st.checkbox("F. SAPOL Callout", key='o_f_sapol_callout')
            st.checkbox("I. Other / Referral", key='o_i_other_referral')
        
        st.markdown("---")

        # --- Submit Button ---
        submit_button = st.form_submit_button("Save Incident Log")

        if submit_button:
            # Simple mandatory field check (Streamlit typically handles empty text inputs unless you set default)
            if not all([log_date, log_time, incident_location, duration, responder, behavior, context, consequence]):
                st.error("Please fill in all mandatory fields (*).")
            else:
                # 1. Compile log entry
                new_log_entry = {
                    'id': str(uuid.uuid4()),
                    'date': log_date,
                    'time': log_time,
                    'behavior': behavior,
                    'location': incident_location,
                    'wot': wot_key,
                    'duration': duration,
                    'context': context,
                    'consequence': consequence,
                    'responder': responder,
                    'outcome_send_home': st.session_state.get('o_a_send_home', False),
                    'outcome_leave_area': st.session_state.get('o_b_left_area', False),
                    'outcome_assault': st.session_state.get('o_c_assault', False),
                    'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
                    'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
                    'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
                    'outcome_restraint_p': st.session_state.get('o_g_restraint_p', False),
                    'outcome_restraint_c': st.session_state.get('o_h_restraint_c', False),
                    'outcome_other_referral': st.session_state.get('o_i_other_referral', False),
                }

                # 2. Save log entry to student data (Mock save)
                if student_id in st.session_state.log_data:
                    st.session_state.log_data[student_id]['logs'].append(new_log_entry)
                    st.success(f"Log for {student_name} saved successfully! Navigating back to analysis...")
                    
                    # 3. Clean up and navigate
                    for key in ['o_a_send_home', 'o_b_left_area', 'o_c_assault', 'o_d_property_damage', 
                                'o_e_staff_injury', 'o_f_sapol_callout', 'o_g_restraint_p', 
                                'o_h_restraint_c', 'o_i_other_referral']:
                        if key in st.session_state:
                            del st.session_state[key]
                            
                    # Navigate back to student detail page after saving
                    navigate_to('student_detail', student_id=student_id)
                else:
                    st.error("Error: Could not find student to save log against.")


def render_student_analysis(student_id, current_role):
    """Renders the analysis page for a specific student."""
    student_data = STUDENTS_DATA.get(student_id, {})
    student_name = student_data.get('name', 'N/A')
    
    st.title(f"Analysis for {student_name}")
    st.header(f"Class: {student_data.get('class', 'N/A')} | Year: {student_data.get('year', 'N/A')}")
    
    if st.sidebar.button("⬅️ Back to Dashboard"):
        navigate_to('staff_area', role=current_role)
    
    df_logs = get_logs_dataframe(student_id)

    if df_logs.empty:
        st.info("No incident logs available for this student yet. Start a Quick Log now!")
        if st.button("📝 Start Quick Log"):
            navigate_to('quick_log', student_id=student_id)
        return

    st.markdown("---")
    st.subheader(f"Total Incidents Logged: {len(df_logs)}")

    tab1, tab2 = st.tabs(["Data Visualizations", "Raw Log History"])

    with tab1:
        st.subheader("Key Incident Trends")
        
        col_viz1, col_viz2 = st.columns(2)

        # 1. Behavior Frequency
        behavior_counts = df_logs['behavior'].value_counts().reset_index()
        behavior_counts.columns = ['Behavior', 'Count']
        fig_behavior = px.bar(
            behavior_counts, 
            x='Count', 
            y='Behavior', 
            orientation='h',
            title='Top Behaviors Displayed',
            color='Count',
            color_continuous_scale=px.colors.sequential.Plotly3
        )
        fig_behavior.update_layout(template="plotly_dark")
        col_viz1.plotly_chart(fig_behavior, use_container_width=True)

        # 2. Location Frequency
        location_counts = df_logs['location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        fig_location = px.bar(
            location_counts, 
            x='Count', 
            y='Location', 
            orientation='h',
            title='Incident Locations',
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_location.update_layout(template="plotly_dark")
        col_viz2.plotly_chart(fig_location, use_container_width=True)

        st.markdown("---")

        col_viz3, col_viz4 = st.columns(2)

        # 3. WOT Distribution
        wot_counts = df_logs['wot'].value_counts().reindex(list(WOT_CATEGORIES.keys())).fillna(0).reset_index()
        wot_counts.columns = ['WOT Zone', 'Count']
        fig_wot = px.pie(
            wot_counts, 
            names='WOT Zone', 
            values='Count',
            title='WOT Zone Distribution',
            color_discrete_map={
                "Green Zone (Optimal)": "#10B981", # Green
                "Yellow Zone (Caution)": "#FCD34D", # Yellow
                "Red Zone (Crisis)": "#EF4444"    # Red
            }
        )
        fig_wot.update_layout(template="plotly_dark")
        col_viz3.plotly_chart(fig_wot, use_container_width=True)

        # 4. Responder Frequency
        responder_counts = df_logs['responder'].value_counts().reset_index()
        responder_counts.columns = ['Responder', 'Count']
        fig_responder = px.bar(
            responder_counts, 
            x='Responder', 
            y='Count', 
            title='Staff Responder Frequency',
            color='Count',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_responder.update_layout(template="plotly_dark")
        col_viz4.plotly_chart(fig_responder, use_container_width=True)


    with tab2:
        st.subheader("Detailed Incident History")
        # Display the log data, selecting relevant columns for clarity
        display_df = df_logs[['date', 'time', 'location', 'behavior', 'wot', 'duration', 'responder', 'context', 'consequence']].copy()
        display_df.columns = ['Date', 'Time', 'Location', 'Behavior', 'WOT Zone', 'Duration (min)', 'Responder', 'Antecedent/Context', 'Consequence']
        
        st.dataframe(display_df, use_container_width=True)


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
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == '__main__':
    main()
