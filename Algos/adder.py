from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


def create(nb_qbits:int, ignore_carry=False, draw=False) -> QuantumCircuit :
    """
    Creates a quantum circuit that adds two numbers of `nb_qbits` Qbits.

    Parameters
    ----------
    nb_qbits : int
        Number of qubits to add

    ignore_carry : bool, optional
        True -> pyramid-shaped distribution

        False -> uniform distribution.

    draw : bool, optional
        If True, displays the circuit

        
    Returns
    -------
    qc : QuantumCircuit
        Quantum circuit of the adder
    """

    n = nb_qbits
    add_carry = 0 if ignore_carry else 1

    qc = QuantumCircuit(3*n+1, n+add_carry)
    qc.h(range(2*n))

    for i in (range(n)) :

        qc.ccx(i, i+n, i+2*n+1)
        qc.cx(i, i+n)

        qc.ccx(i+n, i+2*n, i+2*n+1)
        qc.cx(i+n, i+2*n)

        qc.cx(i, i+n)  # to restore the state of the second Qbit
        
    
    qc.measure(range(2*n, 3*n+add_carry), range(n+add_carry))
    if draw : qc.draw('mpl')
    return qc



if __name__ == "__main__":
    circuit = create(4, ignore_carry=False)

    result = AerSimulator().run(circuit, shots=2**20).result()
    statistics = result.get_counts()
    print(statistics)
    plot_histogram(statistics)
    plt.show()
