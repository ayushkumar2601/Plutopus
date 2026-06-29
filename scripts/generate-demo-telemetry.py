import os
import sys
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

REDPANDA_BROKERS = os.getenv("REDPANDA_BROKERS", "localhost:19092").split(",")

# Static IDs aligning with topology.yaml
TUNNELS = [
    "tun-br01-hub-mpls", "tun-br01-hub-inet",
    "tun-br02-hub-mpls", "tun-br02-hub-inet",
    "tun-br03-hub-mpls", "tun-br03-hub-inet"
]

INTERFACES = [
    "int-hub-mpls", "int-hub-inet",
    "int-br01-mpls", "int-br01-inet",
    "int-br02-mpls", "int-br02-inet",
    "int-br03-mpls", "int-br03-inet"
]

DEVICES = [
    "dev-hub-edge", "dev-br01-edge", "dev-br02-edge", "dev-br03-edge"
]

def get_producer():
    print(f"Connecting to Redpanda at {REDPANDA_BROKERS}...")
    retries = 5
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers=REDPANDA_BROKERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Connected successfully to Redpanda!")
            return producer
        except Exception as e:
            print(f"Connection failed: {e}. Retrying... ({retries} left)")
            retries -= 1
            time.sleep(2)
    raise RuntimeError("Could not connect to Redpanda.")

def generate_telemetry():
    try:
        producer = get_producer()
    except Exception as e:
        print(f"Failed to start telemetry generator: {e}")
        sys.exit(1)

    print("Starting simulated telemetry stream. Press Ctrl+C to stop.")
    
    tick = 0
    try:
        while True:
            timestamp = datetime.utcnow().isoformat()
            
            # Determine overall state (normal, spike, degradation, congestion, latency drift, loss burst, tunnel fail, flap)
            # Cycle states every 20 iterations
            state_cycle = (tick // 20) % 8
            
            latency_multiplier = 1.0
            loss_multiplier = 0.05
            util_base = 35.0
            state_name = "NORMAL"
            
            if state_cycle == 0:
                state_name = "NORMAL"
            elif state_cycle == 1:
                # Traffic Surge / Spike
                latency_multiplier = 1.2
                loss_multiplier = 0.1
                util_base = 85.0
                state_name = "TRAFFIC_SURGE"
            elif state_cycle == 2:
                # Congestion
                latency_multiplier = 1.8
                loss_multiplier = 1.5
                util_base = 92.0
                state_name = "CONGESTION"
            elif state_cycle == 3:
                # Latency Drift
                # Gradual latency scaling based on tick progress
                latency_multiplier = 1.0 + ((tick % 20) * 0.3)
                state_name = "LATENCY_DRIFT"
            elif state_cycle == 4:
                # Packet Loss Burst
                loss_multiplier = 12.0
                state_name = "PACKET_LOSS_BURST"
            elif state_cycle == 5:
                # Tunnel Failure simulation
                latency_multiplier = 10.0
                loss_multiplier = 20.0
                state_name = "TUNNEL_FAILURE"
            elif state_cycle == 6:
                # Interface Flapping
                util_base = 15.0 if (tick % 2 == 0) else 95.0
                state_name = "INTERFACE_FLAPPING"
            else:
                # General Degradation
                latency_multiplier = 4.0
                loss_multiplier = 5.0
                util_base = 50.0
                state_name = "DEGRADATION"

            if tick % 5 == 0:
                print(f"[Generator] Current simulation state: {state_name} (tick {tick})")

            # 1. Generate Metrics for Tunnels (latency, loss)
            for tun_id in TUNNELS:
                # Latency
                lat_val = random.uniform(10.0, 35.0) * latency_multiplier
                producer.send("metrics_raw", {
                    "target_id": tun_id,
                    "name": "latency",
                    "value": lat_val,
                    "timestamp": timestamp
                })
                
                # Packet Loss
                loss_val = max(0.0, random.uniform(0.0, 0.5) + (random.uniform(0.0, 1.0) * loss_multiplier))
                producer.send("metrics_raw", {
                    "target_id": tun_id,
                    "name": "packet_loss",
                    "value": loss_val,
                    "timestamp": timestamp
                })

            # 2. Generate Metrics for Interfaces (utilization)
            for intf_id in INTERFACES:
                util_val = min(100.0, max(0.0, util_base + random.uniform(-10.0, 10.0)))
                producer.send("metrics_raw", {
                    "target_id": intf_id,
                    "name": "utilization",
                    "value": util_val,
                    "timestamp": timestamp
                })

            # 3. Generate Random Events (Syslog)
            if random.random() < 0.15:
                dev_id = random.choice(DEVICES)
                severity = "info"
                message = f"Interface status check - all systems normal."
                
                if state_name == "SPIKE":
                    severity = "warning"
                    message = "High bandwidth threshold exceeded on WAN interface."
                elif state_name == "DEGRADATION":
                    severity = "critical"
                    message = "Tunnel peer keepalive timed out. Link flapping detected."
                
                producer.send("events_raw", {
                    "device_id": dev_id,
                    "severity": severity,
                    "message": message,
                    "timestamp": timestamp
                })

            producer.flush()
            tick += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTelemetry generator stopped.")
    finally:
        producer.close()

if __name__ == "__main__":
    generate_telemetry()
