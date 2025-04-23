# metrics_pipeline.py

import time
from typing import Dict, Any
import numpy as np
from scipy.stats import entropy, wasserstein_distance
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService
from math import sqrt

#############################
# 1) Transpilation
#############################

def transpile_circuit(qc: QuantumCircuit, simulator) -> QuantumCircuit:
    """
    Transpile qc pour qu'il n'utilise que les portes supportées par simulator.
    """
    return transpile(qc, simulator)

#############################
# 2) Exécution
#############################

def execute_circuit(qc: QuantumCircuit,
                    simulator,
                    shots: int = 1024) -> Dict[str, Any]:
    """
    Exécute qc sur simulator, renvoie un dict contenant :
      - 'counts'    : histogramme des résultats
      - 'time_sim'  : temps interne simulé (job.time_taken)
      - 'time_real' : durée réelle de l'appel run(...)
    """
    # lancer la simulation / exécution
    start = time.perf_counter()
    job = simulator.run(qc, shots=shots).result()
    end = time.perf_counter()

    return {
        "counts":    job.get_counts(),
        "time_sim":  getattr(job, "time_taken", None),
        "time_real": end - start
    }

#############################
# 3) Extraction de métriques
#############################

def shannon_entropy(counts: Dict[str,int]) -> float:
    """ Entropie de Shannon H = -∑ p_i log2 p_i """
    freqs = np.array(list(counts.values()), dtype=float)
    ps = freqs / freqs.sum()
    return entropy(ps, base=2)

def emd_distance(counts: Dict[str,int]) -> float:
    """
    Earth Mover's Distance (Wasserstein 1) 
    entre distribution observée et distribution uniforme.
    """
    freqs = np.array(sorted(counts.values()), dtype=float)
    obs = freqs / freqs.sum()
    unif = np.ones_like(obs) / len(obs)
    # scipy.stats.wasserstein_distance prend deux distributions sur bins 0..n-1
    return wasserstein_distance(np.arange(len(obs)), np.arange(len(unif)), obs, unif)

def classical_fidelity(counts: Dict[str,int], ideal_counts: Dict[str,int]) -> float:
    """
    Fidélité classique F = (∑ sqrt(p_i q_i))^2
    où p = counts/shots, q = ideal_counts/shots.
    """
    # fusionner clés
    keys = set(counts) | set(ideal_counts)
    shots_obs   = sum(counts.values())
    shots_ideal = sum(ideal_counts.values())
    s = 0.0
    for k in keys:
        p = counts.get(k, 0) / shots_obs
        q = ideal_counts.get(k, 0) / shots_ideal
        s += sqrt(p*q)
    return s**2

def extract_metrics(qc: QuantumCircuit,
                    exec_data: Dict[str,Any],
                    ideal_counts: Dict[str,int] = None) -> Dict[str, Any]:
    """
    À partir du circuit qc et du dict exec_data (résultats d’exécute),
    calcule et renvoie toutes les features demandées.
    """
    counts   = exec_data["counts"]
    metrics = {}

    # 1. Probabilités et statistiques de base
    metrics["entropy_shannon"] = shannon_entropy(counts)
    metrics["emd_uniform"]     = emd_distance(counts)
    freqs = np.array(list(counts.values()), dtype=float)
    metrics["variance_counts"] = float(np.var(freqs))

    # 2. Fidélité vs distribution idéale (si fournie)
    if ideal_counts:
        metrics["fidelity"] = classical_fidelity(counts, ideal_counts)
    else:
        metrics["fidelity"] = None

    # 3. Temps
    metrics["time_sim"]  = exec_data["time_sim"]
    metrics["time_real"] = exec_data["time_real"]

    # 4. Complexité du circuit
    metrics["depth"]     = qc.depth()
    op_counts = qc.count_ops()
    metrics["num_gates"] = sum(op_counts.values())
    # répartition par type
    metrics["gate_counts"] = dict(op_counts)

    # 5. Spécifiques
    metrics["num_swap"]   = op_counts.get("swap", 0)
    metrics["num_h"]      = op_counts.get("h", 0)

    return metrics

#############################
# 4) Exemple d’usage
#############################

if __name__ == "__main__":
    # 1) Créer un circuit de test (ici un mini-Grover simplifié)
    qc = QuantumCircuit(2, 2)
    qc.h([0,1])        # état de superposition
    qc.cz(0,1)         # inversion de phase sur |11>
    qc.h([0,1])        # inversion de superposition (amplitude)
    qc.measure([0,1], [0,1])

    # 2) Préparer le simulateur idéal et bruité
    sim_ideal = AerSimulator()  # pas de bruit
    # sim_noisy = AerSimulator(noise_model=...)  # tu peux charger ton NoiseModel ici

    # 3) Transpile + exécute
    qc_t       = transpile_circuit(qc, sim_ideal)
    exec_ideal = execute_circuit(qc_t, sim_ideal, shots=1024)

    # 4) Si tu as la distribution idéale attendue, la coder ici
    ideal_counts = {"00": 512, "11": 512}  # par exemple pour Grover

    # 5) Extraire toutes les métriques
    metrics = extract_metrics(qc, exec_ideal, ideal_counts=ideal_counts)

    # 6) Affichage
    import pprint; pprint.pprint(metrics)
