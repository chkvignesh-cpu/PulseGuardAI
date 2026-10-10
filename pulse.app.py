import streamlit
import random
import time

streamlit.set_page_config(page_title="PulseGuard AI - Ward Overview", layout="wide")

# --- 1. Patient Database & Triage Logic ---

# A static list of patients to simulate a hospital ward or clinic
PATIENT_REGISTRY = [
    {"name": "James Holden", "age": 42, "condition_profile": "Stable"},
    {"name": "Naomi Nagata", "age": 36, "condition_profile": "Stable"},
    {"name": "Amos Burton", "age": 45, "condition_profile": "Hypertension Risk"},
    {"name": "Alex Kamal", "age": 52, "condition_profile": "Hypoxia Risk"},
    {"name": "Chrisjen Avasarala", "age": 70, "condition_profile": "Volatile"}
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
        return {
            "spo2": random.randint(96, 100),
            "hr": random.randint(60, 85),
            "bp_sys": random.randint(110, 118),
            "bp_dia": random.randint(70, 78)
        }
    elif profile == "Hypoxia Risk":
        # Simulates a patient struggling with oxygen levels
        return {
            "spo2": random.randint(85, 93),
            "hr": random.randint(95, 115),
            "bp_sys": random.randint(120, 135),
            "bp_dia": random.randint(80, 90)
        }
    elif profile == "Hypertension Risk":
        # Simulates a patient with dangerously high blood pressure
        return {
            "spo2": random.randint(95, 99),
            "hr": random.randint(80, 105),
            "bp_sys": random.randint(165, 190),
            "bp_dia": random.randint(95, 115)
        }
    else:  # Volatile / Random
        return {
            "spo2": random.randint(88, 99),
            "hr": random.randint(45, 130),
            "bp_sys": random.randint(100, 185),
            "bp_dia": random.randint(60, 115)
        }

# --- 3. UI and Dashboard Assembly ---

streamlit.title("PulseGuard AI - Multi-Patient Ward")
streamlit.write("Continuous visual triage for multiple patients. Color indicators shift instantly based on vital thresholds.")

# Streamlit fragment auto-reruns the table every 2 seconds
@streamlit.fragment(run_every=2)
def render_live_ward_table():
    
    # Begin building the HTML table structure
    html_table = """
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <thead>
            <tr style="background-color: #1e1e1e; color: #ffffff; border-bottom: 2px solid #333;">
                <th style="padding: 15px;">Patient Name</th>
                <th style="padding: 15px;">Age</th>
                <th style="padding: 15px;">Blood Oxygen (SpO2)</th>
                <th style="padding: 15px;">Heart Rate (BPM)</th>
                <th style="padding: 15px;">Blood Pressure (mmHg)</th>
                <th style="padding: 15px;">Overall Triage Status</th>
            </tr>
        </thead>
        <tbody>
    """

    # Iterate through each patient and generate their live row
    for patient in PATIENT_REGISTRY:
        vitals = generate_patient_vitals(patient["condition_profile"])
        
        # Calculate severity colors and labels
        spo2_data, hr_data, bp_data = calculate_severity(
            vitals["spo2"], vitals["hr"], vitals["bp_sys"], vitals["bp_dia"]
        )
        
        # Determine the worst-case scenario for the patient's overall status
        all_labels = [spo2_data[1], hr_data[1], bp_data[1]]
        if "CRITICAL" in all_labels:
            overall_color = "#dc3545" # Red
            overall_status = "CRITICAL"
        elif "WARNING" in all_labels:
            overall_color = "#ffc107" # Yellow
            overall_status = "WARNING"
        else:
            overall_color = "#28a745" # Green
            overall_status = "NORMAL"

        # Determine text colors based on background (black text for yellow backgrounds for readability)
        spo2_text_color = "black" if spo2_data[0] == "#ffc107" else "white"
        hr_text_color = "black" if hr_data[0] == "#ffc107" else "white"
        bp_text_color = "black" if bp_data[0] == "#ffc107" else "white"
        overall_text_color = "black" if overall_color == "#ffc107" else "white"

        # Append the row HTML
        html_table += f"""
            <tr style="border-bottom: 1px solid #444; background-color: #2b2b2b; color: white;">
                <td style="padding: 12px; font-weight: bold;">{patient["name"]}</td>
                <td style="padding: 12px;">{patient["age"]}</td>
                <td style="padding: 12px; background-color: {spo2_data[0]}; color: {spo2_text_color}; font-weight: bold; font-size: 1.1rem;">
                    {vitals["spo2"]}%
                </td>
                <td style="padding: 12px; background-color: {hr_data[0]}; color: {hr_text_color}; font-weight: bold; font-size: 1.1rem;">
                    {vitals["hr"]}
                </td>
                <td style="padding: 12px; background-color: {bp_data[0]}; color: {bp_text_color}; font-weight: bold; font-size: 1.1rem;">
                    {vitals["bp_sys"]}/{vitals["bp_dia"]}
                </td>
                <td style="padding: 12px; background-color: {overall_color}; color: {overall_text_color}; font-weight: bold; font-size: 1.2rem; letter-spacing: 1px;">
                    {overall_status}
                </td>
            </tr>
        """

    # Close the HTML table
    html_table += """
        </tbody>
    </table>
    """

    # Render the custom table directly into Streamlit
    streamlit.markdown(html_table, unsafe_allow_html=True)
    streamlit.caption(f"Continuous Data Stream Synced: {time.strftime('%H:%M:%S')}")

# Execute the live update function
render_live_ward_table()
