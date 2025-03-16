from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService

import matplotlib.pyplot as plt

def get_noise_models(my_token, my_backend) :
    service = QiskitRuntimeService(channel='ibm_quantum', token = my_token)
    backend = service.backend(my_backend)
    noise_model = NoiseModel.from_backend(backend)

    # Sauvegarder le modèle de bruit localement
    import pickle
    with open(my_backend + "_noise.pkl", "wb") as f:
        pickle.dump(noise_model, f)

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