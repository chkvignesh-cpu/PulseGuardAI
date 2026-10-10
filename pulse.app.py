import streamlit
import random
import time

streamlit.set_page_config(page_title="PulseGuard AI - Ward Overview", layout="wide")

# --- 1. Patient Database & Triage Logic ---
PATIENT_REGISTRY = [
    {"name": "James Holden", "age": 42, "condition": "Stable"},
    {"name": "Naomi Nagata", "age": 36, "condition": "Stable"},
    {"name": "Amos Burton", "age": 45, "condition": "Hypertension Risk"},
    {"name": "Alex Kamal", "age": 52, "condition": "Hypoxia Risk"},
    {"name": "Chrisjen Avasarala", "age": 70, "condition": "Volatile"}
]

def calculate_severity(spo2, heart_rate, bp_sys, bp_dia):
    """Evaluates individual vitals and returns the appropriate hex color and label."""
    # SpO2 Logic
    if spo2 < 90:
        spo2_color, spo2_label = "#dc3545", "CRITICAL"  # Red
    elif 90 <= spo2 <= 94:
        spo2_color, spo2_label = "#ffc107", "WARNING"   # Yellow
    else:
        spo2_color, spo2_label = "#28a745", "NORMAL"    # Green

    # Heart Rate Logic
    if heart_rate < 50 or heart_rate >= 120:
        hr_color, hr_label = "#dc3545", "CRITICAL"
    elif (50 <= heart_rate <= 59) or (101 <= heart_rate <= 119):
        hr_color, hr_label = "#ffc107", "WARNING"
    else:
        hr_color, hr_label = "#28a745", "NORMAL"

    # Blood Pressure Logic
    if bp_sys >= 180 or bp_dia >= 110:
        bp_color, bp_label = "#dc3545", "CRITICAL"
    elif (120 <= bp_sys <= 179) or (80 <= bp_dia <= 109):
        bp_color, bp_label = "#ffc107", "WARNING"
    else:
        bp_color, bp_label = "#28a745", "NORMAL"

    return (spo2_color, spo2_label), (hr_color, hr_label), (bp_color, bp_label)

# --- 2. Simulated Telemetry Engine ---
def generate_patient_vitals(profile):
    """Generates continuous stream payloads based on the patient's underlying risk profile."""
    if profile == "Stable":
        return {"spo2": random.randint(96, 100), "hr": random.randint(60, 85), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile == "Hypoxia Risk":
        return {"spo2": random.randint(85, 93), "hr": random.randint(95, 115), "bp_sys": random.randint(120, 135), "bp_dia": random.randint(80, 90)}
    elif profile == "Hypertension Risk":
        return {"spo2": random.randint(95, 99), "hr": random.randint(80, 105), "bp_sys": random.randint(165, 190), "bp_dia": random.randint(95, 115)}
    else:  # Volatile / Random
        return {"spo2": random.randint(88, 99), "hr": random.randint(45, 130), "bp_sys": random.randint(100, 185), "bp_dia": random.randint(60, 115)}

# --- 3. UI and Dashboard Assembly ---
streamlit.title("PulseGuard AI - Multi-Patient Ward")
streamlit.write("Continuous visual triage for multiple patients. Values and colors update automatically.")

# Fragment reruns the table every 2 seconds to simulate live patient data
@streamlit.fragment(run_every=2)
def render_live_ward_table():
    
    # Start HTML table definition (using safe HTML structure)
    html_table = "<table style='width: 100%; text-align: center; border-collapse: collapse; font-family: sans-serif;'>"
    html_table += "<tr style='background-color: #333; color: white;'>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>Patient Name</th>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>Age</th>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>SpO2 (%)</th>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>Heart Rate (BPM)</th>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>Blood Pressure (mmHg)</th>"
    html_table += "<th style='padding: 12px; border: 1px solid #555;'>Triage Status</th>"
    html_table += "</tr>"

    for patient in PATIENT_REGISTRY:
        vitals = generate_patient_vitals(patient["condition"])
        
        # Calculate severity colors
        spo2_data, hr_data, bp_data = calculate_severity(
            vitals["spo2"], vitals["hr"], vitals["bp_sys"], vitals["bp_dia"]
        )
        
        # Determine overall status
        all_labels = [spo2_data[1], hr_data[1], bp_data[1]]
        if "CRITICAL" in all_labels:
            overall_color, overall_status = "#dc3545", "CRITICAL"
        elif "WARNING" in all_labels:
            overall_color, overall_status = "#ffc107", "WARNING"
        else:
            overall_color, overall_status = "#28a745", "NORMAL"

        # Dynamically set text color so numbers are readable against warning yellow
        spo2_text = "black" if spo2_data[0] == "#ffc107" else "white"
        hr_text = "black" if hr_data[0] == "#ffc107" else "white"
        bp_text = "black" if bp_data[0] == "#ffc107" else "white"
        overall_text = "black" if overall_color == "#ffc107" else "white"

        # Build each row safely using single-line f-strings to prevent Markdown breaks
        html_table += "<tr>"
        html_table += f"<td style='padding: 12px; border: 1px solid #555; font-weight: bold;'>{patient['name']}</td>"
        html_table += f"<td style='padding: 12px; border: 1px solid #555;'>{patient['age']}</td>"
        
        # Vital sign cells displaying the ACTUAL numerical values with color coding
        html_table += f"<td style='padding: 12px; border: 1px solid #555; background-color: {spo2_data[0]}; color: {spo2_text}; font-size: 18px; font-weight: bold;'>{vitals['spo2']}%</td>"
        html_table += f"<td style='padding: 12px; border: 1px solid #555; background-color: {hr_data[0]}; color: {hr_text}; font-size: 18px; font-weight: bold;'>{vitals['hr']}</td>"
        html_table += f"<td style='padding: 12px; border: 1px solid #555; background-color: {bp_data[0]}; color: {bp_text}; font-size: 18px; font-weight: bold;'>{vitals['bp_sys']} / {vitals['bp_dia']}</td>"
        
        # Overall status
        html_table += f"<td style='padding: 12px; border: 1px solid #555; background-color: {overall_color}; color: {overall_text}; font-size: 16px; font-weight: bold;'>{overall_status}</td>"
        html_table += "</tr>"

    html_table += "</table>"

    # Render HTML
    streamlit.markdown(html_table, unsafe_allow_html=True)
    streamlit.caption(f"Continuous Data Stream Synced: {time.strftime('%H:%M:%S')}")

# Execute
render_live_ward_table()
