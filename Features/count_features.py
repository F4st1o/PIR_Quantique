from typing import Dict
import numpy as np
from scipy.stats import entropy, wasserstein_distance
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt


#############################
# Count-based Features
#############################


def emd(counts: Dict[str, int], ideal_counts: Dict[str, int]) -> float:
    """
    Calcule la distance de type Earth Mover's Distance (Wasserstein-1)
    entre deux distributions de counts.
    """
    count_values = list(counts.values())
    ideal_count_values = list(ideal_counts.values())

    return wasserstein_distance(count_values, ideal_count_values)


def shannon_entropy(counts: Dict[str, int]) -> float:
    """
    Calcule l'entropie de Shannon H = -sum(p_i log2 p_i) pour une distribution de counts.
    """
    freqs = np.array(list(counts.values()), dtype=float)
    ps = freqs / freqs.sum()

    return float(entropy(ps, base=2))


def emd_uniform(counts: Dict[str, int]) -> float:
    """
    Calcule la distance de type Earth Mover's Distance (Wasserstein-1)
    entre la distribution observée et la distribution uniforme.
    """
    count_values = np.array(list(counts.values()), dtype=float)
    unif_distribution = np.ones_like(count_values) / len(count_values)

    return wasserstein_distance(count_values, unif_distribution)


def variance_counts(counts: Dict[str, int]) -> float:
    """
    Calcule la variance des counts.
    """
    freqs = np.array(list(counts.values()), dtype=float)
    ps = freqs / freqs.sum()
    return float(ps.var())


def classical_fidelity(
    counts: Dict[str, int],
    ideal_counts: Dict[str, int]
) -> float:
    """
    Calcule la fidélité classique F = (sum(sqrt(p_i * q_i)))^2
    entre une distribution observée et une distribution idéale.
    """
    keys = set(counts) | set(ideal_counts)
    shots_obs = sum(counts.values())
    shots_ideal = sum(ideal_counts.values())
    s = 0.0
    for k in keys:
        p = counts.get(k, 0) / shots_obs
        q = ideal_counts.get(k, 0) / shots_ideal
        s += np.sqrt(p * q)
    return float(s ** 2)


# Exemple d'utilisation
if __name__ == "__main__":
    ideal = {'11101': 1010, '00011': 2040, '11000': 3597, '11100': 1529, '10101': 5085, '10010': 6755, '10110': 4591, '01101': 7214, '00001': 1047, '00110': 3529, '01001': 5003, '10001': 6999, '11010': 2533, '00101': 3073, '00111': 4120, '01011': 6185, '10111': 4017, '10100': 5670, '10011': 6314, '01110': 7677, '10000': 7859, '11011': 2080, '01111': 8242, '00100': 2536, '01010': 5533, '11110': 539, '00000': 507, '11001': 3064, '01000': 4675, '01100': 6570, '00010': 1479}
    
    counts_brisbane_simu = {'10111': 4913, '00101': 3078, '01011': 5683, '00000': 2087, '01100': 5993, '10101': 5036, '10010': 5651, '10000': 6003, '01110': 6200, '11111': 1985, '11101': 2131, '01010': 5528, '10011': 5536, '11110': 2017, '11000': 3134, '00110': 3240, '01001': 5225, '01111': 6201, '01000': 5213, '01101': 5830, '11011': 2723, '00011': 2578, '00010': 2514, '10001': 6113, '10110': 4854, '10100': 5146, '00111': 3374, '11001': 2947, '00100': 2952, '00001': 2139, '11010': 2704, '11100': 2344}
    counts_brisbane_calc = {'01001': 4613.4, '10110': 6298.4, '01011': 4686.4, '10011': 5457.4, '01111': 5040.4, '01010': 5165.0, '00111': 3914.2, '11111': 4889.6, '10000': 5620.2, '01000': 4778.4, '11110': 5384.0, '10001': 5510.4, '00001': 3662.6, '00010': 4103.4, '11101': 4893.6, '11000': 4986.0, '00101': 3856.4, '11011': 4771.0, '11100': 4914.8, '01100': 5043.4, '01101': 5031.0, '10111': 5747.8, '00110': 4253.2, '00011': 3665.2, '01110': 5477.8, '10100': 5848.6, '10010': 6131.0, '00100': 3930.6, '10101': 5713.8, '11001': 4813.0, '00000': 3706.6, '11010': 5378.8}

    counts_sherbrooke_simu = {'00001': 2843, '10101': 5249, '01110': 5357, '10011': 5421, '10111': 5408, '00111': 2819, '01101': 5374, '01100': 5403, '11111': 2852, '00010': 2875, '01000': 5551, '11101': 2778, '10010': 5543, '00110': 2813, '01010': 5340, '10110': 5233, '01011': 5464, '10001': 5285, '11011': 2739, '00101': 2852, '01111': 5417, '10000': 5383, '10100': 5388, '00000': 2904, '11000': 2740, '01001': 5387, '11010': 2715, '11100': 2702, '00100': 2808, '00011': 2825, '11001': 2704, '11110': 2900}
    counts_sherbrooke_calc = {'11101': 5176.8, '01111': 8891.8, '10100': 6040.6, '01101': 8462.6, '01100': 6331.8, '01011': 5222.2, '11111': 5416.4, '10101': 8010.0, '00111': 6352.2, '10000': 3445.0, '01010': 3928.4, '11001': 2981.8, '10010': 3563.0, '00000': 2688.8, '10001': 4628.4, '00010': 2810.8, '00011': 3840.4, '11011': 3108.4, '00110': 4779.8, '10111': 8434.0, '00001': 3608.4, '01110': 6681.8, '01001': 5057.2, '10110': 6284.4, '00100': 4494.0, '11110': 4010.8, '00101': 6115.0, '11010': 2340.0, '10011': 4799.4, '11100': 3844.4, '11000': 2209.6, '01000': 3728.2}


    plot_histogram(counts_sherbrooke_simu, title="Counts for Sherbrooke simulator")
    plot_histogram(counts_sherbrooke_calc, title="Average counts for Sherbrooke calculator")

    print("EMD simu:", emd(counts_sherbrooke_simu, ideal))
    print("EMD calc:", emd(counts_sherbrooke_calc, ideal))
    print("EMD simu/calc:", emd(counts_sherbrooke_simu, counts_sherbrooke_calc))

    print("\nEMD vs uniform:", emd_uniform(ideal))

    print("\nShannon entropy simu:", shannon_entropy(counts_sherbrooke_simu))
    print("Shannon entropy calc:", shannon_entropy(counts_sherbrooke_calc))

    print("\nClassical fidelity simu vs ideal:", classical_fidelity(counts_sherbrooke_simu, ideal))
    print("Classical fidelity calc vs ideal:", classical_fidelity(counts_sherbrooke_calc, ideal))

    plt.ylabel("Average counts")
    plt.tight_layout()
    plt.show()
