import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid
import plotly.express as px
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from functools import wraps
import traceback
from supabase import create_client, Client

# --- SUPABASE CONFIGURATION ---
SUPABASE_URL = "https://szhebjnxxiwomgediufp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6aGViam54eGl3b21nZWRpdWZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE1MjgxMjMsImV4cCI6MjA3NzEwNDEyM30.AFGZkidWXf07VDcGXRId-rFg5SdAEwmq7EiHM-Zuu5o"

# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    """Returns a cached Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ERROR HANDLING SETUP ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_errors.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, user_message: str = None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ValidationError(AppError):
    """Raised when data validation fails"""
    pass

def handle_errors(user_message: str = "An error occurred"):
    """Decorator to catch and handle errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"{func.__name__}: {e.message}", exc_info=True)
                st.error(e.user_message)
                return None
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                st.error(f"{user_message}. Please try again or contact support.")
                with st.expander("Error Details"):
                    st.code(str(e))
                return None
        return wrapper
    return decorator

# --- 1. CONFIGURATION AND CONSTANTS ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📊"
)

# Apply Bold Modern Professional Theme with Better Contrast
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

/* ========== GLOBAL STYLES ========== */
.main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
    background-attachment: fixed;
    padding: 2rem;
}

.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

/* ========== TYPOGRAPHY ========== */
h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ffffff 0%, #fbbf24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2rem !important;
    text-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    letter-spacing: -0.02em;
}

h2 {
    font-family: 'Poppins', sans-serif;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}

h3 {
    font-family: 'Poppins', sans-serif;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #f3f4f6 !important;
    margin-bottom: 1rem !important;
}

h4 {
    font-family: 'Poppins', sans-serif;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #e5e7eb !important;
}

p, label, span, div {
    font-family: 'Inter', sans-serif;
    color: #f3f4f6 !important;
    font-size: 1rem;
    line-height: 1.6;
}

/* Make captions more visible on dark background */
.caption, [data-testid="stCaptionContainer"] {
    color: #d1d5db !important;
    font-size: 0.9rem !important;
}

/* ========== CARDS & CONTAINERS ========== */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background: rgba(255, 255, 255, 0.98) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 24px !important;
    box-shadow: 
        0 20px 25px -5px rgba(0, 0, 0, 0.2),
        0 10px 10px -5px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.1) !important;
    padding: 2rem !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Make text INSIDE white cards dark and readable */
div[data-testid="stVerticalBlock"] > div[style*="border"] p,
div[data-testid="stVerticalBlock"] > div[style*="border"] label,
div[data-testid="stVerticalBlock"] > div[style*="border"] span,
div[data-testid="stVerticalBlock"] > div[style*="border"] div,
div[data-testid="stVerticalBlock"] > div[style*="border"] h2,
div[data-testid="stVerticalBlock"] > div[style*="border"] h3,
div[data-testid="stVerticalBlock"] > div[style*="border"] h4,
div[data-testid="stVerticalBlock"] > div[style*="border"] * {
    color: #1f2937 !important;
}

div[data-testid="stVerticalBlock"] > div[style*="border"] .caption,
div[data-testid="stVerticalBlock"] > div[style*="border"] [data-testid="stCaptionContainer"] {
    color: #4b5563 !important;
}

/* Ensure form elements inside containers are visible */
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTextInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stSelectbox label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTextArea label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stDateInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTimeInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stNumberInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stSlider label {
    color: #1f2937 !important;
}

div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    transform: translateY(-8px) scale(1.02) !important;
    box-shadow: 
        0 25px 50px -12px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 0 rgba(255, 255, 255, 0.2) !important;
    border-color: rgba(255, 255, 255, 0.7) !important;
}

/* ========== BUTTONS ========== */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border-radius: 16px !important;
    padding: 1rem 2.5rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    text-transform: none !important;
    letter-spacing: 0.02em !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
    transition: left 0.5s !important;
}

.stButton > button:hover::before {
    left: 100% !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    color: white !important;
    box-shadow: 
        0 10px 25px -5px rgba(59, 130, 246, 0.5),
        0 4px 6px -2px rgba(59, 130, 246, 0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    box-shadow: 
        0 20px 35px -5px rgba(59, 130, 246, 0.6),
        0 8px 12px -2px rgba(59, 130, 246, 0.4) !important;
    transform: translateY(-3px) !important;
}

.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #3b82f6 !important;
    border: 3px solid #3b82f6 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 1) !important;
    border-color: #2563eb !important;
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* ========== METRICS ========== */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #ffffff 0%, #eff6ff 100%) !important;
    padding: 2rem !important;
    border-radius: 20px !important;
    border-left: 6px solid #3b82f6 !important;
    box-shadow: 
        0 10px 15px -3px rgba(0, 0, 0, 0.1),
        0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stMetric"]:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.3) !important;
}

div[data-testid="stMetric"] label {
    color: #1f2937 !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1e40af !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
    text-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
}

/* ========== TABS ========== */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background: rgba(255, 255, 255, 0.95);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-radius: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    border-radius: 12px;
    padding: 1rem 2rem;
    color: #1f2937 !important;
    background: transparent;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* ========== INPUT FIELDS ========== */
.stTextInput input, 
.stSelectbox select, 
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
.stNumberInput input {
    border-radius: 12px !important;
    border: 2px solid #cbd5e1 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.3s ease !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    background: white !important;
    color: #1f2937 !important;
}

.stTextInput input:focus, 
.stSelectbox select:focus, 
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* Input labels - light on dark background */
.stTextInput label, .stSelectbox label, .stTextArea label, .stDateInput label, .stTimeInput label, .stNumberInput label {
    color: #f3f4f6 !important;
    font-weight: 600 !important;
}

/* But dark text when inside white cards/forms */
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTextInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stSelectbox label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTextArea label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stDateInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stTimeInput label,
div[data-testid="stVerticalBlock"] > div[style*="border"] .stNumberInput label,
[data-testid="stForm"] .stTextInput label,
[data-testid="stForm"] .stSelectbox label,
[data-testid="stForm"] .stTextArea label,
[data-testid="stForm"] .stDateInput label,
[data-testid="stForm"] .stTimeInput label,
[data-testid="stForm"] .stNumberInput label {
    color: #1f2937 !important;
}

/* Make ALL content inside forms dark and readable */
[data-testid="stForm"],
[data-testid="stForm"] * {
    color: #1f2937 !important;
}

[data-testid="stForm"] h2,
[data-testid="stForm"] h3,
[data-testid="stForm"] h4 {
    color: #111827 !important;
}

[data-testid="stForm"] .caption,
[data-testid="stForm"] [data-testid="stCaptionContainer"] {
    color: #4b5563 !important;
}

/* ========== EXPANDERS ========== */
.streamlit-expanderHeader {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    color: #1e40af !important;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    border: 2px solid #93c5fd !important;
    transition: all 0.3s ease !important;
}

.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
    border-color: #60a5fa !important;
    transform: translateX(4px) !important;
}

/* Make sure expander content is readable */
.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.95) !important;
    padding: 1rem !important;
    border-radius: 0 0 12px 12px !important;
}

.streamlit-expanderContent p,
.streamlit-expanderContent label,
.streamlit-expanderContent span,
.streamlit-expanderContent div,
.streamlit-expanderContent h2,
.streamlit-expanderContent h3,
.streamlit-expanderContent h4,
.streamlit-expanderContent * {
    color: #1f2937 !important;
}

/* Make text inside expanders dark */
.streamlit-expanderContent p,
.streamlit-expanderContent label,
.streamlit-expanderContent span,
.streamlit-expanderContent div {
    color: #1f2937 !important;
}

/* ========== TABLES ========== */
.dataframe {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    border: none !important;
}

.dataframe thead tr {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
}

.dataframe thead th {
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 1.25rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.dataframe tbody td {
    color: #1f2937 !important;
    padding: 1rem !important;
    background: white !important;
}

.dataframe tbody tr {
    transition: all 0.2s ease !important;
    background: white !important;
}

.dataframe tbody tr:hover {
    background: rgba(59, 130, 246, 0.05) !important;
    transform: scale(1.01) !important;
}

/* ========== ALERTS ========== */
.stSuccess {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%) !important;
    color: #065f46 !important;
    border-left: 6px solid #10b981 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2) !important;
}

.stError {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
    color: #991b1b !important;
    border-left: 6px solid #ef4444 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2) !important;
}

.stWarning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
    color: #92400e !important;
    border-left: 6px solid #f59e0b !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.2) !important;
}

.stInfo {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
    color: #1e40af !important;
    border-left: 6px solid #3b82f6 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2) !important;
}

/* ========== SLIDER ========== */
.stSlider > div > div > div {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
}

/* ========== PROGRESS BAR ========== */
.stProgress > div > div > div {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
}

/* ========== SPINNER ========== */
.stSpinner > div {
    border-top-color: #3b82f6 !important;
}

/* ========== SIDEBAR ========== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%) !important;
    backdrop-filter: blur(20px) !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
}

/* ========== ANIMATIONS ========== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.main > div {
    animation: fadeIn 0.6s ease-out;
}

/* ========== SPECIAL EFFECTS ========== */
.stButton > button[kind="primary"]::after {
    content: '→';
    margin-left: 8px;
    transition: margin-left 0.3s ease;
}

.stButton > button[kind="primary"]:hover::after {
    margin-left: 12px;
}

/* ========== COMPREHENSIVE FIX FOR WHITE BACKGROUNDS ========== */
/* Any element with a white or light background should have dark text */
[style*="background: white"],
[style*="background: #fff"],
[style*="background: rgb(255, 255, 255)"],
[style*="background-color: white"],
[style*="background-color: #fff"],
[style*="background-color: rgb(255, 255, 255)"],
div[style*="background: rgba(255, 255, 255"],
div[class*="stContainer"] {
    color: #1f2937 !important;
}

[style*="background: white"] *,
[style*="background: #fff"] *,
[style*="background: rgb(255, 255, 255)"] *,
[style*="background-color: white"] *,
[style*="background-color: #fff"] *,
[style*="background-color: rgb(255, 255, 255)"] *,
div[style*="background: rgba(255, 255, 255"] *,
div[class*="stContainer"] * {
    color: #1f2937 !important;
}

/* Streamlit's default containers */
.element-container {
    color: #f3f4f6 !important;
}

/* Make markdown inside white areas dark */
.stMarkdown {
    color: inherit !important;
}

/* Specific override for columns and containers */
.row-widget,
.stColumn {
    color: #f3f4f6 !important;
}

/* Force ALL st.container(border=True) to have dark text */
[data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"],
[data-testid="column"] > div,
.stContainer,
.css-container {
    color: #1f2937 !important;
}

[data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] *,
[data-testid="column"] > div *,
.stContainer *,
.css-container * {
    color: #1f2937 !important;
}

/* Make sure button text inside containers is visible */
div[style*="border"] .stButton > button[kind="secondary"] {
    color: #3b82f6 !important;
}

/* Ensure metric values are visible */
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #1e40af !important;
}

/* Tab content should be dark */
.stTabs [data-baseweb="tab-panel"] {
    color: #1f2937 !important;
}

.stTabs [data-baseweb="tab-panel"] * {
    color: #1f2937 !important;
}

</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = 'plotly_dark'

MOCK_STAFF = [
    {'id': 's1', 'name': 'Emily Jones', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's2', 'name': 'Daniel Lee', 'role': 'PY', 'active': True, 'archived': False},
    {'id': 's3', 'name': 'Sarah Chen', 'role': 'SY', 'active': True, 'archived': False},
    {'id': 's4', 'name': 'Admin User', 'role': 'ADM', 'active': True, 'archived': False},
    {'id': 's5', 'name': 'Michael Torres', 'role': 'JP', 'active': True, 'archived': False},
    {'id': 's6', 'name': 'Jessica Williams', 'role': 'PY', 'active': True, 'archived': False},
]

# Staff roles available
STAFF_ROLES = ['JP', 'PY', 'SY', 'ADM', 'TRT', 'External SSO']

MOCK_STUDENTS = [
    {'id': 'stu_001', 'name': 'Izack N.', 'grade': '7', 'dob': '2012-03-15', 'edid': 'ED12345', 'profile_status': 'Complete', 'program': 'SY', 'archived': False},
    {'id': 'stu_002', 'name': 'Mia K.', 'grade': '8', 'dob': '2011-07-22', 'edid': 'ED12346', 'profile_status': 'Draft', 'program': 'PY', 'archived': False},
    {'id': 'stu_003', 'name': 'Liam B.', 'grade': '9', 'dob': '2010-11-08', 'edid': 'ED12347', 'profile_status': 'Pending', 'program': 'SY', 'archived': False},
    {'id': 'stu_004', 'name': 'Emma T.', 'grade': 'R', 'dob': '2017-05-30', 'edid': 'ED12348', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_005', 'name': 'Oliver S.', 'grade': 'Y2', 'dob': '2015-09-12', 'edid': 'ED12349', 'profile_status': 'Complete', 'program': 'JP', 'archived': False},
    {'id': 'stu_006', 'name': 'Sophie M.', 'grade': 'Y5', 'dob': '2014-01-25', 'edid': 'ED12350', 'profile_status': 'Complete', 'program': 'PY', 'archived': False},
    {'id': 'stu_arch_001', 'name': 'Jackson P.', 'grade': 'Y10', 'dob': '2009-04-17', 'edid': 'ED12351', 'profile_status': 'Complete', 'program': 'SY', 'archived': True},
    {'id': 'stu_arch_002', 'name': 'Ava L.', 'grade': 'Y6', 'dob': '2013-12-03', 'edid': 'ED12352', 'profile_status': 'Complete', 'program': 'PY', 'archived': True},
]

# Program options
PROGRAM_OPTIONS = ['JP', 'PY', 'SY']

# Grade options by program
GRADE_OPTIONS = {
    'JP': ['R', 'Y1', 'Y2'],
    'PY': ['Y3', 'Y4', 'Y5', 'Y6'],
    'SY': ['Y7', 'Y8', 'Y9', 'Y10', 'Y11', 'Y12']
}

behaviour_LEVELS = ['1 - Low Intensity', '2 - Moderate', '3 - High Risk']
behaviourS_FBA = ['Verbal Refusal', 'Elopement', 'Property Destruction', 'Aggression (Peer)', 'Other - Specify'] 

ANTECEDENTS_NEW = [
    "Requested to transition activity",
    "Given instruction/demand (Academic)",
    "Given instruction/demand (Non-Academic)",
    "Peer conflict/Teasing",
    "Staff attention shifted away",
    "Unstructured free time (Recess/Lunch)",
    "Sensory over-stimulation (Noise/Lights)",
    "Access to preferred item/activity denied"
]

INTERVENTIONS = [
    "Prompted use of coping skill (e.g., breathing)",
    "Proximity control/Non-verbal cue",
    "Redirection to a preferred activity",
    "Offered a break/Choice of task",
    "Used planned ignoring of minor behaviour",
    "Staff de-escalation script/Verbal coaching",
    "Removed other students from area for safety",
    "Called for staff support/Backup"
]

SUPPORT_TYPES = [
    "1:1 (Individual Support)",
    "Independent (No direct support)",
    "Small Group (3-5 students)",
    "Large Group (Whole class/assembly)"
]

LOCATIONS = [
    "--- Select Location ---",
    "JP Classroom",
    "JP Spill Out",
    "PY Classroom",
    "PY Spill Out",
    "SY Classroom",
    "SY Spill Out",
    "Student Kitchen",
    "Admin",
    "Gate",
    "Library",
    "Van/Kia",
    "Swimming",
    "Yard",
    "Playground",
    "Toilets",
    "Excursion",
    "Other"
]

VALID_PAGES = ['login', 'landing', 'program_students', 'direct_log_form', 'critical_incident_abch', 'student_analysis', 'admin_portal']

# --- DATA LOADING FUNCTIONS (SUPABASE) ---

def load_students_from_db() -> List[Dict[str, Any]]:
    """Load all students from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('students').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error loading students: {e}")
        return []

def load_staff_from_db() -> List[Dict[str, Any]]:
    """Load all staff from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('staff').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error loading staff: {e}")
        return []

def load_incidents_from_db() -> List[Dict[str, Any]]:
    """Load all incidents from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('incidents').select('*').execute()
        
        # Normalize field names for backward compatibility
        incidents = []
        if response.data:
            for inc in response.data:
                # Create a copy with both old and new field names
                normalized = inc.copy()
                normalized['date'] = inc.get('incident_date', inc.get('date', ''))
                normalized['time'] = inc.get('incident_time', inc.get('time', ''))
                normalized['day'] = inc.get('day_of_week', inc.get('day', ''))
                incidents.append(normalized)
        
        return incidents
    except Exception as e:
        logger.error(f"Error loading incidents: {e}")
        return []

def load_system_settings() -> Dict[str, Any]:
    """Load system settings from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('system_settings').select('*').execute()
        
        settings = {}
        if response.data:
            for setting in response.data:
                settings[setting['setting_key']] = setting['setting_value']
        
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}

# --- SESSION STATE INITIALIZATION ---

def initialize_session_state():
    """Initialize all session state variables from Supabase"""
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data from database..."):
            # Load from Supabase
            st.session_state.students_list = load_students_from_db()
            st.session_state.staff_list = load_staff_from_db()
            st.session_state.incidents = load_incidents_from_db()
            st.session_state.system_settings = load_system_settings()
            st.session_state.data_loaded = True
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

# --- 2. GLOBAL HELPERS & CORE LOGIC FUNCTIONS ---

def navigate_to(page: str, student_id: Optional[str] = None, program: Optional[str] = None):
    """Changes the current page in session state."""
    try:
        if page not in VALID_PAGES:
            raise ValidationError(f"Invalid page: {page}", "Cannot navigate to requested page")
        
        st.session_state.current_page = page
        if student_id:
            st.session_state.selected_student_id = student_id
        if program:
            st.session_state.selected_program = program
        st.rerun()
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        st.error("Navigation failed.")
        st.session_state.current_page = 'landing'
        st.rerun()

def get_student_by_id(student_id: str) -> Optional[Dict[str, str]]:
    """Safely retrieves student data."""
    try:
        if not student_id:
            return None
        return next((s for s in st.session_state.students_list if s['id'] == student_id), None)
    except Exception as e:
        logger.error(f"Error retrieving student: {e}")
        return None

def get_active_staff() -> List[Dict[str, Any]]:
    """Returns active, non-archived staff."""
    try:
        return [s for s in st.session_state.staff_list if s['active'] and not s.get('archived', False)]
    except Exception as e:
        logger.error(f"Error retrieving staff: {e}")
        return []

def get_staff_by_id(staff_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves staff member by ID."""
    try:
        if not staff_id:
            return None
        return next((s for s in st.session_state.staff_list if s['id'] == staff_id), None)
    except Exception as e:
        logger.error(f"Error retrieving staff member: {e}")
        return None

def get_session_window(incident_time: time) -> str:
    """Calculates session window."""
    try:
        if time(9, 0) <= incident_time <= time(11, 0):
            return "Morning (9:00am - 11:00am)"
        elif time(11, 0, 1) <= incident_time <= time(13, 0):
            return "Middle (11:01am - 1:00pm)"
        elif time(13, 0, 1) <= incident_time <= time(14, 45):
            return "Afternoon (1:01pm - 2:45pm)"
        else:
            return "Outside School Hours (N/A)"
    except Exception as e:
        return "Unknown Session"

def add_staff_member(first_name: str, last_name: str, email: str, role: str) -> bool:
    """Adds a new staff member to Supabase."""
    try:
        if not first_name or not first_name.strip():
            raise ValidationError("First name cannot be empty", "Please enter a first name")
        
        if not last_name or not last_name.strip():
            raise ValidationError("Last name cannot be empty", "Please enter a last name")
        
        if not email or not email.strip():
            raise ValidationError("Email cannot be empty", "Please enter an email address")
        
        if '@' not in email:
            raise ValidationError("Invalid email", "Please enter a valid email address")
        
        if not role or role == "--- Select Role ---":
            raise ValidationError("Role must be selected", "Please select a role")
        
        full_name = f"{first_name.strip()} {last_name.strip()}"
        
        # Check for duplicate email in current session
        existing_email = [s for s in st.session_state.staff_list if s.get('email', '').lower() == email.strip().lower() and not s.get('archived', False)]
        if existing_email:
            raise ValidationError("Duplicate email", "A staff member with this email already exists")
        
        new_staff = {
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'name': full_name,
            'email': email.strip().lower(),
            'role': role,
            'active': True,
            'archived': False
        }
        
        # Insert into Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').insert(new_staff).execute()
        
        if response.data:
            # Update session state
            st.session_state.staff_list.append(response.data[0])
            logger.info(f"Added staff member: {full_name} ({email}, {role})")
            return True
        else:
            raise AppError("Database insert failed", "Could not add staff member")
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding staff: {e}")
        raise AppError("Failed to add staff member", "Could not add staff member. Please try again.")

def archive_staff_member(staff_id: str) -> bool:
    """Archives a staff member in Supabase."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot archive: staff member not found")
        
        # Update in Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').update({
            'archived': True,
            'active': False,
            'archived_date': datetime.now().isoformat()
        }).eq('id', staff_id).execute()
        
        if response.data:
            # Update session state
            staff['archived'] = True
            staff['active'] = False
            staff['archived_date'] = datetime.now().isoformat()
            
            logger.info(f"Archived staff member: {staff['name']}")
            return True
        else:
            raise AppError("Database update failed", "Could not archive staff member")
        
    except Exception as e:
        logger.error(f"Error archiving staff: {e}")
        raise AppError("Failed to archive staff member", "Could not archive staff member. Please try again.")

def unarchive_staff_member(staff_id: str) -> bool:
    """Unarchives a staff member in Supabase."""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            raise ValidationError("Staff member not found", "Cannot unarchive: staff member not found")
        
        # Update in Supabase
        supabase = get_supabase_client()
        response = supabase.table('staff').update({
            'archived': False,
            'active': True
        }).eq('id', staff_id).execute()
        
        if response.data:
            # Update session state
            staff['archived'] = False
            staff['active'] = True
            
            logger.info(f"Unarchived staff member: {staff['name']}")
            return True
        else:
            raise AppError("Database update failed", "Could not unarchive staff member")
        
    except Exception as e:
        logger.error(f"Error unarchiving staff: {e}")
        raise AppError("Failed to unarchive staff member", "Could not unarchive staff member. Please try again.")

def add_student(first_name: str, last_name: str, dob: datetime.date, program: str, grade: str, edid: str) -> bool:
    """Adds a new student to Supabase."""
    try:
        if not first_name or not first_name.strip():
            raise ValidationError("First name cannot be empty", "Please enter a first name")
        
        if not last_name or not last_name.strip():
            raise ValidationError("Last name cannot be empty", "Please enter a last name")
        
        if not program or program == "--- Select Program ---":
            raise ValidationError("Program must be selected", "Please select a program")
        
        if not grade or grade == "--- Select Grade ---":
            raise ValidationError("Grade must be selected", "Please select a grade")
        
        if not dob:
            raise ValidationError("Date of birth is required", "Please enter date of birth")
        
        if not edid or not edid.strip():
            raise ValidationError("EDID is required", "Please enter EDID")
        
        full_name = f"{first_name.strip()} {last_name.strip()}"
        
        # Check for duplicate EDID in current session
        existing_edid = [s for s in st.session_state.students_list if s.get('edid', '').upper() == edid.strip().upper() and not s.get('archived', False)]
        if existing_edid:
            raise ValidationError("Duplicate EDID", f"A student with EDID {edid} already exists")
        
        # Validate DOB is not in the future
        if dob > datetime.now().date():
            raise ValidationError("Invalid date of birth", "Date of birth cannot be in the future")
        
        new_student = {
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'name': full_name,
            'dob': dob.strftime('%Y-%m-%d'),
            'program': program,
            'grade': grade,
            'edid': edid.strip().upper(),
            'profile_status': 'Draft',
            'archived': False
        }
        
        # Insert into Supabase
        supabase = get_supabase_client()
        response = supabase.table('students').insert(new_student).execute()
        
        if response.data:
            # Update session state
            st.session_state.students_list.append(response.data[0])
            logger.info(f"Added student: {full_name} (EDID: {edid}, Program: {program})")
            return True
        else:
            raise AppError("Database insert failed", "Could not add student")
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        raise AppError("Failed to add student", "Could not add student. Please try again.")

def get_students_by_program(program: str, include_archived: bool = False) -> List[Dict[str, Any]]:
    """Gets all students for a specific program."""
    try:
        students = st.session_state.students_list
        filtered = [s for s in students if s.get('program') == program]
        
        if not include_archived:
            filtered = [s for s in filtered if not s.get('archived', False)]
        
        return filtered
    except Exception as e:
        logger.error(f"Error retrieving students by program: {e}")
        return []

# --- AUTHENTICATION FUNCTIONS ---

def verify_login(email: str) -> Optional[Dict[str, Any]]:
    """Verifies if email exists in staff database."""
    try:
        if not email or not email.strip():
            return None
        
        email = email.strip().lower()
        
        # Check in staff list
        staff_member = next((s for s in st.session_state.staff_list if s.get('email', '').lower() == email and not s.get('archived', False)), None)
        
        return staff_member
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None

# --- VALIDATION FUNCTIONS ---

def validate_incident_form(location, reported_by, behaviour_type, severity_level, incident_date, incident_time):
    """Validates incident form."""
    errors = []
    
    if location == "--- Select Location ---":
        errors.append("Please select a valid Location")
    if not isinstance(reported_by, dict) or reported_by.get('id') is None:
        errors.append("Please select a Staff Member")
    if behaviour_type == "--- Select behaviour ---":
        errors.append("Please select a behaviour Type")
    if not (1 <= severity_level <= 5):
        errors.append("Severity level must be between 1 and 5")
    if not incident_date:
        errors.append("Date is required")
    if not incident_time:
        errors.append("Time is required")
    
    if errors:
        raise ValidationError("Form validation failed", "Please correct: " + ", ".join(errors))

def validate_abch_form(context, location, behaviour_desc, consequence, manager_notify, parent_notify):
    """Validates ABCH form."""
    errors = []
    
    if not location or location.strip() == "":
        errors.append("Location is required")
    if not context or context.strip() == "":
        errors.append("Context is required")
    if not behaviour_desc or behaviour_desc.strip() == "":
        errors.append("behaviour description is required")
    if not consequence or consequence.strip() == "":
        errors.append("Consequences are required")
    if not manager_notify:
        errors.append("Line Manager notification required")
    if not parent_notify:
        errors.append("Parent notification required")
    
    if errors:
        raise ValidationError("ABCH validation failed", "Please correct: " + ", ".join(errors))

# --- LOGIN PAGE ---

@handle_errors("Unable to load login page")
def render_login_page():
    """Renders the login page with email authentication."""
    
    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">🔐</div>
        <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
        <p class="hero-subtitle">Staff Login</p>
        <p class="hero-tagline">Please enter your registered staff email address to access the system</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🔑 Login")
            
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                key="login_email"
            )
            
            if st.button("🚀 Login", type="primary", use_container_width=True):
                if email:
                    staff_member = verify_login(email)
                    if staff_member:
                        st.session_state.logged_in = True
                        st.session_state.current_user = staff_member
                        st.session_state.current_page = 'landing'
                        st.success(f"✅ Welcome back, {staff_member['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Email not found. Please contact an administrator to register.")
                else:
                    st.warning("⚠️ Please enter your email address")
            
            st.markdown("---")
            st.caption("💡 **Note:** Only registered staff members can access this system. Contact your administrator if you need access.")

# --- LANDING PAGE ---

@handle_errors("Unable to load landing page")
def render_landing_page():
    """Renders sleek landing page."""
    
    # User info and logout button at top
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        current_user = st.session_state.get('current_user', {})
        st.markdown(f"### 👋 Welcome, {current_user.get('name', 'User')}!")
        st.caption(f"Role: {current_user.get('role', 'N/A')} | {current_user.get('email', 'N/A')}")
    with col_logout:
        st.markdown("##")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    st.markdown("---")
    
    # Spectacular animated header
    st.markdown("""
    <style>
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        background: rgba(255, 255, 255, 0.15);
        -webkit-backdrop-filter: blur(20px);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.2);
    }
    
    .hero-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: gradient-shift 5s ease infinite;
        letter-spacing: -0.03em;
        line-height: 1.2;
        text-shadow: 0 0 40px rgba(167, 139, 250, 0.5);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        letter-spacing: 0.02em;
    }
    
    .hero-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .feature-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        margin: 0.5rem;
        font-size: 0.9rem;
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .feature-badge:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    .divider-line {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
        margin: 3rem 0;
        border-radius: 2px;
    }
    </style>
    
    <div class="hero-section">
        <div class="hero-icon">📊✨</div>
        <h1 class="hero-title">Behaviour Support<br/>& Data Analysis</h1>
        <p class="hero-subtitle">Transform Student Outcomes with Evidence-Based Insights</p>
        <p class="hero-tagline">Comprehensive incident tracking, powerful analytics, and AI-driven recommendations aligned with CPI, Trauma-Informed Practice, BSEM, and the Australian Curriculum</p>
        <div style="margin-top: 2rem;">
            <span class="feature-badge">📈 Real-time Analytics</span>
            <span class="feature-badge">🎯 Evidence-Based</span>
            <span class="feature-badge">🔒 Secure Database</span>
            <span class="feature-badge">📱 Cloud-Based</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    
    st.markdown("### 📚 Select Your Program")
    st.caption("Choose a program to view students, log incidents, and access analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎨 Junior Primary")
        st.caption("Reception - Year 2")
        if st.button("Enter JP Program", key="jp_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='JP')
    
    with col2:
        st.markdown("#### 📖 Primary Years")
        st.caption("Year 3 - Year 6")
        if st.button("Enter PY Program", key="py_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='PY')
    
    with col3:
        st.markdown("#### 🎓 Senior Years")
        st.caption("Year 7 - Year 12")
        if st.button("Enter SY Program", key="sy_btn", use_container_width=True, type="primary"):
            navigate_to('program_students', program='SY')
    
    st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Actions")
    st.caption("Fast access to common tasks")
    
    col_quick1, col_quick2 = st.columns(2)
    
    with col_quick1:
        st.markdown("#### 📝 Quick Incident Log")
        st.caption("Select a student and immediately log a new incident")
        all_active_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        student_options = [{'id': None, 'name': '--- Select Student ---'}] + all_active_students
        selected_student = st.selectbox(
            "Select Student",
            options=student_options,
            format_func=lambda x: x['name'],
            key="quick_log_student",
            label_visibility="collapsed"
        )
        
        if selected_student and selected_student['id']:
            if st.button("Start Quick Log", key="quick_log_btn", use_container_width=True, type="primary"):
                navigate_to('direct_log_form', student_id=selected_student['id'])
    
    with col_quick2:
        st.markdown("#### 🔐 Admin Portal")
        st.caption("Manage staff, students, and system settings")
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("Access Admin Portal", key="admin_btn", use_container_width=True, type="primary"):
            navigate_to('admin_portal')

# --- PROGRAM STUDENTS PAGE ---

@handle_errors("Unable to load program students")
def render_program_students():
    """Renders student list for selected program."""
    program = st.session_state.get('selected_program', 'JP')
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        program_names = {'JP': 'Junior Primary', 'PY': 'Primary Years', 'SY': 'Senior Years'}
        st.title(f"{program_names.get(program, program)} Program")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📚 Current Students", "📦 Archived Students"])
    
    with tab1:
        current_students = get_students_by_program(program, include_archived=False)
        
        if not current_students:
            st.info(f"No current students in the {program} program.")
        else:
            st.markdown(f"### Current Students ({len(current_students)})")
            
            cols_per_row = 3
            for i in range(0, len(current_students), cols_per_row):
                cols = st.columns(cols_per_row)
                for idx, student in enumerate(current_students[i:i+cols_per_row]):
                    with cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"### {student['name']}")
                            st.markdown(f"**Grade:** {student['grade']}")
                            st.caption(f"EDID: {student.get('edid', 'N/A')}")
                            
                            incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                            st.metric("Incidents", incident_count)
                            
                            col_view, col_log = st.columns(2)
                            with col_view:
                                if st.button("👁️ View", key=f"view_{student['id']}", use_container_width=True):
                                    navigate_to('student_analysis', student_id=student['id'])
                            with col_log:
                                if st.button("📝 Log", key=f"log_{student['id']}", use_container_width=True):
                                    navigate_to('direct_log_form', student_id=student['id'])
    
    with tab2:
        archived_students = [s for s in st.session_state.students_list if s.get('program') == program and s.get('archived', False)]
        
        if not archived_students:
            st.info(f"No archived students in the {program} program.")
        else:
            st.markdown(f"### Archived Students ({len(archived_students)})")
            st.caption("Students who have completed the program - read-only")
            
            for student in archived_students:
                with st.expander(f"📦 {student['name']} - Grade {student['grade']}"):
                    st.markdown(f"**Profile Status:** {student.get('profile_status', 'N/A')}")
                    st.markdown(f"**EDID:** {student.get('edid', 'N/A')}")
                    
                    incident_count = len([inc for inc in st.session_state.get('incidents', []) if inc.get('student_id') == student['id']])
                    st.metric("Total Incidents", incident_count)
                    
                    if st.button("View Historical Data", key=f"view_arch_{student['id']}"):
                        navigate_to('student_analysis', student_id=student['id'])

# --- ADMIN PORTAL ---

@handle_errors("Unable to load admin portal")
def render_admin_portal():
    """Renders the admin portal with staff management."""
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title("🔐 Admin Portal")
    with col_back:
        if st.button("⬅ Back to Home"):
            navigate_to('landing')
    
    st.markdown("---")
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Staff Management", "🎓 Student Management", "📊 Reports", "⚙️ Settings"])
    
    with tab1:
        render_staff_management()
    
    with tab2:
        render_student_management()
    
    with tab3:
        st.markdown("### 📊 System Reports")
        st.info("Reports functionality - to be implemented")
    
    with tab4:
        st.markdown("### ⚙️ System Settings")
        st.info("Settings functionality - to be implemented")

@handle_errors("Unable to load staff management")
def render_staff_management():
    """Renders staff management section."""
    
    st.markdown("## 👥 Staff Management")
    st.markdown("---")
    
    # Sub-tabs for active and archived staff
    staff_tab1, staff_tab2 = st.tabs(["✅ Active Staff", "📦 Archived Staff"])
    
    with staff_tab1:
        st.markdown("### Add New Staff Member")
        
        col_add1, col_add2, col_add3, col_add4 = st.columns([2, 2, 3, 2])
        
        with col_add1:
            new_staff_first_name = st.text_input("First Name", key="new_staff_first_name", placeholder="First name")
        
        with col_add2:
            new_staff_last_name = st.text_input("Last Name", key="new_staff_last_name", placeholder="Last name")
        
        with col_add3:
            new_staff_email = st.text_input("Email", key="new_staff_email", placeholder="email@example.com")
        
        with col_add4:
            new_staff_role = st.selectbox(
                "Role",
                options=["--- Select Role ---"] + STAFF_ROLES,
                key="new_staff_role"
            )
        
        col_add_btn = st.columns([4, 1])
        with col_add_btn[1]:
            if st.button("➕ Add Staff", type="primary", use_container_width=True):
                try:
                    if add_staff_member(new_staff_first_name, new_staff_last_name, new_staff_email, new_staff_role):
                        st.success(f"✅ Added {new_staff_first_name} {new_staff_last_name}")
                        st.rerun()
                except (ValidationError, AppError) as e:
                    st.error(e.user_message)
        
        st.markdown("---")
        st.markdown("### Current Active Staff")
        
        active_staff = [s for s in st.session_state.staff_list if not s.get('archived', False)]
        
        if not active_staff:
            st.info("No active staff members")
        else:
            # Group staff by role
            staff_by_role = {}
            for staff in active_staff:
                role = staff.get('role', 'Unknown')
                if role not in staff_by_role:
                    staff_by_role[role] = []
                staff_by_role[role].append(staff)
            
            # Display by role
            for role in STAFF_ROLES:
                if role in staff_by_role:
                    with st.expander(f"**{role}** ({len(staff_by_role[role])} staff)", expanded=True):
                        for staff in staff_by_role[role]:
                            col_staff1, col_staff2, col_staff3 = st.columns([3, 2, 1])
                            
                            with col_staff1:
                                st.markdown(f"**{staff['name']}**")
                            
                            with col_staff2:
                                if staff.get('created_date'):
                                    st.caption(f"Added: {staff['created_date']}")
                            
                            with col_staff3:
                                if st.button("🗄️ Archive", key=f"archive_{staff['id']}", use_container_width=True):
                                    try:
                                        if archive_staff_member(staff['id']):
                                            st.success(f"Archived {staff['name']}")
                                            st.rerun()
                                    except AppError as e:
                                        st.error(e.user_message)
    
    with staff_tab2:
        st.markdown("### Archived Staff Members")
        st.caption("These staff members are no longer active but remain in the system for historical records")
        
        archived_staff = [s for s in st.session_state.staff_list if s.get('archived', False)]
        
        if not archived_staff:
            st.info("No archived staff members")
        else:
            for staff in archived_staff:
                with st.expander(f"📦 {staff['name']} - {staff.get('role', 'N/A')}"):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.markdown(f"**Role:** {staff.get('role', 'N/A')}")
                        if staff.get('created_date'):
                            st.markdown(f"**Added:** {staff['created_date']}")
                    
                    with col_info2:
                        if staff.get('archived_date'):
                            st.markdown(f"**Archived:** {staff['archived_date']}")
                    
                    if st.button("♻️ Restore Staff Member", key=f"restore_{staff['id']}"):
                        try:
                            if unarchive_staff_member(staff['id']):
                                st.success(f"Restored {staff['name']}")
                                st.rerun()
                        except AppError as e:
                            st.error(e.user_message)

@handle_errors("Unable to load student management")
def render_student_management():
    """Renders student management section."""
    
    st.markdown("## 🎓 Student Management")
    st.markdown("---")
    
    st.markdown("### Add New Student")
    
    col_add1, col_add2, col_add3, col_add4, col_add5 = st.columns([2, 2, 1.5, 1, 1])
    
    with col_add1:
        new_student_first_name = st.text_input("First Name", key="new_student_first_name", placeholder="First name")
    
    with col_add2:
        new_student_last_name = st.text_input("Last Name", key="new_student_last_name", placeholder="Last name")
    
    with col_add3:
        new_student_dob = st.date_input(
            "Date of Birth (DD/MM/YYYY)",
            key="new_student_dob",
            min_value=datetime(1990, 1, 1).date(),
            max_value=datetime.now().date(),
            value=datetime(2015, 1, 1).date(),
            format="DD/MM/YYYY"
        )
    
    with col_add4:
        new_student_program = st.selectbox(
            "Program",
            options=["--- Select Program ---"] + PROGRAM_OPTIONS,
            key="new_student_program"
        )
    
    with col_add5:
        # Dynamic grade options based on selected program
        if new_student_program and new_student_program != "--- Select Program ---":
            grade_options = ["--- Select Grade ---"] + GRADE_OPTIONS.get(new_student_program, [])
        else:
            grade_options = ["--- Select Grade ---"]
        
        new_student_grade = st.selectbox(
            "Grade",
            options=grade_options,
            key="new_student_grade"
        )
    
    col_edid, col_add_btn = st.columns([3, 1])
    
    with col_edid:
        new_student_edid = st.text_input(
            "EDID (Education Department ID)",
            key="new_student_edid",
            placeholder="e.g., ED12345",
            help="Unique identifier from Education Department"
        )
    
    with col_add_btn:
        st.markdown("##")  # Spacing
        if st.button("➕ Add Student", type="primary", use_container_width=True):
            try:
                if add_student(
                    new_student_first_name,
                    new_student_last_name,
                    new_student_dob,
                    new_student_program,
                    new_student_grade,
                    new_student_edid
                ):
                    st.success(f"✅ Added {new_student_first_name} {new_student_last_name} to {new_student_program} Program")
                    st.rerun()
            except (ValidationError, AppError) as e:
                st.error(e.user_message)
    
    st.markdown("---")
    st.markdown("### Current Students by Program")
    
    # Group students by program
    program_tabs = st.tabs(["📘 Junior Primary", "📗 Primary Years", "📙 Senior Years", "📚 All Students"])
    
    programs = ['JP', 'PY', 'SY']
    
    for idx, program in enumerate(programs):
        with program_tabs[idx]:
            students_in_program = get_students_by_program(program, include_archived=False)
            
            if not students_in_program:
                st.info(f"No students currently in {program} program")
            else:
                st.markdown(f"**Total Students:** {len(students_in_program)}")
                
                # Create a dataframe for better display
                student_data = []
                for student in students_in_program:
                    age = calculate_age(student.get('dob', ''))
                    student_data.append({
                        'Name': student['name'],
                        'Grade': student['grade'],
                        'EDID': student.get('edid', 'N/A'),
                        'Age': age,
                        'DOB': student.get('dob', 'N/A'),
                        'Status': student.get('profile_status', 'Draft'),
                        'Added': student.get('created_date', 'N/A')
                    })
                
                df = pd.DataFrame(student_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    # All students view
    with program_tabs[3]:
        all_students = [s for s in st.session_state.students_list if not s.get('archived', False)]
        
        if not all_students:
            st.info("No students in the system")
        else:
            st.markdown(f"**Total Students Across All Programs:** {len(all_students)}")
            
            # Summary by program
            col_jp, col_py, col_sy = st.columns(3)
            with col_jp:
                jp_count = len(get_students_by_program('JP', include_archived=False))
                st.metric("JP Students", jp_count)
            with col_py:
                py_count = len(get_students_by_program('PY', include_archived=False))
                st.metric("PY Students", py_count)
            with col_sy:
                sy_count = len(get_students_by_program('SY', include_archived=False))
                st.metric("SY Students", sy_count)
            
            st.markdown("---")
            
            # Full student list
            student_data = []
            for student in sorted(all_students, key=lambda x: (x.get('program', ''), x.get('name', ''))):
                age = calculate_age(student.get('dob', ''))
                student_data.append({
                    'Name': student['name'],
                    'Program': student['program'],
                    'Grade': student['grade'],
                    'EDID': student.get('edid', 'N/A'),
                    'Age': age,
                    'DOB': student.get('dob', 'N/A'),
                    'Status': student.get('profile_status', 'Draft'),
                })
            
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def calculate_age(dob_str: str) -> str:
    """Calculate age from date of birth string."""
    try:
        if not dob_str:
            return "N/A"
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return str(age)
    except Exception as e:
        logger.error(f"Error calculating age: {e}")
        return "N/A"

def generate_student_report(student: Dict[str, Any], incidents: List[Dict[str, Any]]) -> Optional[str]:
    """Generates a comprehensive Word document report with charts and analysis."""
    try:
        import subprocess
        
        # Check if Node.js is available
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.warning("Node.js not available - cannot generate reports")
            return None
        
        # Create temporary directory for charts
        chart_dir = "/home/claude/report_charts"
        subprocess.run(['mkdir', '-p', chart_dir], check=True)
        
        # Generate and save charts as images
        chart_files = {}
        
        # 1. Timeline chart
        timeline_data = pd.DataFrame([{
            'Date': inc['date'],
            'Count': 1
        } for inc in incidents])
        timeline_data['Date'] = pd.to_datetime(timeline_data['Date'])
        daily_counts = timeline_data.groupby('Date').size().reset_index(name='Count')
        
        fig = px.line(daily_counts, x='Date', y='Count', title='Incidents Over Time', markers=True)
        fig.write_image(f"{chart_dir}/timeline.png", width=800, height=400)
        chart_files['timeline'] = f"{chart_dir}/timeline.png"
        
        # 2. behaviour frequency chart
        behaviour_counts = pd.DataFrame(incidents)['behaviour_type'].value_counts().reset_index()
        behaviour_counts.columns = ['behaviour', 'Count']
        fig = px.bar(behaviour_counts, x='Count', y='behaviour', orientation='h', title='behaviour Frequency')
        fig.write_image(f"{chart_dir}/behaviours.png", width=800, height=400)
        chart_files['behaviours'] = f"{chart_dir}/behaviours.png"
        
        # 3. Day of week chart
        day_counts = pd.DataFrame(incidents)['day'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Count']
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
        day_counts = day_counts.sort_values('Day')
        fig = px.bar(day_counts, x='Day', y='Count', title='Incidents by Day of Week')
        fig.write_image(f"{chart_dir}/days.png", width=800, height=400)
        chart_files['days'] = f"{chart_dir}/days.png"
        
        # 4. Location chart
        location_counts = pd.DataFrame(incidents)['location'].value_counts().reset_index()
        location_counts.columns = ['Location', 'Count']
        fig = px.bar(location_counts.head(10), x='Count', y='Location', orientation='h', title='Top 10 Incident Locations')
        fig.write_image(f"{chart_dir}/locations.png", width=800, height=400)
        chart_files['locations'] = f"{chart_dir}/locations.png"
        
        # Calculate key statistics
        avg_severity = sum([inc.get('severity', 0) for inc in incidents]) / len(incidents)
        critical_count = len([inc for inc in incidents if inc.get('is_critical', False)])
        critical_rate = (critical_count / len(incidents) * 100) if len(incidents) > 0 else 0
        
        behaviour_counts_dict = pd.DataFrame(incidents)['behaviour_type'].value_counts()
        top_behaviour = behaviour_counts_dict.index[0] if len(behaviour_counts_dict) > 0 else "N/A"
        top_behaviour_count = behaviour_counts_dict.iloc[0] if len(behaviour_counts_dict) > 0 else 0
        
        antecedent_counts = pd.DataFrame(incidents)['antecedent'].value_counts()
        top_antecedent = antecedent_counts.index[0] if len(antecedent_counts) > 0 else "N/A"
        
        location_counts_stat = pd.DataFrame(incidents)['location'].value_counts()
        top_location = location_counts_stat.index[0] if len(location_counts_stat) > 0 else "N/A"
        
        day_counts_stat = pd.DataFrame(incidents)['day'].value_counts()
        top_day = day_counts_stat.index[0] if len(day_counts_stat) > 0 else "N/A"
        
        session_counts = pd.DataFrame(incidents)['session'].value_counts()
        top_session = session_counts.index[0] if len(session_counts) > 0 else "N/A"
        
        behaviour_pct = (top_behaviour_count/len(incidents)*100) if len(incidents) > 0 else 0
        
        # Note: Full docx generation code omitted for brevity
        # Would require Node.js with docx library installed
        
        logger.info("Report generation attempted but requires Node.js/docx setup")
        return None
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return None

# --- STAFF SELECTOR COMPONENT ---

def render_staff_selector(label: str = "Staff Member", key: str = "staff_selector", include_special_options: bool = True):
    """
    Renders a staff selector with optional TRT and External SSO options.
    Returns a dict with staff info, or special options if selected.
    """
    
    active_staff = get_active_staff()
    
    # Build options list
    options = [{'id': None, 'name': '--- Select Staff ---', 'role': None, 'special': False}]
    
    # Add special options if enabled
    if include_special_options:
        options.append({'id': 'TRT', 'name': 'TRT (Relief Teacher)', 'role': 'TRT', 'special': True})
        options.append({'id': 'External_SSO', 'name': 'External SSO', 'role': 'External SSO', 'special': True})
        options.append({'id': 'divider', 'name': '─────────────────', 'role': None, 'special': False})
    
    # Add active staff
    options.extend([{**s, 'special': False} for s in active_staff])
    
    # Filter out divider from actual selection
    selectable_options = [opt for opt in options if opt['id'] != 'divider']
    
    selected = st.selectbox(
        label,
        options=selectable_options,
        format_func=lambda x: f"{x['name']}" + (f" ({x['role']})" if x['role'] and not x.get('special') else ""),
        key=key
    )
    
    # If TRT or External SSO selected, prompt for name
    if selected and selected.get('special'):
        st.markdown(f"**{selected['name']} selected** - Please enter their name:")
        specific_name = st.text_input(
            f"Enter {selected['role']} Name",
            key=f"{key}_specific_name",
            placeholder=f"Full name of {selected['role']}"
        )
        
        if specific_name and specific_name.strip():
            return {
                'id': selected['id'],
                'name': specific_name.strip(),
                'role': selected['role'],
                'is_special': True
            }
        else:
            # Return with placeholder until name is entered
            return {
                'id': selected['id'],
                'name': f"{selected['role']} (Name Required)",
                'role': selected['role'],
                'is_special': True,
                'name_missing': True
            }
    
    return selected

# --- DIRECT LOG FORM ---

@handle_errors("Unable to load incident form")
def render_direct_log_form():
    """Renders the incident logging form."""
    
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)
    
    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📝 Incident Log: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])
    
    st.markdown("---")
    
    with st.form("incident_form"):
        st.markdown("### Incident Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            incident_date = st.date_input("Date of Incident (DD/MM/YYYY)", value=datetime.now(), format="DD/MM/YYYY")
            incident_time = st.time_input("Time of Incident", value=datetime.now().time())
            location = st.selectbox("Location", options=LOCATIONS)
        
        with col2:
            # Use the staff selector component
            st.markdown("**Reported By**")
            reported_by = render_staff_selector(
                label="Select Staff Member",
                key="incident_staff_selector",
                include_special_options=True
            )
        
        st.markdown("### behaviour Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            behaviour_type = st.selectbox(
                "behaviour Type",
                options=["--- Select behaviour ---"] + behaviourS_FBA
            )
            antecedent = st.selectbox("Antecedent", options=ANTECEDENTS_NEW)
        
        with col4:
            intervention = st.selectbox("Intervention Used", options=INTERVENTIONS)
            support_type = st.selectbox("Support Type", options=SUPPORT_TYPES)
        
        severity_level = st.slider("Severity Level", 1, 5, 2)
        
        description = st.text_area(
            "Additional Description",
            placeholder="Provide additional context about the incident...",
            height=100
        )
        
        submitted = st.form_submit_button("Submit Incident Report", type="primary", use_container_width=True)
        
        if submitted:
            try:
                # Check if special staff needs name
                if reported_by and reported_by.get('name_missing'):
                    st.error("Please enter the name for the selected staff type (TRT or External SSO)")
                    return
                
                # Validate form
                validate_incident_form(
                    location, reported_by, behaviour_type,
                    severity_level, incident_date, incident_time
                )
                
                # Create incident record
                incident_time_obj = datetime.combine(incident_date, incident_time)
                session = get_session_window(incident_time)
                
                new_incident = {
                    'student_id': student_id,
                    'incident_date': incident_date.strftime('%Y-%m-%d'),
                    'incident_time': incident_time.strftime('%H:%M:%S'),
                    'day_of_week': incident_date.strftime('%A'),
                    'session': session,
                    'location': location,
                    'reported_by_name': reported_by['name'],
                    'reported_by_id': reported_by['id'] if not reported_by.get('is_special', False) else None,
                    'reported_by_role': reported_by['role'],
                    'is_special_staff': reported_by.get('is_special', False),
                    'behaviour_type': behaviour_type,
                    'antecedent': antecedent,
                    'intervention': intervention,
                    'support_type': support_type,
                    'severity': severity_level,
                    'description': description,
                    'is_critical': severity_level >= 4
                }
                
                # Save to Supabase
                supabase = get_supabase_client()
                response = supabase.table('incidents').insert(new_incident).execute()
                
                if response.data:
                    # Update session state with the returned record (includes DB-generated ID)
                    saved_incident = response.data[0]
                    # Convert DB field names back to app field names for backward compatibility
                    saved_incident['date'] = saved_incident['incident_date']
                    saved_incident['time'] = saved_incident['incident_time']
                    saved_incident['day'] = saved_incident['day_of_week']
                    st.session_state.incidents.append(saved_incident)
                    
                    st.success("✅ Incident report submitted successfully!")
                    
                    if severity_level >= 4:
                        st.warning("⚠️ This is a critical incident (Severity 4-5). Please complete a Critical Incident ABCH form.")
                else:
                    st.error("Failed to save incident to database")
                    return
                
                # Option to add another or return
                col_another, col_return = st.columns(2)
                with col_another:
                    if st.button("➕ Log Another Incident", use_container_width=True):
                        st.rerun()
                with col_return:
                    if st.button("↩️ Return to Student List", use_container_width=True):
                        navigate_to('program_students', program=student['program'])
                        
            except ValidationError as e:
                st.error(e.user_message)

# --- Placeholder for other render functions ---

def render_critical_incident_abch_form():
    st.title("Critical Incident Form")
    if st.button("⬅ Back"):
        navigate_to('landing')
    st.info("Critical incident ABCH form rendered here")

@handle_errors("Unable to load student analysis")
def render_student_analysis():
    """Renders comprehensive student analysis with data visualizations."""
    
    student_id = st.session_state.get('selected_student_id')
    student = get_student_by_id(student_id)
    
    if not student:
        st.error("Student not found")
        if st.button("Return Home"):
            navigate_to('landing')
        return
    
    # Header
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.title(f"📊 Analysis: {student['name']}")
        st.caption(f"Grade {student['grade']} | {student['program']} Program | EDID: {student.get('edid', 'N/A')}")
    with col_back:
        if st.button("⬅ Back"):
            navigate_to('program_students', program=student['program'])
    
    st.markdown("---")
    
    # Get all incidents for this student
    student_incidents = [inc for inc in st.session_state.incidents if inc.get('student_id') == student_id]
    
    if not student_incidents:
        st.info("No incident data available for this student yet.")
        st.markdown("### Actions")
        if st.button("📝 Log First Incident", type="primary"):
            navigate_to('direct_log_form', student_id=student_id)
        return
    
    # Summary Metrics
    st.markdown("### 📈 Summary Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Incidents", len(student_incidents))
    
    with col2:
        critical_count = len([inc for inc in student_incidents if inc.get('is_critical', False)])
        st.metric("Critical Incidents", critical_count, delta=None if critical_count == 0 else f"{(critical_count/len(student_incidents)*100):.0f}%")
    
    with col3:
        avg_severity = sum([inc.get('severity', 0) for inc in student_incidents]) / len(student_incidents)
        st.metric("Avg Severity", f"{avg_severity:.1f}")
    
    with col4:
        # Get date range
        dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in student_incidents]
        days_span = (max(dates) - min(dates)).days + 1 if len(dates) > 0 else 1
        st.metric("Days Tracked", days_span)
    
    with col5:
        incidents_per_week = (len(student_incidents) / days_span) * 7 if days_span > 0 else 0
        st.metric("Incidents/Week", f"{incidents_per_week:.1f}")
    
    st.markdown("---")
    
    st.info("📊 Full analysis features with charts and recommendations available in complete app")

# --- MAIN ---

def main():
    """Main application logic."""
    
    try:
        # Initialize session state
        initialize_session_state()
        
        # Check if user is logged in
        if not st.session_state.get('logged_in', False):
            render_login_page()
            return
        
        current_page = st.session_state.get('current_page', 'landing')
        
        if current_page == 'login':
            render_login_page()
        elif current_page == 'landing':
            render_landing_page()
        elif current_page == 'program_students':
            render_program_students()
        elif current_page == 'direct_log_form':
            render_direct_log_form()
        elif current_page == 'critical_incident_abch':
            render_critical_incident_abch_form()
        elif current_page == 'student_analysis':
            render_student_analysis()
        elif current_page == 'admin_portal':
            render_admin_portal()
        else:
            st.error("Unknown page")
            navigate_to('landing')
            
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        st.error("A critical error occurred.")

if __name__ == '__main__':
    main()
