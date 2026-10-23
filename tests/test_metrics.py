"""
Tests for QuantumBit Error Rate (QBER) and statistical metrics
Verifies accurate error rate calculations, zero-sifted-bits edge cases, and confidence intervals.
"""

import pytest
from src.metrics import (
    calculate_qber,
    calculate_wilson_confidence_interval,
    analyze_protocol_performance,
)


class TestMetricsCalculation:
    """Verifies numerical correctness of QBER and confidence intervals."""

    def test_qber_exact_values(self):
        """Calculates exact QBER for controlled bit sequences."""
        # 1 mismatch out of 4 -> 25%
        assert calculate_qber([0, 1, 0, 1], [0, 1, 0, 0]) == 0.25

        # 0 mismatches out of 5 -> 0%
        assert calculate_qber([1, 1, 0, 0, 1], [1, 1, 0, 0, 1]) == 0.0

        # All mismatched -> 100%
        assert calculate_qber([0, 0, 0], [1, 1, 1]) == 1.0

    def test_zero_sifted_bits_safe_handling(self):
        """Zero sifted bits should return 0.0 and avoid ZeroDivisionError."""
        qber = calculate_qber([], [])
        assert qber == 0.0

    def test_mismatched_key_lengths_raise_error(self):
        """Keys of differing lengths must raise ValueError."""
        with pytest.raises(ValueError):
            calculate_qber([1, 0], [1])

    def test_wilson_confidence_interval_bounds(self):
        """Confidence interval bounds must remain valid probabilities [0, 1]."""
        lower, upper = calculate_wilson_confidence_interval(errors=25, total=100)
        assert 0.0 <= lower <= 0.25 <= upper <= 1.0
        assert lower < upper

    def test_zero_total_confidence_interval(self):
        """Zero count should return (0.0, 0.0)."""
        lower, upper = calculate_wilson_confidence_interval(errors=0, total=0)
        assert lower == 0.0
        assert upper == 0.0

    def test_analyze_protocol_performance_structure(self):
        """Performance summary must report expected fields and thresholds."""
        stats = analyze_protocol_performance(
            total_qubits=200, sifted_bits=100, errors=24, eve_present=True
        )
        assert stats["qber"] == 0.24
        assert stats["theoretical_qber"] == 0.25
        assert stats["security_breached"] is True
        assert "ci_lower_percentage" in stats
        assert "ci_upper_percentage" in stats
