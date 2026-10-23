"""
Tests for QuantumShield Qiskit Simulation Engine
Verifies circuit execution, Eve disabled (0% error), Eve enabled (~25% error),
noise simulation, repeated Monte Carlo experiments, and reproducibility.
"""

import pytest
import numpy as np
from src.simulation import (
    run_bb84_simulation,
    simulate_single_qubit_transmission,
    run_repeated_experiments,
)
from src.protocol import BASIS_X, BASIS_Z
from src.utils import privacy_amplification_demo


class TestSimulationExecution:
    """Verifies quantum circuit execution with and without Eve."""

    def test_eve_disabled_zero_qber(self):
        """Without Eve and in ideal noiseless simulation, QBER must strictly be 0.0."""
        result = run_bb84_simulation(n_qubits=100, eve_present=False, noise_rate=0.0, seed=42)

        assert result.eve_enabled is False
        assert result.eve_bases is None
        assert result.eve_measured_bits is None
        assert result.total_qubits == 100
        assert result.sifted_bits_count > 0

        # Every sifted bit where Alice and Bob used the same basis must match!
        assert result.alice_sifted_key == result.bob_sifted_key
        assert result.sifted_mismatch_count == 0
        assert result.qber == 0.0
        assert result.agreement_rate == 100.0

    def test_eve_enabled_simulation_structure(self):
        """When Eve is enabled, Eve data fields must be populated and transmission records valid."""
        result = run_bb84_simulation(n_qubits=50, eve_present=True, seed=12345)

        assert result.eve_enabled is True
        assert result.eve_bases is not None
        assert len(result.eve_bases) == 50
        assert result.eve_measured_bits is not None
        assert len(result.eve_measured_bits) == 50
        assert len(result.transmissions) == 50

        # Check transmission records
        for tx in result.transmissions:
            assert tx.eve_present is True
            assert tx.eve_basis in (BASIS_Z, BASIS_X)
            assert tx.eve_measured_bit in (0, 1)

    def test_eve_enabled_error_rate_statistical_range(self):
        """
        With intercept-resend attack on a statistically adequate sample (400 qubits),
        QBER must be significantly non-zero and fall within normal statistical fluctuations
        around the theoretical 25% (e.g. 15% - 35%).
        """
        result = run_bb84_simulation(n_qubits=400, eve_present=True, seed=999)
        assert result.sifted_bits_count > 100
        # QBER should fluctuate around 25%
        assert 0.15 <= result.qber <= 0.35, f"Observed QBER {result.qber} outside expected range [0.15, 0.35]"
        assert result.eavesdropping_detected is True

    def test_simulation_reproducibility(self):
        """Two runs with the same seed must produce identical results."""
        run1 = run_bb84_simulation(n_qubits=60, eve_present=True, seed=777)
        run2 = run_bb84_simulation(n_qubits=60, eve_present=True, seed=777)

        assert run1.alice_bits == run2.alice_bits
        assert run1.alice_bases == run2.alice_bases
        assert run1.bob_bases == run2.bob_bases
        assert run1.bob_measured_bits == run2.bob_measured_bits
        assert run1.eve_bases == run2.eve_bases
        assert run1.eve_measured_bits == run2.eve_measured_bits
        assert run1.qber == run2.qber

    def test_single_qubit_deterministic_matching(self):
        """Single qubit with same basis without Eve must match deterministically."""
        rng = np.random.default_rng(101)
        # Z basis, bit 0
        b_bit, e_bit = simulate_single_qubit_transmission(0, BASIS_Z, BASIS_Z, False, None, 0.0, rng)
        assert b_bit == 0
        assert e_bit is None

        # Z basis, bit 1
        b_bit, _ = simulate_single_qubit_transmission(1, BASIS_Z, BASIS_Z, False, None, 0.0, rng)
        assert b_bit == 1

        # X basis, bit 0
        b_bit, _ = simulate_single_qubit_transmission(0, BASIS_X, BASIS_X, False, None, 0.0, rng)
        assert b_bit == 0

        # X basis, bit 1
        b_bit, _ = simulate_single_qubit_transmission(1, BASIS_X, BASIS_X, False, None, 0.0, rng)
        assert b_bit == 1

    def test_noise_simulation_generates_errors_without_eve(self):
        """Configurable noise must generate errors even when Eve is disabled (Enhancement 3)."""
        result = run_bb84_simulation(n_qubits=300, eve_present=False, noise_rate=0.20, seed=42)
        assert result.eve_enabled is False
        # Noise should induce non-zero QBER
        assert result.sifted_mismatch_count > 0
        assert result.qber > 0.0

    def test_repeated_experiments_aggregation(self):
        """Repeated Monte Carlo experiment returns aggregated statistics (Enhancement 2)."""
        trials_data = run_repeated_experiments(
            n_trials=5, n_qubits_per_trial=100, eve_present=True, base_seed=123
        )
        assert trials_data["n_trials"] == 5
        assert len(trials_data["trial_results"]) == 5
        assert 0.10 <= (trials_data["mean_qber"] / 100.0) <= 0.40
        assert trials_data["std_qber"] >= 0.0

    def test_privacy_amplification_compression(self):
        """Privacy amplification compresses N bits into M bits (Enhancement 6)."""
        key_input = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1]
        compressed_key, msg = privacy_amplification_demo(key_input, target_length=6, seed=42)
        assert len(compressed_key) == 6
        assert all(b in (0, 1) for b in compressed_key)
        assert "Leftover Hash Lemma" in msg
