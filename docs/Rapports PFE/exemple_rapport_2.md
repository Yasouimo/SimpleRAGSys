# Rapport de Stage PFE - Classification d'Images par Deep Learning

**Étudiant:** Ahmed Ben Ali  
**Entreprise:** AI Vision Labs  
**Durée:** 5 mois (Mars - Juillet 2024)  
**Encadrant:** Dr. Sophie Laurent, Data Scientist Senior

## 1. Introduction et contexte

### Problématique
AI Vision Labs travaille avec des clients du secteur médical pour automatiser la détection de pathologies sur des images radiologiques. Le défi principal est d'atteindre une précision supérieure à 90% tout en maintenant un temps d'inférence rapide.

### Objectifs du stage
1. Développer un modèle de classification d'images médicales (3 classes: normal, anomalie bénigne, anomalie maligne)
2. Optimiser les performances du modèle (accuracy > 90%, inference < 100ms)
3. Déployer le modèle en production avec une API REST
4. Créer une interface web de démonstration

## 2. État de l'art

### Technologies étudiées
- **CNN classiques:** VGG16, ResNet, Inception
- **Transfer Learning:** Utilisation de modèles pré-entraînés sur ImageNet
- **Data Augmentation:** Rotation, zoom, flip pour enrichir le dataset
- **Techniques d'optimisation:** Learning rate scheduling, early stopping

## 3. Méthodologie et approche

### Phase 1: Préparation des données (3 semaines)
- Collection de 15,000 images radiologiques anonymisées
- Nettoyage et validation par des médecins experts
- Split: 70% train, 15% validation, 15% test
- Normalisation et preprocessing (resize 224x224, normalisation [-1, 1])

### Phase 2: Développement du modèle (6 semaines)
Approche itérative avec 5 expérimentations:

**Expérience 1:** CNN from scratch
- Architecture: 4 Conv layers + 2 Dense layers
- Résultat: 76% accuracy (insuffisant)

**Expérience 2:** Transfer Learning ResNet50
- Modèle pré-entraîné sur ImageNet
- Fine-tuning des 20 dernières couches
- Résultat: 89% accuracy (presque l'objectif)

**Expérience 3:** Data Augmentation intensive
- Rotation ±30°, zoom ±20%, horizontal flip
- Résultat: 92% accuracy ✓ (objectif atteint)

**Expérience 4:** Ensemble Learning
- Combinaison ResNet50 + InceptionV3 + EfficientNet
- Vote majoritaire pondéré
- Résultat: 94% accuracy (meilleur modèle)

**Expérience 5:** Optimisation de l'inférence
- Quantization int8
- ONNX Runtime
- Résultat: 50ms par image ✓ (objectif dépassé)

### Phase 3: Déploiement (3 semaines)
- Conteneurisation avec Docker
- API FastAPI avec endpoints /predict et /batch_predict
- Hébergement sur AWS EC2 avec auto-scaling
- Monitoring avec Prometheus et Grafana

## 4. Résultats détaillés

### Métriques finales
| Métrique | Valeur |
|----------|---------|
| Accuracy globale | 94.2% |
| Précision (classe maligne) | 96.1% |
| Rappel (classe maligne) | 93.8% |
| F1-Score | 94.9% |
| Temps d'inférence moyen | 50ms |
| Throughput | 20 images/seconde |

### Matrice de confusion
- True Negatives: 4,234
- False Positives: 87
- False Negatives: 143
- True Positives: 3,536

### Performance en production
- 10,000 images traitées par jour
- Disponibilité: 99.8%
- Coût AWS: 150€/mois

## 5. Technologies utilisées

### Stack technique
- **ML/DL:** Python 3.10, TensorFlow 2.13, Keras
- **Data:** NumPy, Pandas, Scikit-learn
- **Visualisation:** Matplotlib, Seaborn, TensorBoard
- **Déploiement:** Docker, FastAPI, Uvicorn
- **Cloud:** AWS EC2, S3, CloudWatch
- **MLOps:** MLflow pour tracking des expériences

## 6. Défis et solutions

### Défi 1: Dataset déséquilibré
Problème: 60% classe normale, 30% bénigne, 10% maligne
Solution: Class weighting + SMOTE pour over-sampling de la classe minoritaire

### Défi 2: Overfitting
Problème: 98% accuracy sur train, 85% sur validation
Solution: Dropout 0.5, L2 regularization, early stopping

### Défi 3: Temps d'inférence trop long
Problème: 200ms par image (objectif: <100ms)
Solution: Model quantization + ONNX conversion → 50ms

## 7. Conclusions et perspectives

### Acquis techniques
- Maîtrise du transfer learning et fine-tuning
- Compétences en déploiement MLOps
- Expérience avec cloud AWS
- Méthodologie scientifique rigoureuse

### Impact business
Le modèle est maintenant utilisé par 3 hôpitaux partenaires et a analysé plus de 50,000 images avec succès. Les médecins rapportent un gain de temps de 40% dans leurs diagnostics préliminaires.

### Améliorations futures
- Intégration de modèles plus récents (Vision Transformers)
- Explainability avec Grad-CAM pour visualiser les zones d'attention
- Extension à d'autres types d'images médicales