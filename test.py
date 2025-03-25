import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Supposons qu'on ait les temps d'exécution pour 3 circuits
circuits_times = [
    np.random.normal(loc=15, scale=1, size=1000),  # Circuit 1
    np.random.normal(loc=20, scale=1.5, size=1000),  # Circuit 2
    np.random.normal(loc=25, scale=2, size=1000)  # Circuit 3
]

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

bin_count = 30  # Nombre de bins sur l'axe X (temps)
bin_edges = np.linspace(10, 35, bin_count + 1)  # Plage commune

# Largeur des barres
dx = (bin_edges[1] - bin_edges[0]) * 0.8
dy = 0.8  # hauteur entre circuits

for i, times in enumerate(circuits_times):
    hist, _ = np.histogram(times, bins=bin_edges)
    xs = bin_edges[:-1]
    ys = np.full_like(xs, i)

    ax.bar3d(xs, ys, np.zeros_like(xs), dx, dy, hist, shade=True)

# Étiquettes
ax.set_xlabel("Temps d'exécution (ms)")
ax.set_ylabel("Index du circuit")
ax.set_zlabel("Fréquence")
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(["Circuit 1", "Circuit 2", "Circuit 3"])
ax.set_title("Histogramme 3D des temps d'exécution")

plt.tight_layout()
plt.show()
