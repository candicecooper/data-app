import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
import uuid
import random
from collections import Counter
from io import BytesIO

st.set_page_config(page_title="CLC Behaviour Support", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# HIGH CONTRAST STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 0.75rem 2rem !important; font-weight: 600 !important; font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5) !important; transition: all 0.3s ease !important;
    }
    .stButton>button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.7) !important; }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%) !important;
        color: #000 !important; font-weight: 700 !important;
    }
    
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: white !important; border-radius: 15px !important; padding: 2rem !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important; font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
    }
    [data-testid="stMetricLabel"] { color: #333 !important; font-weight: 600 !important; }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea,
    .stDateInput>div>div>input, .stTimeInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 10px !important; border: 2px solid #667eea !important;
        background: white !important; color: #000 !important; font-weight: 500 !important;
    }
    
    h1 { color: white !important; font-weight: 800 !important; font-size: 3rem !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important; }
    h2 { color: white !important; font-weight: 700 !important; font-size: 2rem !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important; }
    h3 { color: white !important; font-weight: 600 !important; font-size: 1.5rem !important; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3) !important; }
    
    label { color: #1a1a1a !important; font-weight: 600 !important; }
    
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important; font-weight: 700 !important;
    }
    
    .stSuccess { background: #d1fae5 !important; border-left: 4px solid #10b981 !important; color: #065f46 !important; }
    .stInfo { background: #dbeafe !important; border-left: 4px solid #3b82f6 !important; color: #1e40af !important; }
    .stWarning { background: #fef3c7 !important; border-left: 4px solid #f59e0b !important; color: #92400e !important; }
    
    .streamlit-expanderHeader { background: rgba(255, 255, 255, 0.95) !important; color: #1a1a1a !important; font-weight: 600 !important; }
    .stMarkdown p { color: #1a1a1a !important; line-height: 1.6 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15); border-left: 6px solid #667eea;'>
    <h2 style='color: #667eea; margin: 0; font-size: 1.4rem; text-shadow: none;'>🎭 SANDBOX DEMONSTRATION MODE</h2>
    <p style='color: #333; margin: 0.5rem 0 0 0; font-weight: 500;'>
        This version uses synthetic data only. No real student information is included.
    </p>
</div>
""", unsafe_allow_html=True)

# MOCK DATA
MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP", "email": "emily.jones@example.com"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY", "email": "daniel.lee@example.com"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY", "email": "sarah.chen@example.com"},
    {"id": "s4", "name": "Admin User", "role": "ADM", "email": "admin.user@example.com"},
]

MOCK_STUDENTS = [
    {"id": "stu_jp1", "name": "Emma T.", "grade": "R", "dob": "2018-05-30", "edid": "ED12348", "program": "JP"},
    {"id": "stu_jp2", "name": "Oliver S.", "grade": "Y1", "dob": "2017-09-12", "edid": "ED12349", "program": "JP"},
    {"id": "stu_jp3", "name": "Sophie M.", "grade": "Y2", "dob": "2016-03-20", "edid": "ED12350", "program": "JP"},
    {"id": "stu_py1", "name": "Liam C.", "grade": "Y3", "dob": "2015-06-15", "edid": "ED12351", "program": "PY"},
    {"id": "stu_py2", "name": "Ava R.", "grade": "Y4", "dob": "2014-11-08", "edid": "ED12352", "program": "PY"},
    {"id": "stu_py3", "name": "Noah B.", "grade": "Y6", "dob": "2012-02-28", "edid": "ED12353", "program": "PY"},
    {"id": "stu_sy1", "name": "Isabella G.", "grade": "Y7", "dob": "2011-04-17", "edid": "ED12354", "program": "SY"},
    {"id": "stu_sy2", "name": "Ethan D.", "grade": "Y9", "dob": "2009-12-03", "edid": "ED12355", "program": "SY"},
    {"id": "stu_sy3", "name": "Mia A.", "grade": "Y11", "dob": "2007-08-20", "edid": "ED12356", "program": "SY"},
]

PROGRAM_NAMES = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}
SUPPORT_TYPES = ["1:1 Individual Support", "Independent", "Small Group", "Large Group"]
BEHAVIOUR_TYPES = ["Verbal Refusal", "Elopement", "Property Destruction", "Aggression (Peer)", "Aggression (Adult)", "Self-Harm", "Verbal Aggression", "Other"]
ANTECEDENTS = ["Requested to transition activity", "Given instruction / demand (Academic)", "Peer conflict / teasing", "Staff attention shifted away", 
               "Unstructured free time (Recess/Lunch)", "Sensory overload (noise / lights)", "Access to preferred item denied", "Change in routine or expectation", "Difficult task presented"]
INTERVENTIONS = ["Used calm tone and supportive stance (CPI)", "Offered a break / time away", "Reduced task demand / chunked task", "Provided choices",
                "Removed audience / peers", "Used visual supports", "Co-regulated with breathing / grounding", "Prompted use of coping skill", "Redirection to preferred activity"]
LOCATIONS = ["JP Classroom", "JP Spill Out", "PY Classroom", "PY Spill Out", "SY Classroom", "SY Spill Out", "Student Kitchen", 
             "Admin", "Gate", "Library", "Playground", "Yard", "Toilets", "Excursion", "Swimming"]
VALID_PAGES = ["login", "landing", "program_students", "incident_log", "critical_incident", "student_analysis", "program_overview"]

# SEVERITY GUIDE
def show_severity_guide():
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>
        <h3 style='color: #667eea; text-shadow: none; margin-bottom: 1rem;'>📊 Severity Level Guide</h3>
        <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;'>
            <div style='background: #d1fae5; padding: 1rem; border-radius: 10px; border-left: 4px solid #10b981;'>
                <h4 style='color: #065f46; text-shadow: none; margin: 0;'>1 - Low Level</h4>
                <p style='color: #065f46; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Persistent minor behaviours (talking out, off-task, minor refusal)</p>
            </div>
            <div style='background: #dbeafe; padding: 1rem; border-radius: 10px; border-left: 4px solid #3b82f6;'>
                <h4 style='color: #1e40af; text-shadow: none; margin: 0;'>2 - Disruptive</h4>
                <p style='color: #1e40af; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Impacts others' learning (loud disruption, leaving area, property misuse)</p>
            </div>
            <div style='background: #fef3c7; padding: 1rem; border-radius: 10px; border-left: 4px solid #f59e0b;'>
                <h4 style='color: #92400e; text-shadow: none; margin: 0;'>3 - Concerning</h4>
                <p style='color: #92400e; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Escalated behaviour (verbal aggression, elopement, throwing objects)</p>
            </div>
            <div style='background: #fed7aa; padding: 1rem; border-radius: 10px; border-left: 4px solid #ea580c;'>
                <h4 style='color: #7c2d12; text-shadow: none; margin: 0;'>4 - Serious</h4>
                <p style='color: #7c2d12; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Physical aggression towards others or property destruction</p>
            </div>
            <div style='background: #fee2e2; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc2626;'>
                <h4 style='color: #991b1b; text-shadow: none; margin: 0;'>5 - Critical</h4>
                <p style='color: #991b1b; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Severe violence, injury caused, or significant safety risk</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# EMAIL NOTIFICATION
def send_critical_incident_email(incident_data, student, staff_email, manager_email="manager@clc.sa.edu.au"):
    try:
        st.info(f"""📧 **Email Notification Sent**
        
**To:** {manager_email}, {staff_email}
**Subject:** CRITICAL INCIDENT ALERT - {student['name']}

**Details:**
- Student: {student['name']} ({student['program']} - Grade {student['grade']})
- Date/Time: {incident_data.get('created_at', 'N/A')}
- Behaviour: {incident_data.get('ABCH_primary', {}).get('B', 'N/A')}
- Safety Responses: {', '.join(incident_data.get('safety_responses', []))}

*(In production, this sends actual emails via SMTP)*
        """)
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# WORD DOCUMENT WITH GRAPHS
def generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level):
    try:
        from docx import Document
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        title = doc.add_heading('Behaviour Analysis Plan', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Student Information', 1)
        student_table = doc.add_table(rows=4, cols=2)
        student_table.style = 'Light Grid Accent 1'
        student_table.rows[0].cells[0].text = 'Student Name:'
        student_table.rows[0].cells[1].text = student['name']
        student_table.rows[1].cells[0].text = 'Program:'
        student_table.rows[1].cells[1].text = student['program']
        student_table.rows[2].cells[0].text = 'Grade:'
        student_table.rows[2].cells[1].text = student['grade']
        student_table.rows[3].cells[0].text = 'Report Date:'
        student_table.rows[3].cells[1].text = datetime.now().strftime('%d/%m/%Y')
        
        doc.add_paragraph()
        
        doc.add_heading('Executive Summary', 1)
        summary_para = doc.add_paragraph()
        summary_para.add_run(f"Total Incidents: ").bold = True
        summary_para.add_run(f"{len(full_df)}\n")
        summary_para.add_run(f"Critical Incidents: ").bold = True
        summary_para.add_run(f"{len(full_df[full_df['incident_type'] == 'Critical'])}\n")
        summary_para.add_run(f"Average Severity: ").bold = True
        summary_para.add_run(f"{full_df['severity'].mean():.2f}\n")
        summary_para.add_run(f"Risk Level: ").bold = True
        summary_para.add_run(f"{risk_level} ({risk_score}/100)")
        
        doc.add_paragraph()
        
        doc.add_heading('Summary of Data Findings', 1)
        findings = doc.add_paragraph()
        findings.add_run('Primary Concern: ').bold = True
        findings.add_run(f"{top_beh} is the most frequently recorded behaviour.\n\n")
        findings.add_run('Key Triggers: ').bold = True
        findings.add_run(f"The most common antecedent is '{top_ant}'.\n\n")
        findings.add_run('Hotspot Locations: ').bold = True
        findings.add_run(f"Incidents occur most in {top_loc}, during {top_session}.")
        
        doc.add_paragraph()
        
        doc.add_heading('Visual Analytics', 1)
        
        # Graph 1: Daily Trend
        doc.add_heading('Daily Incident Trend', 2)
        daily_counts = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=daily_counts["date_parsed"], y=daily_counts["count"], mode='lines+markers',
                                  line=dict(color='#667eea', width=2), fill='tozeroy'))
        fig1.update_layout(title="Daily Incidents", xaxis_title="Date", yaxis_title="Count", height=300, width=600)
        img_path1 = "/tmp/daily_trend.png"
        fig1.write_image(img_path1)
        doc.add_picture(img_path1, width=Inches(6))
        doc.add_paragraph("Frequency of incidents over time.")
        doc.add_paragraph()
        
        # Graph 2: Behaviour Distribution
        doc.add_heading('Behaviour Type Distribution', 2)
        beh_counts = full_df["behaviour_type"].value_counts()
        fig2 = go.Figure(data=[go.Pie(labels=beh_counts.index, values=beh_counts.values, hole=0.3)])
        fig2.update_layout(height=400, width=600)
        img_path2 = "/tmp/behaviour_pie.png"
        fig2.write_image(img_path2)
        doc.add_picture(img_path2, width=Inches(5))
        doc.add_paragraph(f"Primary: {beh_counts.index[0]} ({(beh_counts.values[0]/len(full_df)*100):.1f}%)")
        doc.add_paragraph()
        
        # Graph 3: Risk Gauge
        doc.add_heading('Current Risk Level', 2)
        risk_color_map = {"LOW": "#10b981", "MODERATE": "#f59e0b", "HIGH": "#ef4444"}
        fig3 = go.Figure(go.Indicator(mode="gauge+number", value=risk_score, title={'text': "Risk Score"},
                                      gauge={'axis': {'range': [None, 100]}, 'bar': {'color': risk_color_map.get(risk_level, "#666")},
                                             'steps': [{'range': [0, 30], 'color': "#d1fae5"}, {'range': [30, 60], 'color': "#fef3c7"}, 
                                                      {'range': [60, 100], 'color': "#fee2e2"}]}))
        fig3.update_layout(height=300, width=500)
        img_path3 = "/tmp/risk_gauge.png"
        fig3.write_image(img_path3)
        doc.add_picture(img_path3, width=Inches(4))
        doc.add_paragraph(f"Risk Level: {risk_level} ({risk_score}/100)")
        doc.add_paragraph()
        
        doc.add_heading('Clinical Interpretation', 1)
        clinical = doc.add_paragraph()
        clinical.add_run(f"Patterns suggest {student['name']} is most vulnerable when '{top_ant}' occurs in {top_loc} during {top_session}. ")
        clinical.add_run("Through a trauma-informed lens, this behaviour is a safety strategy. CPI emphasises staying Supportive. ")
        clinical.add_run("Berry Street Model points to strengthening Body and Relationship.")
        
        doc.add_paragraph()
        
        doc.add_heading('Recommendations', 1)
        doc.add_heading('1. Proactive Regulation', 2)
        doc.add_paragraph(f"Provide check-in before '{top_ant}'", style='List Bullet')
        doc.add_paragraph(f"Offer regulated start before {top_session}", style='List Bullet')
        
        doc.add_heading('2. Co-regulation (CPI)', 2)
        doc.add_paragraph("Use CPI Supportive stance, low slow voice", style='List Bullet')
        doc.add_paragraph("Reduce audience, one key adult", style='List Bullet')
        
        doc.add_heading('3. Teaching Skills', 2)
        doc.add_paragraph("Link to Personal & Social Capability", style='List Bullet')
        doc.add_paragraph("Teach help-seeking routines", style='List Bullet')
        
        doc.add_heading('4. SMART Goal', 2)
        doc.add_paragraph("Over 5 weeks, use help-seeking strategy in 4/5 opportunities with support.", style='List Bullet')
        
        footer_para = doc.add_paragraph()
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer_para.add_run('\n\nGenerated by CLC Behaviour Support System\n')
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        footer_para.add_run(datetime.now().strftime('%d %B %Y'))
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except ImportError:
        st.error("python-docx not installed. Run: pip install python-docx")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# HELPER FUNCTIONS
def init_state():
    ss = st.session_state
    if "logged_in" not in ss: ss.logged_in = False
    if "current_user" not in ss: ss.current_user = None
    if "current_page" not in ss: ss.current_page = "login"
    if "students" not in ss: ss.students = MOCK_STUDENTS
    if "staff" not in ss: ss.staff = MOCK_STAFF
    if "incidents" not in ss: ss.incidents = generate_mock_incidents(70)
    if "critical_incidents" not in ss: ss.critical_incidents = []
    if "selected_program" not in ss: ss.selected_program = "JP"
    if "selected_student_id" not in ss: ss.selected_student_id = None
    if "current_incident_id" not in ss: ss.current_incident_id = None
    if "abch_rows" not in ss: ss.abch_rows = []

def login_user(email: str) -> bool:
    email = (email or "").strip().lower()
    if not email: return False
    for staff in st.session_state.staff:
        if staff.get("email", "").lower() == email:
            st.session_state.logged_in = True
            st.session_state.current_user = staff
            st.session_state.current_page = "landing"
            return True
    demo = {"id": "demo", "name": "Demo User", "role": "JP", "email": email}
    st.session_state.logged_in = True
    st.session_state.current_user = demo
    st.session_state.current_page = "landing"
    return True

def go_to(page: str, **kwargs):
    if page not in VALID_PAGES: return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        setattr(st.session_state, k, v)
    st.rerun()

def get_student(student_id: str):
    return next((s for s in st.session_state.students if s["id"] == student_id), None)

def get_session_from_time(t: time) -> str:
    return "Morning" if t.hour < 11 else "Middle" if t.hour < 13 else "Afternoon"

def calculate_age(dob_str: str):
    try:
        d = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    except: return None

def generate_mock_incidents(n: int = 70):
    incidents = []
    weights = {"stu_jp1": 8, "stu_jp2": 5, "stu_jp3": 3, "stu_py1": 10, "stu_py2": 7, "stu_py3": 4, "stu_sy1": 12, "stu_sy2": 9, "stu_sy3": 6}
    pool = []
    for stu in MOCK_STUDENTS:
        pool.extend([stu] * weights.get(stu["id"], 5))
    for _ in range(n):
        stu = random.choice(pool)
        sev = random.choices([1, 2, 3, 4, 5], weights=[20, 35, 25, 15, 5])[0]
        dt = datetime.now() - timedelta(days=random.randint(0, 90))
        dt = dt.replace(hour=random.choices([9,10,11,12,13,14,15], weights=[10,15,12,8,12,18,10])[0], minute=random.randint(0,59), second=0)
        ant = random.choice(ANTECEDENTS)
        beh = random.choice(BEHAVIOUR_TYPES)
        incidents.append({
            "id": str(uuid.uuid4()), "student_id": stu["id"], "student_name": stu["name"],
            "date": dt.date().isoformat(), "time": dt.time().strftime("%H:%M:%S"), "day": dt.strftime("%A"),
            "session": get_session_from_time(dt.time()), "location": random.choice(LOCATIONS),
            "behaviour_type": beh, "antecedent": ant, "support_type": random.choice(SUPPORT_TYPES),
            "intervention": random.choice(INTERVENTIONS), "severity": sev, "reported_by": random.choice(MOCK_STAFF)["name"],
            "additional_staff": [], "description": "Mock incident", "hypothesis": generate_simple_function(ant, beh),
            "is_critical": sev >= 4, "duration_minutes": random.randint(2, 25)
        })
    return incidents

def generate_simple_function(ant: str, beh: str) -> str:
    ant = (ant or "").lower()
    if any(k in ant for k in ["instruction","demand","task"]): return "To avoid request / activity"
    if "transition" in ant: return "To avoid transition"
    if any(k in ant for k in ["denied","access","item"]): return "To get tangible"
    if any(k in ant for k in ["sensory","noise","lights"]): return "To avoid sensory"
    return "To get attention"


# PAGES
def render_login_page():
    st.markdown("## 🔐 Staff Login")
    with st.expander("📧 Demo Emails"):
        for staff in MOCK_STAFF:
            st.code(staff["email"])
    email = st.text_input("Email address", placeholder="emily.jones@example.com")
    if st.button("Login", type="primary"):
        if email:
            login_user(email)
            st.success(f"Logged in as {st.session_state.current_user['name']}")
            st.rerun()

def render_landing_page():
    user = st.session_state.current_user or {}
    st.markdown(f"### 👋 Welcome, **{user.get('name', 'User')}**")
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_page = "login"
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Students", len(st.session_state.students))
    with col2: st.metric("Total Incidents", len(st.session_state.incidents))
    with col3: st.metric("Critical", len([i for i in st.session_state.incidents if i.get("is_critical")]))
    
    st.markdown("---")
    st.markdown("### 📚 Select Program")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Junior Primary")
        if st.button("Enter JP", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="JP")
    with col2:
        st.markdown("#### Primary Years")
        if st.button("Enter PY", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="PY")
    with col3:
        st.markdown("#### Senior Years")
        if st.button("Enter SY", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="SY")

def render_program_students_page():
    program = st.session_state.get("selected_program", "JP")
    st.markdown(f"## {PROGRAM_NAMES.get(program, program)} — Students")
    if st.button("⬅ Back"):
        go_to("landing")
    
    students = [s for s in st.session_state.students if s["program"] == program]
    for stu in students:
        stu_incidents = [i for i in st.session_state.incidents if i["student_id"] == stu["id"]]
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"### {stu['name']}")
                st.caption(f"Grade {stu['grade']}")
            with col2:
                st.metric("Incidents", len(stu_incidents))
            with col3:
                if st.button("📝 Log", key=f"log_{stu['id']}", use_container_width=True):
                    go_to("incident_log", selected_student_id=stu["id"])
                if st.button("📊 Analysis", key=f"ana_{stu['id']}", use_container_width=True):
                    go_to("student_analysis", selected_student_id=stu["id"])

def render_incident_log_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student")
        return
    
    st.markdown(f"## 📝 Quick Incident Log — {student['name']}")
    show_severity_guide()
    
    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input("Date", date.today())
            inc_time = st.time_input("Time", datetime.now().time())
            location = st.selectbox("Location", LOCATIONS)
        with col2:
            behaviour = st.selectbox("Behaviour Type", BEHAVIOUR_TYPES)
            antecedent = st.selectbox("Antecedent", ANTECEDENTS)
            support_type = st.selectbox("Support Type", SUPPORT_TYPES)
        
        intervention = st.selectbox("Intervention", INTERVENTIONS)
        duration = st.number_input("Duration (min)", min_value=1, value=5)
        severity = st.slider("Severity", 1, 5, 2)
        description = st.text_area("Description", placeholder="Factual description...")
        
        submitted = st.form_submit_button("Submit", type="primary")
    
    if submitted:
        new_id = str(uuid.uuid4())
        rec = {
            "id": new_id, "student_id": student_id, "student_name": student["name"],
            "date": inc_date.isoformat(), "time": inc_time.strftime("%H:%M:%S"), "day": inc_date.strftime("%A"),
            "session": get_session_from_time(inc_time), "location": location, "behaviour_type": behaviour,
            "antecedent": antecedent, "support_type": support_type, "intervention": intervention,
            "severity": severity, "reported_by": st.session_state.current_user["name"],
            "duration_minutes": duration, "description": description,
            "hypothesis": generate_simple_function(antecedent, behaviour), "is_critical": severity >= 4
        }
        st.session_state.incidents.append(rec)
        st.success("✅ Incident saved")
        
        if severity >= 4:
            st.warning("⚠️ Severity ≥4 → Critical Incident Form Required")
            st.session_state.current_incident_id = new_id
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Complete Critical Form", type="primary", key="go_crit"):
                    go_to("critical_incident", current_incident_id=new_id)
            with col2:
                if st.button("Skip", key="skip"):
                    go_to("program_students", selected_program=student["program"])
        else:
            if st.button("↩️ Back"):
                go_to("program_students", selected_program=student["program"])

def render_critical_incident_page():
    inc_id = st.session_state.get("current_incident_id")
    quick_inc = next((i for i in st.session_state.incidents if i["id"] == inc_id), None)
    if not quick_inc:
        st.error("No incident found")
        return
    
    st.markdown("## 🚨 Critical Incident ABCH Form")
    
    colA, colB, colC, colH = st.columns(4)
    with colA:
        st.subheader("A – Antecedent")
        A_text = st.text_area("What before?", value=quick_inc.get("antecedent", ""), key="crit_A")
    with colB:
        st.subheader("B – Behaviour")
        B_text = st.text_area("What did?", value=quick_inc.get("behaviour_type", ""), key="crit_B")
    with colC:
        st.subheader("C – Consequence")
        C_text = st.text_area("What after?", value="", key="crit_C")
    with colH:
        st.subheader("H – Hypothesis")
        H_text = st.text_area("Why?", value=generate_simple_function(quick_inc.get("antecedent",""), quick_inc.get("behaviour_type","")), key="crit_H")
    
    st.markdown("### Safety Responses")
    safety_responses = st.multiselect("Actions", ["CPI Supportive stance", "Cleared students", "Moved to safe location", "Additional staff", "Safety plan enacted"])
    
    st.markdown("### Notifications")
    notifications = st.multiselect("Who notified?", ["Parent/carer", "Line manager", "SSS", "DCP", "First Aid", "Injury report"])
    
    st.markdown("### Outcomes")
    removed = st.checkbox("Removed from learning")
    family_contact = st.checkbox("Family contacted")
    
    if st.button("Save Critical Incident", type="primary"):
        record = {
            "id": str(uuid.uuid4()), "created_at": datetime.now().isoformat(), "quick_incident_id": quick_inc["id"],
            "student_id": quick_inc["student_id"], "ABCH_primary": {"A": A_text, "B": B_text, "C": C_text, "H": H_text},
            "safety_responses": safety_responses, "notifications": notifications,
            "outcomes": {"removed": removed, "family_contact": family_contact}
        }
        st.session_state.critical_incidents.append(record)
        st.success("✅ Critical incident saved")
        
        student = get_student(quick_inc["student_id"])
        staff_email = st.session_state.current_user.get("email", "staff@example.com")
        send_critical_incident_email(record, student, staff_email)
        
        st.session_state.abch_rows = []
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Analysis", type="primary"):
                go_to("student_analysis", selected_student_id=quick_inc["student_id"])
        with col2:
            if st.button("↩️ Back"):
                go_to("program_students", selected_program=student["program"])


def render_student_analysis_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student")
        return
    
    st.markdown(f"## 📊 Advanced Analysis — {student['name']}")
    
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]
    
    if not quick and not crit:
        st.info("No data yet")
        return
    
    # Build dataframe
    quick_df = pd.DataFrame(quick) if quick else pd.DataFrame()
    crit_df = pd.DataFrame(crit) if crit else pd.DataFrame()
    
    if not quick_df.empty:
        quick_df["incident_type"] = "Quick"
        quick_df["date_parsed"] = pd.to_datetime(quick_df["date"])
    
    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        crit_df["date_parsed"] = pd.to_datetime(crit_df.get("created_at", datetime.now().isoformat()))
        crit_df["severity"] = 5
        crit_df["antecedent"] = crit_df["ABCH_primary"].apply(lambda d: d.get("A","") if isinstance(d, dict) else "")
        crit_df["behaviour_type"] = crit_df["ABCH_primary"].apply(lambda d: d.get("B","") if isinstance(d, dict) else "")
    
    full_df = pd.concat([quick_df, crit_df], ignore_index=True).sort_values("date_parsed")
    
    # EXECUTIVE SUMMARY
    st.markdown("## 📈 Executive Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total", len(full_df))
    with col2: st.metric("Critical", len(full_df[full_df["incident_type"] == "Critical"]))
    with col3: st.metric("Avg Severity", round(full_df["severity"].mean(), 2))
    with col4:
        days = (full_df["date_parsed"].max() - full_df["date_parsed"].min()).days + 1
        st.metric("Days", days)
    with col5: st.metric("Inc/Day", round(len(full_df) / days, 2))
    
    if len(full_df) >= 2:
        recent = full_df.tail(5)["severity"].mean()
        older = full_df.head(5)["severity"].mean()
        trend = "📈 Increasing" if recent > older else "📉 Decreasing" if recent < older else "➡️ Stable"
        st.info(f"**Trend:** {trend}")
    
    st.markdown("---")
    
    # TIME SERIES
    st.markdown("## ⏰ Time-Series Analysis")
    
    st.markdown("### 📅 Daily Frequency")
    daily = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=daily["date_parsed"], y=daily["count"], mode='lines+markers',
                              line=dict(color='#667eea', width=2), fill='tozeroy', fillcolor='rgba(102,126,234,0.2)'))
    fig1.update_layout(title="Daily Incidents", xaxis_title="Date", yaxis_title="Count", hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("**💡 Interpretation:** Look for patterns (e.g., Monday mornings) to plan preventive supports.")
    
    if len(full_df) >= 7:
        st.markdown("### 📊 7-Day Moving Average")
        full_df["date_only"] = full_df["date_parsed"].dt.date
        daily_full = full_df.groupby("date_only").size().reset_index(name="count")
        daily_full["7d_avg"] = daily_full["count"].rolling(window=7, min_periods=1).mean()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=daily_full["date_only"], y=daily_full["count"], mode='lines', name='Daily', line=dict(color='lightgray')))
        fig2.add_trace(go.Scatter(x=daily_full["date_only"], y=daily_full["7d_avg"], mode='lines', name='7-day avg', line=dict(color='#ef4444', width=3)))
        fig2.update_layout(title="Smoothed Trend")
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("### 🎯 Severity Timeline")
    fig3 = go.Figure()
    quick_only = full_df[full_df["incident_type"] == "Quick"]
    crit_only = full_df[full_df["incident_type"] == "Critical"]
    if not quick_only.empty:
        fig3.add_trace(go.Scatter(x=quick_only["date_parsed"], y=quick_only["severity"], mode='markers',
                                  name='Quick', marker=dict(size=10, color='#3b82f6', opacity=0.6)))
    if not crit_only.empty:
        fig3.add_trace(go.Scatter(x=crit_only["date_parsed"], y=crit_only["severity"], mode='markers',
                                  name='Critical', marker=dict(size=15, color='#ef4444', symbol='star')))
    fig3.update_layout(title="Severity Over Time", yaxis=dict(range=[0, 6]))
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # HEATMAPS
    st.markdown("## 🔥 Heatmaps")
    
    st.markdown("### 🗓️ Day × Hour")
    full_df["hour"] = pd.to_datetime(full_df["time"], format="%H:%M:%S", errors="coerce").dt.hour
    full_df["day_of_week"] = full_df["date_parsed"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = full_df.pivot_table(values="severity", index="day_of_week", columns="hour", aggfunc="count", fill_value=0)
    pivot = pivot.reindex(day_order, fill_value=0)
    fig4 = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale='Reds'))
    fig4.update_layout(title="Incident Frequency by Day & Hour")
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("**💡 Interpretation:** Darker = more incidents. Plan supports for high-risk times.")
    
    st.markdown("### 📍 Location × Session")
    loc_pivot = full_df.pivot_table(values="severity", index="location", columns="session", aggfunc="count", fill_value=0)
    fig5 = go.Figure(data=go.Heatmap(z=loc_pivot.values, x=loc_pivot.columns, y=loc_pivot.index, colorscale='YlOrRd'))
    fig5.update_layout(title="Location Hotspots")
    st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # BEHAVIOUR PATTERNS
    st.markdown("## 🧩 Behaviour Patterns")
    
    st.markdown("### 🔗 Antecedent → Behaviour")
    ant_beh = full_df.groupby(["antecedent", "behaviour_type"]).size().reset_index(name="count").sort_values("count", ascending=False).head(15)
    fig6 = go.Figure(data=[go.Bar(x=ant_beh["count"], y=[f"{r['antecedent'][:30]}→{r['behaviour_type']}" for _,r in ant_beh.iterrows()],
                                  orientation='h', marker=dict(color=ant_beh["count"], colorscale='Viridis'))])
    fig6.update_layout(title="Top 15 Patterns")
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("**💡 Action:** Target the top 3 patterns with specific interventions.")
    
    st.markdown("### 🥧 Behaviour Distribution")
    beh_counts = full_df["behaviour_type"].value_counts()
    fig7 = go.Figure(data=[go.Pie(labels=beh_counts.index, values=beh_counts.values, hole=0.3)])
    fig7.update_layout(title="Behaviour Breakdown")
    st.plotly_chart(fig7, use_container_width=True)
    
    st.markdown("---")
    
    # INTERVENTION EFFECTIVENESS
    st.markdown("## 🎯 Intervention Effectiveness")
    
    st.markdown("### 📊 Which Works Best?")
    interv_sev = full_df.groupby("intervention").agg({"severity": ["mean", "count"]}).reset_index()
    interv_sev.columns = ["intervention", "avg_severity", "count"]
    interv_sev = interv_sev[interv_sev["count"] >= 2].sort_values("avg_severity")
    fig9 = go.Figure()
    fig9.add_trace(go.Bar(x=interv_sev["avg_severity"], y=interv_sev["intervention"], orientation='h',
                          marker=dict(color=interv_sev["avg_severity"], colorscale='RdYlGn', reversescale=True, cmin=1, cmax=5),
                          text=interv_sev["count"], texttemplate='n=%{text}', textposition='outside'))
    fig9.update_layout(title="Average Severity by Intervention (Lower = Better)", xaxis=dict(range=[0, 5.5]))
    st.plotly_chart(fig9, use_container_width=True)
    st.markdown("**💡 Action:** Use interventions with lower severity more often. Train staff on top 3.")
    
    if "duration_minutes" in full_df.columns:
        st.markdown("### ⏱️ Duration Analysis")
        duration_by_type = full_df.groupby("behaviour_type")["duration_minutes"].mean().sort_values(ascending=False).reset_index()
        fig10 = go.Figure()
        fig10.add_trace(go.Bar(x=duration_by_type["duration_minutes"], y=duration_by_type["behaviour_type"], orientation='h',
                               marker=dict(color=duration_by_type["duration_minutes"], colorscale='Reds', showscale=True),
                               text=duration_by_type["duration_minutes"].round(1), texttemplate='%{text} min', textposition='outside'))
        fig10.update_layout(title="Average Duration", height=400)
        st.plotly_chart(fig10, use_container_width=True)
        st.markdown("**💡 What this means:** Longer durations = harder to de-escalate. Focus training on top 2-3.")
    
    st.markdown("---")
    
    # RISK ANALYSIS
    st.markdown("## 🔮 Risk Analysis")
    
    st.markdown("### ⚠️ Escalation Detection")
    full_df["severity_change"] = full_df["severity"].diff()
    escalations = full_df[full_df["severity_change"] > 0]
    col1, col2 = st.columns(2)
    with col1: st.metric("Escalation Events", len(escalations))
    with col2:
        if len(escalations) > 0:
            st.metric("Avg Jump", f"+{escalations['severity_change'].mean():.1f}")
    
    st.markdown("### 🎲 Risk Score")
    recent = full_df.tail(5)
    risk_factors = {
        "Recent frequency": len(full_df.tail(7)) / 7,
        "Recent avg severity": recent["severity"].mean(),
        "Critical rate": (len(full_df[full_df["incident_type"] == "Critical"]) / len(full_df)) * 100,
        "Escalation trend": 1 if len(full_df) >= 2 and full_df.tail(5)["severity"].mean() > full_df.head(5)["severity"].mean() else 0
    }
    risk_score = min(100, int((risk_factors["Recent frequency"] * 10) + (risk_factors["Recent avg severity"] * 8) + 
                              (risk_factors["Critical rate"] * 0.5) + (risk_factors["Escalation trend"] * 20)))
    risk_color = "#10b981" if risk_score < 30 else "#f59e0b" if risk_score < 60 else "#ef4444"
    risk_level = "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### Risk Score: <span style='color:{risk_color}; font-size:2em;'>{risk_score}/100</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"### Level: <span style='color:{risk_color};'>{risk_level}</span>", unsafe_allow_html=True)
    
    st.markdown("""**💡 What to do:**
- **LOW (0-29):** Maintain supports, monitor
- **MODERATE (30-59):** Increase check-ins, review triggers
- **HIGH (60-100):** Urgent team meeting, additional supports""")
    
    with st.expander("Risk Factors"):
        for f, v in risk_factors.items():
            st.metric(f, f"{v:.2f}")
    
    st.markdown("---")
    
    # ABC ANALYSIS
    st.markdown("## 🧠 ABC Analysis")
    
    if "hypothesis" in full_df.columns:
        st.markdown("### 🎯 Function Distribution")
        functions = full_df["hypothesis"].value_counts()
        fig12 = go.Figure(data=[go.Bar(x=functions.values, y=functions.index, orientation='h',
                                       marker=dict(color=['#ef4444','#f59e0b','#10b981','#3b82f6','#8b5cf6'][:len(functions)]))])
        fig12.update_layout(title="Behavioural Functions")
        st.plotly_chart(fig12, use_container_width=True)
        st.info(f"**Primary Function:** {functions.index[0]} ({functions.values[0]} incidents, {(functions.values[0]/len(full_df)*100):.1f}%)")
    
    st.markdown("---")
    
    # CLINICAL INTERPRETATION
    if not full_df.empty:
        top_ant = full_df["antecedent"].mode()[0] if len(full_df["antecedent"]) > 0 else "Unknown"
        top_beh = full_df["behaviour_type"].mode()[0] if len(full_df["behaviour_type"]) > 0 else "Unknown"
        top_loc = full_df["location"].mode()[0] if len(full_df["location"]) > 0 else "Unknown"
        top_session = full_df["session"].mode()[0] if len(full_df["session"]) > 0 else "Unknown"
        
        st.markdown("## 🧠 Clinical Interpretation")
        
        st.markdown("### 1. Summary")
        st.markdown(f"""
- **Primary concern:** **{top_beh}** most frequent
- **Key triggers:** **{top_ant}** regularly precedes dysregulation
- **Hotspot:** **{top_loc}** during **{top_session}**
- **Critical rate:** {(len(full_df[full_df['incident_type']=='Critical'])/len(full_df)*100):.1f}%
        """)
        
        st.markdown("### 2. Trauma-Informed Interpretation")
        st.info(f"""Patterns suggest {student['name']} is most vulnerable when **{top_ant}** occurs in **{top_loc}** during **{top_session}**. 
These moments narrow the window of tolerance. Through a trauma-informed lens, this behaviour is a safety strategy. 
CPI emphasises Supportive stance. Berry Street Model points to strengthening Body and Relationship.""")
        
        st.markdown("### 3. Next Steps")
        st.success(f"""
**1. Proactive regulation:** Check-in before **{top_ant}**, regulated start before **{top_session}**  
**2. Co-regulation (CPI):** Supportive stance, low slow voice, minimal language  
**3. Teaching skills:** Link to Personal & Social Capability, teach help-seeking  
**4. SMART Goal:** Over 5 weeks, use help-seeking in 4/5 opportunities with support
        """)
    
    st.markdown("---")
    
    # DATA EXPORT
    st.markdown("## 📄 Data Export")
    
    col1, col2 = st.columns(2)
    with col1:
        csv = full_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, file_name=f"{student['name']}_incidents.csv", mime="text/csv")
    
    with col2:
        docx_file = generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level)
        if docx_file:
            st.download_button("📄 Behaviour Analysis Plan (Word)", docx_file,
                             file_name=f"Behaviour_Analysis_Plan_{student['name'].replace(' ', '_')}.docx",
                             mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    st.markdown("---")
    if st.button("⬅ Back to Students", type="primary"):
        go_to("program_students", selected_program=student["program"])

def render_program_overview_page():
    st.markdown("## 📈 Cross-Program Analytics")
    if st.button("⬅ Back"): go_to("landing")
    
    incidents = st.session_state.incidents
    if not incidents:
        st.info("No incidents")
        return
    
    df = pd.DataFrame(incidents)
    df["date_parsed"] = pd.to_datetime(df["date"])
    df["program"] = df["student_id"].apply(lambda sid: next((s["program"] for s in st.session_state.students if s["id"] == sid), "Unknown"))
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total", len(df))
    with col2: st.metric("Critical", len(df[df["is_critical"] == True]))
    with col3: st.metric("Avg Severity", round(df["severity"].mean(), 2))
    
    st.markdown("### By Program")
    prog_counts = df["program"].value_counts().reset_index()
    prog_counts.columns = ["Program", "Count"]
    fig1 = px.bar(prog_counts, x="Program", y="Count", color="Program")
    st.plotly_chart(fig1, use_container_width=True)

def main():
    init_state()
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    page = st.session_state.current_page
    if page == "landing": render_landing_page()
    elif page == "program_students": render_program_students_page()
    elif page == "incident_log": render_incident_log_page()
    elif page == "critical_incident": render_critical_incident_page()
    elif page == "student_analysis": render_student_analysis_page()
    elif page == "program_overview": render_program_overview_page()
    else: render_landing_page()

if __name__ == "__main__":
    main()
