from typing import Dict, Any

class AlertPrioritizationEngine:
    @staticmethod
    def calculate_priority(
        risk_score: int,
        confidence: float,
        time_to_impact_mins: int,  # lower time to impact = higher priority
        business_criticality: str,  # low, medium, high, mission_critical
        affected_nodes_count: int
    ) -> Dict[str, Any]:
        """
        Calculates a priority score (0-100) and returns a priority level.
        """
        # Criticality weight mapping
        criticality_weight = {
            "low": 10,
            "medium": 30,
            "high": 60,
            "mission_critical": 90
        }.get(business_criticality.lower(), 30)

        # Time to impact factor (shorter time = higher urgency)
        if time_to_impact_mins <= 15:
            urgency_score = 95
        elif time_to_impact_mins <= 30:
            urgency_score = 75
        elif time_to_impact_mins <= 60:
            urgency_score = 50
        else:
            urgency_score = 25

        # Node impact factor
        node_score = min(100, affected_nodes_count * 20)

        # Weighted calculation
        # Risk (30%), Criticality (35%), Urgency/Time (20%), Node impact (15%)
        raw_score = (
            (risk_score * 0.30) +
            (criticality_weight * 0.35) +
            (urgency_score * 0.20) +
            (node_score * 0.15)
        )

        # Grounding with confidence rating
        score = int(round(raw_score * confidence))
        score = max(0, min(100, score))

        # Classify Level
        if score >= 80:
            level = "critical"
        elif score >= 60:
            level = "high"
        elif score >= 35:
            level = "medium"
        else:
            level = "low"

        return {
            "priority": score,
            "level": level
        }
