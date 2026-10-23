"""
QuantumShield: BB84 Quantum Key Distribution and Eavesdropping Detection
Enhanced Streamlit Interactive Dashboard for Qiskit Fall Fest 2026
Team: AI Pirates (VTU-QFF-HC-0142) | Track: Quantum Cryptography & Security
"""

import streamlit as st
import numpy as np
import pandas as pd
from typing import Optional

from src.protocol import ProtocolResult
from src.simulation import run_bb84_simulation, run_repeated_experiments
from src.circuits import build_bb84_qubit_circuit, get_circuit_ascii_art
from src.visualization import (
    plot_qber_comparison,
    plot_cumulative_error_rate,
    plot_basis_matching_pie,
    plot_repeated_trials,
)
from src.utils import result_to_dataframe, bits_to_string, one_time_pad_xor, privacy_amplification_demo
from src.metrics import analyze_protocol_performance

# 1. Page Configuration
st.set_page_config(
    page_title="QuantumShield — BB84 QKD Simulator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark navy, cyan & violet aesthetics
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1120;
        color: #e2e8f0;
    }
    .metric-card {
        background: linear-gradient(135deg, #111c38 0%, #172554 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #06b6d4;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .alert-box {
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
    }
    .alert-breach {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #fca5a5;
    }
    .alert-secure {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #6ee7b7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "result_no_eve" not in st.session_state:
    st.session_state.result_no_eve = None
if "result_with_eve" not in st.session_state:
    st.session_state.result_with_eve = None
if "last_run" not in st.session_state:
    st.session_state.last_run = None
if "monte_carlo_results" not in st.session_state:
    st.session_state.monte_carlo_results = None

# Sidebar Navigation & Controls
st.sidebar.image("https://img.shields.io/badge/Qiskit-Fall%20Fest%202026-blueviolet?style=for-the-badge", use_container_width=True)
st.sidebar.title("🛡️ QuantumShield")
st.sidebar.caption("BB84 Quantum Key Distribution Simulator\nTeam: **AI Pirates** (VTU-QFF-HC-0142)")

nav_selection = st.sidebar.radio(
    "Navigation",
    [
        "1. Dashboard & Simulator",
        "2. How BB84 Works",
        "3. Quantum Circuit Inspector",
        "4. Intercept-Resend Attack Analysis",
        "5. Comparative QBER Benchmark",
        "6. Repeated Monte Carlo Experiments",
        "7. One-Time Pad Encryption Demo",
        "8. Privacy Amplification Demo",
        "9. Project Information & Limitations",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("Simulation Parameters")

n_qubits = st.sidebar.slider("Number of Transmitted Qubits", min_value=10, max_value=500, value=100, step=10)
channel_noise = st.sidebar.slider("Quantum Channel Noise (%)", min_value=0.0, max_value=20.0, value=0.0, step=1.0) / 100.0
qber_threshold = st.sidebar.slider("QBER Security Threshold (%)", min_value=1.0, max_value=15.0, value=5.0, step=0.5) / 100.0

use_seed = st.sidebar.checkbox("Use Fixed Random Seed", value=False)
seed_val = st.sidebar.number_input("Seed Value", value=42, step=1, disabled=not use_seed) if use_seed else None
eve_toggle = st.sidebar.toggle("Enable Eve (Intercept-Resend Attack)", value=False)

col_run, col_reset = st.sidebar.columns(2)

if col_run.button("🚀 Run Simulation", use_container_width=True, type="primary"):
    with st.spinner("Executing Qiskit quantum circuits..."):
        sim_res = run_bb84_simulation(
            n_qubits=n_qubits,
            eve_present=eve_toggle,
            noise_rate=channel_noise,
            seed=int(seed_val) if use_seed else None,
            qber_threshold=qber_threshold,
        )
        st.session_state.last_run = sim_res
        if eve_toggle:
            st.session_state.result_with_eve = sim_res
        else:
            st.session_state.result_no_eve = sim_res
    st.sidebar.success(f"Simulation completed ({n_qubits} qubits)!")

if col_reset.button("🔄 Reset Data", use_container_width=True):
    st.session_state.result_no_eve = None
    st.session_state.result_with_eve = None
    st.session_state.last_run = None
    st.session_state.monte_carlo_results = None
    st.sidebar.info("Session state cleared.")


# View 1: Main Dashboard & Simulator
if nav_selection == "1. Dashboard & Simulator":
    st.title("QuantumShield: BB84 QKD Simulator")
    st.markdown(
        """
        Welcome to **QuantumShield**, an educational simulation of the **Bennett-Brassard 1984 (BB84)** 
        Quantum Key Distribution protocol executed using genuine **Qiskit quantum circuits**.
        Explore quantum state preparation, basis reconciliation (sifting), and intercept-resend eavesdropping detection.
        """
    )

    current_result = st.session_state.last_run

    if current_result is None:
        st.info("👈 Configure your parameters in the sidebar and click **'Run Simulation'** to begin.")
    else:
        perf = analyze_protocol_performance(
            total_qubits=current_result.total_qubits,
            sifted_bits=current_result.sifted_bits_count,
            errors=current_result.sifted_mismatch_count,
            eve_present=current_result.eve_enabled,
        )

        # High-level Alert
        if current_result.eavesdropping_detected:
            st.markdown(
                f"""
                <div class="alert-box alert-breach">
                    <h3>⚠️ Security Threshold Exceeded! Possible Attack or Noise</h3>
                    Observed QBER is <strong>{current_result.qber * 100:.2f}%</strong> (exceeds the configured {qber_threshold * 100:.1f}% threshold).
                    {'An active eavesdropper (Eve) intercepted the quantum states!' if current_result.eve_enabled else 'High channel noise introduced excessive bit flips.'}
                    <strong> The sifted key cannot be trusted in this state.</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="alert-box alert-secure">
                    <h3>✅ Quantum Channel Secure — Key Established</h3>
                    Observed QBER is <strong>{current_result.qber * 100:.2f}%</strong> (within {qber_threshold * 100:.1f}% threshold).
                    Alice and Bob's sifted keys match with {current_result.agreementRate:.1f}% agreement.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Key Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"""<div class="metric-card">
                <div class="metric-sub">TRANSMITTED QUBITS</div>
                <div class="metric-value">{current_result.total_qubits}</div>
                <div class="metric-sub">Eve: {'Active (Intercept)' if current_result.eve_enabled else 'Direct (No Eve)'} | Noise: {channel_noise*100:.1f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""<div class="metric-card">
                <div class="metric-sub">SIFTED KEY BITS</div>
                <div class="metric-value">{current_result.sifted_bits_count}</div>
                <div class="metric-sub">Efficiency: {current_result.basis_match_rate:.1f}% (~50% target)</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f"""<div class="metric-card">
                <div class="metric-sub">OBSERVED QBER</div>
                <div class="metric-value" style="color: {'#ef4444' if current_result.eavesdropping_detected else '#10b981'};">{current_result.qber * 100:.2f}%</div>
                <div class="metric-sub">Threshold: {qber_threshold * 100:.1f}% | Theo: {perf['theoretical_qber_percentage']:.1f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with m4:
            st.markdown(
                f"""<div class="metric-card">
                <div class="metric-sub">SIFTED KEY AGREEMENT</div>
                <div class="metric-value" style="color: {'#a855f7' if current_result.agreement_rate == 100 else '#f59e0b'};">{current_result.agreement_rate:.1f}%</div>
                <div class="metric-sub">Mismatched bits: {current_result.sifted_mismatch_count}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Sifted Key Preview
        st.subheader("🔑 Sifted Key Sequences")
        col_ka, col_kb = st.columns(2)
        with col_ka:
            st.markdown("**Alice's Sifted Key:**")
            st.code(bits_to_string(current_result.alice_sifted_key, max_length=96))
        with col_kb:
            st.markdown("**Bob's Sifted Key:**")
            st.code(bits_to_string(current_result.bob_sifted_key, max_length=96))

        # Visual Charts
        st.subheader("📊 Statistical Analysis & Charts")
        c1, c2 = st.columns(2)
        with c1:
            fig_traj = plot_cumulative_error_rate(current_result)
            st.pyplot(fig_traj)
        with c2:
            fig_pie = plot_basis_matching_pie(current_result)
            st.pyplot(fig_pie)

        # Transmission Table with CSV export
        st.subheader("📋 Per-Qubit Transmission Log")
        df = result_to_dataframe(current_result)
        st.dataframe(df, use_container_width=True, height=300)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Transmission Log as CSV",
            data=csv_data,
            file_name=f"quantumshield_bb84_qubits_{current_result.total_qubits}.csv",
            mime="text/csv",
        )


# View 2: How BB84 Works
elif nav_selection == "2. How BB84 Works":
    st.title("How the BB84 Protocol Works")
    st.markdown(
        """
        The **BB84 protocol**, invented by Charles Bennett and Gilles Brassard in 1984, relies on 
        the fundamental laws of quantum physics — specifically the **No-Cloning Theorem** and the 
        **Heisenberg Uncertainty Principle** — to achieve secure key distribution.
        """
    )

    st.subheader("1. The Two Conjugate Bases")
    st.markdown(
        """
        BB84 uses two mutually unbiased measurement bases:
        
        | Basis | Name | Bit 0 Encoding | Bit 1 Encoding | Qiskit Gates Applied |
        |---|---|---|---|---|
        | **Z** | Computational Basis | $|0\\rangle$ | $|1\\rangle$ | None (for 0), `X` gate (for 1) |
        | **X** | Diagonal / Hadamard Basis | $|+\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$ | $|-\\rangle = \\frac{|0\\rangle - |1\\rangle}{\\sqrt{2}}$ | `H` gate (for 0), `X` then `H` (for 1) |
        """
    )


# View 3: Quantum Circuit Inspector
elif nav_selection == "3. Quantum Circuit Inspector":
    st.title("🔬 Interactive Qiskit Circuit Inspector")
    st.markdown("Examine the exact quantum circuit gates executed by Qiskit for any single qubit transmission.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        inspect_bit = st.selectbox("Alice Bit", [0, 1], index=1)
    with col2:
        inspect_a_basis = st.selectbox("Alice Basis", ["Z", "X"], index=1)
    with col3:
        inspect_b_basis = st.selectbox("Bob Basis", ["Z", "X"], index=1)
    with col4:
        inspect_eve = st.checkbox("Include Eve Intercept", value=True)
    
    inspect_e_basis = "Z"
    if inspect_eve:
        inspect_e_basis = st.selectbox("Eve Basis", ["Z", "X"], index=0)

    qc = build_bb84_qubit_circuit(
        alice_bit=inspect_bit,
        alice_basis=inspect_a_basis,
        bob_basis=inspect_b_basis,
        eve_present=inspect_eve,
        eve_basis=inspect_e_basis if inspect_eve else None,
    )

    st.subheader("Qiskit Circuit ASCII Diagram")
    st.code(get_circuit_ascii_art(qc), language="text")


# View 4: Intercept-Resend Attack Analysis
elif nav_selection == "4. Intercept-Resend Attack Analysis":
    st.title("🕵️ Eve's Intercept-Resend Attack")
    st.markdown(
        """
        ### Why Does Eve Cause a 25% Error Rate?
        When Eve intercepts a qubit, she does not know which basis Alice used. By the **No-Cloning Theorem**, Eve cannot copy the unknown quantum state.
        She must guess a measurement basis:
        """
    )
    st.latex(r"\mathrm{QBER}_{\text{theoretical}} = 0.5 \times 0\% + 0.5 \times 50\% = 25\%")


# View 5: Comparative QBER Benchmark
elif nav_selection == "5. Comparative QBER Benchmark":
    st.title("📈 Comparative QBER Benchmark")
    st.markdown("Compare measured experimental outcomes between the clean channel and the intercepted channel.")

    c_no, c_with = st.session_state.result_no_eve, st.session_state.result_with_eve

    if c_no is None and c_with is None:
        st.warning("Please run at least one simulation with Eve disabled and one with Eve enabled in the sidebar.")
    else:
        fig_comp = plot_qber_comparison(c_no, c_with, threshold=qber_threshold * 100.0)
        st.pyplot(fig_comp)


# View 6: Repeated Monte Carlo Experiments (Enhancement 2)
elif nav_selection == "6. Repeated Monte Carlo Experiments":
    st.title("🎲 Repeated Monte Carlo Experiments (Statistical Convergence)")
    st.markdown(
        """
        In finite quantum experiments, the observed error rate fluctuates due to binomial sampling noise.
        Run **multiple independent trials** to observe empirical statistical convergence toward the theoretical expectation.
        """
    )

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        n_trials = st.slider("Number of Independent Trials", min_value=5, max_value=30, value=10, step=5)
    with col_t2:
        qubits_per_trial = st.slider("Qubits Per Trial", min_value=50, max_value=300, value=100, step=25)
    with col_t3:
        mc_eve = st.checkbox("Enable Eve Across Trials", value=True)

    if st.button("🚀 Run Monte Carlo Batch", type="primary"):
        with st.spinner(f"Simulating {n_trials} independent quantum runs..."):
            mc_res = run_repeated_experiments(
                n_trials=n_trials,
                n_qubits_per_trial=qubits_per_trial,
                eve_present=mc_eve,
                noise_rate=channel_noise,
            )
            st.session_state.monte_carlo_results = mc_res

    mc_data = st.session_state.monte_carlo_results
    if mc_data is not None:
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.metric("Total Trials", mc_data["n_trials"])
        with mc2:
            st.metric("Mean QBER", f"{mc_data['mean_qber']:.2f}%", f"Theo: {mc_data['theoretical_qber']:.2f}%")
        with mc3:
            st.metric("Standard Deviation", f"±{mc_data['std_qber']:.2f}%")
        with mc4:
            st.metric("QBER Range [Min - Max]", f"{mc_data['min_qber']:.1f}% - {mc_data['max_qber']:.1f}%")

        fig_mc = plot_repeated_trials(mc_data)
        st.pyplot(fig_mc)

        st.subheader("Trial Summary Table")
        st.table(pd.DataFrame(mc_data["trial_results"]))


# View 7: One-Time Pad Encryption Demo
elif nav_selection == "7. One-Time Pad Encryption Demo":
    st.title("🔐 Educational Vernam One-Time Pad Demonstration")
    active_res = st.session_state.last_run
    if active_res is None or len(active_res.alice_sifted_key) == 0:
        st.info("Run a simulation with Eve disabled to establish a clean quantum key first.")
    else:
        user_msg = st.text_input("Plaintext Message to Encrypt:", value="QISKIT2026")
        otp_res = one_time_pad_xor(user_msg, active_res.alice_sifted_key)
        if not otp_res["success"]:
            st.error(otp_res["error"])
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Alice's Plaintext (ASCII Binary):**")
                st.code(bits_to_string(otp_res["msg_bits"]))
                st.markdown("**Quantum Key Used:**")
                st.code(bits_to_string(otp_res["used_key"]))
                st.markdown("**Ciphertext C = M ⊕ K:**")
                st.code(bits_to_string(otp_res["cipher_bits"]))
            with c2:
                bob_otp = one_time_pad_xor(user_msg, active_res.bob_sifted_key)
                st.markdown("**Bob's Received Key:**")
                st.code(bits_to_string(bob_otp["used_key"]))
                if active_res.alice_sifted_key[:len(otp_res['used_key'])] == active_res.bob_sifted_key[:len(otp_res['used_key'])]:
                    st.success(f"Decrypted successfully: **'{user_msg}'**")
                else:
                    st.error(f"Corrupted decryption: **'{bob_otp['decrypted_text']}'**")


# View 8: Privacy Amplification Demo (Enhancement 6)
elif nav_selection == "8. Privacy Amplification Demo":
    st.title("🗜️ Privacy Amplification Demonstration")
    st.markdown(
        """
        Even when QBER is below the abort threshold, an eavesdropper may have obtained **partial mutual information**
        $I(A; E) > 0$. **Privacy Amplification** uses universal hashing to compress the sifted key into a shorter,
        information-theoretically secure key, shrinking Eve's knowledge exponentially toward zero.
        """
    )
    active_res = st.session_state.last_run
    if active_res is None or len(active_res.alice_sifted_key) == 0:
        st.info("Run a simulation first to obtain a sifted key.")
    else:
        s_len = len(active_res.alice_sifted_key)
        target_len = st.slider("Target Amplified Key Length", min_value=4, max_value=max(5, s_len - 2), value=max(4, s_len // 2))
        amp_key, expl = privacy_amplification_demo(active_res.alice_sifted_key, target_length=target_len)
        st.success(expl)
        st.markdown("**Raw Sifted Key (N bits):**")
        st.code(bits_to_string(active_res.alice_sifted_key, max_length=96))
        st.markdown(f"**Privacy Amplified Secret Key ({target_len} bits):**")
        st.code(bits_to_string(amp_key, max_length=96))


# View 9: Project Information & Limitations
elif nav_selection == "9. Project Information & Limitations":
    st.title("ℹ️ Project Information & Responsible Use Notice")
    st.markdown(
        """
        ### Hackathon Metadata
        - **Project Name:** QuantumShield
        - **Hackathon:** Qiskit Fall Fest 2026 | **Team:** AI Pirates (VTU-QFF-HC-0142)
        - **Track:** Quantum Cryptography & Security
        - **Repository:** `https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates`

        ---

        ### ⚠️ Mandatory Scientific Correctness Notice
        - **Educational Research Prototype:** Does not claim to implement physical optical hardware.
        - **Noise vs Attack:** QBER alone does not differentiate between intentional eavesdropping and optical fiber attenuation/dark counts.
        - **Authenticated Classical Channel Required:** Production QKD requires Wegman-Carter classical authentication to prevent Man-in-the-Middle attacks.
        """
    )
