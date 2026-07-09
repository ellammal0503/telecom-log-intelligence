def get_top_reasons(row):
    """
    Return top 3 reasons ranked by severity score
    """

    reasons = []

    # -----------------------------
    # SCORING LOGIC
    # -----------------------------
    if row.get("bgp_down", 0) > 0:
        reasons.append(("Backhaul Failure (BGP Down)", "HIGH", 10))

    if row.get("packet_loss", 0) > 1:
        score = min(8, row.get("packet_loss") * 2)
        reasons.append(("High Packet Loss", "HIGH", score))

    if row.get("latency", 0) > 1:
        score = min(6, row.get("latency"))
        reasons.append(("High Latency", "MEDIUM", score))

    if row.get("rrc_fail", 0) > 0:
        reasons.append(("RRC Setup Failure", "MEDIUM", 5))

    if row.get("ho_fail", 0) > 0:
        reasons.append(("Handover Failure", "MEDIUM", 4))

    if row.get("server_error", 0) > 0:
        reasons.append(("Server Error (5xx)", "MEDIUM", 4))

    if row.get("busy", 0) > 0:
        reasons.append(("User Busy", "LOW", 2))

    # -----------------------------
    # SORT & PICK TOP 3
    # -----------------------------
    reasons = sorted(reasons, key=lambda x: x[2], reverse=True)

    top3 = reasons[:3]

    # Convert to JSON-friendly format
    return [
        {"reason": r[0], "severity": r[1], "score": r[2]}
        for r in top3
    ]