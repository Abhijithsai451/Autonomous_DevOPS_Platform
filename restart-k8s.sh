#!/usr/bin/env bash
set -e

NAMESPACE="cortexops-system"

echo "1. Cleaning up existing PostgreSQL deployment and PVC "
kubectl delete deployment infra-pgdb -n "$NAMESPACE" --ignore-not-found --wait=true
kubectl delete pvc infra-pgdb-pvc -n "$NAMESPACE" --ignore-not-found --wait=true

echo " 2. Applying Kustomize configurations from Root "
kubectl apply -k .

echo " 3. Waiting for PostgreSQL to initialize "
kubectl rollout status deployment/infra-pgdb -n "$NAMESPACE" --timeout=60s

echo " 4. Restarting dependent core microservices "
kubectl rollout restart deployment -l tier=core -n "$NAMESPACE"

echo " 5. Verification: Fetching Postgres boot logs "
kubectl logs deployment/infra-pgdb -n "$NAMESPACE" --tail=50