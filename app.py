import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import random
import uuid # Use uuid for robust unique IDs
import plotly.express as px
import numpy as np

# --- Configuration and Aesthetics (High-Contrast Dark Look) ---

st.set_page_config(
    page_title="Behaviour Support & Data Analysis Tool",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a sleek, high-contrast, dark-mode inspired UI
# Corrected #F1F5N9 to #F1F5F9 for valid hex color
st.markdown(
    """
    <style>
    /* High-Contrast Dark Theme for Accessibility and Modern Look */
    
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    h1, h2, h3, .stMarkdown, .st-emotion-cache-1jm69h1 { color: #F1F5F9 !important; }
    
    /* Widget Backgrounds */
    .stForm, .stContainer, .stAlert, .stSelectbox, .stTextInput, .stTextArea,
    .st-emotion-cache-6qob1p { background-color: #1E293B; border-radius: 12px; color: #F1F5F9; }
    
    /* Input Fields */
    div[data-testid="stTextInput"] > div > input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child,
    div[data-testid="stTextArea"] textarea {
        background-color: #334155;
        border: 1px solid #475569;
        color: #F1F5F9;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        transition: background-color 0.2s, transform 0.1s;
    }
    
    /* Primary Button Customization */
    .stButton > button[kind="primary"] {
        background-color: #2563EB; /* Blue-700 */
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #3B82F6; /* Blue-500 */
        transform: translateY(-1px);
    }
    
    /* Secondary Button Customization */
    .stButton > button[kind="secondary"] {
        background-color: #334155; /* Slate-700 */
        color: #94A3B8; /* Slate-400 */
        border: 1px solid #475569;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #475569; /* Slate-600 */
        color: #F1F5F9;
        transform: translateY(-1px);
    }

    /* Metric Boxes (Card styling) */
    [data-testid="stMetricValue"] {
        font-size: 2.0rem; /* Large value */
        color: #3B82F6;
    }

    .student-card {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 10px;
        cursor: pointer;
        transition: border-color 0.2s, background-color 0.2s;
    }
    .student-card:hover {
        border-color: #2563EB;
        background-color: #15202E;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


# --- Initial Data & Mocks ---

STUDENTS = [
    {'id': 'S001', 'name': 'Alex Johnson', 'year': 9, 'gender': 'M', 'grade_level': 'MY'},
    {'id': 'S002', 'name': 'Maya Patel', 'year': 11, 'gender': 'F', 'grade_level': 'SY'},
    {'id': 'S003', 'name': 'Ethan Chan', 'year': 7, 'gender': 'M', 'grade_level': 'PY'},
    {'id': 'S004', 'name': 'Chloe Davis', 'year': 12, 'gender': 'F', 'grade_level': 'SY'},
    {'id': 'S005', 'name': 'Liam Smith', 'year': 8, 'gender': 'M', 'grade_level': 'MY'},
]

INCIDENT_TYPES = ['Physical Aggression', 'Verbal Disruption', 'Refusal to Work', 'Out of Area', 'Tech Misuse']
ABC_CATEGORIES = {
    'A': ['Peer Conflict', 'Task Difficulty', 'Attention Seeking', 'Change in Schedule'],
    'B': ['Yelling', 'Hitting', 'Withdrawing', 'Running away', 'Ignoring Instruction'],
    'C': ['Sent to office', 'Restorative conversation', 'Parent contact', 'Time-out', 'Loss of privilege']
}
STAFF_ROLES = ['PY', 'MY', 'SY', 'ADM']

# Function to generate realistic dummy incidents
def generate_incidents():
    incidents = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    for i in range(250):
        student = random.choice(STUDENTS)
        date_time = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(8, 16), minutes=random.randint(0, 59))
        
        antecedent = random.choice(ABC_CATEGORIES['A'])
        behavior = random.choice(ABC_CATEGORIES['B'])
        consequence = random.choice(ABC_CATEGORIES['C'])
        
        incidents.append({
            'id': str(uuid.uuid4()),
            'student_id': student['id'],
            'date_time': date_time,
            'type': random.choice(INCIDENT_TYPES),
            'staff_reporter': f"Staff {random.choice(STAFF_ROLES)}",
            'location': random.choice(['Classroom', 'Yard', 'Library', 'Canteen', 'Hallway']),
            'antecedent': antecedent,
            'behavior': behavior,
            'consequence': consequence,
            'description': f"Brief log of {behavior.lower()} following {antecedent.lower()}.",
            'follow_up_needed': random.choice([True, False, False]),
        })
    return pd.DataFrame(incidents)


# --- State and Data Management Functions ---

def initialize_state():
    if 'data' not in st.session_state:
        st.session_state.data = generate_incidents()
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'student' not in st.session_state:
        st.session_state.student = None

def navigate_to(page, role=None, student=None):
    st.session_state.page = page
    if role:
        st.session_state.role = role
    if student:
        st.session_state.student = student
    st.rerun()

@st.cache_data
def get_student_by_id(student_id):
    return next((s for s in STUDENTS if s['id'] == student_id), None)

def get_incidents_by_student(student_id):
    return st.session_state.data[st.session_state.data['student_id'] == student_id]

def get_all_incidents():
    return st.session_state.data

def log_incident(student_id, data):
    new_incident = {
        'id': str(uuid.uuid4()),
        'student_id': student_id,
        'date_time': datetime.combine(data['date'], data['time']),
        'type': data['type'],
        'staff_reporter': data['reporter'],
        'location': data['location'],
        'antecedent': data['antecedent'],
        'behavior': data['behavior'],
        'consequence': data['consequence'],
        'description': data['description'],
        'follow_up_needed': data['follow_up'],
    }
    
    # Append the new incident to the DataFrame
    new_df = pd.DataFrame([new_incident])
    st.session_state.data = pd.concat([st.session_state.data, new_df], ignore_index=True)


# --- Component Functions ---

def staff_header(title):
    """Renders a consistent header with logo/title and back button."""
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(f"🛠️ {title}")
    with col2:
        if st.session_state.page != 'landing' and st.button("🚪 Logout/Change Role", key="logout_btn", use_container_width=True):
            navigate_to('landing')

def render_incident_log_form(student):
    """Renders the detailed ABC incident logging form."""
    
    st.subheader(f"Logging Incident for: {student['name']} (Year {student['year']})")

    with st.form(key='incident_log_form', clear_on_submit=True):
        st.markdown("**Incident Details**")
        
        col_date, col_time = st.columns(2)
        with col_date:
            log_date = st.date_input("Date", datetime.now().date())
        with col_time:
            log_time = st.time_input("Time", datetime.now().time().replace(second=0, microsecond=0))

        col_type, col_loc = st.columns(2)
        with col_type:
            incident_type = st.selectbox("Incident Type", INCIDENT_TYPES)
        with col_loc:
            location = st.text_input("Location/Classroom", "Classroom D12")
        
        staff_reporter = st.text_input("Your Name/ID", st.session_state.role)

        st.markdown("---")
        st.markdown("**ABCs (Antecedent, Behavior, Consequence)**")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            antecedent = st.selectbox("A - Antecedent (What happened right before?)", ABC_CATEGORIES['A'])
        with col_b:
            behavior = st.selectbox("B - Behavior (What did the student do?)", ABC_CATEGORIES['B'])
        with col_c:
            consequence = st.selectbox("C - Consequence (What happened immediately after?)", ABC_CATEGORIES['C'])

        st.markdown("---")
        
        description = st.text_area("Full Description/Notes", 
                                    placeholder="Describe the incident, including context and any verbal exchanges.")
        
        follow_up = st.checkbox("Follow-up required (e.g., Admin, Parental Contact)", value=False)

        submitted = st.form_submit_button("Submit Incident Log", type="primary", use_container_width=True)

        if submitted:
            log_data = {
                'date': log_date,
                'time': log_time,
                'type': incident_type,
                'location': location,
                'reporter': staff_reporter,
                'antecedent': antecedent,
                'behavior': behavior,
                'consequence': consequence,
                'description': description,
                'follow_up': follow_up,
            }
            log_incident(student['id'], log_data)
            st.success(f"Incident logged successfully for {student['name']}!")
            # Navigate back to the student list after a successful log
            navigate_to('staff_area', role=st.session_state.role)


def render_student_analysis(student, role):
    """Renders the detailed data analysis view for a selected student."""
    
    # 1. Header and Navigation
    staff_header(f"Data Analysis: {student['name']}")

    # 2. Key Metrics
    incidents = get_incidents_by_student(student['id'])
    num_incidents = len(incidents)
    
    st.markdown(f"**Student ID:** `{student['id']}` | **Year:** `{student['year']}` | **Grade Level:** `{student['grade_level']}`")
    
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(label="Total Incidents Logged", value=num_incidents)
    
    if num_incidents > 0:
        # Calculate recent incidents (last 30 days)
        last_30_days = datetime.now() - timedelta(days=30)
        recent_incidents = incidents[incidents['date_time'] >= last_30_days]
        with col_b:
            st.metric(label="Incidents (Last 30 Days)", value=len(recent_incidents), delta=f"{num_incidents - len(recent_incidents)} previous")

        # Most frequent type
        most_frequent_type = incidents['type'].mode().iloc[0]
        with col_c:
            st.metric(label="Most Frequent Incident", value=most_frequent_type)

        st.markdown("---")

        # 3. Data Visualization (updated to include Location and Reporter charts)
        st.subheader("Visual Summary")
        
        # Row 1: Time of Day and ABC Breakdown
        chart1, chart2 = st.columns(2)
        
        # Chart 1: Incidents by Time of Day
        with chart1:
            st.markdown("#### Incidents by Time of Day")
            incidents['hour'] = incidents['date_time'].dt.hour
            hour_counts = incidents['hour'].value_counts().sort_index().reindex(range(8, 17), fill_value=0).reset_index()
            hour_counts.columns = ['Hour', 'Count']
            
            fig_time = px.bar(
                hour_counts, 
                x='Hour', 
                y='Count', 
                title='Incident Frequency by Hour of Day (8am - 4pm)',
                color_discrete_sequence=['#3B82F6']
            )
            fig_time.update_layout(xaxis_tickmode='linear', xaxis_dtick=1, xaxis_title='Hour', yaxis_title='Count', template="plotly_dark")
            st.plotly_chart(fig_time, use_container_width=True)

        # Chart 2: ABC Category Breakdown
        with chart2:
            st.markdown("#### ABC Breakdown")
            abc_df = incidents[['antecedent', 'behavior', 'consequence']].melt(var_name='Category', value_name='Detail')
            
            fig_abc = px.sunburst(
                abc_df,
                path=['Category', 'Detail'],
                color='Category',
                color_discrete_map={'antecedent':'#F59E0B', 'behavior':'#EF4444', 'consequence':'#10B981'},
                title='Antecedent, Behavior, Consequence Distribution'
            )
            fig_abc.update_layout(margin=dict(t=30, l=0, r=0, b=0), template="plotly_dark")
            st.plotly_chart(fig_abc, use_container_width=True)
            
        st.markdown("---")
        
        # Row 2: Location and Staff Reporter Breakdown (NEW CHARTS)
        chart3, chart4 = st.columns(2)

        # Chart 3 (NEW): Incidents by Location
        with chart3:
            st.markdown("#### Incidents by Location Hotspot")
            fig_location = px.pie(
                incidents, 
                names='location', 
                title='Distribution by Location',
                color_discrete_sequence=px.colors.sequential.Electric
            )
            fig_location.update_layout(template="plotly_dark", showlegend=True, margin=dict(t=30, l=0, r=0, b=0))
            fig_location.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_location, use_container_width=True)
            
        # Chart 4 (NEW): Incidents by Staff Reporter
        with chart4:
            st.markdown("#### Incidents by Reporting Staff")
            fig_reporter = px.bar(
                incidents['staff_reporter'].value_counts().reset_index(),
                x='index',
                y='staff_reporter',
                title='Incidents Reported by Staff Member',
                labels={'index': 'Staff Reporter', 'staff_reporter': 'Incident Count'},
                color='index',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_reporter.update_layout(template="plotly_dark", xaxis={'categoryorder': 'total descending'})
            st.plotly_chart(fig_reporter, use_container_width=True)


        st.markdown("---")

        # 4. Detailed Incident Table 
        st.subheader("Detailed Incident Log")
        
        display_df = incidents[['date_time', 'type', 'location', 'antecedent', 'behavior', 'consequence', 'staff_reporter', 'follow_up_needed', 'description']].copy()
        display_df.rename(columns={'date_time': 'Date/Time', 'type': 'Type', 'location': 'Location', 'staff_reporter': 'Reporter', 'follow_up_needed': 'Follow-Up?'}, inplace=True)
        
        st.dataframe(
            display_df, 
            use_container_width=True,
            # Enable column sorting and searching
            hide_index=True,
            column_config={
                "Date/Time": st.column_config.DatetimeColumn(
                    "Date/Time",
                    format="YYYY-MM-DD HH:mm:ss",
                    step=60,
                ),
                "description": st.column_config.TextColumn("Description", help="Full details of the incident", width="large"),
                "Follow-Up?": st.column_config.CheckboxColumn("Follow-Up?", default=False),
            }
        )

    # 5. Navigation
    st.markdown("---")
    if st.button("⬅ Back to Student List", key="back_from_analysis", type="secondary"):
        navigate_to('staff_area', role=role)
    
    # Optional: Direct log button for this student (for Admin/Head of House)
    if role in ['ADM', 'SY', 'MY', 'PY']:
        if st.button(f"➕ Log New Incident for {student['name']}", key="direct_log_btn", type="primary"):
            navigate_to('quick_log', student=student)


def render_staff_area_home(role):
    """Renders the main dashboard for staff to select a student."""
    
    staff_header(f"Staff Dashboard ({role})")
    
    # Calculate overall metrics
    all_incidents = get_all_incidents()
    
    if all_incidents.empty:
        st.warning("No incidents have been logged yet.")
        student_data = pd.DataFrame(STUDENTS)
    else:
        # Filter students based on role/grade level if needed (optional logic, showing all for now)
        if role != 'ADM':
            filtered_students = [s for s in STUDENTS if s['grade_level'] == role]
        else:
            filtered_students = STUDENTS

        # Convert to DataFrame for easier analysis
        student_data = pd.DataFrame(filtered_students)
        
        # Calculate incident count per student
        incident_counts = all_incidents.groupby('student_id').size().reset_index(name='Incident Count')
        student_data = student_data.merge(incident_counts, left_on='id', right_on='student_id', how='left').fillna(0)
        student_data['Incident Count'] = student_data['Incident Count'].astype(int)
        
        # Sort students by incident count
        student_data = student_data.sort_values(by='Incident Count', ascending=False)
        
        # --- 1. Summary Statistics ---
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Incidents Logged", len(all_incidents))
        with col_m2:
            st.metric("Unique Students Logged", all_incidents['student_id'].nunique())
        with col_m3:
            st.metric("Students in View", len(student_data))

    st.markdown("---")
    st.subheader("Student Quick View")
    
    # Student Search/Filter
    search_query = st.text_input("Search by Name or ID", key="student_search", placeholder="e.g., Alex or S001")
    
    if not student_data.empty:
        if search_query:
            student_data = student_data[
                student_data['name'].str.contains(search_query, case=False) |
                student_data['id'].str.contains(search_query, case=False)
            ]
            
        # --- 2. Refined Student Card Display ---
        # Display students in columns
        students_per_row = 3
        rows = int(np.ceil(len(student_data) / students_per_row))
        
        for i in range(rows):
            cols = st.columns(students_per_row)
            for j in range(students_per_row):
                index = i * students_per_row + j
                if index < len(student_data):
                    student_row = student_data.iloc[index]
                    student_obj = get_student_by_id(student_row['id'])
                    
                    with cols[j]:
                        # Create an interactive card using st.markdown and an embedded button
                        with st.container():
                            # Use a unique key for the button within the card
                            key = f"select_student_{student_row['id']}"
                            
                            # Custom styling for the card content (using markdown)
                            st.markdown(
                                f"""
                                <div class="student-card">
                                    <h3 style='margin-bottom: 0.2rem;'>{student_row['name']}</h3>
                                    <p style='margin-top: 0; color: #94A3B8;'>ID: {student_row['id']} | Year: {student_row['year']}</p>
                                    <p style='font-size: 1.1em; font-weight: bold; color: #3B82F6;'>
                                        Incidents: {student_row['Incident Count']}
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Streamlit doesn't allow a button *inside* a custom markdown container 
                            # to trigger an action easily, so we use the button right below it 
                            # for functional clarity.
                            if st.button("View Analysis / Log", key=key, use_container_width=True):
                                navigate_to('student_detail', student=student_obj)
    else:
        st.info("No students match your current filter or role selection.")
    

# --- Page Rendering Functions (The "Router" Destination) ---

def render_landing_page():
    """The initial landing page for role selection and quick access."""
    st.title("Welcome to the Student Support Data Tool")
    st.subheader("Select your Staff Role to continue:")
    
    col_py, col_my, col_sy, col_adm = st.columns(4)
    
    # Primary Years (PY)
    with col_py:
        if st.button("Primary Years (PY)", key="role_py", type="primary", use_container_width=True):
            navigate_to('staff_area', role='PY')
            
    # Middle Years (MY)
    with col_my:
        if st.button("Middle Years (MY)", key="role_my", type="primary", use_container_width=True):
            navigate_to('staff_area', role='MY')
            
    # Senior Years (SY)
    with col_sy:
        if st.button("Senior Years (SY)", key="role_sy", type="primary", use_container_width=True):
            navigate_to('staff_area', role='SY')
            
    # Admin (ADM)
    with col_adm:
        if st.button("Admin (ADM)", key="role_adm", type="secondary", use_container_width=True):
            navigate_to('staff_area', role='ADM')
            
    st.markdown("---")
    st.info("This application uses a detailed ABCH Quick Log for context-rich data collection, feeding directly into data-driven student analysis.")


def render_quick_log(role, student):
    """Page to render the log form after selecting a student from the dashboard."""
    staff_header("Incident Quick Log")
    render_incident_log_form(student)
    
    if st.button("⬅ Cancel and Return to List", key="back_from_log", type="secondary"):
        navigate_to('staff_area', role=role)


# --- Main Application Loop ---

def main():
    """Controls the main application flow based on session state."""
    
    # 1. Initialize data and state
    initialize_state()

    current_role = st.session_state.get('role')
    current_student = st.session_state.get('student')

    # 2. Page Routing Logic
    if st.session_state.page == 'landing':
        render_landing_page()

    elif st.session_state.page == 'quick_log':
        if current_student and current_role:
             render_quick_log(current_role, current_student) 
        else:
            st.error("Missing context. Returning to dashboard.")
            navigate_to('staff_area', role=current_role)


    elif st.session_state.page == 'student_detail':
        if current_student and current_role:
            render_student_analysis(current_student, current_role)
        else:
            st.error("Student context missing. Please select a student.")
            navigate_to('staff_area', role=current_role)

    elif st.session_state.page == 'staff_area':
        if current_role:
            render_staff_area_home(current_role)
        else:
            st.error("Role missing. Returning to landing page.")
            navigate_to('landing')

if __name__ == "__main__":
    main()
