from typing import Dict, Any, List

class RiskCorrelationEngine:
    @staticmethod
    def get_contributing_signals(entity_type: str, risk_score: int, signals: List[str]) -> List[Dict[str, Any]]:
        """
        Determines the percentage impact contribution of each active telemetry signal to the risk score.
        """
        contributions = []
        if not signals:
            return []

        # Divide the score impact dynamically
        base_weight = 100 / len(signals)
        for sig in signals:
            impact_score = int(risk_score * (base_weight / 100))
            contributions.append({
                "metric": sig,
                "impact": max(1, impact_score)
            })
            
        return contributions
