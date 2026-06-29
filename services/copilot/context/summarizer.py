from sqlalchemy.orm import Session
from context.engine import CopilotContextEngine

class CopilotIncidentSummarizer:
    def __init__(self, db: Session):
        self.db = db
        self.context_eng = CopilotContextEngine(db)

    def summarize_site_incident(self, site_id: str) -> str:
        """
        Converts site telemetry + predictions + risk into structured natural language.
        """
        ctx = self.context_eng.get_site_context(site_id)
        if not ctx:
            return f"Site {site_id} not found in database."

        summary_lines = [
            f"**Site Summary: {ctx['name']}** (Role: {ctx['role'].upper()})",
            f"- **Current Risk Index**: {ctx['risk_score']} ({ctx['risk_level'].upper()})",
        ]

        if ctx["signals"]:
            summary_lines.append("- **Active Risk Signals**:")
            for sig in ctx["signals"]:
                summary_lines.append(f"  * {sig['metric'].replace('_', ' ').capitalize()} (Impact: +{sig['impact']})")
        else:
            summary_lines.append("- **Active Risk Signals**: None (Healthy)")

        if ctx["active_anomalies"]:
            summary_lines.append("- **Active Anomalies Detected**:")
            for anom in ctx["active_anomalies"][:3]:
                summary_lines.append(f"  * [{anom['severity'].upper()}] {anom['description']}")
        else:
            summary_lines.append("- **Active Anomalies**: None")

        if ctx["connected_sites"]:
            summary_lines.append(f"- **Connected Neighbor Nodes**: {', '.join(ctx['connected_sites'])}")

        return "\n".join(summary_lines)

    def summarize_tunnel_incident(self, tunnel_id: str) -> str:
        """
        Converts tunnel metrics + forecasts + anomalies into natural language summaries.
        """
        ctx = self.context_eng.get_tunnel_context(tunnel_id)
        if not ctx:
            return f"Tunnel {tunnel_id} not found in database."

        metrics = ctx["metrics"]
        fc = ctx["forecasts"]
        
        summary_lines = [
            f"**Tunnel Summary: {ctx['tunnel_id']}** (Status: {ctx['status'].upper()})",
            f"- **Current Metrics**: Latency {metrics['latency']:.1f}ms | Packet Loss {metrics['packet_loss']:.2f}%",
            f"- **Forecasted Trend (30m)**: Latency {fc['latency_30m']:.1f}ms | Packet Loss {fc['packet_loss_30m']:.2f}% (Confidence: {fc['confidence'] * 100:.0f}%)",
            f"- **Risk Level**: {ctx['risk_score']} ({ctx['risk_level'].upper()})",
        ]

        if ctx["anomalies"]:
            summary_lines.append("- **Active Path Anomalies**:")
            for a in ctx["anomalies"]:
                summary_lines.append(f"  * [{a['severity'].upper()}] {a['description']}")
        else:
            summary_lines.append("- **Active Path Anomalies**: None")

        return "\n".join(summary_lines)
