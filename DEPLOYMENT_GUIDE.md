# 🚀 Deployment Guide: Update Your Live App

## 📦 Files You Need

1. **[app.py](computer:///mnt/user-data/outputs/app.py)** - Complete application (867 lines)
2. **[requirements.txt](computer:///mnt/user-data/outputs/requirements.txt)** - Dependencies

---

## ⚡ Quick Deploy to Streamlit Cloud

### Step 1: Update Your GitHub Repo

1. Go to your GitHub repo: `data-app/app.py`
2. **Replace the entire file** with the new `app.py`
3. **Replace** `requirements.txt` with the new one
4. Commit with message: "Add all improvements: contrast, graphs, email, severity guide"
5. Push to GitHub

### Step 2: Streamlit Cloud Auto-Deploys

- Streamlit Cloud watches your repo
- Automatically detects changes
- Rebuilds and deploys (2-3 minutes)
- Your app updates at: https://behaviour-tracker.streamlit.app

---

## ✅ What's Included in New App

### Visual Improvements:
- ✅ **High contrast text** everywhere
- ✅ **Purple gradient** background
- ✅ **White containers** with shadows
- ✅ **Sleek buttons** (purple/cyan/green gradients)
- ✅ **Bold fonts** (600-800 weight)
- ✅ **Readable labels** (black text on white)

### New Features:
- ✅ **Severity visual guide** (1-5 color-coded)
- ✅ **Auto critical form trigger** (severity ≥4)
- ✅ **Email notifications** (staff + manager)
- ✅ **Better graphs** (no box plots)
- ✅ **Graph explanations** (what it means + what to do)
- ✅ **Graphs in Word doc** (3 embedded images)

### Analytics (20+ graphs):
1. Daily incident frequency
2. 7-day moving average
3. Severity timeline
4. Day × Hour heatmap
5. Location × Session heatmap
6. Antecedent → Behaviour patterns
7. Behaviour distribution pie
8. Intervention effectiveness
9. Duration bar chart (not box plot!)
10. Escalation detection
11. Risk score (0-100)
12. Function distribution
13. Clinical interpretation
14. And more!

---

## 📋 Testing Your Deployed App

After deployment completes:

### 1. Check Login
- [ ] Go to your app URL
- [ ] Banner shows "SANDBOX DEMONSTRATION MODE" in dark blue on white
- [ ] Banner is readable (not faded gray)
- [ ] Login with any email works

### 2. Check Navigation
- [ ] Landing page shows 3 programs
- [ ] Can enter JP/PY/SY programs
- [ ] Student list shows with incident counts
- [ ] Back button works

### 3. Check Incident Logging
- [ ] Log incident page shows severity guide (5 colored boxes)
- [ ] All text in forms is readable (black labels)
- [ ] Submit incident works
- [ ] Severity 4 shows critical form prompt
- [ ] Severity 1-3 just goes back

### 4. Check Critical Form
- [ ] ABCH form appears
- [ ] All text readable
- [ ] Save shows email notification message
- [ ] Email notification shows who it would send to

### 5. Check Analytics
- [ ] Click "Analysis" on a student with data (try Isabella G.)
- [ ] Executive summary shows metrics
- [ ] All graphs load
- [ ] Graphs have explanations underneath
- [ ] No box plots (replaced with bar charts)
- [ ] Risk score shows with color
- [ ] Download buttons work

### 6. Check Word Export
- [ ] Click "Behaviour Analysis Plan (Word)"
- [ ] File downloads
- [ ] Open in Word
- [ ] Contains 3 embedded graphs
- [ ] All text formatted correctly

---

## 🎨 Visual Verification

### Text Contrast Checklist:
- [ ] Banner text: **Dark blue on white** ✅
- [ ] Headers (h1/h2/h3): **White with shadow** ✅
- [ ] Labels in forms: **Black text** ✅
- [ ] Text in white containers: **Black** ✅
- [ ] Metrics: **Gradient purple text** ✅
- [ ] All text is crisp and readable

### Button Check:
- [ ] Regular buttons: **Purple gradient** ✅
- [ ] Primary buttons: **Cyan/green gradient** ✅
- [ ] Download buttons: **Green gradient** ✅
- [ ] No red buttons ✅
- [ ] Hover effect works (lifts up) ✅

---

## 🔧 If Something's Wrong

### App won't start?
**Check Streamlit Cloud logs:**
1. Click "Manage app" (bottom right)
2. View logs
3. Look for errors

**Common fixes:**
- Missing library? Add to requirements.txt
- Syntax error? Check the file copied correctly
- Import error? Verify all imports at top

### Contrast still poor?
**Clear browser cache:**
- Chrome: Ctrl+Shift+Delete
- Or hard refresh: Ctrl+F5

### Graphs not showing?
**Check dependencies:**
```
streamlit
pandas
plotly
numpy
python-docx
kaleido
```

All must be in requirements.txt!

### Word export fails?
**Error message shows:**
"python-docx not installed"

**Fix:** Add to requirements.txt:
```
python-docx
kaleido
```

---

## 🎯 Production Email Setup

### Current (Sandbox):
Shows what email would be sent - no actual emails

### To Enable Real Emails:

1. **Get SMTP credentials:**
   - Gmail: Enable 2FA, generate app password
   - Office 365: Use your credentials
   - Or use service like SendGrid

2. **Update email function:**

Find this in app.py (around line 100):
```python
def send_critical_incident_email(...):
    # Current code just shows message
```

Replace with production code:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_critical_incident_email(incident_data, student, staff_email, manager_email="manager@clc.sa.edu.au"):
    try:
        msg = MIMEMultipart()
        msg['From'] = "noreply@clc.sa.edu.au"
        msg['To'] = f"{manager_email}, {staff_email}"
        msg['Subject'] = f"CRITICAL INCIDENT ALERT - {student['name']}"
        
        body = f"""
CRITICAL INCIDENT REPORT

Student: {student['name']} ({student['program']} - Grade {student['grade']})
Date/Time: {incident_data.get('created_at')}

Behaviour: {incident_data.get('ABCH_primary', {}).get('B', 'N/A')}
Antecedent: {incident_data.get('ABCH_primary', {}).get('A', 'N/A')}

Safety Responses: {', '.join(incident_data.get('safety_responses', []))}
Notifications: {', '.join(incident_data.get('notifications', []))}

Please review full details in the system.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # For Gmail:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("your_email@gmail.com", "your_app_password")
        
        # For Office 365:
        # server = smtplib.SMTP('smtp.office365.com', 587)
        # server.starttls()
        # server.login("your_email@clc.sa.edu.au", "your_password")
        
        server.send_message(msg)
        server.quit()
        
        st.success("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False
```

3. **Add Streamlit Secrets:**

In Streamlit Cloud:
- Go to app settings
- Add secrets:
```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "your_email@gmail.com"
password = "your_app_password"
manager_email = "manager@clc.sa.edu.au"
```

Then access in code:
```python
import st
server.login(st.secrets["email"]["username"], st.secrets["email"]["password"])
```

---

## 📊 Usage Tips

### For Best Results:

1. **Use Isabella G. for demos** - She has 12 incidents (most data)
2. **Show the heatmaps** - Most impressive visuals
3. **Download Word doc** - Professional reports
4. **Explain risk score** - Proactive support planning
5. **Show severity guide** - Consistent interpretations

### For Training:

1. **Start with severity guide** - Everyone understands 1-5
2. **Log a test incident** - Walk through process
3. **Trigger critical form** - Show severity ≥4 flow
4. **View analytics** - Interpret graphs together
5. **Download report** - Show final output

---

## 🎉 You're Done!

Your app now has:
- ✅ Beautiful high-contrast design
- ✅ Clear severity guide
- ✅ Automatic critical incident handling
- ✅ Email notifications
- ✅ Professional analytics (20+ graphs)
- ✅ Word reports with embedded graphs
- ✅ Production-ready quality

**Just push to GitHub and Streamlit Cloud does the rest!** 🚀

---

## 📞 Quick Help

### Deployment Issue?
- Check Streamlit Cloud logs
- Verify all files committed to GitHub
- Check requirements.txt has all libraries

### Visual Issue?
- Hard refresh browser (Ctrl+F5)
- Clear cache
- Check CSS loaded (view page source)

### Feature Not Working?
- Check console for errors (F12)
- Verify you're using the complete new app.py
- Test with Isabella G. (most data)

---

**Your upgraded app is ready to deploy!** 🎊

**Files:** app.py + requirements.txt  
**Action:** Push to GitHub  
**Result:** Beautiful, professional behaviour tracking system!
