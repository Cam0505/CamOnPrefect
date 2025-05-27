# CamOnPrefect

This project orchestrates data extraction from the CocktailDB API using **Prefect**, transforms it with **DBT**, and stores it in a MotherDuck Data Warehouse. It serves as a learning platform for integrating data engineering tools like Prefect, dbt, and DLT.


## 📁 Project Structure
**.devcontainer/**: Configuration for VS Code's Remote - Containers extension.
**pipelines/**: Contains Prefect flows and tasks for data orchestration.
**dbt/**: Houses dbt models and configurations for data transformation.
**requirements.txt**: Lists Python dependencies.

## 🧱 Project Structure

<details>

<summary><strong>📁 (click to expand)</strong></summary>

```text
CamOnPrefect/
├── dbt/                          # dbt models and configs
│   ├── models/                   # dbt models
│   ├── macros/                   # Custom macros
│   ├── dbt_project.yml           # dbt project configuration
│   └── profiles.yml              # dbt profile (excluded from git)
├── .devcontainer/                # Dev container setup
│   ├── docker-compose.yml        # Project docker-compose file
│   ├── Dockerfile                # Project Dockerfile
│   ├── Init_prefect.sh           # Load Env Variables, Setup Prefect Profile, Login to Prefect Cloud on startup
│   └── devcontainer.json         # Project Dev Container
├── pipelines/
│   ├── .dlt                      # Dlt State, Secrets, Config and pipeline dataset config
│   └── *.py                      # Prefect Flows
├── .github/workflows/            # GitHub Actions CI workflows
│   ├── docs.yml                  # Auto Generate DBT Docs
│   └── ci.yml                    # Automatic CI, builds when changes occur to dbt
├── helper_functions.py           # Helper Functions, need to expand this
├── path_config.py                # Path Directory finder, reusable across scripts, probably add this into helper functions
├── Docker                        # Additional Docker File for Building and Passing a Docker Image to Prefect Cloud in the future
├── entrypoint.sh                 # Troubleshooting Docker Image
├── Prefect.yml                   # Deployment Information for Prefect, Plenty of Improvements to make here if I change to Prefect-Docker workpools.
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

</details>



## 🚀 Features
**Prefect Flows**: Automates data extraction and loading processes.
**DLT Integration**: Facilitates seamless data loading into DuckDB.
**dbt Models**: Transforms raw data into structured formats for analysis.
**File-Based Caching**: Reduces redundant API calls by caching responses.


## Prerequisites

To run this project locally, you will need the following:

- [Docker](https://www.docker.com/) - For containerization of the project
- [VS Code](https://code.visualstudio.com/) with the Remote - Containers extension (optional, but recommended)
- [Prefect](https://www.prefect.io/) - For orchestrating data workflows
- [DBT](https://www.getdbt.com/) - For data transformations
- [DLT](https://dlthub.com/) - For Data Extraction and Loading

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Cam0505/CamOnPrefect.git
cd CamOnPrefect
