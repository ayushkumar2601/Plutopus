import os
from typing import List, Dict, Any

RUNBOOKS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../runbooks"))

class CopilotRetrievalService:
    @staticmethod
    def get_relevant_runbooks(query: str) -> str:
        """
        Retrieves matching troubleshooting runbook guidelines based on search keywords.
        """
        query_lower = query.lower()
        matched_files = []
        
        if "latency" in query_lower:
            matched_files.append("high_latency.md")
        if "loss" in query_lower or "packet" in query_lower:
            matched_files.append("packet_loss.md")
        if "down" in query_lower or "fail" in query_lower or "failure" in query_lower:
            matched_files.append("tunnel_failure.md")
        if "congestion" in query_lower or "utilization" in query_lower:
            matched_files.append("congestion.md")
        if "flap" in query_lower:
            matched_files.append("interface_flapping.md")
        if "route" in query_lower or "instability" in query_lower:
            matched_files.append("route_instability.md")

        # Fallback to load default runbook if no keywords matched
        if not matched_files:
            matched_files = ["high_latency.md"]

        contents = []
        for filename in matched_files:
            filepath = os.path.join(RUNBOOKS_DIR, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r") as f:
                        contents.append(f"### From Runbook: {filename}\n" + f.read())
                except Exception:
                    pass
                    
        return "\n\n".join(contents)
        
    @staticmethod
    def extract_entity_ids(query: str) -> tuple:
        """
        Parses site-id or tunnel-id keywords from user queries.
        """
        query_lower = query.lower()
        site_id = None
        tunnel_id = None
        
        # Search for site-branch-XX or site-hub
        import re
        site_match = re.search(r"(site-branch-\d+|site-hub)", query_lower)
        if site_match:
            site_id = site_match.group(1)
            
        # Search for tun-brXX-hub-mpls/inet
        tun_match = re.search(r"(tun-br\d+-hub-(mpls|inet))", query_lower)
        if tun_match:
            tunnel_id = tun_match.group(1)
            
        return site_id, tunnel_id
