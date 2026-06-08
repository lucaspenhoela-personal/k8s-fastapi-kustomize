# Usa '>' como prefixo de receita em vez de TAB (sobrevive a copy/paste).
.RECIPEPREFIX = >
IMAGE ?= k8s-fastapi-kustomize:dev
CLUSTER ?= fastapi-demo

.PHONY: cluster-up ingress build load deploy test clean

cluster-up:
> kind create cluster --name $(CLUSTER) --config kind-config.yaml

ingress:
> kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
> kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s

build:
> docker build -t $(IMAGE) ./app

load:
> kind load docker-image $(IMAGE) --name $(CLUSTER)

deploy:
> kubectl apply -k k8s/overlays/dev
> kubectl -n fastapi-dev rollout status deploy/api --timeout=120s

test:
> curl -s -H "Host: fastapi.localdev.me" http://localhost/ ; echo
> curl -s -H "Host: fastapi.localdev.me" http://localhost/healthz ; echo
> curl -s -H "Host: fastapi.localdev.me" http://localhost/readyz ; echo

clean:
> kind delete cluster --name $(CLUSTER)
