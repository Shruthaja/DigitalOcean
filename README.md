# SaaS Web Application Deployment on DigitalOcean Kubernetes (DOKS)

## 1. Create a Kubernetes Cluster in Default VPC
- Navigate to **Kubernetes** in the DigitalOcean dashboard.
- Create a **DOKS cluster** with autoscaling set between **1 and 2 nodes**.
- Choose a node pool with a suitable size (e.g., **2 vCPUs, 4GB RAM**).

## 2. Set Up a Load Balancer
- Add a **DigitalOcean Load Balancer** to distribute traffic.
- Ensure it forwards external traffic from **port 80** to your Flask app’s **port 5000**.

## 3. Build and Push Docker Image from Flask App

### 3.1 Create a Dockerfile
Inside your **Flask project root**, create a `Dockerfile`:

```dockerfile
# Use an official Python runtime as a parent image
FROM  python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run the application when the container launches
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

````

3.2 Build and Push the Docker Image
- run `pip freeze > requirements.txt`. Docker will use this as mentioned in the dockerfile to create an image.
- Authenticate with DigitalOcean Container Registry (DOCR):
  ```
  > doctl registry login
  > docker build -t <your-registry>/<your-image>:latest
  > docker push <your-registry>/<your-image>:latest
  ```
 - `<your-registry>` : url to your registry can be easily found in your Container Registry Page

## 4. Connect DOCR to Kubernetes Cluster (via UI)
- Go to Container Registry in the DigitalOcean dashboard.
- Navigate to Settings → Integrations.
- Select your DOKS cluster to allow it to pull images directly from the registry.

## 5. Deploy to Kubernetes -

### 5.1 Apply Kubernetes Manifests
`Deployment (deployment.yaml)` :

```
apiVersion: apps/v1
kind: Deployment
metadata:
name: flask-app
spec:
replicas: 1
selector:
matchLabels:
  app: flask-app
template:
metadata:
  labels:
    app: flask-app
spec:
  containers:
    - name: flask-app
      image: registry.digitalocean.com/shruthaja-container-registry/flask-app:v2
      ports:
        - containerPort: 5000
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "250m"
          memory: "256Mi"

```
`Service (service.yaml)`
```
apiVersion: v1
kind: Service
metadata:
name: flask-service
spec:
type: LoadBalancer
selector:
  app: flask
ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```
## 6. Enable Horizontal Pod Autoscaler (HPA)
`HPA Configuration (hpa.yaml)`

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flask-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask-app
  minReplicas: 1
  maxReplicas: 2
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```
Apply the HPA :


`kubectl apply -f hpa.yaml`
## 7. Install Metrics Server for HPA
### Apply metrics server manifest (metrics.yaml):

`kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
### Verify installation:

`kubectl get deployment metrics-server -n kube-system`
## 8. Verify Deployment
### Check deployments and pods:
```
kubectl get deployments
kubectl get pods
```
Check service and external IP:

`kubectl get svc flask-service`
  
  
