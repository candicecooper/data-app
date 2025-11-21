import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, time, timedelta
import uuid
import random
from collections import Counter
from io import BytesIO

st.set_page_config(page_title="CLC Behaviour Support", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# CLEAN MINIMALISTIC PROFESSIONAL STYLING - LIGHT GRAY BACKGROUND
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: #f5f5f5; }
    
    .stButton>button {
        background: #3498db !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important; font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    .stButton>button:hover { background: #2980b9 !important; }
    
    button[kind="primary"] {
        background: #27ae60 !important; color: white !important; font-weight: 700 !important;
    }
    button[kind="primary"]:hover { background: #229954 !important; }
    
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: white !important; border-radius: 12px !important;
        padding: 2rem !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem !important; font-weight: 700 !important; color: #2c3e50 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #000 !important; font-weight: 600 !important; font-size: 0.9rem !important;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        border: 2px solid #cbd5e1 !important; background: white !important;
        color: #000 !important; font-weight: 500 !important; border-radius: 6px !important;
    }
    
    h1, h2, h3 { color: #2c3e50 !important; font-weight: 700 !important; }
    
    label { color: #000 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
    
    .stSuccess { background: #d1fae5 !important; color: #065f46 !important; 
                 border-left: 4px solid #10b981 !important; font-weight: 600 !important; }
    .stInfo { background: #dbeafe !important; color: #1e40af !important; 
              border-left: 4px solid #3b82f6 !important; font-weight: 600 !important; }
    .stWarning { background: #fef3c7 !important; color: #92400e !important; 
                 border-left: 4px solid #f59e0b !important; font-weight: 600 !important; }
    .stError { background: #fee2e2 !important; color: #991b1b !important;
               border-left: 4px solid #ef4444 !important; font-weight: 600 !important; }
    
    .stMarkdown p, .stMarkdown li { color: #000 !important; font-weight: 500 !important; }
    
    .streamlit-expanderHeader {
        background: white !important; color: #000 !important; 
        font-weight: 600 !important; border: 2px solid #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); border-left: 5px solid #3498db;'>
    <h3 style='color: #2c3e50; margin: 0;'>🎭 SANDBOX MODE</h3>
    <p style='color: #000; margin: 0.5rem 0 0 0; font-weight: 600;'>
        This demonstration uses synthetic data only. No real student information is included.
    </p>
</div>
""", unsafe_allow_html=True)

# MOCK DATA
MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP", "email": "emily.jones@example.com", "password": "demo123"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY", "email": "daniel.lee@example.com", "password": "demo123"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY", "email": "sarah.chen@example.com", "password": "demo123"},
    {"id": "s4", "name": "Admin User", "role": "ADM", "email": "admin@example.com", "password": "admin123"},
]

MOCK_STUDENTS = [
    {"id": "stu_jp1", "name": "Emma T.", "grade": "R", "dob": "2018-05-30", "program": "JP"},
    {"id": "stu_jp2", "name": "Oliver S.", "grade": "Y1", "dob": "2017-09-12", "program": "JP"},
    {"id": "stu_jp3", "name": "Sophie M.", "grade": "Y2", "dob": "2016-03-20", "program": "JP"},
    {"id": "stu_py1", "name": "Liam C.", "grade": "Y3", "dob": "2015-06-15", "program": "PY"},
    {"id": "stu_py2", "name": "Ava R.", "grade": "Y4", "dob": "2014-11-08", "program": "PY"},
    {"id": "stu_py3", "name": "Noah B.", "grade": "Y6", "dob": "2012-02-28", "program": "PY"},
    {"id": "stu_sy1", "name": "Isabella G.", "grade": "Y7", "dob": "2011-04-17", "program": "SY"},
    {"id": "stu_sy2", "name": "Ethan D.", "grade": "Y9", "dob": "2009-12-03", "program": "SY"},
    {"id": "stu_sy3", "name": "Mia A.", "grade": "Y11", "dob": "2007-08-20", "program": "SY"},
]

PROGRAM_NAMES = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}
BEHAVIOUR_TYPES = ["Verbal Refusal", "Elopement", "Property Destruction", "Aggression (Peer)", "Aggression (Adult)", "Self-Harm", "Verbal Aggression", "Other"]
ANTECEDENTS = ["Requested to transition", "Given instruction/demand", "Peer conflict", "Staff attention shifted", "Unstructured time", 
               "Sensory overload", "Access denied", "Change in routine", "Difficult task"]
INTERVENTIONS = ["CPI Supportive stance", "Offered break", "Reduced demand", "Provided choices", "Removed audience", 
                "Visual supports", "Co-regulation", "Prompted coping skill", "Redirection"]
LOCATIONS = ["JP Classroom", "PY Classroom", "SY Classroom", "Playground", "Library", "Admin", "Gate", "Toilets"]
VALID_PAGES = ["login", "landing", "program_students", "incident_log", "critical_incident", "student_analysis"]

def show_severity_guide():
    """PROFESSIONAL SEVERITY GUIDE - GREEN/ORANGE/RED ONLY"""
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1);'>
        <h4 style='color: #2c3e50; margin-bottom: 1rem; font-weight: 700;'>📊 Severity Level Guide</h4>
        <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.5rem;'>
            <div style='background: #d1fae5; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #27ae60;'>
                <div style='color: #065f46; font-weight: 700; margin-bottom: 0.3rem;'>1 - Low</div>
                <div style='color: #065f46; font-size: 0.8rem;'>Persistent minor behaviours</div>
            </div>
            <div style='background: #dbeafe; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #3498db;'>
                <div style='color: #1e40af; font-weight: 700; margin-bottom: 0.3rem;'>2 - Disruptive</div>
                <div style='color: #1e40af; font-size: 0.8rem;'>Impacts others' learning</div>
            </div>
            <div style='background: #fef3c7; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #f39c12;'>
                <div style='color: #92400e; font-weight: 700; margin-bottom: 0.3rem;'>3 - Concerning</div>
                <div style='color: #92400e; font-size: 0.8rem;'>Verbal aggression, elopement</div>
            </div>
            <div style='background: #fed7aa; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #f39c12;'>
                <div style='color: #7c2d12; font-weight: 700; margin-bottom: 0.3rem;'>4 - Serious</div>
                <div style='color: #7c2d12; font-size: 0.8rem;'>Physical aggression</div>
            </div>
            <div style='background: #fee2e2; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #e74c3c;'>
                <div style='color: #991b1b; font-weight: 700; margin-bottom: 0.3rem;'>5 - Critical</div>
                <div style='color: #991b1b; font-size: 0.8rem;'>Severe violence, injury</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def send_critical_incident_email(incident_data, student, staff_email, manager_email="manager@clc.sa.edu.au"):
    st.info(f"""📧 **Email Notification Sent**
    
**To:** {manager_email}, {staff_email}  
**Subject:** CRITICAL INCIDENT - {student['name']}

**Student:** {student['name']} ({student['program']} - Grade {student['grade']})  
**Behaviour:** {incident_data.get('ABCH_primary', {}).get('B', 'N/A')}  
**Safety Responses:** {', '.join(incident_data.get('safety_responses', []))}

*(In production, this sends via SMTP)*
    """)

def generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level):
    """Generate Word doc WITH embedded graphs using kaleido"""
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import plotly.graph_objects as go
        
        doc = Document()
        
        title = doc.add_heading('Behaviour Analysis Plan', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Student Information', 1)
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Light Grid Accent 1'
        info_table.rows[0].cells[0].text = 'Student:'
        info_table.rows[0].cells[1].text = student['name']
        info_table.rows[1].cells[0].text = 'Program:'
        info_table.rows[1].cells[1].text = student['program']
        info_table.rows[2].cells[0].text = 'Grade:'
        info_table.rows[2].cells[1].text = student['grade']
        info_table.rows[3].cells[0].text = 'Date:'
        info_table.rows[3].cells[1].text = datetime.now().strftime('%d/%m/%Y')
        
        doc.add_paragraph()
        
        doc.add_heading('Executive Summary', 1)
        summary = doc.add_paragraph()
        summary.add_run('Total Incidents: ').bold = True
        summary.add_run(f"{len(full_df)}\n")
        summary.add_run('Critical Incidents: ').bold = True
        summary.add_run(f"{len(full_df[full_df['incident_type'] == 'Critical'])}\n")
        summary.add_run('Average Severity: ').bold = True
        summary.add_run(f"{full_df['severity'].mean():.2f}\n")
        summary.add_run('Risk Level: ').bold = True
        summary.add_run(f"{risk_level} ({risk_score}/100)")
        
        doc.add_paragraph()
        
        doc.add_heading('Key Findings', 1)
        findings = doc.add_paragraph()
        findings.add_run('Primary Behaviour: ').bold = True
        findings.add_run(f"{top_beh}\n\n")
        findings.add_run('Most Common Trigger: ').bold = True
        findings.add_run(f"{top_ant}\n\n")
        findings.add_run('Hotspot Location: ').bold = True
        findings.add_run(f"{top_loc} during {top_session}")
        
        doc.add_paragraph()
        
        doc.add_heading('Clinical Interpretation', 1)
        interp = doc.add_paragraph()
        interp.add_run(f"Data indicates {student['name']} is most vulnerable when '{top_ant}' occurs in {top_loc} during {top_session}. ")
        interp.add_run("This behaviour serves as a safety strategy. CPI principles emphasize Supportive stance. ")
        interp.add_run("Berry Street Model suggests strengthening Body (regulation) and Relationship (connection).")
        
        doc.add_paragraph()
        
        doc.add_heading('Recommendations', 1)
        doc.add_heading('1. Proactive Strategies', 2)
        doc.add_paragraph(f"Provide check-in before '{top_ant}'", style='List Bullet')
        doc.add_paragraph(f"Offer regulated start before {top_session}", style='List Bullet')
        
        doc.add_heading('2. Co-regulation (CPI)', 2)
        doc.add_paragraph("Use Supportive stance, low slow voice", style='List Bullet')
        doc.add_paragraph("Reduce audience, one key adult", style='List Bullet')
        
        doc.add_heading('3. Teaching Skills', 2)
        doc.add_paragraph("Link to Personal & Social Capability", style='List Bullet')
        doc.add_paragraph("Teach help-seeking routines", style='List Bullet')
        
        doc.add_heading('4. SMART Goal', 2)
        doc.add_paragraph("Over 5 weeks, use help-seeking strategy in 4/5 opportunities with support.", style='List Bullet')
        
        # ADD GRAPHS TO DOCUMENT
        doc.add_page_break()
        doc.add_heading('Behaviour Analytics', 1)
        
        try:
            # Graph 1: Behavior Frequency
            beh_counts = full_df["behaviour_type"].value_counts().head(5)
            fig1 = go.Figure(data=[
                go.Bar(x=beh_counts.values, y=beh_counts.index, orientation='h',
                       marker_color='#3498db')
            ])
            fig1.update_layout(
                title="Top Behaviors",
                xaxis_title="Frequency",
                yaxis_title="Behavior",
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                font=dict(size=12)
            )
            img_bytes1 = fig1.to_image(format="png", width=1000, height=600)
            img_stream1 = BytesIO(img_bytes1)
            doc.add_picture(img_stream1, width=Inches(6))
            doc.add_paragraph()
            
            # Graph 2: Severity Trend
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=full_df["date_parsed"], 
                y=full_df["severity"],
                mode='lines+markers',
                line=dict(color='#e74c3c', width=2),
                marker=dict(size=8, color='#e74c3c')
            ))
            fig2.update_layout(
                title="Severity Trend Over Time",
                xaxis_title="Date",
                yaxis_title="Severity Level",
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=400,
                font=dict(size=12)
            )
            img_bytes2 = fig2.to_image(format="png", width=1000, height=600)
            img_stream2 = BytesIO(img_bytes2)
            doc.add_picture(img_stream2, width=Inches(6))
            
        except Exception as e:
            doc.add_paragraph(f"Note: Unable to generate graphs. Error: {str(e)}")
        
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.add_run('\n\nGenerated by CLC Behaviour Support\n')
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        footer.add_run(datetime.now().strftime('%d %B %Y'))
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"Error generating document: {e}")
        return None

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

def login_user(email: str, password: str) -> bool:
    email = (email or "").strip().lower()
    password = (password or "").strip()
    if not email or not password: return False
    for staff in st.session_state.staff:
        if staff.get("email", "").lower() == email and staff.get("password", "") == password:
            st.session_state.logged_in = True
            st.session_state.current_user = staff
            st.session_state.current_page = "landing"
            return True
    return False

def go_to(page: str, **kwargs):
    if page not in VALID_PAGES: return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        setattr(st.session_state, k, v)
    st.rerun()

def get_student(sid): return next((s for s in st.session_state.students if s["id"] == sid), None)
def get_session_from_time(t): return "Morning" if t.hour < 11 else "Middle" if t.hour < 13 else "Afternoon"

def generate_mock_incidents(n=70):
    incidents = []
    weights = {"stu_jp1": 8, "stu_jp2": 5, "stu_jp3": 3, "stu_py1": 10, "stu_py2": 7, "stu_py3": 4, 
               "stu_sy1": 12, "stu_sy2": 9, "stu_sy3": 6}
    pool = []
    for stu in MOCK_STUDENTS:
        pool.extend([stu] * weights.get(stu["id"], 5))
    for _ in range(n):
        stu = random.choice(pool)
        sev = random.choices([1, 2, 3, 4, 5], weights=[20, 35, 25, 15, 5])[0]
        dt = datetime.now() - timedelta(days=random.randint(0, 90))
        dt = dt.replace(hour=random.choices([9,10,11,12,13,14,15], weights=[10,15,12,8,12,18,10])[0], 
                       minute=random.randint(0,59), second=0)
        incidents.append({
            "id": str(uuid.uuid4()), "student_id": stu["id"], "student_name": stu["name"],
            "date": dt.date().isoformat(), "time": dt.time().strftime("%H:%M:%S"),
            "day": dt.strftime("%A"), "session": get_session_from_time(dt.time()),
            "location": random.choice(LOCATIONS), "behaviour_type": random.choice(BEHAVIOUR_TYPES),
            "antecedent": random.choice(ANTECEDENTS), "intervention": random.choice(INTERVENTIONS),
            "severity": sev, "reported_by": random.choice(MOCK_STAFF)["name"],
            "description": "Mock incident", "is_critical": sev >= 4, "duration_minutes": random.randint(2, 25)
        })
    return incidents


# PAGES
def render_login_page():
    st.markdown("## 🔐 Staff Login")
    
    with st.container(border=True):
        st.markdown("### Demo Credentials")
        st.markdown("""
        **Email:** emily.jones@example.com  
        **Password:** demo123
        
        **Admin:** admin@example.com  
        **Password:** admin123
        """)
    
    email = st.text_input("Email", placeholder="your.email@example.com", value="", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Enter password", value="", key="login_pass")
    
    if st.button("Login", type="primary", use_container_width=True):
        if login_user(email, password):
            st.success(f"Welcome {st.session_state.current_user['name']}!")
            st.rerun()
        else:
            st.error("Invalid email or password")

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
    st.markdown(f"## {PROGRAM_NAMES.get(program)} — Students")
    if st.button("⬅ Back to Landing"):
        go_to("landing")
    
    students = [s for s in st.session_state.students if s["program"] == program]
    for stu in students:
        stu_incidents = [i for i in st.session_state.incidents if i["student_id"] == stu["id"]]
        critical = [i for i in stu_incidents if i.get("is_critical")]
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"### {stu['name']}")
                st.caption(f"Grade {stu['grade']}")
            with col2:
                st.metric("Incidents", len(stu_incidents))
                st.caption(f"Critical: {len(critical)}")
            with col3:
                if st.button("📝 Log Incident", key=f"log_{stu['id']}", use_container_width=True):
                    go_to("incident_log", selected_student_id=stu["id"])
                if st.button("📊 Analysis", key=f"ana_{stu['id']}", use_container_width=True):
                    go_to("student_analysis", selected_student_id=stu["id"])

def render_incident_log_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected")
        if st.button("Back"): go_to("landing")
        return
    
    st.markdown(f"## 📝 Incident Log — {student['name']}")
    show_severity_guide()
    
    # ALL FIELDS START EMPTY - NO PREFILLED VALUES
    with st.form("incident_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input("Date", value=None, key="inc_date")
            inc_time = st.time_input("Time", value=None, key="inc_time")
            location = st.selectbox("Location", [""] + LOCATIONS, key="inc_loc")
        with col2:
            behaviour = st.selectbox("Behaviour", [""] + BEHAVIOUR_TYPES, key="inc_beh")
            antecedent = st.selectbox("Trigger", [""] + ANTECEDENTS, key="inc_ant")
            intervention = st.selectbox("Intervention", [""] + INTERVENTIONS, key="inc_int")
        
        duration = st.number_input("Duration (minutes)", min_value=0, value=0, key="inc_dur")
        severity = st.slider("Severity (see guide above)", 0, 5, 0, key="inc_sev")
        description = st.text_area("Description", placeholder="Brief factual description...", value="", key="inc_desc")
        
        submitted = st.form_submit_button("Submit Incident", type="primary")
    
    if submitted:
        # Validate required fields
        if not inc_date or not inc_time or not location or not behaviour or not antecedent or not intervention or severity == 0:
            st.error("⚠️ Please fill in all required fields")
            return
            
        new_id = str(uuid.uuid4())
        rec = {
            "id": new_id, "student_id": student_id, "student_name": student["name"],
            "date": inc_date.isoformat(), "time": inc_time.strftime("%H:%M:%S"),
            "day": inc_date.strftime("%A"), "session": get_session_from_time(inc_time),
            "location": location, "behaviour_type": behaviour, "antecedent": antecedent,
            "intervention": intervention, "severity": severity,
            "reported_by": st.session_state.current_user["name"],
            "duration_minutes": duration, "description": description, "is_critical": severity >= 4
        }
        st.session_state.incidents.append(rec)
        st.success("✅ Incident saved successfully")
        
        # CRITICAL INCIDENT FORM ACTIVATION
        if severity >= 4:
            st.warning("⚠️ **Severity Level 4 or 5 Detected**")
            st.info("A Critical Incident ABCH Form is required for this incident.")
            
            st.session_state.current_incident_id = new_id
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Complete Critical Form Now", type="primary", key="crit_now", use_container_width=True):
                    go_to("critical_incident", current_incident_id=new_id)
            with col2:
                if st.button("Complete Later", key="crit_later", use_container_width=True):
                    go_to("program_students", selected_program=student["program"])
        else:
            if st.button("↩️ Back to Students"):
                go_to("program_students", selected_program=student["program"])

def render_critical_incident_page():
    """CRITICAL INCIDENT ABCH FORM - THIS IS THE CHRONOLOGY STRUCTURE"""
    inc_id = st.session_state.get("current_incident_id")
    quick_inc = next((i for i in st.session_state.incidents if i["id"] == inc_id), None)
    
    if not quick_inc:
        st.error("No incident found")
        if st.button("Back"): go_to("landing")
        return
    
    student = get_student(quick_inc["student_id"])
    st.markdown(f"## 🚨 Critical Incident ABCH Form")
    st.markdown(f"**Student:** {student['name']} | **Date:** {quick_inc['date']}")
    
    st.markdown("---")
    st.markdown("### ⏱️ ABCH Analysis (Chronology Structure)")
    st.info("📌 Document the incident chronologically using the ABCH framework")
    
    # ABCH COLUMNS - THIS IS THE CHRONOLOGY STRUCTURE YOU WANTED
    colA, colB, colC, colH = st.columns(4)
    with colA:
        st.markdown("**A – Antecedent**")
        st.caption("What happened BEFORE?")
        A_text = st.text_area("Antecedent details", value="", key="A", height=150, 
                             placeholder="Describe what was happening before the behavior...")
    with colB:
        st.markdown("**B – Behaviour**")
        st.caption("What did student DO?")
        B_text = st.text_area("Behavior description", value="", key="B", height=150,
                             placeholder="Describe the specific behavior observed...")
    with colC:
        st.markdown("**C – Consequence**")
        st.caption("What happened AFTER?")
        C_text = st.text_area("Consequence details", value="", key="C", height=150,
                             placeholder="Describe what happened immediately after...")
    with colH:
        st.markdown("**H – Hypothesis**")
        st.caption("WHY did this occur?")
        H_text = st.text_area("Function/hypothesis", value="", key="H", height=150,
                             placeholder="What was the function of this behavior?")
    
    st.markdown("---")
    st.markdown("### Safety Responses")
    safety = st.multiselect("Actions taken (CPI-aligned)",
        ["CPI Supportive stance", "Cleared area", "Moved to safe location", "Additional staff", "Safety plan enacted"],
        default=[])
    
    st.markdown("### Notifications")
    notifications = st.multiselect("Who was notified?",
        ["Parent/carer", "Line manager", "SSS", "First Aid", "DCP", "Other"],
        default=[])
    
    st.markdown("---")
    
    if st.button("Save Critical Incident", type="primary", use_container_width=True):
        if not A_text or not B_text or not C_text or not H_text:
            st.error("⚠️ Please complete all ABCH fields")
            return
            
        record = {
            "id": str(uuid.uuid4()), "created_at": datetime.now().isoformat(),
            "quick_incident_id": inc_id, "student_id": quick_inc["student_id"],
            "ABCH_primary": {"A": A_text, "B": B_text, "C": C_text, "H": H_text},
            "safety_responses": safety, "notifications": notifications
        }
        st.session_state.critical_incidents.append(record)
        st.success("✅ Critical incident form saved")
        
        # Send email notification
        staff_email = st.session_state.current_user.get("email", "staff@example.com")
        send_critical_incident_email(record, student, staff_email)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Analysis", type="primary", use_container_width=True):
                go_to("student_analysis", selected_student_id=quick_inc["student_id"])
        with col2:
            if st.button("↩️ Back to Students", use_container_width=True):
                go_to("program_students", selected_program=student["program"])


def render_student_analysis_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected")
        if st.button("Back"): go_to("landing")
        return
    
    st.markdown(f"## 📊 Data Analysis — {student['name']}")
    
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]
    
    if not quick and not crit:
        st.info("No incident data available yet for this student.")
        if st.button("↩️ Back"): go_to("program_students", selected_program=student["program"])
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
    
    # SUMMARY METRICS
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Incidents", len(full_df))
    with col2: st.metric("Critical", len(full_df[full_df["incident_type"] == "Critical"]))
    with col3: st.metric("Avg Severity", f"{full_df['severity'].mean():.1f}")
    with col4: st.metric("Last 7 days", len(full_df[full_df["date_parsed"] >= (datetime.now() - timedelta(days=7))]))
    
    st.markdown("---")
    
    # GRAPH 1: BEHAVIOR FREQUENCY - PROFESSIONAL BLUE
    st.markdown("### 📊 Behavior Types")
    beh_counts = full_df["behaviour_type"].value_counts().head(5)
    fig1 = go.Figure(data=[
        go.Bar(x=beh_counts.values, y=beh_counts.index, orientation='h',
               marker_color='#3498db', text=beh_counts.values, textposition='auto')
    ])
    fig1.update_layout(
        height=300, showlegend=False,
        xaxis_title="Frequency", yaxis_title="Behavior",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#000', size=12, family='Inter')
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    with st.expander("💡 What this means"):
        st.markdown(f"""
        **Most Common:** {beh_counts.index[0]} ({beh_counts.values[0]} incidents)  
        **Action:** This is the primary behavior requiring support.
        """)
    
    st.markdown("---")
    
    # GRAPH 2: TIME OF DAY
    st.markdown("### 🕐 Time of Day Distribution")
    if "session" in full_df.columns:
        session_counts = full_df["session"].value_counts()
        fig2 = go.Figure(data=[
            go.Bar(x=session_counts.index, y=session_counts.values,
                   marker_color='#3498db', text=session_counts.values, textposition='auto')
        ])
        fig2.update_layout(
            height=300, showlegend=False,
            xaxis_title="Session", yaxis_title="Frequency",
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(color='#000', size=12, family='Inter')
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("💡 What this means"):
            top_session = session_counts.index[0]
            st.markdown(f"""
            **High-risk time:** {top_session}  
            **Action:** Provide extra support during {top_session} sessions.
            """)
    
    st.markdown("---")
    
    # GRAPH 3: ANTECEDENTS (TRIGGERS)
    st.markdown("### 🎯 Common Triggers")
    ant_counts = full_df["antecedent"].value_counts().head(5)
    fig3 = go.Figure(data=[
        go.Bar(x=ant_counts.values, y=ant_counts.index, orientation='h',
               marker_color='#3498db', text=ant_counts.values, textposition='auto')
    ])
    fig3.update_layout(
        height=300, showlegend=False,
        xaxis_title="Frequency", yaxis_title="Trigger",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#000', size=12, family='Inter')
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    with st.expander("💡 What this means"):
        st.markdown(f"""
        **Key Trigger:** {ant_counts.index[0]} precedes incidents most often  
        **Action:** Plan proactive supports before this trigger occurs.
        """)
    
    st.markdown("---")
    
    # GRAPH 4: SEVERITY OVER TIME - PROFESSIONAL COLORS
    st.markdown("### 📈 Severity Trends")
    fig4 = go.Figure()
    
    # Create color mapping for severity - PROFESSIONAL COLORS ONLY
    severity_colors = full_df["severity"].map({
        1: '#27ae60',  # Green
        2: '#3498db',  # Blue
        3: '#f39c12',  # Orange
        4: '#f39c12',  # Orange
        5: '#e74c3c'   # Red
    })
    
    fig4.add_trace(go.Scatter(
        x=full_df["date_parsed"], y=full_df["severity"],
        mode='markers', 
        marker=dict(size=10, color=severity_colors, opacity=0.7),
        name='Severity'
    ))
    
    # Add trend line
    if len(full_df) >= 2:
        z = np.polyfit(range(len(full_df)), full_df["severity"], 1)
        p = np.poly1d(z)
        fig4.add_trace(go.Scatter(
            x=full_df["date_parsed"], y=p(range(len(full_df))),
            mode='lines', line=dict(color='#e74c3c', width=2, dash='dash'),
            name='Trend'
        ))
    fig4.update_layout(
        height=300, yaxis=dict(range=[0, 6]),
        xaxis_title="Date", yaxis_title="Severity",
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(color='#000', size=12, family='Inter')
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    trend_dir = "increasing" if len(full_df) >= 2 and full_df.tail(5)["severity"].mean() > full_df.head(5)["severity"].mean() else "decreasing"
    
    with st.expander("💡 What this means"):
        st.markdown(f"""
        **Trend:** Severity appears to be **{trend_dir}** over time  
        **Action:** {"Review current strategies if increasing" if trend_dir == "increasing" else "Continue current approach if decreasing"}
        """)
    
    st.markdown("---")
    
    # RISK SCORE - PROFESSIONAL COLORS
    st.markdown("### 🎲 Current Risk Assessment")
    
    recent = full_df.tail(7)
    risk_score = min(100, int(
        (len(recent) / 7 * 10) +
        (recent["severity"].mean() * 8) +
        (len(full_df[full_df["incident_type"] == "Critical"]) / len(full_df) * 50 if len(full_df) > 0 else 0)
    ))
    
    risk_level = "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH"
    risk_color = "#27ae60" if risk_score < 30 else "#f39c12" if risk_score < 60 else "#e74c3c"
    
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 2rem; border-radius: 12px; text-align: center; border: 3px solid {risk_color};'>
            <div style='font-size: 3rem; font-weight: 700; color: {risk_color};'>{risk_score}</div>
            <div style='font-size: 1.2rem; font-weight: 600; color: #000;'>Risk Score</div>
            <div style='font-size: 1rem; font-weight: 700; color: {risk_color}; margin-top: 0.5rem;'>{risk_level} RISK</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        **Risk Levels:**
        - **LOW (0-29):** Maintain current supports, monitor weekly
        - **MODERATE (30-59):** Increase check-ins, review triggers, consider additional supports
        - **HIGH (60-100):** Urgent team meeting, implement intensive supports immediately
        """)
    
    st.markdown("---")
    
    # CLINICAL SUMMARY
    st.markdown("### 🧠 Clinical Summary")
    
    top_beh = full_df["behaviour_type"].mode()[0] if len(full_df) > 0 else "Unknown"
    top_ant = full_df["antecedent"].mode()[0] if len(full_df) > 0 else "Unknown"
    top_loc = full_df["location"].mode()[0] if len(full_df) > 0 and "location" in full_df.columns else "Unknown"
    top_session = full_df["session"].mode()[0] if len(full_df) > 0 and "session" in full_df.columns else "Unknown"
    
    st.info(f"""
    **Key Patterns:**
    - Primary behaviour: **{top_beh}**
    - Main trigger: **{top_ant}**
    - Hotspot location: **{top_loc}**
    - Highest risk time: **{top_session}**
    
    **Interpretation:** {student['name']} is most vulnerable when "{top_ant}" occurs in {top_loc} during {top_session}. 
    This behaviour serves as a safety strategy. Use CPI Supportive stance and co-regulation strategies.
    """)
    
    st.success(f"""
    **Recommended Actions:**
    1. **Proactive:** Check-in before "{top_ant}", regulated start before {top_session}
    2. **In-the-moment:** CPI Supportive stance, low voice, reduce audience
    3. **Teaching:** Link to Personal & Social Capability, teach help-seeking
    4. **SMART Goal:** Over 5 weeks, use help-seeking in 4/5 opportunities with support
    """)
    
    st.markdown("---")
    
    # DATA EXPORT
    st.markdown("### 📄 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = full_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Data",
            data=csv,
            file_name=f"{student['name']}_incidents.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        docx_file = generate_behaviour_analysis_plan_docx(
            student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level
        )
        if docx_file:
            st.download_button(
                label="📄 Behaviour Analysis Plan (with Graphs)",
                data=docx_file,
                file_name=f"BAP_{student['name'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        else:
            st.error("Could not generate Word document. Ensure python-docx is installed.")
    
    st.markdown("---")
    
    if st.button("⬅ Back to Students", type="primary"):
        go_to("program_students", selected_program=student["program"])

def main():
    init_state()
    
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    page = st.session_state.current_page
    
    if page == "landing":
        render_landing_page()
    elif page == "program_students":
        render_program_students_page()
    elif page == "incident_log":
        render_incident_log_page()
    elif page == "critical_incident":
        render_critical_incident_page()
    elif page == "student_analysis":
        render_student_analysis_page()
    else:
        render_landing_page()

if __name__ == "__main__":
    main()
