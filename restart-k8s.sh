#!/usr/bin/env bash
set -e

NAMESPACE="cortexops-system"

echo " Cleaning up existing deployment and PVC "
kubectl delete ns "$NAMESPACE" --ignore-not-found=true --wait=true

echo "Creating fresh namespace..."
kubectl create namespace "$NAMESPACE"

echo " Deploying via Kustomize "
kubectl apply -k .

echo " Scaling Microservices Down for Database Init "
kubectl scale deployment -n "$NAMESPACE" --replicas=0 \
  cortexops-identity \
  cortexops-organization \
  cortexops-workflow \
  cortexops-agent-runtime

echo " Waiting for PostgreSQL to initialize "
kubectl rollout status deployment/infra-pgdb -n "$NAMESPACE" --timeout=60s

echo " Waiting for PostgreSQL TCP port 5432 to be Ready "
until kubectl exec -n "$NAMESPACE" deployment/infra-pgdb -- psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; do
  echo " PostgreSQL is starting up... retrying in 2 seconds"
  sleep 2
done
echo " PostgreSQL database engine is fully operational!"

echo " Scaling Microservices Up "
kubectl scale deployment -n "$NAMESPACE" --replicas=1 \
  cortexops-identity \
  cortexops-organization \
  cortexops-workflow \
  cortexops-agent-runtime

kubectl rollout status deployment/cortexops-identity -n "$NAMESPACE" --timeout=60s
kubectl rollout status deployment/cortexops-organization -n "$NAMESPACE" --timeout=60s
kubectl rollout status deployment/cortexops-workflow -n "$NAMESPACE" --timeout=60s
kubectl rollout status deployment/cortexops-agent-runtime -n "$NAMESPACE" --timeout=60s

echo " Cluster Status "
kubectl get pods -n "$NAMESPACE" -w