from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeVigoV2

def res_noise(qc) :
    backend = FakeVigoV2() # Noise type ?
    noise_model = NoiseModel.from_backend(backend)

    coupling_map = backend.configuration().coupling_map

    basis_gates = noise_model.basis_gates

    backend = AerSimulator(noise_model=noise_model, coupling_map=coupling_map, basis_gates=basis_gates)
    transpiled_circuit = transpile(qc, backend)
    result = backend.run(transpiled_circuit).result()

    counts = result.get_counts(0)
    plot_histogram(counts)

def conc_res(qc) :
    res = []

    result1 = AerSimulator().run(qc).result()
    count1s = result1.get_counts()
    res.append(count1s)
    print(counts1)

    result2 = TerraSampler().run(qc).result()
    counts2 = pub_result2.quasi_dists[0]
    res.append(count2s)
    print(counts2)

    return res

def print_res_by_sim(nom_sim) :
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