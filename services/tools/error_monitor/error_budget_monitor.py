#!/usr/bin/env python3
"""
Monitora taxa de erros de uma API e sinaliza risco/violação de SLO.
- Mede taxa de erros em janela deslizante (rolling window).
- Compara taxa de sucesso observada com SLO alvo (%).
- Calcula burn rate ≈ (error_rate%) / (budget%).
- Alerta quando SLO está em risco na janela.

Uso (exemplo no container):
  TARGET_URL=http://api:8080/simulate RPM=60 DURATION=600 WINDOW=300 SLO=99.5 docker compose up --build
"""
import argparse, time, sys
from collections import deque
from datetime import datetime
from typing import Deque, Tuple

try:
    import requests
except Exception:
    requests = None

OK = {200,201,202,204}

def parse_args():
    p = argparse.ArgumentParser(description="Monitor de Error Budget e SLO")
    p.add_argument("--mode", choices=["active","log"], required=True)
    p.add_argument("--url")
    p.add_argument("--rpm", type=int, default=60)
    p.add_argument("--duration", type=int, default=300)
    p.add_argument("--logfile")
    p.add_argument("--window", type=int, default=300)
    p.add_argument("--slo", type=float, default=99.9)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def evaluate_window(samples: Deque[Tuple[float,int]], slo_pct: float):
    total = len(samples)
    if total == 0:
        return dict(total=0, errors=0, success_rate=100.0, error_rate=0.0,
                    burn_rate=0.0, violated=False)

    errors = sum(1 for _,code in samples if code not in OK)
    success_rate = 100.0 * (total - errors) / total
    error_rate = 100.0 - success_rate
    budget_pct = max(1e-6, 100.0 - slo_pct)
    burn_rate = error_rate / budget_pct
    violated = success_rate < slo_pct
    return dict(total=total, errors=errors, success_rate=success_rate,
                error_rate=error_rate, burn_rate=burn_rate, violated=violated)

def print_summary(now_ts: float, stats: dict, window_seconds: int, slo_pct: float):
    ts = datetime.fromtimestamp(now_ts).isoformat(timespec="seconds")
    msg = (f"[{ts}] window={window_seconds//60}m, samples={stats['total']}, "
           f"success={stats['success_rate']:.3f}%, error={stats['error_rate']:.3f}%, "
           f"burn≈{stats['burn_rate']:.2f}x (SLO {slo_pct:.3f}%)")
    if stats["violated"]:
        msg += "  ⚠️  RISCO/VIOLAÇÃO: sucesso < SLO"
        if stats["burn_rate"] >= 1.0:
            msg += f" | consumindo budget {stats['burn_rate']:.1f}x mais rápido"
    print(msg, flush=True)

def active_mode(url: str, rpm: int, duration: int, window_seconds: int, slo_pct: float, verbose: bool):
    if requests is None:
        print("ERRO: módulo 'requests' indisponível", file=sys.stderr); sys.exit(2)
    if not url:
        print("--url é obrigatório em mode=active", file=sys.stderr); sys.exit(2)

    interval = 60.0 / max(1, rpm)
    samples: Deque[Tuple[float,int]] = deque()
    end = time.time() + duration

    # suporte httpbin-like: .../status/200,500
    simulate_codes = None
    if "/status/" in url and "," in url.rsplit("/status/",1)[1]:
        segment = url.rsplit("/status/",1)[1]
        try:
            simulate_codes = [int(x.strip()) for x in segment.split(",")]
            base = url.split("/status/")[0] + "/status/"
        except Exception:
            simulate_codes = None

    while time.time() < end:
        start = time.time()
        code = 0
        try:
            if simulate_codes:
                code_hint = simulate_codes[int(start) % len(simulate_codes)]
                resp = requests.get(base + str(code_hint), timeout=10)
                code = resp.status_code
            else:
                resp = requests.get(url, timeout=10)
                code = resp.status_code
        except Exception:
            code = 599

        now = time.time()
        samples.append((now, code))

        # expira amostras fora da janela
        cutoff = now - window_seconds
        while samples and samples[0][0] < cutoff:
            samples.popleft()

        stats = evaluate_window(samples, slo_pct)
        if verbose:
            print(f"status_code={code} -> {'OK' if code in OK else 'ERRO'}", flush=True)
        print_summary(now, stats, window_seconds, slo_pct)

        # pacing
        sleep = max(0.0, interval - (time.time() - start))
        time.sleep(sleep)

def log_mode(logfile: str, window_seconds: int, slo_pct: float, verbose: bool):
    import csv
    from datetime import datetime
    from collections import deque
    def parse_ts(ts: str) -> float:
        try: return float(ts)
        except: return datetime.fromisoformat(ts.replace("Z","+00:00")).timestamp()

    samples = []
    with open(logfile, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append((parse_ts(row["timestamp"]), int(row["status_code"])))
    samples.sort(key=lambda x: x[0])

    window: Deque[Tuple[float,int]] = deque()
    for ts, code in samples:
        window.append((ts, code))
        cutoff = ts - window_seconds
        while window and window[0][0] < cutoff:
            window.popleft()
        stats = evaluate_window(window, slo_pct)
        if verbose:
            print(f"[{datetime.fromtimestamp(ts).isoformat(timespec='seconds')}] code={code}")
        print_summary(ts, stats, window_seconds, slo_pct)

def main():
    args = parse_args()
    if args.mode == "active":
        active_mode(args.url, args.rpm, args.duration, args.window, args.slo, args.verbose)
    else:
        log_mode(args.logfile, args.window, args.slo, args.verbose)

if __name__ == "__main__":
    main()
