# Rapport de Stage - Audit de Sécurité Informatique

**Étudiant:** Lucas Martin  
**Entreprise:** CyberSecure Consulting  
**Durée:** 4 mois (Avril - Juillet 2024)  
**Encadrant:** M. Pierre Dubois, CISSP, Expert Sécurité

## 1. Contexte et mission

### Présentation de l'entreprise cliente
PME du secteur bancaire (200 employés) souhaitant se conformer aux normes ISO 27001 et PCI-DSS. Infrastructure mixte on-premise et cloud Azure.

### Objectifs de l'audit
1. Auditer la sécurité du système d'information complet
2. Identifier et classifier les vulnérabilités (CVSS score)
3. Proposer un plan de remédiation priorisé
4. Former l'équipe IT aux bonnes pratiques de sécurité

## 2. Périmètre de l'audit

### Infrastructure auditée
- **Réseau:** 3 sites distants connectés via VPN, 50 serveurs
- **Applications:** 15 applications web internes, 5 applications SaaS
- **Endpoints:** 200 postes de travail Windows 10/11
- **Cloud:** Azure Active Directory, Azure Storage, VM Azure

## 3. Méthodologie d'audit en 4 phases

### Phase 1: Reconnaissance passive (1 semaine)
**Objectif:** Collecte d'informations publiques sans interaction

Activités réalisées:
- OSINT (Open Source Intelligence) sur les domaines
- Recherche de fuites de données sur Have I Been Pwned
- Analyse DNS et sous-domaines (theHarvester, Sublist3r)
- Scan de métadonnées dans les documents publics (FOCA)

Résultats:
- 12 emails d'employés trouvés dans des breaches publiques
- 3 sous-domaines exposés non documentés
- Informations sensibles dans métadonnées PDF (noms utilisateurs, chemins réseau)

### Phase 2: Scan et énumération (2 semaines)
**Objectif:** Cartographie détaillée du réseau

Outils utilisés:
- **Nmap:** Scan de ports (TCP/UDP) et détection OS
- **Nessus Professional:** Scan de vulnérabilités automatisé
- **Nuclei:** Détection de CVEs avec templates personnalisés
- **Shodan:** Recherche d'assets exposés sur Internet

Découvertes:
- 23 ports ouverts inutilement (Telnet 23, FTP 21, SMB 445)
- 8 serveurs avec OS obsolètes (Windows Server 2008 R2 EOL)
- 15 services avec versions outdated et CVEs connues
- 2 bases de données MongoDB exposées sans authentification

### Phase 3: Tests de pénétration (3 semaines)
**Objectif:** Exploitation des vulnérabilités identifiées

#### Test 1: Attaque par force brute
- Outil: Hydra avec wordlist rockyou.txt
- Cible: Portail RDP exposé
- Résultat: 5 comptes compromis avec mots de passe faibles ("admin123", "Password1!")

#### Test 2: Exploitation de CVE-2021-34527 (PrintNightmare)
- Outil: Metasploit Framework
- Cible: Print Spooler non patché
- Résultat: Élévation de privilèges SYSTEM réussie sur 12 serveurs

#### Test 3: Phishing simulé
- 50 emails de test envoyés (Gophish)
- 32% de taux de clic (16 employés)
- 12% ont saisi leurs identifiants (6 employés)

#### Test 4: Analyse d'applications web (OWASP Top 10)
Outils: Burp Suite Professional, OWASP ZAP

Vulnérabilités trouvées:
- **SQL Injection** dans module de recherche (CVSS 9.8 Critical)
- **XSS réfléchi** dans 3 formulaires (CVSS 6.1 Medium)
- **Broken Authentication:** Pas de timeout de session (CVSS 7.5 High)
- **Sensitive Data Exposure:** Mots de passe en clair dans logs (CVSS 8.2 High)

### Phase 4: Analyse et rapport (2 semaines)
- Classification des vulnérabilités selon CVSS v3.1
- Rédaction du rapport exécutif et technique
- Élaboration du plan de remédiation
- Présentation aux dirigeants et équipe IT

## 4. Résultats de l'audit

### Synthèse des vulnérabilités

| Sévérité | Nombre | Exemples |
|----------|--------|----------|
| **Critique (9.0-10.0)** | 5 | SQL Injection, MongoDB sans auth |
| **Élevée (7.0-8.9)** | 12 | Broken Auth, RCE PrintNightmare |
| **Moyenne (4.0-6.9)** | 23 | XSS, CSRF, ports inutiles ouverts |
| **Faible (0.1-3.9)** | 18 | Bannering, métadonnées sensibles |

### Top 5 des vulnérabilités critiques

1. **SQL Injection dans portail client (CVSS 9.8)**
   - Impact: Accès complet à la base de données clients
   - Exploitation: Union-based SQLi avec sqlmap
   - Remédiation: Requêtes préparées (PDO/Prepared Statements)

2. **MongoDB sans authentification (CVSS 9.1)**
   - Impact: 50,000 enregistrements clients exposés
   - Exploitation: Connexion directe depuis Internet
   - Remédiation: Enable auth + firewall rules

3. **PrintNightmare RCE (CVE-2021-34527) (CVSS 8.8)**
   - Impact: 12 serveurs compromissables
   - Exploitation: Metasploit module exploit/windows/dcerpc/cve_2021_34527
   - Remédiation: Patch KB5005010 + désactiver Print Spooler

4. **Mots de passe faibles (CVSS 8.5)**
   - Impact: 15% des comptes avec passwords < 8 caractères
   - Exploitation: Brute force avec Hydra (5 min)
   - Remédiation: Politique de mots de passe forte (12+ chars, complexité)

5. **Absence de MFA (CVSS 8.0)**
   - Impact: Single point of failure sur authentification
   - Exploitation: Phishing réussi sur 6 employés
   - Remédiation: Déploiement Azure MFA pour tous les utilisateurs

## 5. Plan de remédiation proposé

### Court terme (0-1 mois) - Urgence maximale
- **Semaine 1:**
  - Correction SQL Injection (patch d'urgence)
  - Activation authentification MongoDB
  - Désactivation ports inutiles (Telnet, FTP)

- **Semaine 2-4:**
  - Déploiement patches PrintNightmare
  - Mise en place politique mots de passe forte
  - Activation MFA pour comptes administrateurs

### Moyen terme (1-3 mois)
- Migration serveurs Windows 2008 vers 2022
- Déploiement WAF (Web Application Firewall)
- Formation cybersécurité pour tous les employés
- Mise en place SIEM (Security Information and Event Management)

### Long terme (3-6 mois)
- Certification ISO 27001
- Programme de bug bounty interne
- Red Team exercises trimestriels
- Conformité complète PCI-DSS

## 6. Outils et technologies utilisés

### Reconnaissance et OSINT
- theHarvester, Shodan, Censys, FOCA, SpiderFoot

### Scan de vulnérabilités
- Nmap, Nessus Professional, OpenVAS, Nuclei

### Exploitation
- Metasploit Framework, sqlmap, Hydra, John the Ripper

### Web Application Testing
- Burp Suite Professional, OWASP ZAP, Nikto

### Social Engineering
- Gophish (phishing simulation), SET (Social-Engineer Toolkit)

### Analyse réseau
- Wireshark, tcpdump, Zeek (Bro)

## 7. Compétences développées

### Techniques
- Maîtrise des outils de pentesting professionnel
- Méthodologie d'audit structurée (OWASP, NIST)
- Compréhension approfondie des protocoles réseau
- Exploitation de vulnérabilités réelles

### Soft skills
- Communication avec direction non-technique
- Rédaction de rapports clairs et actionnables
- Gestion de la confidentialité des données sensibles
- Éthique en cybersécurité

## 8. Conclusions et impact

### Résultats quantitatifs
- **40 vulnérabilités identifiées** (5 critiques, 12 élevées)
- **Plan de remédiation sur 6 mois** avec budget estimé 80,000€
- **Formation de 15 personnes** aux bonnes pratiques

### Impact pour le client
L'audit a révélé des failles majeures qui auraient pu causer:
- Une fuite de 50,000 données clients (amende RGPD potentielle: 4% CA)
- Un arrêt d'activité de plusieurs jours en cas de ransomware
- Une perte de confiance et atteinte réputationnelle

La mise en œuvre du plan de remédiation réduira le risque cyber de 85% selon notre matrice d'évaluation.

### Perspectives professionnelles
Suite à ce stage, j'ai obtenu mes certifications CEH (Certified Ethical Hacker) et OSCP (Offensive Security Certified Professional). CyberSecure Consulting m'a proposé un CDI comme Pentester Junior.