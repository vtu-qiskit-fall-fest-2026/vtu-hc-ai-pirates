# QuantumShield: BB84 Quantum Key Distribution and Eavesdropping Detection

[![Qiskit](https://img.shields.io/badge/Qiskit-2.x-blueviolet?style=for-the-badge&logo=qiskit)](https://qiskit.org)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Pytest](https://img.shields.io/badge/Tests-29%20Passed-green?style=for-the-badge&logo=pytest)](https://pytest.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow?style=for-the-badge)](LICENSE)

An interactive, educational quantum cybersecurity simulator for the **Bennett-Brassard 1984 (BB84)** Quantum Key Distribution protocol, built with **genuine Qiskit quantum circuits**.

Developed for **Qiskit Fall Fest 2026** by **Team AI Pirates**.

---

## 👥 Hackathon Metadata

- **Project Name:** QuantumShield
- **Project Title:** QuantumShield: BB84 Quantum Key Distribution and Eavesdropping Detection
- **Hackathon:** Qiskit Fall Fest 2026
- **Team Name:** AI Pirates
- **Team ID:** `VTU-QFF-HC-0142`
- **Track:** Quantum Cryptography & Security
- **Official Repository:** [https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates](https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates)

---

## 📌 Problem Statement

Secure communication often depends on sharing a secret key between two parties. However:
1. **Classical Tapping Vulnerability:** Transmitting secret keys across classical networks allows adversaries to intercept, copy, and inspect the key without leaving physical traces.
2. **Post-Quantum Vulnerability:** Traditional asymmetric key exchanges (RSA, ECC) are vulnerable to Shor's algorithm on fault-tolerant quantum computers.
3. **The Educational Gap:** Quantum Key Distribution (QKD) principles — such as quantum state superposition, conjugate bases, and wavefunction collapse — can be abstract and counterintuitive for students.

---

## 💡 Proposed Solution

**QuantumShield** provides an interactive, visual simulation of BB84 powered by **authentic Qiskit quantum circuits**. Rather than using classical random number shortcuts, QuantumShield implements genuine quantum circuit gate operations (Pauli-X, Hadamard, and projective statevector measurements).

Users can:
- Observe Alice encoding secret bits into quantum states.
- Watch Bob independently choose bases and measure received qubits.
- Toggle an adversarial eavesdropper (**Eve**) performing an **intercept-resend attack**.
- Witness the immediate statistical footprint: an unavoidable spike in the **Quantum Bit Error Rate (QBER)** from **0%** to **~25%**.
- Test physical **Channel Noise** modeling fiber attenuation.
- Run **Repeated Monte Carlo Trials** to observe empirical statistical convergence.
- Explore **Privacy Amplification** and **Vernam One-Time Pad** encryption.

---

## 📐 System Architecture

![QuantumShield Architecture Diagram](assets/architecture.png)

### The BB84 Pipeline:
1. **Alice (State Preparation):**
   - Generates random secret bits $a_i \in \{0, 1\}$ and conjugate bases $b_i^A \in \{Z, X\}$.
   - Prepares quantum states using Qiskit:
     - **Z Basis:** Bit 0 $\rightarrow |0\rangle$, Bit 1 $\rightarrow |1\rangle$ (`X` gate).
     - **X Basis:** Bit 0 $\rightarrow |+\rangle$ (`H` gate), Bit 1 $\rightarrow |-\rangle$ (`X` then `H`).

2. **Quantum Channel & Eve Interception:**
   - **Direct Channel:** Unperturbed transmission directly to Bob.
   - **Intercept-Resend Attack (Eve):** Eve intercepts each photon, measures in an independently chosen basis $b_i^E \in \{Z, X\}$, and re-prepares a replacement qubit matching her outcome.

3. **Bob (Measurement):**
   - Independently chooses basis $b_i^B \in \{Z, X\}$.
   - Applies an `H` basis rotation gate prior to computational basis measurement when measuring in X.

4. **Classical Sifting (Reconciliation):**
   - Alice and Bob publicly announce bases used; retain matching positions ($b_i^A = b_i^B$, ~50% retention).

5. **QBER Analysis & Eavesdropping Detection:**
   $$\mathrm{QBER} = \frac{\text{Number of Mismatched Sifted Bits}}{\text{Total Number of Sifted Bits}}$$
   - **No Eve (Noiseless):** $\mathrm{QBER} = 0.0\%$ (Channel Secure $\rightarrow$ Key Accepted).
   - **With Eve:** $\mathrm{QBER} \approx 25.0\%$ (Threshold breached $\rightarrow$ Key Aborted).

---

## 📊 Visual Benchmarks & Results

### 1. QBER Comparison Benchmark
![QBER Comparison Benchmark](assets/qber_comparison.png)

### 2. Monte Carlo Statistical Variance Across Repeated Trials
![Monte Carlo Variance](assets/monte_carlo_distribution.png)

### 3. Representative Qiskit Quantum Circuit
![Representative Qiskit Circuit](assets/circuit_diagram.png)

---

## 🛠️ Installation & Setup Instructions

### Prerequisites
- Python 3.10 or 3.11 installed.
- Git installed.

### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates.git
cd vtu-hc-ai-pirates

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Launch the Streamlit dashboard
streamlit run app.py
```

### Linux / macOS (Bash)
```bash
# Clone the repository
git clone https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates.git
cd vtu-hc-ai-pirates

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Launch the Streamlit dashboard
streamlit run app.py
```

---

## 🧪 Automated Testing

QuantumShield includes a **29-test automated test suite** covering state encoding, sifting algorithms, circuit execution, noise modeling, Monte Carlo batching, and CSV exports.

To execute the test suite:
```powershell
python -m pytest -v
```

### Actual Test Suite Execution Output:
```text
tests/test_metrics.py::TestMetricsCalculation::test_qber_exact_values PASSED           [  3%]
tests/test_metrics.py::TestMetricsCalculation::test_zero_sifted_bits_safe_handling PASSED    [  6%]
tests/test_metrics.py::TestMetricsCalculation::test_mismatched_key_lengths_raise_error PASSED [ 10%]
tests/test_metrics.py::TestMetricsCalculation::test_wilson_confidence_interval_bounds PASSED [ 13%]
tests/test_metrics.py::TestMetricsCalculation::test_zero_total_confidence_interval PASSED    [ 17%]
tests/test_metrics.py::TestMetricsCalculation::test_analyze_protocol_performance_structure PASSED [ 20%]
tests/test_protocol.py::TestProtocolEncoding::test_z_basis_encoding_bit_0 PASSED      [ 24%]
tests/test_protocol.py::TestProtocolEncoding::test_z_basis_encoding_bit_1 PASSED      [ 27%]
tests/test_protocol.py::TestProtocolEncoding::test_x_basis_encoding_bit_0 PASSED      [ 31%]
tests/test_protocol.py::TestProtocolEncoding::test_x_basis_encoding_bit_1 PASSED      [ 34%]
tests/test_protocol.py::TestProtocolEncoding::test_invalid_basis_raises_error PASSED   [ 37%]
tests/test_protocol.py::TestSiftingLogic::test_basis_matching_logic PASSED             [ 41%]
tests/test_protocol.py::TestSiftingLogic::test_basis_mismatching_logic PASSED          [ 44%]
tests/test_protocol.py::TestSiftingLogic::test_reproducibility_with_seed PASSED        [ 48%]
tests/test_protocol.py::TestSiftingLogic::test_invalid_input_lengths_raise_error PASSED [ 51%]
tests/test_simulation.py::TestSimulationExecution::test_eve_disabled_zero_qber PASSED   [ 55%]
tests/test_simulation.py::TestSimulationExecution::test_eve_enabled_simulation_structure PASSED [ 58%]
tests/test_simulation.py::TestSimulationExecution::test_eve_enabled_error_rate_statistical_range PASSED [ 62%]
tests/test_simulation.py::TestSimulationExecution::test_simulation_reproducibility PASSED [ 65%]
tests/test_simulation.py::TestSimulationExecution::test_single_qubit_deterministic_matching PASSED [ 68%]
tests/test_simulation.py::TestSimulationExecution::test_noise_simulation_generates_errors_without_eve PASSED [ 72%]
tests/test_simulation.py::TestSimulationExecution::test_repeated_experiments_aggregation PASSED [ 75%]
tests/test_simulation.py::TestSimulationExecution::test_privacy_amplification_compression PASSED [ 79%]
tests/test_utils.py::TestUtils::test_result_to_dataframe_columns_and_rows PASSED [ 82%]
tests/test_utils.py::TestUtils::test_dataframe_csv_export PASSED         [ 86%]
tests/test_utils.py::TestUtils::test_bits_to_string_formatting PASSED    [ 89%]
tests/test_utils.py::TestUtils::test_one_time_pad_encryption_decryption_match PASSED [ 93%]
tests/test_utils.py::TestUtils::test_one_time_pad_insufficient_key_length PASSED [ 96%]
tests/test_utils.py::TestUtils::test_privacy_amplification_hashing PASSED [100%]

============================== 29 passed in 2.42s ==============================
```

---

## 📁 Repository Structure

```text
QuantumShield/
├── app.py                      # Streamlit interactive dashboard
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── LICENSE                     # Apache 2.0 license
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── config.toml             # Custom dark navy theme configuration
├── src/
│   ├── __init__.py
│   ├── protocol.py             # BB84 protocol definitions, state encoding, sifting
│   ├── circuits.py             # Qiskit QuantumCircuit builders & ASCII drawer
│   ├── simulation.py           # Quantum execution, channel noise & Monte Carlo batching
│   ├── metrics.py              # QBER, Wilson confidence intervals, benchmarks
│   ├── visualization.py        # Dark-themed Matplotlib figures & charts
│   └── utils.py                # Pandas export, OTP demo & Privacy Amplification
├── tests/
│   ├── __init__.py
│   ├── test_protocol.py        # 9 state encoding and sifting unit tests
│   ├── test_simulation.py      # 8 circuit simulation, noise & Monte Carlo tests
│   ├── test_metrics.py         # 6 QBER & boundary condition tests
│   └── test_utils.py           # 6 DataFrame, CSV export & OTP tests
├── assets/
│   ├── architecture.png        # System architecture flowchart
│   ├── qber_comparison.png     # Benchmark chart
│   ├── monte_carlo_distribution.png # Repeated trials variance chart
│   ├── circuit_diagram.png     # Qiskit circuit visual diagram
│   ├── generate_architecture_diagram.py
│   └── generate_visual_assets.py
├── docs/
│   ├── architecture.md         # Detailed architectural breakdown
│   ├── demo_script.md          # 3-minute hackathon presentation script & troubleshooting
│   └── presentation_outline.md # Complete slide deck content outline
└── presentation/
    ├── generate_presentation.py # Automated PowerPoint generator
    └── QuantumShield_Hackathon_Presentation.pptx # 14-slide editable presentation
```

---

## ⚠️ Scientific Correctness & Limitations

This project is an **educational research prototype**, not a commercial QKD deployment:
1. **Simplified Attack Model:** Models intercept-resend attacks; does not model photon-number splitting (PNS) or coherent memory attacks.
2. **Channel Assumptions:** Assumes ideal noiseless physical components unless the channel noise slider is explicitly enabled.
3. **Classical Authentication:** Production QKD requires an initial authenticated classical channel (e.g., Wegman-Carter MACs) to prevent classical man-in-the-middle attacks during basis announcement.
4. **Privacy Amplification:** Production systems execute classical error correction (Cascade/LDPC) and privacy amplification (universal hashing) to eliminate Eve's partial information.

---

## 📑 References & Acknowledgements

1. Bennett, C. H., & Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing.* International Conference on Computers, Systems & Signal Processing.
2. [IBM Quantum Learning: Quantum Key Distribution Module](https://qiskit.qotlabs.org/learning/modules/computer-science/quantum-key-distribution)
3. [Qiskit 2.x Documentation & Tutorials](https://docs.quantum.ibm.com)
4. Shor, P. W., & Preskill, J. (2000). *Simple Proof of Security of the BB84 Quantum Key Distribution Protocol.* Physical Review Letters.
