# CodeNexus - A Parallel Cloud Computing and Static Analysis Tool

## Introduction

* CodeNexus is designed as a cloud-native backend system that offers parallel code compilation alongside static
code analysis. The system is modular, language-agnostic, and suitable for integration into existing competitive coding 
platforms or educational environments that require robust code evaluation engines.

## AWS Infrastructure design

### Infrastructure Overview

* This section outlines the architecture adopted on AWS to enable `parallel code compilation, execution, and static code analysis`.
* Our APIs are hosted on an `EC2 instance`, which is deployed in the `public subnet of a private VPC`. This setup ensures controlled access to resources while allowing public API access.

### Key Components and Workflow:

* FastAPI backend
    * A lightweight FastAPI server handles user submissions.
    * When a user submits code through the GUI, the frontend triggers the `/submit` endpoint of the backend.
* Job Creation and Queueing
    * The backend performs preprocessing on the submitted code and input files.
    * It generates a custom job payload and pushes it to an AWS SQS queue using the Boto3 SDK.
    * A unique `job_id` is returned to the user immediately, which can later be used to fetch results.
* Worker Service
    * A dedicated worker.py service runs continuously and polls the SQS queue for new jobs.
    * Upon receiving a job, it performs the following steps:
        * Spins up a `language-specific Docker container` to compile and execute the code.
        * Launches another `Docker container for static code analysis`, tailored to the submitted language.
        * Captures outputs from both processes.
* Result Storage and Status Tracking
    * Execution and analysis results are uploaded to a designated S3 bucket under a unique job_id directory.
    * The job status and result metadata are updated in `DynamoDB` for quick retrieval and tracking.
    * After successful completion, the job is removed from the SQS queue.
* Result Retrieval Endpoints
    * Users can fetch their results using:
        * `/results/{jobId}` → for execution output
        * `/analysis/{jobId}` → for static code analysis output
    * Both endpoints require the `jobId` as a path parameter to retrieve corresponding data.

## Folder Structure

```sh
    ECC_project/
    ├── docker_container/
    │   ├── main.py                                 # FastAPI entry point
    │   ├── cpp/
    │   │   ├── Dockerfile.codexec                  # docker file for code execution of cpp language
    │   │   └── Dockerfile.staticanalysis           # docker file for static analysis of cpp language
    │   │   └── runner.sh                           # runner script to execute code
    │   ├── go/
    │   │   ├── Dockerfile.codexec                  # docker file for code execution of go language
    │   │   └── Dockerfile.staticanalysis           # docker file for static analysis of go language
    │   │   └── runner.sh                           # runner script to execute code
    │   ├── java/
    │   │   ├── Dockerfile.codexec                  # docker file for code execution of java language
    │   │   └── Dockerfile.staticanalysis           # docker file for static analysis of java language
    │   │   └── runner.sh                           # runner script to execute code
    │   ├── python/
    │   │   ├── Dockerfile.codexec                  # docker file for code execution of python language
    │   │   └── Dockerfile.staticanalysis           # docker file for static analysis of python language
    │   │   └── runner.sh                           # runner script to execute code
    ├── constants.py                                # File containing application specific constants
    ├── docker_executor.py                          # Spinninp up language specific code execution docker containers
    ├── dynamodb_utils.py                           # Utility operations for dynamodb database
    ├── requirements.txt                            # requirements.txt file for dependencies
    ├── s3_utils.py                                 # Utility operations for S3 bucket
    ├── static_analyzer.py                          # Spinninp up language specific static analysis docker containers
    ├── worker.py                                   # Worker script to process AWS SQS queue messages
```

## How to Setup

* Clone this repository.
* Create a virtual environment and activate it.
* Install necessary dependency using below command:
    ```sh
        pip install -r requirements.txt
    ```
* Generate a system level service for `FastAPI backend` and `worker.py` script as per below configuration:
    ```sh
        [Unit]
        Description=FastAPI Backend Service
        After=network.target

        [Service]
        User=<your_linux_username>
        Group=<your_linux_username>
        WorkingDirectory=/home/<your_linux_username>/ECC_project
        Environment="PATH=/home/<your_linux_username>/ECC_project/<virtual-environment-name>/bin"
        ExecStart=/home/<your_linux_username>/ECC_project/venv/bin/gunicorn -c gunicorn_conf.py app.main:app

        StandardOutput=append:/var/log/fastapi/fastapi.log
        StandardError=append:/var/log/fastapi/fastapi-error.log

        Restart=always
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
    ```

    ```sh
        [Unit]
        Description=CodeNexus Background Worker Service
        After=network.target

        [Service]
        User=<your_linux_username>
        Group=<your_linux_username>
        WorkingDirectory=/home/<your_linux_username>/ECC_project
        Environment="PATH=/home/<your_linux_username>/ECC_project/<virtual-environment-name>/bin"
        ExecStart=/home/<your_linux_username>/ECC_project/<virtual-environment-name>/bin/python worker.py

        StandardOutput=append:/var/log/fastapi/worker.log
        StandardError=append:/var/log/fastapi/worker-error.log

        Restart=always
        RestartSec=5

        [Install]
        WantedBy=multi-user.target
    ```
* Reload you `systemd` deamon and restart both services using below command:
    ```sh
        sudo systemctl daemon-reload
        sudo systemctl restart fastapi.service
        sudo systemctl restart worker.service
    ```
* Now you application is live on `localhost:8000`. You can check the application health status by hitting `/health`. You should expect below type of response.
    ```sh
        {"result": "ok"}
    ```

## Colloborators

1. Dev Patel
2. Dhwanit Pandya
3. Pratham Dedhiya
4. Siddhant Singh