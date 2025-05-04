from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


import fuzzing
import adder
import argparse
import time
import datetime



def simulate(circuit, backend, shots: int, nb_simulations=1) -> None :
    """
    Simulates the quantum `circuit` on a given backend.

    Parameters
    ----------
    circuit : QuantumCircuit
        List of quantum circuits to simulate

    backend : BackendV2
        The simulation backend

    shots : int
        Number of shots for the simulation

    nb_simulations : int
        Number of simulations to run
    """
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
    isa_qc = pm.run(circuit)
    sampler = Sampler(mode=backend)


    counts_list = []
    duration_list = []

    for n in range(nb_simulations) :
        print(f"\n\nSimulation {n+1}/{nb_simulations} :")

        start = time.perf_counter()

        #-----------------
        job = sampler.run([isa_qc], shots=shots)
        
        # Waiting for the job to finish
        while not job.in_final_state() :
            print(job.status())
            time.sleep(0.1)
        #-----------------

        end = time.perf_counter() 
        duration = end - start
        duration_list.append(duration)

        print(job.status())

        # If the simulation failed
        if job.status() == 'ERROR' :
            print(job.error_message())
            break
        
        # Print counts histogram
        # print(job.result())
        result = job.result()[0]
        counts = result.data.c.get_counts()
        counts_list.append(counts)
        print("\nCounts :\n", counts)
        plot_histogram(counts)
        plt.show()

        timestamps = job.metrics()['timestamps']
        print(f"\nTimestamps :")
        for key in timestamps :
            print(f"\t{key} : {timestamps[key]}")



        print(f"\nMeasured duration : {duration} seconds")
        

    print(f"\n\nAverage measured duration : {sum(duration_list)/nb_simulations} seconds")

    return counts_list, duration_list



def calculate(circuit, service, backend, shots:int, nb_calculations=1) -> None :
    """
    Simulates the quantum `circuit` on a real backend.

    Parameters
    ----------
    circuit : QuantumCircuit
        Quantum circuits to run on the calculator

    service : QiskitRuntimeService
        The service to use for the calculation

    backend : BackendV2
        The backend to use for the calculation

    shots : int
        Number of shots for the calculation
    """
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
    isa_qc = pm.run(circuit)
    sampler = Sampler(mode=backend)


    counts_list = []
    measured_duration_list = []
    reported_duration_list = []
    
    for n in range(nb_calculations) :
        print(f"\n\nCalculation {n+1}/{nb_calculations} :")

        start = time.perf_counter()
        #-----------------
        job = sampler.run([isa_qc], shots=shots)
        job = service.job(job.job_id())

        # Save the job ID to a file to access it later
        with open('job_id_list.txt', 'a') as fichier:
            fichier.write(job.job_id() + "\n")

        # Waiting for the job to finish
        while not job.in_final_state() :
            print(job.status())
            time.sleep(0.1)
            job = service.job(job.job_id())
        #-----------------
        end = time.perf_counter()
        measured_duration = end - start
        measured_duration_list.append(measured_duration)

        job = service.job(job.job_id())
        print(job.status())

        # If the calculation failed
        if job.status() == 'ERROR' :
            print(job.error_message())
            break
        

        # Print counts histogram
        # print(job.result())
        result = job.result()[0]
        counts = result.data.c.get_counts()
        counts_list.append(counts)
        print("\nCounts :\n", counts)
        plot_histogram(counts)
        plt.show()


        metrics = job.metrics()
        # print(f"\nMetrics :")
        # for key in metrics :
        #     print(f"\t{key} : {metrics[key]}")


        timestamps = metrics['timestamps']
        print(f"\nTimestamps :")
        for key in timestamps :
            print(f"\t{key} : {timestamps[key]}")


        reported_duration = datetime.datetime.fromisoformat(timestamps['finished'].replace("Z", "+00:00")) - datetime.datetime.fromisoformat(timestamps['running'].replace("Z", "+00:00"))
        reported_duration_list.append(reported_duration.total_seconds())
        print(f"\nMeasured duration : {measured_duration} seconds")
        print(f"Reported duration : {reported_duration.total_seconds()} seconds")



    print(f"\n\nAverage measured duration: {sum(measured_duration_list)/nb_calculations} seconds")
    print(f"Average reported duration : {sum(reported_duration_list)/nb_calculations} seconds\n")

    return counts_list, measured_duration_list, reported_duration_list



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate quantum circuits with optional parameters.")
    parser.add_argument("--nb_circuits", type=int, default=3, help="Nombre de circuits à générer.")
    parser.add_argument("--nb_qbits", type=int, default=20, help="Nombre de qubits par circuit.")
    parser.add_argument("--nb_gates", type=int, default=200, help="Nombre de portes par circuit.")
    parser.add_argument("--shots", type=int, default=2**15, help="Nombre de répétitions pour chaque circuit.")
    parser.add_argument("--backend", type=str, default="ibm_sherbrooke", help="Nom du backend (ibm_brisbane ou ibm_sherbrooke).")
    parser.add_argument("--calculate", action="store_true", help="Envoie la requête sur le calculateur.")
    parser.add_argument("--adder", action="store_true", help="Use an adder instead of fuzzing.")
    args = parser.parse_args()


    TOKEN = "5beaf0819b6a2df9aa41c94a0e65b3d8520c89c158823545dcb70710b4ecb6efd5d524de45d2b58a1172d3675407c53edad235f46d861cec36b24bba12671853"

 
    # Load simulator on backend
    service = QiskitRuntimeService(channel='ibm_quantum', token=TOKEN)
    real_backend = service.backend(args.backend)
    simu_backend = AerSimulator.from_backend(real_backend)

    if args.adder :
        circuits = [(adder.create(args.nb_qbits), "")]
        
    else :
        circuits = fuzzing.fuzzing(args.nb_circuits, args.nb_qbits, args.nb_gates, save=False, verbose=False, random_init=True)
    

    for circuit, _ in circuits :
        simulate(circuit, simu_backend, args.shots)

        if args.calculate :
            calculate(circuit, service, real_backend, args.shots)