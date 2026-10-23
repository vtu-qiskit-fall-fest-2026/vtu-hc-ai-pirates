"""
QuantumShield - BB84 Protocol Module
Defines quantum state representations, basis choices, key sifting, and protocol structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


BASIS_Z = "Z"  # Computational basis: {|0>, |1>}
BASIS_X = "X"  # Hadamard / diagonal basis: {|+>, |->}
VALID_BASES = (BASIS_Z, BASIS_X)


@dataclass
class QubitTransmission:
    """Represents a single transmitted qubit through the BB84 channel."""
    index: int
    alice_bit: int
    alice_basis: str
    bob_basis: str
    bob_measured_bit: int
    eve_present: bool = False
    eve_basis: Optional[str] = None
    eve_measured_bit: Optional[int] = None
    basis_matched: bool = False
    bit_matched: bool = False


@dataclass
class ProtocolResult:
    """Holds comprehensive results of a BB84 simulation run."""
    total_qubits: int
    eve_enabled: bool
    transmissions: List[QubitTransmission]
    alice_bits: List[int]
    alice_bases: List[str]
    bob_bases: List[str]
    bob_measured_bits: List[int]
    eve_bases: Optional[List[str]] = None
    eve_measured_bits: Optional[List[int]] = None
    
    # Sifted results
    sifted_indices: List[int] = field(default_factory=list)
    alice_sifted_key: List[int] = field(default_factory=list)
    bob_sifted_key: List[int] = field(default_factory=list)
    
    # Metrics
    sifted_bits_count: int = 0
    discarded_bits_count: int = 0
    sifted_agreement_count: int = 0
    sifted_mismatch_count: int = 0
    qber: float = 0.0
    basis_match_rate: float = 0.0
    agreement_rate: float = 0.0
    eavesdropping_detected: bool = False
    random_seed: Optional[int] = None


def generate_alice_data(n_qubits: int, seed: Optional[int] = None) -> Tuple[List[int], List[str]]:
    """
    Generate Alice's random secret bits and random measurement/encoding bases.
    
    Args:
        n_qubits: Number of qubits to generate.
        seed: Optional random seed for reproducibility.
        
    Returns:
        Tuple of (alice_bits, alice_bases)
    """
    if n_qubits <= 0:
        raise ValueError("Number of qubits must be greater than 0.")
        
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=n_qubits).tolist()
    bases = [BASIS_Z if b == 0 else BASIS_X for b in rng.integers(0, 2, size=n_qubits)]
    return bits, bases


def generate_bob_bases(n_qubits: int, seed: Optional[int] = None) -> List[str]:
    """
    Generate Bob's independent random measurement bases.
    
    Args:
        n_qubits: Number of qubits to measure.
        seed: Optional random seed.
        
    Returns:
        List of bases ('Z' or 'X')
    """
    if n_qubits <= 0:
        raise ValueError("Number of qubits must be greater than 0.")
        
    rng = np.random.default_rng(seed)
    return [BASIS_Z if b == 0 else BASIS_X for b in rng.integers(0, 2, size=n_qubits)]


def generate_eve_bases(n_qubits: int, seed: Optional[int] = None) -> List[str]:
    """
    Generate Eve's independent random bases for intercept-resend attack.
    
    Args:
        n_qubits: Number of qubits to intercept.
        seed: Optional random seed.
        
    Returns:
        List of bases ('Z' or 'X')
    """
    if n_qubits <= 0:
        raise ValueError("Number of qubits must be greater than 0.")
        
    rng = np.random.default_rng(seed)
    return [BASIS_Z if b == 0 else BASIS_X for b in rng.integers(0, 2, size=n_qubits)]


def sift_keys(
    alice_bits: List[int],
    alice_bases: List[str],
    bob_bases: List[str],
    bob_measured_bits: List[int],
) -> Tuple[List[int], List[int], List[int]]:
    """
    Perform classical sifting stage of BB84.
    Keeps only bit positions where Alice and Bob used matching bases.
    
    Args:
        alice_bits: Raw bits chosen by Alice.
        alice_bases: Bases used by Alice to prepare states.
        bob_bases: Bases used by Bob to measure states.
        bob_measured_bits: Measurement outcomes obtained by Bob.
        
    Returns:
        Tuple of (sifted_indices, alice_sifted_key, bob_sifted_key)
    """
    if len(alice_bits) != len(alice_bases) or len(bob_bases) != len(bob_measured_bits):
        raise ValueError("Mismatched list lengths in sifting input.")
    if len(alice_bits) != len(bob_bases):
        raise ValueError("Alice and Bob sequence lengths must match.")

    sifted_indices: List[int] = []
    alice_sifted: List[int] = []
    bob_sifted: List[int] = []

    for idx, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases)):
        if a_basis == b_basis:
            sifted_indices.append(idx)
            alice_sifted.append(alice_bits[idx])
            bob_sifted.append(bob_measured_bits[idx])

    return sifted_indices, alice_sifted, bob_sifted
