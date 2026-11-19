# AI Text Analyzer — Kubernetes (minikube)

Практичний проект №2 «Використання оркестраторів…» (кубернетизація додатку).

Клієнт-серверний додаток для аналізу тексту, що складається з трьох контейнерів,
розгорнутих в **одному Pod** Kubernetes:

| Контейнер   | Образ                        | Призначення |
|-------------|------------------------------|-------------|
| `frontend`  | `text-analyzer-frontend:1.0` (nginx) | веб-сторінка, проксіює `/api/` на `localhost:5000` |
| `api`       | `text-analyzer-api:1.0` (Python/Flask) | REST API: статистика тексту та тональність; пише лог у `/var/log/app/app.log` |
| `log-agent` | `busybox:1.36`               | читає лог із спільного volume `emptyDir` та виводить його |

## Структура

```
api/                 Flask API + Dockerfile
frontend/            nginx + HTML + Dockerfile
docker-compose.yml   локальний запуск у Docker
k8s/pod.yaml         Pod із 3 контейнерами та volume emptyDir
k8s/service.yaml     Service NodePort для доступу з браузера
```

## Запуск у Docker

```
docker compose up -d --build
# http://localhost:8080
docker compose logs log-agent
docker compose down -v
```

## Запуск у Kubernetes (minikube)

```
minikube start --driver=docker
docker compose build
minikube image load text-analyzer-api:1.0
minikube image load text-analyzer-frontend:1.0
kubectl apply -f k8s/
kubectl get pods
minikube service text-analyzer
kubectl logs text-analyzer -c log-agent
```
