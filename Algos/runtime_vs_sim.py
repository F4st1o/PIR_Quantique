# compare_runtime.py

"""
Script pour comparer exécution locale (simulateur Aer) et réelle (IBM Quantum) :
- Déclenchement automatique sur la machine la moins occupée
- Mesure de counts, temps réel et temps file d'attente
- Calcul de métriques classiques (counts, fidelité, EMD, temps)
- Visualisation des histogrammes
"""
import time
import pickle
import os
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wasserstein_distance, entropy as shannon_entropy
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.visualization import plot_histogram

from tokens import get_token_for

# ----------------------------------------------------------------------------

def compare_runtime_and_sim(
    qc: QuantumCircuit,
    token: str,
    shots: int = 1024
) -> Tuple[dict,str, dict, dict]:
    """
    Exécute qc sur simulateur local puis sur un backend IBM Quantum.

    Returns:
      sim_counts       : histogramme du simulateur idéal
      sim_time_total   : temps réel total de sim.run
      real_counts      : histogramme du calculateur IBM
      real_times       : dict avec 'queue_time', 'execution_time'
    """
    # 1) Simulateur local
    sim = AerSimulator()
    tc_sim = transpile(qc, sim, optimization_level=0)
    start_sim = time.perf_counter()
    job_sim = sim.run(tc_sim, shots=shots)
    res_sim = job_sim.result()
    end_sim = time.perf_counter()
    sim_counts = res_sim.get_counts()
    sim_time_total = end_sim - start_sim

    # 2) Calculateur IBM réel
    service = QiskitRuntimeService(channel='ibm_quantum', token=token)
    backend = service.least_busy(simulator=False)
    tc_real = transpile(qc, backend, optimization_level=0)
    sampler = Sampler(backend)
    # Mesurer la durée depuis l'envoi jusqu'à la complétion
    t0 = time.perf_counter()
    job = sampler.run([tc_real], shots=shots)
    # On peut récupérer queue et exécution séparément
    result = job.result()
    t1 = time.perf_counter()

    # IBM Runtime renvoie liste, on prend le premier
    meas_data = result[0].data.meas
    real_counts = meas_data.get_counts()
    # QiskitRuntimeService ne fournit pas toujours queue_time, on estime
    real_times = {
        'wallclock_time': t1 - t0,
        'execution_time_ibm': getattr(result[0], 'time_taken', None)
    }

    return sim_counts, sim_time_total, real_counts, real_times

# ----------------------------------------------------------------------------

def compute_counts_metrics(
    counts_a: dict,
    counts_b: dict,
    shots: int = 1024
) -> dict:
    """
    Calcule des métriques comparatives entre deux histogrammes de counts.

    - Fidelity classique
    - EMD vs uniforme du second
    - Entropie de Shannon des différences
    """
    keys = sorted(set(counts_a) | set(counts_b))
    p = np.array([counts_a.get(k,0)/shots for k in keys])
    q = np.array([counts_b.get(k,0)/shots for k in keys])
    # Classical fidelity
    fidelity = float((np.sqrt(p*q).sum())**2)
    # Earth Mover's Distance vs uniforme pour B
    obs = q.copy()
    emd = wasserstein_distance(np.arange(len(obs)), np.arange(len(obs)), obs, np.ones_like(obs)/len(obs))
    # Entropie SHannon des différences |p - q|
    diff = np.abs(p - q)
    ent = shannon_entropy(diff, base=2)

    return {
        'classical_fidelity': fidelity,
        'emd_uniform_b': emd,
        'entropy_diff': ent
    }

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    # 1) Construction du circuit
    qc = QuantumCircuit(2,2)
    qc.h(0); qc.cx(0,1); qc.measure_all()
    # 2) Récupération du token
    token = get_token_for('Baptiste')
    # 3) Compare simulateur vs runtime
    sim_counts, sim_time, real_counts, real_times = compare_runtime_and_sim(qc, token)

    # 4) Affichage des résultats
    print(f"Simulator counts: {sim_counts}")
    print(f"Simulator runtime: {sim_time:.3f} s")
    print(f"Real device counts: {real_counts}")
    print(f"Real device times: {real_times}")

    # 5) Mètriques comparatives
    metrics = compute_counts_metrics(sim_counts, real_counts)
    print(f"Comparative metrics: {metrics}")

    # 6) Histogrammes
    plot_histogram(sim_counts, title="Simulator Counts")
    plot_histogram(real_counts, title="Real Device Counts")
    plt.show()
