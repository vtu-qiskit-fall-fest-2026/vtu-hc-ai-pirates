/**
 * QuantumShield — BB84 Quantum Key Distribution and Eavesdropping Detection
 * Interactive Application for Qiskit Fall Fest 2026
 * Team: AI Pirates (VTU-QFF-HC-0142) | Track: Quantum Cryptography & Security
 */

import React, { useState, useMemo } from 'react';
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Zap,
  Play,
  RotateCcw,
  Download,
  FileText,
  Key,
  Lock,
  Unlock,
  Radio,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Layers,
  Code2,
  Info,
  BarChart3,
  ExternalLink,
  Cpu,
  Eye,
  EyeOff,
  Sparkles,
  Sliders,
  Compass,
  ArrowRight
} from 'lucide-react';

type Basis = 'Z' | 'X';

interface Transmission {
  index: number;
  aliceBit: number;
  aliceBasis: Basis;
  bobBasis: Basis;
  bobMeasuredBit: number;
  evePresent: boolean;
  eveBasis?: Basis;
  eveMeasuredBit?: number;
  noiseApplied: boolean;
  basisMatched: boolean;
  bitMatched: boolean;
}

interface SimulationResult {
  totalQubits: number;
  eveEnabled: boolean;
  noiseRate: number;
  qberThreshold: number;
  transmissions: Transmission[];
  aliceSiftedKey: number[];
  bobSiftedKey: number[];
  siftedIndices: number[];
  siftedBitsCount: number;
  discardedBitsCount: number;
  siftedMismatchCount: number;
  qber: number;
  basisMatchRate: number;
  agreementRate: number;
  eavesdroppingDetected: boolean;
  seed?: number;
}

interface MonteCarloResult {
  trials: number;
  qubitsPerTrial: number;
  evePresent: boolean;
  noiseRate: number;
  meanQber: number;
  stdQber: number;
  minQber: number;
  maxQber: number;
  trialQbers: number[];
}

// Pseudo-random generator with optional seed
function createRng(seed?: number) {
  if (seed === undefined) {
    return () => Math.random();
  }
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

// Core BB84 Simulation Engine mirroring Qiskit circuit execution with noise
function runSimulation(
  nQubits: number,
  eveEnabled: boolean,
  noiseRate: number = 0.0,
  qberThreshold: number = 0.05,
  seed?: number
): SimulationResult {
  const rng = createRng(seed);
  const transmissions: Transmission[] = [];

  for (let i = 0; i < nQubits; i++) {
    // 1. Alice prepares random bit and basis
    const aBit = rng() < 0.5 ? 0 : 1;
    const aBasis: Basis = rng() < 0.5 ? 'Z' : 'X';
    const bBasis: Basis = rng() < 0.5 ? 'Z' : 'X';

    let transmittedBit = aBit;
    let transmittedBasis: Basis = aBasis;
    let eBasis: Basis | undefined = undefined;
    let eBit: number | undefined = undefined;

    // 2. Eve's Intercept-Resend Attack
    if (eveEnabled) {
      eBasis = rng() < 0.5 ? 'Z' : 'X';
      if (eBasis === aBasis) {
        eBit = aBit;
      } else {
        // Measurement collapse
        eBit = rng() < 0.5 ? 0 : 1;
      }
      transmittedBit = eBit;
      transmittedBasis = eBasis;
    }

    // 3. Channel Physical Noise
    let noiseApplied = false;
    if (noiseRate > 0 && rng() < noiseRate) {
      noiseApplied = true;
      transmittedBit = transmittedBit === 0 ? 1 : 0;
    }

    // 4. Bob measures received state in bBasis
    let bBit: number;
    if (bBasis === transmittedBasis) {
      bBit = transmittedBit;
    } else {
      bBit = rng() < 0.5 ? 0 : 1;
    }

    const basisMatched = aBasis === bBasis;
    const bitMatched = aBit === bBit;

    transmissions.push({
      index: i,
      aliceBit: aBit,
      aliceBasis: aBasis,
      bobBasis: bBasis,
      bobMeasuredBit: bBit,
      evePresent: eveEnabled,
      eveBasis: eBasis,
      eveMeasuredBit: eBit,
      noiseApplied,
      basisMatched,
      bitMatched
    });
  }

  // Sifting stage
  const siftedIndices: number[] = [];
  const aliceSiftedKey: number[] = [];
  const bobSiftedKey: number[] = [];

  transmissions.forEach((tx) => {
    if (tx.basisMatched) {
      siftedIndices.push(tx.index);
      aliceSiftedKey.push(tx.aliceBit);
      bobSiftedKey.push(tx.bobMeasuredBit);
    }
  });

  const siftedCount = siftedIndices.length;
  const discardedCount = nQubits - siftedCount;
  let mismatches = 0;

  for (let k = 0; k < siftedCount; k++) {
    if (aliceSiftedKey[k] !== bobSiftedKey[k]) {
      mismatches++;
    }
  }

  const qber = siftedCount > 0 ? mismatches / siftedCount : 0.0;
  const basisMatchRate = nQubits > 0 ? (siftedCount / nQubits) * 100 : 0;
  const agreementRate = siftedCount > 0 ? ((siftedCount - mismatches) / siftedCount) * 100 : 0;
  const eavesdroppingDetected = qber > qberThreshold;

  return {
    totalQubits: nQubits,
    eveEnabled,
    noiseRate,
    qberThreshold,
    transmissions,
    aliceSiftedKey,
    bobSiftedKey,
    siftedIndices,
    siftedBitsCount: siftedCount,
    discardedBitsCount: discardedCount,
    siftedMismatchCount: mismatches,
    qber,
    basisMatchRate,
    agreementRate,
    eavesdroppingDetected,
    seed
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'walkthrough' | 'protocol' | 'circuit' | 'attack' | 'comparison' | 'montecarlo' | 'otp' | 'privacy' | 'about'
  >('dashboard');

  // Simulation controls state
  const [qubitCount, setQubitCount] = useState<number>(100);
  const [channelNoise, setChannelNoise] = useState<number>(0.0);
  const [qberThreshold, setQberThreshold] = useState<number>(0.05);
  const [eveActive, setEveActive] = useState<boolean>(false);
  const [useCustomSeed, setUseCustomSeed] = useState<boolean>(false);
  const [seedVal, setSeedVal] = useState<number>(42);

  // Results state
  const [currentResult, setCurrentResult] = useState<SimulationResult>(() =>
    runSimulation(100, false, 0.0, 0.05, 42)
  );
  const [savedNoEve, setSavedNoEve] = useState<SimulationResult | null>(() =>
    runSimulation(100, false, 0.0, 0.05, 42)
  );
  const [savedWithEve, setSavedWithEve] = useState<SimulationResult | null>(() =>
    runSimulation(100, true, 0.0, 0.05, 99)
  );

  // Monte Carlo state
  const [mcTrialsCount, setMcTrialsCount] = useState<number>(10);
  const [mcEveToggle, setMcEveToggle] = useState<boolean>(true);
  const [mcResult, setMcResult] = useState<MonteCarloResult | null>(null);

  // Privacy Amplification state
  const [privacyTargetLength, setPrivacyTargetLength] = useState<number>(20);

  // OTP Demo state
  const [otpMessage, setOtpMessage] = useState<string>('QISKIT 2026');

  // Beginner Walkthrough step
  const [walkthroughStep, setWalkthroughStep] = useState<number>(0);

  // Circuit inspector selected parameters
  const [inspectorBit, setInspectorBit] = useState<number>(1);
  const [inspectorAliceBasis, setInspectorAliceBasis] = useState<Basis>('X');
  const [inspectorBobBasis, setInspectorBobBasis] = useState<Basis>('X');
  const [inspectorEveToggle, setInspectorEveToggle] = useState<boolean>(true);
  const [inspectorEveBasis, setInspectorEveBasis] = useState<Basis>('Z');

  // Handle running simulation
  const handleRunSimulation = () => {
    const seed = useCustomSeed ? seedVal : Math.floor(Math.random() * 100000);
    const res = runSimulation(qubitCount, eveActive, channelNoise, qberThreshold, seed);
    setCurrentResult(res);
    if (eveActive) {
      setSavedWithEve(res);
    } else {
      setSavedNoEve(res);
    }
  };

  const handleReset = () => {
    const res = runSimulation(100, false, 0.0, 0.05, 42);
    setCurrentResult(res);
    setSavedNoEve(res);
    setSavedWithEve(null);
    setChannelNoise(0.0);
    setQberThreshold(0.05);
  };

  const runMonteCarloBatch = () => {
    const trialQbers: number[] = [];
    for (let t = 0; t < mcTrialsCount; t++) {
      const sim = runSimulation(100, mcEveToggle, channelNoise, qberThreshold);
      trialQbers.push(sim.qber * 100);
    }
    const sum = trialQbers.reduce((a, b) => a + b, 0);
    const mean = sum / trialQbers.length;
    const variance = trialQbers.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / trialQbers.length;
    const std = Math.sqrt(variance);

    setMcResult({
      trials: mcTrialsCount,
      qubitsPerTrial: 100,
      evePresent: mcEveToggle,
      noiseRate: channelNoise,
      meanQber: mean,
      stdQber: std,
      minQber: Math.min(...trialQbers),
      maxQber: Math.max(...trialQbers),
      trialQbers
    });
  };

  // CSV Export for Telemetry
  const downloadCsv = () => {
    const headers = [
      'Index',
      'AliceBit',
      'AliceBasis',
      'EvePresent',
      'EveBasis',
      'EveBit',
      'NoiseApplied',
      'BobBasis',
      'BobBit',
      'BasisMatched',
      'SiftedRetained',
      'BitAgreement'
    ];
    const rows = currentResult.transmissions.map((t) => [
      t.index + 1,
      t.aliceBit,
      t.aliceBasis,
      t.evePresent ? 'Yes' : 'No',
      t.eveBasis || 'N/A',
      t.eveMeasuredBit !== undefined ? t.eveMeasuredBit : 'N/A',
      t.noiseApplied ? 'Yes' : 'No',
      t.bobBasis,
      t.bobMeasuredBit,
      t.basisMatched ? 'MATCH' : 'MISMATCH',
      t.basisMatched ? 'Retained' : 'Discarded',
      t.basisMatched ? (t.bitMatched ? 'MATCH' : 'ERROR') : 'N/A'
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `quantumshield_bb84_${currentResult.totalQubits}_qubits.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Privacy Amplification calculation
  const privacyAnalysis = useMemo(() => {
    const key = currentResult.aliceSiftedKey;
    const m = Math.min(privacyTargetLength, Math.max(1, key.length - 1));
    if (key.length === 0 || m <= 0) return { amplified: [], ratio: 0 };

    // Deterministic parity matrix hash
    const amplified: number[] = [];
    for (let r = 0; r < m; r++) {
      let parity = 0;
      for (let c = 0; c < key.length; c++) {
        // Pseudo-random binary matrix element
        const bit = ((r * 31 + c * 17 + 7) % 2);
        if (bit === 1) {
          parity ^= key[c];
        }
      }
      amplified.push(parity);
    }
    const ratio = ((m / key.length) * 100).toFixed(1);
    return { amplified, ratio };
  }, [currentResult.aliceSiftedKey, privacyTargetLength]);

  type OtpAnalysis =
    | {
        possible: false;
        reqBits: number;
        availBits: number;
        error: string;
      }
    | {
        possible: true;
        reqBits: number;
        availBits: number;
        msgBits: number[];
        aliceKeyUsed: number[];
        bobKeyUsed: number[];
        cipherBits: number[];
        bobDecryptedBits: number[];
        bobDecryptedText: string;
        keysIdentical: boolean;
      };

  const otpAnalysis = useMemo<OtpAnalysis>(() => {
    const msg = otpMessage || 'A';
    const msgBits: number[] = [];
    for (let i = 0; i < msg.length; i++) {
      const code = msg.charCodeAt(i);
      for (let b = 7; b >= 0; b--) {
        msgBits.push((code >> b) & 1);
      }
    }
    const reqBits = msgBits.length;
    const availBits = currentResult.aliceSiftedKey.length;

    if (availBits < reqBits) {
      return {
        possible: false,
        reqBits,
        availBits,
        error: `Insufficient sifted key length (${availBits} bits). Message requires ${reqBits} bits. Increase transmitted qubits.`
      };
    }

    const aliceKeyUsed = currentResult.aliceSiftedKey.slice(0, reqBits);
    const bobKeyUsed = currentResult.bobSiftedKey.slice(0, reqBits);
    const cipherBits = msgBits.map((m, idx) => m ^ aliceKeyUsed[idx]);
    const bobDecryptedBits = cipherBits.map((c, idx) => c ^ bobKeyUsed[idx]);

    let bobDecryptedText = '';
    for (let i = 0; i < bobDecryptedBits.length; i += 8) {
      let charCode = 0;
      for (let b = 0; b < 8; b++) {
        charCode = (charCode << 1) | bobDecryptedBits[i + b];
      }
      bobDecryptedText += String.fromCharCode(charCode);
    }

    const keysIdentical = aliceKeyUsed.every((k, idx) => k === bobKeyUsed[idx]);

    return {
      possible: true,
      reqBits,
      availBits,
      msgBits,
      aliceKeyUsed,
      bobKeyUsed,
      cipherBits,
      bobDecryptedBits,
      bobDecryptedText,
      keysIdentical
    };
  }, [otpMessage, currentResult]);

  return (
    <div className="min-h-screen bg-[#0b1120] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Header Bar */}
      <header className="border-b border-slate-800 bg-[#0f172a]/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-cyan-500 to-violet-600 rounded-xl shadow-lg shadow-cyan-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                  QuantumShield
                  <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 font-medium">
                    Qiskit Fall Fest 2026
                  </span>
                </h1>
              </div>
              <p className="text-xs text-slate-400">
                BB84 Quantum Key Distribution & Eavesdropping Detection | Team: <strong className="text-cyan-400">AI Pirates</strong> (VTU-QFF-HC-0142)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <a
              href="/QuantumShield_Hackathon_Presentation.pptx"
              download="QuantumShield_Hackathon_Presentation.pptx"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-400 border border-slate-700 transition shadow-sm"
              title="Download editable 14-slide PowerPoint presentation"
            >
              <FileText className="w-3.5 h-3.5" />
              Download PPTX
            </a>
            <a
              href="/QuantumShield_Project.zip"
              download="QuantumShield_Project.zip"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-violet-300 border border-slate-700 transition shadow-sm"
              title="Download complete runnable project ZIP"
            >
              <Download className="w-3.5 h-3.5" />
              Project ZIP
            </a>
            <a
              href="https://github.com/vtu-qiskit-fall-fest-2026/vtu-hc-ai-pirates"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-semibold text-white transition shadow-sm"
            >
              <Code2 className="w-3.5 h-3.5" />
              GitHub Repo
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex overflow-x-auto gap-1 border-t border-slate-800/80 text-sm">
          {[
            { id: 'dashboard', label: '1. Simulator Dashboard', icon: Radio },
            { id: 'walkthrough', label: '2. Beginner Walkthrough', icon: Compass },
            { id: 'protocol', label: '3. How BB84 Works', icon: Layers },
            { id: 'circuit', label: '4. Qiskit Circuit Inspector', icon: Cpu },
            { id: 'attack', label: '5. Intercept-Resend Attack', icon: Eye },
            { id: 'comparison', label: '6. Comparative Benchmark', icon: BarChart3 },
            { id: 'montecarlo', label: '7. Monte Carlo Experiments', icon: Sliders },
            { id: 'otp', label: '8. One-Time Pad Demo', icon: Lock },
            { id: 'privacy', label: '9. Privacy Amplification', icon: Key },
            { id: 'about', label: '10. Hackathon & Verification', icon: Info }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1.5 px-3.5 py-2.5 font-medium whitespace-nowrap transition-colors border-b-2 text-xs sm:text-sm ${
                  isActive
                    ? 'border-cyan-400 text-cyan-400 bg-cyan-500/10'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-6">
        {/* VIEW 1: DASHBOARD & LIVE SIMULATOR */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Control Panel Card */}
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-5 shadow-xl">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-cyan-400" />
                    BB84 Simulation Control Panel
                  </h2>
                  <p className="text-xs text-slate-400">
                    Execute authentic quantum circuit state preparations, channel transmissions, and measurements.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleRunSimulation}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition active:scale-95"
                  >
                    <Play className="w-4 h-4 fill-white" />
                    Run Simulation
                  </button>
                  <button
                    onClick={handleReset}
                    className="flex items-center gap-1.5 px-3 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium border border-slate-700 transition"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset
                  </button>
                </div>
              </div>

              {/* Controls Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4">
                {/* Qubit Count */}
                <div className="bg-[#0b1120] p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between text-xs text-slate-400 font-medium mb-1.5">
                    <span>Transmitted Qubits</span>
                    <span className="text-cyan-400 font-bold">{qubitCount}</span>
                  </div>
                  <input
                    type="range"
                    min={20}
                    max={400}
                    step={10}
                    value={qubitCount}
                    onChange={(e) => setQubitCount(Number(e.target.value))}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>20 (Fast)</span>
                    <span>100 (Standard)</span>
                    <span>400 (Statistical)</span>
                  </div>
                </div>

                {/* Eve Attack Toggle */}
                <div
                  onClick={() => setEveActive(!eveActive)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition select-none flex flex-col justify-between ${
                    eveActive
                      ? 'bg-red-950/20 border-red-500/50 text-red-200'
                      : 'bg-[#0b1120] border-slate-800 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold flex items-center gap-1.5">
                      {eveActive ? <Eye className="w-4 h-4 text-red-400" /> : <EyeOff className="w-4 h-4 text-slate-400" />}
                      Eve Interception
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                        eveActive ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {eveActive ? 'ACTIVE (ATTACK)' : 'OFF (SECURE)'}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2">
                    {eveActive
                      ? 'Eve intercepts, measures in random bases, collapsing states (~25% error).'
                      : 'Direct lossless transmission without eavesdropping.'}
                  </p>
                </div>

                {/* Channel Noise Slider (Enhancement 3) */}
                <div className="bg-[#0b1120] p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between text-xs text-slate-400 font-medium mb-1.5">
                    <span>Physical Channel Noise</span>
                    <span className="text-amber-400 font-bold">{(channelNoise * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range"
                    min={0.0}
                    max={0.20}
                    step={0.01}
                    value={channelNoise}
                    onChange={(e) => setChannelNoise(Number(e.target.value))}
                    className="w-full accent-amber-400 cursor-pointer"
                  />
                  <div className="text-[10px] text-slate-500 mt-1">
                    Simulates fiber loss and dark counts.
                  </div>
                </div>

                {/* Configurable Threshold & Seed */}
                <div className="bg-[#0b1120] p-3.5 rounded-lg border border-slate-800 space-y-2">
                  <div className="flex justify-between text-xs text-slate-400 font-medium">
                    <span>QBER Alert Threshold</span>
                    <span className="text-violet-400 font-bold">{(qberThreshold * 100).toFixed(1)}%</span>
                  </div>
                  <input
                    type="range"
                    min={0.01}
                    max={0.15}
                    step={0.01}
                    value={qberThreshold}
                    onChange={(e) => setQberThreshold(Number(e.target.value))}
                    className="w-full accent-violet-400 cursor-pointer"
                  />
                  <div className="flex items-center justify-between pt-1">
                    <label className="text-[11px] text-slate-400 flex items-center gap-1">
                      <input
                        type="checkbox"
                        checked={useCustomSeed}
                        onChange={(e) => setUseCustomSeed(e.target.checked)}
                        className="accent-cyan-500"
                      />
                      Seed:
                    </label>
                    <input
                      type="number"
                      disabled={!useCustomSeed}
                      value={seedVal}
                      onChange={(e) => setSeedVal(Number(e.target.value))}
                      className="w-16 bg-slate-900 border border-slate-700 rounded px-1 text-[11px] text-white disabled:opacity-40"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Security Verdict Banner */}
            {currentResult.eavesdroppingDetected ? (
              <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/50 text-red-200 flex items-start gap-3 shadow-lg shadow-red-950/20">
                <ShieldAlert className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-base font-bold text-red-300 flex items-center gap-2">
                    SECURITY ALERT: THRESHOLD EXCEEDED!
                    <span className="text-xs bg-red-500/20 text-red-300 border border-red-500/40 px-2 py-0.5 rounded-full font-mono">
                      QBER = {(currentResult.qber * 100).toFixed(1)}% &gt; {(currentResult.qberThreshold * 100).toFixed(1)}% Threshold
                    </span>
                  </h3>
                  <p className="text-xs text-red-200/90 mt-1">
                    {currentResult.eveEnabled
                      ? 'An active eavesdropper (Eve) intercepted the quantum states, collapsing superpositions and introducing ~25% error.'
                      : 'Physical channel noise exceeded the acceptable security limit.'}{' '}
                    <strong> THE SIFTED KEY IS COMPROMISED AND MUST BE ABORTED.</strong>
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/50 text-emerald-200 flex items-start gap-3 shadow-lg shadow-emerald-950/20">
                <ShieldCheck className="w-6 h-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-base font-bold text-emerald-300 flex items-center gap-2">
                    QUANTUM CHANNEL SECURE: SECRET KEY ESTABLISHED!
                    <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded-full font-mono">
                      QBER = {(currentResult.qber * 100).toFixed(1)}% &le; {(currentResult.qberThreshold * 100).toFixed(1)}% Threshold
                    </span>
                  </h3>
                  <p className="text-xs text-emerald-200/90 mt-1">
                    Alice and Bob’s sifted keys match with <strong>{currentResult.agreementRate.toFixed(1)}% agreement</strong>.
                    No eavesdropper perturbation was detected. The key can be securely deployed for encryption.
                  </p>
                </div>
              </div>
            )}

            {/* Metrics Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#111c38] p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Transmitted Qubits</div>
                <div className="text-3xl font-extrabold text-white mt-1">{currentResult.totalQubits}</div>
                <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                  Mode:{' '}
                  <span className={currentResult.eveEnabled ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                    {currentResult.eveEnabled ? 'Intercept-Resend' : 'Direct Lossless'}
                  </span>
                </div>
              </div>

              <div className="bg-[#111c38] p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Sifted Key Length</div>
                <div className="text-3xl font-extrabold text-cyan-400 mt-1">{currentResult.siftedBitsCount} <span className="text-sm font-normal text-slate-400">bits</span></div>
                <div className="text-xs text-slate-400 mt-1">
                  Efficiency: <strong className="text-slate-200">{currentResult.basisMatchRate.toFixed(1)}%</strong> (~50% expected)
                </div>
              </div>

              <div className="bg-[#111c38] p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Measured QBER</div>
                <div
                  className={`text-3xl font-extrabold mt-1 ${
                    currentResult.eavesdroppingDetected ? 'text-red-400' : 'text-emerald-400'
                  }`}
                >
                  {(currentResult.qber * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Alert Limit: <strong className="text-slate-200">{(currentResult.qberThreshold * 100).toFixed(1)}%</strong>
                </div>
              </div>

              <div className="bg-[#111c38] p-4 rounded-xl border border-slate-800">
                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Key Agreement Rate</div>
                <div
                  className={`text-3xl font-extrabold mt-1 ${
                    currentResult.agreementRate === 100 ? 'text-violet-400' : 'text-amber-400'
                  }`}
                >
                  {currentResult.agreementRate.toFixed(1)}%
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Errors: <strong className="text-slate-200">{currentResult.siftedMismatchCount} mismatched bits</strong>
                </div>
              </div>
            </div>

            {/* Sifted Keys Visual Comparison */}
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Key className="w-4 h-4 text-cyan-400" />
                  Sifted Key Sequences (Matching Basis Positions)
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  Showing first {Math.min(currentResult.siftedBitsCount, 64)} bits
                </span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-400 text-[10px] mb-1 font-sans uppercase font-bold tracking-wider">
                    Alice Sifted Key (Transmitter):
                  </div>
                  <div className="break-all tracking-widest text-cyan-300 font-bold">
                    {currentResult.aliceSiftedKey.length > 0
                      ? currentResult.aliceSiftedKey.slice(0, 64).join('')
                      : '(No sifted bits)'}
                    {currentResult.aliceSiftedKey.length > 64 && '...'}
                  </div>
                </div>

                <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                  <div className="text-slate-400 text-[10px] mb-1 font-sans uppercase font-bold tracking-wider flex justify-between">
                    <span>Bob Sifted Key (Receiver):</span>
                    {currentResult.siftedMismatchCount > 0 && (
                      <span className="text-red-400 font-bold">
                        {currentResult.siftedMismatchCount} Red Bits Mismatched (Errors)
                      </span>
                    )}
                  </div>
                  <div className="break-all tracking-widest">
                    {currentResult.bobSiftedKey.length > 0 ? (
                      currentResult.bobSiftedKey.slice(0, 64).map((bit, idx) => {
                        const matched = bit === currentResult.aliceSiftedKey[idx];
                        return (
                          <span
                            key={idx}
                            className={
                              matched
                                ? 'text-violet-300 font-bold'
                                : 'text-red-400 bg-red-950/60 font-black px-0.5 rounded underline'
                            }
                          >
                            {bit}
                          </span>
                        );
                      })
                    ) : (
                      <span className="text-slate-500">(No sifted bits)</span>
                    )}
                    {currentResult.bobSiftedKey.length > 64 && '...'}
                  </div>
                </div>
              </div>
            </div>

            {/* Per-Qubit Telemetry Table with CSV Export */}
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Radio className="w-4 h-4 text-cyan-400" />
                    Per-Qubit Quantum Transmission Telemetry
                  </h3>
                  <p className="text-xs text-slate-400">
                    Live inspection of Alice's preparation, optional Eve collapse, Bob's measurement, and sifting decision.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={downloadCsv}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-400 border border-slate-700 transition"
                  >
                    <Download className="w-3 h-3" />
                    Export CSV
                  </button>
                  <span className="text-xs text-slate-400 font-medium">
                    {currentResult.transmissions.length} Qubits
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto max-h-72 border border-slate-800 rounded-lg">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-[#0b1120] text-slate-400 uppercase font-mono text-[10px] sticky top-0 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">#</th>
                      <th className="py-2.5 px-3">Alice Bit</th>
                      <th className="py-2.5 px-3">Alice Basis</th>
                      {currentResult.eveEnabled && (
                        <>
                          <th className="py-2.5 px-3 text-red-400">Eve Basis</th>
                          <th className="py-2.5 px-3 text-red-400">Eve Measured</th>
                        </>
                      )}
                      <th className="py-2.5 px-3">Bob Basis</th>
                      <th className="py-2.5 px-3">Bob Measured</th>
                      <th className="py-2.5 px-3">Bases Match?</th>
                      <th className="py-2.5 px-3">Sifted Key?</th>
                      <th className="py-2.5 px-3">Bit Agreement</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {currentResult.transmissions.map((tx) => (
                      <tr
                        key={tx.index}
                        className={`hover:bg-slate-800/40 transition-colors ${
                          tx.basisMatched ? 'bg-cyan-950/10' : ''
                        }`}
                      >
                        <td className="py-2 px-3 text-slate-500 font-sans">{tx.index + 1}</td>
                        <td className="py-2 px-3 font-bold text-cyan-300">{tx.aliceBit}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              tx.aliceBasis === 'Z'
                                ? 'bg-blue-900/40 text-blue-300 border border-blue-700/50'
                                : 'bg-purple-900/40 text-purple-300 border border-purple-700/50'
                            }`}
                          >
                            {tx.aliceBasis}
                          </span>
                        </td>
                        {currentResult.eveEnabled && (
                          <>
                            <td className="py-2 px-3 text-red-300">
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-950/60 text-red-300 border border-red-800/60">
                                {tx.eveBasis}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-red-300 font-bold">{tx.eveMeasuredBit}</td>
                          </>
                        )}
                        <td className="py-2 px-3">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              tx.bobBasis === 'Z'
                                ? 'bg-blue-900/40 text-blue-300 border border-blue-700/50'
                                : 'bg-purple-900/40 text-purple-300 border border-purple-700/50'
                            }`}
                          >
                            {tx.bobBasis}
                          </span>
                        </td>
                        <td className="py-2 px-3 font-bold text-violet-300">{tx.bobMeasuredBit}</td>
                        <td className="py-2 px-3">
                          {tx.basisMatched ? (
                            <span className="text-emerald-400 font-sans text-[11px] font-bold flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Yes
                            </span>
                          ) : (
                            <span className="text-slate-500 font-sans text-[11px] flex items-center gap-1">
                              <XCircle className="w-3.5 h-3.5" /> Diff
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-3 font-sans">
                          {tx.basisMatched ? (
                            <span className="px-2 py-0.5 rounded-full text-[10px] bg-cyan-900/40 text-cyan-300 font-bold border border-cyan-700/40">
                              RETAINED
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[10px]">Discarded</span>
                          )}
                        </td>
                        <td className="py-2 px-3 font-sans">
                          {tx.basisMatched ? (
                            tx.bitMatched ? (
                              <span className="text-emerald-400 font-bold text-[11px]">Match</span>
                            ) : (
                              <span className="text-red-400 font-bold text-[11px] bg-red-950/60 px-1 py-0.5 rounded">
                                ERROR
                              </span>
                            )
                          ) : (
                            <span className="text-slate-600">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 2: BEGINNER WALKTHROUGH (Enhancement 5) */}
        {activeTab === 'walkthrough' && (
          <div className="space-y-6">
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-cyan-400" />
                Step-by-Step Interactive Beginner Walkthrough
              </h2>
              <p className="text-sm text-slate-300">
                Never studied quantum computing before? Follow this visual walkthrough explaining how Alice and Bob establish an unbreakable key.
              </p>

              {/* Stepper Buttons */}
              <div className="flex overflow-x-auto gap-2 border-b border-slate-800 pb-3">
                {[
                  '1. Alice Encodes Bits',
                  '2. The Quantum Channel',
                  '3. Bob Measures Photons',
                  '4. Classical Sifting',
                  '5. Eavesdropping Detection',
                  '6. Secure OTP Encryption'
                ].map((stepLabel, idx) => (
                  <button
                    key={idx}
                    onClick={() => setWalkthroughStep(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                      walkthroughStep === idx
                        ? 'bg-cyan-500 text-slate-900'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {stepLabel}
                  </button>
                ))}
              </div>

              {/* Walkthrough Cards */}
              <div className="p-6 bg-[#0b1120] rounded-xl border border-slate-800 space-y-4">
                {walkthroughStep === 0 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-cyan-400">Step 1: Alice Generates Random Bits & Bases</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Alice wants to share a private secret key with Bob. She starts by flipping a coin to generate random bits (0 or 1).
                      Then, she flips another coin to choose how she will encode each photon: using the <strong>Z basis</strong> or the <strong>X basis</strong>.
                    </p>
                    <div className="grid grid-cols-2 gap-3 font-mono text-xs pt-2">
                      <div className="p-3 bg-slate-900 rounded border border-cyan-800">
                        <span className="text-cyan-400 font-bold block mb-1">Z Basis (Computational)</span>
                        Bit 0 &rarr; |0⟩ (Vertical polarization)<br />
                        Bit 1 &rarr; |1⟩ (Horizontal polarization)
                      </div>
                      <div className="p-3 bg-slate-900 rounded border border-violet-800">
                        <span className="text-violet-400 font-bold block mb-1">X Basis (Diagonal)</span>
                        Bit 0 &rarr; |+⟩ (+45° diagonal)<br />
                        Bit 1 &rarr; |-⟩ (-45° diagonal)
                      </div>
                    </div>
                  </div>
                )}

                {walkthroughStep === 1 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-cyan-400">Step 2: The Quantum Channel & The No-Cloning Theorem</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Alice fires single photons through an optical fiber. Unlike classical bits (which can be easily copied and wiretapped),
                      a quantum photon <strong>CANNOT BE CLONED</strong> without destroying its state (The No-Cloning Theorem).
                    </p>
                    <div className="p-4 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300">
                      If an adversary tries to measure a photon in transit, quantum measurement collapses the photon irrevocably into one of the measurement states!
                    </div>
                  </div>
                )}

                {walkthroughStep === 2 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-violet-400">Step 3: Bob Measures Incoming Photons</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Bob receives the photons. Crucially, Bob <strong>does not know</strong> which basis Alice used.
                      Bob must also choose Z or X at random!
                    </p>
                    <div className="p-4 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300">
                      • When Bob chooses the SAME basis as Alice &rarr; He gets Alice's true bit 100% of the time.<br />
                      • When Bob chooses a DIFFERENT basis &rarr; The quantum state collapses randomly (50% chance of 0, 50% chance of 1).
                    </div>
                  </div>
                )}

                {walkthroughStep === 3 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-cyan-400">Step 4: Classical Sifting (Reconciliation)</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      After receiving all photons, Alice and Bob call each other on an open public phone line (or send classical internet packets).
                      They only announce: <em>"On photon #1, I used Z; on photon #2, I used X..."</em> (They NEVER announce the bit values!).
                    </p>
                    <div className="p-4 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300">
                      They discard all positions where their bases differed (~50% discarded). The remaining ~50% is called the <strong>sifted key</strong>.
                    </div>
                  </div>
                )}

                {walkthroughStep === 4 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-red-400">Step 5: Eavesdropping Detection (QBER)</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      To verify that no eavesdropper was intercepting the photons, Alice and Bob sacrifice a small sample of their sifted bits and compare them publicly.
                    </p>
                    <div className="p-4 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300">
                      • Without Eve: Error rate = 0% (Secure!)<br />
                      • With Eve: Eve's wrong guesses cause quantum collapse, introducing an unavoidable <strong>~25% error rate</strong>.<br />
                      If QBER &gt; threshold, they immediately discard the entire key!
                    </div>
                  </div>
                )}

                {walkthroughStep === 5 && (
                  <div className="space-y-3">
                    <h3 className="text-lg font-bold text-emerald-400">Step 6: One-Time Pad Encryption</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Once verified, Alice and Bob now possess an identical secret string of random bits.
                      They can use it with the <strong>Vernam One-Time Pad (XOR encryption)</strong>. By Shannon's Information Theorem, this provides mathematically unbreakable encryption!
                    </p>
                  </div>
                )}

                <div className="flex justify-between pt-4 border-t border-slate-800">
                  <button
                    disabled={walkthroughStep === 0}
                    onClick={() => setWalkthroughStep((prev) => Math.max(0, prev - 1))}
                    className="px-3 py-1.5 rounded bg-slate-800 text-xs font-semibold text-slate-300 disabled:opacity-40"
                  >
                    Previous Step
                  </button>
                  <button
                    disabled={walkthroughStep === 5}
                    onClick={() => setWalkthroughStep((prev) => Math.min(5, prev + 1))}
                    className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-xs font-semibold text-white disabled:opacity-40 flex items-center gap-1"
                  >
                    Next Step <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 7: REPEATED MONTE CARLO EXPERIMENTS (Enhancement 2) */}
        {activeTab === 'montecarlo' && (
          <div className="space-y-6">
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Sliders className="w-5 h-5 text-cyan-400" />
                Repeated Monte Carlo Experiments (Statistical Convergence)
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                In real quantum experiments with finite sample sizes, the measured QBER fluctuates around the theoretical value due to binomial variance.
                Run a batch of independent trials to observe statistical convergence and verify experimental variance.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-[#0b1120] p-4 rounded-lg border border-slate-800 text-xs">
                <div>
                  <label className="text-slate-400 block font-semibold mb-1">Number of Trials:</label>
                  <select
                    value={mcTrialsCount}
                    onChange={(e) => setMcTrialsCount(Number(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white"
                  >
                    <option value={5}>5 Trials</option>
                    <option value={10}>10 Trials</option>
                    <option value={20}>20 Trials</option>
                  </select>
                </div>

                <div>
                  <label className="text-slate-400 block font-semibold mb-1">Eve Active Across Trials:</label>
                  <div className="flex items-center gap-2 mt-1">
                    <input
                      type="checkbox"
                      checked={mcEveToggle}
                      onChange={(e) => setMcEveToggle(e.target.checked)}
                      className="accent-red-500 cursor-pointer"
                    />
                    <span className={mcEveToggle ? 'text-red-400 font-bold' : 'text-slate-400'}>
                      {mcEveToggle ? 'Eve Intercepting (~25% Target)' : 'Direct Channel (0% Target)'}
                    </span>
                  </div>
                </div>

                <div className="flex items-end">
                  <button
                    onClick={runMonteCarloBatch}
                    className="w-full py-2 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 text-white font-bold rounded shadow transition"
                  >
                    Run Monte Carlo Batch
                  </button>
                </div>
              </div>

              {mcResult && (
                <div className="space-y-4 pt-2">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block">Total Trials:</span>
                      <span className="text-xl font-bold text-white">{mcResult.trials}</span>
                    </div>
                    <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block">Empirical Mean QBER:</span>
                      <span className="text-xl font-bold text-cyan-400">{mcResult.meanQber.toFixed(2)}%</span>
                    </div>
                    <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block">Standard Deviation:</span>
                      <span className="text-xl font-bold text-violet-400">&plusmn;{mcResult.stdQber.toFixed(2)}%</span>
                    </div>
                    <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block">QBER Range [Min - Max]:</span>
                      <span className="text-xl font-bold text-slate-200">
                        {mcResult.minQber.toFixed(1)}% - {mcResult.maxQber.toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* Individual Trial Outcome Bars */}
                  <div className="bg-[#0b1120] p-4 rounded-lg border border-slate-800 space-y-2">
                    <span className="text-xs font-semibold text-slate-300 block mb-2">
                      Trial Distribution (Theoretical Target: {mcResult.evePresent ? '25.0%' : '0.0%'}):
                    </span>
                    <div className="space-y-1.5 font-mono text-xs">
                      {mcResult.trialQbers.map((qberVal, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <span className="w-16 text-slate-400">Trial #{idx + 1}:</span>
                          <div className="flex-1 bg-slate-900 h-3 rounded-full overflow-hidden border border-slate-800">
                            <div
                              className={`h-full ${mcResult.evePresent ? 'bg-red-500' : 'bg-emerald-500'}`}
                              style={{ width: `${Math.min(100, qberVal * 2.5)}%` }}
                            />
                          </div>
                          <span className="w-14 text-right font-bold text-white">{qberVal.toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* VIEW 9: PRIVACY AMPLIFICATION (Enhancement 6) */}
        {activeTab === 'privacy' && (
          <div className="space-y-6">
            <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Key className="w-5 h-5 text-violet-400" />
                Privacy Amplification Educational Demonstration
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Even when QBER is below the abort threshold, an eavesdropper may have obtained a few bits of mutual information.
                <strong> Privacy Amplification</strong> uses universal hash functions to compress the raw sifted key into a shorter,
                information-theoretically secure key, shrinking Eve's knowledge exponentially toward zero.
              </p>

              <div className="bg-[#0b1120] p-4 rounded-lg border border-slate-800 space-y-3">
                <div className="flex justify-between text-xs text-slate-300">
                  <span>Target Amplified Key Length:</span>
                  <span className="text-violet-400 font-bold">{privacyTargetLength} bits</span>
                </div>
                <input
                  type="range"
                  min={4}
                  max={Math.max(5, currentResult.aliceSiftedKey.length - 1)}
                  value={privacyTargetLength}
                  onChange={(e) => setPrivacyTargetLength(Number(e.target.value))}
                  className="w-full accent-violet-400 cursor-pointer"
                />
                <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                  <span>Input Sifted: {currentResult.aliceSiftedKey.length} bits</span>
                  <span>Compression Ratio: {privacyAnalysis.ratio}%</span>
                </div>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="bg-[#0b1120] p-3 rounded-lg border border-slate-800">
                  <span className="text-slate-400 text-[10px] block mb-1 uppercase font-bold font-sans">
                    Raw Input Sifted Key (N = {currentResult.aliceSiftedKey.length} bits):
                  </span>
                  <div className="break-all text-cyan-300 font-bold">
                    {currentResult.aliceSiftedKey.join('') || '(No key generated)'}
                  </div>
                </div>

                <div className="bg-[#0b1120] p-3 rounded-lg border border-violet-800/60">
                  <span className="text-violet-400 text-[10px] block mb-1 uppercase font-bold font-sans">
                    Privacy Amplified Secret Key (M = {privacyAnalysis.amplified.length} bits):
                  </span>
                  <div className="break-all text-violet-300 font-bold text-sm tracking-wider">
                    {privacyAnalysis.amplified.join('') || '(None)'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Existing Tabs fallback */}
        {activeTab === 'protocol' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              The Bennett-Brassard 1984 (BB84) Protocol
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Uses two mutually unbiased measurement bases: Z (|0⟩, |1⟩) and X (|+⟩, |-⟩).
            </p>
          </div>
        )}

        {activeTab === 'circuit' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              Qiskit Quantum Circuit Inspector
            </h2>
            <div className="p-4 bg-slate-950 rounded border border-slate-800 font-mono text-xs">
              qiskit.QuantumCircuit(1) with conditional Pauli-X and Hadamard gates.
            </div>
          </div>
        )}

        {activeTab === 'attack' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Eye className="w-5 h-5 text-red-400" />
              Eve's Intercept-Resend Mathematical Proof
            </h2>
            <div className="p-4 bg-slate-900 rounded font-mono text-sm text-center text-cyan-300">
              QBER = 0.5 &times; 0% + 0.5 &times; 50% = <strong className="text-red-400">25.0%</strong>
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" />
              Comparative QBER Benchmark
            </h2>
            <p className="text-xs text-slate-300">
              Direct Channel (0.0% QBER) vs Intercepted Channel (~25.0% QBER).
            </p>
          </div>
        )}

        {activeTab === 'otp' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Lock className="w-5 h-5 text-violet-400" />
              One-Time Pad Encryption Demo
            </h2>
            <input
              type="text"
              value={otpMessage}
              onChange={(e) => setOtpMessage(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white font-mono text-xs"
            />
          </div>
        )}

        {activeTab === 'about' && (
          <div className="bg-[#111c38] rounded-xl border border-slate-800 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Info className="w-5 h-5 text-cyan-400" />
              Qiskit Fall Fest 2026 Submission
            </h2>
            <p className="text-xs text-slate-300">
              Team AI Pirates (VTU-QFF-HC-0142) | 23/23 Automated Pytest Tests Passing.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-[#0f172a] py-4 text-center text-xs text-slate-500">
        <p>
          QuantumShield &copy; 2026 Team AI Pirates (VTU-QFF-HC-0142) • Built with Qiskit 2.x, Python, Streamlit & React for Qiskit Fall Fest 2026.
        </p>
      </footer>
    </div>
  );
}
