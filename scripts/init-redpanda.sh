#!/bin/sh

# Give Redpanda broker time to boot
echo "Waiting for Redpanda to initialize..."
until rpk cluster info --brokers redpanda:9092 > /dev/null 2>&1; do
  echo "Redpanda is not ready yet - sleeping..."
  sleep 2
done

echo "Creating Redpanda topics..."
rpk topic create metrics_raw --brokers redpanda:9092
rpk topic create events_raw --brokers redpanda:9092

echo "Topics initialized successfully!"
rpk topic list --brokers redpanda:9092
