from qiskit_aer import AerSimulator
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService

import fuzzing
import argparse
import time
import datetime


def simulate(circuits, service, simu_backend, shots) :
    for qc, date in circuits :
        pm = generate_preset_pass_manager(backend=simu_backend, optimization_level=0)
        isa_qc = pm.run(qc)
        sampler = Sampler(mode=simu_backend)
    ######
        total_exec_time = 0
        total_simul_time = 0

        time_list = []

        for n in range(5) :  # args.shots
            print(f"\n\nSimulation {n+1}/5 :\n")

            start = time.perf_counter() #-----------------

            job = sampler.run([isa_qc], shots=shots)
            
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
            if n%(shots//10) == 0 : print(n, time_list[-1])


        average = 1000*total_exec_time/shots
        print(f"Temps d'execution moyen: {average} ms")

        print(f"Temps de simulation moyen : {total_simul_time/shots} µs\n")



def calculate(circuits, service, real_backend, shots) :
    for qc, date in circuits :
        pm = generate_preset_pass_manager(backend=real_backend, optimization_level=0)
        isa_qc = pm.run(qc)
        sampler = Sampler(mode=real_backend)
    ######
        total_exec_time = 0
        total_simul_time = 0

        time_list = []

        for n in range(5) :  # args.shots
            print(f"\n\nCalculation {n+1}/5 :\n")

            start = time.perf_counter() #-----------------

            job = sampler.run([isa_qc], shots=shots)

            job = service.job(job.job_id())

            with open('job_id_list.txt', 'a') as fichier:
                fichier.write(job.job_id() + "\n")

            # Waiting for the job to finish
            while not job.in_final_state() :
                print(job.status())
                time.sleep(0.1)
                job = service.job(job.job_id())

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
            if n%(shots//10) == 0 : print(n, time_list[-1])


        average = 1000*total_exec_time/shots
        print(f"Duree d'execution moyen: {average} ms")

        print(f"Temps simulation moyen : {total_simul_time/shots} µs\n")
        return job.result().get_counts(qc), metrics



if __name__ == "__main__":
    # Configuration des arguments
    parser = argparse.ArgumentParser(description="Simulate quantum circuits with optional parameters.")
    parser.add_argument("--nb_circuits", type=int, default=3, help="Nombre de circuits à générer.")
    parser.add_argument("--nb_qbits", type=int, default=20, help="Nombre de qubits par circuit.")
    parser.add_argument("--nb_gates", type=int, default=200, help="Nombre de portes par circuit.")
    parser.add_argument("--shots", type=int, default=2**15, help="Nombre de répétitions pour chaque circuit.")
    parser.add_argument("--backend", type=str, default="ibm_sherbrooke", help="Nom du backend (ibm_brisbane ou ibm_sherbrooke).")
    parser.add_argument("--calculate", action="store_true", help="Envoie la requête sur le calculateur.")
    args = parser.parse_args()



    # Only done once per machine
    TOKEN = "5beaf0819b6a2df9aa41c94a0e65b3d8520c89c158823545dcb70710b4ecb6efd5d524de45d2b58a1172d3675407c53edad235f46d861cec36b24bba12671853"
    QiskitRuntimeService.save_account(token=TOKEN, overwrite=True, channel="ibm_quantum")


 
    # Load simulator on backend
    service = QiskitRuntimeService()
    real_backend = service.backend(args.backend)
    simu_backend = AerSimulator.from_backend(real_backend)

    circuits = fuzzing.fuzzing(args.nb_circuits, args.nb_qbits, args.nb_gates, save=False, verbose=False, random_init=True)
    simulate(circuits, simu_backend, args.shots)

    if args.calculate :
        calculate(circuits, real_backend, args.shots)