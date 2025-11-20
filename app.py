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
    )
    st.plotly_chart(fig, use_container_width=True)

    # Antecedent frequency
    st.markdown("### 🔥 Antecedent frequency")
    ant_counts = full_df["antecedent"].value_counts().reset_index()
    ant_counts.columns = ["Antecedent", "Count"]
    fig2 = px.bar(ant_counts, x="Count", y="Antecedent", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)

    # Location hotspots
    st.markdown("### 📍 Location hotspots")
    loc_counts = full_df["location"].value_counts().reset_index()
    loc_counts.columns = ["Location", "Count"]
    fig3 = px.bar(loc_counts, x="Count", y="Location", orientation="h")
    st.plotly_chart(fig3, use_container_width=True)

    # Behaviour types
    st.markdown("### ⚠️ Behaviour types")
    beh_counts = full_df["behaviour_type"].value_counts().reset_index()
    beh_counts.columns = ["Behaviour", "Count"]
    fig4 = px.bar(beh_counts, x="Count", y="Behaviour", orientation="h")
    st.plotly_chart(fig4, use_container_width=True)

    # Session patterns
    st.markdown("### 🕒 Session patterns")
    sess_counts = full_df["session"].value_counts().reset_index()
    sess_counts.columns = ["Session", "Count"]
    fig5 = px.bar(sess_counts, x="Session", y="Count")
    st.plotly_chart(fig5, use_container_width=True)

    # =====================================================
    # CLINICAL INTERPRETATION & NEXT STEPS
    # =====================================================
    if not full_df.empty:
        # Key patterns for use in summary / narrative
        top_ant = full_df["antecedent"].mode()[0]
        top_beh = full_df["behaviour_type"].mode()[0]
        top_loc = full_df["location"].mode()[0]
        top_session = full_df["session"].mode()[0]

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
