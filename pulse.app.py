import streamlit
import random
import time
import smtplib
from email.message import EmailMessage

streamlit.set_page_config(page_title="PulseGuard AI", layout="wide")

# --- 1. Session State Initialization ---
# Tracks historical trends for the charts and prevents SMS spam
if "vital_history" not in streamlit.session_state:
    streamlit.session_state.vital_history = {
        "heart_rate": [],
        "spo2": [],
        "bp_sys": []
    }
if "last_alert_time" not in streamlit.session_state:
    streamlit.session_state.last_alert_time = 0 

# --- 2. Automated SMS Alert Engine ---
def dispatch_emergency_sms(alert_reason):
    """Sends an SMS via carrier email gateways with a 60-second cooldown."""
    current_time = time.time()
    cooldown_period = 60 
    
    if current_time - streamlit.session_state.last_alert_time < cooldown_period:
        return # Skip sending if in cooldown period
        
    # SETUP REQUIRED: Enter your sender Gmail and App Password
    sender_email = "your_prototype_email@gmail.com"
    sender_password = "your_16_digit_app_password" 
    
    # SETUP REQUIRED: Enter the target phone number and carrier gateway
    # AT&T: number@txt.att.net
    # T-Mobile: number@tmomail.net
    # Verizon: number@vtext.com
    # Sprint: number@messaging.sprintpcs.com
    target_sms_gateway = "1234567890@vtext.com" 

    message = EmailMessage()
    message.set_content(f"PULSEGUARD ALERT:\n{alert_reason}\nCheck dashboard immediately.")
    message['Subject'] = "CRITICAL VITALS"
    message['From'] = sender_email
    message['To'] = target_sms_gateway

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        streamlit.session_state.last_alert_time = current_time
        streamlit.toast(f"Emergency SMS Dispatched! ({alert_reason})", icon="📱")
        
    except Exception as error_message:
        streamlit.toast(f"Failed to send SMS: {error_message}")

# --- 3. Triage Logic Engine ---
def calculate_severity(spo2, heart_rate, bp_systolic, bp_diastolic):
    """Evaluates vital readings and maps to severity colors and labels."""
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

    if bp_systolic >= 180 or bp_diastolic >= 110:
        bp_color, bp_label = "#dc3545", "CRITICAL"
    elif (120 <= bp_systolic <= 179) or (80 <= bp_diastolic <= 109):
        bp_color, bp_label = "#ffc107", "WARNING"
    else:
        bp_color, bp_label = "#28a745", "NORMAL"

    return (spo2_color, spo2_label), (hr_color, hr_label), (bp_color, bp_label)

# --- 4. Simulated Data Engine ---
def generate_telemetry(profile_mode):
    """Generates continuous stream payloads based on testing profile."""
    if profile_mode == "Normal Profile":
        return {"spo2": random.randint(96, 100), "hr": random.randint(65, 82), "bp_sys": random.randint(110, 118), "bp_dia": random.randint(70, 78)}
    elif profile_mode == "Critical Hypoxia Event":
        return {"spo2": random.randint(82, 88), "hr": random.randint(115, 135), "bp_sys": random.randint(125, 140), "bp_dia": random.randint(82, 90)}
    elif profile_mode == "Hypertensive Crisis Event":
        return {"spo2": random.randint(94, 97), "hr": random.randint(105, 128), "bp_sys": random.randint(182, 205), "bp_dia": random.randint(112, 125)}
    else:
        return {
            "spo2": random.choice([random.randint(96, 99), random.randint(86, 92)]),
            "hr": random.choice([random.randint(68, 85), random.randint(120, 138)]),
            "bp_sys": random.choice([random.randint(115, 122), random.randint(180, 195)]),
            "bp_dia": random.choice([random.randint(72, 79), random.randint(110, 120)])
        }

# --- 5. Application UI ---
streamlit.title("PulseGuard AI - Continuous Health Monitoring")
streamlit.caption("Automated visual triage and live SMS alerting system.")

# Control Sidebar
streamlit.sidebar.header("Data Stream Controls")
simulation_profile = streamlit.sidebar.selectbox(
    "Active Patient Condition",
    ["Normal Profile", "Critical Hypoxia Event", "Hypertensive Crisis Event", "Random Fluctuations"]
)
update_frequency = streamlit.sidebar.slider("Sampling Interval (Seconds)", min_value=1, max_value=5, value=2)

# Fragment rerun automatically simulates continuous incoming telemetry
@streamlit.fragment(run_every=update_frequency)
def render_live_vitals_panel():
    data = generate_telemetry(simulation_profile)
    
    # Track historical data
    streamlit.session_state.vital_history["heart_rate"].append(data["hr"])
    streamlit.session_state.vital_history["spo2"].append(data["spo2"])
    streamlit.session_state.vital_history["bp_sys"].append(data["bp_sys"])
    
    if len(streamlit.session_state.vital_history["heart_rate"]) > 20:
        streamlit.session_state.vital_history["heart_rate"].pop(0)
        streamlit.session_state.vital_history["spo2"].pop(0)
        streamlit.session_state.vital_history["bp_sys"].pop(0)

    # Process Triage Colors
    spo2_info, hr_info, bp_info = calculate_severity(
        data["spo2"], data["hr"], data["bp_sys"], data["bp_dia"]
    )

    # Trigger SMS if any vital is Critical
    critical_events = []
    if spo2_info[1] == "CRITICAL":
        critical_events.append(f"SpO2: {data['spo2']}%")
    if hr_info[1] == "CRITICAL":
        critical_events.append(f"HR: {data['hr']} BPM")
    if bp_info[1] == "CRITICAL":
        critical_events.append(f"BP: {data['bp_sys']}/{data['bp_dia']}")
        
    if len(critical_events) > 0:
        alert_reason_text = " | ".join(critical_events)
        dispatch_emergency_sms(alert_reason_text)

    # UI Rendering
    card_template = """
    <div style="background-color: {bg_color}; border-radius: 12px; padding: 22px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
        <h4 style="margin: 0; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;">{title}</h4>
        <h1 style="margin: 10px 0; font-size: 2.8rem; font-weight: bold;">{value} <span style="font-size: 1.2rem;">{unit}</span></h1>
        <div style="background-color: rgba(0,0,0,0.25); display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
            {status}
        </div>
    </div>
    """

    column1, column2, column3 = streamlit.columns(3)

    with column1:
        streamlit.markdown(card_template.format(bg_color=spo2_info[0], title="Blood Oxygen (SpO2)", value=data["spo2"], unit="%", status=spo2_info[1]), unsafe_allow_html=True)
    with column2:
        streamlit.markdown(card_template.format(bg_color=hr_info[0], title="Heart Rate", value=data["hr"], unit="BPM", status=hr_info[1]), unsafe_allow_html=True)
    with column3:
        streamlit.markdown(card_template.format(bg_color=bp_info[0], title="Blood Pressure", value=f"{data['bp_sys']}/{data['bp_dia']}", unit="mmHg", status=bp_info[1]), unsafe_allow_html=True)

    streamlit.subheader("Live Vitals Progression")
    streamlit.line_chart({
        "Heart Rate (BPM)": streamlit.session_state.vital_history["heart_rate"],
        "SpO2 (%)": streamlit.session_state.vital_history["spo2"],
        "Systolic BP (mmHg)": streamlit.session_state.vital_history["bp_sys"]
    })
    
    streamlit.caption(f"Continuous Telemetry Synchronized at: {time.strftime('%H:%M:%S')}")

render_live_vitals_panel()
