import os
import sys
import time
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

# Add paths dynamically
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../topology")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/shared/src")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from plutopus_shared.db import SessionLocal, Base, engine
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event, Forecast, Anomaly, RiskScore
from forecasting import forecast_metric
from anomaly import detect_anomaly
from risk import calculate_tunnel_risk, calculate_site_risk
from correlation import RiskCorrelationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prediction-worker")

# 10s sleep for quick local testing/demo, 300s (5m) for production
SLEEP_INTERVAL = int(os.getenv("PREDICTION_INTERVAL", "15"))

def run_prediction_pipeline():
    logger.info("Initializing prediction database structures...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        logger.info("Starting prediction run...")
        current_time = time.time()
        now = datetime.utcnow()
        
        # 1. Process Interfaces (Utilization)
        interfaces = db.query(Interface).all()
        for intf in interfaces:
            # Query recent 15 metrics
            metrics = db.query(Metric).filter(
                Metric.target_id == intf.id,
                Metric.name == "utilization"
            ).order_by(Metric.timestamp.desc()).limit(15).all()
            
            if not metrics:
                continue
                
            metrics.reverse()
            vals = [m.value for m in metrics]
            times = [m.timestamp.timestamp() for m in metrics]
            
            # Forecast
            f_data = forecast_metric(vals, times, current_time)
            forecast = Forecast(
                target_id=intf.id,
                metric="utilization",
                current_val=f_data["current"],
                forecast_15m=f_data["forecast_15m"],
                forecast_30m=f_data["forecast_30m"],
                forecast_60m=f_data["forecast_60m"],
                confidence=f_data["confidence"],
                timestamp=now
            )
            db.add(forecast)
            
            # Anomaly check
            latest_val = vals[-1]
            hist_vals = vals[:-1]
            anom_data = detect_anomaly(intf.id, "interface", "utilization", latest_val, hist_vals)
            if anom_data:
                anomaly = Anomaly(
                    entity_id=anom_data["entity_id"],
                    entity_type=anom_data["entity_type"],
                    metric=anom_data["metric"],
                    severity=anom_data["severity"],
                    score=anom_data["score"],
                    description=anom_data["description"],
                    timestamp=now
                )
                db.add(anomaly)

        # 2. Process Tunnels (Latency and Loss)
        tunnels = db.query(Tunnel).all()
        tunnel_risk_map = {}
        for tun in tunnels:
            # Latency history
            lat_metrics = db.query(Metric).filter(
                Metric.target_id == tun.id,
                Metric.name == "latency"
            ).order_by(Metric.timestamp.desc()).limit(15).all()
            
            # Loss history
            loss_metrics = db.query(Metric).filter(
                Metric.target_id == tun.id,
                Metric.name == "packet_loss"
            ).order_by(Metric.timestamp.desc()).limit(15).all()

            latest_lat = 15.0
            latest_loss = 0.0
            
            if lat_metrics:
                lat_metrics.reverse()
                vals_lat = [m.value for m in lat_metrics]
                times_lat = [m.timestamp.timestamp() for m in lat_metrics]
                latest_lat = vals_lat[-1]
                
                f_lat = forecast_metric(vals_lat, times_lat, current_time)
                db.add(Forecast(
                    target_id=tun.id,
                    metric="latency",
                    current_val=f_lat["current"],
                    forecast_15m=f_lat["forecast_15m"],
                    forecast_30m=f_lat["forecast_30m"],
                    forecast_60m=f_lat["forecast_60m"],
                    confidence=f_lat["confidence"],
                    timestamp=now
                ))
                
                # Anomaly check latency
                anom_lat = detect_anomaly(tun.id, "tunnel", "latency", latest_lat, vals_lat[:-1])
                if anom_lat:
                    db.add(Anomaly(
                        entity_id=anom_lat["entity_id"],
                        entity_type=anom_lat["entity_type"],
                        metric=anom_lat["metric"],
                        severity=anom_lat["severity"],
                        score=anom_lat["score"],
                        description=anom_lat["description"],
                        timestamp=now
                    ))
                    
            if loss_metrics:
                loss_metrics.reverse()
                vals_loss = [m.value for m in loss_metrics]
                times_loss = [m.timestamp.timestamp() for m in loss_metrics]
                latest_loss = vals_loss[-1]
                
                f_loss = forecast_metric(vals_loss, times_loss, current_time)
                db.add(Forecast(
                    target_id=tun.id,
                    metric="packet_loss",
                    current_val=f_loss["current"],
                    forecast_15m=f_loss["forecast_15m"],
                    forecast_30m=f_loss["forecast_30m"],
                    forecast_60m=f_loss["forecast_60m"],
                    confidence=f_loss["confidence"],
                    timestamp=now
                ))
                
                # Anomaly check loss
                anom_loss = detect_anomaly(tun.id, "tunnel", "packet_loss", latest_loss, vals_loss[:-1])
                if anom_loss:
                    db.add(Anomaly(
                        entity_id=anom_loss["entity_id"],
                        entity_type=anom_loss["entity_type"],
                        metric=anom_loss["metric"],
                        severity=anom_loss["severity"],
                        score=anom_loss["score"],
                        description=anom_loss["description"],
                        timestamp=now
                    ))

            # Calculate Tunnel Risk
            status_down = (tun.status == "down")
            # Fetch latest utilization for tunnels (mapped from its source interface)
            latest_util = 40.0
            util_m = db.query(Metric).filter(
                Metric.target_id == tun.src_interface_id,
                Metric.name == "utilization"
            ).order_by(Metric.timestamp.desc()).first()
            if util_m:
                latest_util = util_m.value
                
            risk_data = calculate_tunnel_risk(tun.id, latest_lat, latest_loss, latest_util, status_down)
            
            # Expose explainability correlation weights
            explain_signals = RiskCorrelationEngine.get_contributing_signals(
                "tunnel", risk_data["risk_score"], risk_data["signals"]
            )
            
            risk_score_db = RiskScore(
                entity_id=tun.id,
                entity_type="tunnel",
                risk_score=risk_data["risk_score"],
                risk_level=risk_data["risk_level"],
                signals=json.dumps(explain_signals),
                timestamp=now
            )
            db.add(risk_score_db)
            tunnel_risk_map[tun.id] = risk_data["risk_score"]

        # 3. Process Sites (Aggregate Spoke/Hub Risks)
        sites = db.query(Site).all()
        for site in sites:
            # Map devices in site
            devices = db.query(Device).filter(Device.site_id == site.id).all()
            dev_ids = [d.id for d in devices]
            
            # Fetch active events/alarms count
            events_count = db.query(Event).filter(
                Event.device_id.in_(dev_ids)
            ).count()
            
            # Terminating tunnels
            interfaces = db.query(Interface).filter(Interface.device_id.in_(dev_ids)).all()
            intf_ids = [i.id for i in interfaces]
            tunnels_site = db.query(Tunnel).filter(
                (Tunnel.src_interface_id.in_(intf_ids)) | 
                (Tunnel.dst_interface_id.in_(intf_ids))
            ).all()
            
            site_tun_risks = [tunnel_risk_map.get(t.id, 0) for t in tunnels_site]
            
            # Hardware warnings check
            dev_degraded = False
            for d in devices:
                latest_dev_event = db.query(Event).filter(
                    Event.device_id == d.id,
                    Event.severity == "critical"
                ).order_by(Event.timestamp.desc()).first()
                if latest_dev_event:
                    dev_degraded = True
                    break

            site_risk = calculate_site_risk(site.id, site_tun_risks, events_count, dev_degraded)
            
            explain_signals_site = RiskCorrelationEngine.get_contributing_signals(
                "site", site_risk["risk_score"], site_risk["signals"]
            )

            risk_score_db = RiskScore(
                entity_id=site.id,
                entity_type="site",
                risk_score=site_risk["risk_score"],
                risk_level=site_risk["risk_level"],
                signals=json.dumps(explain_signals_site),
                timestamp=now
            )
            db.add(risk_score_db)

        db.commit()
        logger.info("Prediction run completed successfully. Persisted forecasts, anomalies, and risk scores.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error in prediction runner: {e}")
    finally:
        db.close()

def main():
    logger.info("Starting Plutopus Prediction Engine Worker...")
    while True:
        try:
            run_prediction_pipeline()
        except Exception as e:
            logger.error(f"Prediction loop error: {e}")
        logger.info(f"Sleeping for {SLEEP_INTERVAL} seconds...")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
