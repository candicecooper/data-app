# 🎨 Styling Guide for Behaviour Support App

## 5 Modern Theme Options

---

## 🔵 **THEME 1: Professional Blue** (RECOMMENDED)
**Best for:** Schools, Educational Settings, Professional Reports

### Colors:
- Primary: Blue (#3b82f6)
- Accent: Deep Blue (#1e40af)
- Background: Light Blue-Grey Gradient
- Text: Navy Blue (#1e3a8a)

### Vibe:
✅ Trustworthy  
✅ Professional  
✅ Educational  
✅ Clean & Modern  

**Perfect for government/education sector work!**

---

## 💜 **THEME 2: Modern Purple**
**Best for:** Psychology Services, Creative Teams

### Colors:
- Primary: Purple (#7c3aed)
- Accent: Bright Purple (#a855f7)
- Background: Light Purple Gradient
- Text: Deep Purple (#6b21a8)

### Vibe:
✅ Creative  
✅ Sophisticated  
✅ Psychology-focused  
✅ Calming  

---

## 🌊 **THEME 3: Clean Teal**
**Best for:** Healthcare, Wellness, Therapeutic Settings

### Colors:
- Primary: Teal (#0d9488)
- Accent: Bright Teal (#14b8a6)
- Background: Mint Green Gradient
- Text: Deep Teal (#115e59)

### Vibe:
✅ Calm  
✅ Medical/Healthcare  
✅ Trustworthy  
✅ Fresh  

---

## 🌙 **THEME 4: Dark Mode Elegance**
**Best for:** Modern Tech Look, Reduced Eye Strain

### Colors:
- Primary: Soft Blue (#60a5fa)
- Accent: Indigo (#818cf8)
- Background: Dark Slate (#0f172a)
- Text: Light Grey (#e2e8f0)

### Vibe:
✅ Modern  
✅ Sleek  
✅ Eye-friendly  
✅ Tech-forward  

---

## ⚪ **THEME 5: Minimal Grey**
**Best for:** Ultra-clean, Scandinavian Minimalism

### Colors:
- Primary: Black (#171717)
- Accent: Grey (#525252)
- Background: Off-White (#fafafa)
- Text: Black (#0a0a0a)

### Vibe:
✅ Ultra-clean  
✅ Minimalist  
✅ Timeless  
✅ Distraction-free  

---

# 📝 How to Apply a Theme

## Step 1: Choose Your Theme

Pick one of the 5 themes above.

## Step 2: Add to Your App

Open `behaviour_support_app.py` and add this code **right after the `st.set_page_config()` line** (around line 64):

### For Theme 1 (Professional Blue):
```python
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

h1, h2, h3 {
    font-family: 'Poppins', sans-serif;
    color: #1e3a8a;
    font-weight: 600;
}

h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    padding: 1.5rem;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    transition: all 0.3s ease;
    border: none;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1e40af;
    font-size: 2rem;
    font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: white;
    padding: 0.5rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    color: #64748b;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
}

.stSuccess {
    background: #d1fae5;
    color: #065f46;
    border-left: 4px solid #10b981;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
}

.stError {
    background: #fee2e2;
    color: #991b1b;
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
}

.stWarning {
    background: #fef3c7;
    color: #92400e;
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
}

.stInfo {
    background: #dbeafe;
    color: #1e40af;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)
```

## Step 3: Save and Push to GitHub

1. Save your file
2. Upload to GitHub (or commit if using Git)
3. Streamlit Cloud will automatically redeploy with new styling!

---

# 🎨 Additional Customization Options

## Custom Logo
Add at the top of your landing page:
```python
st.image("your-logo.png", width=200)
```

## Custom Favicon
In `st.set_page_config()`:
```python
st.set_page_config(
    page_title="Behaviour Support",
    page_icon="📊",  # Or use your logo URL
    layout="wide"
)
```

## Adjust Colors
Want to tweak colors? Change these hex codes:
- Primary color: `#3b82f6` (blue)
- Accent color: `#2563eb` (darker blue)
- Background: `#f5f7fa` (light grey-blue)

---

# 📱 Mobile Responsive
All themes are mobile-responsive by default!

---

# 🔄 Switching Themes
Just replace the `<style>` block with a different theme's CSS and push to GitHub!

---

# 💡 Pro Tips

1. **Match your organization's colors**: Replace the hex codes with your brand colors
2. **Test on different screens**: Check desktop, tablet, and mobile
3. **Keep it consistent**: Use one theme throughout
4. **Accessibility**: Ensure good contrast for readability

---

# 🎯 My Recommendation

For a **behaviour support/education app**, I recommend:

**🥇 Theme 1: Professional Blue**
- Most trusted color for education/healthcare
- Clean and professional
- Great for reports and presentations
- Universally accessible

Want to try multiple themes before deciding? Just swap the CSS and see which one feels right!
