# compare_simulator_vs_hardware.py

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import state_fidelity
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from scipy.stats import wasserstein_distance, entropy as shannon_entropy

from tokens import get_token_for

# 1) Setup IBM Runtime & récup token
token = get_token_for("Baptiste")
service = QiskitRuntimeService(channel="ibm_quantum", token=token)

# 2) Choix du backend QPU
backend_qpu = service.least_busy(simulator=False)
print("Hardware choisi :", backend_qpu.name)

# 3) Charger un modèle de bruit pour la comparaison simulée
noise_model = NoiseModel.from_backend(backend_qpu)

# 4) Préparer Sampler pour le hardware
sampler = Sampler(backend_qpu)

# 5) Générateur simple de circuits
def random_circuit(nb_qubits, depth):
    qc = QuantumCircuit(nb_qubits, nb_qubits)
    rng = np.random.default_rng()
    for _ in range(depth):
        q1 = rng.integers(nb_qubits)
        q2 = rng.choice([i for i in range(nb_qubits) if i != q1])
        qc.h(q1)
        qc.cx(q1, q2)
    qc.measure_all()
    return qc

# 6) Classical fidelity helper
def classical_fidelity(counts, ideal_counts):
    shots = sum(counts.values())
    ik = set(counts) | set(ideal_counts)
    p = np.array([counts.get(k,0)/shots for k in ik])
    q = np.array([ideal_counts.get(k,0)/shots for k in ik])
    return float((np.sqrt(p*q).sum())**2)

# 7) Boucle de collecte
records = []
sim_ideal = AerSimulator(method="statevector")
sim_noisy = AerSimulator(method="statevector", noise_model=noise_model)

for qc in [random_circuit(3,5) for _ in range(20)]:
    tq_i = transpile(qc, sim_ideal, optimization_level=0)
    tq_i.save_statevector()  
    t0 = time.perf_counter()
    res_i = sim_ideal.run(tq_i, shots=1024).result()
    t1 = time.perf_counter()
    rt_i = (t1 - t0)*1000
    sv_i = res_i.get_statevector()

    # ————————————————————————————————
    # 2) SIMULATION BRUITÉE (STATEVECTOR)
    # ————————————————————————————————
    tq_n = transpile(qc, sim_noisy, optimization_level=0)
    tq_n.save_statevector()  
    t0n = time.perf_counter()
    res_n = sim_noisy.run(tq_n, shots=1024).result()
    t1n = time.perf_counter()
    rt_n = (t1n - t0n)*1000
    sv_n = res_n.get_statevector()

    # ————————————————————————————————
    # 3) CALCUL DE LA STATE FIDELITY
    # ————————————————————————————————
    fidelity_state = state_fidelity(sv_i, sv_n)

    # ————————————————————————————————
    # 4) EXÉCUTION SUR QPU (COUNTS SEULEMENT)
    # ————————————————————————————————
    tq_h = transpile(qc, backend_qpu, optimization_level=0)
    t0h = time.perf_counter()
    job_h = sampler.run([tq_h], shots=1024)
    res_h = job_h.result()[0].data.meas
    t1h = time.perf_counter()
    rt_hw = (t1h - t0h)*1000
    counts_hw = res_h.get_counts()

    # ————————————————————————————————
    # 5) METRIQUES COUNTS (CLASSICAL FIDELITY, EMD)
    # ————————————————————————————————
    classical_fid = classical_fidelity(counts_hw, res_i.get_counts())
    emd_hw = wasserstein_distance(
        np.arange(len(counts_hw)), np.arange(len(counts_hw)),
        np.array(list(counts_hw.values()))/1024,
        np.ones(len(counts_hw))/len(counts_hw)
    )

    # ————————————————————————————————
    # 6) STOCKAGE
    # ————————————————————————————————
    records.append({
       "real_time_ideal_ms":    rt_i,
       "real_time_noisy_ms":    rt_n,
       "real_time_hardware_ms": rt_hw,
       "state_fidelity":        fidelity_state,
       "classical_fidelity_hw": classical_fid,
       "emd_hw_vs_uniform":     emd_hw
    })

# 8) DataFrame & visualisations
df = pd.DataFrame(records)

# Histogramme comparaison des temps
plt.figure()
plt.hist(df["real_time_ideal_ms"], bins=10, alpha=0.6, label="Ideal")
plt.hist(df["real_time_noisy_ms"], bins=10, alpha=0.6, label="Noisy")
plt.hist(df["real_time_hardware_ms"], bins=10, alpha=0.6, label="Hardware")
plt.xlabel("Real Time (ms)")
plt.ylabel("Count")
plt.legend()
plt.title("Ideal vs Noisy vs Hardware Times")
plt.show()

# Scatter fidelity vs hardware time
plt.figure()
plt.scatter(df["real_time_hardware_ms"], df["classical_fidelity_hw"], c='red', label="Classical Fidelity HW")
plt.scatter(df["real_time_hardware_ms"], df["state_fidelity"], c='blue', label="State Fidelity (Sim)")
plt.xlabel("Hardware Real Time (ms)")
plt.ylabel("Fidelity")
plt.legend()
plt.title("Fidelity vs Hardware Time")
plt.grid()
plt.show()

# Aperçu des données
print(df.describe())
print(df)

# Sauvegarde
df.to_csv("features_with_hardware.csv", index=False)
