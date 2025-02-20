from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
 
import matplotlib.pyplot as plt

from random import randint, choice


# Ignoring gates with parameters for now
gates = [gate for gate in get_standard_gate_name_mapping().values() if gate.params == [] and gate.num_clbits == 0]


def fuzzing(nb_circuits, nb_qbits, nb_gates) :
    print(f"Generating {nb_circuits} circuits with {nb_qbits} Qbits and {nb_gates} gates")
    circuits = []
    for i in range(nb_circuits) :
        print(f"\nGenerating circuit {i+1}")
        qc = QuantumCircuit(nb_qbits)
        for _ in range(nb_gates) :
            rand_gate = choice(gates)
            qbits_needed = rand_gate.num_qubits

            if qbits_needed > nb_qbits :
                raise ValueError(f"The required number of Qbits for the gate {rand_gate} is greater than the number of Qbits in the circuit ({nb_qbits})")

            # Generate a list of distinct random Qbits
            rand_qbits = set()
            while(len(rand_qbits) < qbits_needed) :
                rand_qbits.add(randint(0, nb_qbits - 1))

            print(f"Added gate : {rand_gate.name.ljust(5)}\t on Qbits : {rand_qbits}")
            qc.append(rand_gate, list(rand_qbits))  # Adds the gate to the circuit
            
        
        qc.measure_all()
        circuits.append(qc)


    print("\nAll circuits generated\n")
    return circuits




def execute() :
    circuits = fuzzing(1, 10, 25)

    for i in range(len(circuits)) :
        qc = circuits[i]

        
        simulator = AerSimulator()
        qc = transpile(qc, simulator)
        qc.draw('mpl')

        result = simulator.run(qc).result()
        counts = result.get_counts(qc)

        print(f"Results for circuit {i+1} :", counts)
        plot_histogram(counts)
        plt.show()



execute()