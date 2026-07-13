import random
import uuid
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
NUM_CALLS = 300
START_TIME = datetime(2026, 7, 1, 10, 0, 0)

# ---------------- FAILURE MAP ----------------
FAILURE_MAP = {
    "RRC": "RRC_SETUP_FAILURE",
    "NAS": "AUTHENTICATION_FAILURE",
    "NGAP": "UE_CONTEXT_RELEASE_COMMAND",
    "SIP": "408 Request Timeout",
    "X2AP": "HO_FAILURE"
}

FAIL_PROB = {
    "RRC": 0.1,
    "NAS": 0.1,
    "NGAP": 0.1,
    "SIP": 0.15,
    "HO": 0.1
}

# ---------------- HELPERS ----------------
def ts(base, delta):
    return (base + timedelta(milliseconds=delta)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def random_ip():
    return f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def log_line(time, module, call_id, event):
    iface_map = {
        "RRC": "Uu",
        "NGAP": "N2",
        "NAS": "N1",
        "SIP": "IMS",
        "X2AP": "X2"
    }

    src_map = {
        "RRC": "UE",
        "NGAP": "gNB",
        "NAS": "UE",
        "SIP": random_ip(),
        "X2AP": "gNB1"
    }

    dst_map = {
        "RRC": "gNB",
        "NGAP": "AMF",
        "NAS": "AMF",
        "SIP": random_ip(),
        "X2AP": "gNB2"
    }
    # KPI enrichment (REALISTIC + OVERLAP)
    kpi = ""

    # --- RRC KPIs ---
    if module == "RRC":
        sinr = random.randint(-10, 30)
        rsrp = random.randint(-125, -70)

        # 🔥 Inject bad radio even in success cases
        if random.random() < 0.3:
            sinr = random.randint(-10, 5)
            rsrp = random.randint(-125, -100)

        kpi = f"| sinr={sinr} | rsrp={rsrp}"


    # --- SIP KPIs ---
    elif module == "SIP":
        latency = random.randint(10, 300)

        # 🔥 Latency spikes (even successful calls)
        if random.random() < 0.3:
            latency = random.randint(200, 600)

        kpi = f"| latency_ms={latency}"


    # --- NGAP KPIs ---
    elif module == "NGAP":
        core_delay = random.randint(5, 100)

        # 🔥 Core congestion simulation
        if random.random() < 0.25:
            core_delay = random.randint(80, 250)

        kpi = f"| core_delay_ms={core_delay}"
    return f"[{time}] {module} | iface={iface_map[module]} | src={src_map[module]} | dst={dst_map[module]} | callId={call_id} | event={event} {kpi}".strip()

# ---------------- FLOW ENGINE ----------------
def run_flow(flow, call_id, base_time, start_t, fail_key=None):
    logs = []
    t = start_t

    for module, event in flow:
        logs.append(log_line(ts(base_time, t), module, call_id, event))
        t += random.randint(20, 80)

        # Failure injection
        if fail_key == module and random.random() < FAIL_PROB.get(module, 0):
            fail_event = FAILURE_MAP[module]
            logs.append(log_line(ts(base_time, t), module, call_id, fail_event))
            #return logs, t, True
            # Inject failure but DO NOT always stop
            if random.random() < 0.5:
                return logs, t, True  # hard fail
            else:
                # recovery flow
                logs.append(log_line(ts(base_time, t), module, call_id, "RECOVERY_ATTEMPT"))
                t += random.randint(20, 50)

    return logs, t, False

# ---------------- FLOWS ----------------

REGISTRATION_FLOW = [
    ("RRC", "RRC_SETUP_REQUEST"),
    ("RRC", "RRC_SETUP_COMPLETE"),

    ("RRC", "RRC_SECURITY_MODE_COMMAND"),
    ("RRC", "RRC_SECURITY_MODE_COMPLETE"),

    # 🔥 Newly added
    ("RRC", "RRC_RECONFIGURATION"),
    ("RRC", "RRC_RECONFIGURATION_COMPLETE"),

    ("NGAP", "INITIAL_UE_MESSAGE"),
    ("NAS", "REGISTRATION_REQUEST"),
    ("NAS", "AUTHENTICATION_REQUEST"),
    ("NAS", "AUTHENTICATION_RESPONSE"),
    ("NAS", "REGISTRATION_ACCEPT"),
]

SESSION_FLOW = [
    ("NGAP", "PDU_SESSION_RESOURCE_SETUP_REQUEST"),
    ("NGAP", "PDU_SESSION_RESOURCE_SETUP_RESPONSE"),
]

SIP_FLOW = [
    ("SIP", "INVITE"),
    ("SIP", "100 Trying"),
    ("SIP", "180 Ringing"),
    ("SIP", "200 OK"),
    ("SIP", "ACK"),
]

HO_FLOW = [
    ("X2AP", "HO_REQUEST"),
    ("X2AP", "HO_REQUEST_ACK"),
    ("X2AP", "HO_COMMAND"),
    ("X2AP", "HO_SUCCESS"),
]

MEAS_FLOW = [
    ("RRC", "RRC_MEASUREMENT_REPORT"),
]

# ---------------- MAIN CALL FLOW ----------------
def generate_call(call_id, base_time):
    logs = []
    t = 0

    success = True  # track overall outcome

    # 1. Registration
    reg_logs, t, failed = run_flow(REGISTRATION_FLOW, call_id, base_time, t, "RRC")
    logs.extend(reg_logs)
    if failed:
        success = False

    # 🔥 Continue even if failed (recovery simulation)
    if failed and random.random() < 0.5:
        logs.append(log_line(ts(base_time, t), "RRC", call_id, "RECOVERY_ATTEMPT"))
        t += random.randint(20, 50)

    # 2. Session Setup
    sess_logs, t, failed = run_flow(SESSION_FLOW, call_id, base_time, t, "NGAP")
    logs.extend(sess_logs)
    if failed:
        success = False

    # 3. SIP Call (noisy + overlapping)
    sip_logs, t, failed = run_flow(SIP_FLOW, call_id, base_time, t, "SIP")
    logs.extend(sip_logs)

    if failed:
        success = False

    # 🔥 Overlap behavior
    if random.random() < 0.6:
        logs.append(log_line(ts(base_time, t), "SIP", call_id, "180 Ringing"))
        t += random.randint(10, 50)

    if random.random() < 0.5:
        logs.append(log_line(ts(base_time, t), "SIP", call_id, "100 Trying"))

    # 🔥 Contradictions
    if success and random.random() < 0.3:
        logs.append(log_line(ts(base_time, t), "SIP", call_id, "RETRY"))

    if not success and random.random() < 0.3:
        logs.append(log_line(ts(base_time, t), "RRC", call_id, "RRC_RECONFIGURATION"))

    # 4. Measurement + HO
    if random.random() < 0.5:
        meas_logs, t, _ = run_flow(MEAS_FLOW, call_id, base_time, t)
        logs.extend(meas_logs)

        ho_logs, t, _ = run_flow(HO_FLOW, call_id, base_time, t, "X2AP")
        logs.extend(ho_logs)

    # 🔥 CRITICAL: Normalize length (remove num_events leakage)
    target_len = random.randint(8, 20)

    while len(logs) < target_len:
        logs.append(log_line(
            ts(base_time, t),
            random.choice(["RRC", "SIP", "NGAP"]),
            call_id,
            random.choice(["NOISE_EVENT", "KEEPALIVE", "STATUS_CHECK"])
        ))
        t += random.randint(5, 20)

    return logs
'''
def generate_call(call_id, base_time):
    logs = []
    t = 0

    # 1. Registration
    reg_logs, t, failed = run_flow(REGISTRATION_FLOW, call_id, base_time, t, "RRC")
    logs.extend(reg_logs)
    if failed:
        return logs

    # 2. Session Setup
    sess_logs, t, failed = run_flow(SESSION_FLOW, call_id, base_time, t, "NGAP")
    logs.extend(sess_logs)
    if failed:
        return logs

    # 3. SIP Call
    #sip_logs, t, failed = run_flow(SIP_FLOW, call_id, base_time, t, "SIP")
    #logs.extend(sip_logs)
    #if failed:
    #    return logs
    
    # SIP Call (NOISY SUCCESS)
    sip_logs, t, failed = run_flow(SIP_FLOW, call_id, base_time, t, "SIP")
    logs.extend(sip_logs)

    # 🔥 Add noise even if success
    if not failed:
        if random.random() < 0.3:
            logs.append(log_line(ts(base_time, t), "SIP", call_id, "180 Ringing"))
            t += random.randint(10, 50)

        if random.random() < 0.2:
            logs.append(log_line(ts(base_time, t), "SIP", call_id, "100 Trying"))

    # 4. Measurement + HO
    if random.random() < 0.3:
        meas_logs, t, _ = run_flow(MEAS_FLOW, call_id, base_time, t)
        logs.extend(meas_logs)

        ho_logs, t, _ = run_flow(HO_FLOW, call_id, base_time, t, "X2AP")
        logs.extend(ho_logs)

    # Add random padding events (for BOTH success & fail)
    for _ in range(random.randint(0, 5)):
        logs.append(log_line(
            ts(base_time, t),
            random.choice(["RRC", "SIP", "NGAP"]),
            call_id,
            random.choice(["NOISE_EVENT", "KEEPALIVE", "STATUS_CHECK"])
        ))

    return logs
'''
# ---------------- GENERATOR ----------------
def generate_logs():
    all_logs = []

    for _ in range(NUM_CALLS):
        call_id = str(uuid.uuid4())[:8]
        base_time = START_TIME + timedelta(seconds=random.randint(0, 3600))

        call_logs = generate_call(call_id, base_time)
        all_logs.extend(call_logs)

    # Interleave logs
    random.shuffle(all_logs)

    with open("data/raw/telecom_logs.txt", "w") as f:
        for line in all_logs:
            f.write(line + "\n")

    print("✅ FINAL production-grade telecom logs generated!")

# Backward compatibility
def generate_all():
    generate_logs()

if __name__ == "__main__":
    generate_logs()