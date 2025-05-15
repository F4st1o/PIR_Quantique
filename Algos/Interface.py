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
import pickle
import matplotlib.pyplot as plt

My_Key = "" # Put your token between the quotes


# Charger le compte IBM
#QiskitRuntimeService.save_account(channel="ibm_quantum", token=My_Key, set_as_default=True)


def get_noise_models_calculators() :
    # Lister les backend physiques (ordinateurs quantiques)
    service = QiskitRuntimeService()
    return service.backends(simulator=False, operational=True, min_num_qubits=10)

def get_noise_model(backend) :
    when = datetime.now()
    #service = QiskitRuntimeService(channel='ibm_quantum', token = my_token)
    #backend = service.backend(my_backend)
    noise_model = NoiseModel.from_backend(backend)

    # Sauvegarder le modèle de bruit localement
    with open("noise_models/"+ backend.name +"_"+ str(when.date()).replace("-","_") + "_noise.pkl", "wb") as f:
        pickle.dump(noise_model, f)



# fonction pour récupérer les noise_models disponiples des calculateurs sur IBM quantum au moment de l'execution de cette fonction  ----------------------------------------
def save_noise_models() :
    backends = get_noise_models_calculators()
    for backend in backends:
        get_noise_model(backend)

# fonction qui permet de recupérer le noise_model sauvegarder ------------------------------------------------------------
def load_noise_model(file_name) :
    with open("noise_models/" + file_name, "rb") as f:
        return pickle.load(f)

# fonction pour recuperer simulateur a partir nom du noise model ---------------------------------
def get_sim_from_noise(qc, file_name) :
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

    my_noise_model = load_noise_model(file_name)
    simulator = AerSimulator(noise_model=my_noise_model)
    return simulator
    # result = simulator.run(qc_transpiled).result()


# fonction qui permet de sauvegarder un qc ------------------------------------------------------------
def save_qc(qc) :
    date = datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")[:-3]
    with open("data/circuit/" + date + "_qc.pkl", "wb") as f:
        pickle.dump(qc, f)


# fonction qui permet de recupérer le qc sauvegarder ------------------------------------------------------------
def load_qc(file_name) :
    with open("data/" + file_name, "rb") as f:
        return pickle.load(f)


"""def conc_res(qc) :
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

1-
save_noise_models()

2-
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
save_qc(qc)

3-
qc = load_qc("2025-04-25 11-42-00-577_qc.pkl")
print(qc.draw())"""