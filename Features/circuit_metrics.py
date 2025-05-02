# circuit_metrics.py

from qiskit import QuantumCircuit
from typing import Dict, Any

def analyze_circuit_metrics(qc: QuantumCircuit) -> Dict[str, Any]:
    """
    Analyse statique d'un QuantumCircuit et extraction de métriques clés.
    
    Renvoie un dict contenant :
      - num_qubits       (int)   : nombre de qubits utilisés
      - depth            (int)   : profondeur du circuit
      - num_ops          (int)   : nombre total d'opérations
      - gate_counts      (dict)  : répartition des portes par type
      - parallelism      (float) : ratio opérations / profondeur
      - num_swap         (int)   : nombre de portes SWAP
      - num_h            (int)   : nombre de portes H
      - num_measure      (int)   : nombre de portes de mesure
    """
    # Comptage unique des opérations
    gate_counts = qc.count_ops()
    depth       = qc.depth()
    num_ops     = qc.size()
    
    # Calcul du ratio de parallélisme (ops par couche)
    parallelism = round(num_ops / depth, 2) if depth > 0 else float(num_ops)
    
    # Extraire quelques portes particulières
    num_swap    = gate_counts.get("swap",    0)
    num_h       = gate_counts.get("h",       0)
    num_measure = gate_counts.get("measure", 0)
    
    return {
        "num_qubits":      qc.num_qubits,
        "depth":           depth,
        "num_ops":         num_ops,
        "gate_counts":     dict(gate_counts),
        "parallelism":     parallelism,
        "num_swap":        num_swap,
        "num_h":           num_h,
        "num_measure":     num_measure,
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # On crée un petit circuit de test
    qc = QuantumCircuit(5, 5)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.t(2)
    qc.h(3)
    qc.cx(3, 4)
    qc.measure_all()
    
    # On analyse et affiche les métriques
    metrics = analyze_circuit_metrics(qc)
    for key, value in metrics.items():
        print(f"{key:15} : {value}")
    # Affichage formaté