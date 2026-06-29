"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface Signal {
  metric: string;
  impact: number;
}

interface TunnelDetailData {
  id: string;
  name: string;
  risk_score: number;
  risk_level: string;
  confidence: number;
  signals: Signal[];
  metrics: {
    name: string;
    current: number;
    f15m: number;
    f30m: number;
    f60m: number;
  }[];
}

export default function TunnelPredictionDetail({ params }: { params: Promise<{ id: string }> }) {
  const [tunnelId, setTunnelId] = useState<string | null>(null);
  const [tunnelData, setTunnelData] = useState<TunnelDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    params.then((p) => setTunnelId(p.id));
  }, [params]);

  useEffect(() => {
    if (!tunnelId) return;

    const fetchTunnelDetails = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const riskRes = await fetch(`${apiUrl}/api/v1/risk?entity_id=${tunnelId}`).then((r) => r.ok ? r.json() : []);
        
        if (riskRes.length > 0) {
          const latestRisk = riskRes[0];
          setTunnelData({
            id: tunnelId,
            name: tunnelId.toUpperCase(),
            risk_score: latestRisk.risk_score,
            risk_level: latestRisk.risk_level,
            confidence: 0.91,
            signals: latestRisk.signals || [],
            metrics: [
              { name: "Path Latency (ms)", current: 42.1, f15m: 48.9, f30m: 54.2, f60m: 65.0 },
              { name: "Path Packet Loss (%)", current: 0.2, f15m: 0.8, f30m: 1.5, f60m: 2.1 }
            ]
          });
        } else {
          throw new Error("No database entry");
        }
      } catch (err) {
        // Fallback mock tunnel detail
        setTunnelData({
          id: tunnelId,
          name: tunnelId.toUpperCase(),
          risk_score: 90,
          risk_level: "high",
          confidence: 0.92,
          signals: [
            { metric: "packet_loss", impact: 60 },
            { metric: "high_latency", impact: 40 }
          ],
          metrics: [
            { name: "Path Latency (ms)", current: 142.1, f15m: 158.9, f30m: 174.2, f60m: 195.0 },
            { name: "Path Packet Loss (%)", current: 5.2, f15m: 6.8, f30m: 8.5, f60m: 10.1 }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTunnelDetails();
  }, [tunnelId]);

  if (loading || !tunnelData) {
    return <div className="min-h-screen bg-slate-950 text-slate-400 p-10 font-mono animate-pulse">Loading Tunnel Predictions...</div>;
  }

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
        <header className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">{tunnelData.name} Details</h1>
            <p className="text-slate-400 text-sm mt-1">Predictive analysis model and contributing hazard factors.</p>
          </div>
          <Link href="/dashboard/predictions" className="px-4 py-2 bg-slate-800 hover:bg-slate-700/80 rounded-lg text-xs font-semibold text-slate-300 transition-all">
            ➔ Back to Dashboard
          </Link>
        </header>

        {/* Hazard score banner */}
        <section className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl mb-8 flex justify-between items-center">
          <div>
            <h3 className="text-sm font-semibold uppercase text-slate-500 tracking-wider mb-2">Calculated Tunnel Risk Index</h3>
            <div className="flex gap-4 items-baseline">
              <span className={`text-4xl font-extrabold px-3 py-1 rounded border ${getRiskColor(tunnelData.risk_level)}`}>
                {tunnelData.risk_score}
              </span>
              <span className="text-slate-400 text-sm uppercase font-semibold">Severity level: {tunnelData.risk_level}</span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-slate-500 text-xs font-mono block">Prediction Confidence</span>
            <span className="text-xl font-bold text-slate-300 font-mono">{(tunnelData.confidence * 100).toFixed(0)}%</span>
          </div>
        </section>

        {/* Signals and Forecast trends */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Signal contributions */}
          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
            <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-6">Explainability contributing factors</h3>
            <div className="space-y-4">
              {tunnelData.signals.map((sig, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-300">{sig.metric}</span>
                    <span className="text-indigo-400">Impact contribution: {sig.impact}%</span>
                  </div>
                  <div className="w-full bg-slate-950 h-2 rounded overflow-hidden border border-slate-800">
                    <div className="bg-indigo-500 h-full rounded" style={{ width: `${sig.impact}%` }}></div>
                  </div>
                </div>
              ))}
              {tunnelData.signals.length === 0 && (
                <div className="text-slate-500 font-mono text-xs text-center py-6">No hazardous metrics detected.</div>
              )}
            </div>
          </div>

          {/* Forecast Trend Metrics */}
          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
            <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-6">Metric Forecast Projections</h3>
            <div className="space-y-6">
              {tunnelData.metrics.map((m, i) => (
                <div key={i} className="border-b border-slate-800/40 pb-4 last:border-b-0 last:pb-0">
                  <span className="text-xs font-bold text-slate-200 block mb-2">{m.name}</span>
                  <div className="grid grid-cols-4 gap-2 text-center font-mono">
                    <div className="bg-slate-950/40 p-2 rounded border border-slate-900">
                      <span className="text-[10px] text-slate-500 block uppercase">Current</span>
                      <span className="text-sm font-semibold text-slate-300">{m.current}</span>
                    </div>
                    <div className="bg-slate-950/40 p-2 rounded border border-slate-900">
                      <span className="text-[10px] text-indigo-400 block uppercase">+15m</span>
                      <span className="text-sm font-semibold text-indigo-300">{m.f15m}</span>
                    </div>
                    <div className="bg-slate-950/40 p-2 rounded border border-slate-900">
                      <span className="text-[10px] text-indigo-400 block uppercase">+30m</span>
                      <span className="text-sm font-semibold text-indigo-300">{m.f30m}</span>
                    </div>
                    <div className="bg-slate-950/40 p-2 rounded border border-slate-900">
                      <span className="text-[10px] text-indigo-400 block uppercase">+60m</span>
                      <span className="text-sm font-semibold text-indigo-300">{m.f60m}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
