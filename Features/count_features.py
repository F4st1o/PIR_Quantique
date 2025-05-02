from typing import Dict
import numpy as np
from scipy.stats import entropy, wasserstein_distance

#############################
# Count-based Features
#############################

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
    if not counts:
        return np.nan  # ou 0.0 selon ton besoin

    
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

    print("Shannon entropy:", shannon_entropy(counts))
    print("EMD vs uniform:", emd_uniform(counts))
    print("Classical fidelity vs ideal:", classical_fidelity(counts, ideal))
