import time
from typing import Dict, Any
from qiskit import QuantumCircuit, transpile
from static_features import static_metrics
#############################
# Execution Features
#############################

def run_timing(
    qc: QuantumCircuit,
    simulator,
    shots: int = 1024
) -> Dict[str, float]:
    """
    Transpile le circuit pour le simulateur donné, exécute et mesure :
      - time_real_ms : temps réel (wall-clock) en millisecondes
      - time_sim_ms  : temps simulé retourné par le simulateur (job.time_taken) en ms, ou None
    """
    # Transpilation
    tq = transpile(qc, simulator, optimization_level=0)

    # Exécution et mesure du temps réel
    start = time.perf_counter()
    job = simulator.run(tq, shots=shots).result()
    end = time.perf_counter()

    # Calcul des métriques
    time_real_ms = (end - start) * 1000
    time_sim = getattr(job, "time_taken", None)
    time_sim_ms = (time_sim * 1000) if time_sim is not None else None

    return {
        "time_real_ms": time_real_ms,
        "time_sim_ms": time_sim_ms
    }


# Exemple d'utilisation
if __name__ == "__main__":
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    # Création d'un circuit de test
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    qc.cx(0, 1)
    qc.measure_all()

    # Initialisation du simulateur
    sim = AerSimulator()

    # Mesure des métriques temporelles
    metrics = run_timing(qc, sim, shots=1024)
    print(metrics)
def _example():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(3, 3)
    qc.h([0, 1, 2])
    qc.cx(0, 1)
    qc.swap(1, 2)
    qc.measure_all()

    metrics = static_metrics(qc)
    print(metrics)


if __name__ == "__main__":
    _example()
