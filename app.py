import streamlit as st
import pandas as pd
from datetime import datetime, time
import uuid
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Behaviour Support Sandbox",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)

# =========================
# MOCK DATA (SANDBOX)
# =========================

MOCK_STAFF = [
    {"id": "s1", "name": "Admin Demo",  "role": "ADM", "email": "admin@demo.edu.au"},
    {"id": "s2", "name": "Emily Jones", "role": "JP",  "email": "emily.jones@demo.edu.au"},
    {"id": "s3", "name": "Daniel Lee",  "role": "PY",  "email": "daniel.lee@demo.edu.au"},
]

MOCK_STUDENTS = [
    {"id": "stu_001", "name": "Izack N.",  "grade": "7", "dob": "2012-03-15", "edid": "ED12345", "program": "SY"},
    {"id": "stu_002", "name": "Mia K.",    "grade": "8", "dob": "2011-07-22", "edid": "ED12346", "program": "PY"},
    {"id": "stu_003", "name": "Liam B.",   "grade": "9", "dob": "2010-11-08", "edid": "ED12347", "program": "SY"},
    {"id": "stu_004", "name": "Emma T.",   "grade": "R", "dob": "2017-05-30", "edid": "ED12348", "program": "JP"},
    {"id": "stu_005", "name": "Oliver S.", "grade": "2", "dob": "2015-09-12", "edid": "ED12349", "program": "JP"},
]

BEHAVIOUR_TYPES = [
    "Verbal refusal",
    "Elopement",
    "Property destruction",
    "Aggression (peer)",
    "Aggression (adult)",
    "Other",
]

ANTECEDENTS = [
    "Requested to transition activity",
    "Given instruction / demand",
    "Peer conflict / teasing",
    "Staff attention shifted away",
    "Unstructured time (recess / lunch)",
    "Sensory overload (noise / busy space)",
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
    "Playground",
    "Yard",
    "Excursion",
    "Swimming",
]

# Support types with NO brackets
SUPPORT_TYPES = [
    "1:1 Individual Support",
    "Independent",
    "Small Group",
    "Large Group",
]

VALID_PAGES = [
    "login",
    "landing",
    "program_students",
    "incident_log",
    "critical_incident_abch",
    "student_analysis",
]

# =========================
# SESSION STATE HELPERS
# =========================

def init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    if "students_list" not in st.session_state:
        st.session_state.students_list = MOCK_STUDENTS
    if "staff_list" not in st.session_state:
        st.session_state.staff_list = MOCK_STAFF
    if "incidents" not in st.session_state:
        st.session_state.incidents = []          # quick incidents
    if "abch_records" not in st.session_state:
        st.session_state.abch_records = {}       # incident_id -> rows list
    if "selected_program" not in st.session_state:
        st.session_state.selected_program = "JP"
    if "selected_student_id" not in st.session_state:
        st.session_state.selected_student_id = None
    if "current_incident_id" not in st.session_state:
        st.session_state.current_incident_id = None
    if "abch_rows" not in st.session_state:
        st.session_state.abch_rows = []

def navigate_to(page: str, **kwargs):
    if page not in VALID_PAGES:
        st.error(f"Invalid page: {page}")
        return
    st.session_state.current_page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.experimental_rerun()

def get_student_by_id(student_id: str):
    if not student_id:
        return None
    return next((s for s in st.session_state.students_list if s["id"] == student_id), None)

def get_students_by_program(program: str):
    return [s for s in st.session_state.students_list if s["program"] == program]

def get_active_staff():
    return st.session_state.staff_list

# =========================
# SIMPLE FUNCTION HYPOTHESIS
# =========================

def simple_function_hypothesis(antecedent: str, behaviour: str) -> str:
    """
    Return a very simple function statement:
    'To get/avoid' + tangible / request / activity / sensory / attention.
    """
    text = (antecedent or "").lower() + " " + (behaviour or "").lower()

    direction = "To get"
    function = "attention"

    if "transition" in text or "work" in text or "task" in text:
        direction = "To avoid"
        function = "activity"
    elif "instruction" in text or "demand" in text or "request" in text:
        direction = "To avoid"
        function = "request"
    elif "sensory" in text or "noise" in text or "busy" in text:
        direction = "To avoid"
        function = "sensory"
    elif any(word in text for word in ["preferred", "item", "device", "game"]):
        direction = "To get"
        function = "tangible"
    elif "peer" in text or "teasing" in text:
        direction = "To get"
        function = "attention"

    return f"{direction} {function}"

# =========================
# AUTH (SANDBOX)
# =========================

def verify_login(email: str):
    """
    Very simple sandbox login:
    - If email matches a mock staff, use that.
    - Otherwise, log in as Admin Demo.
    """
    if not email:
        return None
    email_clean = email.strip().lower()
    for s in MOCK_STAFF:
        if s["email"].lower() == email_clean:
            return s
    return MOCK_STAFF[0]

# =========================
# PAGES
# =========================

def render_login_page():
    st.markdown("## Behaviour Support & Data Analysis — **SANDBOX**")
    st.caption("Demo mode only. Use any email to log in. No real student data is stored.")

    email = st.text_input("Email address", value="admin@demo.edu.au")

    if st.button("Login", type="primary"):
        staff_member = verify_login(email)
        if staff_member:
            st.session_state.logged_in = True
            st.session_state.current_user = staff_member
            st.session_state.current_page = "landing"
            st.experimental_rerun()
        else:
            st.error("Email not recognised.")

def render_landing_page():
    user = st.session_state.current_user or {}
    col_user, col_logout = st.columns([4, 1])

    with col_user:
        st.markdown(f"### 👋 Welcome, {user.get('name', 'User')} — SANDBOX")
        st.caption(f"Role: {user.get('role', 'N/A')} | {user.get('email', 'demo')}")

    with col_logout:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = "login"
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("### 📚 Select Program")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Junior Primary (R–2)**")
        if st.button("Enter JP", use_container_width=True):
            navigate_to("program_students", selected_program="JP")
    with col2:
        st.markdown("**Primary Years (3–6)**")
        if st.button("Enter PY", use_container_width=True):
            navigate_to("program_students", selected_program="PY")
    with col3:
        st.markdown("**Senior Years (7–12)**")
        if st.button("Enter SY", use_container_width=True):
            navigate_to("program_students", selected_program="SY")

def render_program_students():
    program = st.session_state.get("selected_program", "JP")

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"Students — {program} (Sandbox)")
    with col_back:
        if st.button("Back to Home"):
            navigate_to("landing")

    st.markdown("---")

    students = get_students_by_program(program)
    if not students:
        st.info("No students in this program (sandbox).")
        return

    cols_per_row = 3
    for i in range(0, len(students), cols_per_row):
        cols = st.columns(cols_per_row)
        for idx, student in enumerate(students[i:i + cols_per_row]):
            with cols[idx]:
                st.markdown(f"#### {student['name']}")
                st.caption(f"Grade {student['grade']} | EDID {student['edid']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Analysis", key=f"an_{student['id']}"):
                        navigate_to("student_analysis", selected_student_id=student["id"])
                with col_b:
                    if st.button("Log Incident", key=f"log_{student['id']}"):
                        navigate_to("incident_log", selected_student_id=student["id"])

def render_incident_log():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not student:
        st.error("No student selected.")
        if st.button("Back to Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"Incident Log — {student['name']}")
        st.caption(f"Program {student['program']} | Grade {student['grade']}")
    with col_back:
        if st.button("Back"):
            navigate_to("program_students")

    st.markdown("---")

    submitted = False
    with st.form("incident_form"):
        col1, col2 = st.columns(2)

        with col1:
            incident_date = st.date_input("Date of incident", datetime.now())
            incident_time = st.time_input("Time of incident", datetime.now().time())
            location = st.selectbox("Location", LOCATIONS)

        with col2:
            behaviour_type = st.selectbox("Behaviour type", BEHAVIOUR_TYPES)
            antecedent = st.selectbox("Antecedent (trigger)", ANTECEDENTS)
            support_type = st.selectbox("Type of support", SUPPORT_TYPES)

        st.markdown("### Reporter")
        reporter_name = (st.session_state.current_user or {}).get("name", "Unknown")
        st.info(f"Staff member reporting (auto): **{reporter_name}**")

        st.markdown("### Additional staff involved")
        staff_names = [s["name"] for s in get_active_staff()]
        additional_staff = st.multiselect("Select additional staff", staff_names)

        st.markdown("### Adult action / intervention used")
        intervention = st.text_input(
            "What did adults do that helped / attempted to help?",
            placeholder="e.g., Offered break, used calm tone, removed peers...",
        )

        severity = st.slider("Severity level (1 = low, 5 = critical)", 1, 5, 2)

        description = st.text_area(
            "Short factual description",
            placeholder="Brief description of what occurred (no analysis here).",
        )

        # Simple function hypothesis preview
        function_guess = simple_function_hypothesis(antecedent, behaviour_type)
        st.markdown("### Hypothesis – Best Guess of Behaviour Function")
        st.caption("Simple function statement used later in ABCH.")
        hypothesis = st.text_input(
            "Function (editable)",
            value=function_guess,
        )

        submitted = st.form_submit_button("Submit incident", type="primary")

    if submitted:
        incident_id = str(uuid.uuid4())
        incident_time_str = incident_time.strftime("%H:%M:%S")

        new_incident = {
            "id": incident_id,
            "student_id": student_id,
            "student_name": student["name"],
            "incident_date": incident_date.strftime("%Y-%m-%d"),
            "incident_time": incident_time_str,
            "day_of_week": incident_date.strftime("%A"),
            "location": location,
            "behaviour_type": behaviour_type,
            "antecedent": antecedent,
            "severity": severity,
            "support_type": support_type,
            "reported_by": reporter_name,
            "additional_staff": additional_staff,
            "intervention": intervention,
            "description": description,
            "session": "Morning" if incident_time < time(11, 0) else "Afternoon",
            "is_critical": severity >= 3,
            "function_hypothesis": hypothesis,
        }

        st.session_state.incidents.append(new_incident)
        st.success("Incident saved (sandbox).")

        if severity >= 3:
            st.warning("Severity ≥3 recorded as critical — opening ABCH form.")
            # Pre-populate ABCH rows from this incident
            st.session_state.current_incident_id = incident_id
            st.session_state.abch_rows = [{
                "location": location,
                "context": antecedent,
                "time": incident_time_str[:5],
                "behaviour": behaviour_type,
                "consequence": "",
                "hypothesis": hypothesis,
            }]
            navigate_to("critical_incident_abch", selected_student_id=student_id)
        else:
            navigate_to("program_students")

def render_critical_incident_abch():
    incident_id = st.session_state.get("current_incident_id")
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not incident_id or not student:
        st.error("No critical incident selected.")
        if st.button("Back to Home"):
            navigate_to("landing")
        return

    incident = next((i for i in st.session_state.incidents if i["id"] == incident_id), None)

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"Critical Incident ABCH — {student['name']}")
        st.caption(f"Linked to incident on {incident.get('incident_date')} at {incident.get('incident_time')}")
    with col_back:
        if st.button("Back"):
            navigate_to("program_students")

    st.markdown("---")
    st.markdown("### ABCH Table")
    st.caption("Add extra lines if the incident involved multiple phases or locations.")

    rows = st.session_state.abch_rows or []

    # Render each ABCH row
    for idx, row in enumerate(rows):
        st.markdown(f"#### Row {idx + 1}")
        c1, c2, c3, c4, c5, c6 = st.columns([1.2, 2, 1, 2, 2, 2])

        with c1:
            rows[idx]["location"] = st.text_input("Location", value=row["location"], key=f"abch_loc_{idx}")
        with c2:
            rows[idx]["context"] = st.text_area(
                "Context (what was happening before?)",
                value=row["context"],
                key=f"abch_ctx_{idx}",
                height=80,
            )
        with c3:
            rows[idx]["time"] = st.text_input("Time", value=row["time"], key=f"abch_time_{idx}")
        with c4:
            rows[idx]["behaviour"] = st.text_area(
                "Behaviour (observed only)",
                value=row["behaviour"],
                key=f"abch_beh_{idx}",
                height=80,
            )
        with c5:
            rows[idx]["consequence"] = st.text_area(
                "Consequences (what happened after? how did people react?)",
                value=row["consequence"],
                key=f"abch_con_{idx}",
                height=80,
            )
        with c6:
            rows[idx]["hypothesis"] = st.text_input(
                "Function (To get/avoid tangible/request/activity/sensory/attention)",
                value=row["hypothesis"],
                key=f"abch_hyp_{idx}",
            )

        st.markdown("---")

    st.session_state.abch_rows = rows

    col_add, col_save = st.columns([1, 2])

    with col_add:
        if st.button("➕ Add another line"):
            st.session_state.abch_rows.append(
                {
                    "location": incident.get("location", ""),
                    "context": incident.get("antecedent", ""),
                    "time": incident.get("incident_time", "")[:5],
                    "behaviour": incident.get("behaviour_type", ""),
                    "consequence": "",
                    "hypothesis": simple_function_hypothesis(
                        incident.get("antecedent", ""),
                        incident.get("behaviour_type", "")
                    ),
                }
            )
            st.experimental_rerun()

    with col_save:
        if st.button("💾 Save critical ABCH"):
            st.session_state.abch_records[incident_id] = st.session_state.abch_rows
            st.success("Critical ABCH saved in sandbox memory.")
            if st.button("Return to student analysis"):
                navigate_to("student_analysis", selected_student_id=student_id)

def render_student_analysis():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not student:
        st.error("No student selected.")
        if st.button("Back to Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"Analysis — {student['name']}")
    with col_back:
        if st.button("Back"):
            navigate_to("program_students")

    st.markdown("---")

    incidents = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    if not incidents:
        st.info("No incidents yet for this student in sandbox.")
        if st.button("Log first incident"):
            navigate_to("incident_log", selected_student_id=student_id)
        return

    df = pd.DataFrame(incidents)

    # Summary metrics
    st.markdown("### Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total incidents", len(df))
    with col2:
        st.metric("Critical incidents (≥3)", int(df["is_critical"].sum()))
    with col3:
        st.metric("Average severity", round(df["severity"].mean(), 1))
    with col4:
        st.metric("Distinct locations", df["location"].nunique())

    # Timeline
    st.markdown("---")
    st.markdown("### Timeline (severity over time)")
    df["date"] = pd.to_datetime(df["incident_date"])
    fig = px.scatter(
        df,
        x="date",
        y="severity",
        color="is_critical",
        color_discrete_map={True: "red", False: "blue"},
        hover_data=["behaviour_type", "antecedent", "location"],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Antecedent patterns
    st.markdown("---")
    st.markdown("### Antecedent patterns")
    ant_counts = df["antecedent"].value_counts().reset_index()
    ant_counts.columns = ["Antecedent", "Count"]
    fig2 = px.bar(ant_counts, x="Count", y="Antecedent", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)

    # Location patterns
    st.markdown("---")
    st.markdown("### Location patterns")
    loc_counts = df["location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig3 = px.bar(loc_counts, x="Count", y="Location", orientation="h")
    st.plotly_chart(fig3, use_container_width=True)

    # Behaviour types: quick vs critical
    st.markdown("---")
    st.markdown("### Behaviour types (quick vs critical)")
    df["incident_type"] = df["is_critical"].map({True: "Critical", False: "Quick"})
    beh_counts = df.groupby(["behaviour_type", "incident_type"]).size().reset_index(name="Count")
    fig4 = px.bar(
        beh_counts,
        x="Count",
        y="behaviour_type",
        color="incident_type",
        barmode="group",
        orientation="h",
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Function hypotheses
    st.markdown("---")
    st.markdown("### Function hypotheses used")
    func_counts = df["function_hypothesis"].value_counts().reset_index()
    func_counts.columns = ["Function", "Count"]
    fig5 = px.bar(func_counts, x="Count", y="Function", orientation="h")
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown("### Trauma-informed interpretation (narrative)")
    st.info(
        "Use these patterns to plan proactive supports: predict transition times, pre-teach expectations, "
        "and embed co-regulation strategies drawn from Berry Street Education Model and CPI Supportive stance. "
        "Link adjustments to the Australian Curriculum General Capabilities (Personal & Social Capability), "
        "focusing on self-regulation, help-seeking and relationship skills."
    )

# =========================
# MAIN
# =========================

def main():
    init_state()

    if not st.session_state.logged_in:
        render_login_page()
        return

    page = st.session_state.current_page

    if page == "landing":
        render_landing_page()
    elif page == "program_students":
        render_program_students()
    elif page == "incident_log":
        render_incident_log()
    elif page == "critical_incident_abch":
        render_critical_incident_abch()
    elif page == "student_analysis":
        render_student_analysis()
    else:
        render_landing_page()

if __name__ == "__main__":
    main()
