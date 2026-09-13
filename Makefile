# ==============================================================================
# CORTEXOPS PLATFORM MANAGEMENT MAKEFILE
# ==============================================================================

.PHONY: help helm-lint helm-template-dev helm-template-prod helm-install-dev helm-upgrade-dev helm-install-prod helm-upgrade-prod helm-uninstall k8s-status docker-up docker-down

# Configuration Variables
SHELL := /bin/bash
CHART_DIR := infrastructure/helm/cortexops
RELEASE_NAME := cortexops
NAMESPACE := cortexops-system

help:
	@echo "CortexOps Platform Control CLI"
	@echo "----------------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ==============================================================================
# HELM LINT & DRY-RUN TEMPLATING
# ==============================================================================

helm-lint:
	@echo "==> Linting Helm chart at $(CHART_DIR)..."
	helm lint $(CHART_DIR)

helm-template-dev:
	@echo "==> Rendering DEV environment manifests..."
	helm template $(RELEASE_NAME) $(CHART_DIR) -f $(CHART_DIR)/values-dev.yaml

helm-template-prod:
	@echo "==> Rendering PROD environment manifests..."
	helm template $(RELEASE_NAME) $(CHART_DIR) -f $(CHART_DIR)/values-prod.yaml

# ==============================================================================
# KUBERNETES DEPLOYMENTS
# ==============================================================================

k8s-init-namespace:
	@kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

helm-install-dev: k8s-init-namespace
	@echo "==> Deploying CortexOps to DEV environment..."
	helm install $(RELEASE_NAME) $(CHART_DIR) \
		--namespace $(NAMESPACE) \
		-f $(CHART_DIR)/values.yaml \
		-f $(CHART_DIR)/values-dev.yaml

helm-upgrade-dev: k8s-init-namespace
	@echo "==> Upgrading CortexOps in DEV environment..."
	helm upgrade $(RELEASE_NAME) $(CHART_DIR) \
		--namespace $(NAMESPACE) \
		-f $(CHART_DIR)/values.yaml \
		-f $(CHART_DIR)/values-dev.yaml \
		--atomic --timeout 5m0s

helm-install-prod: k8s-init-namespace
	@echo "==> Deploying CortexOps to PROD environment..."
	helm install $(RELEASE_NAME) $(CHART_DIR) \
		--namespace $(NAMESPACE) \
		-f $(CHART_DIR)/values.yaml \
		-f $(CHART_DIR)/values-prod.yaml

helm-upgrade-prod: k8s-init-namespace
	@echo "==> Upgrading CortexOps in PROD environment..."
	helm upgrade $(RELEASE_NAME) $(CHART_DIR) \
		--namespace $(NAMESPACE) \
		-f $(CHART_DIR)/values.yaml \
		-f $(CHART_DIR)/values-prod.yaml \
		--atomic --timeout 10m0s

helm-uninstall:
	@echo "==> Uninstalling $(RELEASE_NAME) from namespace $(NAMESPACE)..."
	helm uninstall $(RELEASE_NAME) --namespace $(NAMESPACE)

# ==============================================================================
# CLUSTER DIAGNOSTICS & STATUS
# ==============================================================================

k8s-status:
	@echo "==> Fetching status for namespace: $(NAMESPACE)"
	@kubectl get pods,svc,pvc -n $(NAMESPACE) -o wide

k8s-logs-apps:
	@kubectl logs -n $(NAMESPACE) -l 'tier in (core,engine)' --all-containers=true -f --tail=100

k8s-logs-infra:
	@kubectl logs -n $(NAMESPACE) -l tier=infrastructure --all-containers=true -f --tail=100

# ==============================================================================
# DOCKER COMPOSE LOCAL RUNNER SHORTCUTS
# ==============================================================================

docker-up:
	@docker compose -f infrastructure/docker/docker-compose.apps.yml up -d --build

docker-down:
	@docker compose -f infrastructure/docker/docker-compose.apps.yml down -v