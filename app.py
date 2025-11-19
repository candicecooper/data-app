from pathlib import Path

content = """# critical_incident_supabase.py
# FULL SUPABASE INTEGRATION FOR CRITICAL INCIDENTS

from supabase import create_client, Client
import logging
from datetime import datetime

# ----------------------------
# CONFIG (replace with your env)
# ----------------------------
SUPABASE_URL = "https://szhebjnxxiwomgediufp.supabase.co"
SUPABASE_KEY = "YOUR_SERVICE_ROLE_OR_ANON_KEY"

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# VALIDATION
# ----------------------------
def validate_critical_incident(record: dict):
    required = [
        "student_id",
        "antecedent",
        "behaviour",
        "consequence",
        "hypothesis",
        "safety_responses",
        "notifications",
        "recommendations"
    ]
    missing = [f for f in required if not record.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

# ----------------------------
# INSERT FUNCTION
# ----------------------------
def insert_critical_incident(record: dict) -> dict:
    validate_critical_incident(record)

    supabase = get_supabase_client()

    payload = {
        "id": record.get("id"),
        "created_at": datetime.now().isoformat(),
        "student_id": record.get("student_id"),
        "quick_incident_id": record.get("quick_incident_id"),

        "antecedent": record.get("antecedent"),
        "behaviour": record.get("behaviour"),
        "consequence": record.get("consequence"),
        "hypothesis": record.get("hypothesis"),

        "safety_responses": record.get("safety_responses"),
        "notifications": record.get("notifications"),
        "outcomes": record.get("outcomes"),
        "recommendations": record.get("recommendations")
    }

    try:
        response = supabase.table("critical_incidents").insert(payload).execute()
        if response.data:
            return response.data[0]
        else:
            raise RuntimeError("No data returned from Supabase")
    except Exception as e:
        logging.error(f"Supabase insert failed: {e}")
        raise

"""

path = "/mnt/data/critical_incident_supabase.py"
Path(path).write_text(content)

path
from pathlib import Path

content = """# section4_critical_incident.py
# FULL CRITICAL INCIDENT ABCH FORM (PRODUCTION VERSION)
# -----------------------------------------------------

import streamlit as st
from datetime import datetime
import uuid
from critical_incident_supabase import insert_critical_incident

# ===========================================================
# MAIN ENTRY POINT
# ===========================================================
def render_critical_incident_form(quick_incident=None, sandbox=True):

    st.title("🚨 Critical Incident ABCH Form")
    st.caption("Severity 4–5 | Critical Incident | ABCH Framework")

    # -------------------------------------------------------
    # Preload quick incident data
    # -------------------------------------------------------
    if quick_incident:
        st.success("Quick incident auto-loaded.")
        with st.expander("View quick incident details"):
            st.json(quick_incident)

    # =======================================================
    # ABCH SECTION (4 COLUMNS)
    # =======================================================
    st.markdown("## 🧩 ABCH Breakdown")

    colA, colB, colC, colH = st.columns(4)

    # A — Antecedent
    with colA:
        st.subheader("A — Antecedent")
        antecedent = st.text_area(
            "What happened before?",
            value=quick_incident.get("antecedent", "") if quick_incident else "",
            key="abch_A"
        )
        st.caption(_suggest_antecedent(quick_incident))

    # B — Behaviour
    with colB:
        st.subheader("B — Behaviour")
        behaviour = st.text_area(
            "What the student did",
            value=quick_incident.get("behaviour_type", "") if quick_incident else "",
            key="abch_B"
        )
        st.caption(_suggest_behaviour(quick_incident))

    # C — Consequence
    with colC:
        st.subheader("C — Consequence")
        consequence = st.text_area(
            "What happened after?",
            key="abch_C"
        )
        st.caption("Describe natural & staff-imposed consequences.")

    # H — Hypothesis
    with colH:
        st.subheader("H — Hypothesis")
        hypo_suggest = _suggest_hypothesis(quick_incident)
        st.info(f"Suggested: {hypo_suggest}")
        hypothesis = st.text_area(
            "Why did this occur?",
            value=hypo_suggest,
            key="abch_H"
        )

    st.markdown("---")

    # =======================================================
    # SAFETY RESPONSES
    # =======================================================
    st.markdown("## 🛡️ Safety Responses (Non-Restraint, CPI-Aligned)")

    safety_responses = st.multiselect(
        "Select safety actions:",
        [
            "CPI Supportive Stance",
            "Cleared nearby students",
            "Student moved to safer location",
            "Additional staff attended",
            "Safety plan enacted",
            "Continued monitoring",
            "First aid offered"
        ],
        key="safety_responses"
    )

    st.markdown("---")

    # =======================================================
    # NOTIFICATIONS
    # =======================================================
    st.markdown("## 📣 Notifications")

    notifications = st.multiselect(
        "Select notifications made:",
        [
            "Parent/Carer Notified",
            "Line Manager Notified",
            "Safety & Wellbeing / SSS Notified",
            "DCP Notified",
            "SAPOL Notified",
            "First Aid Provided",
            "Injury Report Completed",
            "Transport Home Required"
        ],
        key="notifications"
    )

    st.markdown("---")

    # =======================================================
    # OUTCOME TABLE
    # =======================================================
    st.markdown("## 🧾 Outcome Actions")

    removed = st.checkbox("Removed from learning")
    family_contact = st.checkbox("Family contacted")
    safety_updated = st.checkbox("Safety plan updated")
    transport_home = st.checkbox("Transport home required")
    other_actions = st.text_area("Other actions", key="other_actions")

    st.markdown("---")

    # =======================================================
    # RECOMMENDATIONS
    # =======================================================
    st.markdown("## 🎯 Trauma-Informed Recommendations (Auto-Generated)")

    rec_text = _suggest_recommendations(quick_incident)
    st.info(rec_text)

    recommendations = st.text_area(
        "Edit recommendations if needed",
        value=rec_text,
        key="recommendations"
    )

    st.markdown("---")

    # =======================================================
    # SUBMIT FORM
    # =======================================================
    if st.button("💾 Submit Critical Incident", type="primary"):

        record = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),

            "student_id": quick_incident.get("student_id") if quick_incident else None,
            "quick_incident_id": quick_incident.get("id") if quick_incident else None,

            "antecedent": antecedent,
            "behaviour": behaviour,
            "consequence": consequence,
            "hypothesis": hypothesis,

            "safety_responses": safety_responses,
            "notifications": notifications,

            "outcomes": {
                "removed": removed,
                "family_contact": family_contact,
                "safety_updated": safety_updated,
                "transport_home": transport_home,
                "other": other_actions,
            },

            "recommendations": recommendations
        }

        if sandbox:
            st.success("Critical Incident saved (Sandbox Mode).")
            with st.expander("View Saved Record"):
                st.json(record)
        else:
            saved = insert_critical_incident(record)
            st.success("Critical Incident saved to Supabase.")
            st.json(saved)

        return record


# ===========================================================
# SUGGESTION ENGINE LOGIC
# ===========================================================

def _suggest_antecedent(inc):
    if not inc:
        return "Common triggers: transitions, task demands, sensory overload, peer conflict."
    return f"Pattern: Similar antecedents occur during '{inc.get('antecedent','transitions')}'."

def _suggest_behaviour(inc):
    if not inc:
        return "Describe observable behaviour (per CPI guidelines)."
    return f"Behaviour consistent with previous incidents involving {inc.get('behaviour_type')}."

def _suggest_hypothesis(inc):
    if not inc:
        return ("Behaviour likely serves a function such as escape, attention, sensory need, "
                "or attempting to regain control.")
    ant = inc.get("antecedent", "a known trigger")
    beh = inc.get("behaviour_type", "behaviour")
    return (f"Given antecedent '{ant}' and behaviour '{beh}', the likely function relates to escape, "
            "sensory regulation, or maintaining control.")

def _suggest_recommendations(inc):
    if not inc:
        return (
            "Increase predictability and co-regulation. Use CPI Supportive stance early in escalation. "
            "Embed Berry Street Body/Relationship strategies, and link adjustments to General Capabilities."
        )

    antecedent = inc.get("antecedent", "known triggers")
    behaviour = inc.get("behaviour_type", "behaviour of concern")

    return (
        f"The incident triggered by {antecedent} suggests challenges with transitions or task demands. "
        f"Consider embedding co-regulation strategies earlier, and link staff practice to CPI’s Supportive stance. "
        f"Behaviour '{behaviour}' indicates a need for predictable routines, grounding strategies (Berry Street Body), "
        "and reduced cognitive load during peak stress times.\n\n"
        "Link supports to Personal & Social Capability within the Australian Curriculum, and establish SMART goals "
        "for emotional regulation. Regular relational check-ins and proactive adjustments should continue."
    )
"""

# write file
path = "/mnt/data/section4_critical_incident.py"
Path(path).write_text(content)

path
from pathlib import Path

content = """# student_analysis_full.py
# UNIFIED ANALYTICS DASHBOARD FOR QUICK + CRITICAL INCIDENTS
# --------------------------------------------------------------------
# This module provides:
# • Combined dataset merging quick + critical incidents
# • Detailed graphs (Plotly)
# • Pattern detection engine
# • Trauma-informed analysis (CPI, BSEM)
# • ACARA General Capabilities mapping
# • SMART recommendation hooks

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ===========================================================
# MAIN ENTRY POINT
# ===========================================================
def render_student_analysis_full(student, quick_incidents, critical_incidents):
    st.title(f"📊 Unified Analysis for {student.get('name')}")

    # -------------------------------------------------------
    # Convert Quick + Critical datasets
    # -------------------------------------------------------
    qi = pd.DataFrame(quick_incidents) if quick_incidents else pd.DataFrame()
    ci = pd.DataFrame(critical_incidents) if critical_incidents else pd.DataFrame()

    if qi.empty and ci.empty:
        st.info("No incident data available.")
        return

    # Add type labels
    if not qi.empty:
        qi["incident_type"] = "Quick"
    if not ci.empty:
        ci["incident_type"] = "Critical"

    # Standardise fields for merging
    if not ci.empty:
        ci["behaviour_type"] = ci.get("behaviour", "")
        ci["antecedent"] = ci.get("antecedent", "")
        ci["location"] = ci.get("location", "Unknown")
        ci["severity"] = 5  # Critical default severity

    full_df = pd.concat([qi, ci], ignore_index=True)

    # Normalize dates
    if "date" in full_df.columns:
        full_df["date"] = pd.to_datetime(full_df["date"], errors="coerce")
    if "incident_date" in full_df.columns:
        full_df["incident_date"] = pd.to_datetime(full_df["incident_date"], errors="coerce")
        full_df["date"] = full_df["incident_date"]

    st.markdown("### Overall Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Incidents", len(full_df))
    with col2:
        st.metric("Critical Incidents", len(full_df[full_df["incident_type"] == "Critical"]))
    with col3:
        st.metric("Avg Severity", round(full_df.get("severity", pd.Series([0])).mean(), 1))

    st.markdown("---")

    # =======================================================
    # TIMELINE GRAPH
    # =======================================================
    st.subheader("📅 Incident Timeline (Quick vs Critical)")
    if "date" in full_df:
        fig = px.scatter(
            full_df,
            x="date",
            y="severity",
            color="incident_type",
            title="Severity Over Time",
            hover_data=["behaviour_type", "antecedent"]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =======================================================
    # ANTECEDENT FREQUENCY
    # =======================================================
    st.subheader("🔥 Antecedent Frequency")
    if "antecedent" in full_df:
        ant_counts = full_df["antecedent"].value_counts().reset_index()
        ant_counts.columns = ["Antecedent", "Count"]
        fig = px.bar(ant_counts, x="Count", y="Antecedent", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =======================================================
    # LOCATION HOTSPOTS
    # =======================================================
    st.subheader("📍 Location Hotspots")
    if "location" in full_df:
        loc_counts = full_df["location"].value_counts().reset_index()
        loc_counts.columns = ["Location", "Count"]
        fig = px.bar(loc_counts, x="Count", y="Location", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =======================================================
    # BEHAVIOUR TYPES
    # =======================================================
    st.subheader("⚠️ Behaviour Types")
    if "behaviour_type" in full_df:
        beh_counts = full_df["behaviour_type"].value_counts().reset_index()
        beh_counts.columns = ["Behaviour", "Count"]
        fig = px.bar(beh_counts, x="Count", y="Behaviour", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =======================================================
    # PATTERN DETECTION
    # =======================================================
    st.subheader("🔎 Pattern Detection")

    patterns = []

    # Frequent antecedent
    if not full_df["antecedent"].empty:
        top_ant = full_df["antecedent"].mode()[0]
        patterns.append(f"Most frequent antecedent: **{top_ant}**")

    # Frequent behaviour
    if not full_df["behaviour_type"].empty:
        top_beh = full_df["behaviour_type"].mode()[0]
        patterns.append(f"Most common behaviour: **{top_beh}**")

    # Hotspot location
    if not full_df["location"].empty:
        top_loc = full_df["location"].mode()[0]
        patterns.append(f"Hotspot location: **{top_loc}**")

    # Severity average
    avg_sev = full_df["severity"].mean()
    patterns.append(f"Average severity: **{round(avg_sev,1)}**")

    for p in patterns:
        st.markdown(f"- {p}")

    st.markdown("---")

    # =======================================================
    # TRAUMA-INFORMED ANALYSIS
    # =======================================================
    st.subheader("🧠 Trauma-Informed Interpretation")

    ti = _generate_trauma_analysis(patterns)
    st.info(ti)

    # =======================================================
    # RECOMMENDATIONS
    # =======================================================
    st.subheader("🎯 Recommendations (ACARA, CPI, BSEM, SMART aligned)")

    rec = _generate_recommendations(patterns)
    st.success(rec)

# ===========================================================
# TRAUMA-INFORMED ANALYSIS
# ===========================================================
def _generate_trauma_analysis(patterns):
    return (
        "Patterns show predictable triggers aligned with escalation patterns. "
        "Using CPI: Stay in the Supportive phase early, reinforce connection, reduce demands. "
        "Berry Street (Body + Relationship): Co-regulation, predictable routines, sensory supports."
    )

# ===========================================================
# RECOMMENDATIONS ENGINE
# ===========================================================
def _generate_recommendations(patterns):
    return (
        "Embed proactive co-regulation routines, teach emotional literacy, and adjust workload. "
        "Use SMART goals to target behaviour replacement skills. Link to Personal & Social Capability "
        "in the Australian Curriculum. Ensure staff scripts align with CPI guidance."
    )
"""

# write file
path = "/mnt/data/student_analysis_full.py"
Path(path).write_text(content)

path
from pathlib import Path

content = """# app_integrator.py
# Connects all modules together:
# • Quick incident → Critical incident workflow
# • Student analysis page
# • Navigation + session state
# • Sandbox indicators

import streamlit as st
from section4_critical_incident import render_critical_incident_form
from student_analysis_full import render_student_analysis_full

# Placeholder imports for quick incident + student load
# Replace these with your actual data sources
def load_quick_incidents(student_id):
    return []

def load_critical_incidents(student_id):
    return []

def load_student(student_id):
    return {"id": student_id, "name": "Demo Student"}

# ================================================================
# MAIN NAVIGATION WRAPPER
# ================================================================
def init_navigation():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "current_student_id" not in st.session_state:
        st.session_state.current_student_id = None
    if "pending_quick_incident" not in st.session_state:
        st.session_state.pending_quick_incident = None

def go_to(page):
    st.session_state.page = page
    st.experimental_rerun()

# ================================================================
# HOME PAGE
# ================================================================
def render_home():
    st.title("CLC Behaviour App (Sandbox Version)")
    st.caption("All data shown here is demo-only.")

    st.markdown("### Navigation")
    if st.button("Student Analysis Demo"):
        st.session_state.current_student_id = "demo123"
        go_to("analysis")

    if st.button("Start Critical Incident Demo"):
        st.session_state.pending_quick_incident = {
            "id": "quick123",
            "student_id": "demo123",
            "antecedent": "Transition to activity",
            "behaviour_type": "Verbal aggression",
            "description": "Student became elevated during transition",
            "location": "Classroom",
            "severity": 5
        }
        go_to("critical")

# ================================================================
# PAGE: CRITICAL INCIDENT
# ================================================================
def render_critical_page():
    qi = st.session_state.pending_quick_incident
    record = render_critical_incident_form(qi, sandbox=True)

    if record:
        if st.button("Return to Home"):
            go_to("home")
        if st.button("Go to Analysis"):
            go_to("analysis")

# ================================================================
# PAGE: STUDENT ANALYSIS
# ================================================================
def render_analysis_page():
    student_id = st.session_state.current_student_id
    student = load_student(student_id)
    qi = load_quick_incidents(student_id)
    ci = load_critical_incidents(student_id)

    render_student_analysis_full(student, qi, ci)

    if st.button("Return to Home"):
        go_to("home")

# ================================================================
# ROUTER
# ================================================================
def run_app():
    init_navigation()

    page = st.session_state.page

    if page == "home":
        render_home()
    elif page == "critical":
        render_critical_page()
    elif page == "analysis":
        render_analysis_page()
    else:
        st.error("Unknown page.")

"""

path = "/mnt/data/app_integrator.py"
Path(path).write_text(content)

path
from section4_critical_incident import render_critical_incident_form
from student_analysis_full import render_student_analysis_full
