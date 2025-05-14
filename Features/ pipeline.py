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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService

from static_features import static_metrics
from execution_features import run_timing
from count_features import *
# from hardware_features import get_backend_error_metrics

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Algos')))
from fuzzing import fuzzing
from tokens import get_token_for
from simulate import calculate 

def list_physical_backends(token: str, min_qubits: int = 5) -> list:
    """
    Retourne la liste des QPUs IBM Quantum accessibles (opérationnels, non simulateurs)
    et ayant au moins `min_qubits` qubits.
    """
    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    return service.backends(simulator=False, operational=True, min_num_qubits=min_qubits)


def get_noise_model(backend_name: str, token: str, cache_dir: str = "noise_models") -> NoiseModel:
    """
    Récupère et met en cache (pickle) le NoiseModel d'un QPU IBM.
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
    noise_model: Optional[NoiseModel] = get_noise_model('ibm_sherbrooke', get_token_for('Baptiste')),
    ideal_counts: Optional[Dict[str, int]] = None,
    backend_name: Optional[str] = None,
    token: Optional[str] =None) -> Dict[str, Any]:
    """
    Extrait un dictionnaire de features pour un circuit quantique.
    """
    features: Dict[str, Any] = {}

    # Static features
    features.update(static_metrics(qc))

    # Temporal and Count-based features
    sim = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
    tq = transpile(qc, sim, optimization_level=0)
    timing, counts = run_timing(tq, sim, shots=shots)
    features.update(timing)

    # Update features
    features['counts'] = counts
    features['entropy_shannon'] = shannon_entropy(counts)
    features['emd_uniform'] = emd_uniform(counts)

    return features


def plot_features_scatter(data, x, y, label_key):
    """
    Trace un scatter plot de deux features, coloré par scénario.
    """
    df = pd.DataFrame(data)
    for cat, grp in df.groupby(label_key):
        plt.scatter(grp[x], grp[y], label=cat)

    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"{y} vs {x} par scénario")
    plt.legend()
    plt.show()


def plot_feature_distributions(df, features_to_plot):
   """
   Plots the distributions of features for each scenario.
   """
   execution_date = time.strftime("%Y-%m-%d")  # Get the current date
   for feature in features_to_plot:
       plt.figure(figsize=(8, 5))
       for scenario, grp in df.groupby('scenario'):
           # Translate scenario names
           sns.kdeplot(grp[feature].dropna(), label=f"{scenario} ({execution_date})", fill=True, linewidth=2, alpha=0.4)


       plt.title(f'Distribution of {feature}', fontsize=14)
       plt.xlabel(feature, fontsize=12)
       plt.ylabel('Density', fontsize=12)
       plt.legend(title='AerSimulator Scenario')
       plt.grid(True, linestyle='--', alpha=0.6)
       plt.tight_layout()
       plt.show()




def plot_time_features(df, real_time_col):
    """
    Affiche une courbe du temps réel par scénario avec une meilleure lisibilité.
    """
    execution_date = time.strftime("%Y-%m-%d")  # Get the current date
    # Ignore the first value in the DataFrame
    df_plot = df.iloc[1:]

    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df_plot,
        x=df_plot.index,
        y=real_time_col,
        hue="scenario",
        style="scenario",
        markers=True,
        dashes=False,
        palette="tab10"
    )

    plt.title(f'Real time per scenario', fontsize=14)
    plt.xlabel('Index of circuit', fontsize=12)
    plt.ylabel(real_time_col, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Scenario')
    plt.tight_layout()
    plt.show()





if __name__ == '__main__':
    print("Préparer le token et backends")
    token = get_token_for('Momo')
    service = QiskitRuntimeService(channel='ibm_quantum', token=token)
    backend1 = service.backend("ibm_sherbrooke")
    backend2=service.backend("ibm_brisbane")

    noise_model_sherbrooke = NoiseModel.from_backend(backend1)
    noise_model_brisbane = NoiseModel.from_backend(backend2)


    # Générer des circuits
    circuits = fuzzing(25, 4, 10)
    # Extraire les features
    all_features = []
    sim_counts = []
    for scenario, nm in [('ideal', None), ('noisy_sherbrooke', noise_model_sherbrooke), ('noisy_brisbane', noise_model_brisbane), ('calculator_sherbrooke', backend1), ('calculator_brisbane', backend2)]:
        for qc, _ in circuits:
            print(f"Traitement du circuit {qc.name} avec le scénario {scenario}")

            if (scenario == 'calculator_sherbrooke') or (scenario == 'calculator_brisbane'):
                # Exécuter le circuit sur le backend
                counts_list, measured_durations_list, reported_durations_list = calculate(qc, service, nm, shots=2**10, nb_calculations=1)
                counts = counts_list[0]
                measured_duration = measured_durations_list[0]
                reported_duration = reported_durations_list[0]

                feats: Dict[str, Any] = {}

                # Static features
                feats.update(static_metrics(qc))
                feats["time_real_ms"] = measured_duration * 1000
                feats["time_sim_ms"] = reported_duration * 1000
                feats['counts'] = counts
                feats['entropy_shannon'] = shannon_entropy(counts)
                feats['emd_uniform'] = emd_uniform(counts)

            else :
                feats = extract_features(
                    qc,
                    shots=256,
                    noise_model=nm,
                    ideal_counts=None,
                    backend_name=_,
                    token=token
                )

            feats['scenario'] = scenario
            all_features.append(feats)

    

    print("\nVérifier les features extraites")
    if all_features:
        print(list(all_features[0].keys()))
    else:
        print("all_features est vide.")

    # Convertir en DataFrame
    df = pd.DataFrame(all_features)

    # Tracer les distributions des features
    features_to_plot = ['entropy_shannon', 'emd_uniform']  # ['entropy_shannon', 'emd_uniform', 'variance_counts', 'classical_fidelity']
    plot_feature_distributions(df, features_to_plot)
    #plot_time_features(df, 'time_real_ms')


