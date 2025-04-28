from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler



service = QiskitRuntimeService()

with open('job_id_list.txt', 'r') as fichier :
    job_id = fichier.readline()[:20]

    while (job_id != "") :
        print("Waiting for results")
        job = service.job(job_id)

        result = job.result()[0]
        print(f"Got results for job : {job_id}")

        print(job.metrics())
        print("\n\n")
        #print(result.data.meas.get_counts())

        job_id = fichier.readline()[:20]