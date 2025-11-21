import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, time, timedelta
import uuid
import random
from collections import Counter
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================
# CONFIG + CONSTANTS
# =========================================

st.set_page_config(
    page_title="CLC Behaviour Support",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================
# BEAUTIFUL STYLING WITH HIGH CONTRAST
# =========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* HIGH CONTRAST BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.7) !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%) !important;
        color: #000 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0, 201, 255, 0.5) !important;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(0, 201, 255, 0.7) !important;
    }
    
    /* WHITE CONTAINERS WITH HIGH CONTRAST */
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: white !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* METRICS - BOLD AND COLORFUL */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #333 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* INPUT FIELDS - HIGH CONTRAST */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input,
    .stNumberInput>div>div>input,
    .stMultiSelect>div>div>div {
        border-radius: 10px !important;
        border: 2px solid #667eea !important;
        background: white !important;
        color: #000 !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #00c9ff !important;
        box-shadow: 0 0 0 3px rgba(0, 201, 255, 0.2) !important;
    }
    
    /* HEADERS - WHITE WITH SHADOW FOR CONTRAST */
    h1 {
        color: white !important;
        font-weight: 800 !important;
        font-size: 3rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
    }
    
    h2 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
    }
    
    h3 {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* LABELS - DARK TEXT ON WHITE BACKGROUNDS */
    label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* DOWNLOAD BUTTONS - BRIGHT GREEN */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.5) !important;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.7) !important;
    }
    
    /* INFO/SUCCESS BOXES - HIGH CONTRAST */
    .stSuccess {
        background: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
        color: #065f46 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    .stInfo {
        background: #dbeafe !important;
        border-left: 4px solid #3b82f6 !important;
        color: #1e40af !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    .stWarning {
        background: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
        color: #92400e !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    .stError {
        background: #fee2e2 !important;
        border-left: 4px solid #ef4444 !important;
        color: #991b1b !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        border: 2px solid #667eea !important;
    }
    
    /* SLIDER */
    .stSlider > div > div > div > div {
        background: #667eea !important;
    }
    
    /* CHECKBOX/RADIO */
    .stCheckbox > label > div {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* CAPTIONS - READABLE */
    .stCaption {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
    }
    
    /* MARKDOWN IN CONTAINERS */
    .stMarkdown p {
        color: #1a1a1a !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sleek banner
st.markdown("""
<div style='background: white; 
            padding: 1.5rem; 
            border-radius: 15px; 
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            border-left: 6px solid #667eea;'>
    <h2 style='color: #667eea; margin: 0; font-size: 1.4rem; text-shadow: none;'>
        🎭 SANDBOX DEMONSTRATION MODE
    </h2>
    <p style='color: #333; margin: 0.5rem 0 0 0; font-weight: 500;'>
        This version uses synthetic data only. No real student information is included.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================
# SEVERITY GUIDE VISUAL
# =========================================

def show_severity_guide():
    """Display clear severity level guide"""
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 8px 25px rgba(0,0,0,0.1);'>
        <h3 style='color: #667eea; text-shadow: none; margin-bottom: 1rem;'>📊 Severity Level Guide</h3>
        
        <div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;'>
            <div style='background: #d1fae5; padding: 1rem; border-radius: 10px; border-left: 4px solid #10b981;'>
                <h4 style='color: #065f46; text-shadow: none; margin: 0;'>1 - Low Level</h4>
                <p style='color: #065f46; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Persistent minor behaviours (talking out, off-task, minor refusal)
                </p>
            </div>
            
            <div style='background: #dbeafe; padding: 1rem; border-radius: 10px; border-left: 4px solid #3b82f6;'>
                <h4 style='color: #1e40af; text-shadow: none; margin: 0;'>2 - Disruptive</h4>
                <p style='color: #1e40af; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Impacts others' learning (loud disruption, leaving area, property misuse)
                </p>
            </div>
            
            <div style='background: #fef3c7; padding: 1rem; border-radius: 10px; border-left: 4px solid #f59e0b;'>
                <h4 style='color: #92400e; text-shadow: none; margin: 0;'>3 - Concerning</h4>
                <p style='color: #92400e; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Escalated behaviour (verbal aggression, elopement, throwing objects)
                </p>
            </div>
            
            <div style='background: #fed7aa; padding: 1rem; border-radius: 10px; border-left: 4px solid #ea580c;'>
                <h4 style='color: #7c2d12; text-shadow: none; margin: 0;'>4 - Serious</h4>
                <p style='color: #7c2d12; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Physical aggression towards others or property destruction
                </p>
            </div>
            
            <div style='background: #fee2e2; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc2626;'>
                <h4 style='color: #991b1b; text-shadow: none; margin: 0;'>5 - Critical</h4>
                <p style='color: #991b1b; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Severe violence, injury caused, or significant safety risk
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================
# EMAIL NOTIFICATION SYSTEM
# =========================================

def send_critical_incident_email(incident_data, student, staff_email, manager_email="manager@example.com"):
    """Send email notification for critical incidents"""
    try:
        # FOR SANDBOX: Just show what would be sent
        st.info(f"""
        📧 **Email Notification Triggered**
        
        **To:** {manager_email}, {staff_email}
        **Subject:** CRITICAL INCIDENT ALERT - {student['name']}
        
        **Details:**
        - Student: {student['name']} ({student['program']} - Grade {student['grade']})
        - Date/Time: {incident_data.get('created_at', 'N/A')}
        - Primary Behaviour: {incident_data.get('ABCH_primary', {}).get('B', 'N/A')}
        - Antecedent: {incident_data.get('ABCH_primary', {}).get('A', 'N/A')}
        - Safety Responses: {', '.join(incident_data.get('safety_responses', []))}
        - Notifications Made: {', '.join(incident_data.get('notifications', []))}
        
        **Action Required:** Review incident details and follow up with staff and family as needed.
        
        *(In production, this would send actual emails via SMTP)*
        """)
        
        # PRODUCTION CODE (commented out for sandbox):
        # msg = MIMEMultipart()
        # msg['From'] = "noreply@clc.sa.edu.au"
        # msg['To'] = f"{manager_email}, {staff_email}"
        # msg['Subject'] = f"CRITICAL INCIDENT ALERT - {student['name']}"
        # 
        # body = f"""
        # CRITICAL INCIDENT REPORT
        # 
        # Student: {student['name']} ({student['program']} - Grade {student['grade']})
        # Date/Time: {incident_data.get('created_at')}
        # 
        # PRIMARY BEHAVIOUR:
        # {incident_data.get('ABCH_primary', {}).get('B', 'N/A')}
        # 
        # ANTECEDENT (What happened before):
        # {incident_data.get('ABCH_primary', {}).get('A', 'N/A')}
        # 
        # CONSEQUENCE (What happened after):
        # {incident_data.get('ABCH_primary', {}).get('C', 'N/A')}
        # 
        # SAFETY RESPONSES:
        # {', '.join(incident_data.get('safety_responses', []))}
        # 
        # NOTIFICATIONS MADE:
        # {', '.join(incident_data.get('notifications', []))}
        # 
        # Please review full incident details in the system and follow up as required.
        # """
        # 
        # msg.attach(MIMEText(body, 'plain'))
        # 
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login("your_email@gmail.com", "your_password")
        # server.send_message(msg)
        # server.quit()
        
        return True
    except Exception as e:
        st.error(f"Email notification failed: {e}")
        return False

# =========================================
# DATA & CONSTANTS
# =========================================

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

BEHAVIOUR_TYPES = [
    "Verbal Refusal", "Elopement", "Property Destruction", 
    "Aggression (Peer)", "Aggression (Adult)", "Self-Harm", 
    "Verbal Aggression", "Other"
]

ANTECEDENTS = [
    "Requested to transition activity",
    "Given instruction / demand (Academic)",
    "Peer conflict / teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory overload (noise / lights)",
    "Access to preferred item denied",
    "Change in routine or expectation",
    "Difficult task presented",
]

INTERVENTIONS = [
    "Used calm tone and supportive stance (CPI)",
    "Offered a break / time away",
    "Reduced task demand / chunked task",
    "Provided choices",
    "Removed audience / peers",
    "Used visual supports",
    "Co-regulated with breathing / grounding",
    "Prompted use of coping skill",
    "Redirection to preferred activity",
]

LOCATIONS = [
    "JP Classroom", "JP Spill Out", "PY Classroom", "PY Spill Out",
    "SY Classroom", "SY Spill Out", "Student Kitchen", "Admin",
    "Gate", "Library", "Playground", "Yard", "Toilets", "Excursion", "Swimming"
]

VALID_PAGES = [
    "login", "landing", "program_students", "incident_log",
    "critical_incident", "student_analysis", "program_overview"
]
