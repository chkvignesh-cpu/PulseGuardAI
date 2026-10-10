import streamlit
import random
import time

streamlit.set_page_config(page_title="PulseGuard AI - Ward Dashboard", layout="wide")

# --- 1. Generate 1000 Patient Records ---
# We use a fixed random seed here so that when a new tab opens (creating a new session),
# the generated patient database remains exactly identical across all browser tabs.
if "patient_registry" not in streamlit.session_state:
    current_random_state = random.getstate()
    random.seed(42) # Lock seed for consistent multi-tab generation
    
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Dhruv", "Kabir", "Rudra", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Anika", "Navya", "Angel", "Myra", "Sara", "Ira", "Riya", "Aarohi", "Anvi", "Prisha"]
    last_names = ["Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Kulkarni", "Deshmukh", "Mehta", "Gupta", "Singh", "Kumar", "Chopra", "Bose", "Chatterjee", "Banerjee", "Pillai", "Menon", "Joshi", "Bhat", "Hegde", "Shetty", "Gowda", "Naidu", "Chowdhury", "Das", "Dutta", "Mukherjee", "Sen", "Malhotra", "Kapoor", "Khanna", "Saxena"]
    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    allergies_list = ["None Known (NKDA)", "Penicillin", "Sulfa Drugs", "Aspirin / NSAIDs", "Latex", "Peanuts", "Dust Mites", "Ciprofloxacin"]
    histories_list = ["No Major Medical History", "Type 2 Diabetes Mellitus", "Essential Hypertension", "Coronary Artery Disease (Post-Stent)", "Asthma (Moderate Persistent)", "Chronic Kidney Disease Stage 2", "Hypothyroidism", "Previous Stroke (2022)"]
    medications_list = ["None", "Metformin 500mg BD", "Amlodipine 5mg OD", "Atorvastatin 20mg HS", "Telmisartan 40mg OD", "Salbutamol Inhaler PRN", "Levothyroxine 50mcg OD", "Ecosprin 75mg OD"]
    
    registry = []
    patient_count = 0
    
    for first in first_names:
        for last in last_names:
            if patient_count >= 1000:
                break
            
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
                
            mobile_prefix = random.choice(["98", "97", "99", "88", "70", "91", "63"])
            mobile_suffix = str(random.randint(10000000, 99999999))
            phone_number = f"+91 {mobile_prefix}{mobile_suffix[:3]} {mobile_suffix[3:]}"
            email_addr = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"
            
            registry.append({
                "id": f"PG-{1001 + patient_count}",
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
    random.setstate(current_random_state) # Restore normal randomness for telemetry

# --- 2. Triage Logic Engine ---
def calculate_severity(spo2, heart_rate, bp_sys, bp_dia):
    if spo2 < 90:
        spo2_data = ("#dc3545", "CRITICAL")
    elif 90 <= spo2 <= 94:
        spo2_data = ("#ffc107", "WARNING")
    else:
        spo2_data = ("#28a745", "NORMAL")

    if heart_rate < 50 or heart_rate >= 120:
        hr_data = ("#dc3545", "CRITICAL")
    elif (50 <= heart_rate <= 59) or (101 <= heart_rate <= 119):
        hr_data = ("#ffc107", "WARNING")
    else:
        hr_data = ("#28a745", "NORMAL")

    if bp_sys >= 180 or bp_dia >= 110:
        bp_data = ("#dc3545", "CRITICAL")
    elif (120 <= bp_sys <= 179) or (80 <= bp_dia <= 109):
        bp_data = ("#ffc107", "WARNING")
    else:
        bp_data = ("#28a745", "NORMAL")

    return spo2_data, hr_data, bp_data

# --- 3. Simulated Telemetry Engine ---
def generate_patient_vitals(profile):
    if profile == "Stable":
        return {"spo2": random.randint(96, 100), "hr": random.randint(60, 85), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile == "Hypoxia Risk":
        return {"spo2": random.randint(85, 93), "hr": random.randint(95, 115), "bp_sys": random.randint(120, 135), "bp_dia": random.randint(80, 90)}
    elif profile == "Hypertension Risk":
        return {"spo2": random.randint(95, 99), "hr": random.randint(80, 105), "bp_sys": random.randint(165, 190), "bp_dia": random.randint(95, 115)}
    else:
        return {"spo2": random.randint(88, 99), "hr": random.randint(45, 130), "bp_sys": random.randint(100, 185), "bp_dia": random.randint(60, 115)}

# --- 4. APP ROUTING LOGIC ---
# Check if the URL has a "patient_id" query parameter (meaning a new tab was opened)
url_params = streamlit.query_params

if "patient_id" in url_params:
    # =================================================================
    # ROUTE A: INDIVIDUAL PATIENT EHR (NEW TAB)
    # =================================================================
    target_id = url_params["patient_id"]
    patient_data = next((p for p in streamlit.session_state.patient_registry if p["id"] == target_id), None)
    
    if patient_data:
        # Top Navigation Button
        if streamlit.button("← Return to Main Ward"):
            streamlit.query_params.clear()
            streamlit.rerun()
            
        streamlit.title(f"🏥 {patient_data['name']} - Medical Record")
        
        ehr_card_html = f"""
        <div style="background-color: #1e1e1e; padding: 30px; border-radius: 12px; border-left: 8px solid #17a2b8; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-top: 20px;">
            <h2 style="margin-top: 0; color: #17a2b8; margin-bottom: 5px;">Patient ID: {patient_data['id']}</h2>
            <hr style="border-color: #444; margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                
                <div style="flex: 1; min-width: 300px; margin-bottom: 20px; border-right: 1px solid #444; padding-right: 20px;">
                    <h3 style="color: #ccc; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 5px;">Demographics & Contact</h3>
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                    <b>Age / Gender:</b> {patient_data['age']} yrs, {patient_data['gender']}<br>
                    <b>Blood Group:</b> <span style="color: #dc3545; font-weight: bold; font-size: 1.2rem;">{patient_data['blood_group']}</span><br>
                    <b>Mobile (Primary):</b> {patient_data['contact']}<br>
                    <b>Email Address:</b> {patient_data['email']}<br>
                    <b>Emergency Contact:</b> <span style="color: #ffc107;">{patient_data['emergency_contact']}</span>
                    </p>
                </div>
    
                <div style="flex: 1; min-width: 300px; margin-bottom: 20px; padding-left: 20px;">
                    <h3 style="color: #ccc; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 5px;">Clinical Profile</h3>
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                    <b>Known Allergies:</b> <span style="color: #ffc107; font-weight: bold;">{patient_data['allergies']}</span><br>
                    <b>Previous Medical History:</b> <br><span style="color: #fff;">{patient_data['history']}</span><br><br>
                    <b>Current Medications:</b> <br><span style="color: #fff;">{patient_data['medications']}</span><br><br>
                    <b>System Risk Assessment:</b> {patient_data['condition']}
                    </p>
                </div>
    
            </div>
        </div>
        """
        streamlit.markdown(ehr_card_html, unsafe_allow_html=True)
    else:
        streamlit.error("Patient Record Not Found.")
        
else:
    # =================================================================
    # ROUTE B: MAIN LIVE WARD DASHBOARD (DEFAULT VIEW)
    # =================================================================
    streamlit.title("PulseGuard AI - Priority Triage Ward")
    streamlit.write("Click on any **Patient Name** (in blue) to open their full Electronic Health Record in a new tab.")

    @streamlit.fragment(run_every=2)
    def render_live_ward_table():
        critical_rows, warning_rows, normal_rows = [], [], []

        for patient in streamlit.session_state.patient_registry:
            vitals = generate_patient_vitals(patient["condition"])
            spo2_data, hr_data, bp_data = calculate_severity(vitals["spo2"], vitals["hr"], vitals["bp_sys"], vitals["bp_dia"])
            
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

            # The Patient Name is now a clickable HTML link opening a new tab
            row = (
                f"<tr>"
                f"<td style='padding: 8px; border: 1px solid #555;'>{patient['id']}</td>"
                f"<td style='padding: 8px; border: 1px solid #555; font-weight: bold;'>"
                f"  <a href='?patient_id={patient['id']}' target='_blank' style='color: #00d2ff; text-decoration: none;'>{patient['name']} 🔗</a>"
                f"</td>"
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
        <div style="max-height: 550px; overflow-y: auto; border: 2px solid #555; border-radius: 5px; margin-bottom: 20px;">
            <table style="width: 100%; text-align: center; border-collapse: collapse; font-family: sans-serif; font-size: 0.95rem;">
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
