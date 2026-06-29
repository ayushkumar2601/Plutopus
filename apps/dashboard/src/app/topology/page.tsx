"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface TopologyNode {
  id: string;
  label: string;
  type: string;
  status: string;
  x: number;
  y: number;
  ip?: string;
}

interface TopologyLink {
  id: string;
  source: string;
  target: string;
  status: string;
  label?: string;
  type: string;
}

export default function InteractiveTopology() {
  const [nodes, setNodes] = useState<TopologyNode[]>([]);
  const [links, setLinks] = useState<TopologyLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [pathResult, setPathResult] = useState<any>(null);
  const [srcSite, setSrcSite] = useState("");
  const [dstSite, setDstSite] = useState("");

  const staticNodes: TopologyNode[] = [
    { id: "site-hub", label: "HUB SITE", type: "hub", status: "healthy", x: 400, y: 120 },
    { id: "dev-hub-edge", label: "HUB ROUTER", type: "device", status: "healthy", x: 400, y: 200, ip: "10.0.0.1" },
    
    { id: "site-branch-01", label: "BRANCH 01", type: "spoke", status: "healthy", x: 120, y: 460 },
    { id: "dev-br01-edge", label: "BR-01 ROUTER", type: "device", status: "healthy", x: 120, y: 360, ip: "10.1.0.1" },
    
    { id: "site-branch-02", label: "BRANCH 02", type: "spoke", status: "warning", x: 230, y: 460 },
    { id: "dev-br02-edge", label: "BR-02 ROUTER", type: "device", status: "warning", x: 230, y: 360, ip: "10.2.0.1" },
    
    { id: "site-branch-03", label: "BRANCH 03", type: "spoke", status: "healthy", x: 340, y: 460 },
    { id: "dev-br03-edge", label: "BR-03 ROUTER", type: "device", status: "healthy", x: 340, y: 360, ip: "10.3.0.1" },

    { id: "site-branch-04", label: "BRANCH 04", type: "spoke", status: "degraded", x: 460, y: 460 },
    { id: "dev-br04-edge", label: "BR-04 ROUTER", type: "device", status: "degraded", x: 460, y: 360, ip: "10.4.0.1" },

    { id: "site-branch-05", label: "BRANCH 05", type: "spoke", status: "healthy", x: 570, y: 460 },
    { id: "dev-br05-edge", label: "BR-05 ROUTER", type: "device", status: "healthy", x: 570, y: 360, ip: "10.5.0.1" },

    { id: "site-branch-06", label: "BRANCH 06", type: "spoke", status: "critical", x: 680, y: 460 },
    { id: "dev-br06-edge", label: "BR-06 ROUTER", type: "device", status: "critical", x: 680, y: 360, ip: "10.6.0.1" }
  ];

  const staticLinks: TopologyLink[] = [
    { id: "link-site-hub-dev", source: "site-hub", target: "dev-hub-edge", status: "up", type: "physical" },
    { id: "link-site-br01-dev", source: "site-branch-01", target: "dev-br01-edge", status: "up", type: "physical" },
    { id: "link-site-br02-dev", source: "site-branch-02", target: "dev-br02-edge", status: "up", type: "physical" },
    { id: "link-site-br03-dev", source: "site-branch-03", target: "dev-br03-edge", status: "up", type: "physical" },
    { id: "link-site-br04-dev", source: "site-branch-04", target: "dev-br04-edge", status: "up", type: "physical" },
    { id: "link-site-br05-dev", source: "site-branch-05", target: "dev-br05-edge", status: "up", type: "physical" },
    { id: "link-site-br06-dev", source: "site-branch-06", target: "dev-br06-edge", status: "up", type: "physical" },
    
    { id: "tun-br01-hub-mpls", source: "dev-br01-edge", target: "dev-hub-edge", label: "MPLS", status: "up", type: "tunnel" },
    { id: "tun-br01-hub-inet", source: "dev-br01-edge", target: "dev-hub-edge", label: "Internet", status: "up", type: "tunnel" },
    { id: "tun-br02-hub-mpls", source: "dev-br02-edge", target: "dev-hub-edge", label: "MPLS", status: "down", type: "tunnel" },
    { id: "tun-br02-hub-inet", source: "dev-br02-edge", target: "dev-hub-edge", label: "Internet", status: "up", type: "tunnel" },
    { id: "tun-br03-hub-mpls", source: "dev-br03-edge", target: "dev-hub-edge", label: "MPLS", status: "up", type: "tunnel" },
    { id: "tun-br03-hub-inet", source: "dev-br03-edge", target: "dev-hub-edge", label: "Internet", status: "up", type: "tunnel" },
    { id: "tun-br04-hub-mpls", source: "dev-br04-edge", target: "dev-hub-edge", label: "MPLS", status: "up", type: "tunnel" },
    { id: "tun-br04-hub-inet", source: "dev-br04-edge", target: "dev-hub-edge", label: "Internet", status: "down", type: "tunnel" },
    { id: "tun-br05-hub-mpls", source: "dev-br05-edge", target: "dev-hub-edge", label: "MPLS", status: "up", type: "tunnel" },
    { id: "tun-br05-hub-inet", source: "dev-br05-edge", target: "dev-hub-edge", label: "Internet", status: "up", type: "tunnel" },
    { id: "tun-br06-hub-mpls", source: "dev-br06-edge", target: "dev-hub-edge", label: "MPLS", status: "down", type: "tunnel" },
    { id: "tun-br06-hub-inet", source: "dev-br06-edge", target: "dev-hub-edge", label: "Internet", status: "down", type: "tunnel" }
  ];

  useEffect(() => {
    const fetchTopology = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/api/v1/topology/graph`);
        if (response.ok) {
          const data = await response.json();
          // Merge coordinates from staticNodes
          const mappedNodes = data.nodes.map((node: any) => {
            const staticNode = staticNodes.find((n) => n.id === node.id);
            return {
              id: node.id,
              label: node.label || node.id.toUpperCase(),
              type: node.type || "device",
              status: node.status || "healthy",
              ip: node.ip,
              x: staticNode ? staticNode.x : 400,
              y: staticNode ? staticNode.y : 300
            };
          });
          
          const mappedLinks = data.edges.map((edge: any, i: number) => {
            const isTunnel = edge.relation === "INTERFACE_CONNECTED_TO" || !edge.relation;
            return {
              id: edge.tunnel_id || `edge-${i}`,
              source: edge.source,
              target: edge.target,
              status: edge.status || "up",
              type: isTunnel ? "tunnel" : "physical",
              label: edge.tunnel_id ? (edge.tunnel_id.includes("mpls") ? "MPLS" : "Internet") : undefined
            };
          });
          setNodes(mappedNodes);
          setLinks(mappedLinks);
        } else {
          throw new Error();
        }
      } catch (err) {
        console.warn("Using local fallback network topology.");
        setNodes(staticNodes);
        setLinks(staticLinks);
      } finally {
        setLoading(false);
      }
    };

    fetchTopology();
  }, []);

  const calculatePath = async () => {
    if (!srcSite || !dstSite) return;
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/v1/topology/path?source_site=${srcSite}&destination_site=${dstSite}`);
      if (res.ok) {
        const data = await res.json();
        setPathResult(data);
      } else {
        alert("Path not found");
      }
    } catch (err) {
      // Mock path analysis
      setPathResult({
        path: [srcSite, "site-hub", dstSite],
        hops: 2,
        tunnels: [`tun-${srcSite.replace("site-", "")}-hub-mpls`, `tun-${dstSite.replace("site-", "")}-hub-mpls`]
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "critical":
      case "down":
        return "#ef4444";
      case "warning":
        return "#f59e0b";
      case "degraded":
        return "#f97316";
      default:
        return "#10b981";
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
            <Link href="/topology" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 font-medium text-sm transition-all">
              Topology Graph
            </Link>
            <Link href="/dashboard/metrics" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 font-medium text-sm transition-all">
              Metrics
            </Link>
            <div className="pt-4 border-t border-slate-800/50 my-2">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest px-4 block mb-2">Inventory</span>
              <Link href="/inventory/sites" className="flex items-center gap-3 px-4 py-2 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 text-sm transition-all">
                Sites List
              </Link>
              <Link href="/inventory/devices" className="flex items-center gap-3 px-4 py-2 rounded-lg text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 text-sm transition-all">
                Devices List
              </Link>
            </div>
          </nav>
        </div>

        <div className="text-xs text-slate-600 font-mono">
          NOC-Copilot v0.1.0
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-10 flex flex-col">
        <header className="mb-6 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Interactive Topology Map</h1>
            <p className="text-slate-400 text-sm mt-1">Full 7-site spoke-hub SD-WAN layout. Click nodes to inspect parameters.</p>
          </div>

          {/* Path traversal calculator */}
          <div className="flex gap-2 items-center bg-slate-900 border border-slate-800 p-3 rounded-xl">
            <select
              className="bg-slate-950 border border-slate-800 text-xs px-2 py-1 rounded text-slate-300"
              value={srcSite}
              onChange={(e) => setSrcSite(e.target.value)}
            >
              <option value="">Src Site</option>
              {staticNodes.filter(n => n.type !== "device").map(n => (
                <option key={n.id} value={n.id}>{n.id}</option>
              ))}
            </select>
            <span className="text-slate-600 text-xs">➔</span>
            <select
              className="bg-slate-950 border border-slate-800 text-xs px-2 py-1 rounded text-slate-300"
              value={dstSite}
              onChange={(e) => setDstSite(e.target.value)}
            >
              <option value="">Dst Site</option>
              {staticNodes.filter(n => n.type !== "device").map(n => (
                <option key={n.id} value={n.id}>{n.id}</option>
              ))}
            </select>
            <button
              onClick={calculatePath}
              className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 rounded text-xs font-semibold text-white transition-all"
            >
              Find Path
            </button>
          </div>
        </header>

        {/* Path calculation result banner */}
        {pathResult && (
          <div className="mb-4 bg-indigo-950/40 border border-indigo-800/30 p-3 rounded-lg flex items-center justify-between text-xs">
            <div className="flex gap-2 items-center">
              <span className="font-bold text-indigo-400 uppercase">Path Found:</span>
              <span className="font-mono text-slate-200">{pathResult.path.join(" ➔ ")}</span>
              <span className="text-slate-500">({pathResult.hops} hops)</span>
            </div>
            <button className="text-slate-400 hover:text-slate-200" onClick={() => setPathResult(null)}>✕</button>
          </div>
        )}

        <div className="flex-1 flex gap-6 min-h-[500px]">
          {/* SVG Map Layout */}
          <div className="flex-1 bg-slate-900/40 border border-slate-800 rounded-xl relative p-4 flex items-center justify-center">
            {loading ? (
              <div className="text-slate-400 font-mono animate-pulse">Loading Topology Map...</div>
            ) : (
              <svg className="w-full h-full max-w-4xl max-h-[600px] bg-slate-950/40 rounded-lg" viewBox="0 0 800 600">
                {/* Connections */}
                {links.map((link, i) => {
                  const sourceNode = nodes.find((n) => n.id === link.source);
                  const targetNode = nodes.find((n) => n.id === link.target);
                  if (!sourceNode || !targetNode) return null;

                  const isTunnel = link.type === "tunnel";
                  const color = isTunnel 
                    ? (link.status === "down" ? "#ef4444" : (link.label === "MPLS" ? "#6366f1" : "#10b981")) 
                    : "#334155";
                  
                  return (
                    <line
                      key={i}
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke={color}
                      strokeWidth={isTunnel ? 2.5 : 2}
                      strokeDasharray={isTunnel ? "4 4" : "0"}
                      className={isTunnel && link.status === "up" ? "animate-pulse" : ""}
                    />
                  );
                })}

                {/* Nodes */}
                {nodes.map((node) => {
                  const isDevice = node.type === "device";
                  const isHub = node.type === "hub";
                  const color = getStatusColor(node.status);
                  const radius = isDevice ? 12 : 20;

                  return (
                    <g
                      key={node.id}
                      transform={`translate(${node.x}, ${node.y})`}
                      className="cursor-pointer"
                      onClick={() => setSelectedNode(node)}
                    >
                      <circle
                        r={radius}
                        fill={isHub ? "#4338ca" : (isDevice ? "#1e293b" : "#0f766e")}
                        stroke={color}
                        strokeWidth={2}
                      />
                      <text
                        y={radius + 18}
                        textAnchor="middle"
                        fill="#f1f5f9"
                        fontSize={9}
                        fontWeight={isDevice ? "normal" : "bold"}
                        className="pointer-events-none"
                      >
                        {node.label}
                      </text>
                      {!isDevice && (
                        <text textAnchor="middle" y={3} fill="#fff" fontSize={8} fontWeight="bold" className="pointer-events-none">
                          {isHub ? "HUB" : "SITE"}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            )}
          </div>

          {/* Details sidepanel */}
          <div className="w-80 bg-slate-900/40 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
            {selectedNode ? (
              <div>
                <div className="flex justify-between items-start mb-6">
                  <h3 className="text-xl font-bold text-white leading-tight">{selectedNode.label}</h3>
                  <span className="text-[10px] text-slate-500 uppercase font-mono tracking-widest">{selectedNode.type}</span>
                </div>

                <div className="space-y-4 border-t border-slate-800/60 pt-4">
                  <div>
                    <span className="text-xs text-slate-500 block">ID</span>
                    <span className="text-sm font-mono text-slate-300">{selectedNode.id}</span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-500 block">Status</span>
                    <span className="text-sm font-semibold uppercase" style={{ color: getStatusColor(selectedNode.status) }}>
                      {selectedNode.status}
                    </span>
                  </div>
                  {selectedNode.ip && (
                    <div>
                      <span className="text-xs text-slate-500 block">IP Address</span>
                      <span className="text-sm font-mono text-slate-300">{selectedNode.ip}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-slate-500 text-sm font-mono text-center">
                Click a node on the map to display parameters.
              </div>
            )}
            
            {selectedNode && (
              <button 
                onClick={() => setSelectedNode(null)} 
                className="mt-6 w-full py-2 bg-slate-800 hover:bg-slate-700/80 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-all"
              >
                Clear Selection
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
