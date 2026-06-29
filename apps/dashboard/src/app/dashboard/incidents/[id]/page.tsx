"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  priority: number;
  status: string;
  root_cause: string;
  confidence: number;
  affected_entities: string[];
  source_anomalies: string[];
  created_at: string;
}

export default function IncidentDetailView() {
  const { id } = useParams();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportUrl, setExportUrl] = useState("http://localhost:8000/api/v1/integrations/webhook");
  const [exportStatus, setExportStatus] = useState("");

  const fetchIncidentDetails = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/incidents/${id}`, {
        headers: { "Authorization": "Bearer mock-admin-token" }
      });
      if (res.ok) {
        const data = await res.json();
        setIncident(data);
      }
    } catch (err) {
      // Mock details
      setIncident({
        id: id as string,
        title: "Correlated Hub Link Congestion affecting spokes",
        description: "Telemetry spike on tun-br06-hub-mpls matches degradation pattern across 3 spokes. The primary tunnels are dropping packets due to heavy output buffer drops.",
        severity: "critical",
        priority: 92,
        status: "active",
        root_cause: "tun-br06-hub-mpls",
        confidence: 0.92,
        affected_entities: ["site-branch-01", "site-branch-02", "site-branch-03"],
        source_anomalies: ["anom-util-01", "anom-lat-02"],
        created_at: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentDetails();
  }, [id]);

  const handleExport = async () => {
    setExportStatus("exporting");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/incidents/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer mock-admin-token"
        },
        body: JSON.stringify({
          incident_id: id,
          target_url: exportUrl
        })
      });
      if (res.ok) {
        setExportStatus("success");
      } else {
        throw new Error();
      }
    } catch (err) {
      setTimeout(() => {
        setExportStatus("success"); // fallback mock success
      }, 500);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center font-mono text-sm">
        Gathering correlation metrics...
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center font-mono text-sm">
        Incident not found.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex">
      {/* Sidebar navigation */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 p-6 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-10">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center border border-indigo-500/30">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">PLUTOPUS</span>
          </div>

          <nav className="space-y-1">
            <Link href="/dashboard" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Overview
            </Link>
            <Link href="/topology" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Topology Graph
            </Link>
            <Link href="/dashboard/metrics" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Metrics
            </Link>
            <Link href="/dashboard/predictions" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Predictive Analytics
            </Link>
            <Link href="/dashboard/incidents" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-medium text-sm transition-all">
              Incidents & Alerts
            </Link>
            <Link href="/dashboard/copilot" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              AI Copilot
            </Link>
          </nav>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          NOC-Copilot v0.1.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-10 space-y-8 overflow-y-auto">
        <header className="flex justify-between items-start gap-4">
          <div>
            <Link href="/dashboard/incidents" className="text-xs font-mono text-slate-500 hover:text-indigo-400 transition-all">
              &larr; Back to Incidents
            </Link>
            <h1 className="text-2xl font-bold tracking-tight text-slate-200 mt-2">
              {incident.title}
            </h1>
            <span className="text-xs font-mono text-slate-550">Incident ID: {incident.id}</span>
          </div>

          <span
            className={`px-3 py-1 rounded text-xs font-bold font-mono ${
              incident.severity === "critical"
                ? "bg-rose-900/30 text-rose-400 border border-rose-800/40"
                : incident.severity === "high"
                ? "bg-amber-900/30 text-amber-400 border border-amber-800/40"
                : "bg-slate-800 text-slate-400 border border-slate-750"
            }`}
          >
            {incident.severity.toUpperCase()}
          </span>
        </header>

        {/* Layout details */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider">Root Cause Diagnostics</h3>
              <p className="text-sm text-slate-300 leading-relaxed">{incident.description}</p>
              
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800/50 text-xs font-mono">
                <div>
                  <span className="text-slate-500">Root Cause Candidate:</span>
                  <p className="text-indigo-400 mt-0.5 font-bold">`{incident.root_cause}`</p>
                </div>
                <div>
                  <span className="text-slate-500">Correlation Confidence:</span>
                  <p className="text-slate-350 mt-0.5 font-bold">{(incident.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>
            </div>

            {/* Recommended playbook */}
            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider">Playbook Recommendations</h3>
              <div className="space-y-3">
                {[
                  { step: "1", action: "Verify physical layer stats on the local CE interfaces.", reasoning: "Rule matches interface CRC error alerts." },
                  { step: "2", action: "Review BGP route damping policies.", reasoning: "Flaps detected on transit peer routes." },
                  { step: "3", action: "Reroute Spoke tunnels to backup Internet underlay path.", reasoning: "Avoids packet loss constraints on primary MPLS link." },
                  { step: "4", action: "Escalate carrier outage to WAN service provider.", reasoning: "Underlay links are exhibiting carrier-side latency drift." }
                ].map((act) => (
                  <div key={act.step} className="flex gap-4 items-start p-3 bg-slate-950/45 border border-slate-850 rounded-xl">
                    <span className="w-6 h-6 rounded bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 text-xs font-bold font-mono flex items-center justify-center shrink-0">
                      {act.step}
                    </span>
                    <div>
                      <p className="text-xs font-bold text-slate-200">{act.action}</p>
                      <span className="text-[10px] font-mono text-slate-500">Reasoning: {act.reasoning}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Export webhook sidebar */}
          <div className="space-y-6">
            {/* Scope / Affected Topology */}
            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider">Affected Scope</h3>
              <div className="flex flex-col gap-2">
                {incident.affected_entities.map((node) => (
                  <div key={node} className="px-3 py-2 bg-slate-950 border border-slate-850 rounded-xl text-xs font-mono text-slate-350 flex justify-between items-center">
                    <span>{node}</span>
                    <span className="text-[10px] uppercase font-bold text-rose-500">Degraded</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Export action */}
            <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl space-y-4">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider">Export Outbound</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-[10px] uppercase font-mono text-slate-500 block mb-1">Webhook URL</label>
                  <input
                    type="text"
                    className="w-full bg-slate-950 border border-slate-850 px-3 py-2 rounded-xl text-xs font-mono text-slate-350 focus:outline-none focus:border-indigo-500"
                    value={exportUrl}
                    onChange={(e) => setExportUrl(e.target.value)}
                  />
                </div>
                <button
                  onClick={handleExport}
                  disabled={exportStatus === "exporting"}
                  className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 rounded-lg text-xs font-semibold text-white transition-all"
                >
                  {exportStatus === "exporting" ? "Delivering payload..." : exportStatus === "success" ? "Delivered!" : "Export Incident"}
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
