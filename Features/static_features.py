from typing import Dict, Any
from qiskit import QuantumCircuit


def static_metrics(qc: QuantumCircuit) -> Dict[str, Any]:
    """
    Calcule des métriques statiques d'un circuit quantique :
      - num_qubits : nombre de qubits du circuit
      - depth      : profondeur du circuit
      - num_ops    : nombre total d'opérations
      - gate_counts: répartition des portes par type
      - parallelism: ratio ops/profondeur
      - num_swap   : nombre de portes SWAP
      - num_h      : nombre de portes H
      - num_measure: nombre de portes de mesure
    """
    gate_counts = qc.count_ops()
    depth = qc.depth()
    num_ops = qc.size()
    parallelism = round(num_ops / depth, 2) if depth > 0 else float(num_ops)

    return {
        "num_qubits": qc.num_qubits,
        "depth": depth,
        "num_ops": num_ops,
        "gate_counts": dict(gate_counts),
        "parallelism": parallelism,
        "num_swap": gate_counts.get("swap", 0),
        "num_h": gate_counts.get("h", 0),
        "num_measure": gate_counts.get("measure", 0),
    }


# Exemple d'utilisation
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
