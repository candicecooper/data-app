# Incident Reporting System - Deployment Guide

## Overview
Professional incident reporting system with minimalistic design, proper form structures, and comprehensive analytics.

## Key Features Fixed
✅ Clean, light gray professional background (#f5f5f5)
✅ Critical Incident form with proper chronology column structure
✅ All form fields start empty (not prefilled)
✅ Professional severity indicators (green/orange/red, not rainbow)
✅ Graphs included in BAP Word document downloads

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
streamlit run incident_app.py
```

The application will open in your default browser at `http://localhost:8501`

## Application Structure

### 1. Quick Incident Form
- Basic incident reporting for minor to moderate incidents
- Fields include: student name, date/time, location, behavior type, severity
- Empty form fields requiring manual entry
- Professional severity selection (Low/Medium/High with clear descriptions)

### 2. Critical Incident Form
**Key Feature: Chronology Structure**
- Timeline-based documentation with time + description columns
- Add multiple chronology entries as needed
- Detailed antecedent, intervention, and outcome tracking
- Empty fields throughout - staff must complete all sections

### 3. BAP (Behavior Analysis Plan) Form
- Comprehensive behavior support planning
- Functional assessment section
- Prevention, teaching, and response strategies
- Data collection planning
- **Automatic generation of Word document WITH embedded graphs**

### 4. Analytics Dashboard
- Professional charts with appropriate colors:
  - Severity: Green (Low), Orange (Medium), Red (High)
  - Other charts: Professional blue tones
- Incident trends over time
- Student-specific analytics
- Location and behavior type distributions
- Export to CSV/JSON

## Professional Design Elements

### Color Scheme
- Background: Light gray (#f5f5f5)
- Primary: Professional blue (#3498db)
- Success/Low: Green (#27ae60)
- Warning/Medium: Orange (#f39c12)
- Danger/High: Red (#e74c3c)

### Form Design
- White form sections with subtle shadows
- Clear section headers with blue underlines
- Professional button styling
- Clean, readable typography

## Data Storage
- Data stored in `incident_data.json` in the application directory
- Automatic save on each form submission
- Persistent across sessions

## Export Features

### BAP Word Documents
- Professional formatting with tables
- Complete behavior plan documentation
- **Embedded analytics graphs:**
  - Behavior frequency chart for the student
  - Severity trend line over time
- Graphs use kaleido for high-quality PNG export

### CSV/JSON Export
- Full data export from Analytics Dashboard
- Compatible with Excel and data analysis tools

## Usage Tips

1. **Forms Start Empty**: All fields require manual entry to ensure staff review each item
2. **Chronology Entries**: Click "Add Another Chronology Entry" to document timeline details
3. **Required Fields**: Look for asterisk (*) to identify required fields
4. **BAP Graphs**: Graphs automatically generate when downloading BAP document if incident data exists
5. **Professional Appearance**: Designed for educational/clinical settings

## Troubleshooting

### Issue: Graphs not appearing in BAP documents
**Solution**: Ensure kaleido is installed:
```bash
pip install kaleido==0.2.1
```

### Issue: Port already in use
**Solution**: Specify a different port:
```bash
streamlit run incident_app.py --server.port 8502
```

### Issue: Data not persisting
**Solution**: Check write permissions in the application directory

## Security Notes
- This is a local application - no external data transmission
- Data stored locally in JSON format
- For production use, consider implementing:
  - User authentication
  - Database backend
  - Encrypted storage
  - Backup systems

## Customization

### Change Color Scheme
Edit the CSS in the `st.markdown()` section at the top of `incident_app.py`

### Add Form Fields
Modify the form sections in each page's code block

### Adjust Analytics
Customize the charts in the "Analytics Dashboard" section

## Support
For issues or questions, review the inline code comments or modify as needed for your specific requirements.

## Version
Version 2.0 - Professional Clean Design with Fixed Structure and Graph Export

---
**Built with Streamlit** | Professional incident tracking for educational and clinical settings
