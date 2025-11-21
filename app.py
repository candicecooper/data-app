import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date, time, timedelta
import uuid
import random

# =========================================
# CONFIG + CONSTANTS
# =========================================

st.set_page_config(
    page_title="CLC Behaviour Support – SANDBOX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Sandbox banner ---
st.markdown(
    """
<div style='padding: 12px; background-color: #8A1C1C; color: white; border-radius: 8px; margin-bottom: 10px;'>
    <strong>SANDBOX / DEMO MODE:</strong> This app uses mock data only. Do <u>not</u> enter real student information.
</div>
""",
    unsafe_allow_html=True,
)

# --- Mock Staff (with emails so login "works") ---
MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP", "email": "emily.jones@example.com"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY", "email": "daniel.lee@example.com"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY", "email": "sarah.chen@example.com"},
    {"id": "s4", "name": "Admin User", "role": "ADM", "email": "admin.user@example.com"},
    {"id": "s5", "name": "Michael Torres", "role": "JP", "email": "michael.torres@example.com"},
    {"id": "s6", "name": "Jessica Williams", "role": "PY", "email": "jessica.williams@example.com"},
]

# --- EXPANDED Mock Students (3 per program = 9 total) ---
MOCK_STUDENTS = [
    # JP - 3 students
    {"id": "stu_jp1", "name": "Emma T.", "grade": "R", "dob": "2018-05-30", "edid": "ED12348", "program": "JP"},
    {"id": "stu_jp2", "name": "Oliver S.", "grade": "Y1", "dob": "2017-09-12", "edid": "ED12349", "program": "JP"},
    {"id": "stu_jp3", "name": "Sophie M.", "grade": "Y2", "dob": "2016-03-20", "edid": "ED12350", "program": "JP"},
    
    # PY - 3 students  
    {"id": "stu_py1", "name": "Liam C.", "grade": "Y3", "dob": "2015-06-15", "edid": "ED12351", "program": "PY"},
    {"id": "stu_py2", "name": "Ava R.", "grade": "Y4", "dob": "2014-11-08", "edid": "ED12352", "program": "PY"},
    {"id": "stu_py3", "name": "Noah B.", "grade": "Y6", "dob": "2012-02-28", "edid": "ED12353", "program": "PY"},
    
    # SY - 3 students
    {"id": "stu_sy1", "name": "Isabella G.", "grade": "Y7", "dob": "2011-04-17", "edid": "ED12354", "program": "SY"},
    {"id": "stu_sy2", "name": "Ethan D.", "grade": "Y9", "dob": "2009-12-03", "edid": "ED12355", "program": "SY"},
    {"id": "stu_sy3", "name": "Mia A.", "grade": "Y11", "dob": "2007-08-20", "edid": "ED12356", "program": "SY"},
]

PROGRAM_NAMES = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}

SUPPORT_TYPES = [
    "1:1 Individual Support",
    "Independent",
    "Small Group",
    "Large Group",
]

BEHAVIOUR_TYPES = [
    "Verbal Refusal",
    "Elopement",
    "Property Destruction",
    "Aggression (Peer)",
    "Aggression (Adult)",
    "Self-Harm",
    "Verbal Aggression",
    "Other",
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
    "JP Classroom",
    "JP Spill Out",
    "PY Classroom",
    "PY Spill Out",
    "SY Classroom",
    "SY Spill Out",
    "Student Kitchen",
    "Admin",
    "Gate",
    "Library",
    "Playground",
    "Yard",
    "Toilets",
    "Excursion",
    "Swimming",
]

VALID_PAGES = [
    "login",
    "landing",
    "program_students",
    "incident_log",
    "critical_incident",
    "student_analysis",
    "program_overview",  # NEW
]

# =========================================
# HELPER FUNCTIONS
# =========================================


def init_state():
    """Initialise all session_state keys used in the app."""
    ss = st.session_state
    if "logged_in" not in ss:
        ss.logged_in = False
    if "current_user" not in ss:
        ss.current_user = None
    if "current_page" not in ss:
        ss.current_page = "login"
    if "students" not in ss:
        ss.students = MOCK_STUDENTS
    if "staff" not in ss:
        ss.staff = MOCK_STAFF
    if "incidents" not in ss:
        ss.incidents = generate_mock_incidents(70)  # More incidents
    if "critical_incidents" not in ss:
        ss.critical_incidents = []
    if "selected_program" not in ss:
        ss.selected_program = "JP"
    if "selected_student_id" not in ss:
        ss.selected_student_id = None
    if "current_incident_id" not in ss:
        ss.current_incident_id = None
    if "abch_rows" not in ss:
        ss.abch_rows = []


def login_user(email: str) -> bool:
    """
    Very forgiving login for sandbox:
    - If email matches a mock staff email: log in as that staff.
    - Otherwise: log in as 'Demo User (JP)' so you can test.
    """
    email = (email or "").strip().lower()
    if not email:
        return False

    for staff in st.session_state.staff:
        if staff.get("email", "").lower() == email:
            st.session_state.logged_in = True
            st.session_state.current_user = staff
            st.session_state.current_page = "landing"
            return True

    # fallback demo user
    demo = {"id": "demo_staff", "name": "Demo User", "role": "JP", "email": email}
    st.session_state.logged_in = True
    st.session_state.current_user = demo
    st.session_state.current_page = "landing"
    return True


def go_to(page: str, **kwargs):
    """Simple page navigation helper."""
    if page not in VALID_PAGES:
        st.error(f"Unknown page: {page}")
        return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        setattr(st.session_state, k, v)
    st.rerun()


def get_student(student_id: str):
    if not student_id:
        return None
    return next((s for s in st.session_state.students if s["id"] == student_id), None)


def get_active_staff():
    return st.session_state.staff


def get_session_from_time(t: time) -> str:
    h = t.hour
    if h < 11:
        return "Morning"
    elif h < 13:
        return "Middle"
    else:
        return "Afternoon"


def calculate_age(dob_str: str):
    try:
        d = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        years = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        return years
    except Exception:
        return None


def generate_mock_incidents(n: int = 70):
    """Create random quick incidents so the analysis page has something to show."""
    incidents = []
    
    # Weight certain students to have more incidents for realistic patterns
    student_weights = {
        "stu_jp1": 8,
        "stu_jp2": 5, 
        "stu_jp3": 3,
        "stu_py1": 10,
        "stu_py2": 7,
        "stu_py3": 4,
        "stu_sy1": 12,
        "stu_sy2": 9,
        "stu_sy3": 6,
    }
    
    student_pool = []
    for stu in MOCK_STUDENTS:
        weight = student_weights.get(stu["id"], 5)
        student_pool.extend([stu] * weight)
    
    for _ in range(n):
        stu = random.choice(student_pool)
        beh = random.choice(BEHAVIOUR_TYPES)
        ant = random.choice(ANTECEDENTS)
        loc = random.choice(LOCATIONS)
        support = random.choice(SUPPORT_TYPES)
        interv = random.choice(INTERVENTIONS)
        
        # More realistic severity distribution
        sev = random.choices([1, 2, 3, 4, 5], weights=[20, 35, 25, 15, 5])[0]

        dt = datetime.now() - timedelta(days=random.randint(0, 90))
        t_hour = random.choices([9, 10, 11, 12, 13, 14, 15], weights=[10, 15, 12, 8, 12, 18, 10])[0]
        dt = dt.replace(hour=t_hour, minute=random.randint(0, 59), second=0)

        incidents.append(
            {
                "id": str(uuid.uuid4()),
                "student_id": stu["id"],
                "student_name": stu["name"],
                "date": dt.date().isoformat(),
                "time": dt.time().strftime("%H:%M:%S"),
                "day": dt.strftime("%A"),
                "session": get_session_from_time(dt.time()),
                "location": loc,
                "behaviour_type": beh,
                "antecedent": ant,
                "support_type": support,
                "intervention": interv,
                "severity": sev,
                "reported_by": random.choice(MOCK_STAFF)["name"],
                "additional_staff": [],
                "description": "Auto-generated mock incident.",
                "hypothesis": generate_simple_function(ant, beh),
                "is_critical": sev >= 4,
                "duration_minutes": random.randint(2, 25),
            }
        )
    return incidents


# =========================================
# HYPOTHESIS ENGINE (SIMPLE)
# =========================================


def generate_simple_function(antecedent: str, behaviour: str) -> str:
    """
    Returns one simple hypothesis line in the requested format:
    'To get/avoid <function>' where <function> is one of:
    tangible / request / activity / sensory / attention.
    """
    ant = (antecedent or "").lower()
    beh = (behaviour or "").lower()

    # Decide get vs avoid and function
    if any(k in ant for k in ["instruction", "demand", "work", "task", "academic"]):
        get_avoid = "To avoid"
        fn = "request / activity"
    elif "transition" in ant:
        get_avoid = "To avoid"
        fn = "transition / activity"
    elif any(k in ant for k in ["denied", "access", "item", "object", "preferred"]):
        get_avoid = "To get"
        fn = "tangible"
    elif any(k in ant for k in ["sensory", "noise", "lights", "overload"]):
        get_avoid = "To avoid"
        fn = "sensory"
    elif any(k in ant for k in ["peer", "attention", "staff"]):
        get_avoid = "To get"
        fn = "attention"
    else:
        get_avoid = "To get"
        fn = "attention"

    return f"{get_avoid} {fn}"


# =========================================
# PAGES
# =========================================


def render_login_page():
    st.markdown("## 🔐 Staff Login (Sandbox)")
    st.caption(
        "Use any email address. If it matches a mock staff email, you'll log in as them; "
        "otherwise you'll be 'Demo User'."
    )
    
    with st.expander("📧 Demo Staff Emails"):
        for staff in MOCK_STAFF:
            st.code(staff["email"])

    email = st.text_input("Email address", placeholder="emily.jones@example.com")

    if st.button("Login", type="primary"):
        if not email:
            st.warning("Please enter an email.")
        else:
            login_user(email)
            st.success(f"Logged in as {st.session_state.current_user['name']}")
            st.rerun()


def render_landing_page():
    user = st.session_state.current_user or {}
    st.markdown(
        f"### 👋 Welcome, **{user.get('name', 'User')}** "
        f"({user.get('role', 'Role unknown')}) — SANDBOX VERSION"
    )
    st.caption(f"Email: {user.get('email', 'N/A')}")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = "login"
            st.rerun()

    st.markdown("---")

    # Quick stats
    total_incidents = len(st.session_state.incidents)
    total_students = len(st.session_state.students)
    critical_count = len([i for i in st.session_state.incidents if i.get("is_critical")])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Students", total_students)
    with col2:
        st.metric("📊 Total Incidents", total_incidents)
    with col3:
        st.metric("🚨 Critical Incidents", critical_count)

    st.markdown("---")
    st.markdown("### 📚 Select Program")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Junior Primary")
        jp_students = len([s for s in st.session_state.students if s["program"] == "JP"])
        st.caption(f"{jp_students} students")
        if st.button("Enter JP", key="enter_jp", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="JP")
            
    with col2:
        st.markdown("#### Primary Years")
        py_students = len([s for s in st.session_state.students if s["program"] == "PY"])
        st.caption(f"{py_students} students")
        if st.button("Enter PY", key="enter_py", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="PY")
            
    with col3:
        st.markdown("#### Senior Years")
        sy_students = len([s for s in st.session_state.students if s["program"] == "SY"])
        st.caption(f"{sy_students} students")
        if st.button("Enter SY", key="enter_sy", use_container_width=True, type="primary"):
            go_to("program_students", selected_program="SY")

    st.markdown("---")

    st.markdown("### ⚡ Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Quick Incident Log")
        all_students = [s for s in st.session_state.students]
        selected = st.selectbox(
            "Select student",
            options=all_students,
            format_func=lambda s: f"{s['name']} ({s['program']} - Grade {s['grade']})",
        )

        if st.button("Start Quick Log", type="primary", key="quick_log_btn", use_container_width=True):
            go_to("incident_log", selected_student_id=selected["id"])
    
    with col2:
        st.markdown("#### Program Overview")
        st.caption("View cross-program analytics")
        if st.button("View Program Analytics", use_container_width=True):
            go_to("program_overview")


def render_program_students_page():
    program = st.session_state.get("selected_program", "JP")
    st.markdown(f"## {PROGRAM_NAMES.get(program, program)} Program — Students")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅ Back to landing"):
            go_to("landing")

    students = [s for s in st.session_state.students if s["program"] == program]

    if not students:
        st.info("No students in this program (mock).")
        return

    # Student cards with incident counts
    for stu in students:
        stu_incidents = [i for i in st.session_state.incidents if i["student_id"] == stu["id"]]
        critical = [i for i in stu_incidents if i.get("is_critical")]
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"### {stu['name']}")
                st.caption(f"Grade {stu['grade']} | EDID {stu['edid']}")
                age = calculate_age(stu["dob"])
                if age is not None:
                    st.caption(f"Age: {age} years")
            
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
        st.error("No student selected.")
        if st.button("Back to landing"):
            go_to("landing")
        return

    st.markdown(f"## 📝 Quick Incident Log — {student['name']}")
    st.caption(f"{student['program']} Program | Grade {student['grade']}")

    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input("Date", date.today())
            inc_time = st.time_input("Time", datetime.now().time())
            location = st.selectbox("Location", LOCATIONS)
        with col2:
            behaviour = st.selectbox("Behaviour Type", BEHAVIOUR_TYPES)
            antecedent = st.selectbox("Antecedent (Trigger)", ANTECEDENTS)
            support_type = st.selectbox("Type of Support", SUPPORT_TYPES)

        st.markdown("### Staff")
        reporter = st.session_state.current_user["name"]
        st.info(f"Staff member reporting: **{reporter}** (auto-filled)")

        staff_names = [s["name"] for s in get_active_staff()]
        additional_staff = st.multiselect(
            "Additional staff involved (if any)", options=staff_names
        )

        st.markdown("### Intervention Used")
        intervention = st.selectbox(
            "Adult action / de-escalation strategy",
            INTERVENTIONS,
        )
        
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=60, value=5)

        severity = st.slider("Severity (1 = low, 5 = high)", 1, 5, 2)

        description = st.text_area(
            "Brief description (factual)",
            placeholder="Short, objective description of what occurred…",
        )

        st.markdown("### Hypothesis (auto-generated, editable)")
        auto_hyp = generate_simple_function(antecedent, behaviour)
        hypothesis = st.text_input("Function of behaviour", value=auto_hyp)

        submitted = st.form_submit_button("Submit Incident", type="primary")

    if submitted:
        new_id = str(uuid.uuid4())
        rec = {
            "id": new_id,
            "student_id": student_id,
            "student_name": student["name"],
            "date": inc_date.isoformat(),
            "time": inc_time.strftime("%H:%M:%S"),
            "day": inc_date.strftime("%A"),
            "session": get_session_from_time(inc_time),
            "location": location,
            "behaviour_type": behaviour,
            "antecedent": antecedent,
            "support_type": support_type,
            "reported_by": reporter,
            "additional_staff": additional_staff,
            "intervention": intervention,
            "severity": severity,
            "duration_minutes": duration,
            "description": description,
            "hypothesis": hypothesis,
            "is_critical": severity >= 4,
        }
        st.session_state.incidents.append(rec)
        st.success("✅ Incident saved (sandbox).")

        if severity >= 4:
            st.warning("⚠️ Severity ≥ 4 → Proceed to Critical Incident ABCH form?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Complete ABCH Form", type="primary"):
                    go_to("critical_incident", current_incident_id=new_id)
            with col2:
                if st.button("↩️ Back to students"):
                    go_to("program_students", selected_program=student["program"])
        else:
            if st.button("↩️ Back to students"):
                go_to("program_students", selected_program=student["program"])


def generate_critical_recommendations(quick_inc: dict) -> str:
    ant = quick_inc.get("antecedent", "known triggers")
    beh = quick_inc.get("behaviour_type", "behaviour of concern")
    loc = quick_inc.get("location", "learning area")
    sess = quick_inc.get("session", "session")

    return (
        f"Patterns suggest incidents often occur when '{ant}' in the {loc} during {sess}. "
        "Consider applying CPI's Supportive stance earlier in the escalation, increasing "
        "co-regulation opportunities, and building predictable routines at these times. "
        "Use Berry Street Education Model strategies (Body and Relationship) such as grounding, "
        "rhythmic regulation, and warm relational check-ins. Link adjustments to the Australian "
        "Curriculum General Capabilities (Personal & Social Capability), and set a SMART goal "
        "around help-seeking and self-regulation during similar tasks or transitions."
    )


def render_critical_incident_page():
    inc_id = st.session_state.get("current_incident_id")
    quick_inc = next((i for i in st.session_state.incidents if i["id"] == inc_id), None)

    if not quick_inc:
        st.error("No quick incident found to build the critical form from.")
        if st.button("Back to landing"):
            go_to("landing")
        return

    st.markdown("## 🚨 Critical Incident ABCH Form")
    st.caption("Auto-filled from quick log. Edit as required.")

    with st.expander("Quick incident details"):
        st.json(quick_inc)

    # ABCH laid out in 4 columns
    st.markdown("### ABCH Overview")
    colA, colB, colC, colH = st.columns(4)

    with colA:
        st.subheader("A – Antecedent")
        A_text = st.text_area(
            "What happened before?",
            value=quick_inc.get("antecedent", ""),
            key="crit_A",
        )

    with colB:
        st.subheader("B – Behaviour")
        B_text = st.text_area(
            "What did the student do?",
            value=quick_inc.get("behaviour_type", ""),
            key="crit_B",
        )

    with colC:
        st.subheader("C – Consequence")
        C_text = st.text_area(
            "What happened after?",
            value="",
            key="crit_C",
        )

    with colH:
        st.subheader("H – Hypothesis")
        default_H = generate_simple_function(
            quick_inc.get("antecedent", ""), quick_inc.get("behaviour_type", "")
        )
        H_text = st.text_area("Why did this occur?", value=default_H, key="crit_H")

    st.markdown("---")

    # Additional ABCH lines for complex incidents
    st.markdown("### Additional Incident Elements (optional)")

    if st.button("➕ Add another ABCH line"):
        st.session_state.abch_rows.append({"A": "", "B": "", "C": "", "H": ""})

    for idx, row in enumerate(st.session_state.abch_rows):
        st.markdown(f"**Extra element {idx+1}**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            row["A"] = st.text_input("A", value=row["A"], key=f"rowA_{idx}")
        with c2:
            row["B"] = st.text_input("B", value=row["B"], key=f"rowB_{idx}")
        with c3:
            row["C"] = st.text_input("C", value=row["C"], key=f"rowC_{idx}")
        with c4:
            row["H"] = st.text_input("H", value=row["H"], key=f"rowH_{idx}")

    st.markdown("---")

    st.markdown("### Safety Responses (CPI-aligned, non-restraint)")
    safety_responses = st.multiselect(
        "Actions taken",
        [
            "CPI Supportive stance",
            "Cleared nearby students",
            "Student moved to safer location",
            "Additional staff attended",
            "Safety plan enacted",
            "Continued monitoring until regulated",
            "First aid offered",
        ],
    )

    st.markdown("### Notifications")
    notifications = st.multiselect(
        "Who was notified?",
        [
            "Parent / carer",
            "Line manager",
            "Safety & Wellbeing / SSS",
            "DCP",
            "SAPOL",
            "First Aid officer",
            "Injury report completed",
            "Transport home required",
        ],
    )

    st.markdown("### Outcome actions")
    removed = st.checkbox("Removed from learning")
    family_contact = st.checkbox("Family contacted")
    safety_updated = st.checkbox("Safety plan updated")
    transport_home = st.checkbox("Transport home required")
    other_actions = st.text_area("Other actions / follow-up")

    st.markdown("### Recommendations (auto-generated, editable)")
    rec_text = generate_critical_recommendations(quick_inc)
    recommendations = st.text_area("Recommendations", value=rec_text, height=200)

    if st.button("Save critical incident", type="primary"):
        record = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "quick_incident_id": quick_inc["id"],
            "student_id": quick_inc["student_id"],
            "ABCH_primary": {"A": A_text, "B": B_text, "C": C_text, "H": H_text},
            "ABCH_additional": st.session_state.abch_rows,
            "safety_responses": safety_responses,
            "notifications": notifications,
            "outcomes": {
                "removed": removed,
                "family_contact": family_contact,
                "safety_updated": safety_updated,
                "transport_home": transport_home,
                "other": other_actions,
            },
            "recommendations": recommendations,
        }
        st.session_state.critical_incidents.append(record)
        st.success("✅ Critical incident saved (sandbox).")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Go to student analysis"):
                go_to("student_analysis", selected_student_id=quick_inc["student_id"])
        with col2:
            if st.button("↩️ Back to students"):
                go_to("program_students", selected_program=get_student(quick_inc["student_id"])["program"])


# =========================================
# STUDENT ANALYSIS PAGE (with clinical section)
# =========================================

def render_student_analysis_page():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected.")
        if st.button("Back to landing"):
            go_to("landing")
        return

    st.markdown(f"## 📊 Data Analysis — {student['name']}")
    st.caption(f"{student['program']} program | Grade {student['grade']}")

    # --- Pull incidents for this student ---
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]

    if not quick and not crit:
        st.info("No incident data yet for this student.")
        if st.button("Log first incident"):
            go_to("incident_log", selected_student_id=student_id)
        return

    # ---------- Build unified dataframe ----------
    quick_df = pd.DataFrame(quick) if quick else pd.DataFrame()
    crit_df = pd.DataFrame(crit) if crit else pd.DataFrame()

    if not quick_df.empty:
        quick_df["incident_type"] = "Quick"
        quick_df["date_parsed"] = pd.to_datetime(quick_df["date"])

    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        # Use created_at if present, otherwise now
        if "created_at" in crit_df.columns:
            crit_df["date_parsed"] = pd.to_datetime(crit_df["created_at"])
        else:
            crit_df["date_parsed"] = pd.to_datetime(datetime.now().isoformat())

        # Criticals default to severity 5 if not otherwise set
        crit_df["severity"] = 5

        # Align some key columns for graphs
        crit_df["antecedent"] = crit_df["ABCH_primary"].apply(
            lambda d: d.get("A") if isinstance(d, dict) else ""
        )
        crit_df["behaviour_type"] = crit_df["ABCH_primary"].apply(
            lambda d: d.get("B") if isinstance(d, dict) else ""
        )
        # Give criticals a location/session from last quick if available
        if not quick_df.empty:
            crit_df["location"] = quick_df["location"].iloc[0]
            crit_df["session"] = quick_df["session"].iloc[0]
        else:
            crit_df["location"] = "Unknown"
            crit_df["session"] = "Unknown"

    full_df = pd.concat([quick_df, crit_df], ignore_index=True)

    # ---------- Summary metrics ----------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total incidents", len(full_df))
    with col2:
        st.metric(
            "Critical incidents",
            len(full_df[full_df["incident_type"] == "Critical"]),
        )
    with col3:
        st.metric("Average severity", round(full_df["severity"].mean(), 1))
    with col4:
        days_span = (
            full_df["date_parsed"].max() - full_df["date_parsed"].min()
        ).days + 1
        st.metric("Days tracked", days_span)

    st.markdown("---")

    # =====================================================
    # GRAPHS
    # =====================================================

    # Timeline
    st.markdown("### ⏱️ Severity over time (Quick vs Critical)")
    fig = px.scatter(
        full_df,
        x="date_parsed",
        y="severity",
        color="incident_type",
        hover_data=["behaviour_type", "antecedent", "location"],
        labels={"date_parsed": "Date", "severity": "Severity"},
        color_discrete_map={"Quick": "#3b82f6", "Critical": "#ef4444"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Antecedent frequency
    st.markdown("### 🔥 Antecedent frequency")
    ant_counts = full_df["antecedent"].value_counts().reset_index()
    ant_counts.columns = ["Antecedent", "Count"]
    fig2 = px.bar(ant_counts, x="Count", y="Antecedent", orientation="h", color_discrete_sequence=["#10b981"])
    st.plotly_chart(fig2, use_container_width=True)

    # Location hotspots
    st.markdown("### 📍 Location hotspots")
    loc_counts = full_df["location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig3 = px.bar(loc_counts, x="Count", y="Location", orientation="h", color_discrete_sequence=["#f59e0b"])
    st.plotly_chart(fig3, use_container_width=True)

    # Behaviour types
    st.markdown("### ⚠️ Behaviour types")
    beh_counts = full_df["behaviour_type"].value_counts().reset_index()
    beh_counts.columns = ["Behaviour", "Count"]
    fig4 = px.bar(beh_counts, x="Count", y="Behaviour", orientation="h", color_discrete_sequence=["#ef4444"])
    st.plotly_chart(fig4, use_container_width=True)

    # Session patterns
    st.markdown("### 🕒 Session patterns")
    sess_counts = full_df["session"].value_counts().reset_index()
    sess_counts.columns = ["Session", "Count"]
    fig5 = px.bar(sess_counts, x="Session", y="Count", color_discrete_sequence=["#8b5cf6"])
    st.plotly_chart(fig5, use_container_width=True)

    # =====================================================
    # CLINICAL INTERPRETATION & NEXT STEPS
    # =====================================================
    if not full_df.empty:
        # Key patterns for use in summary / narrative
        top_ant = full_df["antecedent"].mode()[0] if len(full_df["antecedent"]) > 0 else "Unknown"
        top_beh = full_df["behaviour_type"].mode()[0] if len(full_df["behaviour_type"]) > 0 else "Unknown"
        top_loc = full_df["location"].mode()[0] if len(full_df["location"]) > 0 else "Unknown"
        top_session = full_df["session"].mode()[0] if len(full_df["session"]) > 0 else "Unknown"

        total = len(full_df)
        crit_total = len(full_df[full_df["incident_type"] == "Critical"])
        quick_total = total - crit_total
        crit_rate = (crit_total / total) * 100 if total > 0 else 0

        # Trend in severity (first vs last)
        full_sorted = full_df.sort_values("date_parsed")
        if len(full_sorted) >= 2:
            first_sev = full_sorted["severity"].iloc[0]
            last_sev = full_sorted["severity"].iloc[-1]
            if last_sev > first_sev:
                severity_trend = "increasing over time"
            elif last_sev < first_sev:
                severity_trend = "decreasing over time"
            else:
                severity_trend = "relatively stable over time"
        else:
            severity_trend = "unable to determine (limited data)"

        st.markdown("---")
        st.markdown("## 🧠 Clinical Interpretation & Next Steps")

        # ---------- 1. Summary of Data Findings ----------
        st.markdown("### 1. Summary of Data Findings")

        st.markdown(
            f"- **Primary concern:** **{top_beh}** is the most frequently recorded "
            f"behaviour of concern."
        )
        st.markdown(
            f"- **Key triggers:** The most common antecedent is **{top_ant}**, "
            f"indicating this context regularly precedes dysregulation."
        )
        st.markdown(
            f"- **Hotspot locations:** Incidents most often occur in **{top_loc}**, "
            f"particularly during the **{top_session}** session."
        )
        st.markdown(
            f"- **Incident profile:** {quick_total} quick incidents and {crit_total} "
            f"critical incidents have been recorded (critical incidents = "
            f"**{crit_rate:.1f}%** of all incidents)."
        )
        st.markdown(
            f"- **Severity trend:** Overall severity appears **{severity_trend}**."
        )

        # ---------- 2. Clinical interpretation (trauma-informed) ----------
        st.markdown("### 2. Clinical Interpretation (Trauma-Informed)")

        clinical_text = (
            f"Patterns suggest that {student['name']} is most vulnerable when **{top_ant}** "
            f"occurs, often in the **{top_loc}** during **{top_session}**. These moments "
            "likely narrow the student's window of tolerance, increasing the risk of "
            "fight/flight responses such as the identified behaviour.\n\n"
            "Through a **trauma-informed lens**, this behaviour is understood as a safety "
            "strategy rather than wilful defiance. CPI emphasises staying in the **Supportive** "
            "phase as early as possible — calm body language, non-threatening stance and "
            "minimal verbal load.\n\n"
            "The **Berry Street Education Model** (Body, Relationship, Stamina, Engagement) "
            "points towards strengthening **Body** (regulation routines, predictable transitions) "
            "and **Relationship** (connection before correction). SMART trauma principles "
            "highlight the importance of predictability, relational safety and reducing cognitive "
            "load during known trigger times."
        )
        st.info(clinical_text)

        # ---------- 3. Next Steps & Recommendations ----------
        st.markdown("### 3. Next Steps & Recommendations")

        next_steps = (
            "1. **Proactive regulation around key triggers**  \n"
            f"   - Provide a brief check-in and clear visual cue before **{top_ant}**.  \n"
            "   - Offer a regulated start (breathing, movement, sensory tool) before the "
            f"high-risk **{top_session}** session.\n\n"
            "2. **Co-regulation & staff responses (CPI aligned)**  \n"
            "   - Use CPI Supportive stance, low slow voice and minimal language when early "
            "signs of escalation appear.  \n"
            "   - Reduce audience by moving peers where possible and maintain connection with "
            "one key adult.\n\n"
            "3. **Teaching replacement skills (Australian Curriculum – General Capabilities)**  \n"
            "   - Link goals to **Personal and Social Capability** (self-management & "
            "social management).  \n"
            "   - Explicitly teach and rehearse a help-seeking routine the student can use "
            "in place of the behaviour (e.g., card, phrase, movement to a safe space).\n\n"
            "4. **SMART-style goal example**  \n"
            "   - *Over the next 5 weeks, during identified trigger times, the student will "
            "use an agreed help-seeking strategy instead of the behaviour of concern in "
            "4 out of 5 opportunities, with co-regulation support from staff.*"
        )
        st.success(next_steps)

    if st.button("⬅ Back to students"):
        go_to("program_students", selected_program=student["program"])


# NEW: Program Overview Page
def render_program_overview_page():
    st.markdown("## 📈 Cross-Program Analytics")
    st.caption("Incident patterns across all programs")
    
    if st.button("⬅ Back to landing"):
        go_to("landing")
    
    incidents = st.session_state.incidents
    if not incidents:
        st.info("No incidents recorded yet.")
        return
    
    df = pd.DataFrame(incidents)
    df["date_parsed"] = pd.to_datetime(df["date"])
    
    # Get student program info
    df["program"] = df["student_id"].apply(
        lambda sid: next((s["program"] for s in st.session_state.students if s["id"] == sid), "Unknown")
    )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", len(df))
    with col2:
        st.metric("Critical Incidents", len(df[df["is_critical"] == True]))
    with col3:
        st.metric("Average Severity", round(df["severity"].mean(), 2))
    
    st.markdown("---")
    
    # Program comparison
    st.markdown("### 📚 Incidents by Program")
    prog_counts = df["program"].value_counts().reset_index()
    prog_counts.columns = ["Program", "Count"]
    fig1 = px.bar(prog_counts, x="Program", y="Count", color="Program")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Behaviour types across programs
    st.markdown("### ⚠️ Behaviour Types by Program")
    beh_by_prog = df.groupby(["program", "behaviour_type"]).size().reset_index(name="count")
    fig2 = px.bar(beh_by_prog, x="behaviour_type", y="count", color="program", barmode="group")
    fig2.update_xaxes(tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Time trends
    st.markdown("### 📅 Incident Trends Over Time")
    df["week"] = df["date_parsed"].dt.to_period("W").astype(str)
    weekly = df.groupby(["week", "program"]).size().reset_index(name="count")
    fig3 = px.line(weekly, x="week", y="count", color="program")
    fig3.update_xaxes(tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Location hotspots
    st.markdown("### 📍 Location Hotspots (All Programs)")
    loc_counts = df["location"].value_counts().head(10).reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig4 = px.bar(loc_counts, x="Count", y="Location", orientation="h")
    st.plotly_chart(fig4, use_container_width=True)


# =========================================
# MAIN APP ROUTER
# =========================================

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
    elif page == "program_overview":
        render_program_overview_page()
    elif page == "login":
        render_login_page()
    else:
        st.error("Unknown page.")
        render_landing_page()


if __name__ == "__main__":
    main()
