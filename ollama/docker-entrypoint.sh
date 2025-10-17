#!/usr/bin/env bash
set -euo pipefail

ollama serve &
SERVE_PID=$!

until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  sleep 0.5
done

BASE_MODEL="gpt-oss:20b"
MODEL_NAME="my-ai-model"
MODELFILE_PATH="/opt/Modelfile"
HASH_FILE="/root/.ollama/${MODEL_NAME}.hash"

if ! ollama show "$BASE_MODEL" >/dev/null 2>&1; then
  echo "[entrypoint] Base model yok, pull deneniyor..."
  ollama pull "$BASE_MODEL" || echo "[entrypoint] Uyarı: pull başarısız (TLS/Proxy?). Yerelde varsa devam."
fi

NEW_HASH="$(sha256sum "$MODELFILE_PATH" | awk '{print $1}')"
OLD_HASH="$(cat "$HASH_FILE" 2>/dev/null || echo "")"

if [[ "$NEW_HASH" != "$OLD_HASH" ]]; then
  echo "[entrypoint] Modelfile değişmiş -> modeli yeniden oluşturuyoruz"
  ollama rm "$MODEL_NAME" || true
  ollama create "$MODEL_NAME" -f "$MODELFILE_PATH"
  echo -n "$NEW_HASH" > "$HASH_FILE"
else
  echo "[entrypoint] Modelfile aynı -> mevcut modeli kullanıyoruz"
fi

wait "$SERVE_PID"