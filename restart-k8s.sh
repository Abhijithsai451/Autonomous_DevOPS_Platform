#!/usr/bin/env bash
set -e

NAMESPACE="cortexops-system"

echo " Cleaning up existing  deployment and PVC "
kubectl delete deployments --all -n "$NAMESPACE" --ignore-not-found --wait=true
kubectl delete pvc --all -n "$NAMESPACE" --ignore-not-found --wait=true
kubectl delete secret --all -n "$NAMESPACE" --ignore-not-found

echo " Deleting generated ConfigMaps, Avoiding system ca-bundle deletion"
kubectl delete configmap cortexops-common-config -n "$NAMESPACE" --ignore-not-found
kubectl delete configmap -l kustomize.toolkit.fluxcd.io/name -n "$NAMESPACE" --ignore-not-found 2>/dev/null || true
kubectl delete configmap -n "$NAMESPACE" -l 'app.kubernetes.io/created-by=kustomize' --ignore-not-found 2>/dev/null || true

echo " Applying Kustomize configurations from Root "
kubectl apply -k .

echo " Waiting for PostgreSQL to initialize "
kubectl rollout status deployment/infra-pgdb -n "$NAMESPACE" --timeout=60s

echo " Waiting for PostgreSQL TCP port 5432 to be Ready"
until kubectl exec -n "$NAMESPACE" deployment/infra-pgdb -- psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; do
  echo " PostgreSQL is starting up... retrying in 2 seconds"
  sleep 2
done
echo " PostgreSQL database engine is fully operational!"

echo " Restarting dependent core microservices "
kubectl rollout status deployment/cortexops-identity -n "$NAMESPACE" --timeout=20s
kubectl rollout status deployment/cortexops-organization -n "$NAMESPACE" --timeout=20s
kubectl rollout status deployment/cortexops-workflow -n "$NAMESPACE" --timeout=20s
kubectl rollout status deployment/cortexops-agent-runtime -n "$NAMESPACE" --timeout=20s

echo " Cluster Status "
kubectl get pods -n "$NAMESPACE"