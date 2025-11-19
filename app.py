import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
import random
import uuid
import plotly.express as px
from typing import List, Dict, Any, Optional
import logging
from functools import wraps

# ---------------------------------------------------------------------
# 0. BASIC CONFIG + LOGGING
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Behaviour Support & Data Analysis - SANDBOX",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# 1. ERROR HANDLING DECORATOR
# ---------------------------------------------------------------------


class AppError(Exception):
    def __init__(self, message: str, user_message: Optional[str] = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(message)


class ValidationError(AppError):
    pass


def handle_errors(user_message: str = "An error occurred"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{func.__name__}: {e.message}", exc_info=True)
                st.error(e.user_message)
            except Exception as e:
                logger.critical(
                    f"Unexpected error in {func.__name__}: {e}", exc_info=True
                )
                st.error(f"{user_message}.")
                with st.expander("Error details"):
                    st.code(repr(e))
        return wrapper
    return decorator


# ---------------------------------------------------------------------
# 2. CONSTANTS / OPTIONS
# ---------------------------------------------------------------------

VALID_PAGES = [
    "login",
    "landing",
    "program_students",
    "direct_log_form",
    "critical_incident_abch",
    "student_analysis",
    "admin_portal",
]

PROGRAM_OPTIONS = ["JP", "PY", "SY"]
GRADE_OPTIONS = {
    "JP": ["R", "Y1", "Y2"],
    "PY": ["Y3", "Y4", "Y5", "Y6"],
    "SY": ["Y7", "Y8", "Y9", "Y10", "Y11", "Y12"],
}

behaviourS_FBA = [
    "Verbal Refusal",
    "Elopement",
    "Property Destruction",
    "Aggression (Peer)",
    "Physical Aggression (Staff)",
    "Other - Specify",
]

ANTECEDENTS_NEW = [
    "Requested to transition activity",
    "Given instruction/demand (Academic)",
    "Given instruction/demand (Non-Academic)",
    "Peer conflict/Teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory over-stimulation (Noise/Lights)",
    "Access to preferred item/activity denied",
]

INTERVENTIONS = [
    "Prompted use of coping skill (e.g., breathing)",
    "Proximity control / non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break / choice of task",
    "Used planned ignoring of minor behaviour",
    "Staff de-escalation script / verbal coaching",
    "Removed other students from area for safety",
    "Called for staff support / backup",
]

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class / assembly)",
]

LOCATIONS = [
    "--- Select Location ---",
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
    "Van/Kia",
    "Swimming",
    "Yard",
    "Playground",
    "Toilets",
    "Excursion",
    "Other",
]


# ---------------------------------------------------------------------
# 3. MOCK DATA GENERATION (SANDBOX)
# ---------------------------------------------------------------------


def generate_mock_students() -> List[Dict[str, Any]]:
    students = [
        # JP
        {
            "id": "student_JP001",
            "name": "Emma Thompson",
            "grade": "R",
            "dob": "2018-03-15",
            "edid": "JP001",
            "program": "JP",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_JP002",
            "name": "Oliver Martinez",
            "grade": "Y1",
            "dob": "2017-07-22",
            "edid": "JP002",
            "program": "JP",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_JP003",
            "name": "Sophia Wilson",
            "grade": "Y2",
            "dob": "2016-11-08",
            "edid": "JP003",
            "program": "JP",
            "profile_status": "Complete",
            "archived": False,
        },
        # PY
        {
            "id": "student_PY001",
            "name": "Liam Chen",
            "grade": "Y3",
            "dob": "2015-05-30",
            "edid": "PY001",
            "program": "PY",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_PY002",
            "name": "Ava Rodriguez",
            "grade": "Y4",
            "dob": "2014-09-12",
            "edid": "PY002",
            "program": "PY",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_PY003",
            "name": "Noah Brown",
            "grade": "Y6",
            "dob": "2012-01-25",
            "edid": "PY003",
            "program": "PY",
            "profile_status": "Complete",
            "archived": False,
        },
        # SY
        {
            "id": "student_SY001",
            "name": "Isabella Garcia",
            "grade": "Y7",
            "dob": "2011-04-17",
            "edid": "SY001",
            "program": "SY",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_SY002",
            "name": "Ethan Davis",
            "grade": "Y9",
            "dob": "2009-12-03",
            "edid": "SY002",
            "program": "SY",
            "profile_status": "Complete",
            "archived": False,
        },
        {
            "id": "student_SY003",
            "name": "Mia Anderson",
            "grade": "Y11",
            "dob": "2007-08-20",
            "edid": "SY003",
            "program": "SY",
            "profile_status": "Complete",
            "archived": False,
        },
    ]
    return students


def generate_mock_staff() -> List[Dict[str, Any]]:
    staff = [
        {
            "id": "staff_1",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@demo.edu.au",
            "role": "JP",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_2",
            "name": "Michael Lee",
            "email": "michael.lee@demo.edu.au",
            "role": "PY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_3",
            "name": "Jessica Williams",
            "email": "jessica.williams@demo.edu.au",
            "role": "SY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_4",
            "name": "Admin Demo",
            "email": "admin@demo.edu.au",
            "role": "ADM",
            "active": True,
            "archived": False,
        },
    ]
    return staff


def _session_window_for_time(t: time) -> str:
    if time(9, 0) <= t <= time(11, 0):
        return "Morning (9:00–11:00)"
    if time(11, 0, 1) <= t <= time(13, 0):
        return "Middle (11:01–13:00)"
    if time(13, 0, 1) <= t <= time(14, 45):
        return "Afternoon (13:01–14:45)"
    return "Outside School Hours"


def generate_mock_incidents(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Generate ~70 incidents over last 90 days
    incidents: List[Dict[str, Any]] = []
    staff_names = [s["name"] for s in generate_mock_staff()]
    student_ids = [s["id"] for s in students]
    base_date = datetime.now().date() - timedelta(days=90)

    for _ in range(70):
        student_id = random.choice(student_ids)
        student_name = next(s["name"] for s in students if s["id"] == student_id)

        day_offset = random.randint(0, 85)
        inc_date = base_date + timedelta(days=day_offset)
        hour = random.choices([9, 10, 11, 12, 13, 14], [2, 3, 2, 1, 2, 3])[0]
        minute = random.randint(0, 59)
        inc_time = time(hour, minute)

        behaviour_type = random.choice(behaviourS_FBA[:-1])
        severity = random.choices([1, 2, 3, 4, 5], [4, 3, 2, 1, 0.5])[0]
        is_critical = severity >= 3  # SANDBOX rule: 3+ is critical
        incident_type = "Critical" if is_critical else "Quick"

        antecedent = random.choice(ANTECEDENTS_NEW)
        intervention = random.choice(INTERVENTIONS)
        location = random.choice(LOCATIONS[1:])
        session = _session_window_for_time(inc_time)

        # Adult response outcome (for analysis)
        outcome = random.choices(
            ["De-escalated", "Partially helped", "Escalated"],
            [0.55, 0.25, 0.2],
        )[0]

        incidents.append(
            {
                "id": str(uuid.uuid4()),
                "student_id": student_id,
                "student_name": student_name,
                "date": inc_date.strftime("%Y-%m-%d"),
                "time": inc_time.strftime("%H:%M"),
                "day": inc_date.strftime("%A"),
                "session": session,
                "location": location,
                "behaviour_type": behaviour_type,
                "antecedent": antecedent,
                "intervention": intervention,
                "support_type": random.choice(SUPPORT_TYPES),
                "severity": severity,
                "is_critical": is_critical,
                "incident_type": incident_type,
                "reported_by_name": random.choice(staff_names),
                "adult_outcome": outcome,  # for "what worked best"
                # ABCH & Outcome fields start empty (can be filled in form)
                "abch_location": "",
                "abch_context": "",
                "abch_time": "",
                "abch_behaviour_desc": "",
                "abch_consequence": "",
                "abch_hypothesis": "",
                "sapol_flags": [],
                "ambulance_flags": [],
                "internal_responses": [],
                "notifications": [],
                "admin_notes": "",
            }
        )

    return incidents


# ---------------------------------------------------------------------
# 4. SESSION STATE INITIALISATION
# ---------------------------------------------------------------------


def init_session_state():
    if "data_loaded" not in st.session_state:
        st.session_state.students_list = generate_mock_students()
        st.session_state.staff_list = generate_mock_staff()
        st.session_state.incidents = generate_mock_incidents(
            st.session_state.students_list
        )
        st.session_state.data_loaded = True

    st.session_state.setdefault("current_page", "login")
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("current_user", None)
    st.session_state.setdefault("selected_student_id", None)
    st.session_state.setdefault("current_incident_id", None)


# ---------------------------------------------------------------------
# 5. GENERIC HELPERS
# ---------------------------------------------------------------------


def navigate_to(
    page: str,
    student_id: Optional[str] = None,
    program: Optional[str] = None,
    incident_id: Optional[str] = None,
):
    if page not in VALID_PAGES:
        raise ValidationError("Invalid page", "Cannot navigate to requested page")
    st.session_state.current_page = page
    if student_id:
        st.session_state.selected_student_id = student_id
    if program:
        st.session_state.selected_program = program
    if incident_id:
        st.session_state.current_incident_id = incident_id
    st.experimental_rerun()


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    return next(
        (s for s in st.session_state.students_list if s["id"] == student_id), None
    )


def get_active_staff() -> List[Dict[str, Any]]:
    return [s for s in st.session_state.staff_list if s["active"] and not s["archived"]]


def calculate_age(dob_str: str) -> str:
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        return str(age)
    except Exception:
        return "N/A"


def get_students_by_program(program: str, include_archived: bool = False):
    students = [s for s in st.session_state.students_list if s["program"] == program]
    if not include_archived:
        students = [s for s in students if not s["archived"]]
    return students


# ---------------------------------------------------------------------
# 6. VALIDATION
# ---------------------------------------------------------------------


def validate_incident_form(
    location, reported_by, behaviour_type, severity_level, incident_date, incident_time
):
    errors = []
    if location == "--- Select Location ---":
        errors.append("Select a Location")
    if not isinstance(reported_by, dict) or not reported_by.get("id"):
        errors.append("Select a staff member")
    if behaviour_type == "--- Select behaviour ---":
        errors.append("Select a behaviour")
    if not (1 <= severity_level <= 5):
        errors.append("Severity must be 1–5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")
    if errors:
        raise ValidationError("Incident validation failed", ", ".join(errors))


def validate_abch_form(location, context, behaviour, consequence, hypothesis):
    errors = []
    if not location.strip():
        errors.append("ABCH Location is required")
    if not context.strip():
        errors.append("Context is required")
    if not behaviour.strip():
        errors.append("Behaviour description is required")
    if not consequence.strip():
        errors.append("Consequences are required")
    if not hypothesis.strip():
        errors.append("Hypothesis is required")
    if errors:
        raise ValidationError("ABCH validation failed", ", ".join(errors))


# ---------------------------------------------------------------------
# 7. AUTH (SANDBOX – VERY SIMPLE)
# ---------------------------------------------------------------------


def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    email = (email or "").strip().lower()
    if not email or not password:
        return None
    # SANDBOX RULE: any mock staff email + password "demo"
    if password != "demo":
        return None
    return next(
        (s for s in st.session_state.staff_list if s["email"].lower() == email), None
    )


# ---------------------------------------------------------------------
# 8. UI COMPONENTS
# ---------------------------------------------------------------------


def render_staff_selector(label: str, key: str):
    staff = get_active_staff()
    options = [{"id": None, "name": "--- Select Staff ---", "role": None}]
    options += staff
    selected = st.selectbox(
        label,
        options=options,
        format_func=lambda x: x["name"],
        key=key,
    )
    return selected


# ---------------------------------------------------------------------
# 9. PAGES
# ---------------------------------------------------------------------


@handle_errors("Unable to load login page")
def render_login_page():
    st.markdown(
        """
    <div style="text-align:center; padding:2rem;">
      <h1>🔐 Behaviour Support & Data Analysis</h1>
      <p>Sandbox demo – use any demo staff email and password <b>demo</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            email = st.text_input(
                "Email", placeholder="sarah.johnson@demo.edu.au", key="login_email"
            )
            password = st.text_input(
                "Password", type="password", value="", placeholder="demo"
            )
            if st.button("Login", type="primary", use_container_width=True):
                user = verify_login(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.session_state.current_page = "landing"
                    st.success(f"Welcome {user['name']}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials (hint: password is 'demo').")


@handle_errors("Unable to load landing page")
def render_landing_page():
    user = st.session_state.get("current_user", {})
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.markdown(f"### 👋 Welcome, {user.get('name','User')}")
        st.caption(f"Role: {user.get('role','N/A')} | {user.get('email','')}")
    with col_logout:
        st.markdown("##")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_page = "login"
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("### 📚 Select Program")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎨 Junior Primary (R–2)")
        if st.button("Enter JP", use_container_width=True):
            navigate_to("program_students", program="JP")
    with col2:
        st.markdown("#### 📖 Primary Years (3–6)")
        if st.button("Enter PY", use_container_width=True):
            navigate_to("program_students", program="PY")
    with col3:
        st.markdown("#### 🎓 Senior Years (7–12)")
        if st.button("Enter SY", use_container_width=True):
            navigate_to("program_students", program="SY")

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown("#### 📝 Quick Incident Log")
        all_students = [
            s for s in st.session_state.students_list if not s["archived"]
        ]
        options = [{"id": None, "name": "--- Select Student ---"}] + all_students
        student = st.selectbox(
            "Select student",
            options=options,
            format_func=lambda x: x["name"],
            label_visibility="collapsed",
            key="quick_student",
        )
        if student and student["id"]:
            if st.button("Start Quick Log", type="primary", use_container_width=True):
                navigate_to("direct_log_form", student_id=student["id"])
    with col_q2:
        st.markdown("#### 🔐 Admin Portal (sandbox)")
        if st.button("Open Admin Portal", use_container_width=True):
            navigate_to("admin_portal")


@handle_errors("Unable to load program student list")
def render_program_students():
    program = st.session_state.get("selected_program", "JP")
    program_names = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"{program_names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("landing")

    st.markdown("---")
    tab_current, tab_archived = st.tabs(["Current", "Archived"])

    with tab_current:
        students = get_students_by_program(program, include_archived=False)
        if not students:
            st.info("No current students.")
        else:
            cols_per_row = 3
            for i in range(0, len(students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, student in enumerate(students[i : i + cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {student['name']}")
                            st.caption(
                                f"Grade: {student['grade']} • EDID: {student['edid']}"
                            )
                            count = len(
                                [
                                    inc
                                    for inc in st.session_state.incidents
                                    if inc["student_id"] == student["id"]
                                ]
                            )
                            st.metric("Incidents", count)
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button(
                                    "View",
                                    key=f"view_{student['id']}",
                                    use_container_width=True,
                                ):
                                    navigate_to(
                                        "student_analysis", student_id=student["id"]
                                    )
                            with col_log:
                                if st.button(
                                    "Log",
                                    key=f"log_{student['id']}",
                                    use_container_width=True,
                                ):
                                    navigate_to(
                                        "direct_log_form", student_id=student["id"]
                                    )

    with tab_archived:
        students = get_students_by_program(program, include_archived=True)
        students = [s for s in students if s["archived"]]
        if not students:
            st.info("No archived students.")
        else:
            for s in students:
                with st.expander(f"{s['name']} (Grade {s['grade']})"):
                    st.write(f"EDID: {s['edid']}")
                    cnt = len(
                        [
                            inc
                            for inc in st.session_state.incidents
                            if inc["student_id"] == s["id"]
                        ]
                    )
                    st.metric("Incidents", cnt)
                    if st.button(
                        "View analysis", key=f"view_arch_{s['id']}"
                    ):
                        navigate_to("student_analysis", student_id=s["id"])


@handle_errors("Unable to load admin portal")
def render_admin_portal():
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal (Sandbox)")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("landing")

    st.markdown("---")
    st.info("In sandbox mode this is read-only – students/staff are preloaded.")


# -------------------------- INCIDENT LOG FORM -------------------------


@handle_errors("Unable to load incident form")
def render_direct_log_form():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found.")
        if st.button("Back to home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log – {student['name']}")
        st.caption(f"{student['program']} • Grade {student['grade']}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student["program"])

    st.markdown("---")

    with st.form("incident_form"):
        col1, col2 = st.columns(2)
        with col1:
            inc_date = st.date_input(
                "Date of incident", value=date.today(), format="DD/MM/YYYY"
            )
            inc_time = st.time_input("Time of incident", value=datetime.now().time())
            location = st.selectbox("Location", LOCATIONS)
        with col2:
            st.markdown("**Reported by**")
            reported_by = render_staff_selector(
                "Staff member", key="incident_staff_selector"
            )

        st.markdown("### Behaviour information")
        col3, col4 = st.columns(2)
        with col3:
            behaviour_type = st.selectbox(
                "Behaviour type",
                options=["--- Select behaviour ---"] + behaviourS_FBA,
            )
            antecedent = st.selectbox("Antecedent", options=ANTECEDENTS_NEW)
        with col4:
            intervention = st.selectbox("Intervention used", options=INTERVENTIONS)
            support_type = st.selectbox("Support type", options=SUPPORT_TYPES)

        severity = st.slider("Severity (1 = low, 5 = high risk)", 1, 5, 2)
        description = st.text_area(
            "Additional description (optional)",
            placeholder="Briefly describe the incident...",
        )

        submitted = st.form_submit_button(
            "Submit incident report", type="primary", use_container_width=True
        )

        if submitted:
            validate_incident_form(
                location,
                reported_by,
                behaviour_type,
                severity,
                inc_date,
                inc_time,
            )

            session = _session_window_for_time(inc_time)
            is_critical = severity >= 3
            incident_type = "Critical" if is_critical else "Quick"

            new_incident = {
                "id": str(uuid.uuid4()),
                "student_id": student_id,
                "student_name": student["name"],
                "date": inc_date.strftime("%Y-%m-%d"),
                "time": inc_time.strftime("%H:%M"),
                "day": inc_date.strftime("%A"),
                "session": session,
                "location": location,
                "reported_by_name": reported_by["name"],
                "behaviour_type": behaviour_type,
                "antecedent": antecedent,
                "intervention": intervention,
                "support_type": support_type,
                "severity": severity,
                "is_critical": is_critical,
                "incident_type": incident_type,
                "adult_outcome": "De-escalated",
                "description": description,
                # Empty ABCH/outcome details (to be filled in critical form)
                "abch_location": "",
                "abch_context": "",
                "abch_time": "",
                "abch_behaviour_desc": "",
                "abch_consequence": "",
                "abch_hypothesis": "",
                "sapol_flags": [],
                "ambulance_flags": [],
                "internal_responses": [],
                "notifications": [],
                "admin_notes": "",
            }

            st.session_state.incidents.append(new_incident)

            if is_critical:
                st.success("Incident saved and flagged as CRITICAL.")
                st.info(
                    "Because severity is 3 or above, the Critical Incident ABCH form will now open."
                )
                navigate_to(
                    "critical_incident_abch",
                    student_id=student_id,
                    incident_id=new_incident["id"],
                )
            else:
                st.success("Incident saved as a quick incident.")
                col_again, col_back2 = st.columns(2)
                with col_again:
                    if st.button("Log another incident", use_container_width=True):
                        st.experimental_rerun()
                with col_back2:
                    if st.button("Back to student list", use_container_width=True):
                        navigate_to(
                            "program_students", program=student["program"]
                        )


# -------------------- CRITICAL INCIDENT ABCH FORM ---------------------


@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    student_id = st.session_state.get("selected_student_id")
    incident_id = st.session_state.get("current_incident_id")
    student = get_student_by_id(student_id)
    incident = next(
        (i for i in st.session_state.incidents if i["id"] == incident_id), None
    )

    if not student or not incident:
        st.error("Critical incident not found.")
        if st.button("Back to home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"🚨 Critical Incident ABCH – {student['name']}")
        st.caption(
            f"{incident['date']} at {incident['time']} • "
            f"{incident['location']} • Severity {incident['severity']}"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("student_analysis", student_id=student_id)

    st.markdown("---")
    st.markdown("### ABCH Summary (One line for this critical incident)")

    with st.form("abch_form"):
        # ABCH headline row – mirrors your table
        col_loc, col_ctx, col_time, col_beh, col_cons, col_hyp = st.columns(
            [1.2, 2.5, 0.8, 2.2, 2.2, 2.1]
        )
        with col_loc:
            abch_location = st.text_input(
                "Location", value=incident.get("abch_location", "")
            )
        with col_ctx:
            abch_context = st.text_area(
                "Context (what was happening before?)",
                value=incident.get("abch_context", ""),
                height=80,
            )
        with col_time:
            abch_time = st.text_input(
                "Time", value=incident.get("abch_time", incident["time"])
            )
        with col_beh:
            abch_behaviour_desc = st.text_area(
                "Behaviour (observed)",
                value=incident.get("abch_behaviour_desc", ""),
                height=80,
            )
        with col_cons:
            abch_consequence = st.text_area(
                "Consequences (what happened after / how did people react?)",
                value=incident.get("abch_consequence", ""),
                height=80,
            )
        with col_hyp:
            abch_hypothesis = st.text_area(
                "Hypothesis – best guess of function "
                "(to get / avoid • tangible • task • sensory • attention)",
                value=incident.get("abch_hypothesis", ""),
                height=80,
            )

        st.markdown("---")
        st.markdown("### Intended Outcomes vs Actual Outcomes")

        st.markdown("#### Emergency Services")
        col_sapol, col_ambulance, col_rep = st.columns([2, 2, 1.5])
        sapol_options = [
            "Drug possession",
            "Assault",
            "Absconding",
            "Removal",
            "Call out",
            "Stealing",
            "Vandalism",
        ]
        ambulance_options = ["Call out", "Taken to hospital"]

        with col_sapol:
            sapol_flags = st.multiselect(
                "SAPOL", sapol_options, default=incident.get("sapol_flags", [])
            )
        with col_ambulance:
            ambulance_flags = st.multiselect(
                "SA Ambulance Services",
                ambulance_options,
                default=incident.get("ambulance_flags", []),
            )
        with col_rep:
            report_number = st.text_input("Report number (if applicable)", value="")

        st.markdown("#### Incident Internally Managed")
        internal_options = [
            "Restorative session",
            "Community service (age appropriate)",
            "Re-entry meeting / plan",
            "Case review",
            "Make-up time (class work)",
            "Other follow-up",
        ]
        internal_responses = st.multiselect(
            "Internal responses", internal_options, default=incident.get("internal_responses", [])
        )

        st.markdown("#### Notifications / Follow-Up")
        notify_options = [
            "Line manager notified",
            "Parent / caregiver notified",
            "ED155: Staff injury submitted",
            "ED155: Student injury submitted",
            "Copy of critical incident in student file",
        ]
        notifications = st.multiselect(
            "Notifications / records",
            notify_options,
            default=incident.get("notifications", []),
        )

        st.markdown("### Administration only")
        col_lm, col_mgr = st.columns(2)
        with col_lm:
            lm_sig = st.text_input("Line manager name / signature")
        with col_mgr:
            mgr_sig = st.text_input("Manager name / signature")

        safety_plan = st.text_area(
            "Safety & Risk Plan – to be developed / reviewed",
            placeholder="Outline any changes to supervision, environment, routines, or individual safety plan.",
            height=100,
        )
        other_outcomes = st.text_area(
            "Other outcomes to be pursued by Cowandilla Learning Centre Management",
            height=100,
        )

        admin_notes = (
            f"Line Manager: {lm_sig}\n"
            f"Manager: {mgr_sig}\n\n"
            f"Safety/Risk Plan:\n{safety_plan}\n\n"
            f"Other outcomes:\n{other_outcomes}"
        )

        submitted = st.form_submit_button(
            "Save critical incident summary", type="primary"
        )

        if submitted:
            validate_abch_form(
                abch_location, abch_context, abch_behaviour_desc, abch_consequence, abch_hypothesis
            )
            # update incident in session_state
            incident.update(
                {
                    "abch_location": abch_location,
                    "abch_context": abch_context,
                    "abch_time": abch_time,
                    "abch_behaviour_desc": abch_behaviour_desc,
                    "abch_consequence": abch_consequence,
                    "abch_hypothesis": abch_hypothesis,
                    "sapol_flags": sapol_flags,
                    "ambulance_flags": ambulance_flags,
                    "internal_responses": internal_responses,
                    "notifications": notifications,
                    "admin_notes": admin_notes,
                    "report_number": report_number,
                }
            )
            st.success("Critical incident ABCH details saved.")
            if st.button("Go to student analysis", use_container_width=True):
                navigate_to("student_analysis", student_id=student_id)


# --------------------------- STUDENT ANALYSIS -------------------------


@handle_errors("Unable to load student analysis")
def render_student_analysis():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found.")
        if st.button("Back to home"):
            navigate_to("landing")
        return

    incidents = [
        inc for inc in st.session_state.incidents if inc["student_id"] == student_id
    ]

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis – {student['name']}")
        st.caption(
            f"{student['program']} • Grade {student['grade']} • EDID {student['edid']}"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student["program"])

    if not incidents:
        st.info("No incidents recorded yet.")
        if st.button("Log first incident", type="primary"):
            navigate_to("direct_log_form", student_id=student_id)
        return

    df = pd.DataFrame(incidents)

    # ---------- Summary metrics ----------
    st.markdown("### High-level summary")

    total = len(df)
    critical = df["is_critical"].sum()
    quick = total - critical
    avg_sev = df["severity"].mean()

    dates = pd.to_datetime(df["date"])
    days_span = (dates.max() - dates.min()).days + 1
    incidents_per_week = (total / days_span) * 7 if days_span > 0 else total

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total incidents", total)
    with col2:
        st.metric("Critical incidents", int(critical), delta=f"{critical/total*100:.0f}% of total")
    with col3:
        st.metric("Quick incidents", int(quick))
    with col4:
        st.metric("Average severity", f"{avg_sev:.1f}")
    with col5:
        st.metric("Incidents per week", f"{incidents_per_week:.1f}")

    st.markdown("---")

    # ---------- Visuals ----------
    st.markdown("### Visual patterns")

    col_g1, col_g2 = st.columns(2)

    # 1. Timeline critical vs quick
    df_timeline = df.copy()
    df_timeline["date"] = pd.to_datetime(df_timeline["date"])
    df_timeline.sort_values("date", inplace=True)
    df_timeline["count"] = 1
    df_timeline_group = (
        df_timeline.groupby(["date", "incident_type"])["count"]
        .sum()
        .reset_index()
    )

    with col_g1:
        fig1 = px.line(
            df_timeline_group,
            x="date",
            y="count",
            color="incident_type",
            markers=True,
            title="Incidents over time (Critical vs Quick)",
        )
        st.plotly_chart(fig1, use_container_width=True)

    # 2. Sessions by critical/non
    df_session = (
        df.groupby(["session", "incident_type"])["id"]
        .count()
        .reset_index(name="count")
    )
    with col_g2:
        fig2 = px.bar(
            df_session,
            x="session",
            y="count",
            color="incident_type",
            title="Incidents by session window",
            barmode="group",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 3. Locations
    st.markdown("#### Locations and antecedents")
    col_g3, col_g4 = st.columns(2)
    df_loc = (
        df.groupby(["location", "incident_type"])["id"]
        .count()
        .reset_index(name="count")
    )
    with col_g3:
        fig3 = px.bar(
            df_loc,
            x="count",
            y="location",
            color="incident_type",
            orientation="h",
            title="Incident locations (critical vs quick)",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # 4. Antecedents
    df_ant = (
        df.groupby(["antecedent", "incident_type"])["id"]
        .count()
        .reset_index(name="count")
    )
    with col_g4:
        fig4 = px.bar(
            df_ant,
            x="count",
            y="antecedent",
            color="incident_type",
            orientation="h",
            title="Antecedents leading to incidents",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # 5. Interventions vs adult outcome (what worked)
    st.markdown("#### Adult responses – what appears to work best?")
    df_int = (
        df.groupby(["intervention", "adult_outcome"])["id"]
        .count()
        .reset_index(name="count")
    )
    fig5 = px.bar(
        df_int,
        x="intervention",
        y="count",
        color="adult_outcome",
        title="Interventions and observed adult outcomes",
        barmode="group",
    )
    fig5.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig5, use_container_width=True)

    # -----------------------------------------------------------------
    # Pattern extraction for narrative recommendations
    # -----------------------------------------------------------------

    def top_value(series: pd.Series) -> Optional[str]:
        if series.empty:
            return None
        return series.value_counts().idxmax()

    top_location = top_value(df["location"])
    top_antecedent = top_value(df["antecedent"])
    top_behaviour = top_value(df["behaviour_type"])
    top_session = top_value(df["session"])
    top_intervention_all = top_value(df["intervention"])
    # which intervention most often linked to De-escalated?
    df_de = df[df["adult_outcome"] == "De-escalated"]
    best_deint = top_value(df_de["intervention"]) if not df_de.empty else None

    st.markdown("---")
    st.markdown("### Trauma-informed analysis & recommendations")

    st.markdown("#### Key patterns observed")
    bullets = []
    if top_location:
        bullets.append(f"- **Most frequent location:** {top_location}")
    if top_session:
        bullets.append(f"- **Most common session window:** {top_session}")
    if top_antecedent:
        bullets.append(f"- **Typical antecedent/trigger:** {top_antecedent}")
    if top_behaviour:
        bullets.append(f"- **Most observed behaviour pattern:** {top_behaviour}")
    if best_deint:
        bullets.append(
            f"- **Intervention most often linked with de-escalation:** {best_deint}"
        )
    if bullets:
        st.markdown("\n".join(bullets))
    else:
        st.write("Patterns are not yet clear – more data is needed.")

    # Narrative recommendations using BSEM / trauma-informed / CPI language
    st.markdown("#### Recommendations (Trauma-informed, BSEM, SMART, CPI-aligned)")

    st.markdown(
        """
1. **Regulate – Relate – Reason (Berry Street & Trauma-informed lens)**  
   - Prioritise **regulation first** in the high-risk settings above (e.g. breathing, sensory tools, movement breaks) before problem-solving.  
   - Ensure a predictable **warm greeting and check-in** for this student during the highest-risk session window.  
   - Where possible, offer **co-regulation** with a known, trusted adult when early signs of dysregulation appear (voice, posture, proximity matching CPI guidance).

2. **Antecedent & environment adjustments**  
   - Given the pattern around **antecedents and location**, adjust the environment to reduce known triggers – for example:
     - Pre-teaching expectations before transitions.
     - Providing **visual schedules** and rehearsal for changes.
     - Offering choice (task / seating / partner) to increase a sense of control.
   - Where the hypothesis indicates “to avoid task” as a likely function, adapt tasks using **SMART goals** (small, measurable steps) so success is achievable within the student’s current window of tolerance.

3. **Adult responses that are working – do more of these**  
   - Data suggests that **{best_deint if best_deint else "specific interventions"}** is frequently linked with *de-escalation*.  
   - Make this strategy **explicit in the student’s support plan** and coach all staff (including TRTs/SSOs) to use the same language and sequence.
   - Maintain **neutral, low-expressed emotion** and use CPI-aligned scripts (calm, respectful, directive language; clear options and limits).

4. **Consistency & rupture-repair (Berry Street / CPI)**  
   - After any critical incident, schedule a short **re-entry / restorative conversation** once the student is regulated (not in the peak of crisis).  
   - Use a simple script: *What happened? What were you feeling? Who has been affected? What do we need to do to repair it?*  
   - Ensure **follow-through on agreed outcomes** (e.g., restorative session, make-up work) so natural consequences feel fair rather than punitive.

5. **Linking to Australian Curriculum – General Capabilities**  
   - Map the student’s goals and support strategies explicitly to:
     - **Personal & Social Capability** – self-awareness, self-management, social awareness, social management.  
     - **Critical & Creative Thinking** – helping the student reflect on triggers, options, and consequences.  
     - **Ethical Understanding** – supporting empathy for peers affected by incidents.
   - Use incidents as data to update **SMARTAR goals** (e.g., “Over the next 5 weeks, during the morning session, the student will use an agreed coping strategy with adult prompting in 4/5 opportunities.”).

6. **Future data use**  
   - Continue to distinguish **quick vs critical incidents** in your logging so you can monitor:
     - Reduction in overall critical incidents over time.  
     - Whether adjustments to environment and adult responses reduce incidents in the highest-risk locations / times.
   - Revisit the charts each review cycle to celebrate growth and refine supports.
"""
    )


# ---------------------------------------------------------------------
# 10. MAIN
# ---------------------------------------------------------------------


def main():
    init_session_state()

    if not st.session_state.logged_in:
        render_login_page()
        return

    page = st.session_state.get("current_page", "landing")
    if page == "landing":
        render_landing_page()
    elif page == "program_students":
        render_program_students()
    elif page == "direct_log_form":
        render_direct_log_form()
    elif page == "critical_incident_abch":
        render_critical_incident_abch_form()
    elif page == "student_analysis":
        render_student_analysis()
    elif page == "admin_portal":
        render_admin_portal()
    else:
        st.error("Unknown page – sending you home.")
        st.session_state.current_page = "landing"
        st.experimental_rerun()


if __name__ == "__main__":
    main()
