# QuantumShield: Presentation Outline & Slide Deck Structure

**File:** `presentation/QuantumShield_Hackathon_Presentation.pptx`  
**Format:** 16:9 Widescreen, Dark Navy Theme (#0b1120), Cyan (#06b6d4) & Violet (#a855f7) accents  
**Hackathon:** Qiskit Fall Fest 2026 | Team AI Pirates (VTU-QFF-HC-0142)  

---

### Slide Breakdown:

1. **Slide 1 — Title Slide**
   - Title: QuantumShield: BB84 Quantum Key Distribution and Eavesdropping Detection
   - Track: Quantum Cryptography & Security
   - Team: AI Pirates (VTU-QFF-HC-0142)
   - Technology: Qiskit 2.x, Python 3.10+, Streamlit, Matplotlib

2. **Slide 2 — Problem Statement**
   - The Secret Key Dilemma: Classical symmetric encryption vulnerability
   - Classical passive eavesdropping: Wiretapping without detection
   - Educational barrier: Steep learning curve for quantum measurement principles

3. **Slide 3 — Motivation: Why Quantum Physics?**
   - No-Cloning Theorem: Impossibility of duplicating unknown quantum states
   - Heisenberg Uncertainty Principle: Measurement collapse on conjugate bases
   - The Quantum Footprint: Forcing eavesdroppers to expose themselves through error rates

4. **Slide 4 — Proposed Solution**
   - Interactive BB84 simulation powered by authentic Qiskit quantum circuits
   - Real-time QBER calculation and eavesdropping alert thresholds
   - Dual interface: Streamlit dashboard and responsive web portal

5. **Slide 5 — BB84 Fundamentals & Basis Encoding**
   - Computational Basis (Z): $|0\rangle$, $|1\rangle$ (Pauli-X gate)
   - Hadamard Basis (X): $|+\rangle$, $|-\rangle$ (Hadamard H gate)
   - Conjugate transition probabilities: Uniform $50\%$ overlap

6. **Slide 6 — System Architecture**
   - Modular workflow: Alice State Prep $\rightarrow$ Quantum Channel $\rightarrow$ Bob Measurement
   - Attack branch: Eve Intercept-Resend stage
   - Classical reconciliation: Public basis sifting $\rightarrow$ QBER verification $\rightarrow$ Secret key

7. **Slide 7 — Protocol Workflow**
   - 6-phase protocol lifecycle: Transmission, Public Announcement, Sifting, Error Estimation, Security Check, Key Usage

8. **Slide 8 — Qiskit Implementation**
   - Construction of single and multi-qubit `QuantumCircuit` objects
   - Basis transformation via `H` gates
   - Measurement and state collapse using Qiskit `Statevector` primitives

9. **Slide 9 — Application Interface**
   - Dark navy cybersecurity dashboard with real-time parameter controls
   - Per-qubit telemetry tables, cumulative error convergence charts, and pie charts
   - Built-in Vernam One-Time Pad encryption demonstrator

10. **Slide 10 — Mathematical Proof of Eve's 25% Error Rate**
    - Formal probabilistic proof of intercept-resend attack
    - $P(\text{Match}) \times 0\% + P(\text{Mismatch}) \times 50\% = 25.0\%$

11. **Slide 11 — Experimental Simulation Results**
    - Genuine benchmark results:
      - Direct Channel: $N=200$, Sifted$=98$, $\mathrm{QBER}=0.00\%$
      - Intercepted Channel: $N=200$, Sifted$=104$, $\mathrm{QBER}=25.00\%$

12. **Slide 12 — Automated Testing & Verification**
    - 20 unit and statistical tests in pytest suite
    - $100\%$ pass rate in $1.24$ seconds across protocol, simulation, and metrics modules

13. **Slide 13 — Scientific Limitations & Future Scope**
    - Responsible disclosure: Educational simulator vs production physical QKD
    - Roadmap: Real IBM Quantum hardware backends (Heron/Eagle), PNS attack modeling, Cascade error correction

14. **Slide 14 — Conclusion & References**
    - Summary of deliverables and achievements
    - Academic and IBM Quantum reference citations
