import streamlit
import random
import time

streamlit.set_page_config(page_title="PulseGuard AI - 1000 Patient Mega Ward", layout="wide")

# --- 1. Generate 1000 Patients (Runs only once on startup) ---
if "patient_registry" not in streamlit.session_state:
    # First names (36) x Last names (35) = 1,260 possible combinations
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright"]
    
    registry = []
    patient_count = 0
    
    for first in first_names:
        for last in last_names:
            if patient_count >= 1000:
                break
            
            # Assign risk profiles. Mostly stable, but about 15% are high-risk.
            profile_chance = random.random()
            if profile_chance < 0.85:
                profile = "Stable"
            elif profile_chance < 0.90:
                profile = "Hypoxia Risk"
            elif profile_chance < 0.95:
                profile = "Hypertension Risk"
            else:
                profile = "Volatile"
                
            registry.append({
                "id": f"PT-{1001 + patient_count}",
                "name": f"{first} {last}",
                "age": random.randint(18, 95),
                "condition": profile
            })
            patient_count += 1
            
        if patient_count >= 1000:
            break
            
    # Save to session state so names don't change on every refresh
    streamlit.session_state.patient_registry = registry

# --- 2. Triage Logic Engine ---
def calculate_severity(spo2, heart_rate, bp_sys, bp_dia):
    """Evaluates individual vitals and returns the appropriate hex color and label."""
    if spo2 < 90:
        spo2_color, spo2_label = "#dc3545", "CRITICAL"
    elif 90 <= spo2 <= 94:
        spo2_color, spo2_label = "#ffc107", "WARNING"
    else:
        spo2_color, spo2_label = "#28a745", "NORMAL"

    if heart_rate < 50 or heart_rate >= 120:
        hr_color, hr_label = "#dc3545", "CRITICAL"
    elif (50 <= heart_rate <= 59) or (101 <= heart_rate <= 119):
        hr_color, hr_label = "#ffc107", "WARNING"
    else:
        hr_color, hr_label = "#28a745", "NORMAL"

    if bp_sys >= 180 or bp_dia >= 110:
        bp_color, bp_label = "#dc3545", "CRITICAL"
    elif (120 <= bp_sys <= 179) or (80 <= bp_dia <= 109):
        bp_color, bp_label = "#ffc107", "WARNING"
    else:
        bp_color, bp_label = "#28a745", "NORMAL"

    return (spo2_color, spo2_label), (hr_color, hr_label), (bp_color, bp_label)

# --- 3. Simulated Telemetry Engine ---
def generate_patient_vitals(profile):
    """Generates continuous stream payloads based on the patient's underlying risk profile."""
    if profile == "Stable":
        return {"spo2": random.randint(96, 100), "hr": random.randint(60, 85), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile == "Hypoxia Risk":
        return {"spo2": random.randint(85, 93), "hr": random.randint(95, 115), "bp_sys": random.randint(120, 135), "bp_dia": random.randint(80, 90)}
    elif profile == "Hypertension Risk":
        return {"spo2": random.randint(95, 99), "hr": random.randint(80, 105), "bp_sys": random.randint(165, 190), "bp_dia": random.randint(95, 115)}
    else:
        return {"spo2": random.randint(88, 99), "hr": random.randint(45, 130), "bp_sys": random.randint(100, 185), "bp_dia": random.randint(60, 115)}

# --- 4. UI and Dashboard Assembly ---
streamlit.title("PulseGuard AI - 1000 Patient Monitor")
streamlit.write("Real-time visual triage calculating continuous data for 1,000 patients simultaneously.")

# Auto-refreshing block for continuous readings
@streamlit.fragment(run_every=2)
def render_live_ward_table():
    
    html_rows = []
    total_stable = 0
    total_warning = 0
    total_critical = 0

    # 1. Process all 1000 patients in the background
    for patient in streamlit.session_state.patient_registry:
        vitals = generate_patient_vitals(patient["condition"])
        
        spo2_data, hr_data, bp_data = calculate_severity(
            vitals["spo2"], vitals["hr"], vitals["bp_sys"], vitals["bp_dia"]
        )
        
        all_labels = [spo2_data[1], hr_data[1], bp_data[1]]
        if "CRITICAL" in all_labels:
            overall_color, overall_status = "#dc3545", "CRITICAL"
            total_critical += 1
        elif "WARNING" in all_labels:
            overall_color, overall_status = "#ffc107", "WARNING"
            total_warning += 1
        else:
            overall_color, overall_status = "#28a745", "NORMAL"
            total_stable += 1

        spo2_text = "black" if spo2_data[0] == "#ffc107" else "white"
        hr_text = "black" if hr_data[0] == "#ffc107" else "white"
        bp_text = "black" if bp_data[0] == "#ffc107" else "white"
        overall_text = "black" if overall_color == "#ffc107" else "white"

        # Build the HTML row for this patient
        row = (
            f"<tr>"
            f"<td style='padding: 10px; border: 1px solid #555; font-weight: bold;'>{patient['id']}</td>"
            f"<td style='padding: 10px; border: 1px solid #555; font-weight: bold;'>{patient['name']}</td>"
            f"<td style='padding: 10px; border: 1px solid #555;'>{patient['age']}</td>"
            f"<td style='padding: 10px; border: 1px solid #555; background-color: {spo2_data[0]}; color: {spo2_text}; font-weight: bold;'>{vitals['spo2']}%</td>"
            f"<td style='padding: 10px; border: 1px solid #555; background-color: {hr_data[0]}; color: {hr_text}; font-weight: bold;'>{vitals['hr']}</td>"
            f"<td style='padding: 10px; border: 1px solid #555; background-color: {bp_data[0]}; color: {bp_text}; font-weight: bold;'>{vitals['bp_sys']}/{vitals['bp_dia']}</td>"
            f"<td style='padding: 10px; border: 1px solid #555; background-color: {overall_color}; color: {overall_text}; font-weight: bold;'>{overall_status}</td>"
            f"</tr>"
        )
        html_rows.append(row)

    # 2. Render Live Summary Metrics above the table
    col1, col2, col3 = streamlit.columns(3)
    with col1:
        streamlit.metric("🟢 STABLE PATIENTS", total_stable)
    with col2:
        streamlit.metric("🟡 WARNING STATUS", total_warning)
    with col3:
        streamlit.metric("🔴 CRITICAL EMERGENCIES", total_critical)

    # 3. Assemble the scrollable table
    table_header = """
    <div style="max-height: 600px; overflow-y: auto; border: 2px solid #555; border-radius: 5px;">
        <table style="width: 100%; text-align: center; border-collapse: collapse; font-family: sans-serif;">
            <thead style="position: sticky; top: 0; background-color: #222; color: white; z-index: 1;">
                <tr>
                    <th style="padding: 12px; border: 1px solid #555;">ID</th>
                    <th style="padding: 12px; border: 1px solid #555;">Patient Name</th>
                    <th style="padding: 12px; border: 1px solid #555;">Age</th>
                    <th style="padding: 12px; border: 1px solid #555;">SpO2 (%)</th>
                    <th style="padding: 12px; border: 1px solid #555;">Heart Rate (BPM)</th>
                    <th style="padding: 12px; border: 1px solid #555;">Blood Pressure (mmHg)</th>
                    <th style="padding: 12px; border: 1px solid #555;">Triage Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    table_footer = """
            </tbody>
        </table>
    </div>
    """

    # Inject the HTML (using .join is much faster for 1000 rows than adding strings one by one)
    complete_html = table_header + "".join(html_rows) + table_footer
    streamlit.markdown(complete_html, unsafe_allow_html=True)
    streamlit.caption(f"1,000 Data Streams Synchronized at: {time.strftime('%H:%M:%S')}")

# Execute
render_live_ward_table()
