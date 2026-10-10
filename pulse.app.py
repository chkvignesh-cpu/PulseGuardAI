import streamlit
import random
import time

streamlit.set_page_config(page_title="PulseGuard AI - Clinical Ward EHR", layout="wide")

# --- 1. Generate 1000 Patient Records with Clinical EHR Profiles ---
# Runs only once on startup to populate the database
if "patient_registry" not in streamlit.session_state:
    # Using common Indian names to match the regional context
    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Shaurya", "Atharv", "Dhruv", "Kabir", "Rudra", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari",
        "Anika", "Navya", "Angel", "Myra", "Sara", "Ira", "Riya", "Aarohi", "Anvi", "Prisha"
    ]
    last_names = [
        "Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Kulkarni", "Deshmukh", "Mehta",
        "Gupta", "Singh", "Kumar", "Chopra", "Bose", "Chatterjee", "Banerjee", "Pillai", "Menon", "Joshi",
        "Bhat", "Hegde", "Shetty", "Gowda", "Naidu", "Chowdhury", "Das", "Dutta", "Mukherjee", "Sen",
        "Malhotra", "Kapoor", "Khanna", "Saxena"
    ]
    
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    allergies_list = [
        "None Known (NKDA)", "Penicillin", "Sulfa Drugs", "Aspirin / NSAIDs", 
        "Latex", "Peanuts", "Dust Mites", "Ciprofloxacin"
    ]
    histories_list = [
        "No Major Medical History", "Type 2 Diabetes Mellitus", "Essential Hypertension", 
        "Coronary Artery Disease (Post-Stent 2023)", "Asthma (Moderate Persistent)", 
        "Chronic Kidney Disease Stage 2", "Hypothyroidism", "Previous Stroke (2022)"
    ]
    medications_list = [
        "None", "Metformin 500mg BD", "Amlodipine 5mg OD", "Atorvastatin 20mg HS",
        "Telmisartan 40mg OD", "Salbutamol Inhaler PRN", "Levothyroxine 50mcg OD", "Ecosprin 75mg OD"
    ]
    
    registry = []
    patient_count = 0
    
    for first in first_names:
        for last in last_names:
            if patient_count >= 1000:
                break
            
            patient_id = f"PG-{1001 + patient_count}"
            
            # Risk profile stratification
            profile_chance = random.random()
            if profile_chance < 0.85:
                profile = "Stable"
            elif profile_chance < 0.90:
                profile = "Hypoxia Risk"
            elif profile_chance < 0.95:
                profile = "Hypertension Risk"
            else:
                profile = "Volatile"
                
            # Indian mobile format: +91 9xxxx xxxxx / 8xxxx xxxxx / 7xxxx xxxxx
            mobile_prefix = random.choice(["98", "97", "99", "88", "70", "91", "63"])
            mobile_suffix = str(random.randint(10000000, 99999999))
            phone_number = f"+91 {mobile_prefix}{mobile_suffix[:3]} {mobile_suffix[3:]}"
            
            # Formatted email
            email_addr = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"
            
            registry.append({
                "id": patient_id,
                "name": f"{first} {last}",
                "age": random.randint(19, 88),
                "gender": random.choice(["Male", "Female"]),
                "blood_group": random.choice(blood_groups),
                "condition": profile,
                "allergies": random.choice(allergies_list),
                "history": random.choice(histories_list),
                "medications": random.choice(medications_list),
                "contact": phone_number,
                "email": email_addr,
                "emergency_contact": f"+91 {random.choice(['98', '99', '88'])}{str(random.randint(1000000, 9999999))}"
            })
            patient_count += 1
            
        if patient_count >= 1000:
            break
            
    streamlit.session_state.patient_registry = registry

# --- 2. Triage Logic Engine ---
def calculate_severity(spo2, heart_rate, bp_sys, bp_dia):
    """Evaluates individual vitals and returns the hex color and severity level."""
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
    """Generates live continuous streams based on patient baseline condition."""
    if profile == "Stable":
        return {"spo2": random.randint(96, 100), "hr": random.randint(60, 85), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile == "Hypoxia Risk":
        return {"spo2": random.randint(85, 93), "hr": random.randint(95, 115), "bp_sys": random.randint(120, 135), "bp_dia": random.randint(80, 90)}
    elif profile == "Hypertension Risk":
        return {"spo2": random.randint(95, 99), "hr": random.randint(80, 105), "bp_sys": random.randint(165, 190), "bp_dia": random.randint(95, 115)}
    else:
        return {"spo2": random.randint(88, 99), "hr": random.randint(45, 130), "bp_sys": random.randint(100, 185), "bp_dia": random.randint(60, 115)}

# --- 4. Main UI Dashboard ---
streamlit.title("PulseGuard AI - Priority Triage Ward")
streamlit.write("Dynamically sorted telemetry for 1,000 patients. Use the EHR Lookup tool below to view deep medical histories.")

# --- LIVE TELEMETRY WARD ---
@streamlit.fragment(run_every=2)
def render_live_ward_table():
    critical_rows = []
    warning_rows = []
    normal_rows = []

    for patient in streamlit.session_state.patient_registry:
        vitals = generate_patient_vitals(patient["condition"])
        
        spo2_data, hr_data, bp_data = calculate_severity(
            vitals["spo2"], vitals["hr"], vitals["bp_sys"], vitals["bp_dia"]
        )
        
        all_labels = [spo2_data[1], hr_data[1], bp_data[1]]
        if "CRITICAL" in all_labels:
            overall_color, overall_status = "#dc3545", "CRITICAL"
        elif "WARNING" in all_labels:
            overall_color, overall_status = "#ffc107", "WARNING"
        else:
            overall_color, overall_status = "#28a745", "NORMAL"

        spo2_text = "black" if spo2_data[0] == "#ffc107" else "white"
        hr_text = "black" if hr_data[0] == "#ffc107" else "white"
        bp_text = "black" if bp_data[0] == "#ffc107" else "white"
        overall_text = "black" if overall_color == "#ffc107" else "white"

        row = (
            f"<tr>"
            f"<td style='padding: 8px; border: 1px solid #555; font-weight: bold;'>{patient['id']}</td>"
            f"<td style='padding: 8px; border: 1px solid #555; font-weight: bold;'>{patient['name']}</td>"
            f"<td style='padding: 8px; border: 1px solid #555;'>{patient['blood_group']}</td>"
            f"<td style='padding: 8px; border: 1px solid #555; background-color: {spo2_data[0]}; color: {spo2_text}; font-weight: bold;'>{vitals['spo2']}%</td>"
            f"<td style='padding: 8px; border: 1px solid #555; background-color: {hr_data[0]}; color: {hr_text}; font-weight: bold;'>{vitals['hr']}</td>"
            f"<td style='padding: 8px; border: 1px solid #555; background-color: {bp_data[0]}; color: {bp_text}; font-weight: bold;'>{vitals['bp_sys']}/{vitals['bp_dia']}</td>"
            f"<td style='padding: 8px; border: 1px solid #555; background-color: {overall_color}; color: {overall_text}; font-weight: bold;'>{overall_status}</td>"
            f"</tr>"
        )
        
        if overall_status == "CRITICAL":
            critical_rows.append(row)
        elif overall_status == "WARNING":
            warning_rows.append(row)
        else:
            normal_rows.append(row)

    col1, col2, col3 = streamlit.columns(3)
    with col1:
        streamlit.metric("🔴 CRITICAL EMERGENCIES", len(critical_rows))
    with col2:
        streamlit.metric("🟡 WARNING STATUS", len(warning_rows))
    with col3:
        streamlit.metric("🟢 STABLE PATIENTS", len(normal_rows))

    table_header = """
    <div style="max-height: 400px; overflow-y: auto; border: 2px solid #555; border-radius: 5px; margin-bottom: 20px;">
        <table style="width: 100%; text-align: center; border-collapse: collapse; font-family: sans-serif; font-size: 0.9rem;">
            <thead style="position: sticky; top: 0; background-color: #222; color: white; z-index: 1;">
                <tr>
                    <th style="padding: 10px; border: 1px solid #555;">ID</th>
                    <th style="padding: 10px; border: 1px solid #555;">Patient Name</th>
                    <th style="padding: 10px; border: 1px solid #555;">Blood</th>
                    <th style="padding: 10px; border: 1px solid #555;">SpO2 (%)</th>
                    <th style="padding: 10px; border: 1px solid #555;">Heart Rate</th>
                    <th style="padding: 10px; border: 1px solid #555;">Blood Pressure</th>
                    <th style="padding: 10px; border: 1px solid #555;">Triage Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    complete_html = table_header + "".join(critical_rows) + "".join(warning_rows) + "".join(normal_rows) + "</tbody></table></div>"
    streamlit.markdown(complete_html, unsafe_allow_html=True)
    streamlit.caption(f"Telemetry Synced at: {time.strftime('%H:%M:%S')}")

render_live_ward_table()

# --- 5. DEEP EHR LOOKUP DRAWER ---
streamlit.markdown("---")
streamlit.subheader("🏥 Electronic Health Record (EHR) Lookup")

# Create a dropdown to select a patient by ID or Name
patient_lookup_list = [f"{p['id']} - {p['name']}" for p in streamlit.session_state.patient_registry]
selected_patient_str = streamlit.selectbox("Search Patient Database:", patient_lookup_list)

# Extract the selected patient's dictionary
selected_id = selected_patient_str.split(" - ")[0]
patient_data = next((p for p in streamlit.session_state.patient_registry if p["id"] == selected_id), None)

if patient_data:
    # Render the EHR Card using Streamlit layout
    ehr_card_html = f"""
    <div style="background-color: #1e1e1e; padding: 25px; border-radius: 10px; border-left: 6px solid #17a2b8; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <h3 style="margin-top: 0; color: #17a2b8;">{patient_data['name']} <span style="color: gray; font-size: 1.2rem;">({patient_data['id']})</span></h3>
        <hr style="border-color: #444;">
        <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
            
            <div style="flex: 1; min-width: 250px; margin-bottom: 15px;">
                <h4 style="color: #ccc; margin-bottom: 5px;">Demographics</h4>
                <b>Age/Gender:</b> {patient_data['age']} yrs, {patient_data['gender']}<br>
                <b>Blood Group:</b> <span style="color: #dc3545; font-weight: bold;">{patient_data['blood_group']}</span><br>
                <b>Primary Contact:</b> {patient_data['contact']}<br>
                <b>Email:</b> {patient_data['email']}<br>
                <b>Emergency Contact:</b> {patient_data['emergency_contact']}
            </div>

            <div style="flex: 1; min-width: 250px; margin-bottom: 15px;">
                <h4 style="color: #ccc; margin-bottom: 5px;">Clinical History</h4>
                <b>Allergies:</b> <span style="color: #ffc107; font-weight: bold;">{patient_data['allergies']}</span><br>
                <b>Medical History:</b> {patient_data['history']}<br>
                <b>Current Medications:</b> {patient_data['medications']}<br>
                <b>Underlying Risk Profile:</b> {patient_data['condition']}
            </div>

        </div>
    </div>
    """
    streamlit.markdown(ehr_card_html, unsafe_allow_html=True)
