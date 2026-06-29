"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  priority: number;
  status: string;
  root_cause: string;
  affected_entities: string[];
  created_at: string;
}

export default function IncidentsDashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState("all");

  const fetchIncidents = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      // First, trigger a correlation run to populate any new incidents from anomalies
      await fetch(`${apiUrl}/api/v1/incidents/correlated`, {
        headers: { "Authorization": "Bearer mock-admin-token" } // token is bypassed or stubbed in dashboard local environment
      });

      const res = await fetch(`${apiUrl}/api/v1/incidents`, {
        headers: { "Authorization": "Bearer mock-admin-token" }
      });
      if (res.ok) {
        const data = await res.json();
        setIncidents(data);
      }
    } catch (err) {
      // Stub fallback data
      setIncidents([
        {
          id: "inc-101",
          title: "Correlated Hub Link Congestion affecting spokes",
          description: "Telemetry spike on tun-br06-hub-mpls matches degradation pattern across 3 spokes.",
          severity: "critical",
          priority: 92,
          status: "active",
          root_cause: "tun-br06-hub-mpls",
          affected_entities: ["site-branch-01", "site-branch-02", "site-branch-03"],
          created_at: new Date().toISOString()
        },
        {
          id: "inc-102",
          title: "Local site degradation on site-branch-04",
          description: "Multiple interface anomalies detected on branch 04 edge routers.",
          severity: "high",
          priority: 78,
          status: "active",
          root_cause: "site-branch-04",
          affected_entities: ["site-branch-04"],
          created_at: new Date(Date.now() - 3600000).toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const filteredIncidents = incidents.filter((i) => {
    if (filterSeverity === "all") return true;
    return i.severity.toLowerCase() === filterSeverity.toLowerCase();
  });

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

      {/* Main content area */}
      <main className="flex-1 p-10 space-y-8 overflow-y-auto">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Correlated Incident Management
            </h1>
            <p className="text-sm text-slate-550 mt-1">
              Topology-aware root cause correlation and alert priority indexes.
            </p>
          </div>
          <button
            onClick={fetchIncidents}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition-all shadow-md"
          >
            Force Run Correlation
          </button>
        </header>

        {/* Filters */}
        <section className="flex gap-2">
          {["all", "critical", "high", "medium", "low"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
                filterSeverity === sev
                  ? "bg-indigo-600/10 border-indigo-500/30 text-indigo-400"
                  : "bg-slate-900 border-slate-800 text-slate-450 hover:bg-slate-850"
              }`}
            >
              {sev.toUpperCase()}
            </button>
          ))}
        </section>

        {/* Incident list */}
        {loading ? (
          <div className="text-center py-20 text-slate-500 font-mono text-sm">
            Evaluating topological anomalies...
          </div>
        ) : (
          <section className="grid gap-4">
            {filteredIncidents.map((inc) => (
              <div
                key={inc.id}
                className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row justify-between gap-6 hover:border-slate-700/60 transition-all"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                        inc.severity === "critical"
                          ? "bg-rose-900/30 text-rose-400 border border-rose-800/40"
                          : inc.severity === "high"
                          ? "bg-amber-900/30 text-amber-400 border border-amber-800/40"
                          : "bg-slate-800 text-slate-400 border border-slate-750"
                      }`}
                    >
                      {inc.severity.toUpperCase()}
                    </span>
                    <span className="text-xs font-mono text-slate-500">Priority Score:</span>
                    <span className="text-xs font-bold font-mono text-indigo-400">{inc.priority}</span>
                    <span className="text-slate-700">|</span>
                    <span className="text-xs text-slate-500 font-mono">RC Candidate: `{inc.root_cause}`</span>
                  </div>

                  <h3 className="text-base font-bold text-slate-200">{inc.title}</h3>
                  <p className="text-sm text-slate-400 max-w-3xl leading-relaxed">{inc.description}</p>
                  
                  <div className="flex gap-2 items-center flex-wrap pt-2">
                    <span className="text-[10px] font-mono text-slate-650 uppercase">Scope:</span>
                    {inc.affected_entities.map((node) => (
                      <span key={node} className="px-1.5 py-0.5 bg-slate-950 border border-slate-850 rounded text-[10px] font-mono text-slate-450">
                        {node}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col justify-between items-end gap-4 min-w-[120px]">
                  <span className="text-[10px] font-mono text-slate-600">
                    {new Date(inc.created_at).toLocaleTimeString()}
                  </span>
                  <Link
                    href={`/dashboard/incidents/${inc.id}`}
                    className="px-4 py-1.5 bg-slate-805 hover:bg-slate-800 border border-slate-750 rounded-lg text-xs font-semibold transition-all text-indigo-400"
                  >
                    View Timeline
                  </Link>
                </div>
              </div>
            ))}

            {filteredIncidents.length === 0 && (
              <div className="text-center py-20 text-slate-500 font-mono text-sm">
                No active correlated incidents matching the filter.
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
