"""
QuantumShield - Utility Helpers
Provides data formatting, table conversions, binary string manipulations,
Vernam One-Time Pad encryption, and Privacy Amplification educational demonstrations.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from src.protocol import ProtocolResult


def result_to_dataframe(result: ProtocolResult) -> pd.DataFrame:
    """
    Converts transmission records from ProtocolResult into a structured pandas DataFrame.
    """
    rows: List[Dict[str, Any]] = []
    for tx in result.transmissions:
        row = {
            "Qubit Index": tx.index,
            "Alice Bit": tx.alice_bit,
            "Alice Basis": tx.alice_basis,
            "Eve Present": "Yes" if tx.eve_present else "No",
            "Eve Basis": tx.eve_basis if tx.eve_present else "N/A",
            "Eve Bit": tx.eve_measured_bit if tx.eve_present else "N/A",
            "Bob Basis": tx.bob_basis,
            "Bob Bit": tx.bob_measured_bit,
            "Basis Match": "MATCH" if tx.basis_matched else "MISMATCH (Discarded)",
            "Bit Agreement": (
                ("MATCH" if tx.bit_matched else "ERROR") if tx.basis_matched else "N/A"
            ),
            "Sifted": "Retained" if tx.basis_matched else "Discarded",
        }
        rows.append(row)
    return pd.DataFrame(rows)


def bits_to_string(bits: List[int], max_length: int = 64) -> str:
    """Formats a list of binary integers into a clean string representation."""
    s = "".join(str(b) for b in bits)
    if len(s) > max_length:
        return s[:max_length] + f"... ({len(s)} bits total)"
    return s


def one_time_pad_xor(message: str, key_bits: List[int]) -> Dict[str, Any]:
    """
    Demonstrates Vernam One-Time Pad encryption/decryption using the BB84 sifted key.
    
    Args:
        message: Plaintext ASCII message.
        key_bits: Sifted quantum key bits.
        
    Returns:
        Dict with plaintext, key used, ciphertext bits, and decrypted message.
    """
    message_bytes = message.encode("utf-8")
    msg_bits = []
    for byte in message_bytes:
        for i in range(7, -1, -1):
            msg_bits.append((byte >> i) & 1)

    required_bits = len(msg_bits)
    if len(key_bits) < required_bits:
        return {
            "success": False,
            "error": f"Key length ({len(key_bits)} bits) is shorter than required message length ({required_bits} bits).",
            "required_bits": required_bits,
            "available_bits": len(key_bits),
        }

    used_key = key_bits[:required_bits]
    cipher_bits = [m ^ k for m, k in zip(msg_bits, used_key)]
    
    # Decrypt
    decrypted_bits = [c ^ k for c, k in zip(cipher_bits, used_key)]
    
    # Convert back to string
    dec_bytes = bytearray()
    for i in range(0, len(decrypted_bits), 8):
        byte_val = 0
        for bit in decrypted_bits[i:i+8]:
            byte_val = (byte_val << 1) | bit
        dec_bytes.append(byte_val)
        
    decrypted_text = dec_bytes.decode("utf-8", errors="replace")

    return {
        "success": True,
        "message": message,
        "required_bits": required_bits,
        "msg_bits": msg_bits,
        "used_key": used_key,
        "cipher_bits": cipher_bits,
        "decrypted_text": decrypted_text,
    }


def privacy_amplification_demo(
    sifted_key: List[int],
    target_length: int,
    seed: int = 42,
) -> Tuple[List[int], str]:
    """
    Educational demonstration of Privacy Amplification using a Toeplitz / parity matrix hash.
    Shrinks an $N$-bit sifted key into an $M$-bit final secret key ($M < N$),
    exponentially compressing any potential partial mutual information an eavesdropper might have obtained.
    
    Args:
        sifted_key: Raw sifted bit sequence.
        target_length: Desired final secure key length (M < len(sifted_key)).
        seed: Random seed for public matrix generation.
        
    Returns:
        Tuple of (amplified_key, explanation_message)
    """
    n = len(sifted_key)
    if n == 0 or target_length <= 0:
        return [], "Empty input or non-positive target length."
    if target_length >= n:
        return sifted_key[:target_length], "Target length must be smaller than sifted key for compression."

    rng = np.random.default_rng(seed)
    # Generate random binary hash matrix H of size (target_length x n)
    hash_matrix = rng.integers(0, 2, size=(target_length, n))
    
    # Key vector multiplication modulo 2: K_secret = (H * K_sifted) mod 2
    key_vec = np.array(sifted_key, dtype=int)
    amplified_bits = (np.dot(hash_matrix, key_vec) % 2).tolist()

    ratio = (target_length / n) * 100
    msg = (
        f"Compressed {n} sifted bits into {target_length} secure bits ({ratio:.1f}% compression ratio). "
        f"By Leftover Hash Lemma, Eve's mutual information drops to < 2^(-(n - target_length))."
    )
    return amplified_bits, msg
