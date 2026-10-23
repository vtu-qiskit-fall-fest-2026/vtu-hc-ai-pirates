# QuantumShield: 3-Minute Hackathon Demo Script & Troubleshooting Guide

**Hackathon:** Qiskit Fall Fest 2026  
**Track:** Quantum Cryptography & Security  
**Team:** AI Pirates (VTU-QFF-HC-0142)  
**Target Duration:** ~3 Minutes  

---

### [0:00 - 0:35] Part 1: The Problem & The Quantum Solution
> **Speaker:**
> "Distinguished judges and fellow quantum enthusiasts, welcome to **QuantumShield**.
> 
> In modern cybersecurity, symmetric encryption protects virtually all sensitive communication. But there is a glaring fundamental vulnerability: **how do Alice and Bob securely share that secret key in the first place?** Classical channels can be secretly tapped without leaving any physical footprint.
> 
> Quantum Key Distribution — specifically the **Bennett-Brassard 1984 (BB84)** protocol — changes the game entirely. Thanks to the No-Cloning Theorem and quantum measurement collapse, an eavesdropper cannot observe the key without irreversibly disturbing the quantum states.
> 
> However, quantum cryptography can be abstract and intimidating for beginners. Our team, **AI Pirates**, built **QuantumShield** — an interactive educational simulator executing **genuine Qiskit 2.x quantum circuits** for every single transmitted photon."

---

### [0:35 - 1:15] Part 2: Live Demo — The Secure Channel (Eve Disabled)
> **Action:**
> *(Navigate to Dashboard. Set Qubits = 100, Eve Toggle = OFF. Click "Run Simulation".)*
> 
> **Speaker:**
> "Let's begin with a baseline transmission on an ideal quantum channel.
> 
> Alice generates random secret bits and encodes each into a quantum state using two conjugate bases: the computational Z basis with Pauli-X gates, and the diagonal X basis with Hadamard gates. Bob independently chooses his measurement bases.
> 
> Notice what happens during classical basis reconciliation:
> - About 50% of the bits are discarded where bases differed.
> - On the retained matching bases, Alice and Bob achieve **100% bit agreement**.
> - The observed Quantum Bit Error Rate (QBER) is **exactly 0.00%**.
> 
> The dashboard confirms: **Quantum Channel Secure — Key Established!**"

---

### [1:15 - 2:05] Part 3: Live Demo — Eavesdropping Attack (Eve Enabled)
> **Action:**
> *(Toggle "Enable Eve (Intercept-Resend Attack)". Click "Run Simulation".)*
> 
> **Speaker:**
> "Now let's simulate an adversary — Eve — intercepting our transmission.
> 
> Eve intercepts each photon, guesses a measurement basis, measures the qubit, and resends a replacement. But by the No-Cloning Theorem, Eve cannot copy the state. Whenever she guesses the wrong basis — which happens 50% of the time — she collapses the superposition. When Bob measures in Alice's original basis, he has a 50% chance of an error.
> 
> Look at the live metrics:
> - The observed QBER instantly spikes to **~25%** ($0.5 \times 0\% + 0.5 \times 50\% = 25.0\%$).
> - Our automated security threshold is breached: **Eavesdropping Detected!**
> - Alice and Bob immediately abort the compromised key."

---

### [2:05 - 2:40] Part 4: Advanced Enhancements (Noise, Monte Carlo & Privacy Amplification)
> **Action:**
> *(Navigate to 'Repeated Monte Carlo Experiments', click 'Run Monte Carlo Batch', then navigate to 'Privacy Amplification Demo'.)*
> 
> **Speaker:**
> "We enhanced QuantumShield with advanced research tools:
> 1. **Repeated Monte Carlo Trials:** In finite quantum experiments, single runs fluctuate; our batch runner proves empirical convergence toward the theoretical 25% across trials.
> 2. **Physical Channel Noise:** We model depolarizing channel noise, demonstrating to students that fiber attenuation produces non-zero QBER even without an eavesdropper.
> 3. **Privacy Amplification:** Using 2-Universal parity hashing, we compress sifted keys to eliminate any residual mutual information an eavesdropper could have learned."

---

### [2:40 - 3:00] Part 5: Testing, Limitations & Conclusion
> **Speaker:**
> "To guarantee engineering rigor, our project includes a **29-test automated test suite with pytest** covering state encoding, sifting logic, noise models, and CSV export, achieving a 100% pass rate.
> 
> Responsible disclosure: As an educational prototype, QuantumShield models intercept-resend attacks in simulation. Real-world physical QKD requires authenticated classical channels and physical detectors.
> 
> QuantumShield transforms abstract quantum cryptography into an intuitive, verifiable experience. Thank you!"

---

## 🛠️ Troubleshooting Guide

### 1. `ModuleNotFoundError: No module named 'qiskit'`
- **Cause:** Qiskit is not installed in your active Python virtual environment.
- **Fix:** 
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

### 2. `AttributeError: module 'qiskit' has no attribute 'Aer'`
- **Cause:** In Qiskit 2.x, the legacy `qiskit-aer` provider was decoupled.
- **Fix:** QuantumShield is natively built using Qiskit 2.x standard `qiskit.quantum_info.Statevector` and core primitives, requiring no external C++ compiled binaries or legacy Aer backends.

### 3. Port 8501 Already in Use (Streamlit)
- **Cause:** Another Streamlit process is occupying the default port.
- **Fix:**
  ```powershell
  streamlit run app.py --server.port 8502
  ```

### 4. PowerShell Execution Policy Restriction
- **Cause:** Script execution is disabled by default in Windows PowerShell.
- **Fix:**
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  .\.venv\Scripts\Activate.ps1
  ```

### 5. CSV Export Encoding Warnings
- **Cause:** Non-ASCII characters in operating system regional settings.
- **Fix:** QuantumShield enforces strict `utf-8` encoding across all DataFrame and CSV export pipelines.
