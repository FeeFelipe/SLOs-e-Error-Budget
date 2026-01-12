import os
import time
import requests

def main():
    target = os.getenv("TARGET_URL", "http://api:8080/simulate")
    rpm = int(os.getenv("RPM", 60))
    duration = int(os.getenv("DURATION", 600))
    window = int(os.getenv("WINDOW", 300))
    slo = float(os.getenv("SLO", 99.5))
    verbose = os.getenv("VERBOSE", "false").lower() == "true"

    interval = 60 / rpm
    results = []
    start = time.time()
    while time.time() - start < duration:
        try:
            r = requests.get(target, timeout=2)
            ok = r.status_code == 200
        except Exception:
            ok = False
        results.append(ok)
        # Mantém janela deslizante
        if len(results) > window:
            results.pop(0)
        if len(results) == window:
            success = sum(results) / window * 100
            error = 100 - success
            error_budget = 100 - slo
            burn = error / error_budget if error_budget > 0 else 0
            ts = time.strftime("%Y-%m-%dT%H:%M:%S")
            msg = f"[{ts}] window={window//60}m samples={window} success={success:.1f}% error={error:.1f}% burn≈{burn:.1f}x (SLO {slo}%)"
            if burn > 1:
                msg += " ⚠️ RISCO/VIOLAÇÃO"
            print(msg)
        if verbose:
            print(f"Requisição: {'OK' if ok else 'ERRO'}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
