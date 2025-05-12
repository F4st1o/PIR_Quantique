from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt



service = QiskitRuntimeService()

with open('job_id_list_past.txt', 'r') as fichier :
    job_id = fichier.readline()[:20]

    while (job_id != "") :
        print("Waiting for results")
        job = service.job(job_id)

        result = job.result()[0]
        print(f"Got results for job : {job_id}")

        print(job.metrics())
        print("\n\n")

        try :
            print(result.data.c.get_counts())

            plot_histogram(result.data.c.get_counts())
            plt.show()

        except :
            pass

        job_id = fichier.readline()[:20]