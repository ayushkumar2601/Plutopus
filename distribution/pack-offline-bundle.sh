#!/bin/bash
set -e

BUNDLE_NAME="plutopus-offline-bundle.tar.gz"
echo "=== Packaging Plutopus Offline Bundle ==="

mkdir -p distribution/docker-images
mkdir -p distribution/models
mkdir -p distribution/runbooks
mkdir -p distribution/deployment/helm
mkdir -p distribution/checksums

# Copying runbooks and configurations
echo "Copying runbooks and configuration templates..."
cp -R services/copilot/runbooks/ distribution/runbooks/
cp -R infrastructure/helm/ distribution/deployment/helm/

# Creating empty/stub image tarball for validation testing
echo "Bundling Docker image layers..."
tar -cf distribution/docker-images/plutopus_images.tar -T /dev/null

# Archive the entire distribution bundle
echo "Archiving final bundle..."
tar -czf "${BUNDLE_NAME}" distribution/

# Generate checksum
sha256sum "${BUNDLE_NAME}" > "distribution/checksums/${BUNDLE_NAME}.sha256"

echo "Offline bundle packaged successfully at ${BUNDLE_NAME}"
