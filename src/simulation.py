"""
QuantumShield - Simulation Engine
Executes genuine Qiskit circuits for BB84 quantum state preparation and measurements.
Uses Qiskit quantum_info Statevector and primitives to accurately simulate quantum evolution.
Includes configurable channel noise and repeated Monte Carlo experiment batching.
"""

from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from src.protocol import (
    BASIS_X,
    BASIS_Z,
    ProtocolResult,
    QubitTransmission,
    generate_alice_data,
    generate_bob_bases,
    generate_eve_bases,
    sift_keys,
)
from src.circuits import build_alice_preparation_circuit


def simulate_single_qubit_transmission(
    alice_bit: int,
    alice_basis: str,
    bob_basis: str,
    eve_present: bool = False,
    eve_basis: Optional[str] = None,
    noise_rate: float = 0.0,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[int, Optional[int]]:
    """
    Simulates a single qubit transmission through Alice -> [Eve] -> [Noise] -> Bob using Qiskit Statevector.
    
    Args:
        alice_bit: Bit chosen by Alice (0 or 1).
        alice_basis: Basis chosen by Alice ('Z' or 'X').
        bob_basis: Basis chosen by Bob ('Z' or 'X').
        eve_present: Whether Eve performs intercept-resend attack.
        eve_basis: Eve's measurement basis if present.
        noise_rate: Probability of channel bit-flip/depolarization noise [0.0, 0.5].
        rng: NumPy random generator.
        
    Returns:
        Tuple of (bob_measured_bit, eve_measured_bit)
    """
    if rng is None:
        rng = np.random.default_rng()

    # 1. Alice prepares the quantum state via Qiskit QuantumCircuit
    prep_circuit = build_alice_preparation_circuit(alice_bit, alice_basis)
    state = Statevector.from_instruction(prep_circuit)
    
    eve_measured_bit = None

    # 2. Optional Eve Intercept-Resend attack
    if eve_present:
        if eve_basis is None:
            raise ValueError("eve_basis required when eve_present is True")
        
        # Eve measures the state in eve_basis:
        # If measuring in X basis, apply Hadamard before measuring in computational basis
        eve_meas_circuit = QuantumCircuit(1)
        if eve_basis == BASIS_X:
            eve_meas_circuit.h(0)
        eve_state = state.evolve(eve_meas_circuit)
        
        # Calculate probabilities from Qiskit Statevector
        probs = np.abs(eve_state.probabilities())
        probs = probs / np.sum(probs)  # normalize
        eve_measured_bit = int(rng.choice([0, 1], p=probs))
        
        # Eve creates a replacement qubit in her measured state and basis
        resend_circuit = build_alice_preparation_circuit(eve_measured_bit, eve_basis)
        state = Statevector.from_instruction(resend_circuit)

    # 3. Optional Quantum Channel Physical Noise (Depolarizing / Phase-Bit Flip)
    if noise_rate > 0.0:
        if rng.random() < noise_rate:
            # Apply random Pauli noise (X, Y, or Z gate)
            noise_circuit = QuantumCircuit(1)
            noise_gate = rng.choice(['x', 'y', 'z'])
            if noise_gate == 'x':
                noise_circuit.x(0)
            elif noise_gate == 'y':
                noise_circuit.y(0)
            else:
                noise_circuit.z(0)
            state = state.evolve(noise_circuit)

    # 4. Bob measures the received state in bob_basis
    bob_meas_circuit = QuantumCircuit(1)
    if bob_basis == BASIS_X:
        bob_meas_circuit.h(0)
    bob_state = state.evolve(bob_meas_circuit)
    bob_probs = np.abs(bob_state.probabilities())
    bob_probs = bob_probs / np.sum(bob_probs)
    bob_measured_bit = int(rng.choice([0, 1], p=bob_probs))

    return bob_measured_bit, eve_measured_bit


def run_bb84_simulation(
    n_qubits: int = 100,
    eve_present: bool = False,
    noise_rate: float = 0.0,
    seed: Optional[int] = None,
    qber_threshold: float = 0.05,
) -> ProtocolResult:
    """
    Executes a complete BB84 simulation using Qiskit circuits for state preparation and measurement.
    
    Args:
        n_qubits: Number of transmitted qubits (default 100).
        eve_present: Whether an eavesdropper intercepts qubits.
        noise_rate: Physical channel noise probability.
        seed: Random seed for reproducibility.
        qber_threshold: Educational alert threshold for QBER breach (default 0.05).
        
    Returns:
        ProtocolResult containing full transmission log, sifted keys, and QBER metrics.
    """
    if n_qubits <= 0:
        raise ValueError("Number of qubits must be strictly positive.")
    if not (0.0 <= noise_rate <= 0.5):
        raise ValueError("noise_rate must be between 0.0 and 0.5.")

    rng = np.random.default_rng(seed)
    
    # Generate Alice's raw bits and bases
    alice_bits, alice_bases = generate_alice_data(n_qubits, seed=rng.integers(0, 2**31 - 1))
    bob_bases = generate_bob_bases(n_qubits, seed=rng.integers(0, 2**31 - 1))
    
    eve_bases = None
    if eve_present:
        eve_bases = generate_eve_bases(n_qubits, seed=rng.integers(0, 2**31 - 1))

    transmissions: List[QubitTransmission] = []
    bob_measured_bits: List[int] = []
    eve_measured_bits: Optional[List[int]] = [] if eve_present else None

    # Transmit each qubit through Qiskit quantum circuits
    for i in range(n_qubits):
        e_basis = eve_bases[i] if eve_present and eve_bases is not None else None
        b_bit, e_bit = simulate_single_qubit_transmission(
            alice_bit=alice_bits[i],
            alice_basis=alice_bases[i],
            bob_basis=bob_bases[i],
            eve_present=eve_present,
            eve_basis=e_basis,
            noise_rate=noise_rate,
            rng=rng,
        )
        bob_measured_bits.append(b_bit)
        if eve_present and eve_measured_bits is not None and e_bit is not None:
            eve_measured_bits.append(e_bit)

        basis_match = (alice_bases[i] == bob_bases[i])
        bit_match = (alice_bits[i] == b_bit)

        transmissions.append(
            QubitTransmission(
                index=i,
                alice_bit=alice_bits[i],
                alice_basis=alice_bases[i],
                bob_basis=bob_bases[i],
                bob_measured_bit=b_bit,
                eve_present=eve_present,
                eve_basis=e_basis,
                eve_measured_bit=e_bit,
                basis_matched=basis_match,
                bit_matched=bit_match,
            )
        )

    # Perform classical sifting
    sifted_indices, alice_sifted_key, bob_sifted_key = sift_keys(
        alice_bits, alice_bases, bob_bases, bob_measured_bits
    )

    sifted_count = len(sifted_indices)
    discarded_count = n_qubits - sifted_count

    # Calculate errors among sifted bits
    if sifted_count > 0:
        sifted_mismatches = sum(
            1 for a_k, b_k in zip(alice_sifted_key, bob_sifted_key) if a_k != b_k
        )
        sifted_agreements = sifted_count - sifted_mismatches
        qber = sifted_mismatches / sifted_count
        agreement_rate = (sifted_agreements / sifted_count) * 100.0
    else:
        sifted_mismatches = 0
        sifted_agreements = 0
        qber = 0.0
        agreement_rate = 0.0

    basis_match_rate = (sifted_count / n_qubits) * 100.0 if n_qubits > 0 else 0.0
    
    # Eavesdropping detection threshold
    eavesdropping_detected = qber > qber_threshold

    return ProtocolResult(
        total_qubits=n_qubits,
        eve_enabled=eve_present,
        transmissions=transmissions,
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_measured_bits=bob_measured_bits,
        eve_bases=eve_bases,
        eve_measured_bits=eve_measured_bits,
        sifted_indices=sifted_indices,
        alice_sifted_key=alice_sifted_key,
        bob_sifted_key=bob_sifted_key,
        sifted_bits_count=sifted_count,
        discarded_bits_count=discarded_count,
        sifted_agreement_count=sifted_agreements,
        sifted_mismatch_count=sifted_mismatches,
        qber=qber,
        basis_match_rate=basis_match_rate,
        agreement_rate=agreement_rate,
        eavesdropping_detected=eavesdropping_detected,
        random_seed=seed,
    )


def run_repeated_experiments(
    n_trials: int = 10,
    n_qubits_per_trial: int = 100,
    eve_present: bool = False,
    noise_rate: float = 0.0,
    base_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Executes repeated independent trials to observe statistical convergence and finite-sample variance.
    
    Args:
        n_trials: Number of independent simulation runs (e.g. 10).
        n_qubits_per_trial: Qubits transmitted per trial.
        eve_present: Whether Eve is active.
        noise_rate: Channel noise level.
        base_seed: Starting seed.
        
    Returns:
        Dict with mean QBER, std deviation, min/max, individual trial results, and theoretical comparison.
    """
    if n_trials <= 0:
        raise ValueError("Number of trials must be greater than zero.")

    qber_values = []
    sifted_counts = []
    trial_results = []
    
    rng = np.random.default_rng(base_seed)

    for trial_idx in range(n_trials):
        trial_seed = int(rng.integers(0, 2**31 - 1)) if base_seed is not None else None
        res = run_bb84_simulation(
            n_qubits=n_qubits_per_trial,
            eve_present=eve_present,
            noise_rate=noise_rate,
            seed=trial_seed,
        )
        qber_values.append(res.qber * 100.0)
        sifted_counts.append(res.sifted_bits_count)
        trial_results.append({
            "Trial": trial_idx + 1,
            "Transmitted Qubits": res.total_qubits,
            "Sifted Bits": res.sifted_bits_count,
            "Errors": res.sifted_mismatch_count,
            "QBER (%)": res.qber * 100.0,
            "Breached": res.eavesdropping_detected,
        })

    mean_qber = float(np.mean(qber_values))
    std_qber = float(np.std(qber_values))
    min_qber = float(np.min(qber_values))
    max_qber = float(np.max(qber_values))

    # Theoretical baseline
    theo_base = 25.0 if eve_present else 0.0
    theo_effective = theo_base + (noise_rate * 50.0 if not eve_present else 0.0)

    return {
        "n_trials": n_trials,
        "n_qubits_per_trial": n_qubits_per_trial,
        "eve_present": eve_present,
        "noise_rate": noise_rate,
        "mean_qber": mean_qber,
        "std_qber": std_qber,
        "min_qber": min_qber,
        "max_qber": max_qber,
        "theoretical_qber": theo_effective,
        "qber_values": qber_values,
        "sifted_counts": sifted_counts,
        "trial_results": trial_results,
    }
