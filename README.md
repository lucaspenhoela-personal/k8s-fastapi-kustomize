# k8s-fastapi-kustomize

Aplicacao containerizada (FastAPI + Redis) implantada em Kubernetes com
manifestos organizados via Kustomize (base + overlays dev/prod). Roda 100%
local com kind, sem custo. CI no GitHub Actions valida os manifestos e sobe
um cluster efemero para smoke test.

## Stack

- FastAPI servindo `/`, `/healthz` (liveness), `/readyz` (readiness) e `/metrics`
- Redis como dependencia (contador de visitas)
- Imagem Docker multi-stage, usuario nao-root, root filesystem somente leitura
- Deployments com probes, requests/limits e securityContext restritivo
- HorizontalPodAutoscaler por CPU
- Ingress (nginx) em `fastapi.localdev.me`
- Kustomize: `base` + overlays `dev` (1 replica, sem HPA) e `prod` (3-10 replicas)

## Pre-requisitos

Docker, kind, kubectl. O `kubectl` ja embute o Kustomize (`kubectl kustomize`).

## Subir local

    kind create cluster --name fastapi-demo --config kind-config.yaml
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    docker build -t k8s-fastapi-kustomize:dev ./app
    kind load docker-image k8s-fastapi-kustomize:dev --name fastapi-demo
    kubectl apply -k k8s/overlays/dev

## Testar

    curl -H "Host: fastapi.localdev.me" http://localhost/

## Estrutura

    app/                 codigo da API + Dockerfile
    k8s/base/            manifestos comuns
    k8s/overlays/dev/    1 replica, sem HPA
    k8s/overlays/prod/   3-10 replicas, tag de imagem :prod
    .github/workflows/   pipeline de CI

## Limpar

    kind delete cluster --name fastapi-demo
