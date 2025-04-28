# pipeline.py

"""
Pipeline unique pour extraire toutes les features d'un circuit quantique :
 - métriques statiques
 - métriques temporelles
 - métriques basées sur counts (entropie, EMD, classical fidelity)
 - métriques d'état (state fidelity)
 - métriques hardware (T1, T2, gate/readout errors)
"""
import os
import pickle
import time
from typing import Dict, Any, Optional
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService

# Import des modules de features
from static_features import static_metrics
from execution_features import run_timing
from count_features import shannon_entropy, emd_uniform, classical_fidelity
from adder_features import generate_xor_adder_circuit, analyze_noise_on_adder
from hardware_features import get_backend_error_metrics 

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Algos')))
from fuzzing import fuzzing
from tokens import get_token_for
def list_physical_backends(
    token: str,
    min_qubits: int = 5
) -> list:
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
    now = time.strftime("%Y%m%d")
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


def extract_features(
    qc: QuantumCircuit,
    shots: int = 1024,
    noise_model: Optional[NoiseModel] = get_noise_model('ibmq_sherbrooke', get_token_for('Baptiste')),
    ideal_counts: Optional[Dict[str, int]] = None,
    backend_name: Optional[str] = None,
    token: Optional[str] =None) -> Dict[str, Any]:
    """
    Extrait un dictionnaire de features pour un circuit qc.

    Params:
      qc           : QuantumCircuit à analyser.
      shots        : nombre de tirages pour les counts.
      noise_model  : NoiseModel pour la simulation bruitée (facultatif).
      ideal_counts : distribution idéale pour calculer classical_fidelity (facultatif).
      backend_name : nom du backend IBM pour features hardware (facultatif).
      token        : IBM Quantum token si backend_name fourni.

    Retour:
      Dict contenant toutes les features statiques, temporelles, counts,
      state fidelity et données hardware (si applicables).
    """
    features: Dict[str, Any] = {}

    # 1) Static features
    features.update(static_metrics(qc))

    # 2) Temporal features on simulator (ideal or noisy)
    sim = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
    timing = run_timing(qc, sim, shots=shots)
    features.update(timing)

    # 3) Count-based features
    tq = transpile(qc, sim, optimization_level=0)
    job = sim.run(tq, shots=shots).result()
    counts = job.get_counts()

    features['entropy_shannon'] = shannon_entropy(counts)
    features['emd_uniform']     = emd_uniform(counts)
    freqs = np.array(list(counts.values()), dtype=float)
    features['variance_counts'] = float(freqs.var())
    features['classical_fidelity'] = classical_fidelity(counts, ideal_counts) if ideal_counts else None

        # 4) Adder-based features (XOR adder noise stats)
    if noise_model:
        adder_stats = analyze_noise_on_adder(qc, noise_model, shots=shots)
        features.update(adder_stats)
        print(f"Adder features: {adder_stats}")

    else:
        features.update({
            'mean_ideal': None,
            'var_ideal': None,
            'mean_noisy': None,
            'var_noisy': None
        })

    # 5) Hardware features
    if backend_name and token:
        hw_feats = get_backend_error_metrics(backend_name, token)
        print(f"Hardware features: {hw_feats}")

        features.update(hw_feats)

    return features


# Exemple d'utilisation
if __name__ == '__main__':
    from tokens import get_token_for
    from qiskit_aer.noise import NoiseModel
    import matplotlib.pyplot as plt
    import pandas as pd

    # 1) Préparer le token et backends
    token = get_token_for('Baptiste')
    service = QiskitRuntimeService(channel='ibm_quantum', token=token)
    backend_name = service.least_busy(simulator=False).name
    noise_model = NoiseModel.from_backend(service.backend(backend_name))

    # 2) Générer plusieurs circuits de test
    circuits = fuzzing(
        20,          # Nombre de circuits à générer
        4,            # Nombre de qubits par circuit
        10,            # Nombre de portes par circuit
        )    # Initialisation aléatoire des qubits

 
    # 3) Extraire features pour idéal et bruité
    all_features = []
    for scenario, nm in [('ideal', None), ('noisy', noise_model)]:
        for qc, _ in circuits:
            feats = extract_features(
                qc,
                shots=512,
                noise_model=nm,
                ideal_counts=None,
                backend_name=backend_name,
                token=token
            )
            feats['scenario'] = scenario
            all_features.append(feats)

    # 4) Plot scatter de deux features coloré par scénario
    def plot_features_scatter(data, x, y, label_key):
        df = pd.DataFrame(data)
        for cat, grp in df.groupby(label_key):
            plt.scatter(grp[x], grp[y], label=cat)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{y} vs {x} par scénario")
        plt.legend()
        plt.show()

    if all_features:
        print(all_features[0].keys())  # Print keys of the first dictionary in the list
    else:
        print("all_features is empty.")
    
    # Convert all_features to a DataFrame for easier plotting
    df = pd.DataFrame(all_features)

 
    # Plot histograms for some features
    features_to_plot = ['var_ideal','var_noisy', 'variance_counts' ]
    for feature in features_to_plot:
        plt.figure()
        for scenario, grp in df.groupby('scenario'):
            grp[feature].plot(kind='hist', alpha=0.5, label=scenario, bins=20)
        plt.title(f"Histogram of {feature}")
        plt.xlabel(feature)
        plt.ylabel("Frequency")
        plt.legend()
        plt.show()

    # 5) Plot importance des features (exemple fictif)
    def plot_feature_importance(importances: Dict[str, float]):
        plt.figure(figsize=(6,4))
        plt.bar(importances.keys(), importances.values())
        plt.xticks(rotation=45, ha='right')
        plt.title('Importance des features')
        plt.tight_layout()
        plt.show()

    # Exemple d'importances
    example_importances = {'var_noisy':0.3, 'variance_counts':0.5, 'entropy_shannon':0.2}
    plot_feature_importance(example_importances)


