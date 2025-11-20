# app.py — CLC Behaviour Support Sandbox Version
# ----------------------------------------------
# - No Supabase calls (mock data only)
# - Quick Incident Log + Critical ABCH workflow
# - Detailed student analysis with graphs + trauma-informed recommendations

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
import uuid
import random
import plotly.express as px

# =========================================================
# 1. PAGE CONFIG + SANDBOX BANNER
# =========================================================

st.set_page_config(
    page_title="CLC Behaviour Support — SANDBOX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<div style='padding: 12px; background-color: #8a1c1c; color: white;
            border-radius: 10px; margin-bottom: 10px;'>
  <strong>⚠️ SANDBOX / DEMO MODE:</strong>
  This version uses mock data only. Do NOT enter real student information.
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 2. MOCK DATA
# =========================================================

MOCK_STAFF = [
    {"id": "s1", "name": "Emily Jones", "role": "JP"},
    {"id": "s2", "name": "Daniel Lee", "role": "PY"},
    {"id": "s3", "name": "Sarah Chen", "role": "SY"},
    {"id": "s4", "name": "Admin User", "role": "ADM"},
    {"id": "s5", "name": "Michael Torres", "role": "JP"},
    {"id": "s6", "name": "Jessica Williams", "role": "PY"},
]

MOCK_STUDENTS = [
    {"id": "stu_001", "name": "Izack N.", "grade": "7", "dob": "2012-03-15", "edid": "ED12345", "program": "SY"},
    {"id": "stu_002", "name": "Mia K.", "grade": "8", "dob": "2011-07-22", "edid": "ED12346", "program": "PY"},
    {"id": "stu_003", "name": "Liam B.", "grade": "9", "dob": "2010-11-08", "edid": "ED12347", "program": "SY"},
    {"id": "stu_004", "name": "Emma T.", "grade": "R", "dob": "2017-05-30", "edid": "ED12348", "program": "JP"},
    {"id": "stu_005", "name": "Oliver S.", "grade": "Y2", "dob": "2015-09-12", "edid": "ED12349", "program": "JP"},
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
    "Other",
]

ANTECEDENTS = [
    "Requested to transition activity",
    "Given instruction/demand (academic)",
    "Given instruction/demand (non-academic)",
    "Peer conflict / teasing",
    "Staff attention shifted away",
    "Unstructured free time",
    "Sensory overload",
    "Access to preferred item denied",
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

SESSIONS = ["Morning", "Middle", "Afternoon"]


def generate_mock_incidents(n=60):
    records = []
    for _ in range(n):
        stu = random.choice(MOCK_STUDENTS)
        d = datetime.now().date() - timedelta(days=random.randint(0, 40))
        t = time(hour=random.randint(9, 15), minute=random.choice([0, 15, 30, 45]))
        sev = random.randint(1, 5)
        session = (
            "Morning"
            if t.hour < 11
            else "Middle"
            if t.hour < 13
            else "Afternoon"
        )
        behaviour = random.choice(BEHAVIOUR_TYPES)
        ant = random.choice(ANTECEDENTS)
        loc = random.choice(LOCATIONS)
        support = random.choice(SUPPORT_TYPES)
        intervention = random.choice(
            [
                "Offered a break",
                "Used calm tone and active listening",
                "Reduced demands and chunked task",
                "Moved peers away and co-regulated",
                "Provided sensory strategy",
                "",
            ]
        )
        records.append(
            {
                "id": str(uuid.uuid4()),
                "student_id": stu["id"],
                "student_name": stu["name"],
                "incident_date": d.strftime("%Y-%m-%d"),
                "incident_time": t.strftime("%H:%M:%S"),
                "day_of_week": d.strftime("%A"),
                "session": session,
                "location": loc,
                "behaviour_type": behaviour,
                "antecedent": ant,
                "severity": sev,
                "support_type": support,
                "reported_by": random.choice(MOCK_STAFF)["name"],
                "additional_staff": [],
                "intervention": intervention,
                "description": "",
                "hypothesis": "",
                "is_critical": sev >= 3,
            }
        )
    return records


# =========================================================
# 3. SESSION STATE + HELPERS
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "students" not in st.session_state:
    st.session_state.students = MOCK_STUDENTS
if "staff" not in st.session_state:
    st.session_state.staff = MOCK_STAFF
if "incidents" not in st.session_state:
    st.session_state.incidents = generate_mock_incidents()
if "critical_incidents" not in st.session_state:
    st.session_state.critical_incidents = []
if "selected_program" not in st.session_state:
    st.session_state.selected_program = "JP"
if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None
if "current_incident_id" not in st.session_state:
    st.session_state.current_incident_id = None


def go_to(page: str, **kwargs):
    st.session_state.current_page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()


def get_student(student_id: str):
    if not student_id:
        return None
    return next(
        (s for s in st.session_state.students if s["id"] == student_id),
        None,
    )


def get_active_staff():
    return st.session_state.staff


def get_session_from_time(t: time) -> str:
    if t.hour < 11:
        return "Morning"
    elif t.hour < 13:
        return "Middle"
    else:
        return "Afternoon"


# =========================================================
# 4. LOGIN PAGE
# =========================================================

def render_login():
    st.title("🔐 CLC Behaviour Support — Sandbox Login")

    st.caption(
        "In sandbox mode, you can log in with any email that matches a mock staff, "
        "e.g. **emily.jones@demo.com**, **daniel.lee@demo.com**, etc."
    )

    email = st.text_input("Email", placeholder="first.last@demo.com")

    if st.button("Login", type="primary"):
        email_clean = email.strip().lower()
        staff_match = None
        for staff in st.session_state.staff:
            expected = staff["name"].replace(" ", ".").lower() + "@demo.com"
            if expected == email_clean:
                staff_match = staff
                break

        if staff_match:
            st.session_state.logged_in = True
            st.session_state.current_user = staff_match
            go_to("landing")
        else:
            # Fallback: log in as Demo User but still allow use
            st.session_state.logged_in = True
            st.session_state.current_user = {
                "id": "demo",
                "name": "Demo User",
                "role": "ADM",
            }
            st.warning("Email not matched to mock staff. Logged in as Demo User.")
            go_to("landing")


# =========================================================
# 5. LANDING PAGE
# =========================================================

def render_landing():
    user = st.session_state.current_user or {}
    col_left, col_right = st.columns([4, 1])
    with col_left:
        st.markdown(f"### 👋 Welcome, {user.get('name', 'User')}")
        st.caption(f"Role: {user.get('role', 'N/A')}  |  Mode: SANDBOX (Mock Data)")
    with col_right:
        if st.button("Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.experimental_rerun()

    st.markdown("---")

    st.markdown(
        """
### 🧭 Sandbox Navigation

- Choose a **program** → **student** → log incidents or view analysis  
- Quick incidents with **severity ≥ 3** will automatically redirect to the **Critical Incident ABCH form**  
- All data is **mock** and resets when the app restarts
"""
    )

    st.markdown("### 🎓 Select Program")

    c1, c2, c3 = st.columns(3)
    if c1.button("Junior Primary (JP)", use_container_width=True):
        go_to("program_students", selected_program="JP")
    if c2.button("Primary Years (PY)", use_container_width=True):
        go_to("program_students", selected_program="PY")
    if c3.button("Senior Years (SY)", use_container_width=True):
        go_to("program_students", selected_program="SY")

    st.markdown("---")
    st.markdown("### 📊 Quick Demo Actions")
    q1, q2 = st.columns(2)
    with q1:
        if st.button("View Analysis for first SY student"):
            # just pick first SY student for demo
            stu = next((s for s in MOCK_STUDENTS if s["program"] == "SY"), None)
            if stu:
                go_to("student_analysis", selected_student_id=stu["id"])
    with q2:
        if st.button("Start Quick Incident for first JP student"):
            stu = next((s for s in MOCK_STUDENTS if s["program"] == "JP"), None)
            if stu:
                go_to("incident_log", selected_student_id=stu["id"])


# =========================================================
# 6. PROGRAM STUDENTS PAGE
# =========================================================

def render_program_students():
    program = st.session_state.get("selected_program", "JP")
    students = [
        s for s in st.session_state.students if s["program"] == program
    ]

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"{PROGRAM_NAMES.get(program, program)} Program (Sandbox)")
    with col_back:
        if st.button("⬅ Home", use_container_width=True):
            go_to("landing")

    st.markdown("---")

    if not students:
        st.info("No students in this program (mock data).")
        return

    st.markdown(f"### Current Students in {PROGRAM_NAMES.get(program, program)}")

    cols_per_row = 3
    for i in range(0, len(students), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, stu in enumerate(students[i : i + cols_per_row]):
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"**{stu['name']}**")
                    st.caption(f"Grade: {stu['grade']} | EDID: {stu['edid']}")
                    col_view, col_log = st.columns(2)
                    if col_view.button("📊 Analyse", key=f"view_{stu['id']}"):
                        go_to("student_analysis", selected_student_id=stu["id"])
                    if col_log.button("📝 Log Incident", key=f"log_{stu['id']}"):
                        go_to("incident_log", selected_student_id=stu["id"])


# =========================================================
# 7. HYPOTHESIS ENGINE
# =========================================================

def generate_hypothesis(antecedent, behaviour, intervention, severity):
    base = f"The behaviour appears linked to the antecedent '{antecedent}', resulting in '{behaviour}'. "

    if severity >= 4:
        sev_text = "This reached a high severity level, suggesting the student moved outside their window of tolerance. "
    elif severity == 3:
        sev_text = "This reached a concerning level, indicating emerging dysregulation. "
    else:
        sev_text = "The behaviour was lower intensity but still highlights underlying unmet needs. "

    # BSEM inference
    bsem_map = {
        "transition": "Body/Regulation and Engagement",
        "instruction": "Stamina and Engagement",
        "peer": "Belonging and Character",
        "sensory": "Body/Regulation",
        "denied": "Engagement and Character",
        "unstructured": "Body/Regulation and Relationship",
    }
    ant_lower = antecedent.lower()
    bsem_text = ""
    for key, domain in bsem_map.items():
        if key in ant_lower:
            bsem_text = f"From a Berry Street Education Model perspective, this links to challenges in {domain}. "
            break

    # CPI inference
    if "peer" in ant_lower:
        cpi_text = "CPI suggests this may sit in the escalation phase driven by interpersonal conflict. "
    else:
        cpi_text = "CPI principles suggest this may reflect early escalation where demands exceed available coping skills. "

    smart_text = (
        "Using a SMART trauma lens, increasing predictability, relational safety, and reducing cognitive load "
        "during known trigger times is likely to support regulation. "
    )

    if intervention:
        inter_text = f"The adult action used ('{intervention}') provides information about what helps the student begin to down-regulate. "
    else:
        inter_text = ""

    ac_text = (
        "This incident connects strongly to the Australian Curriculum General Capabilities of Personal and "
        "Social Capability (self-management, social awareness) and Critical and Creative Thinking (problem-solving in social contexts). "
    )

    return base + sev_text + bsem_text + cpi_text + smart_text + inter_text + ac_text


# =========================================================
# 8. INCIDENT LOG PAGE
# =========================================================

def render_incident_log():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)

    if not student:
        st.error("No student selected.")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log — {student['name']}")
        st.caption(f"Program: {student['program']} | Grade: {student['grade']}")
    with col_back:
        if st.button("⬅ Back to Program"):
            go_to("program_students", selected_program=student["program"])

    with st.form("incident_form"):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=datetime.now().date())
            t = st.time_input("Time", value=datetime.now().time())
            location = st.selectbox("Location", LOCATIONS)
        with c2:
            behaviour = st.selectbox("Behaviour Type", BEHAVIOUR_TYPES)
            antecedent = st.selectbox("Antecedent (Trigger)", ANTECEDENTS)
            support_type = st.selectbox("Type of Support", SUPPORT_TYPES)

        st.markdown("### Staff Member Reporting")
        reporter_name = (st.session_state.current_user or {}).get("name", "Unknown")
        st.info(f"Reported by: **{reporter_name}** (auto-filled)")

        st.markdown("### Additional Staff Involved")
        staff_options = [s["name"] for s in get_active_staff()]
        additional_staff = st.multiselect(
            "Select additional staff (if any):", staff_options
        )

        st.markdown("### Intervention / Adult Actions Used")
        intervention = st.text_input(
            "Describe adult actions used to de-escalate or support:",
            placeholder="e.g., Offered a break, used calm tone, removed peers, reduced demands…",
        )

        severity = st.slider("Severity (1–5)", 1, 5, 2)

        description = st.text_area(
            "Short Description (factual)",
            placeholder="Brief factual description of what occurred…",
        )

        st.markdown("### Suggested Hypothesis (Editable)")
        auto_hyp = generate_hypothesis(antecedent, behaviour, intervention, severity)
        hypothesis = st.text_area("Hypothesis", value=auto_hyp)

        submitted = st.form_submit_button("Submit Incident", type="primary")

        if submitted:
            session_label = get_session_from_time(t)
            incident_id = str(uuid.uuid4())

            record = {
                "id": incident_id,
                "student_id": student_id,
                "student_name": student["name"],
                "incident_date": d.strftime("%Y-%m-%d"),
                "incident_time": t.strftime("%H:%M:%S"),
                "day_of_week": d.strftime("%A"),
                "session": session_label,
                "location": location,
                "behaviour_type": behaviour,
                "antecedent": antecedent,
                "severity": severity,
                "support_type": support_type,
                "reported_by": reporter_name,
                "additional_staff": additional_staff,
                "intervention": intervention,
                "description": description,
                "hypothesis": hypothesis,
                "is_critical": severity >= 3,
            }

            st.session_state.incidents.append(record)
            st.success("Incident saved (Sandbox).")

            if severity >= 3:
                st.warning(
                    "This has been flagged as a Critical Incident (Severity ≥3). "
                    "Redirecting to the ABCH Critical Incident form…"
                )
                go_to("critical_incident", current_incident_id=incident_id)
            else:
                go_to("program_students", selected_program=student["program"])


# =========================================================
# 9. CRITICAL INCIDENT ABCH FORM
# =========================================================

def render_critical_incident():
    inc_id = st.session_state.get("current_incident_id")
    quick_incident = next(
        (i for i in st.session_state.incidents if i["id"] == inc_id),
        None,
    )

    if not quick_incident:
        st.error("No critical incident found in session.")
        return

    stu = get_student(quick_incident["student_id"])
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🚨 Critical Incident ABCH Form")
        if stu:
            st.caption(
                f"Student: {stu['name']} | Program: {stu['program']} | Grade: {stu['grade']}"
            )
        st.caption(
            f"From quick incident on {quick_incident['incident_date']} at {quick_incident['incident_time']} "
            f"({quick_incident['location']})"
        )
    with col_back:
        if st.button("⬅ Back to Analysis"):
            go_to("student_analysis", selected_student_id=quick_incident["student_id"])

    with st.expander("Quick Incident Snapshot"):
        st.json(quick_incident)

    st.markdown("## 🧩 ABCH Breakdown (Side-by-Side)")

    colA, colB, colC, colH = st.columns(4)

    with colA:
        st.subheader("A — Antecedent")
        antecedent_A = st.text_area(
            "What happened before?",
            value=quick_incident.get("antecedent", ""),
            key="abch_A",
        )
        st.caption(
            "Consider environmental, relational, and task demands immediately before the incident."
        )

    with colB:
        st.subheader("B — Behaviour")
        behaviour_B = st.text_area(
            "What did the student do?",
            value=quick_incident.get("behaviour_type", ""),
            key="abch_B",
        )
        st.caption("Use CPI: describe observable behaviour only, not assumptions.")

    with colC:
        st.subheader("C — Consequence")
        consequence_C = st.text_area(
            "What happened after (immediate + short-term)?",
            key="abch_C",
        )
        st.caption(
            "Include what adults did, peer response, and any changes to environment/routines."
        )

    with colH:
        st.subheader("H — Hypothesis")
        suggested_h = generate_hypothesis(
            quick_incident.get("antecedent", ""),
            quick_incident.get("behaviour_type", ""),
            quick_incident.get("intervention", ""),
            quick_incident.get("severity", 3),
        )
        st.info(f"Suggested: {suggested_h}")
        hypothesis_H = st.text_area(
            "Why did this occur?",
            value=suggested_h,
            key="abch_H",
        )

    st.markdown("---")

    st.markdown("## 🛡️ Safety Responses (Non-Restraint, CPI-Aligned)")
    safety_responses = st.multiselect(
        "Select safety actions taken:",
        [
            "CPI Supportive Stance",
            "Cleared nearby students",
            "Student moved to safer location",
            "Additional staff attended",
            "Safety plan enacted",
            "Continued monitoring until regulated",
            "First aid offered",
        ],
    )

    st.markdown("---")

    st.markdown("## 📣 Notifications")
    notifications = st.multiselect(
        "Who was notified:",
        [
            "Parent/Carer Notified",
            "Line Manager Notified",
            "Safety & Wellbeing / SSS Notified",
            "DCP Notified",
            "SAPOL Notified",
            "First Aid Provided",
            "Injury Report Completed",
            "Transport Home Required",
        ],
    )

    st.markdown("---")

    st.markdown("## 🧾 Outcome Actions")
    removed = st.checkbox("Removed from learning")
    family_contact = st.checkbox("Family contacted")
    safety_updated = st.checkbox("Safety plan updated / reviewed")
    transport_home = st.checkbox("Transport home required")
    other_actions = st.text_area("Other actions / follow-up")

    st.markdown("---")

    st.markdown("## 🎯 Trauma-Informed Recommendations")
    rec_text = (
        "Based on this pattern, increase proactive co-regulation routines at known trigger times, "
        "and ensure CPI Supportive stance is used early in the escalation curve. Embed Berry Street Body "
        "strategies (movement, sensory breaks, rhythmic routines) and Relationship strategies (check-ins, "
        "predictable adult responses).\n\n"
        "Explicitly teach emotional literacy, help-seeking, and repair within the Australian Curriculum "
        "General Capabilities (Personal and Social Capability, Ethical Understanding). Set a SMART goal "
        "focused on replacement behaviours (e.g., asking for a break, using a visual signal) and rehearse "
        "these skills during calm moments."
    )
    st.info(rec_text)
    recommendations = st.text_area(
        "Edit recommendations if needed", value=rec_text
    )

    if st.button("💾 Save Critical Incident (Sandbox)"):
        record = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "student_id": quick_incident["student_id"],
            "quick_incident_id": quick_incident["id"],
            "antecedent": antecedent_A,
            "behaviour": behaviour_B,
            "consequence": consequence_C,
            "hypothesis": hypothesis_H,
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
        st.success("Critical Incident saved (Sandbox).")
        with st.expander("View saved record"):
            st.json(record)


# =========================================================
# 10. STUDENT ANALYSIS (DETAILED)
# =========================================================

def render_student_analysis():
    student_id = st.session_state.get("selected_student_id")
    student = get_student(student_id)
    if not student:
        st.error("No student selected.")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis — {student['name']}")
        st.caption(
            f"Program: {student['program']} | Grade: {student['grade']} | EDID: {student['edid']}"
        )
    with col_back:
        if st.button("⬅ Back to Program"):
            go_to("program_students", selected_program=student["program"])

    # Filter incidents for student
    incidents = [
        i
        for i in st.session_state.incidents
        if i["student_id"] == student_id
    ]
    if not incidents:
        st.info("No incidents logged yet for this student.")
        if st.button("📝 Log first incident", type="primary"):
            go_to("incident_log", selected_student_id=student_id)
        return

    df = pd.DataFrame(incidents)

    # Quick vs Critical classification based on severity
    df["incident_type"] = np.where(df["severity"] >= 3, "Critical (≥3)", "Quick (1–2)")

    df["incident_date"] = pd.to_datetime(df["incident_date"], errors="coerce")
    df = df.sort_values("incident_date")

    # Summary metrics
    st.markdown("### Overview")
    total = len(df)
    crit = (df["incident_type"] == "Critical (≥3)").sum()
    avg_sev = df["severity"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", total)
    with col2:
        st.metric("Critical (≥3)", crit)
    with col3:
        st.metric("Avg Severity", f"{avg_sev:.1f}")
    with col4:
        days_span = (
            (df["incident_date"].max() - df["incident_date"].min()).days + 1
        )
        per_week = total / days_span * 7 if days_span > 0 else total
        st.metric("Incidents per Week", f"{per_week:.1f}")

    st.markdown("---")

    # Timeline
    st.subheader("📅 Severity over Time (Quick vs Critical)")
    fig_t = px.scatter(
        df,
        x="incident_date",
        y="severity",
        color="incident_type",
        hover_data=["behaviour_type", "antecedent", "location", "session"],
        title="Incident Severity Over Time",
    )
    fig_t.update_traces(marker=dict(size=10))
    st.plotly_chart(fig_t, use_container_width=True)

    st.markdown("---")

    # Antecedent frequency
    st.subheader("🔥 Antecedent Frequency (Quick vs Critical)")
    if "antecedent" in df.columns:
        ant_counts = (
            df.groupby(["antecedent", "incident_type"])
            .size()
            .reset_index(name="count")
        )
        fig_a = px.bar(
            ant_counts,
            x="count",
            y="antecedent",
            color="incident_type",
            orientation="h",
            barmode="group",
            title="Antecedent Patterns",
        )
        st.plotly_chart(fig_a, use_container_width=True)

    # Location hotspots
    st.subheader("📍 Location Hotspots")
    if "location" in df.columns:
        loc_counts = (
            df.groupby(["location", "incident_type"])
            .size()
            .reset_index(name="count")
        )
        fig_l = px.bar(
            loc_counts,
            x="count",
            y="location",
            color="incident_type",
            orientation="h",
            barmode="group",
            title="Incident Locations (Quick vs Critical)",
        )
        st.plotly_chart(fig_l, use_container_width=True)

    # Behaviour types
    st.subheader("⚠️ Behaviour Types")
    if "behaviour_type" in df.columns:
        beh_counts = (
            df.groupby(["behaviour_type", "incident_type"])
            .size()
            .reset_index(name="count")
        )
        fig_b = px.bar(
            beh_counts,
            x="count",
            y="behaviour_type",
            color="incident_type",
            orientation="h",
            barmode="group",
            title="Behaviours of Concern",
        )
        st.plotly_chart(fig_b, use_container_width=True)

    # Session distribution
    st.subheader("🕒 Session Patterns (Morning / Middle / Afternoon)")
    if "session" in df.columns:
        ses_counts = (
            df.groupby(["session", "incident_type"])
            .size()
            .reset_index(name="count")
        )
        fig_s = px.bar(
            ses_counts,
            x="session",
            y="count",
            color="incident_type",
            barmode="group",
            title="Incidents by Session",
        )
        st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("---")

    # Pattern detection
    st.subheader("🔎 Pattern Detection")

    patterns = []

    if "antecedent" in df.columns and not df["antecedent"].dropna().empty:
        top_ant = df["antecedent"].mode()[0]
        patterns.append(f"Most frequent antecedent: **{top_ant}**")

    if "behaviour_type" in df.columns and not df["behaviour_type"].dropna().empty:
        top_beh = df["behaviour_type"].mode()[0]
        patterns.append(f"Most common behaviour: **{top_beh}**")

    if "location" in df.columns and not df["location"].dropna().empty:
        top_loc = df["location"].mode()[0]
        patterns.append(f"Most frequent location: **{top_loc}**")

    if "session" in df.columns and not df["session"].dropna().empty:
        top_ses = df["session"].mode()[0]
        patterns.append(f"Most common session: **{top_ses}**")

    if "intervention" in df.columns:
        non_blank_int = df["intervention"].replace("", pd.NA).dropna()
        if not non_blank_int.empty:
            top_int = non_blank_int.mode()[0]
            patterns.append(
                f"Most frequently used adult action: **{top_int}** (consider whether this is preventative, co-regulating, or reactive)."
            )

    for p in patterns:
        st.markdown(f"- {p}")

    st.markdown("---")

    # Trauma-informed narrative
    st.subheader("🧠 Trauma-Informed Interpretation")
    ti_text = (
        "The patterns suggest predictable triggers where stress and demands may be exceeding the student's "
        "window of tolerance. Using CPI's model, focus on recognising early escalation and staying in the "
        "Supportive phase for longer (calm tone, space, choice). Berry Street's Body and Relationship pillars "
        "highlight the importance of consistent, regulating routines (movement, sensory breaks) and strong, "
        "predictable relational safety.\n\n"
        "Consider whether classroom expectations, transitions, and environmental factors (noise, crowding) "
        "are appropriately scaffolded for this student. A trauma-informed lens assumes the behaviour is a "
        "communication of need rather than 'defiance'."
    )
    st.info(ti_text)

    # Recommendations
    st.subheader("🎯 Recommendations (BSEM, CPI, SMART, ACARA Capabilities)")
    rec_text = (
        "1. **Proactive supports**:\n"
        "   - Build in predictable check-ins at the times and locations where incidents cluster.\n"
        "   - Use visual schedules, countdowns, and clear pre-corrections before transitions.\n\n"
        "2. **Co-regulation strategies (BSEM Body & Relationship)**:\n"
        "   - Establish brief movement/sensory routines before high-demand tasks.\n"
        "   - Maintain a calm, regulated adult presence; script CPI-aligned supportive language.\n\n"
        "3. **Skill-building (ACARA General Capabilities)**:\n"
        "   - Teach emotional vocabulary and self-advocacy (Personal and Social Capability).\n"
        "   - Use role-play and problem-solving to practise safer responses to triggers (Critical and Creative Thinking).\n\n"
        "4. **SMART goal focus**:\n"
        "   - Set 1–2 specific, measurable goals (e.g., 'When asked to transition, student will use a break card "
        "or ask for help in 4/5 opportunities across 2 weeks').\n"
        "   - Monitor data weekly to review whether adjustments are reducing both quick and critical incidents.\n\n"
        "5. **Team alignment**:\n"
        "   - Ensure all adults use consistent scripts, de-escalation strategies, and follow the same safety plan.\n"
        "   - Share key strategies with home and other key settings where appropriate."
    )
    st.success(rec_text)


# =========================================================
# 11. ROUTER
# =========================================================

def main():
    if not st.session_state.logged_in:
        render_login()
        return

    page = st.session_state.get("current_page", "landing")

    if page == "login":
        render_login()
    elif page == "landing":
        render_landing()
    elif page == "program_students":
        render_program_students()
    elif page == "incident_log":
        render_incident_log()
    elif page == "critical_incident":
        render_critical_incident()
    elif page == "student_analysis":
        render_student_analysis()
    else:
        st.error("Unknown page state.")
        st.session_state.current_page = "landing"


if __name__ == "__main__":
    main()
