@handle_errors("Unable to load student analysis")
def render_student_analysis():
    """Renders comprehensive student analysis with visualisations and recommendations."""
    student_id = st.session_state.get("selected_student_id")
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found.")
        if st.button("Return Home"):
            navigate_to("landing")
        return

    # Header
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(
            f"Grade {student['grade']} | {student['program']} Program | "
            f"EDID: {student.get('edid', 'N/A')}"
        )
    with col_back:
        if st.button("⬅ Back"):
            navigate_to("program_students", program=student['program'])

    st.markdown("---")

    # Pull incidents for this student
    student_incidents = [
        inc for inc in st.session_state.incidents
        if inc.get('student_id') == student_id
    ]
    if not student_incidents:
        st.info("No incident data available for this student yet.")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to("direct_log_form", student_id=student_id)
        return

    df = pd.DataFrame(student_incidents)

    # ---- NORMALISE / FEATURE ENGINEERING ----
    # Date
    if 'incident_date' in df.columns:
        df['Date'] = pd.to_datetime(df['incident_date'])
    else:
        df['Date'] = pd.to_datetime(df['date'])

    # Day of week
    if 'day' in df.columns:
        df['Day'] = df['day']
    elif 'day_of_week' in df.columns:
        df['Day'] = df['day_of_week']
    else:
        df['Day'] = df['Date'].dt.day_name()

    # Time & hour
    if 'incident_time' in df.columns:
        df['Time_raw'] = df['incident_time']
    elif 'time' in df.columns:
        df['Time_raw'] = df['time']
    else:
        df['Time_raw'] = None

    def parse_hour(x):
        try:
            return datetime.strptime(x, "%H:%M:%S").hour
        except Exception:
            return None

    df['Hour'] = df['Time_raw'].apply(parse_hour)
    df['HourBucket'] = df['Hour'].apply(
        lambda h: f"{h:02d}:00–{h:02d}:59" if h is not None else "Unknown"
    )

    # Ensure severity numeric
    df['severity'] = pd.to_numeric(df.get('severity', 0), errors='coerce').fillna(0)

    # --------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------
    st.markdown("### 📈 Summary Statistics")

    total_incidents = len(df)
    critical_count = int(df.get('is_critical', False).sum())
    critical_rate = (critical_count / total_incidents * 100) if total_incidents else 0
    avg_sev = df['severity'].mean() if total_incidents else 0

    dates = df['Date'].dropna()
    if len(dates) > 0:
        days_span = (dates.max() - dates.min()).days + 1
    else:
        days_span = 1
    incidents_per_week = (total_incidents / days_span) * 7 if days_span > 0 else 0

    top_behaviour = df['behaviour_type'].value_counts().idxmax() if 'behaviour_type' in df.columns and not df['behaviour_type'].isna().all() else "N/A"
    top_location = df['location'].value_counts().idxmax() if 'location' in df.columns and not df['location'].isna().all() else "N/A"
    top_day = df['Day'].value_counts().idxmax() if not df['Day'].isna().all() else "N/A"
    top_session = df['session'].value_counts().idxmax() if 'session' in df.columns and not df['session'].isna().all() else "N/A"

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Incidents", total_incidents)
    with col2:
        st.metric("Critical (≥3)", critical_count, f"{critical_rate:.0f}%")
    with col3:
        st.metric("Avg Severity", f"{avg_sev:.1f}")
    with col4:
        st.metric("Days Tracked", days_span)
    with col5:
        st.metric("Incidents per Week", f"{incidents_per_week:.1f}")
    with col6:
        st.metric("Most Frequent behaviour", top_behaviour)

    st.markdown("---")

    # --------------------------------------------------
    # TIMELINE & SEVERITY OVER TIME
    # --------------------------------------------------
    st.markdown("### ⏱️ Patterns Over Time")

    daily = df.groupby('Date').size().reset_index(name='Count')
    fig_timeline = px.line(
        daily,
        x='Date',
        y='Count',
        title="Incidents Over Time",
        template=PLOTLY_THEME,
        markers=True,
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Severity over time
    fig_sev_time = px.scatter(
        df.sort_values('Date'),
        x='Date',
        y='severity',
        title="Severity Over Time",
        template=PLOTLY_THEME,
    )
    fig_sev_time.update_traces(mode="lines+markers")
    fig_sev_time.update_yaxes(title="Severity (1–5)", dtick=1)
    st.plotly_chart(fig_sev_time, use_container_width=True)

    # --------------------------------------------------
    # SEVERITY & TIME-OF-DAY DISTRIBUTION
    # --------------------------------------------------
    col_a, col_b = st.columns(2)

    with col_a:
        sev_counts = df['severity'].value_counts().sort_index().reset_index()
        sev_counts.columns = ['Severity', 'Count']
        fig_sev_dist = px.bar(
            sev_counts,
            x='Severity',
            y='Count',
            title="Severity Distribution",
            template=PLOTLY_THEME,
        )
        fig_sev_dist.update_xaxes(dtick=1)
        st.plotly_chart(fig_sev_dist, use_container_width=True)

    with col_b:
        # Hour-of-day profile
        hour_counts = df['HourBucket'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Time Window', 'Count']
        fig_hour = px.bar(
            hour_counts,
            x='Time Window',
            y='Count',
            title="Incidents by Time of Day",
            template=PLOTLY_THEME,
        )
        fig_hour.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_hour, use_container_width=True)

    # --------------------------------------------------
    # DAY x SESSION HEATMAP
    # --------------------------------------------------
    st.markdown("### 📅 When in the Week? (Day × Session)")

    if 'session' in df.columns:
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['Day'] = pd.Categorical(df['Day'], categories=day_order, ordered=True)
        pivot = pd.pivot_table(
            df,
            index='Day',
            columns='session',
            values='id' if 'id' in df.columns else 'student_id',
            aggfunc='count',
            fill_value=0,
        )
        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            title="Incidents by Day of Week and Session",
            aspect="auto",
            template=PLOTLY_THEME,
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No session data available to build Day × Session heatmap.")

    # --------------------------------------------------
    # behaviour / ANTECEDENT / LOCATION / SUPPORT
    # --------------------------------------------------
    st.markdown("### 🧩 What is Happening? (behaviours, Antecedents, Locations)")

    col_c, col_d = st.columns(2)

    with col_c:
        if 'behaviour_type' in df.columns:
            beh_counts = df['behaviour_type'].value_counts().reset_index()
            beh_counts.columns = ['Behaviour', 'Count']
            fig_beh = px.bar(
                beh_counts,
                x='Count',
                y='Behaviour',
                orientation='h',
                title="behaviour Frequency",
                template=PLOTLY_THEME,
            )
            st.plotly_chart(fig_beh, use_container_width=True)

        if 'antecedent' in df.columns:
            ant_counts = df['antecedent'].value_counts().reset_index()
            ant_counts.columns = ['Antecedent (Trigger)', 'Count']
            fig_ant = px.bar(
                ant_counts,
                x='Count',
                y='Antecedent (Trigger)',
                orientation='h',
                title="Top Antecedents (Triggers)",
                template=PLOTLY_THEME,
            )
            st.plotly_chart(fig_ant, use_container_width=True)

    with col_d:
        if 'location' in df.columns:
            loc_counts = df['location'].value_counts().reset_index()
            loc_counts.columns = ['Location', 'Count']
            fig_loc = px.bar(
                loc_counts.head(10),
                x='Count',
                y='Location',
                orientation='h',
                title="Top Incident Locations",
                template=PLOTLY_THEME,
            )
            st.plotly_chart(fig_loc, use_container_width=True)

        if 'support_type' in df.columns:
            sup_counts = df['support_type'].value_counts().reset_index()
            sup_counts.columns = ['Support Type', 'Count']
            fig_sup = px.bar(
                sup_counts,
                x='Support Type',
                y='Count',
                title="Support Context at Time of Incident",
                template=PLOTLY_THEME,
            )
            fig_sup.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_sup, use_container_width=True)

    # --------------------------------------------------
    # ABCH SUMMARY (IF PRESENT)
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("### 📋 ABCH Rows for this Student")

    abch_rows = [
        r for r in st.session_state.critical_abch_records
        if r.get('student_id') == student_id
    ]
    if not abch_rows:
        st.info("No ABCH rows recorded yet for this student.")
    else:
        df_abch = pd.DataFrame([
            {
                "Location": r['location'],
                "Context": r['context'],
                "Time": r['time'],
                "Behaviour": r['behaviour_desc'],
                "Consequences": r['consequence'],
                "Hypothesis": r['hypothesis'],
                "Manager Notified": "Yes" if r['manager_notify'] else "No",
                "Parent Notified": "Yes" if r['parent_notify'] else "No",
                "Recorded": r['created_at'].split("T")[0],
            }
            for r in abch_rows
        ])
        st.dataframe(df_abch, use_container_width=True, hide_index=True)

        # Very simple hypothesis category scan
        def classify_function(text: str) -> str:
            t = text.lower()
            if any(k in t for k in ["attention", "adult", "peer"]):
                return "Attention"
            if any(k in t for k in ["escape", "avoid", "get away", "leave"]):
                return "Escape/Avoidance"
            if any(k in t for k in ["sensory", "noise", "crowd", "bright"]):
                return "Sensory"
            if any(k in t for k in ["item", "object", "tangible", "preferred"]):
                return "Tangible/Activity"
            return "Other/Unclear"

        df_abch['Function Category'] = df_abch['Hypothesis'].apply(classify_function)
        func_counts = df_abch['Function Category'].value_counts().reset_index()
        func_counts.columns = ['Function', 'Count']
        fig_func = px.pie(
            func_counts,
            names='Function',
            values='Count',
            title="Inferred Behaviour Functions (from ABCH hypotheses)",
            template=PLOTLY_THEME,
        )
        st.plotly_chart(fig_func, use_container_width=True)

    # --------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("### 🧠 Data-Informed Recommendations")

    # Prep some additional pattern info
    top_antecedent = df['antecedent'].value_counts().idxmax() if 'antecedent' in df.columns and not df['antecedent'].isna().all() else "N/A"
    top_hour = df['Hour'].value_counts().idxmax() if df['Hour'].notna().any() else None
    hour_string = f"{top_hour:02d}:00–{top_hour:02d}:59" if top_hour is not None else "N/A"

    st.markdown("#### 1. Key Patterns Noted")
    st.markdown(
        f"- **Most frequent behaviour:** {top_behaviour}\n"
        f"- **Most frequent location:** {top_location}\n"
        f"- **Most active time window:** {hour_string}\n"
        f"- **Most common day:** {top_day}\n"
        f"- **Typical session:** {top_session}\n"
        f"- **Most common antecedent (trigger):** {top_antecedent}\n"
        f"- **Critical incidents:** {critical_count} ({critical_rate:.0f}% of all incidents)"
    )

    st.markdown("#### 2. Environmental / Routine Adjustments")
    st.markdown(
        "- Increase **adult presence and proactive check-ins** in the highest-risk location and time window.\n"
        "- Where incidents cluster around transitions or instructions, **front-load information** (visual schedules, countdowns, clear expectations) and offer **choice-based entry** into tasks.\n"
        "- If the same day/session is consistently ‘hot’, consider **lighter cognitive load** or **preferred activities** at that time while skills are being built."
    )

    st.markdown("#### 3. Skills for the Student")
    st.markdown(
        "- Teach and rehearse **2–3 concrete replacement behaviours** that meet the same function as the problem behaviour "
        "(e.g., asking for a break instead of eloping, using a card/gesture to request help).\n"
        "- Embed **co-regulated practice** in calm times: short role-plays of the tricky moments reflected in the ABCH rows.\n"
        "- Pair any success (even partial) with **specific positive feedback** linked to the function: "
        "“You used your break card instead of walking out – that helped you get the quiet space you needed.”"
    )

    st.markdown("#### 4. Staff Response Consistency")
    st.markdown(
        "- Use the ABCH hypotheses to **standardise staff responses**: same cue, same de-escalation steps, same follow-up.\n"
        "- Where attention is part of the function, ensure staff avoid **unintentionally rewarding escalation** and instead "
        "provide attention for early, more regulated communication attempts.\n"
        "- If high severity repeats in the same session, consider a **pre-planned de-escalation pathway** (where to move, who steps in, "
        "how and when peers are moved)."
    )

    st.markdown("#### 5. Family & Transition Planning")
    st.markdown(
        "- Share a **short visual summary** (simple graphs + 3 dot points) with families and, where appropriate, the student.\n"
        "- Use these patterns to inform **transition plans** (e.g., avoid starting new arrangements in the most challenging session/day; "
        "stagger changes and maintain one stable adult).\n"
        "- Revisit data after 4–6 weeks of any plan: look for **reduction in severity**, **shift in functions**, and **increase in "
        "replacement behaviour incidents**."
    )

    st.info(
        "These recommendations are generated from the incident pattern only. "
        "They should always be considered alongside clinical advice, student voice, "
        "family perspectives, and team professional judgement."
    )
