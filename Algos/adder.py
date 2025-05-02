from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import get_standard_gate_name_mapping
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from qiskit_ibm_runtime import Options
# Pour affichage et outliers
#from utils import remove_outliers, graph, graph3d

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import norm, gaussian_kde

from random import sample, choice

import time
from datetime import datetime


def adder(nb_qbits):
    '''
    Additionne 2 nombres de nb_qbits
    '''

    n = nb_qbits
    qc = QuantumCircuit(3*n+1)

    qc.h(range(2*n))

    for i in (range(n)) :

        qc.ccx(i, i+n, i+2*n+1)
        qc.cx(i, i+n)

        qc.ccx(i+n, i+2*n, i+2*n+1)
        qc.cx(i+n, i+2*n)

        qc.cx(i, i+n)
        
    
    qc.measure_all()
   # qc.draw('mpl')
    return qc



if __name__ == "__main__":
    # Récupérer token et NoiseModel pour un QPU IBM
    circuit = adder(2)
    result = AerSimulator().run(circuit).result()
    statistics = result.get_counts()
    print(statistics)
    plot_histogram(statistics)
    plt.show()
    