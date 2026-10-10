import streamlit
import random
import time
import smtplib
from email.message import EmailMessage

# --- 1. Configuration & State ---
streamlit.set_page_config(page_title="PulseGuard AI", layout="wide")

# Persistent session state for historical trends and SMS cooldown tracking
if "vital_history" not in streamlit.session_state:
    streamlit.session_state.vital_history = {
        "heart_rate": [],
        "spo2": [],
        "bp_sys": []
    }
if "last_sms_time" not in streamlit.session_state:
    streamlit.session_state.last_sms_time = 0

# --- 2. SMS Alert Gateway ---
def dispatch_emergency_sms(alert_reason, carrier_domain, phone_number):
    """Sends an SMS alert via carrier email gateways with a 60-second cooldown."""
    current_time = time.time()
    cooldown_period = 60  # Wait 60 seconds between SMS texts
    
    if current_time - streamlit.session_state.last_sms_time < cooldown_period:
        return  # Cooldown active, skip sending
        
    sender_email = "your_prototype_email@gmail.com"  # Replace with your Gmail
    sender_password = "your_16_digit_app_password"   # Replace with Google App Password
    
    # Construct the SMS gateway address (e.g., 5551234567@txt.att.net)
    recipient_address = f"{phone_number}@{carrier_domain}"

    message = EmailMessage()
    # SMS messages should be brief
    message.set_content(f"PULSEGUARD ALERT: Patient Critical.\nReason: {alert_reason}")
    message['Subject'] = "URGENT"
    message['From'] = sender_email
    message['To'] = recipient_address

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        streamlit.session_state.last_sms_time = current_time
        streamlit.toast(f"SMS Text Dispatched to Doctor! ({alert_reason})", icon="📱")
    except Exception as error_message:
        streamlit.toast(f"Failed to send SMS: {error_message}", icon="⚠️")

# --- 3. Triage Logic Engine ---
def calculate_severity(spo2, heart_rate, bp_systolic, bp_diastolic):
    """Evaluates vitals and returns color hex codes and string labels."""
    if spo2 < 90:
        spo2_info = ("#dc3545", "CRITICAL")
    elif 90 <= spo2 <= 94:
        spo2_info = ("#ffc107", "WARNING")
    else:
        spo2_info = ("#28a745", "NORMAL")

    if heart_rate < 50 or heart_rate >= 120:
        hr_info = ("#dc3545", "CRITICAL")
    elif (50 <= heart_rate <= 59) or (101 <= heart_rate <= 119):
        hr_info = ("#ffc107", "WARNING")
    else:
        hr_info = ("#28a745", "NORMAL")

    if bp_systolic >= 180 or bp_diastolic >= 110:
        bp_info = ("#dc3545", "CRITICAL")
    elif (120 <= bp_systolic <= 179) or (80 <= bp_diastolic <= 109):
        bp_info = ("#ffc107", "WARNING")
    else:
        bp_info = ("#28a745", "NORMAL")

    return spo2_info, hr_info, bp_info

# --- 4. Simulated Data Engine ---
def generate_telemetry(profile_mode):
    """Generates continuous stream payloads based on testing profile."""
    if profile_mode == "Normal Profile":
        return {"spo2": random.randint(96, 100), "hr": random.randint(65, 82), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile_mode == "Critical Hypoxia Event":
        return {"spo2": random.randint(82, 88), "hr": random.randint(115, 135), "bp_sys": random.randint(125, 140), "bp_dia": random.randint(82, 90)}
    elif profile_mode == "Hypertensive Crisis Event":
        return {"spo2": random.randint(94, 97), "hr": random.randint(105, 128), "bp_sys": random.randint(182, 205), "bp_dia": random.randint(112, 125)}

# --- 5. Dashboard UI ---
streamlit.title("PulseGuard AI - Real-Time Vitals & SMS Alerts")

# Sidebar Configuration
streamlit.sidebar.header("Data Stream Controls")
simulation_profile = streamlit.sidebar.selectbox("Active Patient Condition", ["Normal Profile", "Critical Hypoxia Event", "Hypertensive Crisis Event"])

streamlit.sidebar.markdown("---")
streamlit.sidebar.header("SMS Alert Configuration")
enable_sms = streamlit.sidebar.checkbox("Enable Automatic SMS Alerts", value=False)
doctor_phone = streamlit.sidebar.text_input("Doctor Phone Number (No dashes)", "5551234567")
# Dictionary mapping carrier names to their email-to-sms domains
carrier_mapping = {
    "Verizon": "vtext.com",
    "AT&T": "txt.att.net",
    "T-Mobile": "tmomail.net",
    "Sprint": "messaging.sprintpcs.com"
}
selected_carrier = streamlit.sidebar.selectbox("Mobile Carrier", list(carrier_mapping.keys()))
carrier_domain = carrier_mapping[selected_carrier]

# Fragment rerun automatically simulates continuous incoming telemetry
@streamlit.fragment(run_every=2)
def render_live_vitals_panel():
    data = generate_telemetry(simulation_profile)
    
    # Track history
    streamlit.session_state.vital_history["heart_rate"].append(data["hr"])
    streamlit.session_state.vital_history["spo2"].append(data["spo2"])
    streamlit.session_state.vital_history["bp_sys"].append(data["bp_sys"])
    if len(streamlit.session_state.vital_history["heart_rate"]) > 20:
        streamlit.session_state.vital_history["heart_rate"].pop(0)
        streamlit.session_state.vital_history["spo2"].pop(0)
        streamlit.session_state.vital_history["bp_sys"].pop(0)

    spo2_info, hr_info, bp_info = calculate_severity(data["spo2"], data["hr"], data["bp_sys"], data["bp_dia"])

    # Trigger SMS if enabled and any vital is CRITICAL
    if enable_sms:
        critical_events = []
        if spo2_info[1] == "CRITICAL":
            critical_events.append(f"SpO2 {data['spo2']}%")
        if hr_info[1] == "CRITICAL":
            critical_events.append(f"HR {data['hr']} BPM")
        if bp_info[1] == "CRITICAL":
            critical_events.append(f"BP {data['bp_sys']}/{data['bp_dia']}")
            
        if critical_events:
            alert_reason_text = " | ".join(critical_events)
            dispatch_emergency_sms(alert_reason_text, carrier_domain, doctor_phone)

    # Render Cards
    card_template = """
    <div style="background-color: {bg_color}; border-radius: 12px; padding: 22px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
        <h4 style="margin: 0; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;">{title}</h4>
        <h1 style="margin: 10px 0; font-size: 2.8rem; font-weight: bold;">{value} <span style="font-size: 1.2rem;">{unit}</span></h1>
        <div style="background-color: rgba(0,0,0,0.25); display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
            {status}
        </div>
    </div>
    """

    col1, col2, col3 = streamlit.columns(3)
    with col1:
        streamlit.markdown(card_template.format(bg_color=spo2_info[0], title="SpO2", value=data["spo2"], unit="%", status=spo2_info[1]), unsafe_allow_html=True)
    with col2:
        streamlit.markdown(card_template.format(bg_color=hr_info[0], title="Heart Rate", value=data["hr"], unit="BPM", status=hr_info[1]), unsafe_allow_html=True)
    with col3:
        streamlit.markdown(card_template.format(bg_color=bp_info[0], title="Blood Pressure", value=f"{data['bp_sys']}/{data['bp_dia']}", unit="mmHg", status=bp_info[1]), unsafe_allow_html=True)

    # Render History Chart
    streamlit.subheader("Live Vitals Progression")
    streamlit.line_chart({
        "Heart Rate (BPM)": streamlit.session_state.vital_history["heart_rate"],
        "SpO2 (%)": streamlit.session_state.vital_history["spo2"],
        "Systolic BP (mmHg)": streamlit.session_state.vital_history["bp_sys"]
    })

render_live_vitals_panel()
