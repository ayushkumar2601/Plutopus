from datetime import datetime
from typing import Dict, Any, Optional

def normalize_metric(msg_val: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parses and normalizes raw metrics.
    Expected payload keys: target_id (str), name/metric_name (str), value (float), and optional timestamp (ISO string).
    """
    try:
        target_id = msg_val.get("target_id")
        name = msg_val.get("name") or msg_val.get("metric_name")
        value_raw = msg_val.get("value")
        if value_raw is None:
            return None
        value = float(value_raw)
        
        ts_str = msg_val.get("timestamp")
        if ts_str:
            timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.utcnow()
            
        if not target_id or not name:
            return None
            
        return {
            "target_id": target_id,
            "name": name,
            "value": value,
            "timestamp": timestamp
        }
    except Exception as e:
        print(f"Error normalizing metric: {e}")
        return None

def normalize_event(msg_val: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parses and normalizes Syslog and SNMP events.
    Expected payload keys: device_id (str), severity (str), message (str), and optional timestamp.
    """
    try:
        device_id = msg_val.get("device_id")
        severity = msg_val.get("severity", "info").lower()
        message = msg_val.get("message")
        
        ts_str = msg_val.get("timestamp")
        if ts_str:
            timestamp = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.utcnow()
            
        if not device_id or not message:
            return None
            
        return {
            "device_id": device_id,
            "severity": severity,
            "message": message,
            "timestamp": timestamp
        }
    except Exception as e:
        print(f"Error normalizing event: {e}")
        return None
