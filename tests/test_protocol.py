"""
Tests for QuantumShield BB84 Protocol Logic (Unit tests)
Verifies state encoding, basis generation, key sifting, and seed reproducibility.
"""

import pytest
from src.protocol import (
    BASIS_X,
    BASIS_Z,
    generate_alice_data,
    generate_bob_bases,
    generate_eve_bases,
    sift_keys,
)
from src.circuits import build_alice_preparation_circuit


class TestProtocolEncoding:
    """Tests for Alice state preparation and encoding circuits."""

    def test_z_basis_encoding_bit_0(self):
        """Bit 0 in Z basis must prepare |0> state."""
        qc = build_alice_preparation_circuit(bit=0, basis=BASIS_Z)
        assert qc.num_qubits == 1
        # In |0>, no X gate should be applied
        op_names = [inst.operation.name for inst in qc.data]
        assert "x" not in op_names
        assert "h" not in op_names

    def test_z_basis_encoding_bit_1(self):
        """Bit 1 in Z basis must apply X gate to prepare |1> state."""
        qc = build_alice_preparation_circuit(bit=1, basis=BASIS_Z)
        assert qc.num_qubits == 1
        op_names = [inst.operation.name for inst in qc.data]
        assert "x" in op_names
        assert "h" not in op_names

    def test_x_basis_encoding_bit_0(self):
        """Bit 0 in X basis must apply H gate to prepare |+> state."""
        qc = build_alice_preparation_circuit(bit=0, basis=BASIS_X)
        assert qc.num_qubits == 1
        op_names = [inst.operation.name for inst in qc.data]
        assert "h" in op_names
        assert "x" not in op_names

    def test_x_basis_encoding_bit_1(self):
        """Bit 1 in X basis must apply X followed by H to prepare |-> state."""
        qc = build_alice_preparation_circuit(bit=1, basis=BASIS_X)
        assert qc.num_qubits == 1
        op_names = [inst.operation.name for inst in qc.data]
        assert "x" in op_names
        assert "h" in op_names
        # Check order: x gate before h gate
        assert op_names == ["x", "h"]

    def test_invalid_basis_raises_error(self):
        """Invalid basis string should raise ValueError."""
        with pytest.raises(ValueError):
            build_alice_preparation_circuit(bit=0, basis="Y")


class TestSiftingLogic:
    """Tests for classical sifting and basis matching."""

    def test_basis_matching_logic(self):
        """Positions where bases match should be retained in sifted key."""
        alice_bits = [1, 0, 1, 0]
        alice_bases = ["Z", "X", "Z", "X"]
        bob_bases = ["Z", "Z", "Z", "X"]
        bob_bits = [1, 1, 1, 0]

        indices, a_sifted, b_sifted = sift_keys(alice_bits, alice_bases, bob_bases, bob_bits)

        # Positions 0, 2, 3 have matching bases ("Z"=="Z", "Z"=="Z", "X"=="X")
        assert indices == [0, 2, 3]
        assert a_sifted == [1, 1, 0]
        assert b_sifted == [1, 1, 0]

    def test_basis_mismatching_logic(self):
        """Positions where bases differ must be discarded."""
        alice_bits = [1, 0]
        alice_bases = ["Z", "X"]
        bob_bases = ["X", "Z"]
        bob_bits = [0, 1]

        indices, a_sifted, b_sifted = sift_keys(alice_bits, alice_bases, bob_bases, bob_bits)
        assert len(indices) == 0
        assert len(a_sifted) == 0
        assert len(b_sifted) == 0

    def test_reproducibility_with_seed(self):
        """Fixed random seed must yield identical bit and basis sequences."""
        bits1, bases1 = generate_alice_data(50, seed=42)
        bits2, bases2 = generate_alice_data(50, seed=42)
        assert bits1 == bits2
        assert bases1 == bases2

        bob1 = generate_bob_bases(50, seed=123)
        bob2 = generate_bob_bases(50, seed=123)
        assert bob1 == bob2

    def test_invalid_input_lengths_raise_error(self):
        """Mismatched sequence lengths in sifting must raise ValueError."""
        with pytest.raises(ValueError):
            sift_keys([1, 0], ["Z"], ["Z"], [1])
