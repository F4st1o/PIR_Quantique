from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, gaussian_kde

from random import sample, choice

import time
from datetime import datetime


# Ignoring gates with parameters for now
gates = [gate for gate in get_standard_gate_name_mapping().values() if gate.params == [] and gate.num_clbits == 0]

def remove_outliers(data):
    """ Supprime les valeurs extrêmes basées sur l'IQR """
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [x for x in data if lower_bound <= x <= upper_bound]


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




def graph(time_list) :
    # Suppression des valeurs extrêmes --------------------------------------------
    time_list = remove_outliers(time_list)

    # Calcul des statistiques
    mean_time = np.mean(time_list)
    std_time = np.std(time_list)

    # Tracer l'histogramme normalisé
    plt.hist(time_list, bins="auto", density=True, alpha=0.5, color='b', label="Données")

    # Estimation par noyau gaussien (KDE)
    kde = gaussian_kde(time_list)
    x_range = np.linspace(min(time_list), max(time_list), 100)
    plt.plot(x_range, kde(x_range), 'g', label="Densité estimée (KDE)")

    # Superposition de la gaussienne ajustée (Normal PDF)
    pdf = norm.pdf(x_range, mean_time, std_time)
    plt.plot(x_range, pdf, 'r', linestyle="dashed", label="Distribution Normale ajustée")

    # Affichage
    plt.xlabel("Temps de simulation (ms)")
    plt.ylabel("Densité de probabilité")
    plt.title("Distribution du temps de simulation")
    plt.legend()
    plt.show()
    # -----------------------------------------------------


def execute(repetition = 5000, save = True) :
    circuits = fuzzing(1, 10, 25, save, verbose=False, random_init = True)

    for i in range(len(circuits)) :
        qc, date = circuits[i]

        
        simulator = AerSimulator()
        qc = transpile(qc, simulator, optimization_level=0)
        # qc.draw('mpl')

        total_exec_time = 0
        total_simul_time = 0

        time_list = []

        for n in range(repetition) :
            start = time.perf_counter()
            result = simulator.run(qc).result()
            end = time.perf_counter()

            total_exec_time += (end - start)
            total_simul_time += result.time_taken

            time_list.append(1000*result.time_taken)  # Only simul time for now
            if n%100 == 0 : print(n, time_list[-1])

        

        print(f"Duree d'execution moyen: {1000*total_exec_time/repetition} ms")
        #print(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")
        #print(f"Avant filtrage: {len(time_list)} valeurs, après filtrage: {len(time_list)} valeurs\n")


        graph(time_list)
        
        
        if save :
            with open("data/" + date, "a") as fichier :
                fichier.write(f"Duree d'execution moyen: {1000*total_exec_time/repetition} ms\n")
                fichier.write(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")

        counts = result.get_counts(qc)

        # print(f"Results for circuit {i+1} :", counts)
        # plot_histogram(counts)
        plt.show()



execute()