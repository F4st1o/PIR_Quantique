# Importations modernes (Qiskit 1.0+)
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import Options
# 1. Connexion au compte IBM Quantum (méthode moderne)
service = QiskitRuntimeService(
    channel="ibm_quantum",
    My_Key = "" # Put your token between the quotes
)

# 2. Création du circuit quantique (inchangé)
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

# 3. Choix du backend (nouvelle nomenclature)
backend = service.backend("ibm_sherbrooke")  # Les noms ont changé (ajout de "ibm_")

options = Options()
options.transpilation = {"optimization_level": 3}
options.resilience = {"level": 1}
options.environment = {"log_level": "INFO"}


# 4. Exécution avec gestion de session (méthode recommandée)
with Session(service=service, backend=backend) as session:
    job = backend.run(qc, options=options, shots=1024)
    
    # 5. Surveillance du job (méthode moderne)
  #  job_monitor(job)
    
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
options.environment.log_level = "INFO"  # Logging détailléfrom qiskit_ibm_provider.job import job_monitor
