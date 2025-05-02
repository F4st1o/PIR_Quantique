# noise_analysis.py

"""
Script complet pour analyser l'impact du bruit sur un circuit quantique :
- Charger et mettre en cache le NoiseModel IBM
- Générer un circuit dense
- Mesurer la fidélité d'état (statevector)
- Mesurer et comparer les distributions de mesure (counts)
- Afficher des métriques complémentaires (EMD, fidélité classique)
- Visualiser les histogrammes idéal vs bruité
"""
import os
import pickle
from difflib import get_close_matches
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.quantum_info import state_fidelity
from qiskit.visualization import plot_histogram
from scipy.stats import wasserstein_distance

from tokens import get_token_for

# ----------------------------------------------------------------------------

def load_noise_model(
    backend_name: str,
    token: str,
    instance: Optional[str] = None,
    cache_dir: str = "noise_models"
) -> NoiseModel:
    """
    Charge (ou met en cache) le modèle de bruit pour un backend IBM Quantum.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"{backend_name}_noise.pkl")

    # 1) Recharger si déjà en cache
    if os.path.exists(cache_path):
        print(f"Rechargement du NoiseModel depuis {cache_path}")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    # 2) Interroger les backends disponibles
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    backends = service.backends(instance=instance)
    names = [b.name for b in backends]
    print("Backends disponibles :", names)

    # 3) Choix du backend exact
    if backend_name not in names:
        suggestions = get_close_matches(backend_name, names, n=3, cutoff=0.3)
        msg = f"Backend '{backend_name}' introuvable."
        if suggestions:
            msg += f" Suggestions: {suggestions}"
        raise ValueError(msg)

    # 4) Récupérer le backend et bâtir le NoiseModel
    backend = (
        service.backend(backend_name, instance=instance)
        if instance else service.backend(backend_name)
    )
    noise_model = NoiseModel.from_backend(backend)

    # 5) Mettre en cache
    with open(cache_path, "wb") as f:
        pickle.dump(noise_model, f)
        print(f"NoiseModel mis en cache dans {cache_path}")
    return noise_model

# ----------------------------------------------------------------------------

def generate_extremely_noisy_circuit(num_qubits: int = 5) -> QuantumCircuit:
    """
    Génère un circuit dense pour maximiser l'influence du bruit.
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    # Couche de rotations variées
    for i in range(num_qubits):
        qc.h(i); qc.t(i); qc.rx(0.5, i); qc.rz(1.2, i)
    # Chaînes de CNOT pour intrication
    pairs = [(i, (i+1)%num_qubits) for i in range(num_qubits)] + [(0,2),(1,3),(2,4)]
    for a,b in pairs:
        qc.cx(a,b)
    # Boucles de perturbation
    for _ in range(3):
        for i in range(num_qubits): qc.t(i); qc.h(i); qc.rx(0.7,i); qc.ry(0.4,i)
        qc.cx(0, num_qubits-1); qc.cx(num_qubits-1,2); qc.cx(1,3)
    qc.measure_all()
    return qc

# ----------------------------------------------------------------------------

def compute_state_fidelity(
    qc: QuantumCircuit,
    noise_model: NoiseModel,
    method: str = "statevector"
) -> float:
    """
    Calcule la fidélité d'état entre version idéale et bruitée.
    """
    sim_i = AerSimulator(method=method)
    sim_n = AerSimulator(method=method, noise_model=noise_model)
    t_i = transpile(qc, sim_i, optimization_level=0)
    t_n = transpile(qc, sim_n, optimization_level=0)
    t_i.save_statevector(); t_n.save_statevector()
    res_i = sim_i.run(t_i).result(); res_n = sim_n.run(t_n).result()
    sv_i = res_i.get_statevector(); sv_n = res_n.get_statevector()
    fidelity = state_fidelity(sv_i, sv_n)
    print(f"Statevector fidelity: {fidelity:.6f}")
    return fidelity

# ----------------------------------------------------------------------------

def compute_count_metrics(
    qc: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 1024
) -> dict:
    """
    Exécute qc idéal et bruité en mode qasm, renvoie counts et métriques classiques.
    """
    sim_i = AerSimulator()
    sim_n = AerSimulator(noise_model=noise_model)
    t_i = transpile(qc, sim_i, optimization_level=0)
    t_n = transpile(qc, sim_n, optimization_level=0)
    # Exécutions
    res_i = sim_i.run(t_i, shots=shots).result(); counts_i = res_i.get_counts()
    res_n = sim_n.run(t_n, shots=shots).result(); counts_n = res_n.get_counts()
    # Metrics
    # 1) Classical fidelity: (sum sqrt(p_i q_i))^2
    keys = set(counts_i) | set(counts_n)
    p = np.array([counts_i.get(k,0)/shots for k in keys])
    q = np.array([counts_n.get(k,0)/shots for k in keys])
    classical_fid = float((np.sqrt(p*q).sum())**2)
    # 2) EMD vs idéal
    obs = np.array([counts_n.get(k,0) for k in keys], dtype=float)
    obs /= obs.sum()
    unif = np.ones_like(obs)/len(obs)
    emd = wasserstein_distance(np.arange(len(obs)), np.arange(len(obs)), obs, unif)
    # Print et plot
    print(f"Classical fidelity (counts): {classical_fid:.6f}")
    print(f"EMD vs uniforme: {emd:.6f}")
    plot_histogram(counts_i, title="Counts ideal"); plot_histogram(counts_n, title="Counts noisy")
    plt.show()
    return {"counts_ideal": counts_i, "counts_noisy": counts_n,
            "classical_fidelity": classical_fid, "emd_uniform": emd}

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    # Initialisation
    token = get_token_for("Baptiste")
    backend = "ibm_sherbrooke"
    nm = load_noise_model(backend, token)
    print(f"Noise model chargé pour {backend}.")

    # Génération du circuit
    qc = generate_extremely_noisy_circuit()

    # Fidelity sur état pur
    compute_state_fidelity(qc, nm)

    # Métriques de distribution (measurement)
    compute_count_metrics(qc, nm, shots=1024)
