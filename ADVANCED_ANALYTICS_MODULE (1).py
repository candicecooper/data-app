# =========================================
# ADVANCED ANALYTICS MODULE
# Add this section to your sandbox app
# =========================================

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter

def render_advanced_student_analysis(student_id: str):
    """
    Comprehensive analytics dashboard with 15+ visualizations
    """
    student = get_student(student_id)
    if not student:
        st.error("No student selected.")
        return

    st.markdown(f"## 📊 Advanced Data Analysis — {student['name']}")
    st.caption(f"{student['program']} program | Grade {student['grade']}")

    # Get incidents
    quick = [i for i in st.session_state.incidents if i["student_id"] == student_id]
    crit = [c for c in st.session_state.critical_incidents if c["student_id"] == student_id]

    if not quick and not crit:
        st.info("No incident data yet for this student.")
        return

    # Build unified dataframe
    quick_df = pd.DataFrame(quick) if quick else pd.DataFrame()
    crit_df = pd.DataFrame(crit) if crit else pd.DataFrame()

    if not quick_df.empty:
        quick_df["incident_type"] = "Quick"
        quick_df["date_parsed"] = pd.to_datetime(quick_df["date"])

    if not crit_df.empty:
        crit_df["incident_type"] = "Critical"
        if "created_at" in crit_df.columns:
            crit_df["date_parsed"] = pd.to_datetime(crit_df["created_at"])
        else:
            crit_df["date_parsed"] = pd.to_datetime(datetime.now().isoformat())
        crit_df["severity"] = 5
        crit_df["antecedent"] = crit_df["ABCH_primary"].apply(
            lambda d: d.get("A") if isinstance(d, dict) else ""
        )
        crit_df["behaviour_type"] = crit_df["ABCH_primary"].apply(
            lambda d: d.get("B") if isinstance(d, dict) else ""
        )

    full_df = pd.concat([quick_df, crit_df], ignore_index=True)
    full_df = full_df.sort_values("date_parsed")

    # ==============================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ==============================================
    st.markdown("## 📈 Executive Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Incidents", len(full_df))
    with col2:
        critical_count = len(full_df[full_df["incident_type"] == "Critical"])
        st.metric("Critical", critical_count)
    with col3:
        avg_sev = round(full_df["severity"].mean(), 2)
        st.metric("Avg Severity", avg_sev)
    with col4:
        days_span = (full_df["date_parsed"].max() - full_df["date_parsed"].min()).days + 1
        st.metric("Days Tracked", days_span)
    with col5:
        incidents_per_day = round(len(full_df) / days_span, 2)
        st.metric("Inc/Day", incidents_per_day)

    # Trend indicator
    if len(full_df) >= 2:
        recent_avg = full_df.tail(5)["severity"].mean()
        older_avg = full_df.head(5)["severity"].mean()
        trend = "📈 Increasing" if recent_avg > older_avg else "📉 Decreasing" if recent_avg < older_avg else "➡️ Stable"
        st.info(f"**Severity Trend (last 5 vs first 5):** {trend}")

    st.markdown("---")

    # ==============================================
    # SECTION 2: TIME-SERIES ANALYSIS
    # ==============================================
    st.markdown("## ⏰ Time-Series Analysis")

    # 2.1 Daily incident frequency
    st.markdown("### 📅 Incident Frequency Over Time")
    daily_counts = full_df.groupby(full_df["date_parsed"].dt.date).size().reset_index(name="count")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=daily_counts["date_parsed"],
        y=daily_counts["count"],
        mode='lines+markers',
        name='Incidents per day',
        line=dict(color='#3b82f6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)'
    ))
    fig1.update_layout(
        title="Daily Incident Count",
        xaxis_title="Date",
        yaxis_title="Number of Incidents",
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # 2.2 Moving average (7-day)
    if len(full_df) >= 7:
        st.markdown("### 📊 7-Day Moving Average (Smoothed Trend)")
        full_df["date_only"] = full_df["date_parsed"].dt.date
        daily = full_df.groupby("date_only").size().reset_index(name="count")
        daily["7d_avg"] = daily["count"].rolling(window=7, min_periods=1).mean()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily["date_only"],
            y=daily["count"],
            mode='lines',
            name='Daily count',
            line=dict(color='lightgray', width=1)
        ))
        fig2.add_trace(go.Scatter(
            x=daily["date_only"],
            y=daily["7d_avg"],
            mode='lines',
            name='7-day average',
            line=dict(color='#ef4444', width=3)
        ))
        fig2.update_layout(
            title="Trend Analysis (7-Day Moving Average)",
            xaxis_title="Date",
            yaxis_title="Incidents",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 2.3 Severity timeline with annotations
    st.markdown("### 🎯 Severity Timeline (with Critical Incidents Highlighted)")
    fig3 = go.Figure()
    
    # Regular incidents
    quick_only = full_df[full_df["incident_type"] == "Quick"]
    crit_only = full_df[full_df["incident_type"] == "Critical"]
    
    if not quick_only.empty:
        fig3.add_trace(go.Scatter(
            x=quick_only["date_parsed"],
            y=quick_only["severity"],
            mode='markers',
            name='Quick Incident',
            marker=dict(size=10, color='#3b82f6', opacity=0.6),
            hovertemplate='%{y} - %{text}<extra></extra>',
            text=quick_only["behaviour_type"]
        ))
    
    if not crit_only.empty:
        fig3.add_trace(go.Scatter(
            x=crit_only["date_parsed"],
            y=crit_only["severity"],
            mode='markers',
            name='Critical Incident',
            marker=dict(size=15, color='#ef4444', symbol='star'),
            hovertemplate='CRITICAL: %{text}<extra></extra>',
            text=crit_only["behaviour_type"]
        ))
    
    fig3.update_layout(
        title="Severity Over Time (Quick vs Critical)",
        xaxis_title="Date",
        yaxis_title="Severity Level",
        yaxis=dict(range=[0, 6])
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ==============================================
    # SECTION 3: HEATMAPS & PATTERN ANALYSIS
    # ==============================================
    st.markdown("## 🔥 Heatmaps & Pattern Analysis")

    # 3.1 Day of week vs Time of day heatmap
    st.markdown("### 🗓️ Day-of-Week × Time-of-Day Heatmap")
    full_df["hour"] = pd.to_datetime(full_df["time"], format="%H:%M:%S", errors="coerce").dt.hour
    full_df["day_of_week"] = full_df["date_parsed"].dt.day_name()
    
    # Create pivot table
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = full_df.pivot_table(
        values="severity",
        index="day_of_week",
        columns="hour",
        aggfunc="count",
        fill_value=0
    )
    pivot = pivot.reindex(day_order, fill_value=0)
    
    fig4 = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Reds',
        hovertemplate='%{y}, %{x}:00<br>Incidents: %{z}<extra></extra>'
    ))
    fig4.update_layout(
        title="Incident Frequency by Day & Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # 3.2 Location vs Session heatmap
    st.markdown("### 📍 Location × Session Heatmap")
    loc_sess_pivot = full_df.pivot_table(
        values="severity",
        index="location",
        columns="session",
        aggfunc="count",
        fill_value=0
    )
    
    fig5 = go.Figure(data=go.Heatmap(
        z=loc_sess_pivot.values,
        x=loc_sess_pivot.columns,
        y=loc_sess_pivot.index,
        colorscale='YlOrRd',
        hovertemplate='%{y} during %{x}<br>Incidents: %{z}<extra></extra>'
    ))
    fig5.update_layout(
        title="Location Hotspots by Session",
        xaxis_title="Session",
        yaxis_title="Location"
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")

    # ==============================================
    # SECTION 4: BEHAVIOUR PATTERN ANALYSIS
    # ==============================================
    st.markdown("## 🧩 Behaviour Pattern Analysis")

    # 4.1 Antecedent-Behaviour co-occurrence
    st.markdown("### 🔗 Antecedent → Behaviour Patterns")
    
    ant_beh_counts = full_df.groupby(["antecedent", "behaviour_type"]).size().reset_index(name="count")
    ant_beh_counts = ant_beh_counts.sort_values("count", ascending=False).head(15)
    
    fig6 = go.Figure(data=[go.Bar(
        x=ant_beh_counts["count"],
        y=[f"{row['antecedent'][:30]}... → {row['behaviour_type']}" 
           for _, row in ant_beh_counts.iterrows()],
        orientation='h',
        marker=dict(
            color=ant_beh_counts["count"],
            colorscale='Viridis'
        )
    )])
    fig6.update_layout(
        title="Top 15 Antecedent → Behaviour Pairs",
        xaxis_title="Frequency",
        yaxis_title="Pattern"
    )
    st.plotly_chart(fig6, use_container_width=True)

    # 4.2 Behaviour type distribution (pie chart)
    st.markdown("### 🥧 Behaviour Type Distribution")
    beh_counts = full_df["behaviour_type"].value_counts()
    
    fig7 = go.Figure(data=[go.Pie(
        labels=beh_counts.index,
        values=beh_counts.values,
        hole=0.3,
        marker=dict(colors=['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'])
    )])
    fig7.update_layout(title="Behaviour Type Breakdown")
    st.plotly_chart(fig7, use_container_width=True)

    # 4.3 Behaviour chains (sequences)
    st.markdown("### 🔄 Behaviour Sequences (What Follows What)")
    if len(full_df) >= 3:
        full_df_sorted = full_df.sort_values("date_parsed")
        sequences = []
        for i in range(len(full_df_sorted) - 1):
            curr = full_df_sorted.iloc[i]["behaviour_type"]
            next_beh = full_df_sorted.iloc[i + 1]["behaviour_type"]
            sequences.append(f"{curr} → {next_beh}")
        
        seq_counts = pd.Series(sequences).value_counts().head(10)
        
        fig8 = go.Figure(data=[go.Bar(
            x=seq_counts.values,
            y=seq_counts.index,
            orientation='h',
            marker=dict(color='#8b5cf6')
        )])
        fig8.update_layout(
            title="Top 10 Behaviour Sequences",
            xaxis_title="Frequency",
            yaxis_title="Sequence"
        )
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("---")

    # ==============================================
    # SECTION 5: INTERVENTION EFFECTIVENESS
    # ==============================================
    st.markdown("## 🎯 Intervention Effectiveness Analysis")

    # 5.1 Intervention vs Severity (does intervention correlate with lower severity?)
    st.markdown("### 📊 Intervention Success Rate (Severity Reduction)")
    
    interv_sev = full_df.groupby("intervention").agg({
        "severity": ["mean", "count"]
    }).reset_index()
    interv_sev.columns = ["intervention", "avg_severity", "count"]
    interv_sev = interv_sev[interv_sev["count"] >= 2]  # Only interventions used 2+ times
    interv_sev = interv_sev.sort_values("avg_severity")
    
    fig9 = go.Figure()
    fig9.add_trace(go.Bar(
        x=interv_sev["avg_severity"],
        y=interv_sev["intervention"],
        orientation='h',
        marker=dict(
            color=interv_sev["avg_severity"],
            colorscale='RdYlGn',
            reversescale=True,
            cmin=1,
            cmax=5
        ),
        text=interv_sev["count"],
        texttemplate='n=%{text}',
        textposition='outside'
    ))
    fig9.update_layout(
        title="Average Severity by Intervention Type (Lower = More Effective)",
        xaxis_title="Average Severity",
        yaxis_title="Intervention",
        xaxis=dict(range=[0, 5.5])
    )
    st.plotly_chart(fig9, use_container_width=True)

    # 5.2 Duration analysis
    if "duration_minutes" in full_df.columns:
        st.markdown("### ⏱️ Incident Duration Analysis")
        
        fig10 = go.Figure()
        fig10.add_trace(go.Box(
            y=full_df["duration_minutes"],
            x=full_df["behaviour_type"],
            marker=dict(color='#3b82f6')
        ))
        fig10.update_layout(
            title="Duration Distribution by Behaviour Type",
            xaxis_title="Behaviour Type",
            yaxis_title="Duration (minutes)"
        )
        fig10.update_xaxes(tickangle=-45)
        st.plotly_chart(fig10, use_container_width=True)

    st.markdown("---")

    # ==============================================
    # SECTION 6: PREDICTIVE INDICATORS
    # ==============================================
    st.markdown("## 🔮 Predictive Indicators & Risk Analysis")

    # 6.1 Escalation pattern detection
    st.markdown("### ⚠️ Escalation Pattern Detection")
    
    # Look at severity changes
    full_df["severity_change"] = full_df["severity"].diff()
    escalations = full_df[full_df["severity_change"] > 0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Escalation Events", len(escalations))
        st.caption("Times when severity increased from previous incident")
    with col2:
        if len(escalations) > 0:
            avg_escalation = escalations["severity_change"].mean()
            st.metric("Avg Escalation Jump", f"+{avg_escalation:.1f}")
        else:
            st.metric("Avg Escalation Jump", "N/A")

    # 6.2 Risk score calculation
    st.markdown("### 🎲 Current Risk Assessment")
    
    # Calculate risk factors
    recent_incidents = full_df.tail(5)
    risk_factors = {
        "Recent frequency": len(full_df.tail(7)) / 7,  # Last 7 days average
        "Recent avg severity": recent_incidents["severity"].mean(),
        "Critical incident rate": (len(full_df[full_df["incident_type"] == "Critical"]) / len(full_df)) * 100,
        "Escalation trend": 1 if len(full_df) >= 2 and full_df.tail(5)["severity"].mean() > full_df.head(5)["severity"].mean() else 0
    }
    
    # Simple risk score (0-100)
    risk_score = min(100, int(
        (risk_factors["Recent frequency"] * 10) +
        (risk_factors["Recent avg severity"] * 8) +
        (risk_factors["Critical incident rate"] * 0.5) +
        (risk_factors["Escalation trend"] * 20)
    ))
    
    # Color code
    risk_color = "#10b981" if risk_score < 30 else "#f59e0b" if risk_score < 60 else "#ef4444"
    risk_level = "LOW" if risk_score < 30 else "MODERATE" if risk_score < 60 else "HIGH"
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### Overall Risk Score: <span style='color:{risk_color}; font-size:2em;'>{risk_score}/100</span>", 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f"### Level: <span style='color:{risk_color};'>{risk_level}</span>", 
                   unsafe_allow_html=True)
    
    with st.expander("📊 Risk Factor Breakdown"):
        for factor, value in risk_factors.items():
            st.metric(factor, f"{value:.2f}")

    st.markdown("---")

    # ==============================================
    # SECTION 7: COMPARATIVE ANALYSIS
    # ==============================================
    st.markdown("## 📐 Comparative Analysis")

    # 7.1 Student vs Program Average
    st.markdown("### 👥 Student vs Program Cohort")
    
    # Get all students in same program
    program_students = [s["id"] for s in st.session_state.students if s["program"] == student["program"]]
    program_incidents = [i for i in st.session_state.incidents if i["student_id"] in program_students]
    
    if len(program_incidents) > 0:
        program_df = pd.DataFrame(program_incidents)
        
        comparison = pd.DataFrame({
            "Metric": ["Incidents", "Avg Severity", "Critical %"],
            "This Student": [
                len(full_df),
                round(full_df["severity"].mean(), 2),
                round((len(full_df[full_df["severity"] >= 4]) / len(full_df)) * 100, 1)
            ],
            "Program Avg": [
                round(len(program_df) / len(program_students), 1),
                round(program_df["severity"].mean(), 2),
                round((len(program_df[program_df["severity"] >= 4]) / len(program_df)) * 100, 1)
            ]
        })
        
        fig11 = go.Figure()
        fig11.add_trace(go.Bar(
            name='This Student',
            x=comparison["Metric"],
            y=comparison["This Student"],
            marker=dict(color='#3b82f6')
        ))
        fig11.add_trace(go.Bar(
            name='Program Average',
            x=comparison["Metric"],
            y=comparison["Program Avg"],
            marker=dict(color='#10b981')
        ))
        fig11.update_layout(
            title="Student vs Program Comparison",
            barmode='group'
        )
        st.plotly_chart(fig11, use_container_width=True)

    st.markdown("---")

    # ==============================================
    # SECTION 8: ABC HYPOTHESIS ANALYSIS
    # ==============================================
    st.markdown("## 🧠 Functional Behaviour Analysis")

    # 8.1 Function distribution
    if "hypothesis" in full_df.columns:
        st.markdown("### 🎯 Hypothesized Functions (ABC Analysis)")
        
        # Extract function from hypothesis
        functions = full_df["hypothesis"].value_counts()
        
        fig12 = go.Figure(data=[go.Bar(
            x=functions.values,
            y=functions.index,
            orientation='h',
            marker=dict(
                color=['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'][:len(functions)]
            )
        )])
        fig12.update_layout(
            title="Behavioural Function Distribution",
            xaxis_title="Frequency",
            yaxis_title="Function"
        )
        st.plotly_chart(fig12, use_container_width=True)

        # Most common function
        top_function = functions.index[0]
        st.info(f"**Primary Function:** {top_function} ({functions.values[0]} incidents, "
               f"{(functions.values[0]/len(full_df)*100):.1f}% of total)")

    st.markdown("---")

    # ==============================================
    # SECTION 9: REPORTING & EXPORT
    # ==============================================
    st.markdown("## 📄 Data Export & Reporting")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download CSV
        csv = full_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv,
            file_name=f"{student['name']}_incidents.csv",
            mime="text/csv"
        )
    
    with col2:
        # Summary report
        summary = f"""
INCIDENT SUMMARY REPORT
Student: {student['name']}
Program: {student['program']} | Grade: {student['grade']}
Report Date: {datetime.now().strftime('%Y-%m-%d')}

OVERVIEW:
- Total Incidents: {len(full_df)}
- Critical Incidents: {len(full_df[full_df['incident_type'] == 'Critical'])}
- Date Range: {full_df['date_parsed'].min().strftime('%Y-%m-%d')} to {full_df['date_parsed'].max().strftime('%Y-%m-%d')}
- Average Severity: {full_df['severity'].mean():.2f}

TOP PATTERNS:
- Most Common Behaviour: {full_df['behaviour_type'].mode()[0]}
- Most Common Trigger: {full_df['antecedent'].mode()[0]}
- Highest Risk Location: {full_df['location'].mode()[0]}
- Highest Risk Session: {full_df['session'].mode()[0]}

RISK LEVEL: {risk_level} ({risk_score}/100)
"""
        st.download_button(
            label="📄 Download Summary Report (TXT)",
            data=summary,
            file_name=f"{student['name']}_summary.txt",
            mime="text/plain"
        )
    
    with col3:
        st.info("📊 Additional export formats available in production version (PDF, Excel)")

    # Final back button
    st.markdown("---")
    if st.button("⬅ Back to Students", type="primary"):
        go_to("program_students", selected_program=student["program"])


# ==============================================
# HELPER: Add this as a new page option
# ==============================================

# In your VALID_PAGES list, add:
# "advanced_analysis"

# In your main() router, add:
# elif page == "advanced_analysis":
#     render_advanced_student_analysis(st.session_state.selected_student_id)
