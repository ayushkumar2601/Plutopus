"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface SiteRow {
  id: string;
  name: string;
  role: string;
  status: string;
}

export default function SitesInventory() {
  const [sites, setSites] = useState<SiteRow[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/v1/sites`);
        if (res.ok) {
          const data = await res.json();
          const mapped = data.map((item: any) => ({
            id: item.id,
            name: item.name,
            role: item.role,
            status: "healthy"
          }));
          setSites(mapped);
        } else {
          throw new Error();
        }
      } catch (err) {
        console.warn("Using mock site inventory.");
        setSites([
          { id: "site-hub", name: "Hub Site", role: "hub", status: "healthy" },
          { id: "site-branch-01", name: "Branch Office 01", role: "spoke", status: "healthy" },
          { id: "site-branch-02", name: "Branch Office 02", role: "spoke", status: "warning" },
          { id: "site-branch-03", name: "Branch Office 03", role: "spoke", status: "healthy" },
          { id: "site-branch-04", name: "Branch Office 04", role: "spoke", status: "degraded" },
          { id: "site-branch-05", name: "Branch Office 05", role: "spoke", status: "healthy" },
          { id: "site-branch-06", name: "Branch Office 06", role: "spoke", status: "critical" },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchSites();
  }, []);

  const filteredSites = sites.filter((site) => {
    const matchesSearch = site.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          site.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === "all" || site.role === roleFilter;
    return matchesSearch && matchesRole;
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
            <div className="pt-4 border-t border-slate-800/50 my-2">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest px-4 block mb-2">Inventory</span>
              <Link href="/inventory/sites" className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 text-sm transition-all">
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
      <main className="flex-1 p-10 overflow-y-auto">
        <header className="mb-8 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Sites Inventory</h1>
            <p className="text-slate-400 text-sm mt-1">Registry of physical site locations, branch scopes, and roles.</p>
          </div>
        </header>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="Search by ID or name..."
            className="flex-1 bg-slate-900 border border-slate-800 px-4 py-2 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="bg-slate-900 border border-slate-800 px-4 py-2 rounded-lg text-sm text-slate-300 focus:outline-none"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">All Roles</option>
            <option value="hub">Hub</option>
            <option value="spoke">Spoke</option>
          </select>
        </div>

        {/* Inventory Table */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
          {loading ? (
            <div className="p-10 text-slate-400 font-mono text-center animate-pulse">Loading Inventory...</div>
          ) : (
            <table className="w-full text-left text-xs font-mono text-slate-300">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-6">Site ID</th>
                  <th className="py-3 px-6">Name</th>
                  <th className="py-3 px-6">Role</th>
                  <th className="py-3 px-6">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredSites.map((site) => (
                  <tr key={site.id} className="border-b border-slate-800/30 hover:bg-slate-800/10">
                    <td className="py-4 px-6 font-bold text-indigo-400">{site.id}</td>
                    <td className="py-4 px-6 text-slate-200">{site.name}</td>
                    <td className="py-4 px-6 uppercase text-slate-400">{site.role}</td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                        site.status === "critical" ? "bg-red-950 text-red-400 border-red-800/30" : "bg-emerald-950 text-emerald-400 border-emerald-800/30"
                      }`}>
                        {site.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}
