import streamlit as st
from datetime import datetime
import uuid

# --- FBA and Data Constants ---
FUNCTION_OPTIONS = [
    'Escape/Avoidance (Task/Demand)',
    'Attention (Peer/Staff)',
    'Tangible (Access to item/activity)',
    'Sensory/Automatic (Internal feeling)',
    'Unknown/Other'
]

# Mock data for location generation (as requested)
MOCK_LOCATIONS = [
    "Classroom 3A", "Playground (Oval)", "Library", "School Office", "Hallway (East Wing)"
]

# --- Session State Initialization ---
if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []
    # Initialize with one empty step
    st.session_state.abch_chronology.append({
        'id': str(uuid.uuid4()),
        'location': MOCK_LOCATIONS[0], # Auto-generated initial location
        'context': '',
        'time': datetime.now().strftime("%H:%M"), # Auto-generated initial time
        'behavior': '',
        'consequence': '',
        'function': FUNCTION_OPTIONS[0] # Default best guess
    })

# --- Helper Functions ---

def generate_default_function(step_data):
    """
    Mock function to autogenerate the 'best guess' function based on simple heuristics.
    In a real app, this would use machine learning or more complex logic.
    For this example, it defaults based on the consequence.
    """
    consequence_text = step_data.get('consequence', '').lower()
    
    if 'removed from' in consequence_text or 'break' in consequence_text or 'task stopped' in consequence_text:
        return 'Escape/Avoidance (Task/Demand)'
    if 'staff attention' in consequence_text or 'comforted' in consequence_text:
        return 'Attention (Peer/Staff)'
    if 'given' in consequence_text or 'access to' in consequence_text:
        return 'Tangible (Access to item/activity)'
    
    return 'Unknown/Other'

def add_new_behavior_layer():
    """Adds a new blank step to the chronology, carrying over the location and time."""
    last_step = st.session_state.abch_chronology[-1]
    
    # Auto-populate the next step with the last step's time and location
    # Real-world apps might add a few minutes to the time.
    new_time = last_step['time'] 
    new_location = last_step['location']
    
    st.session_state.abch_chronology.append({
        'id': str(uuid.uuid4()),
        'location': new_location,
        'context': '',
        'time': new_time,
        'behavior': '',
        'consequence': '',
        'function': FUNCTION_OPTIONS[0]
    })

def update_step_data(step_id, key, value):
    """Updates a specific field for a specific step in the chronology."""
    for step in st.session_state.abch_chronology:
        if step['id'] == step_id:
            step[key] = value
            # Re-run autogeneration if needed (e.g., if consequence changes)
            if key == 'consequence':
                step['function'] = generate_default_function(step)
            break

def render_chronology_step(step, step_index):
    """Renders a single row of the Chronology table."""
    step_id = step['id']
    
    # 6 columns for the data entry
    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2, 1.2, 3, 3, 2])
    
    # --- ANTECEDENT (TRIGGER) ---
    with col1:
        # Location (Auto-generated/Editable)
        new_loc = st.selectbox(
            f"Location",
            options=MOCK_LOCATIONS,
            index=MOCK_LOCATIONS.index(step['location']),
            key=f"loc_{step_id}",
            on_change=update_step_data, args=(step_id, 'location', st.session_state[f"loc_{step_id}"])
        )
    with col2:
        # Context (Narrative)
        st.text_area(
            "Context (What was happening immediately before?)",
            value=step['context'],
            key=f"context_{step_id}",
            height=60,
            on_change=update_step_data, args=(step_id, 'context', st.session_state[f"context_{step_id}"])
        )
        
    # --- BEHAVIOUR ---
    with col3:
        # Time (Auto-generated/Editable)
        st.text_input(
            "Time (HH:MM)",
            value=step['time'],
            key=f"time_{step_id}",
            on_change=update_step_data, args=(step_id, 'time', st.session_state[f"time_{step_id}"])
        )
    with col4:
        # What did the student do? (Behavior Narrative)
        st.text_area(
            "What did the student do? (Observable actions)",
            value=step['behavior'],
            key=f"behavior_{step_id}",
            height=60,
            on_change=update_step_data, args=(step_id, 'behavior', st.session_state[f"behavior_{step_id}"])
        )

    # --- CONSEQUENCE ---
    with col5:
        # What happened after the behaviour? How did people react?
        st.text_area(
            "What happened after? (Staff/Peer reaction)",
            value=step['consequence'],
            key=f"consequence_{step_id}",
            height=60,
            on_change=update_step_data, args=(step_id, 'consequence', st.session_state[f"consequence_{step_id}"])
        )
        
    # --- HYPOTHESIS ---
    with col6:
        # Best guess behaviour function (Autogenerated/Selectable)
        current_function = generate_default_function(step) # Re-calculate the default function
        st.selectbox(
            "Best Guess Function",
            options=FUNCTION_OPTIONS,
            index=FUNCTION_OPTIONS.index(current_function) if current_function in FUNCTION_OPTIONS else 0,
            key=f"function_{step_id}",
            help="This is an auto-generated suggestion, please review and amend.",
            on_change=update_step_data, args=(step_id, 'function', st.session_state[f"function_{step_id}"])
        )

    # Add a horizontal separator between steps
    st.markdown("---")
    
def render_critical_incident_form():
    """Renders the main Critical Incident Form, including chronology and outcomes."""
    
    st.title("Critical Incident Form (A \u2192 B \u2192 C \u2192 H)")
    st.markdown("---")
    
    st.header("Chronology of Events")
    
    # Render Overarching Headers
    header_cols = st.columns([3.5, 4.2, 3]) # Total width ratio matches the 6 data columns below
    with header_cols[0]:
        st.subheader(":blue[Antecedent (Trigger)]")
    with header_cols[1]:
        st.subheader(":blue[Behaviour]")
    with header_cols[2]:
        st.subheader(":blue[Consequence & Hypothesis]")


    # Render the sub-headers (column titles)
    col_h1, col_h2, col_h3, col_h4, col_h5, col_h6 = st.columns([1.5, 2, 1.2, 3, 3, 2])
    col_h1.caption("**Location**")
    col_h2.caption("**Context**")
    col_h3.caption("**Time**")
    col_h4.caption("**What did the student do?**")
    col_h5.caption("**What happened after?**")
    col_h6.caption("**Function**")
    
    st.markdown("---")
    
    # Render all chronological steps
    for i, step in enumerate(st.session_state.abch_chronology):
        st.markdown(f"#### Incident Layer {i + 1}")
        render_chronology_step(step, i)

    # Option to add another layer of behaviour
    st.button("➕ Add Another Layer of Behaviour", on_click=add_new_behavior_layer)
    
    st.markdown("---")
    
    # --- Outcomes and Review Section (Placeholder) ---
    st.header("Outcomes and Review")
    
    st.markdown("""
        * **Outcomes:** Document the immediate and follow-up actions taken.
        * **Review:** Reflective summary of the incident and suggested next steps for support planning.
    """)
    
    st.selectbox("Immediate Outcome", options=["Send Home", "Removal to Safe Space", "Restorative Conversation", "Other"])
    st.text_area("Detailed Review Summary", "Based on the A-B-C-H analysis, the primary function of the behavior appears to be...")
    
    st.button("💾 Finalize and Save Incident Log", type="primary")

# --- Main App Execution ---
# Note: For a single-file Streamlit component, we call the function directly.
render_critical_incident_form()
