# 🚀 Quick Start: Advanced Analytics

## 📦 Installation

```bash
# No additional libraries needed!
# plotly, pandas, numpy should already be installed
```

## 📥 Files You Need

1. **ADVANCED_ANALYTICS_MODULE.py** - The analytics code (scipy-free!)
2. **ANALYTICS_FEATURES_GUIDE.md** - Complete documentation

## ⚡ Quick Integration (3 Steps)

### Step 1: Add Required Import
At the top of your sandbox app, add:
```python
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
```

### Step 2: Copy the Function
Copy the entire `render_advanced_student_analysis()` function from the module into your app.

### Step 3: Replace or Add Page
**Option A - Replace existing:**
```python
def render_student_analysis_page():
    render_advanced_student_analysis(
        st.session_state.selected_student_id
    )
```

**Option B - Add as new page:**
```python
# Add to VALID_PAGES:
"advanced_analysis"

# In main() router:
elif page == "advanced_analysis":
    render_advanced_student_analysis(
        st.session_state.selected_student_id
    )

# Add button on student page:
if st.button("📊 Advanced Analysis"):
    go_to("advanced_analysis", 
          selected_student_id=student["id"])
```

## ✅ Test It

```bash
streamlit run your_app.py
```

1. Login
2. Select a student with incidents
3. Click "Analysis" (or "Advanced Analysis")
4. See 20+ graphs!

## 🎯 What You Get

### 9 Major Sections:
1. Executive Summary (5 metrics)
2. Time-Series (3 graphs)
3. Heatmaps (2 graphs)
4. Behaviour Patterns (3 graphs)
5. Intervention Effectiveness (2 graphs)
6. Predictive Indicators (risk score)
7. Comparative Analysis (vs cohort)
8. ABC Analysis (functions)
9. Data Export (CSV, TXT)

### 20+ Visualizations:
- ⏰ Daily incident frequency
- 📈 7-day moving average
- 🎯 Severity timeline
- 🔥 Day × Hour heatmap
- 📍 Location × Session heatmap
- 🔗 Antecedent → Behaviour patterns
- 🥧 Behaviour distribution pie
- 🔄 Behaviour sequences
- 📊 Intervention effectiveness
- ⏱️ Duration box plots
- ⚠️ Escalation detection
- 🎲 Risk score (0-100)
- 👥 Student vs cohort comparison
- 🧠 Function distribution
- And more!

## 🎨 Customize

### Colors
```python
# Find and change:
marker=dict(color='#3b82f6')  # Blue
marker=dict(color='#ef4444')  # Red
marker=dict(color='#10b981')  # Green
```

### Risk Formula
```python
# Adjust weights in risk_score calculation:
risk_score = min(100, int(
    (frequency * 10) +      # Change 10
    (severity * 8) +        # Change 8
    (critical_rate * 0.5) + # Change 0.5
    (escalation * 20)       # Change 20
))
```

### Thresholds
```python
# Change risk levels:
risk_color = "#10b981" if risk_score < 30 else ...  # Change 30
risk_level = "LOW" if risk_score < 30 else ...       # Change 30
```

## 🐛 Troubleshooting

### Graphs not showing
- Check you have incidents in your data
- Verify date fields are formatted correctly
- Try with at least 10 incidents

### Risk score is 0
- Need at least 5 incidents for meaningful risk calculation
- Check severity values are 1-5

## 💡 Pro Tips

1. **Test with mock data first** - Use the sandbox version
2. **Review with team** - Make sure graphs make sense
3. **Adjust risk formula** - Calibrate to your context
4. **Print heatmaps** - Great for team meetings
5. **Export regularly** - Keep CSV records

## 📚 Full Documentation

See **ANALYTICS_FEATURES_GUIDE.md** for:
- Detailed explanation of each graph
- How to interpret results
- Use cases and examples
- Training guide for staff
- Advanced customization

## 🎉 You're Done!

Your app now has professional-grade analytics with 20+ visualizations!

---

**Questions?** Check the full guide or experiment with the sandbox version first!
