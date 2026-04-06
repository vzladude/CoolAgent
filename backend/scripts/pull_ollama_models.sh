#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Script para descargar los modelos de Ollama necesarios.
# Ejecutar después de levantar el contenedor de Ollama.
#
# Uso: ./scripts/pull_ollama_models.sh
# ─────────────────────────────────────────────────────────────

set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"

echo "🔄 Esperando que Ollama esté disponible..."
until curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; do
    sleep 2
    echo "   ⏳ Ollama no está listo todavía..."
done
echo "✅ Ollama está disponible"
echo ""

# Modelos a descargar
CHAT_MODEL="${OLLAMA_CHAT_MODEL:-qwen3:8b}"
VISION_MODEL="${OLLAMA_VISION_MODEL:-qwen2.5vl:7b}"
EMBEDDING_MODEL="${OLLAMA_EMBEDDING_MODEL:-qwen3-embedding:4b}"

echo "📦 Descargando modelos..."
echo ""

echo "1/3 — Chat: $CHAT_MODEL"
docker exec coolagent-ollama ollama pull "$CHAT_MODEL"
echo "✅ $CHAT_MODEL descargado"
echo ""

echo "2/3 — Vision: $VISION_MODEL"
docker exec coolagent-ollama ollama pull "$VISION_MODEL"
echo "✅ $VISION_MODEL descargado"
echo ""

echo "3/3 — Embeddings: $EMBEDDING_MODEL"
docker exec coolagent-ollama ollama pull "$EMBEDDING_MODEL"
echo "✅ $EMBEDDING_MODEL descargado"
echo ""

echo "🎉 ¡Todos los modelos descargados exitosamente!"
echo ""
echo "Modelos disponibles:"
docker exec coolagent-ollama ollama list
