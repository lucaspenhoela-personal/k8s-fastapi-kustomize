import os
import time

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import redis

APP_NAME = os.getenv("APP_NAME", "k8s-fastapi-kustomize")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

app = FastAPI(title=APP_NAME)
_started_at = time.time()

# Cliente Redis preguicoso: nao derruba o app se o Redis ainda nao subiu.
_redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD or None,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)


@app.get("/")
def root():
    try:
        visits = _redis.incr("visits")
    except redis.RedisError:
        visits = None
    return {
        "app": APP_NAME,
        "environment": ENVIRONMENT,
        "visits": visits,
        "message": "Hello from Kubernetes",
    }


@app.get("/healthz")
def healthz():
    # Liveness: o processo esta vivo. Nao depende de dependencias externas.
    return {"status": "ok", "uptime_seconds": round(time.time() - _started_at, 1)}


@app.get("/readyz")
def readyz():
    # Readiness: so recebe trafego se o Redis responder.
    try:
        _redis.ping()
    except redis.RedisError as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not-ready", "redis": str(exc)},
        )
    return {"status": "ready", "redis": "ok"}


@app.get("/metrics")
def metrics():
    # Exposicao minima no formato Prometheus (sem libs extras).
    try:
        visits = int(_redis.get("visits") or 0)
    except redis.RedisError:
        visits = 0
    body = (
        "# HELP app_visits_total Total de visitas registradas.\n"
        "# TYPE app_visits_total counter\n"
        f"app_visits_total {visits}\n"
        "# HELP app_uptime_seconds Tempo de vida do processo.\n"
        "# TYPE app_uptime_seconds gauge\n"
        f"app_uptime_seconds {round(time.time() - _started_at, 1)}\n"
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")
