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
parser.add_argument("--nb_gates", type=int, default=50, help="Nombre de portes par circuit.")
parser.add_argument("--shots", type=int, default=2**15, help="Nombre de répétitions pour chaque circuit.")
parser.add_argument("--backend", type=str, default="ibm_brisbane", help="Nom du backend (ibm_brisbane ou ibm_sherbrooke).")
parser.add_argument("--calculate", action="store_true", help="Envoie la requête sur le calculateur.")
args = parser.parse_args()


circuits = fuzzing.fuzzing(args.nb_circuits, args.nb_qbits, args.nb_gates, save=False, verbose=False, random_init=True)

 
# Load simulator on backend
service = QiskitRuntimeService()
real_backend = service.backend(args.backend)
simu_backend = AerSimulator.from_backend(real_backend)

 

def simulate() :
    for qc, date in circuits :
        pm = generate_preset_pass_manager(backend=simu_backend, optimization_level=0)
        isa_qc = pm.run(qc)
        sampler = Sampler(mode=simu_backend)
    ######
        total_exec_time = 0
        total_simul_time = 0

        time_list = []

        for n in range(5) :  # args.shots
            print(f"\n\nSimulation {n+1}/{args.shots} :\n")

            start = time.perf_counter() #-----------------

            job = sampler.run([isa_qc], shots=args.shots)
            
            # Waiting for the job to finish
            while not job.in_final_state() :
                print(job.status())
                time.sleep(0.1)

            end = time.perf_counter() #-----------------

            # If the simulation failed
            if job.status() == 'ERROR' :
                print(job.error_message())
                break


            print(job.status())
            metrics = job.metrics()

            print(f"\nTimestamps :\n{metrics['timestamps']}")

            duration = metrics['timestamps']['finished'] - metrics['timestamps']['running']
            simul_time = duration.microseconds


            print(f"Temps d'execution : {end - start} ms")
            print(f"Temps de simulation : {simul_time} µs")
            
            total_exec_time += (end - start)
            total_simul_time += simul_time

            time_list.append(simul_time)  # Only simul time for now
            if n%(args.shots//10) == 0 : print(n, time_list[-1])


        average = 1000*total_exec_time/args.shots
        print(f"Temps d'execution moyen: {average} ms")

        print(f"Temps de simulation moyen : {total_simul_time/args.shots} µs\n")



def calculate() :
    for qc, date in circuits :
        pm = generate_preset_pass_manager(backend=real_backend, optimization_level=0)
        isa_qc = pm.run(qc)
        sampler = Sampler(mode=real_backend)
    ######
        total_exec_time = 0
        total_simul_time = 0

        time_list = []

        for n in range(5) :  # args.shots
            print(f"\n\nCalculation {n+1}/{args.shots} :\n")

            start = time.perf_counter() #-----------------

            local_job = sampler.run([isa_qc], shots=args.shots)

            job = service.job(local_job.job_id())

            print(job.status())
            print(job.metrics())

            # Waiting for the job to finish
            while not job.in_final_state() :
                print(job.status())
                time.sleep(0.1)

            end = time.perf_counter() #-----------------

            job = service.job(job.job_id())

            # If the simulation failed
            if job.status() == 'ERROR' :
                print(job.error_message())
                break

            metrics = job.metrics()

            print(job.status())

            print(f"\nMetrics :\n{metrics}")

            datetime.str

            duration = datetime.datetime.fromisoformat(metrics['timestamps']['finished'].replace("Z", "+00:00")) - datetime.datetime.fromisoformat(metrics['timestamps']['running'].replace("Z", "+00:00"))  # Format de date incompatible lors de l'exécution sur le calculateur
            print(duration)
            simul_time = duration.microseconds
            print(f"Duration: {simul_time} µs")


            
            total_exec_time += (end - start)
            total_simul_time += simul_time

            time_list.append(simul_time)  # Only simul time for now
            if n%(args.shots//10) == 0 : print(n, time_list[-1])


        average = 1000*total_exec_time/args.shots
        print(f"Duree d'execution moyen: {average} ms")

        print(f"Temps simulation moyen : {total_simul_time/args.shots} µs\n")



simulate()

if args.calculate :
    calculate()