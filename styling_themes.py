"""
Modern Styling Options for Behaviour Support App
Choose your preferred theme and add to your app!
"""

# ============================================
# THEME 1: PROFESSIONAL BLUE (Recommended)
# Clean, trustworthy, educational
# ============================================

THEME_1_PROFESSIONAL_BLUE = """
<style>
/* Import modern fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

/* Global Styling */
.main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Headers */
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

/* Cards and Containers */
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

/* Buttons */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    transition: all 0.3s ease;
    border: none;
    text-transform: none;
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

.stButton > button[kind="secondary"] {
    background: white;
    color: #3b82f6;
    border: 2px solid #3b82f6;
}

.stButton > button[kind="secondary"]:hover {
    background: #eff6ff;
    border-color: #2563eb;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

div[data-testid="stMetric"] label {
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1e40af;
    font-size: 2rem;
    font-weight: 700;
}

/* Tabs */
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
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Input Fields */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    font-family: 'Inter', sans-serif;
    transition: border-color 0.2s ease;
}

.stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Expanders */
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: #1e40af;
    background: #f0f9ff;
    border-radius: 8px;
    padding: 1rem;
}

/* Tables */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.dataframe thead tr {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
}

/* Success/Error Messages */
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
"""

# ============================================
# THEME 2: MODERN PURPLE (Creative & Sophisticated)
# Educational psychology vibe
# ============================================

THEME_2_MODERN_PURPLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

.main {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
}

h1, h2, h3 {
    font-family: 'Outfit', sans-serif;
    color: #6b21a8;
    font-weight: 600;
}

h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.1);
    border: 2px solid #f3e8ff !important;
    transition: all 0.3s ease;
}

div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    border-color: #c084fc !important;
    box-shadow: 0 20px 25px -5px rgba(124, 58, 237, 0.2);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white;
    border-radius: 14px;
    font-weight: 600;
    padding: 0.75rem 2rem;
    box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #9333ea 100%);
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(124, 58, 237, 0.4);
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
    padding: 1.5rem;
    border-radius: 14px;
    border-left: 5px solid #a855f7;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #7c3aed;
    font-size: 2rem;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white !important;
    border-radius: 10px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6b21a8 0%, #581c87 100%);
}

.stSuccess { background: #d1fae5; border-left: 4px solid #10b981; }
.stError { background: #fee2e2; border-left: 4px solid #ef4444; }
.stWarning { background: #fef3c7; border-left: 4px solid #f59e0b; }
.stInfo { background: #dbeafe; border-left: 4px solid #a855f7; }
</style>
"""

# ============================================
# THEME 3: CLEAN TEAL (Healthcare Professional)
# Calm, trustworthy, medical
# ============================================

THEME_3_CLEAN_TEAL = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

.main {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #115e59;
    font-weight: 600;
}

h1 {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.1);
    border: 2px solid #ccfbf1 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
    transform: translateY(-2px);
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 100%);
    border-left: 5px solid #14b8a6;
    border-radius: 12px;
    padding: 1.5rem;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #0d9488;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
    color: white !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #115e59 0%, #134e4a 100%);
}
</style>
"""

# ============================================
# THEME 4: DARK MODE ELEGANCE (Modern & Sleek)
# Professional dark theme
# ============================================

THEME_4_DARK_MODE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.main {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #e2e8f0;
}

h1, h2, h3 {
    color: #f1f5f9;
    font-weight: 600;
}

h1 {
    background: linear-gradient(135deg, #60a5fa 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.6);
}

div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.6);
    border-left: 4px solid #60a5fa;
    border-radius: 12px;
}

div[data-testid="stMetric"] label {
    color: #94a3b8;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #60a5fa;
    font-weight: 700;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(30, 41, 59, 0.6);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    color: white !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.2);
}

.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: rgba(30, 41, 59, 0.6);
    color: #e2e8f0;
    border: 1px solid rgba(148, 163, 184, 0.3);
}

.stSuccess { background: rgba(16, 185, 129, 0.2); border-left: 4px solid #10b981; color: #6ee7b7; }
.stError { background: rgba(239, 68, 68, 0.2); border-left: 4px solid #ef4444; color: #fca5a5; }
.stWarning { background: rgba(245, 158, 11, 0.2); border-left: 4px solid #f59e0b; color: #fcd34d; }
</style>
"""

# ============================================
# THEME 5: MINIMAL GREY (Ultra Clean)
# Scandinavian minimalism
# ============================================

THEME_5_MINIMAL_GREY = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.main {
    font-family: 'Inter', sans-serif;
    background: #fafafa;
    color: #171717;
}

h1, h2, h3 {
    color: #171717;
    font-weight: 600;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.5rem;
    color: #0a0a0a;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e5e5 !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.stButton > button[kind="primary"] {
    background: #171717;
    color: white;
    border-radius: 8px;
    font-weight: 500;
    padding: 0.75rem 2rem;
}

.stButton > button[kind="primary"]:hover {
    background: #0a0a0a;
}

.stButton > button[kind="secondary"] {
    background: white;
    color: #171717;
    border: 1px solid #e5e5e5;
}

div[data-testid="stMetric"] {
    background: #fafafa;
    border-left: 3px solid #171717;
    border-radius: 8px;
    padding: 1.5rem;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #171717;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: #171717;
    color: white !important;
    border-radius: 6px;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e5e5;
}

section[data-testid="stSidebar"] * {
    color: #171717 !important;
}
</style>
"""
