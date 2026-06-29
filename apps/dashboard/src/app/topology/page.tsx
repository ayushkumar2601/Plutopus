"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface TopologyNode {
  id: str;
  label: str;
  type: str;
  status: str;
}

interface TopologyLink {
  id: str;
  source: str;
  target: str;
  status: str;
}

export default function Topology() {
  const [nodes, setNodes] = useState<any[]>([]);
  const [links, setLinks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopology = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/v1/topology`);
        if (response.ok) {
          const data = await response.json();
          setNodes(data.nodes);
          setLinks(data.links);
        } else {
          throw new Error("Failed to load topology from backend");
        }
      } catch (err) {
        console.warn("Failed to connect to API topology endpoint, loading mock lab topology.");
        // Fallback mock topology aligning with topology.yaml
        setNodes([
          { id: "site-hub", label: "Hub Site", type: "hub", x: 400, y: 150 },
          { id: "dev-hub-edge", label: "Hub-Edge-Router", type: "device", x: 400, y: 230 },
          { id: "site-branch-01", label: "Branch 01", type: "spoke", x: 150, y: 450 },
          { id: "dev-br01-edge", label: "Branch-01-Edge", type: "device", x: 150, y: 370 },
          { id: "site-branch-02", label: "Branch 02", type: "spoke", x: 400, y: 450 },
          { id: "dev-br02-edge", label: "Branch-02-Edge", type: "device", x: 400, y: 370 },
          { id: "site-branch-03", label: "Branch 03", type: "spoke", x: 650, y: 450 },
          { id: "dev-br03-edge", label: "Branch-03-Edge", type: "device", x: 650, y: 370 },
        ]);
        setLinks([
          { id: "link-site-hub-dev", source: "site-hub", target: "dev-hub-edge", type: "physical" },
          { id: "link-site-br01-dev", source: "site-branch-01", target: "dev-br01-edge", type: "physical" },
          { id: "link-site-br02-dev", source: "site-branch-02", target: "dev-br02-edge", type: "physical" },
          { id: "link-site-br03-dev", source: "site-branch-03", target: "dev-br03-edge", type: "physical" },
          { id: "tun-br01-hub-mpls", source: "dev-br01-edge", target: "dev-hub-edge", label: "MPLS", type: "tunnel" },
          { id: "tun-br01-hub-inet", source: "dev-br01-edge", target: "dev-hub-edge", label: "Internet", type: "tunnel" },
          { id: "tun-br02-hub-mpls", source: "dev-br02-edge", target: "dev-hub-edge", label: "MPLS", type: "tunnel" },
          { id: "tun-br02-hub-inet", source: "dev-br02-edge", target: "dev-hub-edge", label: "Internet", type: "tunnel" },
          { id: "tun-br03-hub-mpls", source: "dev-br03-edge", target: "dev-hub-edge", label: "MPLS", type: "tunnel" },
          { id: "tun-br03-hub-inet", source: "dev-br03-edge", target: "dev-hub-edge", label: "Internet", type: "tunnel" },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchTopology();
  }, []);

  // Map nodes to coordinates if loaded dynamically from API
  const getNodeCoordinates = (nodeId: string, index: number) => {
    // If nodes already have positions from fallback:
    const existing = nodes.find((n) => n.id === nodeId);
    if (existing && existing.x !== undefined) {
      return { x: existing.x, y: existing.y };
    }
    // Dynamic circle positioning
    const angle = (index * 2 * Math.PI) / Math.max(1, nodes.length);
    return {
      x: 400 + Math.cos(angle) * 180,
      y: 300 + Math.sin(angle) * 180,
    };
  };

  const positionedNodes = nodes.map((node, idx) => {
    const coords = getNodeCoordinates(node.id, idx);
    return { ...node, ...coords };
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
            <Link href="/topology" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-medium text-sm transition-all">
              Topology Graph
            </Link>
            <Link href="/dashboard/metrics" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Metrics
            </Link>
          </nav>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          NOC-Copilot v0.1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 flex flex-col">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-white">Lab Topology Map</h1>
          <p className="text-slate-400 text-sm mt-1">Seeded SD-WAN/MPLS logical topology and active tunnel meshes.</p>
        </header>

        {/* Visual Graph Panel */}
        <section className="flex-1 bg-slate-900/40 border border-slate-800 rounded-xl relative p-4 flex items-center justify-center min-h-[500px]">
          {loading ? (
            <div className="text-slate-400 font-mono animate-pulse">Loading Topology Graph...</div>
          ) : (
            <svg className="w-full h-full max-w-4xl max-h-[600px] border border-slate-800/50 rounded-lg bg-slate-950/40" viewBox="0 0 800 600">
              {/* Draw Connections */}
              {links.map((link, i) => {
                const sourceNode = positionedNodes.find((n) => n.id === link.source);
                const targetNode = positionedNodes.find((n) => n.id === link.target);
                if (!sourceNode || !targetNode) return null;

                const isTunnel = link.type === "tunnel" || !link.id.startsWith("link-site-");
                const strokeColor = isTunnel 
                  ? (link.label === "MPLS" ? "#6366f1" : "#10b981") 
                  : "#334155";
                
                const midX = (sourceNode.x + targetNode.x) / 2;
                const midY = (sourceNode.y + targetNode.y) / 2;

                return (
                  <g key={i}>
                    <line
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke={strokeColor}
                      strokeWidth={isTunnel ? 2.5 : 2}
                      strokeDasharray={isTunnel ? "4 4" : "0"}
                      className={isTunnel ? "animate-pulse" : ""}
                    />
                    {isTunnel && (
                      <g transform={`translate(${midX + (link.label === "MPLS" ? -15 : 15)}, ${midY - 10})`}>
                        <rect x={-20} y={-8} width={40} height={16} rx={4} fill="#020617" stroke="#1e293b" strokeWidth={1} />
                        <text textAnchor="middle" y={4} fontSize={9} fill={strokeColor} fontWeight="bold" fontFamily="monospace">
                          {link.label || "TUNNEL"}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* Draw Nodes */}
              {positionedNodes.map((node, i) => {
                const isDevice = node.type === "device";
                const isHub = node.type === "hub";
                const fillColor = isHub ? "#4338ca" : (isDevice ? "#1e293b" : "#0f766e");
                const strokeColor = isHub ? "#818cf8" : (isDevice ? "#475569" : "#2dd4bf");
                const nodeRadius = isDevice ? 14 : 22;

                return (
                  <g key={i} transform={`translate(${node.x}, ${node.y})`} className="cursor-pointer">
                    <circle
                      r={nodeRadius}
                      fill={fillColor}
                      stroke={strokeColor}
                      strokeWidth={2}
                    />
                    <text
                      y={nodeRadius + 18}
                      textAnchor="middle"
                      fill="#e2e8f0"
                      fontSize={11}
                      fontWeight={isDevice ? "normal" : "bold"}
                    >
                      {node.label}
                    </text>
                    {/* Inner graphic */}
                    {!isDevice && (
                      <text textAnchor="middle" y={4} fill="#fff" fontSize={10} fontWeight="bold">
                        {isHub ? "HUB" : "SITE"}
                      </text>
                    )}
                  </g>
                );
              })}
            </svg>
          )}
        </section>
      </main>
    </div>
  );
}
