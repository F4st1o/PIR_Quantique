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

# ----------------------------------------------------------------------------
# 1) Lister les calculateurs physiques disponibles
# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------
# 2) Charger et mettre en cache un modèle de bruit pour un QPU
# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------
# 3) Extraire les métriques d'erreur d'un backend QPU
# ----------------------------------------------------------------------------

def get_backend_error_metrics(
    backend_name: str,
    token: str
) -> Dict[str, float]:
    """
    Extrait des propriétés matérielles d'un QPU IBM :
      - T1 moyen (s)
      - T2 moyen (s)
      - erreur de porte moyenne
      - erreur de mesure moyenne
    """
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    backend = service.backend(backend_name)
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
    from tokens import get_token_for

    token = get_token_for('Baptiste')
    # 1) Lister les QPUs
    qpus = list_physical_backends(token, min_qubits=5)
    print("Available QPUs:", [b.name for b in qpus])

    # Choisir le moins occupé
    backend_name = qpus[0].name
    print("Selected backend:", backend_name)

    # 2) Charger le modèle de bruit
    nm = get_noise_model(backend_name, token)
    print("NoiseModel loaded for", backend_name)

    # 3) Extraire les métriques hardware
    hw_metrics = get_backend_error_metrics(backend_name, token)
    print("Hardware error metrics:", hw_metrics)
