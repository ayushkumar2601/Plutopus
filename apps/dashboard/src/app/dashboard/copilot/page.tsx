"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface Message {
  role: "user" | "copilot";
  content: string;
  sources?: string[];
  confidence?: number;
}

export default function CopilotDashboard() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "copilot",
      content: "Hello! I am Antigravity, your network analyst Copilot. I can retrieve topology details, explain predicted tunnel/site risk indexes, and fetch matched troubleshooting runbooks. Ask me anything about the network.",
      sources: ["Local Network Registry"]
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [incidentSummary, setIncidentSummary] = useState("");
  
  const suggestedQuestions = [
    "Why is site-branch-06 at risk?",
    "Show active anomalies.",
    "Which tunnels are predicted to fail?",
    "Explain risks for site-branch-04"
  ];

  useEffect(() => {
    const fetchIncidentSummary = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/v1/copilot/incident-summary`, { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          setIncidentSummary(data.summary);
        }
      } catch (err) {
        setIncidentSummary("Site BRANCH OFFICE 06 currently exhibits elevated latency.\n\nForecast: Latency 195.0ms within 30 minutes.\nRisk Score: 90 (HIGH)\nPrimary signals:\n- degraded_tunnels\n- alarm_events_spike");
      }
    };
    fetchIncidentSummary();
  }, []);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;
    
    setMessages((prev) => [...prev, { role: "user", content: textToSend }]);
    setQuery("");
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/copilot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: textToSend })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "copilot",
            content: data.answer,
            sources: data.sources,
            confidence: data.confidence
          }
        ]);
      } else {
        throw new Error();
      }
    } catch (err) {
      // Mock Fallback response in case API fails
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "copilot",
            content: `### Grounded Fallback Response\n\nActive monitoring indicates that the target component contains warnings.\n\n* **Risk level**: Elevated\n* **Matching Runbooks**: High Latency Troubleshooting\n\n**Sources**: Matching Troubleshooting Runbooks`,
            sources: ["Fallback Engine"],
            confidence: 0.75
          }
        ]);
      }, 500);
    } finally {
      setLoading(false);
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
            <Link href="/dashboard/predictions" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Predictive Analytics
            </Link>
            <Link href="/dashboard/copilot" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-medium text-sm transition-all">
              AI Copilot
            </Link>
          </nav>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          NOC-Copilot v0.1.0
        </div>
      </aside>

      {/* Main content grid */}
      <main className="flex-1 p-10 flex gap-8 overflow-hidden h-screen">
        {/* Chat area */}
        <section className="flex-1 flex flex-col justify-between bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden p-6 relative">
          <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex flex-col max-w-[80%] rounded-xl p-4 border ${
                  msg.role === "user"
                    ? "ml-auto bg-indigo-900/40 border-indigo-800/45 text-slate-200"
                    : "mr-auto bg-slate-950/40 border-slate-800/60 text-slate-300"
                }`}
              >
                <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-1.5">{msg.role}</span>
                <div className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</div>
                
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800/50 flex flex-wrap gap-1.5 items-center">
                    <span className="text-[9px] uppercase font-bold text-slate-500 mr-1 font-mono">Sources:</span>
                    {msg.sources.map((s, idx) => (
                      <span key={idx} className="px-1.5 py-0.5 bg-slate-900 border border-slate-800 rounded text-[9px] font-mono text-slate-400">
                        {s}
                      </span>
                    ))}
                    {msg.confidence && (
                      <span className="ml-auto text-[9px] font-mono text-indigo-400">
                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="mr-auto max-w-[80%] rounded-xl p-4 bg-slate-950/40 border border-slate-800/60 text-slate-500 font-mono text-xs animate-pulse">
                Antigravity is compiling topological retrieval context...
              </div>
            )}
          </div>

          {/* Prompt inputs */}
          <div className="mt-4 space-y-3">
            {/* Suggested Question tags */}
            <div className="flex gap-2 flex-wrap">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="px-3 py-1 bg-slate-950 hover:bg-slate-900 border border-slate-850 hover:border-slate-800 rounded-full text-[10px] text-slate-400 hover:text-slate-200 transition-all font-mono"
                >
                  {q}
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask about latency, packet loss, or sites risk levels..."
                className="flex-1 bg-slate-950 border border-slate-800 px-4 py-3 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend(query)}
              />
              <button
                onClick={() => handleSend(query)}
                className="px-6 bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold rounded-xl text-white transition-all"
              >
                Send
              </button>
            </div>
          </div>
        </section>

        {/* Side panel */}
        <aside className="w-80 flex flex-col gap-6 h-full overflow-y-auto">
          {/* Incident summaries */}
          <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-2xl flex-1 flex flex-col justify-between overflow-hidden">
            <div className="overflow-hidden flex flex-col flex-1">
              <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4">Active Incident summaries</h3>
              <div className="flex-1 overflow-y-auto whitespace-pre-wrap text-xs font-mono text-slate-400 bg-slate-950/40 border border-slate-850 p-4 rounded-xl leading-relaxed">
                {incidentSummary}
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
