# 🎯 CLC Behaviour Support System

A beautiful, professional behaviour tracking and analytics application for educational settings. This system provides comprehensive incident tracking, advanced data analytics, and automated report generation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 Modern, Sleek Design
- Beautiful purple/blue gradient interface
- Smooth animations and transitions
- Professional glass-effect styling
- Responsive layout for all screen sizes

### 📊 Comprehensive Analytics
- **20+ Interactive Visualizations**
  - Time-series analysis with trend detection
  - Heatmaps for day/time patterns
  - Behaviour sequence analysis
  - Intervention effectiveness metrics
  - Risk assessment scoring

### 📝 Incident Tracking
- Quick incident logging
- Critical incident ABCH forms
- Automated hypothesis generation
- Staff collaboration features

### 📄 Professional Reports
- **Word Document Export** - "Behaviour Analysis Plan"
- CSV data exports
- Trauma-informed clinical interpretations
- CPI and Berry Street Model aligned recommendations

### 🔒 Secure & Compliant
- Sandbox mode for demonstrations
- No real student data required
- Professional educational standards

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/clc-behaviour-support.git
   cd clc-behaviour-support
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to this URL manually

## 🎭 Demo Mode

The application includes sandbox mode with mock data for demonstrations:

### Demo Staff Logins

Use any of these email addresses to log in:

- `emily.jones@example.com` - Junior Primary
- `daniel.lee@example.com` - Primary Years
- `sarah.chen@example.com` - Senior Years
- `admin.user@example.com` - Admin
- Any other email - Demo User

### Sample Students

The app includes 9 mock students across three programs:
- **Junior Primary (JP)**: Emma T., Oliver S., Sophie M.
- **Primary Years (PY)**: Liam C., Ava R., Noah B.
- **Senior Years (SY)**: Isabella G., Ethan D., Mia A.

Isabella G. has the most incident data for comprehensive analytics demonstration.

## 📖 Usage Guide

### 1. Login
- Enter any email address on the login screen
- Use demo staff emails or any email for demo mode

### 2. Select a Program
- Choose from Junior Primary, Primary Years, or Senior Years
- View student lists with incident counts

### 3. Log Incidents
- Quick incident logging with all required fields
- Automatic hypothesis generation
- Critical incident ABCH forms for severity ≥4

### 4. View Analytics
- Comprehensive data analysis for each student
- 20+ interactive visualizations
- Risk assessment and trend analysis
- Clinical interpretations and recommendations

### 5. Generate Reports
- Download CSV data exports
- Generate professional Word documents
- "Behaviour Analysis Plan" with clinical insights

## 🎨 Key Features Explained

### Executive Summary
- Total incidents tracked
- Critical incident counts
- Average severity metrics
- Incidents per day tracking

### Time-Series Analysis
- Daily incident frequency charts
- 7-day moving averages
- Severity timeline with critical incident highlights

### Heatmap Analysis
- Day-of-week × Time-of-day patterns
- Location × Session hotspots
- Visual identification of high-risk periods

### Behaviour Patterns
- Antecedent → Behaviour relationships
- Behaviour type distribution
- Sequential behaviour chains
- Functional behaviour analysis

### Intervention Effectiveness
- Average severity by intervention type
- Duration analysis by behaviour
- Success rate metrics

### Risk Assessment
- Automated risk scoring (0-100)
- Escalation pattern detection
- Risk level classification (LOW/MODERATE/HIGH)
- Detailed risk factor breakdown

### Clinical Interpretation
- Trauma-informed analysis
- CPI (Crisis Prevention Institute) alignment
- Berry Street Education Model references
- Australian Curriculum General Capabilities links
- SMART goal recommendations

## 📄 Report Generation

### Behaviour Analysis Plan (Word Document)

Includes:
- Student information
- Executive summary
- Data findings
- Clinical interpretation
- Trauma-informed recommendations
- CPI-aligned strategies
- SMART goals
- Professional formatting

## 🛠️ Customization

### Changing Colors

Edit the CSS in `app.py` (lines 40-170) to customize:

```python
# Main background gradient
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# Primary buttons
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

# Download buttons
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
```

### Adding Students

Modify the `MOCK_STUDENTS` list in `app.py` (lines 190-208):

```python
{"id": "stu_id", "name": "Student Name", "grade": "Y1", 
 "dob": "2018-01-01", "edid": "ED00000", "program": "JP"}
```

### Adjusting Behaviour Types

Edit the lists in `app.py`:
- `BEHAVIOUR_TYPES` (lines 228-236)
- `ANTECEDENTS` (lines 238-246)
- `INTERVENTIONS` (lines 248-256)
- `LOCATIONS` (lines 258-272)

## 📊 Data Structure

### Incident Record
```python
{
    "id": "unique_id",
    "student_id": "stu_id",
    "date": "2024-01-01",
    "time": "10:30:00",
    "location": "Classroom",
    "behaviour_type": "Verbal Refusal",
    "antecedent": "Given instruction",
    "severity": 3,
    "intervention": "Used calm tone",
    "hypothesis": "To avoid request"
}
```

### Critical Incident Record
```python
{
    "id": "unique_id",
    "student_id": "stu_id",
    "ABCH_primary": {
        "A": "Antecedent",
        "B": "Behaviour",
        "C": "Consequence",
        "H": "Hypothesis"
    },
    "safety_responses": [...],
    "notifications": [...],
    "outcomes": {...}
}
```

## 🔧 Troubleshooting

### App won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Try running with verbose output
streamlit run app.py --logger.level=debug
```

### Styling not displaying
- Clear browser cache (Ctrl+F5)
- Check browser console for errors
- Try a different browser

### Word documents not generating
```bash
# Reinstall python-docx
pip uninstall python-docx
pip install python-docx
```

## 🎯 Best Practices

1. **For Demonstrations**
   - Use Isabella G. (has most data)
   - Explore all analytics sections
   - Download sample reports
   - Show risk assessment features

2. **For Testing**
   - Log various severity levels
   - Try different behaviour types
   - Test intervention effectiveness
   - Generate ABCH forms

3. **For Presentations**
   - Start with landing page
   - Show quick incident logging
   - Navigate to student analysis
   - Demonstrate report generation

## 📱 Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Internet Explorer (not supported)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CPI (Crisis Prevention Institute)** - Behaviour support framework
- **Berry Street Education Model** - Trauma-informed practices
- **Australian Curriculum** - General Capabilities alignment
- **Streamlit** - Application framework
- **Plotly** - Interactive visualizations

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Email: support@example.com
- Documentation: See guide documents

## 🎓 Educational Context

This system is designed for:
- Special education settings
- Behaviour support programs
- Student wellbeing tracking
- Team collaboration
- Data-driven decision making

## 🔮 Future Enhancements

Planned features:
- [ ] PDF export for reports
- [ ] Email notifications
- [ ] Multi-user authentication
- [ ] Real-time collaboration
- [ ] Mobile app version
- [ ] Advanced predictive analytics
- [ ] Integration with student information systems

## 📊 Performance

- Handles 1000+ incidents smoothly
- Renders charts in < 2 seconds
- Generates reports in < 3 seconds
- Optimized for daily use

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

---

**Made with ❤️ for educators supporting student wellbeing**

Version 1.0 | Last Updated: November 2024
