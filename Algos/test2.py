# Importations modernes (Qiskit 1.0+)
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Options
from qiskit.tools.monitor import job_monitor

# 1. Connexion au compte IBM Quantum (méthode moderne)
service = QiskitRuntimeService(
    channel="ibm_quantum",
    token="5beaf0819b6a2df9aa41c94a0e65b3d8520c89c158823545dcb70710b4ecb6efd5d524de45d2b58a1172d3675407c53edad235f46d861cec36b24bba12671853" # Remplacer par votre token réel
)

# 2. Création du circuit quantique (inchangé)
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# 3. Choix du backend (nouvelle nomenclature)
backend = service.backend("ibm_lima")  # Les noms ont changé (ajout de "ibm_")

# Configuration des options d'exécution
options = Options()
options.execution.shots = 1024
options.optimization_level = 3  # Niveau d'optimisation du transpiler

# 4. Exécution avec gestion de session (méthode recommandée)
with Session(service=service, backend=backend) as session:
    job = backend.run(qc, options=options)
    
    # 5. Surveillance du job (méthode moderne)
    job_monitor(job)
    
    # 6. Récupération des résultats
    result = job.result()
    counts = result.get_counts()

# 7. Affichage des résultats
print("\nRésultats de mesure:")
print(counts)

# Visualisation du circuit
qc.draw(output="mpl")

# Informations détaillées sur le backend
print(backend.status())
print(backend.configuration().to_dict())

# Options avancées (exemple)
options.resilience_level = 1  # Correction d'erreurs basique
options.environment.log_level = "INFO"  # Logging détaillé