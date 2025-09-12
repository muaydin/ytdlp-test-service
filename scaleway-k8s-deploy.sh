#!/bin/bash

# Scaleway Kubernetes Deployment Script for yt-dlp Test Service
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

create_k8s_cluster() {
    print_status "Creating Kubernetes cluster..."
    
    if scw k8s cluster get $CLUSTER_NAME region=$REGION >/dev/null 2>&1; then
        print_warning "Cluster $CLUSTER_NAME already exists. Skipping creation."
        return 0
    fi
    
    scw k8s cluster create \
        name=$CLUSTER_NAME \
        version=1.30.14 \
        region=$REGION \
        cni=cilium \
        description="Kubernetes cluster for yt-dlp test service"
    
    print_status "Waiting for cluster to be ready..."
    scw k8s cluster wait $CLUSTER_NAME region=$REGION
    
    print_success "Kubernetes cluster created successfully!"
}

create_node_pool() {
    print_status "Creating node pool..."
    
    CLUSTER_ID=$(scw k8s cluster get $CLUSTER_NAME region=$REGION --output=json | jq -r '.id')
    
    if scw k8s pool get $CLUSTER_NAME-pool cluster-id=$CLUSTER_ID region=$REGION >/dev/null 2>&1; then
        print_warning "Node pool already exists. Skipping creation."
        return 0
    fi
    
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
    
    scw k8s kubeconfig get $CLUSTER_NAME region=$REGION > kubeconfig.yaml
    
    export KUBECONFIG=$(pwd)/kubeconfig.yaml
    
    kubectl get nodes
    
    print_success "kubectl configured successfully!"
}

deploy_application() {
    print_status "Deploying application to Kubernetes..."
    
    # Get registry endpoint for the deployment
    REGISTRY_ID=$(scw registry namespace list region=$REGION --output=json | jq -r '.[] | select(.name=="'$REGISTRY_NAME'") | .id')
    REGISTRY_ENDPOINT=$(scw registry namespace get $REGISTRY_ID region=$REGION --output=json | jq -r '.endpoint')
    
    print_status "Using image: $REGISTRY_ENDPOINT/$APP_NAME:$IMAGE_TAG"
    
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
    print_status "Starting Scaleway Kubernetes deployment for $APP_NAME..."
    
    check_prerequisites
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
