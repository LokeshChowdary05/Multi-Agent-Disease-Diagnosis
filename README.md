# 🩺 Multi-Agent Disease Diagnosis

A modular Python framework for simulating collaborative disease diagnosis using multiple intelligent agents. This project demonstrates how AI-driven agents can discuss, analyze, and generate comprehensive medical reports from patient data.

---

## Features

- **Multi-Agent Collaboration:** Simulates discussion among AI agents to improve diagnostic accuracy.
- **Orchestrated Workflow:** Central orchestrator coordinates agent interactions and report generation.
- **Automated Report Generation:** Produces detailed medical summaries and PDF reports.
- **Extensible Design:** Easily add or customize agents and data sources.
- **Docker Support:** Containerized setup for reproducibility and deployment.

---

## Quick Start

**Requirements**
- Python 3.8+
- (Optional) Docker

**Installation**
-- git clone https://github.com/LokeshChowdary05/Multi-Agent-Disease-Diagnosis.git

--cd Multi-Agent-Disease-Diagnosis

--python -m venv venv

Activate (Windows)
 - venv\Scripts\activate

Activate (macOS/Linux)
 - source venv/bin/activate
 - 
 - pip install -r requirements.txt


**Run the Application**

- python run app.py


---

## Project Structure

Multi-Agent-Disease-Diagnosis/

├── agents.py                    # Agent definitions and logic

├── orchestrator.py              # Manages agent workflow

├── medical_data.py              # Handles patient data

├── pdf_generator.py             # Generates PDF reports

├── app.py                       # Main entry point

├── requirements.txt             # Python dependencies

├── docker-compose.yml           # Docker orchestration

├── Dockerfile                   # Docker image setup

├── instructions.txt             # Usage instructions

├── *.pdf                        # Example output reports


---

## Usage
- Run the app to simulate agent discussion and generate a diagnosis report.
- Generated reports will be saved as PDF files in the project directory.
- The Project Primarily shows how agents work for the Case of Medical Diagnosis in real-time environment.

---

## License

This project is licensed under the MIT License.

---

Feel Free to email : lokeshchowdary.pl@gmail.com
