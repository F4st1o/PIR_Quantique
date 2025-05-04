from typing import Dict
import numpy as np
from scipy.stats import entropy, wasserstein_distance

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
    # Distribution exemple
    ideal = {"00": 512, "11": 512}
    counts = {"00": 400, "01": 50, "10": 50, "11": 524}

    ideal = {'01100': 1406, '01010': 1263, '10110': 1116, '01001': 1217, '10010': 1395, '01110': 1458, '00110': 951, '10001': 1452, '01111': 1467, '01000': 1231, '00011': 676, '00001': 562, '10100': 1251, '00100': 855, '10101': 1212, '01011': 1326, '11001': 847, '00111': 954, '00101': 797, '11110': 561, '10011': 1349, '11111': 519, '01101': 1441, '00000': 571, '10111': 1108, '00010': 677, '11100': 619, '10000': 1447, '11010': 806, '11101': 594, '11000': 867, '11011': 773}
    counts = {'01101': 968, '10101': 1174, '10011': 1216, '10010': 1198, '10111': 1296, '00111': 953, '10110': 1305, '11110': 1041, '01100': 978, '00110': 938, '00001': 831, '00011': 889, '01011': 1010, '11011': 976, '01111': 976, '11100': 1025, '11010': 950, '11101': 984, '11001': 910, '01001': 972, '01110': 1036, '11111': 1060, '00000': 936, '10000': 1200, '01000': 1047, '01010': 1021, '10100': 1180, '10001': 1089, '00010': 940, '00100': 869, '00101': 898, '11000': 902}

    print("EMD:", emd(counts, ideal))
    print("Shannon entropy:", shannon_entropy(counts))
    print("EMD vs uniform:", emd_uniform(counts))
    print("Classical fidelity vs ideal:", classical_fidelity(counts, ideal))
