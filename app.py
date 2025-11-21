import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json
import os
from docx import Document
from docx.shared import Inches, RGBColor, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# Page configuration - Clean and professional
st.set_page_config(
    page_title="Incident Reporting System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional, minimalistic styling - light gray background
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #34495e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .severity-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 2px solid;
        background-color: white;
    }
    .severity-low {
        border-color: #27ae60;
        color: #27ae60;
    }
    .severity-medium {
        border-color: #f39c12;
        color: #f39c12;
    }
    .severity-high {
        border-color: #e74c3c;
        color: #e74c3c;
    }
    .form-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 4px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'quick_incidents' not in st.session_state:
    st.session_state.quick_incidents = []
if 'critical_incidents' not in st.session_state:
    st.session_state.critical_incidents = []
if 'baps' not in st.session_state:
    st.session_state.baps = []

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Quick Incident Form", "Critical Incident Form", "BAP Form", "Analytics Dashboard"]
)

# Helper function to save data
def save_data():
    data = {
        'quick_incidents': st.session_state.quick_incidents,
        'critical_incidents': st.session_state.critical_incidents,
        'baps': st.session_state.baps
    }
    with open('incident_data.json', 'w') as f:
        json.dump(data, f, default=str)

# Helper function to load data
def load_data():
    if os.path.exists('incident_data.json'):
        with open('incident_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.quick_incidents = data.get('quick_incidents', [])
            st.session_state.critical_incidents = data.get('critical_incidents', [])
            st.session_state.baps = data.get('baps', [])

# Load data on startup
load_data()

# ==================== QUICK INCIDENT FORM ====================
if page == "Quick Incident Form":
    st.markdown('<div class="main-header">Quick Incident Report</div>', unsafe_allow_html=True)
    
    with st.form("quick_incident_form"):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        # Basic Information
        st.markdown('<div class="section-header">Basic Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", value="", key="qi_student")
            incident_date = st.date_input("Date of Incident *", value=None, key="qi_date")
        with col2:
            staff_name = st.text_input("Staff Member Name *", value="", key="qi_staff")
            incident_time = st.time_input("Time of Incident", value=None, key="qi_time")
        
        # Incident Details
        st.markdown('<div class="section-header">Incident Details</div>', unsafe_allow_html=True)
        location = st.selectbox(
            "Location *",
            ["", "Classroom", "Playground", "Cafeteria", "Hallway", "Bathroom", "Bus", "Other"],
            key="qi_location"
        )
        
        if location == "Other":
            location_other = st.text_input("Please specify location", value="", key="qi_location_other")
        
        behavior_type = st.multiselect(
            "Behavior Type *",
            ["Physical Aggression", "Verbal Aggression", "Property Destruction", 
             "Self-Injury", "Elopement", "Refusal", "Disruption", "Other"],
            default=[],
            key="qi_behavior"
        )
        
        description = st.text_area(
            "Brief Description *",
            value="",
            height=150,
            placeholder="Describe what happened...",
            key="qi_description"
        )
        
        # Severity Assessment
        st.markdown('<div class="section-header">Severity Assessment</div>', unsafe_allow_html=True)
        severity = st.selectbox(
            "Severity Level *",
            ["", "Low - Minor disruption, no injury", 
             "Medium - Moderate disruption, minor injury risk",
             "High - Major disruption, injury occurred or high risk"],
            key="qi_severity"
        )
        
        # Response Actions
        st.markdown('<div class="section-header">Response Actions</div>', unsafe_allow_html=True)
        interventions = st.multiselect(
            "Interventions Used",
            ["Verbal Redirect", "Physical Prompt", "Removal from Area", "Break Offered",
             "De-escalation Techniques", "Restraint (Document separately)", "Other"],
            default=[],
            key="qi_interventions"
        )
        
        outcome = st.text_area(
            "Outcome/Resolution",
            value="",
            height=100,
            placeholder="How was the situation resolved?",
            key="qi_outcome"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Submit Quick Incident Report", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([student_name, incident_date, staff_name, location, behavior_type, description, severity]):
                st.error("⚠️ Please fill in all required fields marked with *")
            else:
                incident = {
                    'type': 'Quick Incident',
                    'timestamp': datetime.now().isoformat(),
                    'student_name': student_name,
                    'staff_name': staff_name,
                    'incident_date': str(incident_date),
                    'incident_time': str(incident_time) if incident_time else "",
                    'location': location,
                    'behavior_type': behavior_type,
                    'description': description,
                    'severity': severity,
                    'interventions': interventions,
                    'outcome': outcome
                }
                st.session_state.quick_incidents.append(incident)
                save_data()
                st.success("✅ Quick incident report submitted successfully!")
                st.balloons()

# ==================== CRITICAL INCIDENT FORM ====================
elif page == "Critical Incident Form":
    st.markdown('<div class="main-header">Critical Incident Report</div>', unsafe_allow_html=True)
    st.info("📌 Use this form for serious incidents requiring detailed documentation and chronological tracking.")
    
    with st.form("critical_incident_form"):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        # Basic Information
        st.markdown('<div class="section-header">Basic Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            ci_student = st.text_input("Student Name *", value="", key="ci_student")
            ci_date = st.date_input("Date of Incident *", value=None, key="ci_date")
            ci_location = st.text_input("Location *", value="", key="ci_location")
        with col2:
            ci_staff = st.text_input("Reporting Staff Member *", value="", key="ci_staff")
            ci_start_time = st.time_input("Incident Start Time *", value=None, key="ci_start")
            ci_end_time = st.time_input("Incident End Time", value=None, key="ci_end")
        
        # Incident Classification
        st.markdown('<div class="section-header">Incident Classification</div>', unsafe_allow_html=True)
        ci_type = st.multiselect(
            "Incident Type *",
            ["Physical Aggression (Staff)", "Physical Aggression (Peer)", "Physical Aggression (Self)",
             "Property Destruction", "Elopement/AWOL", "Verbal Threats", "Sexual Behavior",
             "Medical Emergency", "Other Crisis"],
            default=[],
            key="ci_type"
        )
        
        injuries = st.radio(
            "Were there any injuries? *",
            ["", "No", "Yes - Minor", "Yes - Requiring Medical Attention"],
            key="ci_injuries"
        )
        
        if "Yes" in str(injuries):
            injury_details = st.text_area(
                "Injury Details *",
                value="",
                placeholder="Describe injuries and treatment provided...",
                key="ci_injury_details"
            )
        
        # CHRONOLOGY SECTION - This is the critical structure!
        st.markdown('<div class="section-header">⏱️ Incident Chronology (Timeline)</div>', unsafe_allow_html=True)
        st.markdown("**Document the incident in chronological order with times and details**")
        
        # Dynamic chronology entries
        if 'chronology_entries' not in st.session_state:
            st.session_state.chronology_entries = 1
        
        chronology_data = []
        
        for i in range(st.session_state.chronology_entries):
            st.markdown(f"**Entry {i+1}**")
            col1, col2 = st.columns([1, 4])
            with col1:
                entry_time = st.time_input(
                    f"Time",
                    value=None,
                    key=f"chrono_time_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                entry_description = st.text_area(
                    f"What happened",
                    value="",
                    height=80,
                    placeholder="Describe what occurred at this time...",
                    key=f"chrono_desc_{i}",
                    label_visibility="collapsed"
                )
            
            chronology_data.append({
                'time': str(entry_time) if entry_time else "",
                'description': entry_description
            })
            
            st.markdown("---")
        
        # Antecedent Information
        st.markdown('<div class="section-header">Antecedent Information</div>', unsafe_allow_html=True)
        antecedent = st.text_area(
            "What was happening before the incident? *",
            value="",
            height=120,
            placeholder="Describe the context, triggers, or events leading up to the incident...",
            key="ci_antecedent"
        )
        
        # Response and Interventions
        st.markdown('<div class="section-header">Response and Interventions</div>', unsafe_allow_html=True)
        interventions_used = st.multiselect(
            "Interventions/Strategies Used *",
            ["Verbal De-escalation", "Environmental Modification", "Physical Escort",
             "Physical Restraint", "Seclusion/Time-out", "Crisis Intervention",
             "Emergency Services Called", "Other"],
            default=[],
            key="ci_interventions"
        )
        
        if "Physical Restraint" in interventions_used:
            restraint_duration = st.text_input(
                "Restraint Duration *",
                value="",
                placeholder="e.g., 5 minutes",
                key="ci_restraint_duration"
            )
            restraint_type = st.text_input(
                "Type of Restraint *",
                value="",
                key="ci_restraint_type"
            )
        
        response_details = st.text_area(
            "Detailed Response Description *",
            value="",
            height=120,
            placeholder="Describe all actions taken during and after the incident...",
            key="ci_response"
        )
        
        # Outcome and Follow-up
        st.markdown('<div class="section-header">Outcome and Follow-up</div>', unsafe_allow_html=True)
        resolution = st.text_area(
            "How was the incident resolved? *",
            value="",
            height=100,
            key="ci_resolution"
        )
        
        notifications = st.multiselect(
            "Notifications Made",
            ["Parent/Guardian", "Administrator", "School Psychologist", "Behavior Specialist",
             "Medical Personnel", "Law Enforcement", "Other"],
            default=[],
            key="ci_notifications"
        )
        
        follow_up = st.text_area(
            "Follow-up Actions Required",
            value="",
            height=100,
            placeholder="List any follow-up actions, meetings, or reviews needed...",
            key="ci_followup"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.form_submit_button("➕ Add Another Chronology Entry"):
                st.session_state.chronology_entries += 1
                st.rerun()
        with col2:
            submitted = st.form_submit_button("Submit Critical Incident", use_container_width=True)
        
        if submitted:
            # Validate required fields
            required_fields = [ci_student, ci_date, ci_start_time, ci_location, ci_staff, 
                             ci_type, injuries, antecedent, interventions_used, 
                             response_details, resolution]
            
            if not all([f for f in required_fields if f != ""]):
                st.error("⚠️ Please fill in all required fields marked with *")
            else:
                incident = {
                    'type': 'Critical Incident',
                    'timestamp': datetime.now().isoformat(),
                    'student_name': ci_student,
                    'staff_name': ci_staff,
                    'incident_date': str(ci_date),
                    'start_time': str(ci_start_time),
                    'end_time': str(ci_end_time) if ci_end_time else "",
                    'location': ci_location,
                    'incident_type': ci_type,
                    'injuries': injuries,
                    'injury_details': injury_details if "Yes" in str(injuries) else "",
                    'chronology': chronology_data,
                    'antecedent': antecedent,
                    'interventions': interventions_used,
                    'restraint_info': {
                        'duration': restraint_duration if "Physical Restraint" in interventions_used else "",
                        'type': restraint_type if "Physical Restraint" in interventions_used else ""
                    },
                    'response_details': response_details,
                    'resolution': resolution,
                    'notifications': notifications,
                    'follow_up': follow_up
                }
                st.session_state.critical_incidents.append(incident)
                st.session_state.chronology_entries = 1  # Reset
                save_data()
                st.success("✅ Critical incident report submitted successfully!")
                st.balloons()

# ==================== BAP FORM ====================
elif page == "BAP Form":
    st.markdown('<div class="main-header">Behavior Analysis Plan (BAP)</div>', unsafe_allow_html=True)
    
    with st.form("bap_form"):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        # Student Information
        st.markdown('<div class="section-header">Student Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            bap_student = st.text_input("Student Name *", value="", key="bap_student")
            bap_grade = st.text_input("Grade/Class", value="", key="bap_grade")
            bap_date = st.date_input("Plan Date *", value=None, key="bap_date")
        with col2:
            bap_teacher = st.text_input("Teacher/Case Manager *", value="", key="bap_teacher")
            bap_team = st.text_input("Team Members", value="", key="bap_team")
            bap_review = st.date_input("Review Date", value=None, key="bap_review")
        
        # Target Behaviors
        st.markdown('<div class="section-header">Target Behaviors</div>', unsafe_allow_html=True)
        target_behavior = st.text_area(
            "Operational Definition of Target Behavior(s) *",
            value="",
            height=120,
            placeholder="Clearly define the behavior(s) to be addressed...",
            key="bap_target"
        )
        
        # Functional Assessment
        st.markdown('<div class="section-header">Functional Assessment</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Hypothesized Function(s):**")
            functions = st.multiselect(
                "Select all that apply",
                ["Attention Seeking", "Escape/Avoidance", "Access to Tangibles",
                 "Sensory Stimulation", "Communication", "Multiple Functions"],
                default=[],
                key="bap_functions"
            )
        
        with col2:
            st.write("**Setting Events/Triggers:**")
            triggers = st.text_area(
                "",
                value="",
                height=100,
                placeholder="What increases likelihood of behavior?",
                key="bap_triggers"
            )
        
        antecedents = st.text_area(
            "Common Antecedents *",
            value="",
            height=100,
            placeholder="What typically happens right before the behavior?",
            key="bap_antecedents"
        )
        
        consequences = st.text_area(
            "Typical Consequences *",
            value="",
            height=100,
            placeholder="What typically happens after the behavior?",
            key="bap_consequences"
        )
        
        # Prevention Strategies
        st.markdown('<div class="section-header">Prevention Strategies</div>', unsafe_allow_html=True)
        prevention = st.text_area(
            "Proactive Strategies *",
            value="",
            height=150,
            placeholder="List strategies to prevent the behavior from occurring...",
            key="bap_prevention"
        )
        
        # Teaching Strategies
        st.markdown('<div class="section-header">Replacement Behaviors & Teaching</div>', unsafe_allow_html=True)
        replacement = st.text_area(
            "Replacement Behavior(s) to Teach *",
            value="",
            height=120,
            placeholder="What appropriate behavior(s) will serve the same function?",
            key="bap_replacement"
        )
        
        teaching = st.text_area(
            "Teaching Procedures *",
            value="",
            height=120,
            placeholder="How will the replacement behavior be taught?",
            key="bap_teaching"
        )
        
        # Response Strategies
        st.markdown('<div class="section-header">Response Strategies</div>', unsafe_allow_html=True)
        response = st.text_area(
            "When Target Behavior Occurs *",
            value="",
            height=120,
            placeholder="How should staff respond to the target behavior?",
            key="bap_response"
        )
        
        reinforcement = st.text_area(
            "Reinforcement Plan *",
            value="",
            height=120,
            placeholder="How will appropriate behavior be reinforced?",
            key="bap_reinforcement"
        )
        
        # Data Collection
        st.markdown('<div class="section-header">Data Collection</div>', unsafe_allow_html=True)
        data_method = st.multiselect(
            "Data Collection Method(s) *",
            ["Frequency Count", "Duration", "Interval Recording", "ABC Data",
             "Behavior Rating Scale", "Other"],
            default=[],
            key="bap_data_method"
        )
        
        data_frequency = st.selectbox(
            "Data Collection Frequency *",
            ["", "Continuous", "Daily", "Weekly", "As Needed"],
            key="bap_data_freq"
        )
        
        success_criteria = st.text_area(
            "Success Criteria *",
            value="",
            height=100,
            placeholder="What are the measurable goals?",
            key="bap_criteria"
        )
        
        # Additional Notes
        st.markdown('<div class="section-header">Additional Information</div>', unsafe_allow_html=True)
        additional_notes = st.text_area(
            "Additional Notes/Considerations",
            value="",
            height=100,
            key="bap_notes"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submitted = st.form_submit_button("Submit BAP", use_container_width=True)
        
        if submitted:
            # Validate required fields
            required_fields = [
                bap_student, bap_date, bap_teacher, target_behavior, antecedents,
                consequences, prevention, replacement, teaching, response,
                reinforcement, data_method, data_frequency, success_criteria
            ]
            
            if not all([f for f in required_fields if f != "" and f != []]):
                st.error("⚠️ Please fill in all required fields marked with *")
            else:
                bap = {
                    'type': 'BAP',
                    'timestamp': datetime.now().isoformat(),
                    'student_name': bap_student,
                    'grade': bap_grade,
                    'plan_date': str(bap_date),
                    'teacher': bap_teacher,
                    'team': bap_team,
                    'review_date': str(bap_review) if bap_review else "",
                    'target_behavior': target_behavior,
                    'functions': functions,
                    'triggers': triggers,
                    'antecedents': antecedents,
                    'consequences': consequences,
                    'prevention': prevention,
                    'replacement': replacement,
                    'teaching': teaching,
                    'response': response,
                    'reinforcement': reinforcement,
                    'data_method': data_method,
                    'data_frequency': data_frequency,
                    'success_criteria': success_criteria,
                    'additional_notes': additional_notes
                }
                st.session_state.baps.append(bap)
                save_data()
                st.success("✅ Behavior Analysis Plan submitted successfully!")
                
                # Generate Word Document with graphs
                st.info("📄 Generating BAP document with analytics...")
                doc_buffer = generate_bap_word_document(bap)
                
                st.download_button(
                    label="📥 Download BAP Document (with graphs)",
                    data=doc_buffer,
                    file_name=f"BAP_{bap_student.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                st.balloons()

# ==================== ANALYTICS DASHBOARD ====================
elif page == "Analytics Dashboard":
    st.markdown('<div class="main-header">Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Quick Incidents", len(st.session_state.quick_incidents))
    with col2:
        st.metric("Critical Incidents", len(st.session_state.critical_incidents))
    with col3:
        st.metric("BAPs Created", len(st.session_state.baps))
    with col4:
        total = len(st.session_state.quick_incidents) + len(st.session_state.critical_incidents)
        st.metric("Total Incidents", total)
    
    if st.session_state.quick_incidents or st.session_state.critical_incidents:
        # Combine incidents for analysis
        all_incidents = []
        
        for inc in st.session_state.quick_incidents:
            all_incidents.append({
                'Type': 'Quick',
                'Student': inc['student_name'],
                'Date': inc['incident_date'],
                'Severity': inc['severity'].split(' - ')[0] if inc.get('severity') else 'Unknown',
                'Behaviors': ', '.join(inc.get('behavior_type', [])),
                'Location': inc.get('location', 'Unknown')
            })
        
        for inc in st.session_state.critical_incidents:
            all_incidents.append({
                'Type': 'Critical',
                'Student': inc['student_name'],
                'Date': inc['incident_date'],
                'Severity': 'High',
                'Behaviors': ', '.join(inc.get('incident_type', [])),
                'Location': inc.get('location', 'Unknown')
            })
        
        df = pd.DataFrame(all_incidents)
        
        # Severity Distribution - Professional colors (green, orange, red)
        st.markdown('<div class="section-header">Incident Severity Distribution</div>', unsafe_allow_html=True)
        severity_counts = df['Severity'].value_counts()
        
        # Professional color mapping
        color_map = {
            'Low': '#27ae60',      # Green
            'Medium': '#f39c12',   # Orange
            'High': '#e74c3c'      # Red
        }
        
        fig_severity = go.Figure(data=[
            go.Bar(
                x=severity_counts.index,
                y=severity_counts.values,
                marker_color=[color_map.get(sev, '#95a5a6') for sev in severity_counts.index],
                text=severity_counts.values,
                textposition='auto'
            )
        ])
        fig_severity.update_layout(
            title="Incidents by Severity Level",
            xaxis_title="Severity",
            yaxis_title="Count",
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False
        )
        st.plotly_chart(fig_severity, use_container_width=True)
        
        # Incidents by Student
        st.markdown('<div class="section-header">Incidents by Student</div>', unsafe_allow_html=True)
        student_counts = df['Student'].value_counts().head(10)
        fig_students = px.bar(
            x=student_counts.values,
            y=student_counts.index,
            orientation='h',
            color_discrete_sequence=['#3498db']
        )
        fig_students.update_layout(
            title="Top 10 Students by Incident Count",
            xaxis_title="Number of Incidents",
            yaxis_title="Student Name",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_students, use_container_width=True)
        
        # Incidents over time
        st.markdown('<div class="section-header">Incident Trends</div>', unsafe_allow_html=True)
        df['Date'] = pd.to_datetime(df['Date'])
        timeline = df.groupby('Date').size().reset_index(name='Count')
        fig_timeline = px.line(
            timeline,
            x='Date',
            y='Count',
            markers=True,
            color_discrete_sequence=['#3498db']
        )
        fig_timeline.update_layout(
            title="Incidents Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Incidents",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Location analysis
        st.markdown('<div class="section-header">Incidents by Location</div>', unsafe_allow_html=True)
        location_counts = df['Location'].value_counts()
        fig_location = px.pie(
            values=location_counts.values,
            names=location_counts.index,
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_location.update_layout(
            title="Incident Distribution by Location",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_location, use_container_width=True)
        
        # Data table
        st.markdown('<div class="section-header">Recent Incidents</div>', unsafe_allow_html=True)
        st.dataframe(df.sort_values('Date', ascending=False).head(20), use_container_width=True)
        
        # Export options
        st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"incidents_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col2:
            json_data = json.dumps({
                'quick_incidents': st.session_state.quick_incidents,
                'critical_incidents': st.session_state.critical_incidents,
                'baps': st.session_state.baps
            }, indent=2, default=str)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name=f"incidents_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    else:
        st.info("📊 No incidents recorded yet. Submit some incidents to see analytics.")

# ==================== WORD DOCUMENT GENERATION WITH GRAPHS ====================
def generate_bap_word_document(bap_data):
    """Generate a professional BAP Word document with embedded graphs"""
    doc = Document()
    
    # Title
    title = doc.add_heading('Behavior Analysis Plan (BAP)', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Student Information
    doc.add_heading('Student Information', 1)
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Light Grid Accent 1'
    
    info_fields = [
        ('Student Name:', bap_data['student_name']),
        ('Grade/Class:', bap_data['grade']),
        ('Plan Date:', bap_data['plan_date']),
        ('Teacher/Case Manager:', bap_data['teacher']),
        ('Team Members:', bap_data['team']),
        ('Review Date:', bap_data['review_date'])
    ]
    
    for i, (label, value) in enumerate(info_fields):
        table.rows[i].cells[0].text = label
        table.rows[i].cells[0].paragraphs[0].runs[0].bold = True
        table.rows[i].cells[1].text = str(value)
    
    doc.add_paragraph()
    
    # Target Behavior
    doc.add_heading('Target Behavior(s)', 1)
    doc.add_paragraph(bap_data['target_behavior'])
    
    # Functional Assessment
    doc.add_heading('Functional Assessment', 1)
    doc.add_paragraph(f"Hypothesized Functions: {', '.join(bap_data['functions'])}")
    doc.add_paragraph(f"Setting Events/Triggers: {bap_data['triggers']}")
    doc.add_paragraph(f"Common Antecedents: {bap_data['antecedents']}")
    doc.add_paragraph(f"Typical Consequences: {bap_data['consequences']}")
    
    # Strategies
    doc.add_heading('Prevention Strategies', 1)
    doc.add_paragraph(bap_data['prevention'])
    
    doc.add_heading('Replacement Behaviors & Teaching', 1)
    doc.add_paragraph(f"Replacement Behavior(s): {bap_data['replacement']}")
    doc.add_paragraph(f"Teaching Procedures: {bap_data['teaching']}")
    
    doc.add_heading('Response Strategies', 1)
    doc.add_paragraph(f"When Target Behavior Occurs: {bap_data['response']}")
    doc.add_paragraph(f"Reinforcement Plan: {bap_data['reinforcement']}")
    
    # Data Collection
    doc.add_heading('Data Collection Plan', 1)
    doc.add_paragraph(f"Methods: {', '.join(bap_data['data_method'])}")
    doc.add_paragraph(f"Frequency: {bap_data['data_frequency']}")
    doc.add_paragraph(f"Success Criteria: {bap_data['success_criteria']}")
    
    # Additional Notes
    if bap_data['additional_notes']:
        doc.add_heading('Additional Notes', 1)
        doc.add_paragraph(bap_data['additional_notes'])
    
    # Add Analytics Section with Graphs
    doc.add_page_break()
    doc.add_heading('Student Behavior Analytics', 1)
    
    # Filter incidents for this student
    student_incidents = []
    for inc in st.session_state.quick_incidents:
        if inc['student_name'] == bap_data['student_name']:
            student_incidents.append(inc)
    for inc in st.session_state.critical_incidents:
        if inc['student_name'] == bap_data['student_name']:
            student_incidents.append(inc)
    
    if student_incidents:
        doc.add_paragraph(f"Total Incidents for {bap_data['student_name']}: {len(student_incidents)}")
        
        # Create and embed graphs
        try:
            # Behavior frequency graph
            behaviors = {}
            for inc in student_incidents:
                inc_behaviors = inc.get('behavior_type', []) or inc.get('incident_type', [])
                for behavior in inc_behaviors:
                    behaviors[behavior] = behaviors.get(behavior, 0) + 1
            
            if behaviors:
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(behaviors.keys()),
                        y=list(behaviors.values()),
                        marker_color='#3498db'
                    )
                ])
                fig.update_layout(
                    title=f"Behavior Frequency for {bap_data['student_name']}",
                    xaxis_title="Behavior Type",
                    yaxis_title="Frequency",
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                # Save graph as image
                img_bytes = fig.to_image(format="png", width=1000, height=600)
                img_stream = io.BytesIO(img_bytes)
                doc.add_picture(img_stream, width=Inches(6))
                
            # Severity over time (if applicable)
            severity_data = []
            for inc in student_incidents:
                if 'incident_date' in inc and 'severity' in inc:
                    severity_data.append({
                        'date': inc['incident_date'],
                        'severity': inc['severity'].split(' - ')[0] if ' - ' in inc.get('severity', '') else 'Unknown'
                    })
            
            if len(severity_data) > 1:
                doc.add_paragraph()
                df_sev = pd.DataFrame(severity_data)
                df_sev['date'] = pd.to_datetime(df_sev['date'])
                df_sev = df_sev.sort_values('date')
                
                severity_map = {'Low': 1, 'Medium': 2, 'High': 3}
                df_sev['severity_num'] = df_sev['severity'].map(severity_map)
                
                fig2 = go.Figure(data=go.Scatter(
                    x=df_sev['date'],
                    y=df_sev['severity_num'],
                    mode='lines+markers',
                    marker=dict(size=10, color='#e74c3c'),
                    line=dict(color='#e74c3c', width=2)
                ))
                fig2.update_layout(
                    title="Incident Severity Trend",
                    xaxis_title="Date",
                    yaxis_title="Severity Level",
                    yaxis=dict(ticktext=['', 'Low', 'Medium', 'High'], tickvals=[0, 1, 2, 3]),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                img_bytes2 = fig2.to_image(format="png", width=1000, height=600)
                img_stream2 = io.BytesIO(img_bytes2)
                doc.add_picture(img_stream2, width=Inches(6))
                
        except Exception as e:
            doc.add_paragraph(f"Note: Unable to generate graphs. {str(e)}")
    else:
        doc.add_paragraph("No incident data available for this student yet.")
    
    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Footer
st.sidebar.markdown("---")
st.sidebar.info("📋 Incident Reporting System v2.0\n\nProfessional behavior tracking and analysis")
