from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_aer.noise import NoiseModel
from qiskit.transpiler import CouplingMap
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
from qiskit_ibm_runtime.noise_learner import NoiseLearner
from qiskit_ibm_runtime.options import (NoiseLearnerOptions,ResilienceOptionsV2,EstimatorOptions,)
from datetime import datetime

#from qiskit_ibm_runtime import QiskitRuntimeService
#from qiskit_ibm_provider import IBMProvider
#from qiskit_ibm_provider.least_busy import least_busy
#from qiskit import IBMQ
import matplotlib.pyplot as plt

My_Key = "" # Put your token between the quotes

# Charger le compte IBM
#QiskitRuntimeService.save_account(channel="ibm_quantum", token=My_Key, set_as_default=True)


def get_noise_models_calculators() :
    # Lister les backend physiques (ordinateurs quantiques)
    service = QiskitRuntimeService()
    return service.backends(simulator=False, operational=True, min_num_qubits=10)
    


# def print_noise_model_calculators() :
#     backends = get_noise_models_calculators()
#     file = open("noise_models.txt", "w")

#     for backend in backends:
#         props = backend.properties()
#         file.write("Backend:"  + backend.name + "\n")
#         list = [str(props.t1(q)) for q in range(backend.configuration().n_qubits)]
#         str1 = "["+ ", ".join(list) + "]"
#         file.write("T1 (temps de decoherence) des qubits:"+ str1 + "\n")
#         list = [ str(props.t2(q)) for q in range(backend.configuration().n_qubits)]
#         str1 = "["+ ", ".join(list) + "]"
#         file.write("T2 (temps de coherence) des qubits: " + str1 + "\n")
#         file.write("-" * 40 + "\n")        
#         """
#         print(f"Backend: {backend.name}")
#         print("T1 (temps de decoherence) des qubits:", [props.t1(q) for q in range(backend.configuration().n_qubits)])
#         print("T2 (temps de coherence) des qubits:", [props.t2(q) for q in range(backend.configuration().n_qubits)])
#         """
#         #print("Erreurs de porte:", [props.gate_error('cx', [i, j]) for i in range(backend.configuration().n_qubits) for j in range(i + 1, backend.configuration().n_qubits)])
#         print("-" * 40)
    



def get_noise_model(backend) :
    when = datetime.now()
    #service = QiskitRuntimeService(channel='ibm_quantum', token = my_token)
    #backend = service.backend(my_backend)
    noise_model = NoiseModel.from_backend(backend)

    # Sauvegarder le modèle de bruit localement
    import pickle
    with open(backend.name +"_"+ str(when.date()).replace("-","_") + "_noise.pkl", "wb") as f:
        pickle.dump(noise_model, f)


def get_noise_models() :
    backends = get_noise_models_calculators()
    for backend in backends:
        get_noise_model(backend)



def get_sim_from_noise(qc, my_backend) :
    # Backends physiques != simulés (aer, qasm, ...) :
    # ibmq_manila : un processeur quantique à 5 qubits
    # ibmq_jakarta : un processeur quantique à 7 qubits
    # ibm_washington : un processeur quantique à 127 qubits

    """ Pour créer une session avec un calculateur quantique à partir d'un token """
    ################################################################################
    # service = QiskitRuntimeService(channel='ibm_quantum', token = my_token)
    # -> Connexion via ibm_quantum (Accès gratuit ou premium, channel standard)
    # -> Connexion via ibm_cloud (Accès avec compte IBM Cloud pour du cloud)
    ################################################################################

    import pickle
    with open(my_backend + "_noise.pkl", "rb") as f:
        my_noise_model = pickle.load(f)

    qc_transpiled = transpile(qc, backend=my_backend) # traduit le circuit en utilisant uniquement les portes natives du backend choisi
    simulator = AerSimulator(noise_model=my_noise_model)

    return simulator
    # result = simulator.run(qc_transpiled).result()

def conc_res(qc) :
    res = []

    result1 = AerSimulator().run(qc).result()
    counts1 = result1.get_counts()
    res.append(counts1)
    print(counts1)

    result2 = TerraSampler().run(qc).result()
    counts2 = pub_result2.quasi_dists[0]
    res.append(counts2)
    print(counts2)

    return res

def print_res_by_sim(nom_sim, qc) :
    res = conc_res(qc)

    match nom_sim:
        case "AER":
            plot_histogram(res[1])
        case "STV":
            plot_histogram(res[2])
        case "UNIT":
            plot_histogram(res[3])
        case "DENS":
            plot_histogram(res[4])
        case "STAB":
            plot_histogram(res[5])
        case "MAPROD":
            plot_histogram(res[6])
        case _:
            print("Bad simulator request !")
    
    plt.show()

##################################################################################################################################################
#
# Many simulators : AerSimulator, StatevectorSimulator, UnitarySimulator, DensityMatrixSimulator, StabilizerSimulator, MatrixProductStateSimulator
# 
##################################################################################################################################################

get_noise_models()