from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from qiskit_ibm_runtime import Options
# Pour affichage et outliers
#from utils import remove_outliers, graph, graph3d

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm, gaussian_kde

from random import sample, choice

import time
from datetime import datetime


TOKEN = "5beaf0819b6a2df9aa41c94a0e65b3d8520c89c158823545dcb70710b4ecb6efd5d524de45d2b58a1172d3675407c53edad235f46d861cec36b24bba12671853"

# QiskitRuntimeService.save_account(token=TOKEN, overwrite=True, channel="ibm_quantum")

# Ignoring gates with parameters for now
gates = [gate for gate in get_standard_gate_name_mapping().values() if gate.params == [] and gate.num_clbits == 0]

def remove_outliers(data, upper_bound):
    """ Supprime les valeurs extrêmes basées sur l'IQR """
    return [x for x in data if x <= upper_bound]


def fuzzing(nb_circuits: int, nb_qbits: int, nb_gates: int, save=False, verbose = False, random_init = False) -> list[QuantumCircuit, str] :
    """
    Generates a list of circuits with random gates and Qbits

    Parameters
    ----------
    nb_circuits : int
        Number of circuits to generate

    nb_qQiskitRuntimeService()
        A list of QuantumCircuit objects
    """

    print(f"Generating {nb_circuits} circuits with {nb_qbits} Qbits and {nb_gates} gates")
    circuits = []
    for i in range(nb_circuits) :
        date = datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")[:-3]
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


def graph3d(circuit_list) :
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    bin_count = 500  # Nombre de bins sur l'axe X (temps)
    bin_edges = np.linspace(0, 200, bin_count + 1)  # Plage commune

    # Largeur des barres
    dx = (bin_edges[1] - bin_edges[0]) * 0.8
    dy = 0.8  # hauteur entre circuits

    for i, times in enumerate(circuit_list):
        hist, _ = np.histogram(times, bins=bin_edges)
        xs = bin_edges[:-1]
        ys = np.full_like(xs, i)

        ax.bar3d(xs, ys, np.zeros_like(xs), dx, dy, hist, shade=True)

    # Étiquettes
    ax.set_xlabel("Temps d'exécution (ms)")
    ax.set_ylabel("Index du circuit")
    ax.set_zlabel("Fréquence")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Circuit 1", "Circuit 2", "Circuit 3"])
    ax.set_title("Histogramme 3D des temps d'exécution")

    plt.tight_layout()
    plt.show()

def graph(time_list) :
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


def execute(repetition = 1000, save = True) :
    circuits = fuzzing(3, 10, 25, save, verbose=False, random_init = True)

    time_list_list = []
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

        
        average = 1000*total_exec_time/repetition
        print(f"Duree d'execution moyen: {average} ms")
        #print(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")
        #print(f"Avant filtrage: {len(time_list)} valeurs, après filtrage: {len(time_list)} valeurs\n")


        # Suppression des valeurs extrêmes
        time_list = remove_outliers(time_list, 2*average)

        graph(time_list)
        time_list_list.append(time_list)
        
        
        if save :
            with open("data/" + date, "a") as fichier :
                fichier.write(f"Duree d'execution moyen: {1000*total_exec_time/repetition} ms\n")
                fichier.write(f"Temps simulation moyen : {1000*total_simul_time/repetition} ms\n")

        counts = result.get_counts(qc)

        # print(f"Results for circuit {i+1} :", counts)
        # plot_histogram(counts)
        plt.show()

    graph3d(time_list_list)


def calculate() :
    circuits = fuzzing(1, 10, 25, save=False, verbose=True, random_init = True)

    example_circuit, date = circuits[0]

    # You'll need to specify the credentials when initializing QiskitRuntimeService, if they were not previously saved.
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)

    qc = transpile(example_circuit, backend=backend, optimization_level=0)
    
    sampler = Sampler(backend)
    print("Running job")
    job = sampler.run([qc], shots=100)
    print(f"job id: {job.job_id()}")

    return job.job_id()



    


def getResults(job_id) :
    service = QiskitRuntimeService()

    job = service.job(job_id)

    print("Waiting for results")
    result = job.result()[0]
    print("Got results")

    print(result.data.meas.get_counts())


#execute()
#job_id = calculate()
getResults("czq56gtd8drg008gf0yg")