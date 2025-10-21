import os
import random
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

app = FastAPI(title="API Demo SLO/Error Budget")

def env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default

SIM_SUCCESS_PROB = env_float("SIM_SUCCESS_PROB", 0.97)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/simulate", response_class=PlainTextResponse)
def simulate(ok: float | None = None):
    """
    Retorna 200 com probabilidade 'ok' (0..1) e 500 caso contrário.
    - usa query param ?ok=0.97 ou env SIM_SUCCESS_PROB
    """
    p = SIM_SUCCESS_PROB if ok is None else float(ok)
    if random.random() < p:
        return Response(content="OK", status_code=200)
    return Response(content="ERROR", status_code=500)

@app.get("/status/{codes}", response_class=PlainTextResponse)
def status_codes(codes: str):
    """
    Alterna códigos: /status/200,500
    Útil para simular falhas determinísticas no monitor.
    """
    parts = [int(x.strip()) for x in codes.split(",") if x.strip().isdigit()]
    if not parts:
        return Response(content="Bad codes", status_code=400)
    import time
    code = parts[int(time.time()) % len(parts)]
    return Response(content=str(code), status_code=code)
