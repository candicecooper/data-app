import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np
import time # Import time for sleep functionality in quick_log

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
    div[data-testid="stTextInput"] > div > textarea,
    .st-emotion-cache-1cpxdwl,
    .st-emotion-cache-13gs9y { background-color: #334155; color: #F1F5F9; border: 1px solid #475569; border-radius: 8px; }
    
    /* Buttons */
    .stButton > button {
        background-color: #4C1D95; /* Deep Purple */
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.2s;
        border: none;
    }
    .stButton > button:hover {
        background-color: #5B21B6; /* Lighter Purple on hover */
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Radio Buttons / Checkboxes */
    .stRadio > label, .stCheckbox > label {
        color: #E2E8F0;
    }
    .stRadio div[role="radiogroup"] div {
        background-color: #334155;
        border-radius: 6px;
        padding: 5px 10px;
        margin-bottom: 5px;
        border: 1px solid #475569;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #6366F1; /* Indigo accent */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stMetric"] > div > div:first-child {
        color: #94A3B8; /* Secondary text color */
    }
    [data-testid="stMetric"] > div > div:nth-child(2) {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F1F5F9;
    }
    
    /* General Container Styling */
    .st-emotion-cache-16ids9g { /* Main block container */
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar collapse button fix (if sidebar is used) */
    [data-testid="collapsed-sidebar"] {
        background-color: #1E293B !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- FBA Data, Staff Mock Data, and Helper Functions ---

# --- MOCK DATA REQUIRED FOR LOGGING DROPDOWNS ---
MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones (JP)', 'role': 'JP', 'active': True, 'special': False},
    {'id': 's2', 'name': 'Daniel Lee (PY)', 'role': 'PY', 'active': True, 'special': False},
    {'id': 's3', 'name': 'Sarah Chen (SY)', 'role': 'SY', 'active': True, 'special': False},
    {'id': 's4', 'name': 'Admin User (ADM)', 'role': 'ADM', 'active': True, 'special': False},
    {'id': 's_trt', 'name': 'TRT', 'role': 'TRT', 'active': True, 'special': True},
    {'id': 's_sso', 'name': 'External SSO', 'role': 'SSO', 'active': True, 'special': True},
]

# --- FBA and Data Constants ---

BEHAVIORS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Self-Injurious Behaviour', 'Outburst (Screaming/Crying)', 'Other']
ANTECEDENTS = ['Transition to non-preferred activity', 'Task demands/Request to work', 'Access to preferred item/activity denied', 'Peer interaction/conflict', 'Sensory overload (noise/light)', 'Unstructured time (recess/lunch)', 'Non-contingent attention removed', 'Other']
CONSEQUENCES = ['Sent to time-out/chill-out', 'Verbal reprimand/Correction', 'Loss of privilege/preferred item', 'Access to preferred item/activity provided', 'Ignored (extinction)', 'Escaped task demands', 'Counselling/Discussion', 'Physical intervention (safe hold)', 'Other']
SETTINGS = ['Classroom (Whole Group)', 'Classroom (Small Group)', 'Individual Workstation', 'Playground/Recess', 'Library/Specialist Room', 'Cafeteria', 'Hallway/Transition', 'Other (Specify)']
INTENSITY_LEVELS = {
    1: "Minimal (Muttering, minimal off-task, easily redirected)",
    2: "Low (Verbal protest, small disruptions, redirection effective within 3-5s)",
    3: "Medium (Verbal refusal/threats, moderate non-compliance, requires multiple redirections/calm-down time)",
    4: "High (Elopement, minor property destruction, sustained verbal abuse, requires staff support/removal)",
    5: "Critical (Assault/Injury/Major destruction, immediate risk, requires physical intervention/emergency services)"
}
DURATION_OPTIONS = ['< 1 minute', '1-5 minutes', '5-15 minutes', '15-30 minutes', '> 30 minutes']

# WOT_OPTIONS is renamed to RESOLUTION_STATUS_OPTIONS to match the uploaded code's intent in Step 2
RESOLUTION_STATUS_OPTIONS = ['Co-regulated/Settled quickly', 'Settled independently (long duration)', 'Still escalated/Unsettled', 'Sent home/Left area']

OUTCOME_MAPPINGS = {
    'o_a_send_home': 'Send Home/Exclusion',
    'o_b_left_area': 'Left Area (Staff Directed)',
    'o_c_assault': 'Assault (Peer/Staff)',
    'o_d_property_damage': 'Property Damage',
    'o_e_staff_injury': 'Staff Injury',
    'o_f_sapol_callout': 'SAPOL Callout',
    'o_g_restraint': 'Restraint/Physical Intervention',
    'o_h_seclusion': 'Seclusion/Isolation',
    'o_i_first_aid_minor': 'First Aid (Minor)',
    'o_j_first_aid_amb': 'First Aid (Ambulance)',
    'o_k_reportable': 'Reportable Incident (Mandatory)',
    'o_l_debrief': 'Staff Debrief Required',
    'o_m_follow_up_parent': 'Parent Follow-up',
    'o_n_follow_up_staff': 'Staff Follow-up/Plan Review',
    'o_o_counselling': 'Counselling Referral',
    'o_p_safety_plan_rev': 'Safety Plan Review',
    'o_q_other': 'Other (Specify)',
    'o_r_call_out_amb': 'Call Out (Ambulance)',
}

# --- Mock Data and Database Helpers ---

def get_active_staff():
    """Returns the names of all active staff members for selection."""
    active_staff = [s['name'] for s in MOCK_STAFF if s['active']]
    return active_staff

def save_quick_log_to_db(log_entry):
    """
    MOCK function to save the log entry to the database (or a DataFrame in this case).
    """
    if 'log_history' not in st.session_state:
        st.session_state['log_history'] = pd.DataFrame(columns=list(log_entry.keys()))
    
    # Ensure all list columns are correctly handled for concatenation
    for col in ['staff_involved', 'behaviors', 'consequences']:
        if col in log_entry and isinstance(log_entry[col], list):
             log_entry[col] = [log_entry[col]] # Wrap the list in a list for correct DataFrame creation
    
    new_row_df = pd.DataFrame([log_entry])
    st.session_state['log_history'] = pd.concat([st.session_state['log_history'], new_row_df], ignore_index=True)


# --- Mock Data for Students (Preserved) ---
MOCK_STUDENTS = [
    {'name': 'Alex Johnson', 'id': 's101', 'year': 5, 'plan_status': 'Tier 3 (BSP)', 'last_log_intensity': 4, 'total_logs': 15, 'key_behavior': 'Elopement'},
    {'name': 'Beth Smith', 'id': 's102', 'year': 7, 'plan_status': 'Tier 2 (Safety Plan)', 'last_log_intensity': 2, 'total_logs': 8, 'key_behavior': 'Verbal Refusal'},
    {'name': 'Charlie Brown', 'id': 's103', 'year': 9, 'plan_status': 'Tier 1 (Classroom)', 'last_log_intensity': 1, 'total_logs': 3, 'key_behavior': 'Disruption'},
    {'name': 'Dana White', 'id': 's104', 'year': 10, 'plan_status': 'Tier 3 (BSP)', 'last_log_intensity': 5, 'total_logs': 22, 'key_behavior': 'Aggression (Peer)'},
]

def get_student_data(student_name):
    """Retrieves mock data for a specific student."""
    return next((s for s in MOCK_STUDENTS if s['name'] == student_name), None)

def navigate_to(page, student=None, role=None):
    """Handles page navigation and updates session state."""
    st.session_state.page = page
    if student:
        st.session_state.student = student
    if role:
        st.session_state.role = role

def initialize_quick_log_state():
    """Initializes/resets the state variables for the two-step quick log."""
    if 'ql_step' not in st.session_state or st.session_state.ql_step == 'final':
        st.session_state.ql_step = 1
    if 'preliminary_data' not in st.session_state:
        st.session_state.preliminary_data = {
            'log_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'is_abch_completed': False,
        }
    # Reset critical outcome keys for clean slate on new log attempt
    for key in OUTCOME_MAPPINGS.keys():
        if key in st.session_state:
            del st.session_state[key]

# --- Incident Reporting UI Functions (CORRECTED TO USE TWO-STEP FLOW) ---

def render_quick_log(role, student_name):
    """
    Renders the two-step quick A-B-C-H log form based on the uploaded code structure.
    """
    initialize_quick_log_state()

    st.title(f"Quick Incident Log for {student_name}")
    st.caption(f"Staff Role: **{role}** | Log ID: {st.session_state.preliminary_data['log_id'][:8]} | Step: {st.session_state.ql_step} of 2")
    st.markdown("---")

    if st.session_state.ql_step == 1:
        st.subheader("Step 1: Antecedent, Behavior, Consequence (A-B-C)")
        
        with st.form("quick_log_step_1", clear_on_submit=False):
            
            # --- Context/Timing ---
            st.markdown("##### Context & Timing")
            col1, col2 = st.columns(2)
            with col1:
                log_date = st.date_input("Date of Incident", datetime.now().date(), key='ql_log_date')
                log_time = st.time_input("Time of Incident", datetime.now().time(), key='ql_log_time')
                setting = st.selectbox("Setting/Location", options=SETTINGS, key='ql_log_setting')
            
            with col2:
                logged_by_staff = st.selectbox("Staff Logging Incident", options=get_active_staff(), key='ql_log_staff')
                staff_involved = st.multiselect("Other Staff Involved (if any)", options=[s for s in get_active_staff() if s != logged_by_staff], key='ql_log_involved')

            st.markdown("---")

            # --- A - Antecedent
            st.markdown("#### A: Antecedent (What happened *immediately* before the behaviour?)")
            antecedent = st.selectbox("Primary Antecedent", options=ANTECEDENTS, key='ql_log_antecedent')
            
            # --- B - Behaviour
            st.markdown("#### B: Behaviour (What was the *observable* behaviour?)")
            col3, col4 = st.columns([2, 1])
            with col3:
                behaviors = st.multiselect("Observed Behaviours (Select all that apply)", options=BEHAVIORS_FBA, key='ql_log_behaviors')
            with col4:
                intensity = st.radio("Max Intensity Level", 
                                     options=list(INTENSITY_LEVELS.keys()), 
                                     format_func=lambda x: f"{x}: {INTENSITY_LEVELS[x].split('(')[0].strip()}", 
                                     key='ql_log_intensity', index=2, horizontal=True)

            # --- C - Consequence / Duration
            st.markdown("#### C: Consequence & Duration")
            col5, col6 = st.columns(2)
            with col5:
                consequences = st.multiselect("Observed Consequences (Select all that apply)", options=CONSEQUENCES, key='ql_log_consequences')
            with col6:
                duration = st.selectbox("Duration of Incident", options=DURATION_OPTIONS, key='ql_log_duration', index=1)
                
            st.markdown("---")

            if st.form_submit_button("Continue to Narrative (Step 2/2)"):
                # Save Step 1 data to preliminary_data
                st.session_state.preliminary_data.update({
                    'student_name': student_name,
                    'logged_by_role': role,
                    'log_date': log_date.isoformat(),
                    'log_time': log_time.isoformat(),
                    'setting': setting,
                    'logged_by_staff': logged_by_staff,
                    'staff_involved': staff_involved,
                    'antecedent': antecedent,
                    'behaviors': behaviors,
                    'intensity': intensity,
                    'consequences': consequences,
                    'duration': duration,
                })
                
                # Validation check for minimum data
                if not behaviors or not antecedent:
                    st.error("Please select at least one Behavior and the Antecedent before continuing.")
                    st.stop()
                
                # Move to Step 2
                st.session_state.ql_step = 2
                st.rerun()
                
    elif st.session_state.ql_step == 2:
        st.subheader("Step 2: Narrative, Plan (H), and Outcomes")
        
        preliminary_data = st.session_state.preliminary_data
        
        # Display key summary from Step 1
        st.info(f"Summary: Level **{preliminary_data['intensity']}** incident, triggered by **{preliminary_data['antecedent']}**, observed: **{', '.join(preliminary_data['behaviors'])}**.")
        
        with st.form("quick_log_step_2", clear_on_submit=True):
            
            # --- Narrative and H (Plan) ---
            st.markdown("#### Objective Narrative")
            incident_narrative = st.text_area(
                "Brief, Objective Context (What did you see, hear, and do?)",
                height=120,
                key='ql_incident_narrative'
            )

            st.markdown("#### H: Plan / Next Steps")
            how_to_respond_plan = st.text_area(
                "Effective strategies used & plan for next time (Required)",
                height=100,
                key='ql_how_to_respond'
            )
            
            st.markdown("---")

            # --- Resolution Status / Window of Tolerance (WOT) ---
            st.markdown("#### Resolution Status (WOT Check)")
            refined_wot = st.radio(
                "How was the situation resolved?",
                options=RESOLUTION_STATUS_OPTIONS,
                key='ql_refined_wot',
                index=0,
                horizontal=True
            )

            st.markdown("---")
            
            # --- Critical Incident Section (Conditional Display) ---
            is_critical = preliminary_data['intensity'] >= 4
            
            st.subheader(f"Critical Incident Outcomes (Required for Intensity {preliminary_data['intensity']} Logs)")
            
            # Display if intensity is 4 or 5
            if is_critical:
                st.warning("🚨 This log requires mandatory review due to high intensity. Please check all relevant outcomes.")
                
                with st.container(border=True):
                    st.markdown("##### Mandatory Outcomes")
                    col_cr_a, col_cr_b, col_cr_c = st.columns(3)
                    with col_cr_a:
                        st.checkbox(OUTCOME_MAPPINGS['o_c_assault'], key='o_c_assault')
                        st.checkbox(OUTCOME_MAPPINGS['o_d_property_damage'], key='o_d_property_damage')
                        st.checkbox(OUTCOME_MAPPINGS['o_e_staff_injury'], key='o_e_staff_injury')
                    with col_cr_b:
                        st.checkbox(OUTCOME_MAPPINGS['o_g_restraint'], key='o_g_restraint')
                        st.checkbox(OUTCOME_MAPPINGS['o_h_seclusion'], key='o_h_seclusion')
                        st.checkbox(OUTCOME_MAPPINGS['o_f_sapol_callout'], key='o_f_sapol_callout')
                    with col_cr_c:
                        st.checkbox(OUTCOME_MAPPINGS['o_i_first_aid_minor'], key='o_i_first_aid_minor')
                        st.checkbox(OUTCOME_MAPPINGS['o_j_first_aid_amb'], key='o_j_first_aid_amb')
                        st.checkbox(OUTCOME_MAPPINGS['o_k_reportable'], key='o_k_reportable')
                    
                    st.markdown("---")
                    
                    st.markdown("##### Follow-up & Plan Review")
                    col_cr_d, col_cr_e, col_cr_f = st.columns(3)
                    with col_cr_d:
                        st.checkbox(OUTCOME_MAPPINGS['o_a_send_home'], key='o_a_send_home')
                        st.checkbox(OUTCOME_MAPPINGS['o_b_left_area'], key='o_b_left_area')
                    with col_cr_e:
                        st.checkbox(OUTCOME_MAPPINGS['o_l_debrief'], key='o_l_debrief')
                        st.checkbox(OUTCOME_MAPPINGS['o_m_follow_up_parent'], key='o_m_follow_up_parent')
                    with col_cr_f:
                        st.checkbox(OUTCOME_MAPPINGS['o_n_follow_up_staff'], key='o_n_follow_up_staff')
                        st.checkbox(OUTCOME_MAPPINGS['o_p_safety_plan_rev'], key='o_p_safety_plan_rev')

            st.markdown("---")
            
            # --- Submission Button ---
            if st.form_submit_button("✅ Finalise and Save Incident Log"):
                
                # Final Validation
                if not how_to_respond_plan or len(how_to_respond_plan.split()) < 5:
                    st.error("The 'H: Plan / Next Steps' field is critical and requires a substantial plan (at least 5 words provided).")
                    st.stop()
                if not incident_narrative or len(incident_narrative.split()) < 5:
                    st.error("The 'Objective Narrative' field is critical and requires context (at least 5 words provided).")
                    st.stop()

                # Consolidate and Save Data
                log_entry = preliminary_data.copy()
                log_entry.update({
                    'is_abch_completed': True,
                    'wot_status': refined_wot,
                    'incident_narrative': incident_narrative,
                    'how_to_respond': how_to_respond_plan,
                    # Critical Outcomes - retrieve all checkbox values
                    'outcome_send_home': st.session_state.get('o_a_send_home', False),
                    'outcome_leave_area': st.session_state.get('o_b_left_area', False),
                    'outcome_assault': st.session_state.get('o_c_assault', False),
                    'outcome_property_damage': st.session_state.get('o_d_property_damage', False),
                    'outcome_staff_injury': st.session_state.get('o_e_staff_injury', False),
                    'outcome_sapol_callout': st.session_state.get('o_f_sapol_callout', False),
                    'outcome_restraint': st.session_state.get('o_g_restraint', False),
                    'outcome_seclusion': st.session_state.get('o_h_seclusion', False),
                    'outcome_first_aid_minor': st.session_state.get('o_i_first_aid_minor', False),
                    'outcome_first_aid_amb': st.session_state.get('o_j_first_aid_amb', False),
                    'outcome_reportable': st.session_state.get('o_k_reportable', False),
                    'outcome_debrief': st.session_state.get('o_l_debrief', False),
                    'outcome_follow_up_parent': st.session_state.get('o_m_follow_up_parent', False),
                    'outcome_follow_up_staff': st.session_state.get('o_n_follow_up_staff', False),
                    'outcome_counselling': st.session_state.get('o_o_counselling', False),
                    'outcome_safety_plan_rev': st.session_state.get('o_p_safety_plan_rev', False),
                    'outcome_other': st.session_state.get('o_q_other', False),
                    'outcome_ambulance': st.session_state.get('o_r_call_out_amb', False) or st.session_state.get('o_j_first_aid_amb', False),
                })
                
                save_quick_log_to_db(log_entry)
                
                # Clean up
                st.session_state.ql_step = 'final' # Use 'final' to signal successful completion
                del st.session_state.preliminary_data
                for key in OUTCOME_MAPPINGS.keys():
                    if key in st.session_state:
                        del st.session_state[key]

                st.success(f"Incident Log '{log_entry['log_id'][:8]}' successfully saved!")
                st.info("Log automatically navigates back to Student Detail in 1 second.")
                time.sleep(1) 
                navigate_to('student_detail', student=student_name, role=role)
                st.rerun()

    # Back button for Step 2
    if st.session_state.ql_step == 2:
        if st.button("⬅️ Back to Step 1 (A-B-C)", key="back_to_step1"):
            st.session_state.ql_step = 1
            st.rerun()

# This function is now a simple redirection, as the critical incident reporting is 
# integrated into the main quick log form (via the Critical Outcomes section).
def render_critical_incident(role, student_name):
    """
    Renders a redirection to the quick log, as the critical incident reporting is 
    integrated into the main quick log form (via the Critical Outcomes section).
    """
    st.header("Critical Incident Reporting")
    st.error("The Critical Incident Report functionality has been integrated directly into the Quick Log form (Step 2) and is mandatory for Intensity 4 & 5 incidents. Please use the Quick Log to record all incident details.")
    st.info(f"Navigate to Quick Log for {student_name}", icon="➡️")
    if st.button(f"Go to Quick Log for {student_name}"):
        navigate_to('quick_log', student=student_name, role=role)


# --- Student Analysis Function (Preserved) ---

def render_student_analysis(student_name, role):
    """Renders detailed analysis and reporting tools for a specific student."""
    st.title(f"Detailed Analysis: {student_name}")
    student_data = get_student_data(student_name)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Logs", student_data['total_logs'])
    with col_b:
        st.metric("Current Plan", student_data['plan_status'])
    with col_c:
        st.metric("Key Behaviour", student_data['key_behavior'])
        
    st.markdown("---")
    
    # Check if log history exists for plotting
    if 'log_history' in st.session_state and not st.session_state['log_history'].empty:
        df_logs = st.session_state['log_history']
        df_student = df_logs[df_logs['student_name'] == student_name].copy()
        
        if not df_student.empty:
            df_student['log_datetime'] = pd.to_datetime(df_student['log_date'] + ' ' + df_student['log_time'])
            
            st.subheader("Intensity Trend")
            fig_intensity = px.line(
                df_student.sort_values('log_datetime'),
                x='log_datetime',
                y='intensity',
                title='Incident Intensity Over Time',
                markers=True,
                color_discrete_sequence=['#6366F1']
            )
            fig_intensity.update_layout(
                xaxis_title="Date/Time",
                yaxis_title="Intensity Level",
                yaxis=dict(tickmode='array', tickvals=list(INTENSITY_LEVELS.keys()), ticktext=[str(k) for k in INTENSITY_LEVELS.keys()]),
                plot_bgcolor='#1E293B',
                paper_bgcolor='#1E293B',
                font_color='#F1F5F9'
            )
            st.plotly_chart(fig_intensity, use_container_width=True)
            
            st.markdown("---")
            
            col_chart_a, col_chart_b = st.columns(2)
            
            # Antecedent Distribution
            with col_chart_a:
                st.subheader("Antecedent Distribution")
                antecedent_counts = df_student['antecedent'].value_counts().reset_index()
                antecedent_counts.columns = ['Antecedent', 'Count']
                fig_ante = px.bar(
                    antecedent_counts,
                    x='Count',
                    y='Antecedent',
                    orientation='h',
                    title='Incident Triggers',
                    color='Count',
                    color_continuous_scale='Sunsetdark'
                )
                fig_ante.update_layout(
                    yaxis_title="",
                    plot_bgcolor='#1E293B',
                    paper_bgcolor='#1E293B',
                    font_color='#F1F5F9'
                )
                st.plotly_chart(fig_ante, use_container_width=True)

            # Behaviour Distribution
            with col_chart_b:
                st.subheader("Top Behaviours")
                # Flatten the list of behaviors
                all_behaviors = [b for sublist in df_student['behaviors'] for b in sublist]
                behavior_counts = pd.Series(all_behaviors).value_counts().reset_index()
                behavior_counts.columns = ['Behaviour', 'Count']
                fig_behav = px.pie(
                    behavior_counts.head(5),
                    values='Count',
                    names='Behaviour',
                    title='Top 5 Observable Behaviours',
                    color_discrete_sequence=px.colors.sequential.RdPu
                )
                fig_behav.update_layout(
                    showlegend=True,
                    plot_bgcolor='#1E293B',
                    paper_bgcolor='#1E293B',
                    font_color='#F1F5F9'
                )
                st.plotly_chart(fig_behav, use_container_width=True)


            st.markdown("---")
            st.subheader("Latest Incident Logs")
            st.dataframe(df_student[['log_datetime', 'intensity', 'antecedent', 'incident_narrative', 'how_to_respond']]
                         .sort_values('log_datetime', ascending=False)
                         .head(10),
                         use_container_width=True,
                         column_config={
                            "log_datetime": st.column_config.DatetimeColumn("Date/Time", format="YYYY-MM-DD HH:mm"),
                            "intensity": st.column_config.NumberColumn("Int", help="Max Intensity Level"),
                            "antecedent": "Antecedent",
                            "incident_narrative": "Narrative",
                            "how_to_respond": "Plan/Response"
                         })
                         
        else:
             st.info("No Quick Logs found for this student yet.")
    
    else:
        st.info("No Quick Logs have been recorded in the mock database.")

    st.markdown("---")
    
    # Action Buttons
    col_btn_a, col_btn_b, col_btn_c = st.columns(3)
    with col_btn_a:
        if st.button(f"➕ New Quick Log for {student_name}", use_container_width=True, key="new_log_btn"):
            navigate_to('quick_log', student=student_name, role=role)
    with col_btn_b:
        if st.button(f"🔙 Back to Staff Area", use_container_width=True, key="back_staff_btn"):
            navigate_to('staff_area', role=role)
    with col_btn_c:
        if role == 'ADM' and st.button(f"⚙️ Manage Plans/Staff (ADM)", use_container_width=True, key="manage_plans_btn"):
             st.warning("Management functionality not yet implemented.")


# --- Staff Area UI Function (Preserved) ---

def render_staff_area(role):
    """Renders the dashboard for staff to select a student and view summary metrics."""
    st.header(f"Staff Dashboard ({role} User)")
    st.subheader("Select a Student for Detailed Analysis or Quick Logging")

    # Mock Summary Metrics (using log history if available)
    total_incidents = st.session_state.get('log_history', pd.DataFrame()).shape[0]
    critical_incidents = st.session_state.get('log_history', pd.DataFrame()).query('intensity >= 4').shape[0]
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Students Monitored", len(MOCK_STUDENTS))
    with col_m2:
        st.metric("Total Incidents Logged", total_incidents)
    with col_m3:
        st.metric("Critical Incidents (Level 4/5)", critical_incidents, delta=f"{critical_incidents/total_incidents*100:.1f}% of total" if total_incidents else None)

    st.markdown("---")

    # Student Selector Table
    st.subheader("Current Focus Students")
    
    student_options = [s['name'] for s in MOCK_STUDENTS]
    selected_student = st.selectbox("Choose a Student:", options=['Select...'] + student_options)

    if selected_student != 'Select...':
        student_data = get_student_data(selected_student)
        st.markdown(f"**Student:** {student_data['name']} | **Year:** {student_data['year']} | **Plan:** {student_data['plan_status']}")
        
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            if st.button(f"View Analysis for {selected_student}", use_container_width=True, key="view_analysis_btn"):
                navigate_to('student_detail', student=selected_student, role=role)
        with col_s2:
            if st.button(f"Log Incident for {selected_student}", use_container_width=True, key="log_incident_btn"):
                navigate_to('quick_log', student=selected_student, role=role)
    
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


# --- Landing Page (Preserved) ---

def render_landing_page():
    """Renders the initial landing page for role selection."""
    st.title("Behaviour Support & Data Analysis Tool")
    st.subheader("Select Your Role to Access the Dashboard")
    
    col_j, col_p, col_a = st.columns(3)
    
    with col_j:
        if st.button("Junior Primary (JP) Staff", use_container_width=True):
            navigate_to('staff_area', role='JP')
    with col_p:
        if st.button("Primary (PY/SY) Staff", use_container_width=True):
            navigate_to('staff_area', role='PY')
    with col_a:
        if st.button("Admin/Leadership (ADM)", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


# --- State Initialization (Preserved) ---

def initialize_state():
    """Initializes session state variables if they don't exist."""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'student' not in st.session_state:
        st.session_state.student = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'user_id' not in st.session_state:
        # Mock user ID for demonstration
        st.session_state.user_id = str(uuid.uuid4())[:8]

    # Initialize log history if missing (mock database)
    if 'log_history' not in st.session_state:
        # Column list derived from the fields in save_quick_log_to_db and render_quick_log
        log_columns = [
            'log_id', 'student_name', 'logged_by_role', 'timestamp', 'is_abch_completed',
            'log_date', 'log_time', 'setting', 'logged_by_staff', 'staff_involved',
            'antecedent', 'behaviors', 'intensity', 'consequences', 'duration',
            'wot_status', 'incident_narrative', 'how_to_respond', 
            # Critical Outcomes (must match keys used in the save logic of render_quick_log)
            'outcome_send_home', 'outcome_leave_area', 'outcome_assault', 'outcome_property_damage', 
            'outcome_staff_injury', 'outcome_sapol_callout', 'outcome_restraint', 'outcome_seclusion',
            'outcome_first_aid_minor', 'outcome_first_aid_amb', 'outcome_reportable', 'outcome_debrief', 
            'outcome_follow_up_parent', 'outcome_follow_up_staff', 'outcome_counselling', 'outcome_safety_plan_rev', 
            'outcome_other', 'outcome_ambulance',
        ]
        st.session_state['log_history'] = pd.DataFrame(columns=log_columns)


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
            st.error("Role context missing. Returning to landing page.")
            navigate_to('landing')

    elif st.session_state.page == 'critical_incident':
        if current_student and current_role:
            # Note: This route now forces navigation back to the quick log as it's the integrated flow
            render_critical_incident(current_role, current_student)
        else:
             st.error("Missing context. Returning to dashboard.")
             navigate_to('staff_area', role=current_role)

if __name__ == "__main__":
    main()
