import React from "react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center justify-center relative overflow-hidden font-sans">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />

      {/* Main Content Card */}
      <main className="z-10 flex flex-col items-center max-w-md w-full px-6 text-center">
        {/* Animated Octopus/Network Icon Placeholder */}
        <div className="mb-8 relative flex items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-indigo-500/20 blur-md animate-pulse" />
          <div className="w-16 h-16 rounded-2xl bg-indigo-600 flex items-center justify-center border border-indigo-400/30 shadow-2xl shadow-indigo-500/50">
            <svg
              className="w-8 h-8 text-white animate-pulse"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
        </div>

        <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-200 via-slate-100 to-indigo-200 bg-clip-text text-transparent sm:text-5xl">
          Plutopus Dashboard
        </h1>
        
        <p className="mt-4 text-slate-400 text-sm sm:text-base max-w-sm">
          Self-Hosted Predictive NOC Copilot for SD-WAN & MPLS networks.
        </p>

        {/* Loading Indicator */}
        <div className="mt-12 w-full bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex items-center justify-between text-xs mb-3 text-slate-400 font-mono">
            <span>Core Engines</span>
            <span className="text-indigo-400 animate-pulse">CONNECTING</span>
          </div>

          <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
            <div className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-1.5 rounded-full w-2/3 animate-infinite-loading" />
          </div>

          <div className="mt-4 text-sm text-slate-300 font-medium animate-pulse">
            System Initializing...
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="absolute bottom-6 text-xs text-slate-600 font-mono">
        Plutopus v0.1.0-alpha &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
