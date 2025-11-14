# Assuming this code is inserted within def render_incident_log_form(student):

# --- ABCH CHRONOLOGY SECTION START ---

if 'abch_chronology' not in st.session_state:
    st.session_state.abch_chronology = []

st.markdown("### 2. Critical Incident Chronology (A-B-C-H)")
st.markdown("""
    **Log the sequence of events chronologically.**
    Each entry details the time and the Antecedent (A), Behavior (B), or Consequence (C) that occurred.
""")

col_add, col_sort_label = st.columns([1, 4])
with col_add:
    # Button to add a new event entry
    if st.button("➕ Add Entry", key="add_chronology_entry", type="primary"):
        # Add a new entry with a unique ID and current time default
        st.session_state.abch_chronology.append({
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().strftime("%H:%M"),
            'type': 'Antecedent',
            'detail': '',
            'staff_response': '',
            'staff_id': None
        })

# Reverse the list for display so the latest entry is at the top,
# but keep the internal list chronological for sorting before saving.
chronology_display = sorted(st.session_state.abch_chronology, key=lambda x: x['timestamp'], reverse=True)

if not chronology_display:
    st.info("No chronology entries added yet. Use 'Add Entry' to start logging the sequence.")

# Retrieve all staff names for the selectbox (using MOCK_STAFF assumed to be in scope)
all_staff_names = [s['name'] for s in MOCK_STAFF] 

# Loop through entries for editing
for i, entry in enumerate(chronology_display):
    # Find the original index in the session state list to safely update/delete
    original_index = next((j for j, item in enumerate(st.session_state.abch_chronology) if item['id'] == entry['id']), -1)

    if original_index == -1:
        continue 

    st.markdown(f"#### Event Log Entry {len(st.session_state.abch_chronology) - original_index}")
    
    # Use a unique key based on the original index/ID to allow editing and deletion
    key_prefix = f"abch_{original_index}_{entry['id'][:4]}"
    
    col_time, col_type, col_staff, col_delete = st.columns([2, 3, 4, 1])

    # Time Input (HH:MM)
    with col_time:
        current_time_str = st.text_input(
            "Time (HH:MM)", 
            value=st.session_state.abch_chronology[original_index]['timestamp'], 
            key=f"{key_prefix}_time",
            max_chars=5,
            help="E.g., 11:15"
        )
        st.session_state.abch_chronology[original_index]['timestamp'] = current_time_str

    # Type of Event (A, B, or C)
    with col_type:
        type_options = ['Antecedent', 'Behaviour', 'Consequence', 'Staff Intervention']
        current_type = st.session_state.abch_chronology[original_index]['type']
        new_type = st.selectbox(
            "Event Type",
            options=type_options,
            index=type_options.index(current_type) if current_type in type_options else 0,
            key=f"{key_prefix}_type"
        )
        st.session_state.abch_chronology[original_index]['type'] = new_type

    # Staff Involved in this specific step
    with col_staff:
        current_staff_id = st.session_state.abch_chronology[original_index]['staff_id']
        current_staff_name = next((s['name'] for s in MOCK_STAFF if s['id'] == current_staff_id), None)
        
        staff_index = all_staff_names.index(current_staff_name) if current_staff_name in all_staff_names else 0
        selected_staff_name = st.selectbox(
            "Staff Involved",
            options=all_staff_names,
            index=staff_index,
            key=f"{key_prefix}_staff"
        )
        # Map the selected name back to the ID for storage
        selected_staff_id = next((s['id'] for s in MOCK_STAFF if s['name'] == selected_staff_name), None)
        st.session_state.abch_chronology[original_index]['staff_id'] = selected_staff_id

    # Delete Button
    with col_delete:
        st.write(" ") # Spacer
        if st.button("🗑️", key=f"{key_prefix}_delete", help="Delete this entry"):
            st.session_state.abch_chronology.pop(original_index)
            st.rerun() # Rerun to update the display

    # Detail Text Area
    detail_key = f"{key_prefix}_detail"
    current_detail = st.session_state.abch_chronology[original_index]['detail']
    st.session_state.abch_chronology[original_index]['detail'] = st.text_area(
        f"Description of the {new_type}", 
        value=current_detail, 
        key=detail_key, 
        height=70
    )
    
    # Staff Response Text Area (if applicable)
    if new_type in ['Consequence', 'Staff Intervention']:
         response_key = f"{key_prefix}_response"
         current_response = st.session_state.abch_chronology[original_index]['staff_response']
         st.session_state.abch_chronology[original_index]['staff_response'] = st.text_area(
            "Staff Action/Response", 
            value=current_response, 
            key=response_key, 
            height=50
        )

    st.divider() # Visual separator between entries

# Final chronological sort before the form completes
st.session_state.abch_chronology = sorted(
    st.session_state.abch_chronology, 
    key=lambda x: datetime.strptime(x['timestamp'], "%H:%M") if len(x['timestamp']) == 5 else datetime.min
)
# --- ABCH CHRONOLOGY SECTION END ---
