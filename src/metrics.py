"""
QuantumShield - Metrics & Statistical Analysis Module
Computes QBER, confidence intervals, basis matching efficiency, and compares empirical vs theoretical bounds.
"""

from typing import Dict, List, Tuple
import math


THEORETICAL_QBER_NO_EVE = 0.0
THEORETICAL_QBER_INTERCEPT_RESEND = 0.25
STANDARD_QBER_THRESHOLD = 0.11  # 11% Shor-Preskill / BB84 security limit


def calculate_qber(alice_sifted: List[int], bob_sifted: List[int]) -> float:
    """
    Calculates the Quantum Bit Error Rate (QBER).
    
    QBER = (Number of mismatched sifted bits) / (Total sifted bits)
    
    Returns 0.0 if sifted key is empty.
    """
    if len(alice_sifted) != len(bob_sifted):
        raise ValueError("Alice and Bob sifted keys must have identical lengths.")
    
    total_sifted = len(alice_sifted)
    if total_sifted == 0:
        return 0.0

    mismatches = sum(1 for a, b in zip(alice_sifted, bob_sifted) if a != b)
    return mismatches / total_sifted


def calculate_wilson_confidence_interval(
    errors: int, total: int, confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Computes Wilson score interval for binomial proportion (QBER).
    Appropriate for small and large sample sizes.
    """
    if total == 0:
        return 0.0, 0.0
        
    z = 1.95996  # For 95% confidence
    if confidence == 0.99:
        z = 2.57583
    elif confidence == 0.90:
        z = 1.64485

    p_hat = errors / total
    denom = 1 + (z**2) / total
    center = (p_hat + (z**2) / (2 * total)) / denom
    margin = (z / denom) * math.sqrt((p_hat * (1 - p_hat) / total) + ((z**2) / (4 * total**2)))

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower, upper


def analyze_protocol_performance(
    total_qubits: int,
    sifted_bits: int,
    errors: int,
    eve_present: bool,
) -> Dict[str, float]:
    """
    Generates a full statistical performance breakdown.
    """
    qber = (errors / sifted_bits) if sifted_bits > 0 else 0.0
    basis_efficiency = (sifted_bits / total_qubits * 100.0) if total_qubits > 0 else 0.0
    theoretical_qber = THEORETICAL_QBER_INTERCEPT_RESEND if eve_present else THEORETICAL_QBER_NO_EVE
    deviation = abs(qber - theoretical_qber)
    lower_ci, upper_ci = calculate_wilson_confidence_interval(errors, sifted_bits)

    return {
        "qber": qber,
        "qber_percentage": qber * 100.0,
        "theoretical_qber": theoretical_qber,
        "theoretical_qber_percentage": theoretical_qber * 100.0,
        "deviation": deviation,
        "basis_efficiency_percentage": basis_efficiency,
        "ci_lower_percentage": lower_ci * 100.0,
        "ci_upper_percentage": upper_ci * 100.0,
        "threshold_percentage": STANDARD_QBER_THRESHOLD * 100.0,
        "security_breached": qber > 0.05,
    }
