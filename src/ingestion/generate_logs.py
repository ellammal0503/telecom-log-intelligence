import random
import pandas as pd
from datetime import datetime, timedelta

NUM_CALLS = 1000
START_TIME = datetime(2026, 7, 1, 10, 0, 0)

def generate_all():

    sip_logs = []
    rrc_logs = []
    csr_logs = []

    for call_id in range(NUM_CALLS):

        t = START_TIME + timedelta(seconds=random.randint(0, 3600))

        # -----------------------------
        # NETWORK CONDITIONS (ROOT CAUSE)
        # -----------------------------
        packet_loss = random.random() < 0.2
        latency_issue = random.random() < 0.2
        bgp_down = random.random() < 0.1
        rrc_failure = random.random() < 0.15

        # -----------------------------
        # DETERMINE CALL OUTCOME (DEPENDENT)
        # -----------------------------
        if bgp_down or packet_loss:
            flow_type = "TIMEOUT"
        elif latency_issue:
            flow_type = "SERVER_ERROR"
        elif rrc_failure:
            flow_type = "BUSY"
        else:
            flow_type = "SUCCESS"

        # -----------------------------
        # SIP FLOW
        # -----------------------------
        sip_logs.append([call_id, t, "INVITE"])

        t += timedelta(milliseconds=100)
        sip_logs.append([call_id, t, "100 Trying"])

        if flow_type == "SUCCESS":
            sip_logs.append([call_id, t, "180 Ringing"])
            sip_logs.append([call_id, t, "200 OK"])

        elif flow_type == "TIMEOUT":
            t += timedelta(seconds=2)
            sip_logs.append([call_id, t, "408 Timeout"])

        elif flow_type == "BUSY":
            sip_logs.append([call_id, t, "486 Busy Here"])

        elif flow_type == "SERVER_ERROR":
            sip_logs.append([call_id, t, "500 Server Error"])

        # -----------------------------
        # RRC FLOW
        # -----------------------------
        rrc_logs.append([call_id, t, "RRC_SETUP_REQUEST"])

        if rrc_failure:
            rrc_logs.append([call_id, t, "RRC_SETUP_FAILURE"])
        else:
            rrc_logs.append([call_id, t, "RRC_SETUP_COMPLETE"])

        # HO events
        if random.random() < 0.3:
            rrc_logs.append([call_id, t, "HO_ATTEMPT"])

            if packet_loss or latency_issue:
                rrc_logs.append([call_id, t, "HO_FAILURE"])
            else:
                rrc_logs.append([call_id, t, "HO_SUCCESS"])

        # -----------------------------
        # CSR EVENTS (CORRELATED)
        # -----------------------------
        if bgp_down:
            csr_logs.append([t, "ERROR", "BGP_DOWN"])

        if packet_loss:
            csr_logs.append([t, "WARN", "HIGH_PACKET_LOSS"])

        if latency_issue:
            csr_logs.append([t, "WARN", "HIGH_LATENCY"])

        if random.random() < 0.05:
            csr_logs.append([t, "CRITICAL", "IF_DOWN"])

    sip_df = pd.DataFrame(sip_logs, columns=["call_id", "timestamp", "sip_message"])
    rrc_df = pd.DataFrame(rrc_logs, columns=["call_id", "timestamp", "rrc_event"])
    csr_df = pd.DataFrame(csr_logs, columns=["timestamp", "level", "event"])

    sip_df.to_csv("data/raw/sip_logs.csv", index=False)
    rrc_df.to_csv("data/raw/rrc_logs.csv", index=False)
    csr_df.to_csv("data/raw/csr_logs.csv", index=False)

    print("✅ Correlated logs generated!")


if __name__ == "__main__":
    generate_all()