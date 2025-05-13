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
    counts_bribane_simu = {'00011': 2550, '00110': 3597, '00101': 3239, '10100': 5108, '10111': 4530, '11111': 1706, '11101': 2169, '10011': 5573, '11001': 3195, '11010': 2794, '01111': 6342, '01100': 6021, '01101': 6117, '11110': 1818, '10110': 4579, '11100': 2189, '00111': 3573, '10010': 5882, '00001': 2105, '10101': 4852, '01011': 5368, '01110': 6357, '01010': 5359, '11011': 2815, '10001': 6214, '00000': 1990, '01001': 5003, '11000': 3201, '10000': 6265, '01000': 5064, '00010': 2415, '00100': 3082}
    counts_sherbrooke_simu = {'01100': 5175, '10011': 5085, '10010': 5133, '00101': 3101, '01011': 5134, '11010': 3013, '10101': 5108, '00000': 3157, '11111': 2947, '10000': 5236, '00011': 3112, '01010': 5143, '01101': 5149, '01111': 5135, '01001': 5368, '10100': 5102, '10001': 5182, '01000': 5185, '11000': 3032, '11100': 3059, '11011': 2896, '11001': 3023, '10110': 5071, '00111': 3106, '10111': 5118, '00001': 3189, '11110': 2997, '11101': 2924, '00100': 2957, '00010': 3051, '01110': 5171, '00110': 3013}
    counts_sherbrooke_calc = {'01101': 6630, '10101': 5165, '10110': 4018, '10001': 3503, '11001': 3217, '01100': 4962, '00111': 5649, '10111': 5147, '01001': 4569, '11000': 2348, '10011': 3408, '01110': 5092, '01011': 4766, '00011': 3907, '01000': 3476, '11110': 3618, '00010': 2883, '01111': 6703, '00101': 5600, '10100': 3878, '10010': 2575, '00100': 4254, '11101': 4709, '00110': 4186, '00001': 3913, '11100': 3518, '11111': 4651, '01010': 3525, '00000': 2940, '11010': 2411, '11011': 3200, '10000': 2651}

    plot_histogram(counts_sherbrooke_simu)
    plot_histogram(counts_sherbrooke_calc)
    print("EMD simu:", emd(counts_sherbrooke_simu, ideal))
    print("EMD calc:", emd(counts_sherbrooke_calc, ideal))
    print("EMD simu/calc:", emd(counts_sherbrooke_simu, counts_sherbrooke_calc))

    print("EMD vs uniform:", emd_uniform(counts_bribane_simu))
    print("Shannon entropy:", shannon_entropy(counts_bribane_simu))
    print("Classical fidelity vs ideal:", classical_fidelity(counts_bribane_simu, ideal))
    plt.show()
