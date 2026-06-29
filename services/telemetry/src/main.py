import os
import json
import time
import logging
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from plutopus_shared.db import SessionLocal, engine, Base
from plutopus_shared.models import Metric, Event, TelemetrySnapshot
from normalizers import normalize_metric, normalize_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("telemetry-worker")

REDPANDA_BROKERS = os.getenv("REDPANDA_BROKERS", "redpanda:9092").split(",")
METRICS_TOPIC = "metrics_raw"
EVENTS_TOPIC = "events_raw"

def get_consumer():
    logger.info(f"Connecting to Redpanda brokers: {REDPANDA_BROKERS}")
    retries = 10
    while retries > 0:
        try:
            consumer = KafkaConsumer(
                METRICS_TOPIC,
                EVENTS_TOPIC,
                bootstrap_servers=REDPANDA_BROKERS,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                group_id="telemetry-worker-group"
            )
            logger.info("Successfully connected to Redpanda!")
            return consumer
        except Exception as e:
            logger.warning(f"Failed to connect to Redpanda: {e}. Retrying in 3 seconds... ({retries} left)")
            retries -= 1
            time.sleep(3)
    raise RuntimeError("Could not connect to Redpanda brokers.")

def process_messages():
    # Make sure database tables are present
    Base.metadata.create_all(bind=engine)
    
    try:
        consumer = get_consumer()
    except Exception as e:
        logger.critical(e)
        return

    db: Session = SessionLocal()
    
    logger.info("Telemetry consumer worker started. Listening for messages...")
    
    metric_count = 0
    event_count = 0
    last_snapshot_time = time.time()
    
    try:
        for msg in consumer:
            topic = msg.topic
            payload = msg.value
            logger.debug(f"Received message from topic {topic}: {payload}")
            
            if topic == METRICS_TOPIC:
                normalized = normalize_metric(payload)
                if normalized:
                    metric = Metric(
                        target_id=normalized["target_id"],
                        name=normalized["name"],
                        value=normalized["value"],
                        timestamp=normalized["timestamp"]
                    )
                    db.add(metric)
                    metric_count += 1
                else:
                    logger.warning(f"Invalid metric payload received: {payload}")
            
            elif topic == EVENTS_TOPIC:
                normalized = normalize_event(payload)
                if normalized:
                    event = Event(
                        device_id=normalized["device_id"],
                        severity=normalized["severity"],
                        message=normalized["message"],
                        timestamp=normalized["timestamp"]
                    )
                    db.add(event)
                    event_count += 1
                else:
                    logger.warning(f"Invalid event payload received: {payload}")
            
            # Commit batches frequently or on every message for early stages
            db.commit()
            
            # Create a system health snapshot every 10 seconds
            current_time = time.time()
            if current_time - last_snapshot_time > 10:
                snapshot = TelemetrySnapshot(
                    metric_count=metric_count,
                    event_count=event_count,
                    healthy=True
                )
                db.add(snapshot)
                db.commit()
                logger.info(f"Saved Telemetry Snapshot - metrics accumulated: {metric_count}, events: {event_count}")
                last_snapshot_time = current_time

    except KeyboardInterrupt:
        logger.info("Stopping telemetry worker...")
    except Exception as e:
        logger.error(f"Error in telemetry loop: {e}")
    finally:
        db.close()
        consumer.close()

if __name__ == "__main__":
    process_messages()
