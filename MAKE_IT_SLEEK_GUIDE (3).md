# 🎨 Making Your App Sleek & Beautiful - Complete Guide

## 📥 Quick Summary of Changes

I'll show you exactly what to change to:
1. ✅ Remove cohort comparison graph
2. ✅ Make it visually stunning (purple/blue gradient theme)
3. ✅ Remove red buttons (replace with sleek blue/purple)
4. ✅ Add Word document export for "Behaviour Analysis Plan"

---

## 🎨 PART 1: Add Sleek Styling

### Find this line in your app (around line 13):
```python
st.set_page_config(
    page_title="CLC Behaviour Support – SANDBOX",
```

### Add this AFTER the st.set_page_config:

```python
# =========================================
# SLEEK MODERN STYLING
# =========================================

st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background gradient - purple/blue */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom buttons - sleek blue/purple */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Primary button - cyan gradient */
    button[kind="primary"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4) !important;
    }
    
    button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.6) !important;
    }
    
    /* Containers with white background */
    [data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Metrics - gradient text */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* Input fields - rounded with border */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input {
        border-radius: 10px !important;
        border: 2px solid #e0e7ff !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Headers - white text */
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Expanders - glass effect */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Success/info boxes */
    .stSuccess, .stInfo {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        border-left: 4px solid #4facfe !important;
    }
    
    /* Download buttons - green gradient */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4) !important;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(17, 153, 142, 0.6) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)
```

### Replace the red banner with this sleek one:

Find this section:
```python
st.markdown(
    """
<div style='padding: 12px; background-color: #8A1C1C; color: white; ...
```

Replace with:
```python
st.markdown("""
<div style='background: rgba(255, 255, 255, 0.95); 
            padding: 1.5rem; 
            border-radius: 15px; 
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;'>
    <h3 style='color: #667eea; margin: 0; font-size: 1.2rem;'>
        🎭 SANDBOX MODE
    </h3>
    <p style='color: #666; margin: 0.5rem 0 0 0;'>
        This demonstration uses synthetic data only. No real student information is included.
    </p>
</div>
""", unsafe_allow_html=True)
```

---

## 🗑️ PART 2: Remove Cohort Comparison

### Find this section (around line 1300-1400):

```python
# ==============================================
# SECTION 7: COMPARATIVE ANALYSIS
# ==============================================
st.markdown("## 📐 Comparative Analysis")

st.markdown("### 👥 Student vs Program Cohort")
```

### DELETE everything from that heading until the next `st.markdown("---")`:

Delete all of this:
```python
st.markdown("## 📐 Comparative Analysis")

st.markdown("### 👥 Student vs Program Cohort")

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
```

Just remove that entire section!

---

## 📄 PART 3: Add Word Document Export

### Step 1: Install python-docx

```bash
pip install python-docx
```

### Step 2: Add this function at the top of your file (after imports):

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

def generate_behaviour_analysis_plan_docx(student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level):
    """Generate a Word document for Behaviour Analysis Plan"""
    doc = Document()
    
    # Title
    title = doc.add_heading('Behaviour Analysis Plan', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Student Info
    doc.add_heading('Student Information', 1)
    student_table = doc.add_table(rows=4, cols=2)
    student_table.style = 'Light Grid Accent 1'
    
    student_table.rows[0].cells[0].text = 'Student Name:'
    student_table.rows[0].cells[1].text = student['name']
    student_table.rows[1].cells[0].text = 'Program:'
    student_table.rows[1].cells[1].text = student['program']
    student_table.rows[2].cells[0].text = 'Grade:'
    student_table.rows[2].cells[1].text = student['grade']
    student_table.rows[3].cells[0].text = 'Report Date:'
    student_table.rows[3].cells[1].text = datetime.now().strftime('%d/%m/%Y')
    
    doc.add_paragraph()
    
    # Executive Summary
    doc.add_heading('Executive Summary', 1)
    summary_para = doc.add_paragraph()
    summary_para.add_run(f"Total Incidents: ").bold = True
    summary_para.add_run(f"{len(full_df)}\n")
    summary_para.add_run(f"Critical Incidents: ").bold = True
    summary_para.add_run(f"{len(full_df[full_df['incident_type'] == 'Critical'])}\n")
    summary_para.add_run(f"Average Severity: ").bold = True
    summary_para.add_run(f"{full_df['severity'].mean():.2f}\n")
    summary_para.add_run(f"Risk Level: ").bold = True
    summary_para.add_run(f"{risk_level} ({risk_score}/100)")
    
    doc.add_paragraph()
    
    # Data Findings
    doc.add_heading('Summary of Data Findings', 1)
    findings = doc.add_paragraph()
    findings.add_run('Primary Concern: ').bold = True
    findings.add_run(f"{top_beh} is the most frequently recorded behaviour of concern.\n\n")
    findings.add_run('Key Triggers: ').bold = True
    findings.add_run(f"The most common antecedent is '{top_ant}', indicating this context regularly precedes dysregulation.\n\n")
    findings.add_run('Hotspot Locations: ').bold = True
    findings.add_run(f"Incidents most often occur in {top_loc}, particularly during the {top_session} session.")
    
    doc.add_paragraph()
    
    # Clinical Interpretation
    doc.add_heading('Clinical Interpretation (Trauma-Informed)', 1)
    clinical = doc.add_paragraph()
    clinical.add_run(
        f"Patterns suggest that {student['name']} is most vulnerable when '{top_ant}' occurs, "
        f"often in the {top_loc} during {top_session}. These moments likely narrow the student's "
        "window of tolerance, increasing the risk of fight/flight responses.\n\n"
    )
    clinical.add_run(
        "Through a trauma-informed lens, this behaviour is understood as a safety strategy rather than "
        "wilful defiance. CPI emphasises staying in the Supportive phase as early as possible.\n\n"
    )
    clinical.add_run(
        "The Berry Street Education Model points towards strengthening Body (regulation routines, "
        "predictable transitions) and Relationship (connection before correction)."
    )
    
    doc.add_paragraph()
    
    # Recommendations
    doc.add_heading('Recommendations & Next Steps', 1)
    
    doc.add_heading('1. Proactive Regulation Around Key Triggers', 2)
    rec1 = doc.add_paragraph(style='List Bullet')
    rec1.add_run(f"Provide a brief check-in and clear visual cue before '{top_ant}'")
    rec2 = doc.add_paragraph(style='List Bullet')
    rec2.add_run(f"Offer a regulated start before the high-risk {top_session} session")
    
    doc.add_heading('2. Co-regulation & Staff Responses (CPI Aligned)', 2)
    rec3 = doc.add_paragraph(style='List Bullet')
    rec3.add_run("Use CPI Supportive stance, low slow voice and minimal language")
    rec4 = doc.add_paragraph(style='List Bullet')
    rec4.add_run("Reduce audience by moving peers where possible")
    
    doc.add_heading('3. Teaching Replacement Skills', 2)
    rec5 = doc.add_paragraph(style='List Bullet')
    rec5.add_run("Link goals to Personal and Social Capability")
    rec6 = doc.add_paragraph(style='List Bullet')
    rec6.add_run("Explicitly teach help-seeking routines")
    
    doc.add_heading('4. SMART Goal Example', 2)
    goal = doc.add_paragraph(style='List Bullet')
    goal.add_run(
        f"Over the next 5 weeks, during identified trigger times, the student will use "
        f"an agreed help-seeking strategy in 4 out of 5 opportunities."
    )
    
    doc.add_paragraph()
    
    # Footer
    footer_para = doc.add_paragraph()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.add_run('\n\nGenerated by CLC Behaviour Support System\n')
    footer_run.font.size = Pt(9)
    footer_run.font.color.rgb = RGBColor(128, 128, 128)
    footer_para.add_run(datetime.now().strftime('%d %B %Y at %I:%M %p'))
    
    # Save to BytesIO
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
```

### Step 3: Update the Data Export section

Find this section (around line 1450):
```python
st.markdown("## 📄 Data Export & Reporting")

col1, col2, col3 = st.columns(3)
```

Replace with:
```python
st.markdown("## 📄 Data Export & Reporting")

col1, col2 = st.columns(2)  # Changed from 3 to 2 columns
```

Then find:
```python
with col2:
    summary = f"""
INCIDENT SUMMARY REPORT
...
```

Replace that entire col2 section with:
```python
with col2:
    # Generate Word document
    docx_file = generate_behaviour_analysis_plan_docx(
        student, full_df, top_ant, top_beh, top_loc, top_session, risk_score, risk_level
    )
    
    if docx_file:
        st.download_button(
            label="📄 Download Behaviour Analysis Plan (Word)",
            data=docx_file,
            file_name=f"Behaviour_Analysis_Plan_{student['name'].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
```

And delete the col3 section entirely.

---

## 📋 Summary of Changes

### What you're doing:
1. ✅ Adding beautiful purple/blue gradient theme
2. ✅ Making all buttons sleek (no more red!)
3. ✅ Removing cohort comparison graph
4. ✅ Adding Word document export called "Behaviour Analysis Plan"

### Files you need:
- Your existing `app_COMPLETE_WITH_ANALYTICS.py`
- Install: `pip install python-docx`

### Changes needed:
1. Add CSS styling (after st.set_page_config)
2. Replace red banner with sleek one
3. Delete cohort comparison section
4. Add docx generation function
5. Update data export section

---

## 🎨 Color Scheme

### New Theme:
- **Background:** Purple/Blue gradient (#667eea → #764ba2)
- **Buttons:** Purple gradient (no more red!)
- **Primary buttons:** Cyan gradient (#4facfe → #00f2fe)
- **Download buttons:** Green gradient (#11998e → #38ef7d)
- **Accent:** White containers with subtle shadows

---

## ✅ Testing

After making changes:
1. Run the app
2. Login
3. Go to a student with data
4. Click "Analysis"
5. Scroll to bottom
6. Click "Download Behaviour Analysis Plan (Word)"
7. Open the Word document!

---

## 💡 Pro Tips

- The Word document includes all key findings
- Professional layout with headers and formatting
- Includes student info, data summary, interpretation, and recommendations
- Ready to print or share with team

---

**Your app will look AMAZING with these changes!** 🎨✨

Purple gradient background, sleek buttons, no red, and professional Word reports! 🎉
