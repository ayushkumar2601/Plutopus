import os
import json
import sys
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add copilot path dynamically to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../services/copilot")))

from plutopus_shared import get_db, Site, Tunnel, RiskScore
from context.engine import CopilotContextEngine
from context.summarizer import CopilotIncidentSummarizer
from retrieval import CopilotRetrievalService
from memory import CopilotMemoryManager
from llm import call_ollama, generate_fallback_response
from prompts import SYSTEM_PROMPT, ANALYST_TEMPLATE

router = APIRouter()

# Global memory manager for session memory
memory_mgr = CopilotMemoryManager()

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"

class ExplainRequest(BaseModel):
    site_id: Optional[str] = None
    tunnel_id: Optional[str] = None

@router.post("/chat", response_model=Dict[str, Any])
def copilot_chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Natural language querying route. Compiles context and matched runbooks,
    queries Ollama, and falls back gracefully to a deterministic template if offline.
    """
    query = req.query
    session_id = req.session_id

    # 1. Extract potential entity IDs
    site_id, tunnel_id = CopilotRetrievalService.extract_entity_ids(query)
    
    # 2. Assemble context dictionary
    context_eng = CopilotContextEngine(db)
    context_data = {}
    sources = []
    
    if site_id:
        context_data = context_eng.get_site_context(site_id)
        sources.append(f"Site Context: {site_id}")
    elif tunnel_id:
        context_data = context_eng.get_tunnel_context(tunnel_id)
        sources.append(f"Tunnel Context: {tunnel_id}")
    else:
        # Fallback to high-level network stats
        sites = db.query(Site).all()
        tunnels = db.query(Tunnel).all()
        context_data = {
            "summary": "Global Network Context",
            "total_sites": len(sites),
            "total_tunnels": len(tunnels)
        }
        sources.append("Global Network Registry")

    # 3. Retrieve matched runbooks
    runbook_contents = CopilotRetrievalService.get_relevant_runbooks(query)
    if runbook_contents:
        sources.append("Troubleshooting Runbook guidelines")

    # 4. Fetch history and build prompt
    history = memory_mgr.get_history(session_id)
    history_str = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    
    prompt = ANALYST_TEMPLATE.format(
        context=json.dumps(context_data, indent=2) if isinstance(context_data, dict) else str(context_data),
        runbooks=runbook_contents,
        history=history_str,
        query=query
    )

    # 5. Call Ollama
    answer = call_ollama(prompt, SYSTEM_PROMPT)
    confidence = 0.89
    
    # Safety Layer Fallback
    if not answer:
        answer = generate_fallback_response(query, context_data, runbook_contents)
        confidence = 0.75

    # 6. Save memory
    memory_mgr.add_message(session_id, "user", query)
    memory_mgr.add_message(session_id, "copilot", answer)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence
    }

@router.post("/explain", response_model=Dict[str, Any])
def copilot_explain(req: ExplainRequest, db: Session = Depends(get_db)):
    """
    Provides explainable diagnostic outputs for a specific site or tunnel.
    """
    context_eng = CopilotContextEngine(db)
    runbook_srv = CopilotRetrievalService()
    
    if req.site_id:
        ctx = context_eng.get_site_context(req.site_id)
        runbooks = runbook_srv.get_relevant_runbooks("latency events flap")
        return {
            "entity_id": req.site_id,
            "entity_type": "site",
            "risk_score": ctx.get("risk_score", 0),
            "risk_level": ctx.get("risk_level", "low"),
            "signals": ctx.get("signals", []),
            "anomalies": ctx.get("active_anomalies", []),
            "runbook_recommendations": runbooks
        }
    elif req.tunnel_id:
        ctx = context_eng.get_tunnel_context(req.tunnel_id)
        runbooks = runbook_srv.get_relevant_runbooks("latency loss check")
        return {
            "entity_id": req.tunnel_id,
            "entity_type": "tunnel",
            "risk_score": ctx.get("risk_score", 0),
            "risk_level": ctx.get("risk_level", "low"),
            "signals": ctx.get("signals", []),
            "anomalies": ctx.get("anomalies", []),
            "runbook_recommendations": runbooks
        }
    else:
        raise HTTPException(status_code=400, detail="Must provide either site_id or tunnel_id")

@router.post("/incident-summary", response_model=Dict[str, Any])
def copilot_incident_summary(db: Session = Depends(get_db)):
    """
    Compiles all critical/elevated components into plain natural language incident summaries.
    """
    summarizer = CopilotIncidentSummarizer(db)
    
    # Find sites with elevated or high risk
    elevated_sites = db.query(RiskScore).filter(
        RiskScore.entity_type == "site",
        RiskScore.risk_level.in_(["elevated", "high"])
    ).order_by(RiskScore.timestamp.desc()).all()
    
    seen = set()
    summaries = []
    
    for s in elevated_sites:
        if s.entity_id not in seen:
            seen.add(s.entity_id)
            summaries.append(summarizer.summarize_site_incident(s.entity_id))
            
    if not summaries:
        return {
            "summary": "All network sites operating within healthy parameters. No elevated risk alerts.",
            "count": 0
        }
        
    return {
        "summary": "\n\n---\n\n".join(summaries),
        "count": len(summaries)
    }
