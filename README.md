# kubernetes-project

## Description
This project walks you through converting Docker Compose applications into Kubernetes deployments, deploying them on a Minikube cluster, and setting up a CI/CD pipeline with Jenkins. The project includes several tasks that progressively build a Kubernetes infrastructure with resource management, scaling, and Helm integration. Additionally, it introduces ArgoCD for Kubernetes deployments in a CI/CD pipeline.

## Prerequisites
* Docker and Docker Compose
* Minikube
* Kubernetes CLI (kubectl)
* Jenkins
* ArgoCD
* Helm

## Task 1: Convert Docker Compose to Kubernetes Deployments
Convert the Python application and static website from Docker Compose to Kubernetes deployments.

Create Deployment YAML files:
nginx-deployment.yaml
app-deployment.yaml

Pull the necessary images from a private container registry.

Verify the deployment:
kubectl apply -f nginx-deployment.yaml
kubectl apply -f app-deployment.yaml

## Task 2: Deploy Applications in Minikube
Deploy the application in a namespace within the Minikube cluster.

Create the Namespace:
kubectl create namespace demo_app

Deploy the Applications:
kubectl apply -f nginx-deployment.yaml -n demo_app
kubectl apply -f app-deployment.yaml -n demo_app

Verify the Deployments:
kubectl get deployments -n demo_app
kubectl get pods -n demo_app

## Task 3: Create a Service for the Static Website
Create a Service of type ClusterIP for the Nginx static website.

Create the Service YAML:
nginx-service.yaml

Deploy the Service:
kubectl apply -f nginx-service.yaml -n demo_app

Verify the Service:
kubectl get services -n demo_app

## Task 4: Create an Ingress Resource
Create an Ingress resource to expose the Nginx static website externally.

Create the Ingress YAML:
nginx-ingress.yaml

Deploy the Ingress:
kubectl apply -f nginx-ingress.yaml -n demo_app

Test Access: 
Use curl to test if the service is accessible through the Ingress.

## Task 5: Configure Resource Restrictions & Probes
Configure resource limits for CPU and memory, and set up Liveness and Readiness probes for the deployments.

Update nginx-deployment.yaml to include:
CPU and memory limits
Liveness and Readiness probes

Apply the Updates:
kubectl apply -f nginx-deployment.yaml -n demo_app

Verify Resource Limits and Probes:
kubectl describe pod <nginx_pod_name> -n demo_app

## Task 6: Set Up Horizontal Pod Autoscaler (HPA)
Set up HPA to scale the deployments based on CPU utilization.

Create the HPA YAML for Nginx.
Deploy the HPA:
kubectl apply -f nginx-hpa.yaml -n demo_app

Verify the HPA:
kubectl get hpa -n demo_app

## Task 7: Set Up Persistent Volume Claim (PVC)
Create a PVC for the Nginx web server to store data persistently.

Create the PVC YAML:
nginx-pvc.yaml
Update nginx-deployment.yaml to mount the PVC.

Deploy the Updates:
kubectl apply -f nginx-deployment.yaml -n demo_app

Verify the Volume:
kubectl exec -it <nginx_pod_name> -- ls /usr/share/nginx/html

## Task 8: Convert to Helm Charts
Convert the Kubernetes templates to a Helm chart for easy management.

Create the Helm Chart Structure:
mkdir my-python-app-chart
cd my-python-app-chart
touch Chart.yaml values.yaml
mkdir templates
Move the Deployment YAMLs to the Templates Directory.

Install the Helm Chart:
helm install my-python-app ./my-python-app-chart

## CI/CD with Jenkins and Kubernetes

### Task 1: Set Up Jenkins Kubernetes Cloud
Configure Jenkins to connect to the Minikube cluster using a Kubernetes service account.
Install the Jenkins Kubernetes plugin and create a role binding for Jenkins.

### Task 2: Create a Jenkins Pipeline
Modify the Jenkinsfile to use the Kubernetes namespace for agents.
Automate deployment using the YAML files created earlier.
Set up a rolling deployment strategy for zero downtime.

## Bonus Task: ArgoCD Integration
Install and configure ArgoCD for managing Kubernetes deployments through GitOps.

Install ArgoCD on Minikube.

Define ArgoCD Applications for Nginx and the Python app.

Integrate ArgoCD with Jenkins:

Use the ArgoCD CLI in the Jenkins pipeline to automate deployments.
Test the Integration by making changes to the application and observing the automated deployment via ArgoCD.

