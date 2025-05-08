# CamOnPrefect

This project is a data engineering pipeline built with **Prefect**, **Docker**, and **DBT**. It serves as an example of automating data workflows and performing data transformation tasks using modern tools.

## Project Structure

- **.devcontainer/**: Contains configuration files for working within a containerized development environment using Visual Studio Code.
- **Dockerfile**: The Docker configuration used to build the project container.
- **docker-compose.yml**: Defines the services and dependencies for the project.
- **prefect/**: Prefect workflows and tasks that orchestrate data processing.
- **dbt/**: Contains DBT configurations and models for transforming data.
- **requirements.txt**: Python dependencies for the project.
- **README.md**: Project documentation.

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