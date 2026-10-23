"""
QuantumShield - Qiskit Circuit Builders
Constructs authentic Qiskit QuantumCircuit instances for Alice preparation, Eve intercept-resend, and Bob measurement.
"""

from typing import Optional
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from src.protocol import BASIS_X, BASIS_Z


def build_alice_preparation_circuit(bit: int, basis: str) -> QuantumCircuit:
    """
    Builds Alice's quantum state preparation circuit.
    
    Encoding specification:
    - Z basis, bit 0: |0> (Identity / no gate)
    - Z basis, bit 1: |1> (X gate)
    - X basis, bit 0: |+> (H gate)
    - X basis, bit 1: |-> (X gate followed by H gate)
    
    Args:
        bit: Secret bit (0 or 1).
        basis: Basis ('Z' or 'X').
        
    Returns:
        QuantumCircuit of 1 qubit prepared in the target quantum state.
    """
    qr = QuantumRegister(1, name="q")
    qc = QuantumCircuit(qr, name=f"Alice_prep_{basis}_{bit}")

    if basis == BASIS_Z:
        if bit == 1:
            qc.x(qr[0])
    elif basis == BASIS_X:
        if bit == 0:
            qc.h(qr[0])
        elif bit == 1:
            qc.x(qr[0])
            qc.h(qr[0])
    else:
        raise ValueError(f"Invalid basis '{basis}'. Must be '{BASIS_Z}' or '{BASIS_X}'.")

    return qc


def build_bb84_qubit_circuit(
    alice_bit: int,
    alice_basis: str,
    bob_basis: str,
    eve_present: bool = False,
    eve_basis: Optional[str] = None,
) -> QuantumCircuit:
    """
    Builds a single-qubit full transmission circuit including Alice preparation,
    optional Eve intercept-resend attack, and Bob measurement.
    
    Args:
        alice_bit: Alice's bit (0 or 1).
        alice_basis: Alice's basis ('Z' or 'X').
        bob_basis: Bob's basis ('Z' or 'X').
        eve_present: Whether Eve is actively intercepting.
        eve_basis: Eve's basis ('Z' or 'X') if present.
        
    Returns:
        QuantumCircuit configured with registers and gates.
    """
    qr = QuantumRegister(1, name="qubit")
    cr_bob = ClassicalRegister(1, name="bob_meas")
    
    if eve_present:
        if eve_basis is None:
            raise ValueError("eve_basis must be provided when eve_present is True")
        cr_eve = ClassicalRegister(1, name="eve_meas")
        qc = QuantumCircuit(qr, cr_eve, cr_bob, name="BB84_Eve_Attack")
    else:
        qc = QuantumCircuit(qr, cr_bob, name="BB84_Direct")

    # 1. Alice State Preparation
    if alice_basis == BASIS_Z:
        if alice_bit == 1:
            qc.x(qr[0])
    elif alice_basis == BASIS_X:
        if alice_bit == 0:
            qc.h(qr[0])
        elif alice_bit == 1:
            qc.x(qr[0])
            qc.h(qr[0])
    qc.barrier(label="Alice Channel")

    # 2. Optional Eve Intercept-Resend Attack
    if eve_present:
        if eve_basis == BASIS_X:
            qc.h(qr[0])
        qc.measure(qr[0], cr_eve[0])
        qc.barrier(label="Eve Intercept")
        
        # In Qiskit, Eve resets and resends the state matching her measurement outcome
        qc.reset(qr[0])
        # Resend state matching Eve's measured outcome:
        # If Eve's measurement was 1, apply X gate
        qc.x(qr[0]).c_if(cr_eve, 1)
        # If Eve used X basis, transform |0> -> |+> and |1> -> |->
        if eve_basis == BASIS_X:
            qc.h(qr[0])
        qc.barrier(label="Eve Resend")

    # 3. Bob's Measurement
    if bob_basis == BASIS_X:
        qc.h(qr[0])
    qc.measure(qr[0], cr_bob[0])

    return qc


def get_circuit_ascii_art(qc: QuantumCircuit) -> str:
    """Returns ASCII representation of a quantum circuit."""
    return qc.draw(output="text").single_string()
