
from disclosure_snippets import DISCLOSURE_SNIPPETS
import re

def extract_signals(snippet: str) -> dict:
    """
    Extracts risk flags, hedging detection, and sentiment from a disclosure snippet.
    (Mock mode: uses keyword/regex rules).
    """
    risk_flags = []
    hedging_detected = False
    sentiment = "neutral"

    # Risk Flags
    if re.search(r'litigation|regulatory|customer concentration', snippet, re.IGNORECASE):
        if 'litigation' in snippet.lower():
            risk_flags.append('litigation_risk')
        if 'regulatory' in snippet.lower():
            risk_flags.append('regulatory_risk')
        if 'customer concentration' in snippet.lower() or 'top three customers' in snippet.lower():
            risk_flags.append('customer_concentration_risk')

    # Hedging Detection
    if re.search(r'assuming|cautiously|visibility', snippet, re.IGNORECASE):
        hedging_detected = True

    # Sentiment Classification
    if re.search(r'confident|approved', snippet, re.IGNORECASE):
        sentiment = "confident"
    elif hedging_detected:
        sentiment = "cautious"

    return {"risk_flags": risk_flags, "hedging_detected": hedging_detected, "sentiment": sentiment}

# Run against all 6 committed disclosure snippets and record the output
if __name__ == '__main__':
    print("--- Disclosure Snippet Analysis ---")
    for i, snippet in enumerate(DISCLOSURE_SNIPPETS):
        signals = extract_signals(snippet)
        print(f"\nSnippet {i+1} ({snippet.split(':')[0]}):")
        print(f"  Snippet: {snippet}")
        print(f"  Signals: {signals}")
