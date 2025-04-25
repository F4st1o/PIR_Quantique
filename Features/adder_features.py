from typing import Dict, Any, List
from matplotlib import pyplot as plt
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
from qiskit import QuantumCircuit, transpile,QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import pickle
import os
from tokens import get_token_for
from datetime import datetime
from typing import Any, Dict, List
import numpy as np
from qiskit.quantum_info import state_fidelity
try:
    from qiskit.circuit.library.arithmetic import QFTAdder
except ImportError:
    # Fallback: implement simple ripple-carry adder if QFTAdder unavailable
    QFTAdder = None

def list_physical_backends(
    token: str,
    min_qubits: int = 5
) -> List[Any]:
    """
    Retourne la liste des QPUs IBM Quantum accessibles (opérationnels, non simulateurs)
    et ayant au moins `min_qubits` qubits.

    token: votre jeton IBM Quantum.
    min_qubits: filtre sur le nombre minimal de qubits.
    """
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    return service.backends(
        simulator=False,
        operational=True,
        min_num_qubits=min_qubits
    )

def get_noise_model(
    backend_name: str,
    token: str,
    cache_dir: str = "noise_models"
) -> NoiseModel:
    """
    Récupère et met en cache (pickle) le NoiseModel d'un QPU IBM.
    - backend_name: nom du QPU (ex. 'ibmq_jakarta')
    - token: jeton IBM Quantum
    - cache_dir: dossier local pour stocker les modèles
    """
    os.makedirs(cache_dir, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d")
    cache_file = os.path.join(cache_dir, f"{backend_name}_{now}_noise.pkl")

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    backend = service.backend(backend_name)
    model = NoiseModel.from_backend(backend)

    with open(cache_file, "wb") as f:
        pickle.dump(model, f)
    return model

def generate_xor_adder_circuit(num_bits: int = 8) -> QuantumCircuit:
    """
    Génère un 'adder' basique en XOR bit à bit (addition mod 2) :
    - 16 qubits : A[0..7], B[0..7]
    - 16 bits classiques pour la mesure
    """
    qc = QuantumCircuit(2 * num_bits, 2 * num_bits)
    # Superposition équiprobable sur A et B
    qc.h(range(2 * num_bits))
    # XOR A_i -> B_i
    for i in range(num_bits):
        qc.cx(i, num_bits + i)
    qc.measure(range(2 * num_bits), range(2 * num_bits))
    return qc

def analyze_noise_on_adder(
    qc: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 2048
) -> Dict[str, Any]:
    """
    Exécute qc en idéal et bruité, retourne counts et stats.
    """
    sim_ideal = AerSimulator()
    sim_noisy = AerSimulator(noise_model=noise_model)

    # Transpile une seule fois
    tq_ideal = transpile(qc, sim_ideal, optimization_level=0)
    tq_noisy = transpile(qc, sim_noisy, optimization_level=0)

    # Run
    res_i = sim_ideal.run(tq_ideal, shots=shots).result()
    res_n = sim_noisy.run(tq_noisy, shots=shots).result()
    counts_i = res_i.get_counts()
    counts_n = res_n.get_counts()

    # Stats
    vals_i = np.array(list(counts_i.values()), dtype=float)
    vals_n = np.array(list(counts_n.values()), dtype=float)
    stats = {
        "counts_ideal":   counts_i,
        "counts_noisy":   counts_n,
        "mean_ideal":     float(vals_i.mean()),
        "var_ideal":      float(vals_i.var()),
        "mean_noisy":     float(vals_n.mean()),
        "var_noisy":      float(vals_n.var()),
    }
    return stats

def plot_counts_comparison(stats: Dict[str, Any]):
    """
    Trace deux histogrammes côte à côte pour idéal vs bruité.
    """
    ci, cn = stats["counts_ideal"], stats["counts_noisy"]
    # convertir dictionnaire en listes alignées
    keys = sorted(set(ci)|set(cn))
    vals_i = [ci.get(k,0) for k in keys]
    vals_n = [cn.get(k,0) for k in keys]

    x = np.arange(len(keys))
    width = 0.4

    plt.figure(figsize=(12,5))
    plt.bar(x - width/2, vals_i, width, label="Idéal")
    plt.bar(x + width/2, vals_n, width, label="Bruitée")
    plt.xticks(x, keys, rotation='vertical', fontsize=8)
    plt.xlabel("Résultat (bitstring)")
    plt.ylabel("Counts")
    plt.title("Distribution Idéal vs Bruitée")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Récupérer token et NoiseModel pour un QPU IBM
    token = get_token_for("Baptiste")
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    backend = service.least_busy(simulator=False)
    noise_model = NoiseModel.from_backend(service.backend(backend.name))

    # Générer circuit et analyser
    qc_adder = generate_xor_adder_circuit(num_bits=8)
    stats = analyze_noise_on_adder(qc_adder, noise_model, shots=2048)

    # Afficher les stats
    print("Moyenne counts idéal :", stats["mean_ideal"])
    print("Variance counts idéal :", stats["var_ideal"])
    print("Moyenne counts bruité :", stats["mean_noisy"])
    print("Variance counts bruité :", stats["var_noisy"])

    # Tracer
    plot_counts_comparison(stats)