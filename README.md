Certainly! Below is a `README.md` file that covers the entire project, including the steps for setting up the FastAPI application, EKS cluster, and configuring GitHub Actions runners on Kubernetes.

---

# Project: FastAPI Application Deployment and Kubernetes Self-Hosted GitHub Runners Setup

## Overview

This project involves two major components:

1. **Deployment of a FastAPI application** using Nginx and Gunicorn on an Ubuntu server.
2. **Setting up a Kubernetes cluster (EKS) with self-hosted GitHub Actions runners** using the GitHub Actions Runner Controller.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [FastAPI Application Deployment](#fastapi-application-deployment)
   - [Step 1: Setting Up the Server](#step-1-setting-up-the-server)
   - [Step 2: Configuring the FastAPI Application](#step-2-configuring-the-fastapi-application)
   - [Step 3: Setting Up Nginx and Gunicorn](#step-3-setting-up-nginx-and-gunicorn)
   - [Step 4: Testing the Deployment](#step-4-testing-the-deployment)
3. [Kubernetes Self-Hosted GitHub Runners](#kubernetes-self-hosted-github-runners)
   - [Step 1: EKS Cluster Setup](#step-1-eks-cluster-setup)
   - [Step 2: Installing Required Tools](#step-2-installing-required-tools)
   - [Step 3: Installing GitHub Actions Runner Controller](#step-3-installing-github-actions-runner-controller)
   - [Step 4: Configuring GitHub Actions Runners](#step-4-configuring-github-actions-runners)
   - [Step 5: Testing the Runners](#step-5-testing-the-runners)
4. [Troubleshooting](#troubleshooting)
5. [Cleanup](#cleanup)
6. [Conclusion](#conclusion)

---

## Prerequisites

- AWS account with permissions to create and manage EKS clusters, IAM roles, and associated resources.
- Domain name (optional for FastAPI).
- Ubuntu server with `ssh` access.
- AWS CLI configured with credentials.
- Basic understanding of Kubernetes, FastAPI, and GitHub Actions.

## FastAPI Application Deployment

### Step 1: Setting Up the Server

1. **SSH into your server:**

   ```bash
   ssh ubuntu@your-server-ip
   ```

2. **Update and upgrade your server:**

   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

3. **Install Python, Pip, and Virtualenv:**

   ```bash
   sudo apt-get install python3 python3-pip python3-venv -y
   ```

### Step 2: Configuring the FastAPI Application

1. **Clone the FastAPI application repository:**

   ```bash
   git clone https://github.com/hngprojects/hng_boilerplate_python_fastapi_web.git
   cd hng_boilerplate_python_fastapi_web
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root and add the following:

   ```bash
   SECRET_KEY=your_secret_key
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=your_db_name
   DB_TYPE=postgresql
   ```

### Step 3: Setting Up Nginx and Gunicorn

1. **Install Nginx and Gunicorn:**

   ```bash
   sudo apt-get install nginx -y
   pip install gunicorn
   ```

2. **Configure Gunicorn:**

   Create a Gunicorn systemd service file at `/etc/systemd/system/gunicorn.service`:

   ```bash
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/hng_boilerplate_python_fastapi_web
   ExecStart=/home/ubuntu/hng_boilerplate_python_fastapi_web/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/hng_boilerplate_python_fastapi_web/fastapi.sock main:app

   [Install]
   WantedBy=multi-user.target
   ```

   Start and enable Gunicorn:

   ```bash
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

3. **Configure Nginx:**

   Remove the default Nginx configuration and create a new one at `/etc/nginx/sites-available/fastapi`:

   ```bash
   server {
       listen 80;
       server_name your_domain_or_ip;

       location / {
           proxy_pass http://unix:/home/ubuntu/hng_boilerplate_python_fastapi_web/fastapi.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Enable the configuration and restart Nginx:

   ```bash
   sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   ```

### Step 4: Testing the Deployment

1. **Check the status of Gunicorn and Nginx:**

   ```bash
   sudo systemctl status gunicorn
   sudo systemctl status nginx
   ```

2. **Access the application:**

   Open a web browser and navigate to `http://your_domain_or_ip`.

## Kubernetes Self-Hosted GitHub Runners

### Step 1: EKS Cluster Setup

1. **Install `eksctl`:**

   ```bash
   curl -Lo eksctl https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz
   tar -xvf eksctl_Linux_amd64.tar.gz
   sudo mv eksctl /usr/local/bin/
   ```

2. **Create the EKS Cluster:**

   ```bash
   eksctl create cluster --name github-runners-cluster --region us-east-2 --nodes 2 --managed
   ```

### Step 2: Installing Required Tools

1. **Install `kubectl`:**

   ```bash
   sudo snap install kubectl --classic
   ```

2. **Install Helm:**

   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

3. **Install `aws-iam-authenticator`:**

   Download the binary:

   ```bash
   curl -Lo aws-iam-authenticator https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.5.9/aws-iam-authenticator-linux-amd64
   chmod +x aws-iam-authenticator
   sudo mv aws-iam-authenticator /usr/local/bin/aws-iam-authenticator
   ```

### Step 3: Installing GitHub Actions Runner Controller

1. **Add the Helm chart repository and update:**

   ```bash
   helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
   helm repo update
   ```

2. **Create a namespace for the controller:**

   ```bash
   kubectl create namespace actions-runner-system
   ```

3. **Install the controller:**

   ```bash
   helm install --namespace actions-runner-system actions-runner-controller actions-runner-controller/actions-runner-controller
   ```

### Step 4: Configuring GitHub Actions Runners

1. **Create a Kubernetes Secret to store your GitHub token:**

   ```bash
   kubectl create secret generic controller-manager -n actions-runner-system --from-literal=github_token=<your_github_token>
   ```

2. **Deploy the runners:**

   Create a `runner.yaml` with the following content:

   ```yaml
   apiVersion: actions.summerwind.dev/v1alpha1
   kind: RunnerDeployment
   metadata:
     name: example-runnerdeploy
     namespace: actions-runner-system
   spec:
     replicas: 1
     template:
       spec:
         repository: <your_github_repository>
         group: "group-name"
         labels:
           - "self-hosted"
   ```

   Apply the YAML file:

   ```bash
   kubectl apply -f runner.yaml
   ```

### Step 5: Testing the Runners

1. **Verify the deployment:**

   ```bash
   kubectl get pods -n actions-runner-system
   ```

2. **Check GitHub for registered runners.**

3. **Trigger a workflow in GitHub to test the runners.**

## Troubleshooting

- **EKS Cluster Creation Failures**: Ensure IAM roles have sufficient permissions.
- **Nginx/Gunicorn Issues**: Check Nginx and Gunicorn logs for errors.
- **AWS IAM Authenticator Errors**: Ensure the correct binary is downloaded for your architecture.

## Cleanup

To delete the EKS cluster:

```bash
eksctl delete cluster --region=us-east-2 --name=github-runners-cluster
```

## Conclusion

By following the steps outlined in this document, you

 successfully deployed a FastAPI application and set up self-hosted GitHub Actions runners on an EKS cluster. This setup ensures a scalable, production-ready environment for your applications and CI/CD pipelines.

---


