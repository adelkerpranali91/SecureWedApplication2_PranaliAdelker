Improving Multi-Stage Attack Detection in SIEM Systems through Cross-Layer MITRE ATT&CK Aligned Event Correlation and Analysis

Research Project | Master of Science in Cybersecurity
Student ID: 24203513
Supervisor: MARK MONAGHAN

This folder includes artefacts created during th research implementation of multi-stage attacks in Elastic Security environment. The project executes four attack tecnhiques and gathered host and network telemetry again each attack, tests the detection of these attack with set of custom detection rule. The rule further developed the cross-layer multi-stage correlation rule that correlate related event into a single security incident.

OVERVIEW
The project develops and tests detection capability for four stages of an attack technique aligned with MITRE ATT&CK.

- PERSISTENCE [T1053.003] -- Scheduled Task/Job :Cron 
- COLLECTION [T1005] -- Data from Local System
- IMPACT [T1489] -- Service Stop
- EXFILTRATION [T1020] -- Automated Exfiltration for HTTP PUT request.

Atomic Red Team was used to simulate the attacks, both the host telemetry and the network telemetry were collected and sent to Elasticsearch through the fleet to be analysed in Kibana. Custom detection rules for each individual attack stages was created by .Event Query Language correlation rules were created for Multi-stage attack detection and cross-layer telemetry correlation.

<img width="391" height="464" alt="image" src="https://github.com/user-attachments/assets/e521e0bb-995c-4fa0-8eda-042609a08a64" />


LAB ENVIRONMENT
- Windows Host -- runs the Hyper-V and is used to access Kibana over browser connection.
- Hyper-V -- virtualization layer that isolates virtual network switch. 
- Ubuntu VM -- Once installed and configured runs a full stack from Elasticsearch, Kibana, Fleet Server, ELastic Agent, auditd and Suricata on Ubuntu VM.

SOFTWARE REQUIREMENTS
- Audit [Auditd Manager Integration]
- Suricata [ Suricata integration]
- Atomic Red Team [ open-source attack simulation framework]
- Elastic Stack [various uses over Elastic Security]

TELEMETRY CONFIGURATION 
- Custom AUDITD rules were used to monitor cron, process execution and network configs.
- Suricata enabled with default configuration, ensuring JSON was enabled

DETECTION RULES
- Custom detection rules were created for each individual attack technique and aligned then to MITRE ATT&CK techniques
- Event Query Language was used to create both the multi-stage attack correaltion rule and the cross-layer multiple telemetry correlation rule.

FOLDER STRUCTURE 
ARTEFACTS/
|--AUDITD/                Custom auditd rules
|--DETECTION RULES/     Exported security detection rules
|--EVALUATION/          Scenarios executed and Metrics
|--RESULTS/             Alerts Generated
   |--screenshots
|--SIMULATIONS          Attack Commands
|--TELEMETRY            Raw telemetry for each attack
|--CONFIGURATION MANUAL  Detailed lab configuration 
