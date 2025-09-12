# Scaleway Deployment Guide for yt-dlp Test Service

This guide will help you deploy your Flask application to Scaleway using Container Registry and Kubernetes.

## Prerequisites

1. **Scaleway CLI**: Already installed and configured ✅
2. **Docker**: For building and pushing images
3. **kubectl**: For Kubernetes management (will be installed automatically)

## Step-by-Step Deployment

### 1. Verify Scaleway Configuration

```bash
# Check your current configuration
scw config get default-region
scw config get default-project-id
```

### 2. Run the Deployment Script

The deployment script will automatically:
- Create a container registry
- Build and push your Docker image
- Create a Kubernetes cluster
- Deploy your application

```bash
# Make the script executable (already done)
chmod +x scaleway-deploy.sh

# Run the deployment
./scaleway-deploy.sh
```

### 3. Manual Steps (Alternative)

If you prefer to run commands manually:

#### Create Container Registry
```bash
scw registry namespace create \
    --name=ytdlp-registry \
    --region=fr-par \
    --description="Container registry for yt-dlp test service"
```

#### Build and Push Image
```bash
# Get registry endpoint
REGISTRY_ENDPOINT=$(scw registry namespace get ytdlp-registry --region=fr-par --output=json | jq -r '.endpoint')

# Build image
docker build -t ytdlp-test:latest .

# Tag for registry
docker tag ytdlp-test:latest $REGISTRY_ENDPOINT/ytdlp-test:latest

# Login to registry
scw registry login --region=fr-par

# Push image
docker push $REGISTRY_ENDPOINT/ytdlp-test:latest
```

#### Create Kubernetes Cluster
```bash
scw k8s cluster create \
    --name=ytdlp-cluster \
    --version=1.28 \
    --region=fr-par \
    --cni=cilium \
    --description="Kubernetes cluster for yt-dlp test service"

# Wait for cluster to be ready
scw k8s cluster wait ytdlp-cluster --region=fr-par
```

#### Create Node Pool
```bash
# Get cluster ID
CLUSTER_ID=$(scw k8s cluster get ytdlp-cluster --region=fr-par --output=json | jq -r '.id')

# Create node pool
scw k8s pool create \
    --cluster-id=$CLUSTER_ID \
    --name="ytdlp-cluster-pool" \
    --node-type=DEV1-M \
    --size=1 \
    --region=fr-par \
    --autohealing=true \
    --autoscaling=true \
    --min-size=1 \
    --max-size=3

# Wait for node pool to be ready
scw k8s pool wait ytdlp-cluster-pool --cluster-id=$CLUSTER_ID --region=fr-par
```

#### Configure kubectl
```bash
# Get kubeconfig
scw k8s kubeconfig get ytdlp-cluster --region=fr-par > kubeconfig.yaml

# Set KUBECONFIG environment variable
export KUBECONFIG=$(pwd)/kubeconfig.yaml

# Test connection
kubectl get nodes
```

#### Deploy Application
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/ytdlp-test -n ytdlp-namespace
```

## Monitoring Your Deployment

### Check Deployment Status
```bash
# Check pods
kubectl get pods -n ytdlp-namespace

# Check services
kubectl get services -n ytdlp-namespace

# Check logs
kubectl logs -f deployment/ytdlp-test -n ytdlp-namespace
```

### Get Service URL
```bash
# Get external IP
kubectl get service ytdlp-test-service -n ytdlp-namespace

# Test the service
curl http://<EXTERNAL_IP>/health
```

## Cost Optimization

### Node Pool Configuration
- **Node Type**: DEV1-M (1 vCPU, 2GB RAM) - Cost-effective for development
- **Auto-scaling**: Enabled (1-3 nodes)
- **Auto-healing**: Enabled

### Resource Limits
- **Memory**: 256Mi request, 512Mi limit
- **CPU**: 250m request, 500m limit

## Troubleshooting

### Common Issues

1. **Registry Login Issues**
   ```bash
   scw registry login --region=fr-par
   ```

2. **Cluster Not Ready**
   ```bash
   scw k8s cluster wait ytdlp-cluster --region=fr-par
   ```

3. **Pod Not Starting**
   ```bash
   kubectl describe pod <pod-name> -n ytdlp-namespace
   kubectl logs <pod-name> -n ytdlp-namespace
   ```

4. **Service Not Accessible**
   ```bash
   kubectl get service ytdlp-test-service -n ytdlp-namespace
   kubectl get endpoints ytdlp-test-service -n ytdlp-namespace
   ```

### Cleanup Commands

If you need to clean up resources:

```bash
# Delete Kubernetes resources
kubectl delete -f k8s/

# Delete cluster
scw k8s cluster delete ytdlp-cluster --region=fr-par

# Delete registry
scw registry namespace delete ytdlp-registry --region=fr-par
```

## Security Notes

1. **API Keys**: Your API keys are stored in `~/.config/scw/config.yaml`
2. **Kubeconfig**: The kubeconfig file contains sensitive information
3. **Container Registry**: Images are private by default
4. **Load Balancer**: External IP is assigned automatically

## Next Steps

After successful deployment:

1. **Custom Domain**: Configure a custom domain with Scaleway DNS
2. **SSL Certificate**: Add SSL/TLS certificate for HTTPS
3. **Monitoring**: Set up monitoring and alerting
4. **Backup**: Configure backup strategies
5. **CI/CD**: Set up automated deployments

## Support

- **Scaleway Documentation**: https://www.scaleway.com/en/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Docker Documentation**: https://docs.docker.com/
