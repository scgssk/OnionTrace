def confidence_label(confidence: float) -> str:
    if confidence >= 0.75:
        return "HIGH"
    elif confidence >= 0.4:
        return "MEDIUM"
    return "LOW"
