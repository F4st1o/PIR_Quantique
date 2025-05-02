# compare_simulator_noise_features.py

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.quantum_info import state_fidelity

# Récupérer votre token IBM Quantum (ou remplacez par une string)
from tokens import get_token_for
token = get_token_for("Baptiste")

# Charger le modèle de bruit du backend IBM
service = QiskitRuntimeService(channel="ibm_quantum", token=token)
backends = service.backends()
print([b.name for b in backends])
backend = service.backend("ibm_brisbane")
noise_model = NoiseModel.from_backend(backend)


def random_circuit(nb_qubits: int, depth: int) -> QuantumCircuit:
    qc = QuantumCircuit(nb_qubits, nb_qubits)
    rng = np.random.default_rng()
    for _ in range(depth):
        q1 = rng.integers(nb_qubits)
        # on choisit q2 parmi tous les autres qubits
        possibles = [i for i in range(nb_qubits) if i != q1]
        q2 = rng.choice(possibles)
        qc.h(q1)
        qc.cx(q1, q2)
    qc.measure_all()
    return qc


# Générer un ensemble de circuits
num_circuits = 20
circuits = [random_circuit(3, 5) for _ in range(num_circuits)]

# Préparer les simulateurs
sim_ideal = AerSimulator()
sim_noisy = AerSimulator(noise_model=noise_model)

# Collecte des features
records = []
for qc in circuits:
    # Transpilation
    tq_i = transpile(qc, sim_ideal, optimization_level=0)
    tq_n = transpile(qc, sim_noisy, optimization_level=0)
    # Sauvegarde statevector
    tq_i.save_statevector()
    tq_n.save_statevector()
    # Exécution idéal
    t0 = time.perf_counter()
    res_i = sim_ideal.run(tq_i).result()
    t1 = time.perf_counter()
    rt_i = (t1 - t0) * 1000  # ms
    sv_i = res_i.get_statevector()
    # Exécution bruité
    t0n = time.perf_counter()
    res_n = sim_noisy.run(tq_n).result()
    t1n = time.perf_counter()
    rt_n = (t1n - t0n) * 1000
    sv_n = res_n.get_statevector()
    # Calcul de la fidélité d'état
    fid = state_fidelity(sv_i, sv_n)
    # Enregistrer
    records.append({
        "real_time_ideal_ms": rt_i,
        "real_time_noisy_ms": rt_n,
        "state_fidelity": fid
    })

# Construire un DataFrame
df = pd.DataFrame(records)

# 1) Histogramme des temps d'exécution
plt.figure()
plt.hist(df["real_time_ideal_ms"], bins=10, alpha=0.7, label="Ideal")
plt.hist(df["real_time_noisy_ms"], bins=10, alpha=0.7, label="Noisy")
plt.xlabel("Real Time (ms)")
plt.ylabel("Count")
plt.title("Distribution of Real Execution Times")
plt.legend()
plt.show()

# 2) Nuage de points Fidelity vs Real Time Noisy
plt.figure()
plt.scatter(df["real_time_noisy_ms"], df["state_fidelity"], c='blue', edgecolor='k')
plt.xlabel("Real Time Noisy (ms)")
plt.ylabel("State Fidelity")
plt.title("State Fidelity vs Noisy Real Time")
plt.grid(True)
plt.show()

# 3) Affichage du DataFrame (console)
print(df.describe())
print(df)

# Optionnel : sauvegarder les données
df.to_csv("sim_vs_noise_features.csv", index=False)
