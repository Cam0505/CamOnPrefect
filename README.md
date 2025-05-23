# CamOnPrefect

This project orchestrates data extraction from the CocktailDB API using **Prefect**, transforms it with **DBT**, and stores it in a MotherDuck Data Warehouse. It serves as a learning platform for integrating data engineering tools like Prefect, dbt, and DLT.


## 📁 Project Structure
**.devcontainer/**: Configuration for VS Code's Remote - Containers extension.
**pipelines/**: Contains Prefect flows and tasks for data orchestration.
**dbt/**: Houses dbt models and configurations for data transformation.
**requirements.txt**: Lists Python dependencies.

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