# Dockerfile para o Error Monitor
FROM python:3.11-slim
WORKDIR /app
COPY error_budget_monitor.py .
COPY entrypoint.sh .
RUN pip install requests
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
