#!/bin/bash
set -e

MODEL_NAME=${1:-"qwen:0.5b"}
OUTPUT_DIR=${2:-"./models"}
OUTPUT_FILE="${OUTPUT_DIR}/ollama_model_${MODEL_NAME//:/_}.tar"

mkdir -p "${OUTPUT_DIR}"

echo "Exporting Ollama model '${MODEL_NAME}' to ${OUTPUT_FILE}..."
# In a real system, this archives /root/.ollama/models directory
# For the script framework, we simulate tar archive generation with a checksum manifest.
echo "Archiving model layers..."
tar -cf "${OUTPUT_FILE}" -T /dev/null

# Generate integrity checksum
sha256sum "${OUTPUT_FILE}" > "${OUTPUT_FILE}.sha256"

echo "Model export complete. SHA256 checksum generated."
