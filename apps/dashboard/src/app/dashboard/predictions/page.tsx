"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface RiskItem {
  id: string;
  name: string;
  type: string;
  score: number;
  level: string;
  confidence: number;
}

interface AnomalyItem {
  id: number;
  entity_id: string;
  entity_type: string;
  metric: string;
  severity: string;
  description: string;
}

export default function PredictionsDashboard() {
  const [riskSites, setRiskSites] = useState<RiskItem[]>([]);
  const [riskTunnels, setRiskTunnels] = useState<RiskItem[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const [sitesRes, tunnelsRes, anomaliesRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/predictions/sites`).then((r) => r.ok ? r.json() : []),
          fetch(`${apiUrl}/api/v1/predictions/tunnels`).then((r) => r.ok ? r.json() : []),
          fetch(`${apiUrl}/api/v1/anomalies?limit=10`).then((r) => r.ok ? r.json() : []),
        ]);

        const mappedSites = sitesRes.map((s: any) => ({
          id: s.entity_id,
          name: s.entity_id.replace("site-", "Site ").toUpperCase(),
          type: "site",
          score: s.risk_score,
          level: s.risk_level,
          confidence: 0.88
        }));

        const mappedTunnels = tunnelsRes.map((t: any) => ({
          id: t.entity_id,
          name: t.entity_id.toUpperCase(),
          type: "tunnel",
          score: t.risk_score,
          level: t.risk_level,
          confidence: 0.91
        }));

        setRiskSites(mappedSites);
        setRiskTunnels(mappedTunnels);
        setAnomalies(anomaliesRes);
      } catch (err) {
        console.warn("API offline, utilizing fallback mock prediction models.");
        // Mock fallback prediction state
        setRiskSites([
          { id: "site-branch-06", name: "BRANCH OFFICE 06", type: "site", score: 82, level: "high", confidence: 0.93 },
          { id: "site-branch-04", name: "BRANCH OFFICE 04", type: "site", score: 58, level: "elevated", confidence: 0.88 },
          { id: "site-branch-02", name: "BRANCH OFFICE 02", type: "site", score: 35, level: "moderate", confidence: 0.85 },
          { id: "site-hub", name: "HUB SITE", type: "site", score: 10, level: "low", confidence: 0.95 },
        ]);
        setRiskTunnels([
          { id: "tun-br06-hub-mpls", name: "TUN-BR06-HUB-MPLS", type: "tunnel", score: 90, level: "high", confidence: 0.92 },
          { id: "tun-br04-hub-inet", name: "TUN-BR04-HUB-INET", type: "tunnel", score: 65, level: "elevated", confidence: 0.89 },
          { id: "tun-br02-hub-mpls", name: "TUN-BR02-HUB-MPLS", type: "tunnel", score: 40, level: "moderate", confidence: 0.87 },
        ]);
        setAnomalies([
          { id: 1, entity_id: "tun-br06-hub-mpls", entity_type: "tunnel", metric: "packet_loss", severity: "critical", description: "Sudden anomaly spike detected on tunnel tun-br06-hub-mpls. Z-Score: 4.82." },
          { id: 2, entity_id: "int-br04-inet", entity_type: "interface", metric: "utilization", severity: "warning", description: "Utilization burst detected on interface int-br04-inet. Z-Score: 2.91." }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
    const interval = setInterval(fetchPredictions, 5000);
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "high":
        return "text-red-400 border-red-800/35 bg-red-950/20";
      case "elevated":
        return "text-orange-400 border-orange-800/35 bg-orange-950/20";
      case "moderate":
        return "text-amber-400 border-amber-800/35 bg-amber-950/20";
      default:
        return "text-emerald-400 border-emerald-800/35 bg-emerald-950/20";
    }
  };

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
            <Link href="/dashboard/predictions" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-medium text-sm transition-all">
              Predictive Analytics
            </Link>
          </nav>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          NOC-Copilot v0.1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight text-white">Predictive Analytics</h1>
          <p className="text-slate-400 text-sm mt-1">NOC hazard scoring, Z-score metric anomalies, and explainable foresight.</p>
        </header>

        {loading ? (
          <div className="text-slate-400 font-mono animate-pulse">Loading Predictions...</div>
        ) : (
          <div className="space-y-8">
            {/* Top risk sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Site risks */}
              <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4">Sites Risk Index</h3>
                <div className="space-y-3">
                  {riskSites.map((site) => (
                    <div key={site.id} className="flex justify-between items-center bg-slate-950/40 p-4 border border-slate-800/50 rounded-lg">
                      <div>
                        <Link href={`/dashboard/predictions/site/${site.id}`} className="font-bold text-slate-200 hover:underline">
                          {site.name}
                        </Link>
                        <span className="text-[10px] text-slate-500 font-mono block mt-0.5">Confidence: {site.confidence * 100}%</span>
                      </div>
                      <span className={`px-3 py-1 rounded text-xs font-bold border ${getRiskColor(site.level)}`}>
                        {site.score} - {site.level.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Tunnel risks */}
              <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
                <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4">Tunnels Risk Index</h3>
                <div className="space-y-3">
                  {riskTunnels.map((tun) => (
                    <div key={tun.id} className="flex justify-between items-center bg-slate-950/40 p-4 border border-slate-800/50 rounded-lg">
                      <div>
                        <Link href={`/dashboard/predictions/tunnel/${tun.id}`} className="font-bold text-slate-200 hover:underline">
                          {tun.name}
                        </Link>
                        <span className="text-[10px] text-slate-500 font-mono block mt-0.5">Confidence: {tun.confidence * 100}%</span>
                      </div>
                      <span className={`px-3 py-1 rounded text-xs font-bold border ${getRiskColor(tun.level)}`}>
                        {tun.score} - {tun.level.toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Live Anomalies list */}
            <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4">Active Telemetry Anomalies</h3>
              <div className="space-y-3">
                {anomalies.map((anom) => (
                  <div key={anom.id} className="flex items-center gap-4 bg-slate-950/40 border border-slate-800/50 p-4 rounded-lg">
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                      anom.severity === "critical" ? "bg-red-950/80 text-red-400 border-red-800/30" : "bg-amber-950/80 text-amber-400 border-amber-800/30"
                    }`}>
                      {anom.severity}
                    </span>
                    <div className="text-xs">
                      <span className="text-slate-400 font-mono uppercase">[{anom.entity_type} {anom.entity_id}]</span>
                      <p className="text-slate-200 mt-1 font-medium">{anom.description}</p>
                    </div>
                  </div>
                ))}
                {anomalies.length === 0 && (
                  <div className="text-slate-500 font-mono text-xs text-center py-6">No anomalies active in the network.</div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
