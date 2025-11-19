import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
import random
import plotly.express as px
from typing import List, Dict, Any, Optional
import logging
from functools import wraps
import numpy as np

# =========================
#  LOGGING & ERROR HANDLING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sandbox_app_errors.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for application errors"""

    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


class ValidationError(AppError):
    """Raised when data validation fails"""

    pass


def handle_errors(user_message: str = "An error occurred"):
    """Decorator to catch and handle errors in UI render functions"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{func.__name__}: {e.message}", exc_info=True)
                st.error(e.user_message)
                return None
            except Exception as e:
                logger.critical(
                    f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True
                )
                st.error(f"{user_message}. Please try again.")
                with st.expander("Error details (for developer)"):
                    st.code(repr(e))
                return None

        return wrapper

    return decorator


# =========================
#  CONFIGURATION & CONSTANTS
# =========================

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool - SANDBOX",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊",
)

PLOTLY_THEME = "plotly"

# Staff roles available
STAFF_ROLES = ["JP", "PY", "SY", "ADM", "TRT", "External SSO"]

# Program options
PROGRAM_OPTIONS = ["JP", "PY", "SY"]

# Grade options by program
GRADE_OPTIONS = {
    "JP": ["R", "Y1", "Y2"],
    "PY": ["Y3", "Y4", "Y5", "Y6"],
    "SY": ["Y7", "Y8", "Y9", "Y10", "Y11", "Y12"],
}

BEHAVIOUR_LEVELS = ["1 - Low Intensity", "2 - Moderate", "3 - High Risk"]
BEHAVIOURS_FBA = [
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
    "Proximity control/Non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break/Choice of task",
    "Used planned ignoring of minor behaviour",
    "Staff de-escalation script/Verbal coaching",
    "Removed other students from area for safety",
    "Called for staff support/Backup",
]

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class/assembly)",
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

VALID_PAGES = [
    "login",
    "landing",
    "program_students",
    "direct_log_form",
    "critical_incident_abch",
    "student_analysis",
    "admin_portal",
]

# =========================
#  MOCK / SANDBOX DATA
# =========================


def generate_mock_students() -> List[Dict[str, Any]]:
    """Generate mock students for demo"""
    students = [
        # JP Program (3 students)
        {
            "id": "student_JP001",
            "first_name": "Emma",
            "last_name": "Thompson",
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
            "first_name": "Oliver",
            "last_name": "Martinez",
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
            "first_name": "Sophia",
            "last_name": "Wilson",
            "name": "Sophia Wilson",
            "grade": "Y2",
            "dob": "2016-11-08",
            "edid": "JP003",
            "program": "JP",
            "profile_status": "Complete",
            "archived": False,
        },
        # PY Program (3 students)
        {
            "id": "student_PY001",
            "first_name": "Liam",
            "last_name": "Chen",
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
            "first_name": "Ava",
            "last_name": "Rodriguez",
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
            "first_name": "Noah",
            "last_name": "Brown",
            "name": "Noah Brown",
            "grade": "Y6",
            "dob": "2012-01-25",
            "edid": "PY003",
            "program": "PY",
            "profile_status": "Complete",
            "archived": False,
        },
        # SY Program (3 students)
        {
            "id": "student_SY001",
            "first_name": "Isabella",
            "last_name": "Garcia",
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
            "first_name": "Ethan",
            "last_name": "Davis",
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
            "first_name": "Mia",
            "last_name": "Anderson",
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
    """Generate mock staff for demo"""
    staff = [
        {
            "id": "staff_1",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@demo.edu.au",
            "role": "JP",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_2",
            "first_name": "Michael",
            "last_name": "Lee",
            "name": "Michael Lee",
            "email": "michael.lee@demo.edu.au",
            "role": "JP",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_3",
            "first_name": "Jessica",
            "last_name": "Williams",
            "name": "Jessica Williams",
            "email": "jessica.williams@demo.edu.au",
            "role": "PY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_4",
            "first_name": "David",
            "last_name": "Martinez",
            "name": "David Martinez",
            "email": "david.martinez@demo.edu.au",
            "role": "PY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_5",
            "first_name": "Emily",
            "last_name": "Brown",
            "name": "Emily Brown",
            "email": "emily.brown@demo.edu.au",
            "role": "SY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_6",
            "first_name": "James",
            "last_name": "Wilson",
            "name": "James Wilson",
            "email": "james.wilson@demo.edu.au",
            "role": "SY",
            "active": True,
            "archived": False,
        },
        {
            "id": "staff_admin",
            "first_name": "Admin",
            "last_name": "Demo",
            "name": "Admin Demo",
            "email": "admin@demo.edu.au",
            "role": "ADM",
            "active": True,
            "archived": False,
        },
    ]
    return staff


def generate_mock_incidents(
    students: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generate ~70 mock incidents across students"""
    incidents = []
    student_ids = [s["id"] for s in students]
    student_name_lookup = {s["id"]: s["name"] for s in students}

    staff_names = [
        "Sarah Johnson",
        "Michael Lee",
        "Jessica Williams",
        "David Martinez",
        "Emily Brown",
        "James Wilson",
    ]

    behaviours = [
        "Verbal Refusal",
        "Elopement",
        "Property Destruction",
        "Aggression (Peer)",
        "Physical Aggression (Staff)",
    ]
    locations = [
        "JP Classroom",
        "PY Classroom",
        "SY Classroom",
        "Yard",
        "Playground",
        "Library",
    ]

    base_date = datetime.now() - timedelta(days=90)

    for i in range(70):
        student_id = random.choice(student_ids)
        student_name = student_name_lookup[student_id]
        incident_date = base_date + timedelta(days=random.randint(0, 85))

        # Time distribution
        hour = random.choices(
            [9, 10, 11, 12, 13, 14], weights=[2, 3, 2, 1, 2, 3]
        )[0]
        minute = random.randint(0, 59)
        incident_time = time(hour=hour, minute=minute)

        # Severity more likely to be low/moderate
        severity = random.choices([1, 2, 3, 4, 5], weights=[5, 3, 2, 1, 1])[0]
        behaviour_type = random.choice(behaviours)
        location = random.choice(locations)
        antecedent = random.choice(ANTECEDENTS_NEW)
        intervention = random.choice(INTERVENTIONS)
        support_type = random.choice(
            ["1:1 (Individual Support)", "Small Group (3-5 students)"]
        )

        session = None
        if time(9, 0) <= incident_time <= time(11, 0):
            session = "Morning (9:00am - 11:00am)"
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            session = "Middle (11:01am - 1:00pm)"
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            session = "Afternoon (1:01pm - 2:45pm)"
        else:
            session = "Outside School Hours (N/A)"

        is_critical = severity >= 3

        incidents.append(
            {
                "id": f"inc_{i+1}",
                "student_id": student_id,
                "student_name": student_name,
                "incident_date": incident_date.strftime("%Y-%m-%d"),
                "date": incident_date.strftime("%Y-%m-%d"),
                "incident_time": incident_time.strftime("%H:%M:%S"),
                "time": incident_time.strftime("%H:%M:%S"),
                "day_of_week": incident_date.strftime("%A"),
                "day": incident_date.strftime("%A"),
                "session": session,
                "location": location,
                "reported_by": random.choice(staff_names),
                "reported_by_role": random.choice(["JP", "PY", "SY"]),
                "behaviour_type": behaviour_type,
                "antecedent": antecedent,
                "intervention": intervention,
                "support_type": support_type,
                "severity": severity,
                "is_critical": is_critical,
                "description": f"Mock incident involving {behaviour_type.lower()} in {location.lower()}.",
            }
        )

    return incidents


def load_students_from_sandbox() -> List[Dict[str, Any]]:
    return generate_mock_students()


def load_staff_from_sandbox() -> List[Dict[str, Any]]:
    return generate_mock_staff()


def load_incidents_from_sandbox(
    students: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return generate_mock_incidents(students)


def load_system_settings() -> Dict[str, Any]:
    """Simple placeholder settings"""
    return {
        "sandbox_mode": True,
        "critical_threshold": 3,  # severity 3+ triggers ABCH
    }


# =========================
#  SESSION STATE INIT
# =========================


def initialize_session_state():
    """Initialize all session state variables"""
    if "data_loaded" not in st.session_state:
        with st.spinner("Loading sandbox data..."):
            st.session_state.students_list = load_students_from_sandbox()
            st.session_state.staff_list = load_staff_from_sandbox()
            st.session_state.incidents = load_incidents_from_sandbox(
                st.session_state.students_list
            )
            st.session_state.system_settings = load_system_settings()
            st.session_state.data_loaded = True

    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "pending_abch_incident" not in st.session_state:
        st.session_state.pending_abch_incident = None


# =========================
#  HELPERS & CORE LOGIC
# =========================


def navigate_to(
    page: str, student_id: Optional[str] = None, program: Optional[str] = None
):
    """Changes the current page in session state."""
    try:
        if page not in VALID_PAGES:
            raise ValidationError(f"Invalid page: {page}", "Cannot navigate to page")

        st.session_state.current_page = page
        if student_id:
            st.session_state.selected_student_id = student_id
        if program:
            st.session_state.selected_program = program
        st.rerun()
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        st.error("Navigation failed.")
        st.session_state.current_page = "landing"
        st.rerun()


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """Safely retrieves student data."""
    try:
        if not student_id:
            return None
        return next(
            (s for s in st.session_state.students_list if s["id"] == student_id), None
        )
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None


def get_active_staff() -> List[Dict[str, Any]]:
    """Returns active, non-archived staff."""
    try:
        return [
            s
            for s in st.session_state.staff_list
            if s.get("active", True) and not s.get("archived", False)
        ]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []


def get_session_window(incident_time: time) -> str:
    """Calculates session window."""
    try:
        if time(9, 0) <= incident_time <= time(11, 0):
            return "Morning (9:00am - 11:00am)"
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            return "Middle (11:01am - 1:00pm)"
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            return "Afternoon (1:01pm - 2:45pm)"
        else:
            return "Outside School Hours (N/A)"
    except Exception:
        return "Unknown Session"


def add_staff_member(
    first_name: str, last_name: str, email: str, role: str
) -> bool:
    """Adds a new staff member to sandbox (in-memory only)."""
    if not first_name or not first_name.strip():
        raise ValidationError("First name cannot be empty", "Please enter a first name")

    if not last_name or not last_name.strip():
        raise ValidationError("Last name cannot be empty", "Please enter a last name")

    if not email or not email.strip():
        raise ValidationError("Email cannot be empty", "Please enter an email address")

    if "@" not in email:
        raise ValidationError("Invalid email", "Please enter a valid email address")

    if not role or role == "--- Select Role ---":
        raise ValidationError("Role must be selected", "Please select a role")

    full_name = f"{first_name.strip()} {last_name.strip()}"

    existing_email = [
        s
        for s in st.session_state.staff_list
        if s.get("email", "").lower() == email.strip().lower()
        and not s.get("archived", False)
    ]
    if existing_email:
        raise ValidationError(
            "Duplicate email", "A staff member with this email already exists"
        )

    email_clean = email.strip().lower()
    staff_id = "staff_" + email_clean.replace("@", "_").replace(".", "_")

    new_staff = {
        "id": staff_id,
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "name": full_name,
        "email": email_clean,
        "role": role,
        "active": True,
        "archived": False,
    }

    st.session_state.staff_list.append(new_staff)
    logger.info(f"[SANDBOX] Added staff member: {full_name} ({email}, {role})")
    return True


def archive_staff_member(staff_id: str) -> bool:
    staff = next(
        (s for s in st.session_state.staff_list if s.get("id") == staff_id), None
    )
    if not staff:
        raise ValidationError("Staff member not found", "Cannot archive staff member")

    staff["archived"] = True
    staff["active"] = False
    staff["archived_date"] = datetime.now().isoformat()
    return True


def unarchive_staff_member(staff_id: str) -> bool:
    staff = next(
        (s for s in st.session_state.staff_list if s.get("id") == staff_id), None
    )
    if not staff:
        raise ValidationError("Staff member not found", "Cannot restore staff member")

    staff["archived"] = False
    staff["active"] = True
    return True


def add_student(
    first_name: str,
    last_name: str,
    dob: date,
    program: str,
    grade: str,
    edid: str,
) -> bool:
    if not first_name or not first_name.strip():
        raise ValidationError("First name cannot be empty", "Please enter a first name")

    if not last_name or not last_name.strip():
        raise ValidationError("Last name cannot be empty", "Please enter a last name")

    if not program or program == "--- Select Program ---":
        raise ValidationError("Program must be selected", "Please select a program")

    if not grade or grade == "--- Select Grade ---":
        raise ValidationError("Grade must be selected", "Please select a grade")

    if not dob:
        raise ValidationError("Date of birth is required", "Please enter date of birth")

    if not edid or not edid.strip():
        raise ValidationError("EDID is required", "Please enter EDID")

    if dob > datetime.now().date():
        raise ValidationError(
            "Invalid date of birth", "Date of birth cannot be in the future"
        )

    full_name = f"{first_name.strip()} {last_name.strip()}"

    existing_edid = [
        s
        for s in st.session_state.students_list
        if s.get("edid", "").upper() == edid.strip().upper()
        and not s.get("archived", False)
    ]
    if existing_edid:
        raise ValidationError(
            "Duplicate EDID", f"A student with EDID {edid} already exists"
        )

    student_id = "student_" + edid.strip().upper().replace(" ", "_")

    new_student = {
        "id": student_id,
        "first_name": first_name.strip(),
        "last_name": last_name.strip(),
        "name": full_name,
        "dob": dob.strftime("%Y-%m-%d"),
        "program": program,
        "grade": grade,
        "edid": edid.strip().upper(),
        "profile_status": "Draft",
        "archived": False,
    }

    st.session_state.students_list.append(new_student)
    logger.info(f"[SANDBOX] Added student: {full_name} ({edid}, {program})")
    return True


def get_students_by_program(
    program: str, include_archived: bool = False
) -> List[Dict[str, Any]]:
    students = st.session_state.students_list
    filtered = [s for s in students if s.get("program") == program]
    if not include_archived:
        filtered = [s for s in filtered if not s.get("archived", False)]
    return filtered


# =========================
#  AUTH (SANDBOX)
# =========================


def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    SANDBOX LOGIN:
    - Matches email to mock staff list
    - Password for ALL users = 'demo'
    """
    try:
        if not email or not email.strip() or not password:
            return None

        email = email.strip().lower()
        staff_member = next(
            (
                s
                for s in st.session_state.staff_list
                if s.get("email", "").lower() == email
                and not s.get("archived", False)
            ),
            None,
        )

        if not staff_member:
            return None

        if password != "demo":
            return None

        return staff_member
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None


# =========================
#  VALIDATION
# =========================


def validate_incident_form(
    location,
    reported_by,
    behaviour_type,
    severity_level,
    incident_date,
    incident_time,
):
    errors = []

    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or reported_by.get("id") is None:
        errors.append("Please select a Staff Member")
    if behaviour_type == "--- Select behaviour ---":
        errors.append("Please select a behaviour Type")
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")

    if errors:
        raise ValidationError(
            "Form validation failed", "Please correct: " + ", ".join(errors)
        )


def validate_abch_form(
    context, antecedent, behaviour_desc, consequence, manager_notify, parent_notify
):
    errors = []

    if not context or context.strip() == "":
        errors.append("Context is required")
    if not antecedent or antecedent.strip() == "":
        errors.append("Antecedent is required")
    if not behaviour_desc or behaviour_desc.strip() == "":
        errors.append("Behaviour description is required")
    if not consequence or consequence.strip() == "":
        errors.append("Consequences are required")
    if not manager_notify:
        errors.append("Line Manager notification required")
    if not parent_notify:
        errors.append("Parent notification required")

    if errors:
        raise ValidationError(
            "ABCH validation failed", "Please correct: " + ", ".join(errors)
        )


# =========================
#  UI COMPONENTS
# =========================


def calculate_age(dob_str: str) -> str:
    try:
        if not dob_str:
            return "N/A"
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        return str(age)
    except Exception as e:
        logger.error(f"Error calculating age: {e}")
        return "N/A"


def render_staff_selector(
    label: str = "Staff Member",
    key: str = "staff_selector",
    include_special_options: bool = True,
):
    """
    Renders a staff selector with optional TRT and External SSO options.
    Returns a dict with staff info, or special options if selected.
    """
    active_staff = get_active_staff()

    options = [
        {"id": None, "name": "--- Select Staff ---", "role": None, "special": False}
    ]

    if include_special_options:
        options.append(
            {"id": "TRT", "name": "TRT (Relief Teacher)", "role": "TRT", "special": True}
        )
        options.append(
            {
                "id": "External_SSO",
                "name": "External SSO",
                "role": "External SSO",
                "special": True,
            }
        )
        options.append(
            {
                "id": "divider",
                "name": "─────────────────",
                "role": None,
                "special": False,
            }
        )

    options.extend([{**s, "special": False} for s in active_staff])
    selectable_options = [opt for opt in options if opt["id"] != "divider"]

    selected = st.selectbox(
        label,
        options=selectable_options,
        format_func=lambda x: f"{x['name']}"
        + (f" ({x['role']})" if x["role"] and not x.get("special") else ""),
        key=key,
    )

    if selected and selected.get("special"):
        st.markdown(f"**{selected['name']} selected** - Please enter their name:")
        specific_name = st.text_input(
            f"Enter {selected['role']} Name",
            key=f"{key}_specific_name",
            placeholder=f"Full name of {selected['role']}",
        )

        if specific_name and specific_name.strip():
            return {
                "id": selected["id"],
                "name": specific_name.strip(),
                "role": selected["role"],
                "is_special": True,
            }
        else:
            return {
                "id": selected["id"],
                "name": f"{selected['role']} (Name Required)",
                "role": selected["role"],
                "is_special": True,
                "name_missing": True,
            }

    return selected


# =========================
#  PAGES
# =========================

# --- LOGIN PAGE ---


@handle_errors("Unable to load login page")
def render_login_page():
    """Renders the login page with email + demo password."""
    st.markdown(
        """
<div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <h3 style="color: white; margin: 0;">
        🎭 SANDBOX MODE - Synthetic data only / password = <code>demo</code>
    </h3>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="hero-section">
    <div class="hero-icon">🔐</div>
    <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
    <p class="hero-subtitle">Staff Login (Sandbox)</p>
    <p class="hero-tagline">Use your demo staff email + password <b>demo</b> to explore features.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("### 🔑 Login")

            email = st.text_input(
                "Email Address",
                placeholder="sarah.johnson@demo.edu.au",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="demo",
                key="login_password",
            )

            if st.button("🚀 Login", type="primary", use_container_width=True):
                if email and password:
                    staff_member = verify_login(email, password)
                    if staff_member:
                        st.session_state.logged_in = True
                        st.session_state.current_user = staff_member
                        st.session_state.current_page = "landing"
                        st.success(f"✅ Welcome back, {staff_member['name']}!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Invalid email or password. (Sandbox password = 'demo')"
                        )
                else:
                    st.warning("⚠️ Please enter both email and password")

            st.markdown("---")
            st.caption(
                "🔬 **Sandbox note:** This environment does not use any real data or Supabase."
            )


# --- LANDING PAGE ---


@handle_errors("Unable to load landing page")
def render_landing_page():
    current_user = st.session_state.get("current_user", {})

    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.markdown(f"### 👋 Welcome, {current_user.get('name', 'User')}!")
        st.caption(
            f"Role: {current_user.get('role', 'N/A')} | {current_user.get('email', 'N/A')}"
        )
    with col_logout:
        st.markdown("##")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = "login"
            st.rerun()

    st.markdown("---")

    # Simple CSS for hero
    st.markdown(
        """
<style>
.hero-section {
    text-align: center;
    padding: 3rem 2rem;
    margin-bottom: 3rem;
    background: rgba(255, 255, 255, 0.15);
    -webkit-backdrop-filter: blur(20px);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 
        0 25px 50px -12px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
}
.hero-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.3rem;
}
.hero-tagline {
    font-size: 1rem;
    max-width: 650px;
    margin: 0 auto;
}
.divider-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.15), transparent);
    margin: 3rem 0;
    border-radius: 2px;
}
</style>
<div class="hero-section">
    <div class="hero-icon">📊✨</div>
    <h1 class="hero-title">Behaviour Support & Data Analysis</h1>
    <p class="hero-subtitle">Sandbox Demo</p>
    <p class="hero-tagline">
        Explore behaviour incident logging, critical ABCH workflow, and student-level analytics 
        in a safe, synthetic environment.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    st.markdown("### 📚 Select Your Program")
    st.caption("Choose a program to view students, log incidents, and access analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🎨 Junior Primary")
        st.caption("Reception - Year 2")
        if st.button(
            "Enter JP Program", key="jp_btn", use_container_width=True, type="primary"
        ):
            navigate_to("program_students", program="JP")

    with col2:
        st.markdown("#### 📖 Primary Years")
        st.caption("Year 3 - Year 6")
        if st.button(
            "Enter PY Program", key="py_btn", use_container_width=True, type="primary"
        ):
            navigate_to("program_students", program="PY")

    with col3:
        st.markdown("#### 🎓 Senior Years")
        st.caption("Year 7 - Year 12")
        if st.button(
            "Enter SY Program", key="sy_btn", use_container_width=True, type="primary"
        ):
            navigate_to("program_students", program="SY")

    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")
    st.caption("Fast access to common tasks")

    col_quick1, col_quick2 = st.columns(2)

    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        st.caption("Select a student and immediately log a new incident")
        all_active_students = [
            s for s in st.session_state.students_list if not s.get("archived", False)
        ]
        student_options = [{"id": None, "name": "--- Select Student ---"}] + [
            {"id": s["id"], "name": s["name"]} for s in all_active_students
        ]
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x["name"],
            key="quick_log_student",
            label_visibility="collapsed",
        )

        if selected_student and selected_student["id"]:
            if st.button(
                "Start Quick Log",
                key="quick_log_btn",
                use_container_width=True,
                type="primary",
            ):
                navigate_to("direct_log_form", student_id=selected_student["id"])

    with col_quick2:
        st.markdown("#### 🔐 Admin Portal")
        st.caption("Manage staff, students, and system settings (sandbox only)")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "Access Admin Portal",
            key="admin_btn",
            use_container_width=True,
            type="primary",
        ):
            navigate_to("admin_portal")


# --- PROGRAM STUDENTS ---


@handle_errors("Unable to load program students")
def render_program_students():
    program = st.session_state.get("selected_program", "JP")

    col_title, col_back = st.columns([4, 1])
    with col_title:
        program_names = {"JP": "Junior Primary", "PY": "Primary Years", "SY": "Senior Years"}
        st.title(f"{program_names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to("landing")

    st.markdown("---")

    tab1, tab2 = st.tabs(["📚 Current Students", "📦 Archived Students"])

    with tab1:
        current_students = get_students_by_program(program, include_archived=False)
        if not current_students:
            st.info(f"No current students in the {program} program.")
        else:
            st.markdown(f"### Current Students ({len(current_students)})")
            cols_per_row = 3
            for i in range(0, len(current_students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, student in enumerate(current_students[i : i + cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {student['name']}")
                            st.markdown(f"**Grade:** {student['grade']}")
                            st.caption(f"EDID: {student.get('edid', 'N/A')}")

                            incident_count = len(
                                [
                                    inc
                                    for inc in st.session_state.get("incidents", [])
                                    if inc.get("student_id") == student["id"]
                                ]
                            )
                            st.metric("Incidents", incident_count)

                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button(
                                    "👁️ View",
                                    key=f"view_{student['id']}",
                                    use_container_width=True,
                                ):
                                    navigate_to("student_analysis", student_id=student["id"])
                            with col_log:
                                if st.button(
                                    "📝 Log",
                                    key=f"log_{student['id']}",
                                    use_container_width=True,
                                ):
                                    navigate_to("direct_log_form", student_id=student["id"])

    with tab2:
        archived_students = [
            s
            for s in st.session_state.students_list
            if s.get("program") == program and s.get("archived", False)
        ]

        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("Students who have completed the program - read-only")

            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(
                        f"**Profile Status:** {student.get('profile_status', 'N/A')}"
                    )
                    st.markdown(f"**EDID:** {student.get('edid', 'N/A')}")

                    incident_count = len(
                        [
                            inc
                            for inc in st.session_state.get("incidents", [])
                            if inc.get("student_id") == student["id"]
                        ]
                    )
                    st.metric("Total Incidents", incident_count)

                    if st.button(
                        "View Historical Data", key=f"view_arch_{student['id']}"
                    ):
                        navigate_to("student_analysis", student_id=student["id"])


# --- ADMIN PORTAL ---


@handle_errors("Unable to load admin portal")
def render_admin_portal():
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal (Sandbox)")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to("landing")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["👥 Staff Management", "🎓 Student Management", "📊 Reports", "⚙️ Settings"]
    )

    with tab1:
        render_staff_management()

    with tab2:
        render_student_management()

    with tab3:
        st.markdown("### 📊 System Reports")
        st.info("High-level reports - (demo placeholder).")

    with tab4:
        st.markdown("### ⚙️ System Settings")
        st.write("Sandbox mode: ✅ Enabled")
        st.write(
            f"Critical ABCH threshold: severity ≥ {st.session_state.system_settings.get('critical_threshold', 3)}"
        )


@handle_errors("Unable to load staff management")
def render_staff_management():
    st.markdown("## 👥 Staff Management")
    st.markdown("---")

    staff_tab1, staff_tab2 = st.tabs(["✅ Active Staff", "📦 Archived Staff"])

    with staff_tab1:
        st.markdown("### Add New Staff Member")

        col_add1, col_add2, col_add3, col_add4 = st.columns([2, 2, 3, 2])

        with col_add1:
            new_staff_first_name = st.text_input(
                "First Name", key="new_staff_first_name", placeholder="First name"
            )

        with col_add2:
            new_staff_last_name = st.text_input(
                "Last Name", key="new_staff_last_name", placeholder="Last name"
            )

        with col_add3:
            new_staff_email = st.text_input(
                "Email", key="new_staff_email", placeholder="email@example.com"
            )

        with col_add4:
            new_staff_role = st.selectbox(
                "Role",
                options=["--- Select Role ---"] + STAFF_ROLES,
                key="new_staff_role",
            )

        col_add_btn = st.columns([4, 1])
        with col_add_btn[1]:
            if st.button("➕ Add Staff", type="primary", use_container_width=True):
                try:
                    if add_staff_member(
                        new_staff_first_name,
                        new_staff_last_name,
                        new_staff_email,
                        new_staff_role,
                    ):
                        st.success(f"✅ Added {new_staff_first_name} {new_staff_last_name}")
                        st.rerun()
                except (ValidationError, AppError) as e:
                    st.error(e.user_message)

        st.markdown("---")
        st.markdown("### Current Active Staff")

        active_staff = [s for s in st.session_state.staff_list if not s.get("archived", False)]

        if not active_staff:
            st.info("No active staff members")
        else:
            staff_by_role: Dict[str, List[Dict[str, Any]]] = {}
            for staff in active_staff:
                role = staff.get("role", "Unknown")
                staff_by_role.setdefault(role, []).append(staff)

            for role in STAFF_ROLES:
                if role in staff_by_role:
                    with st.expander(
                        f"**{role}** ({len(staff_by_role[role])} staff)", expanded=True
                    ):
                        for staff in staff_by_role[role]:
                            col_staff1, col_staff2, col_staff3 = st.columns([3, 2, 1])

                            with col_staff1:
                                st.markdown(f"**{staff['name']}**")

                            with col_staff2:
                                st.caption(staff.get("email", ""))

                            with col_staff3:
                                staff_key = staff.get("id") or staff.get("email")
                                if st.button(
                                    "🗄️ Archive",
                                    key=f"archive_{staff_key}",
                                    use_container_width=True,
                                ):
                                    try:
                                        if archive_staff_member(staff.get("id")):
                                            st.success(f"Archived {staff['name']}")
                                            st.rerun()
                                    except AppError as e:
                                        st.error(e.user_message)

    with staff_tab2:
        st.markdown("### Archived Staff Members")
        archived_staff = [s for s in st.session_state.staff_list if s.get("archived", False)]

        if not archived_staff:
            st.info("No archived staff members")
        else:
            for staff in archived_staff:
                with st.expander(f"📦 {staff['name']} - {staff.get('role', 'N/A')}"):
                    st.markdown(f"**Role:** {staff.get('role', 'N/A')}")
                    if staff.get("archived_date"):
                        st.markdown(f"**Archived:** {staff['archived_date']}")

                    staff_key = staff.get("id") or staff.get("email")
                    if st.button(
                        "♻️ Restore Staff Member", key=f"restore_{staff_key}"
                    ):
                        try:
                            if unarchive_staff_member(staff.get("id")):
                                st.success(f"Restored {staff['name']}")
                                st.rerun()
                        except AppError as e:
                            st.error(e.user_message)


@handle_errors("Unable to load student management")
def render_student_management():
    st.markdown("## 🎓 Student Management")
    st.markdown("---")

    st.markdown("### Add New Student")

    col_add1, col_add2, col_add3, col_add4, col_add5 = st.columns(
        [2, 2, 1.5, 1, 1]
    )

    with col_add1:
        new_student_first_name = st.text_input(
            "First Name", key="new_student_first_name", placeholder="First name"
        )

    with col_add2:
        new_student_last_name = st.text_input(
            "Last Name", key="new_student_last_name", placeholder="Last name"
        )

    with col_add3:
        new_student_dob = st.date_input(
            "Date of Birth (DD/MM/YYYY)",
            key="new_student_dob",
            min_value=date(1990, 1, 1),
            max_value=datetime.now().date(),
            value=date(2015, 1, 1),
            format="DD/MM/YYYY",
        )

    with col_add4:
        new_student_program = st.selectbox(
            "Program",
            options=["--- Select Program ---"] + PROGRAM_OPTIONS,
            key="new_student_program",
        )

    with col_add5:
        if new_student_program and new_student_program != "--- Select Program ---":
            grade_options = ["--- Select Grade ---"] + GRADE_OPTIONS.get(
                new_student_program, []
            )
        else:
            grade_options = ["--- Select Grade ---"]

        new_student_grade = st.selectbox(
            "Grade", options=grade_options, key="new_student_grade"
        )

    col_edid, col_add_btn = st.columns([3, 1])

    with col_edid:
        new_student_edid = st.text_input(
            "EDID (Education Department ID)",
            key="new_student_edid",
            placeholder="e.g., ED12345",
        )

    with col_add_btn:
        st.markdown("##")
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            try:
                if add_student(
                    new_student_first_name,
                    new_student_last_name,
                    new_student_dob,
                    new_student_program,
                    new_student_grade,
                    new_student_edid,
                ):
                    st.success(
                        f"✅ Added {new_student_first_name} {new_student_last_name} to {new_student_program} Program"
                    )
                    st.rerun()
            except (ValidationError, AppError) as e:
                st.error(e.user_message)

    st.markdown("---")
    st.markdown("### Current Students by Program")

    program_tabs = st.tabs(
        ["📘 Junior Primary", "📗 Primary Years", "📙 Senior Years", "📚 All Students"]
    )
    programs = ["JP", "PY", "SY"]

    for idx, program in enumerate(programs):
        with program_tabs[idx]:
            students_in_program = get_students_by_program(program, include_archived=False)
            if not students_in_program:
                st.info(f"No students currently in {program} program")
            else:
                st.markdown(f"**Total Students:** {len(students_in_program)}")
                rows = []
                for student in students_in_program:
                    age = calculate_age(student.get("dob", ""))
                    rows.append(
                        {
                            "Name": student["name"],
                            "Grade": student["grade"],
                            "EDID": student.get("edid", "N/A"),
                            "Age": age,
                            "DOB": student.get("dob", "N/A"),
                            "Status": student.get("profile_status", "Draft"),
                        }
                    )
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)

    with program_tabs[3]:
        all_students = [
            s for s in st.session_state.students_list if not s.get("archived", False)
        ]
        if not all_students:
            st.info("No students in the system")
        else:
            st.markdown(
                f"**Total Students Across All Programs:** {len(all_students)}"
            )

            col_jp, col_py, col_sy = st.columns(3)
            with col_jp:
                st.metric(
                    "JP Students",
                    len(get_students_by_program("JP", include_archived=False)),
                )
            with col_py:
                st.metric(
                    "PY Students",
                    len(get_students_by_program("PY", include_archived=False)),
                )
            with col_sy:
                st.metric(
                    "SY Students",
                    len(get_students_by_program("SY", include_archived=False)),
                )

            st.markdown("---")

            rows = []
            for student in sorted(
                all_students, key=lambda x: (x.get("program", ""), x.get("name", ""))
            ):
                age = calculate_age(student.get("dob", ""))
                rows.append(
                    {
                        "Name": student["name"],
                        "Program": student["program"],
                        "Grade": student["grade"],
                        "EDID": student.get("edid", "N/A"),
                        "Age": age,
                        "DOB": student.get("dob", "N/A"),
                        "Status": student.get("profile_status", "Draft"),
                    }
                )
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)


# --- DIRECT INCIDENT LOG ---


@handle_errors("Unable to load incident form")
def render_direct_log_form():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student["program"])

    st.markdown("---")

    with st.form("incident_form"):
        st.markdown("### Incident Details")

        col1, col2 = st.columns(2)

        with col1:
            incident_date = st.date_input(
                "Date of Incident (DD/MM/YYYY)",
                value=datetime.now(),
                format="DD/MM/YYYY",
            )
            incident_time = st.time_input(
                "Time of Incident", value=datetime.now().time()
            )
            location = st.selectbox("Location", options=LOCATIONS)

        with col2:
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True,
            )

        st.markdown("### Behaviour Information")

        col3, col4 = st.columns(2)

        with col3:
            behaviour_type = st.selectbox(
                "Behaviour Type",
                options=["--- Select behaviour ---"] + BEHAVIOURS_FBA,
            )
            antecedent = st.selectbox("Antecedent", options=ANTECEDENTS_NEW)

        with col4:
            intervention = st.selectbox("Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)

        severity_level = st.slider("Severity Level", 1, 5, 2)

        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional context about the incident...",
            height=120,
        )

        submitted = st.form_submit_button(
            "Submit Incident Report", type="primary", use_container_width=True
        )

        if submitted:
            try:
                if reported_by and reported_by.get("name_missing"):
                    st.error(
                        "Please enter the name for the selected staff type (TRT or External SSO)"
                    )
                    return

                validate_incident_form(
                    location,
                    reported_by,
                    behaviour_type,
                    severity_level,
                    incident_date,
                    incident_time,
                )

                session = get_session_window(incident_time)

                new_incident = {
                    "id": f"inc_manual_{len(st.session_state.incidents)+1}",
                    "student_id": student_id,
                    "student_name": student["name"],
                    "incident_date": incident_date.strftime("%Y-%m-%d"),
                    "date": incident_date.strftime("%Y-%m-%d"),
                    "incident_time": incident_time.strftime("%H:%M:%S"),
                    "time": incident_time.strftime("%H:%M:%S"),
                    "day_of_week": incident_date.strftime("%A"),
                    "day": incident_date.strftime("%A"),
                    "session": session,
                    "location": location,
                    "reported_by": reported_by["name"],
                    "reported_by_role": reported_by["role"],
                    "is_special_staff": reported_by.get("is_special", False),
                    "behaviour_type": behaviour_type,
                    "antecedent": antecedent,
                    "intervention": intervention,
                    "support_type": support_type,
                    "severity": severity_level,
                    "is_critical": severity_level
                    >= st.session_state.system_settings.get(
                        "critical_threshold", 3
                    ),
                    "description": description,
                }

                st.session_state.incidents.append(new_incident)

                st.success("✅ Incident report saved (sandbox).")

                # If at/above critical threshold → redirect to ABCH
                critical_threshold = st.session_state.system_settings.get(
                    "critical_threshold", 3
                )
                if severity_level >= critical_threshold:
                    st.warning(
                        f"⚠️ This incident meets the Critical Criteria (Severity ≥ {critical_threshold}). "
                        "Redirecting to Critical Incident ABCH form..."
                    )
                    st.session_state.pending_abch_incident = new_incident
                    navigate_to("critical_incident_abch")
                else:
                    col_another, col_return = st.columns(2)
                    with col_another:
                        if st.button("➕ Log Another Incident", use_container_width=True):
                            st.rerun()
                    with col_return:
                        if st.button(
                            "↩️ Return to Student List", use_container_width=True
                        ):
                            navigate_to(
                                "program_students", program=student["program"]
                            )

            except ValidationError as e:
                st.error(e.user_message)


# --- CRITICAL INCIDENT ABCH (LAYOUT IN COLUMNS) ---


@handle_errors("Unable to load critical incident form")
def render_critical_incident_abch_form():
    st.title("🚨 Critical Incident – ABCH Summary (Sandbox)")

    pending_incident = st.session_state.get("pending_abch_incident")

    col_back, col_spacer = st.columns([1, 5])
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to("landing")

    st.markdown("---")

    if pending_incident:
        st.markdown("### Linked Incident Summary")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Student:** {pending_incident.get('student_name')}")
                st.markdown(f"**Date:** {pending_incident.get('date')}")
            with col2:
                st.markdown(
                    f"**Time:** {pending_incident.get('time')} ({pending_incident.get('session')})"
                )
                st.markdown(f"**Location:** {pending_incident.get('location')}")
            with col3:
                st.markdown(
                    f"**Behaviour:** {pending_incident.get('behaviour_type', 'N/A')}"
                )
                st.markdown(
                    f"**Severity:** {pending_incident.get('severity', 'N/A')} (Critical)"
                )

    st.markdown("### ABCH – Critical Incident Summary")

    with st.form("abch_form"):
        # A / B / C / H in a single row of columns
        colA, colB, colC, colH = st.columns(4)

        with colA:
            antecedent_text = st.text_area(
                "A – Antecedent",
                value=pending_incident.get("antecedent", "") if pending_incident else "",
                height=150,
                placeholder=(
                    "What was happening just before the incident?\n"
                    "- Activity / task\n- People present\n- Triggers noticed"
                ),
            )

        with colB:
            behaviour_text = st.text_area(
                "B – Behaviour",
                value=pending_incident.get("behaviour_type", "")
                + (
                    f"\n\nDetail:\n{pending_incident.get('description','')}"
                    if pending_incident
                    else ""
                ),
                height=150,
                placeholder=(
                    "What did you see/hear?\n- Specific observable actions\n"
                    "- Verbal / non-verbal behaviour\n- Duration / intensity"
                ),
            )

        with colC:
            consequence_text = st.text_area(
                "C – Consequence",
                height=150,
                placeholder=(
                    "What happened next?\n- Staff responses\n- Peer responses\n"
                    "- Immediate outcomes / follow up"
                ),
            )

        with colH:
            context_text = st.text_area(
                "H – Hypothesis / Context",
                height=150,
                placeholder=(
                    "What is your best guess about WHY?\n- Possible function (escape, attention, sensory, control)\n"
                    "- Known triggers / vulnerabilities\n- Relevant background factors"
                ),
            )

        st.markdown("---")

        col_flags1, col_flags2 = st.columns(2)
        with col_flags1:
            manager_notify = st.checkbox(
                "✅ Line Manager notified", value=False, key="abch_manager_notify"
            )
            parent_notify = st.checkbox(
                "✅ Parent / Carer notified", value=False, key="abch_parent_notify"
            )

        with col_flags2:
            followup_actions = st.text_area(
                "Planned Follow-Up / Adjustments",
                height=100,
                placeholder=(
                    "What will be adjusted or trialled?\n- Environmental changes\n"
                    "- Staff responses / scripts\n- Student supports / goals"
                ),
            )

        submitted = st.form_submit_button(
            "Save ABCH Summary (Sandbox)", type="primary", use_container_width=True
        )

        if submitted:
            try:
                validate_abch_form(
                    context_text,
                    antecedent_text,
                    behaviour_text,
                    consequence_text,
                    manager_notify,
                    parent_notify,
                )

                # In sandbox we just log it and clear pending
                logger.info(
                    "[SANDBOX] ABCH summary saved\n"
                    f"A: {antecedent_text}\nB: {behaviour_text}\nC: {consequence_text}\nH: {context_text}"
                )

                st.success("✅ ABCH critical incident summary saved (sandbox).")

                st.session_state.pending_abch_incident = None

                col_nav1, col_nav2 = st.columns(2)
                with col_nav1:
                    if st.button(
                        "↩️ Return to Student Analysis",
                        use_container_width=True,
                        key="abch_to_student",
                    ):
                        if pending_incident:
                            navigate_to(
                                "student_analysis",
                                student_id=pending_incident.get("student_id"),
                            )
                        else:
                            navigate_to("landing")
                with col_nav2:
                    if st.button(
                        "🏠 Back to Home",
                        use_container_width=True,
                        key="abch_to_home",
                    ):
                        navigate_to("landing")

            except ValidationError as e:
                st.error(e.user_message)


# --- STUDENT ANALYSIS ---


@handle_errors("Unable to load student analysis")
def render_student_analysis():
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)

    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to("landing")
        return

    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(
            f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student["program"])

    st.markdown("---")

    student_incidents = [
        inc
        for inc in st.session_state.get("incidents", [])
        if inc.get("student_id") == student_id
    ]

    if not student_incidents:
        st.info("No incident data available for this student yet.")
        st.markdown("### Actions")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to("direct_log_form", student_id=student_id)
        return

    df = pd.DataFrame(student_incidents)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    st.markdown("### 📈 Summary Statistics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Incidents", len(df))

    with col2:
        critical_count = df["is_critical"].sum()
        critical_pct = (critical_count / len(df) * 100.0) if len(df) > 0 else 0
        st.metric(
            "Critical Incidents",
            int(critical_count),
            delta=f"{critical_pct:.0f}%" if critical_count else None,
        )

    with col3:
        avg_severity = df["severity"].mean() if "severity" in df else 0
        st.metric("Avg Severity", f"{avg_severity:.1f}")

    with col4:
        days_span = (
            (df["date"].max() - df["date"].min()).days + 1 if df["date"].notna().any() else 1
        )
        st.metric("Days Tracked", days_span)

    with col5:
        incidents_per_week = (len(df) / days_span) * 7 if days_span > 0 else 0
        st.metric("Incidents/Week", f"{incidents_per_week:.1f}")

    st.markdown("---")

    # === CHARTS ===
    st.markdown("### 📊 Visual Insights")

    tab_over_time, tab_patterns, tab_heatmaps, tab_table = st.tabs(
        ["⏱ Over Time", "📌 Patterns", "🔥 Heatmaps", "📋 Raw Data"]
    )

    # --- Over Time ---
    with tab_over_time:
        st.markdown("#### Incidents Over Time")

        daily_counts = (
            df.groupby("date").size().reset_index(name="Count").sort_values("date")
        )
        if not daily_counts.empty:
            fig = px.line(
                daily_counts,
                x="date",
                y="Count",
                markers=True,
                title="Daily Incident Count",
            )
            fig.update_layout(template=PLOTLY_THEME, xaxis_title="Date", yaxis_title="Incidents")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to show over-time chart.")

        st.markdown("#### Severity Over Time")
        if "severity" in df and df["date"].notna().any():
            fig = px.scatter(
                df,
                x="date",
                y="severity",
                color="is_critical",
                title="Severity Over Time (Critical in colour)",
                hover_data=["behaviour_type", "location", "session"],
            )
            fig.update_layout(
                template=PLOTLY_THEME,
                xaxis_title="Date",
                yaxis_title="Severity (1–5)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- Patterns ---
    with tab_patterns:
        st.markdown("#### Behaviour Patterns")

        colp1, colp2 = st.columns(2)

        with colp1:
            if "behaviour_type" in df:
                behaviour_counts = (
                    df["behaviour_type"].value_counts().reset_index()
                )
                behaviour_counts.columns = ["Behaviour", "Count"]
                fig = px.bar(
                    behaviour_counts,
                    x="Count",
                    y="Behaviour",
                    orientation="h",
                    title="Behaviour Frequency",
                )
                fig.update_layout(
                    template=PLOTLY_THEME, xaxis_title="Incidents", yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)

        with colp2:
            if "location" in df:
                loc_counts = df["location"].value_counts().reset_index()
                loc_counts.columns = ["Location", "Count"]
                fig = px.bar(
                    loc_counts,
                    x="Location",
                    y="Count",
                    title="Incidents by Location",
                )
                fig.update_layout(
                    template=PLOTLY_THEME,
                    xaxis_title="Location",
                    yaxis_title="Incidents",
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Day & Session Patterns")
        cold1, cold2 = st.columns(2)

        with cold1:
            if "day" in df:
                # order days
                day_order = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                df["day"] = pd.Categorical(
                    df["day"], categories=day_order, ordered=True
                )
                day_counts = (
                    df["day"].value_counts().sort_index().reset_index()
                )
                day_counts.columns = ["Day", "Count"]
                fig = px.bar(
                    day_counts,
                    x="Day",
                    y="Count",
                    title="Incidents by Day of Week",
                )
                fig.update_layout(
                    template=PLOTLY_THEME,
                    xaxis_title="Day",
                    yaxis_title="Incidents",
                )
                st.plotly_chart(fig, use_container_width=True)

        with cold2:
            if "session" in df:
                session_counts = df["session"].value_counts().reset_index()
                session_counts.columns = ["Session", "Count"]
                fig = px.bar(
                    session_counts,
                    x="Session",
                    y="Count",
                    title="Incidents by Session",
                )
                fig.update_layout(
                    template=PLOTLY_THEME,
                    xaxis_title="Session",
                    yaxis_title="Incidents",
                    xaxis_tickangle=-20,
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Support Type Usage")
        if "support_type" in df:
            support_counts = df["support_type"].value_counts().reset_index()
            support_counts.columns = ["Support Type", "Count"]
            fig = px.pie(
                support_counts,
                names="Support Type",
                values="Count",
                title="Support Types Used",
            )
            fig.update_layout(template=PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)

    # --- Heatmaps ---
    with tab_heatmaps:
        st.markdown("#### Day × Session Heatmap")

        if "day" in df and "session" in df:
            pivot = (
                df.pivot_table(
                    index="day",
                    columns="session",
                    values="id",
                    aggfunc="count",
                    fill_value=0,
                )
                .reindex(
                    [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]
                )
            )
            if not pivot.empty:
                fig = px.imshow(
                    pivot,
                    labels=dict(
                        x="Session", y="Day of Week", color="Incident Count"
                    ),
                    title="Incidents by Day and Session",
                    aspect="auto",
                )
                fig.update_layout(template=PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for a heatmap yet.")

        st.markdown("#### Behaviour × Location Heatmap")
        if "behaviour_type" in df and "location" in df:
            pivot_bl = df.pivot_table(
                index="behaviour_type",
                columns="location",
                values="id",
                aggfunc="count",
                fill_value=0,
            )
            if not pivot_bl.empty:
                fig = px.imshow(
                    pivot_bl,
                    labels=dict(
                        x="Location", y="Behaviour Type", color="Incident Count"
                    ),
                    title="Behaviours by Location",
                    aspect="auto",
                )
                fig.update_layout(template=PLOTLY_THEME)
                st.plotly_chart(fig, use_container_width=True)

    # --- Raw Data ---
    with tab_table:
        st.markdown("#### Incident Table")
        show_cols = [
            "date",
            "time",
            "day",
            "session",
            "location",
            "behaviour_type",
            "severity",
            "is_critical",
            "support_type",
            "reported_by",
        ]
        show_cols = [c for c in show_cols if c in df.columns]
        st.dataframe(df[show_cols].sort_values("date"), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🎯 Data-Informed Recommendations")

    # Simple pattern analysis for recommendations
    recommendations = []

    # Top behaviour
    if "behaviour_type" in df:
        top_behaviour = df["behaviour_type"].value_counts().idxmax()
        top_count = df["behaviour_type"].value_counts().max()
        recommendations.append(
            f"- **Most frequent behaviour:** {top_behaviour} "
            f"(~{top_count} recorded incidents). Consider a targeted plan addressing this pattern."
        )

    # Top day
    if "day" in df:
        top_day = df["day"].value_counts().idxmax()
        recommendations.append(
            f"- **Peak day:** {top_day}. Explore timetable, transitions and demands on this day."
        )

    # Top session
    if "session" in df:
        top_session = df["session"].value_counts().idxmax()
        recommendations.append(
            f"- **Peak time-of-day:** {top_session}. Plan proactive regulation supports prior to this window."
        )

    # Critical ratio
    if "is_critical" in df:
        critical_count = df["is_critical"].sum()
        if critical_count > 0:
            recommendations.append(
                f"- **Critical incidents present:** {critical_count}. Ensure ABCH summaries are completed and reviewed with the team."
            )

    # Antecedents
    if "antecedent" in df:
        top_antecedent = df["antecedent"].value_counts().idxmax()
        recommendations.append(
            f"- **Common antecedent:** {top_antecedent}. Consider environmental changes or rehearsal of alternative responses."
        )

    # Support type
    if "support_type" in df:
        top_support = df["support_type"].value_counts().idxmax()
        recommendations.append(
            f"- **Most used support type:** {top_support}. Reflect on whether this matches the student's current needs "
            "and promotes increasing independence over time."
        )

    if not recommendations:
        st.info("No specific recommendations can be generated yet – more data is needed.")
    else:
        st.markdown("\n".join(recommendations))


# =========================
#  MAIN
# =========================


def main():
    try:
        initialize_session_state()

        if not st.session_state.get("logged_in", False):
            render_login_page()
            return

        current_page = st.session_state.get("current_page", "landing")

        if current_page == "login":
            render_login_page()
        elif current_page == "landing":
            render_landing_page()
        elif current_page == "program_students":
            render_program_students()
        elif current_page == "direct_log_form":
            render_direct_log_form()
        elif current_page == "critical_incident_abch":
            render_critical_incident_abch_form()
        elif current_page == "student_analysis":
            render_student_analysis()
        elif current_page == "admin_portal":
            render_admin_portal()
        else:
            st.error("Unknown page")
            navigate_to("landing")

    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        st.error("A critical error occurred in the sandbox app.")


if __name__ == "__main__":
    main()
