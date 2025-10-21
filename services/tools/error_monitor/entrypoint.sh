#!/bin/sh
set -e

: "${TARGET_URL:=http://api:8080/simulate}"
: "${RPM:=60}"
: "${DURATION:=600}"
: "${WINDOW:=300}"
: "${SLO:=99.5}"
: "${VERBOSE:=false}"

echo "Starting Error Monitor..."
echo "TARGET_URL=$TARGET_URL RPM=$RPM DURATION=$DURATION WINDOW=$WINDOW SLO=$SLO VERBOSE=$VERBOSE"

if [ "$VERBOSE" = "true" ]; then
  VERBOSE_FLAG="--verbose"
else
  VERBOSE_FLAG=""
fi

python /app/error_budget_monitor.py \
  --mode active \
  --url "$TARGET_URL" \
  --rpm "$RPM" \
  --duration "$DURATION" \
  --window "$WINDOW" \
  --slo "$SLO" \
  $VERBOSE_FLAG
