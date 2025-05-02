# hardware_features.py

"""
Fonctions pour interroger les QPUs IBM Quantum et extraire leurs caractéristiques matérielles
"""
from typing import Dict, Any, List
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer.noise import NoiseModel
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import pickle
import os
from datetime import datetime

from tokens import get_token_for

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Algos')))

from fuzzing import fuzzing
from simulate import calculate


# ----------------------------------------------------------------------------
# 2) Charger et mettre en cache un modèle de bruit pour un QPU
# ----------------------------------------------------------------------------

def get_noise_model(
    backend,
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
    cache_file = os.path.join(cache_dir, f"{backend.name}_{now}_noise.pkl")

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    model = NoiseModel.from_backend(backend)

    with open(cache_file, "wb") as f:
        pickle.dump(model, f)
    return model

# ----------------------------------------------------------------------------
# 3) Extraire les métriques d'erreur d'un backend QPU
# ----------------------------------------------------------------------------

def get_backend_error_metrics(
    backend_name,
    token: str
) -> Dict[str, float]:
    """
    Extrait des propriétés matérielles d'un QPU IBM :
      - T1 moyen (s)
      - T2 moyen (s)
      - erreur de porte moyenne
      - erreur de mesure moyenne
    """
    props = backend.properties()

    t1_list = []
    t2_list = []
    readout_list = []
    error_list = []

    # Récupération T1, T2, readout_error par qubit
    for qubit in props.qubits:
        for param in qubit:
            if param.name == "T1":
                t1_list.append(param.value)
            elif param.name == "T2":
                t2_list.append(param.value)
            elif param.name == "readout_error":
                readout_list.append(param.value)

    # Récupération du gate_error pour chaque porte
    for gate in props.gates:
        for param in gate.parameters:
            if param.name == "gate_error":
                error_list.append(param.value)

    return {
        "avg_T1":            float(sum(t1_list)/len(t1_list)) if t1_list else 0.0,
        "avg_T2":            float(sum(t2_list)/len(t2_list)) if t2_list else 0.0,
        "avg_readout_error": float(sum(readout_list)/len(readout_list)) if readout_list else 0.0,
        "avg_gate_error":    float(sum(error_list)/len(error_list)) if error_list else 0.0,
    }

# ----------------------------------------------------------------------------
# Exemple d'utilisation
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    token = get_token_for('Baptiste')

    service = QiskitRuntimeService(channel="ibm_quantum", token=token)

    # 1) Lister les QPUs
    qpus = service.backends(simulator=False, operational=True, min_num_qubits=5)
    print("Available QPUs:", [b.name for b in qpus])

    # Choisir le moins occupé
    backend = service.backend(qpus[0].name)
    print("Selected backend:", backend.name)

    # 2) Charger le modèle de bruit
    nm = get_noise_model(backend, token)
    print("NoiseModel loaded for", backend.name)

    # 3) Extraire les métriques hardware
    hw_metrics = get_backend_error_metrics(backend, token)
    print("Hardware error metrics:", hw_metrics)

    # 4) Exécuter un circuit de test
    circuits = fuzzing(1, 5, 10)
    calculate(circuits, service, backend, 512)

