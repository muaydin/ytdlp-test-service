#!/bin/bash

# Scaleway Deployment Script for yt-dlp Test Service
set -e

# Configuration
APP_NAME="ytdlp-test"
REGION="fr-par"
REGISTRY_NAME="ytdlp-registry"
CLUSTER_NAME="ytdlp-cluster"
NAMESPACE="ytdlp-namespace"
IMAGE_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists scw; then
        print_error "Scaleway CLI (scw) is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists kubectl; then
        print_warning "kubectl is not installed. Installing kubectl..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install kubectl
        else
            print_error "Please install kubectl manually for your OS."
            exit 1
        fi
    fi
    
    print_success "All prerequisites are met!"
}

create_registry() {
    print_status "Creating container registry..."
    
    # Check if registry already exists by listing namespaces
    if scw registry namespace list region=$REGION --output=json | jq -r '.[] | select(.name=="'$REGISTRY_NAME'") | .id' | grep -q .; then
        print_warning "Registry $REGISTRY_NAME already exists. Skipping creation."
        return 0
    fi
    
    scw registry namespace create \
        name=$REGISTRY_NAME \
        region=$REGION \
        description="Container registry for yt-dlp test service"
    
    print_success "Container registry created successfully!"
}

build_and_push_image() {
    print_status "Building and pushing Docker image..."
    
    # Get registry ID and endpoint
    REGISTRY_ID=$(scw registry namespace list region=$REGION --output=json | jq -r '.[] | select(.name=="'$REGISTRY_NAME'") | .id')
    REGISTRY_ENDPOINT=$(scw registry namespace get $REGISTRY_ID region=$REGION --output=json | jq -r '.endpoint')
    
    if [ -z "$REGISTRY_ENDPOINT" ]; then
        print_error "Failed to get registry endpoint. Make sure the registry exists."
        exit 1
    fi
    
    print_status "Building Docker image..."
    docker build -t $APP_NAME:$IMAGE_TAG .
    
    docker tag $APP_NAME:$IMAGE_TAG $REGISTRY_ENDPOINT/$APP_NAME:$IMAGE_TAG
    
    print_status "Logging into Scaleway Container Registry..."
    scw registry login region=$REGION
    
    print_status "Pushing image to registry..."
    docker push $REGISTRY_ENDPOINT/$APP_NAME:$IMAGE_TAG
    
    print_success "Image pushed successfully!"
    echo "Image: $REGISTRY_ENDPOINT/$APP_NAME:$IMAGE_TAG"
}

create_k8s_cluster() {
    print_status "Checking Kubernetes cluster..."
    
    # Check if cluster exists and get its status
    CLUSTER_STATUS=$(scw k8s cluster list --output=json | jq -r ".[] | select(.name==\"$CLUSTER_NAME\") | .status" 2>/dev/null)
    
    if [ "$CLUSTER_STATUS" = "ready" ]; then
        print_success "Cluster $CLUSTER_NAME already exists and is ready!"
        return 0
    elif [ "$CLUSTER_STATUS" = "creating" ] || [ "$CLUSTER_STATUS" = "upgrading" ]; then
        print_status "Cluster $CLUSTER_NAME is $CLUSTER_STATUS. Waiting for it to be ready..."
        scw k8s cluster wait $CLUSTER_NAME region=$REGION
        print_success "Cluster is now ready!"
        return 0
    elif [ -n "$CLUSTER_STATUS" ]; then
        print_warning "Cluster $CLUSTER_NAME exists but status is: $CLUSTER_STATUS"
        print_status "Waiting for cluster to be ready..."
        scw k8s cluster wait $CLUSTER_NAME region=$REGION
        return 0
    fi
    
    print_status "Creating new Kubernetes cluster..."
    scw k8s cluster create \
        name=$CLUSTER_NAME \
        version=1.31.12 \
        region=$REGION \
        cni=cilium \
        description="Kubernetes cluster for yt-dlp test service"
    
    print_status "Waiting for cluster to be ready..."
    scw k8s cluster wait $CLUSTER_NAME region=$REGION
    
    print_success "Kubernetes cluster created successfully!"
}

create_node_pool() {
    print_status "Checking node pool..."
    
    CLUSTER_ID=$(scw k8s cluster list --output=json | jq -r ".[] | select(.name==\"$CLUSTER_NAME\") | .id")
    
    if [ -z "$CLUSTER_ID" ]; then
        print_error "Could not find cluster ID for $CLUSTER_NAME"
        return 1
    fi
    
    # Check if node pool already exists
    POOL_COUNT=$(scw k8s pool list cluster-id=$CLUSTER_ID region=$REGION --output=json | jq '. | length')
    
    if [ "$POOL_COUNT" -gt 0 ]; then
        print_success "Node pool already exists for cluster $CLUSTER_NAME!"
        return 0
    fi
    
    print_status "Creating node pool..."
    
    scw k8s pool create \
        cluster-id=$CLUSTER_ID \
        name="$CLUSTER_NAME-pool" \
        node-type=DEV1-M \
        size=1 \
        region=$REGION \
        autohealing=true \
        autoscaling=true \
        min-size=1 \
        max-size=3
    
    print_status "Waiting for node pool to be ready..."
    scw k8s pool wait $CLUSTER_NAME-pool cluster-id=$CLUSTER_ID region=$REGION
    
    print_success "Node pool created successfully!"
}

configure_kubectl() {
    print_status "Configuring kubectl..."
    
    CLUSTER_ID=$(scw k8s cluster list --output=json | jq -r ".[] | select(.name==\"$CLUSTER_NAME\") | .id")
    
    if [ -z "$CLUSTER_ID" ]; then
        print_error "Could not find cluster ID for $CLUSTER_NAME"
        return 1
    fi
    
    scw k8s kubeconfig get $CLUSTER_ID region=$REGION > kubeconfig.yaml
    
    export KUBECONFIG=$(pwd)/kubeconfig.yaml
    
    kubectl get nodes
    
    print_success "kubectl configured successfully!"
}

deploy_application() {
    print_status "Deploying application to Kubernetes..."
    
    # Get registry endpoint for the deployment
    REGISTRY_ID=$(scw registry namespace list region=$REGION --output=json | jq -r '.[] | select(.name=="'$REGISTRY_NAME'") | .id')
    REGISTRY_ENDPOINT=$(scw registry namespace get $REGISTRY_ID region=$REGION --output=json | jq -r '.endpoint')
    
    # Update deployment.yaml with correct image
    sed "s|rg.fr-par.scw.cloud/ytdlp-registry/ytdlp-test:latest|$REGISTRY_ENDPOINT/$APP_NAME:$IMAGE_TAG|g" k8s/deployment.yaml > k8s/deployment-updated.yaml
    
    # Apply namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply deployment
    kubectl apply -f k8s/deployment-updated.yaml
    
    # Apply service
    kubectl apply -f k8s/service.yaml
    
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/$APP_NAME -n $NAMESPACE
    
    print_success "Application deployed successfully!"
}

get_service_url() {
    print_status "Getting service URL..."
    
    kubectl wait --for=condition=ready --timeout=300s service/$APP_NAME-service -n $NAMESPACE
    
    EXTERNAL_IP=$(kubectl get service $APP_NAME-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$EXTERNAL_IP" ]; then
        print_warning "External IP not yet assigned. You can check with: kubectl get service $APP_NAME-service -n $NAMESPACE"
    else
        print_success "Service is available at: http://$EXTERNAL_IP"
        echo "You can test the service with: curl http://$EXTERNAL_IP/health"
    fi
}

cleanup() {
    print_status "Cleaning up temporary files..."
    rm -f kubeconfig.yaml k8s/deployment-updated.yaml
}

main() {
    print_status "Starting Scaleway deployment for $APP_NAME..."
    
    check_prerequisites
    create_registry
    build_and_push_image
    create_k8s_cluster
    create_node_pool
    configure_kubectl
    deploy_application
    get_service_url
    
    print_success "Deployment completed successfully!"
    print_status "To check the status of your deployment:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl get services -n $NAMESPACE"
    echo "  kubectl logs -f deployment/$APP_NAME -n $NAMESPACE"
}

trap cleanup EXIT
main "$@"
