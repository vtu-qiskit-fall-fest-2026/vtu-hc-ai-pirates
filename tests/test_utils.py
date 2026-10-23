"""
Tests for QuantumShield Utility Functions (tests/test_utils.py)
Verifies DataFrame conversion, CSV export, One-Time Pad encryption, and Privacy Amplification.
"""

import pytest
import io
import pandas as pd
from src.simulation import run_bb84_simulation
from src.utils import (
    result_to_dataframe,
    bits_to_string,
    one_time_pad_xor,
    privacy_amplification_demo,
)


class TestUtils:
    """Verifies helper functions, table exporters, and OTP encryption."""

    def test_result_to_dataframe_columns_and_rows(self):
        """Transmission log DataFrame must have all expected columns and row count."""
        sim = run_bb84_simulation(n_qubits=20, eve_present=True, seed=42)
        df = result_to_dataframe(sim)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 20
        expected_cols = [
            "Qubit Index",
            "Alice Bit",
            "Alice Basis",
            "Eve Present",
            "Eve Basis",
            "Eve Bit",
            "Bob Basis",
            "Bob Bit",
            "Basis Match",
            "Bit Agreement",
            "Sifted",
        ]
        for col in expected_cols:
            assert col in df.columns

    def test_dataframe_csv_export(self):
        """DataFrame must export to a valid CSV format without errors."""
        sim = run_bb84_simulation(n_qubits=15, eve_present=False, seed=99)
        df = result_to_dataframe(sim)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_text = csv_buffer.getvalue()

        assert "Qubit Index,Alice Bit,Alice Basis" in csv_text
        assert len(csv_text.strip().split("\n")) == 16  # 1 header + 15 rows

    def test_bits_to_string_formatting(self):
        """Verifies binary formatting and truncation indicator."""
        bits = [1, 0, 1, 1, 0]
        assert bits_to_string(bits) == "10110"

        long_bits = [1] * 100
        formatted = bits_to_string(long_bits, max_length=10)
        assert formatted.startswith("1111111111... (100 bits total)")

    def test_one_time_pad_encryption_decryption_match(self):
        """OTP encryption with identical keys must decrypt to original message."""
        msg = "QISKIT"
        # 6 chars * 8 bits = 48 bits
        key = [1, 0, 1, 0] * 12
        res = one_time_pad_xor(msg, key)

        assert res["success"] is True
        assert res["decrypted_text"] == msg
        assert res["required_bits"] == 48

    def test_one_time_pad_insufficient_key_length(self):
        """OTP must return error when sifted key is shorter than message."""
        msg = "VERY_LONG_SECRET_MESSAGE"
        short_key = [1, 0, 1]
        res = one_time_pad_xor(msg, short_key)

        assert res["success"] is False
        assert "shorter than required" in res["error"]

    def test_privacy_amplification_hashing(self):
        """Privacy amplification must compress N bits to M bits."""
        sifted = [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1]
        compressed, msg = privacy_amplification_demo(sifted, target_length=8, seed=123)

        assert len(compressed) == 8
        assert all(b in (0, 1) for b in compressed)
        assert "Leftover Hash Lemma" in msg
