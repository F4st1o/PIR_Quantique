from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService

import fuzzing
import argparse
import time
import datetime


# Configuration des arguments
parser = argparse.ArgumentParser(description="Simulate quantum circuits with optional parameters.")
parser.add_argument("--nb_circuits", type=int, default=1, help="Nombre de circuits à générer.")
parser.add_argument("--nb_qbits", type=int, default=5, help="Nombre de qubits par circuit.")
parser.add_argument("--nb_gates", type=int, default=10, help="Nombre de portes par circuit.")
parser.add_argument("--shots", type=int, default=2**15, help="Nombre de répétitions pour chaque circuit.")
parser.add_argument("--backend", type=str, default="ibm_brisbane", help="Nom du backend IBM Quantum.")
parser.add_argument("--calculate", action="store_true", help="Envoie la requête sur le calculateur (pas de simulation).")
args = parser.parse_args()


circuits = fuzzing.fuzzing(args.nb_circuits, args.nb_qbits, args.nb_gates, save=False, verbose=False, random_init=True)

 
# Load simulator on backend
service = QiskitRuntimeService()
backend = service.backend(args.backend)

if not args.calculate :
    print("Simulating execution")
    backend = AerSimulator.from_backend(backend)
 


for qc, date in circuits :
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
    isa_qc = pm.run(qc)
    sampler = Sampler(mode=backend)
######
    total_exec_time = 0
    total_simul_time = 0

    time_list = []

    for n in range(5) :  # args.shots
        start = time.perf_counter() #-----------------

        local_job = sampler.run([isa_qc], shots=args.shots)
        if args.calculate :
            job = service.job(local_job.job_id())

            print(job.status())
            job.wait_for_final_state()

        else :
            while not local_job.done() :
                time.sleep(0.1)



        end = time.perf_counter() #-----------------

        if args.calculate :
            job = service.job(job.job_id())

        else :
            job = local_job

        metrics = job.metrics()

        print(job.status())

        print(f"\nMetrics :\n{metrics}")

        duration = metrics['timestamps']['finished'] - metrics['timestamps']['running']  # Format de date incompatible lors de l'exécution sur le calculateur
        simul_time = duration.microseconds
        print(f"Duration: {simul_time} µs")


        
        total_exec_time += (end - start)
        total_simul_time += simul_time

        time_list.append(simul_time)  # Only simul time for now
        if n%(args.shots//10) == 0 : print(n, time_list[-1])


    average = 1000*total_exec_time/args.shots
    print(f"Duree d'execution moyen: {average} ms")

    print(f"Temps simulation moyen : {total_simul_time/args.shots} µs\n")