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

    # --- Collect student records ---
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]

    if not quick and not crit:
        st.info("No incident data yet for this student.")
        if st.button("Log first incident"):
            go_to("incident_log", selected_student_id=student_id)
        return

    # --- Build unified dataframe safely ---
    quick_df = pd.DataFrame(quick) if quick else pd.DataFrame()
    crit_df = pd.DataFrame(crit) if crit else pd.DataFrame()

    if not quick_df.empty:
        quick_df["incident_type"] = "Quick"
        quick_df["date_parsed"] = pd.to_datetime(quick_df["date"], errors="coerce")

    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        crit_df["date_parsed"] = pd.to_datetime(
            crit_df.get("created_at", datetime.now()), errors="coerce"
        )
        crit_df["severity"] = 5

        # Extract ABCH
        def safe_ABCH(d, key):
            if isinstance(d, dict) and key in d:
                return d[key]
            return ""

        crit_df["antecedent"] = crit_df["ABCH_primary"].apply(lambda d: safe_ABCH(d, "A"))
        crit_df["behaviour_type"] = crit_df["ABCH_primary"].apply(lambda d: safe_ABCH(d, "B"))

        # Use last quick data for graph alignment
        if not quick_df.empty:
            crit_df["location"] = quick_df["location"].iloc[0]
            crit_df["session"] = quick_df["session"].iloc[0]
        else:
            crit_df["location"] = "Unknown"
            crit_df["session"] = "Unknown"

    full_df = pd.concat([quick_df, crit_df], ignore_index=True)

    # --- Required columns with fallback ---
    def safe_mode(col):
        try:
            return full_df[col].dropna().mode().iloc[0]
        except Exception:
            return "Unknown"

    def safe_mean(col):
        try:
            return float(full_df[col].dropna().astype(float).mean())
        except Exception:
            return 0

    # Summary
    total = len(full_df)
    crit_total = len(full_df[full_df["incident_type"] == "Critical"])
    quick_total = total - crit_total
    avg_sev = safe_mean("severity")

    # Safe mode values
    top_ant = safe_mode("antecedent")
    top_beh = safe_mode("behaviour_type")
    top_loc = safe_mode("location")
    top_session = safe_mode("session")

    # Date span
    try:
        days_span = (full_df["date_parsed"].max() - full_df["date_parsed"].min()).days + 1
    except Exception:
        days_span = "Unknown"

    crit_rate = (crit_total / total * 100) if total > 0 else 0

    # --- Summary metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total incidents", total)
    col2.metric("Critical incidents", crit_total)
    col3.metric("Avg severity", round(avg_sev, 1))
    col4.metric("Days tracked", days_span)

    st.markdown("---")

    # ==================================================
    # VISUALISATIONS
    # ==================================================

    st.markdown("### ⏱️ Severity Over Time")
    fig = px.scatter(
        full_df,
        x="date_parsed",
        y="severity",
        color="incident_type",
        hover_data=["antecedent", "behaviour_type", "location"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔥 Antecedent Frequency")
    ant_counts = full_df["antecedent"].value_counts().reset_index()
    ant_counts.columns = ["Antecedent", "Count"]
    st.plotly_chart(px.bar(ant_counts, x="Count", y="Antecedent", orientation="h"), use_container_width=True)

    st.markdown("### 📍 Location Hotspots")
    loc_counts = full_df["location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    st.plotly_chart(px.bar(loc_counts, x="Count", y="Location", orientation="h"), use_container_width=True)

    st.markdown("### ⚠ Behaviour Types")
    beh_counts = full_df["behaviour_type"].value_counts().reset_index()
    beh_counts.columns = ["Behaviour", "Count"]
    st.plotly_chart(px.bar(beh_counts, x="Count", y="Behaviour", orientation="h"), use_container_width=True)

    st.markdown("### 🕒 Session Patterns")
    sess_counts = full_df["session"].value_counts().reset_index()
    sess_counts.columns = ["Session", "Count"]
    st.plotly_chart(px.bar(sess_counts, x="Session", y="Count"), use_container_width=True)

    st.markdown("---")

    # ==================================================
    # CLINICAL INTERPRETATION
    # ==================================================

    st.markdown("## 🧠 Clinical Interpretation & Next Steps")
    st.markdown("### 1. Summary of Findings")

    st.markdown(
        f"""
- **Primary behaviour:** **{top_beh}**  
- **Most common trigger:** **{top_ant}**  
- **Hotspot location:** **{top_loc}**  
- **Most challenging session:** **{top_session}**  
- **Critical incidents:** {crit_total} of {total} (**{crit_rate:.1f}%**)  
- **Severity trend:** Based on data over {days_span} day(s)
"""
    )

    st.markdown("### 2. Trauma-Informed Interpretation")
    st.info(
        f"""
Patterns indicate that **{student['name']}** is most vulnerable during **{top_session}**
and when **{top_ant}** occurs. These conditions likely narrow their *window of tolerance*, 
increasing the chance of a survival-based response (fight/flight/freeze).

- CPI emphasises early **Supportive Stance** to prevent escalation.  
- Berry Street Education Model highlights predictable routines, relational safety, 
  and co-regulation as protective factors.  
- SMART trauma principles suggest reducing cognitive load, providing cues, and 
  maximising predictability during known trigger times.
"""
    )

    st.markdown("### 3. Recommendations (BSEM, CPI, SMART, ACARA)")

    st.success(
        f"""
**A. Proactive Support (BSEM Body & Stamina)**  
- Use short regulation breaks before **{top_ant}**.  
- Provide movement/sensory options in **{top_loc}**.  

**B. Co-Regulation (CPI)**  
- Use calm tone and body position.  
- Reduce audience, maintain connection with one adult.  

**C. Skills Teaching (Australian Curriculum – General Capabilities)**  
- Teach help-seeking scripts linked to self-management.  
- Use visuals, choice boards, reduced verbal load.  

**D. SMART Goal Example**  
- *Over 5 weeks, when faced with {top_ant}, {student['name']} will use a help-seeking strategy  
  in 4/5 opportunities with co-regulation support.*
"""
    )

    if st.button("⬅ Back to students"):
        go_to("program_students", selected_program=student["program"])
