from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
 
import matplotlib.pyplot as plt

from random import sample, choice

import time
from datetime import datetime


# Ignoring gates with parameters for now
gates = [gate for gate in get_standard_gate_name_mapping().values() if gate.params == [] and gate.num_clbits == 0]


def fuzzing(nb_circuits: int, nb_qbits: int, nb_gates: int, save , verbose = False, random_init = False) -> list[QuantumCircuit, str] :
    """
    Generates a list of circuits with random gates and Qbits

    Parameters
    ----------
    nb_circuits : int
        Number of circuits to generate

    nb_qbits : int
        Number of Qbits in each circuit

    nb_gates : int
        Number of gates in each circuit

    random_init : bool
        If True, apply Hadamard gates to all Qbits before applying the random gates

    Returns
    -------
    list
        A list of QuantumCircuit objects
    """

    print(f"Generating {nb_circuits} circuits with {nb_qbits} Qbits and {nb_gates} gates")
    circuits = []
    for i in range(nb_circuits) :
        date = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")[:-3]
        if save:
            print("test")
            fichier = open("data/" + date, "w")
            fichier.write(f"nb_qbits = {nb_qbits}\n")
            fichier.write(f"nb_gates = {nb_gates}\n")

        if verbose : print(f"\nGenerating circuit {i+1}")
        qc = QuantumCircuit(nb_qbits)

        if random_init :
            qc.h(range(nb_qbits))
            if verbose : print("Applied Hadamard gate to all Qbits")
            if save : fichier.write(f"h : {list(range(nb_qbits))}\n")

        for _ in range(nb_gates) :
            rand_gate = choice(gates)
            qbits_needed = rand_gate.num_qubits

            if qbits_needed > nb_qbits :
                raise ValueError(f"The required number of Qbits for the gate {rand_gate} is greater than the number of Qbits in the circuit ({nb_qbits})")

            # Generate a list of distinct random Qbits
            rand_qbits = sample(range(nb_qbits), qbits_needed)

            if verbose : print(f"Added gate : {rand_gate.name.ljust(5)}\t on Qbits : {rand_qbits}")
            if save : fichier.write(f"{rand_gate.name} : {rand_qbits}\n")

            qc.append(rand_gate, rand_qbits)  # Adds the gate to the circuit
            
        
        qc.measure_all()
        circuits.append((qc, date))
        if save : fichier.close()


    print("\nAll circuits generated\n")
    return circuits




def execute(repetition = 50, save = True) :
    circuits = fuzzing(2, 10, 25, save, verbose=True, random_init = True)

    for i in range(len(circuits)) :
        qc, date = circuits[i]

        
        simulator = AerSimulator()
        qc = transpile(qc, simulator, optimization_level=0)
        qc.draw('mpl')

        total_exec_time = 0
        total_simul_time = 0

        for _ in range(repetition) :
            start = time.perf_counter()
            result = simulator.run(qc).result()
            end = time.perf_counter()

            total_exec_time += (end - start)
            total_simul_time += result.time_taken

        print(f"Duree d'execution moyen: {1000*total_exec_time/repetition} ms")
        print(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")
        
        if save :
            with open("data/" + date, "a") as fichier :
                fichier.write(f"Duree d'execution moyen: {1000*total_exec_time/repetition} ms\n")
                fichier.write(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")

        # counts = result.get_counts(qc)

        # print(f"Results for circuit {i+1} :", counts)
        # plot_histogram(counts)
        # plt.show()



execute()