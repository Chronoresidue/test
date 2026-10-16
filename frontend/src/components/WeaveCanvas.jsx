import React, { useState } from 'react';
import { Layers, Sparkles, CheckCircle2 } from 'lucide-react';

export default function WeaveCanvas({ onExplore }) {
  const [activeNode, setActiveNode] = useState(null);

  const nodes = [
    { id: 'fe', label: 'Frontend & UI', skill: 'React / Tailwind', x: 18, y: 35, color: '#17A982', category: 'Interface' },
    { id: 'be', label: 'Backend Core', skill: 'Python / FastAPI', x: 50, y: 22, color: '#536FF1', category: 'Architecture' },
    { id: 'ai', label: 'Applied AI', skill: 'PyTorch / RAG', x: 82, y: 35, color: '#8676D8', category: 'Intelligence' },
    { id: 'ds', label: 'Product Design', skill: 'Figma / UX Systems', x: 32, y: 72, color: '#ED8B76', category: 'Experience' },
    { id: 'ops', label: 'Cloud & DevOps', skill: 'Docker / CI/CD', x: 68, y: 72, color: '#D5A747', category: 'Infrastructure' },
  ];

  const threads = [
    { from: 'fe', to: 'be', label: 'API Contract' },
    { from: 'be', to: 'ai', label: 'Inference Pipeline' },
    { from: 'fe', to: 'ds', label: 'Design Tokens' },
    { from: 'be', to: 'ops', label: 'Deployment Weave' },
    { from: 'ai', to: 'fe', label: 'Generative Surface' },
    { from: 'ds', to: 'ops', label: 'Accessibility Audit' },
  ];

  const getNode = (id) => nodes.find(n => n.id === id);

  return (
    <div className="relative rounded-2xl border border-border bg-surface p-6 sm:p-8 shadow-paper overflow-hidden">
      {/* Background cartographic thread lattice */}
      <div className="absolute inset-0 weave-grid opacity-60 pointer-events-none" />

      {/* Header Info */}
      <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-teal-brand animate-pulse" />
            <span className="text-[11px] font-mono uppercase tracking-wider text-teal-dark font-medium">
              Signature Motif: Living Capability Lattice
            </span>
          </div>
          <h2 className="font-display font-bold text-2xl text-ink">
            Complementary Skill Weaving
          </h2>
          <p className="text-secondary text-sm max-w-xl">
            TeamWeave analyzes requirement-level coverage rather than raw member counts, ensuring full multi-disciplinary balance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-canvas border border-border text-secondary">
            Deterministic Engine
          </span>
          <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-teal-mint border border-teal-brand/20 text-teal-dark font-medium">
            Explainable Allocations
          </span>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <div className="relative w-full h-[280px] sm:h-[320px] rounded-xl bg-canvas/70 border border-border overflow-hidden flex items-center justify-center">
        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <defs>
            <linearGradient id="threadGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#17A982" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#536FF1" stopOpacity="0.4" />
            </linearGradient>
          </defs>

          {/* Render Connection Threads */}
          {threads.map((t, idx) => {
            const n1 = getNode(t.from);
            const n2 = getNode(t.to);
            if (!n1 || !n2) return null;
            const isHighlighted = activeNode === t.from || activeNode === t.to;

            // Curved bezier path
            const midX = (n1.x + n2.x) / 2;
            const midY = (n1.y + n2.y) / 2 - (idx % 2 === 0 ? 5 : -5);

            return (
              <g key={idx}>
                <path
                  d={`M ${n1.x} ${n1.y} Q ${midX} ${midY} ${n2.x} ${n2.y}`}
                  fill="none"
                  stroke={isHighlighted ? "#17A982" : "#D8DAD0"}
                  strokeWidth={isHighlighted ? "1.2" : "0.7"}
                  strokeDasharray={isHighlighted ? "none" : "2 1.5"}
                  className="transition-all duration-300"
                />
              </g>
            );
          })}

          {/* Render Nodes */}
          {nodes.map((n) => {
            const isHovered = activeNode === n.id;
            return (
              <g 
                key={n.id} 
                className="cursor-pointer transition-transform duration-200"
                onMouseEnter={() => setActiveNode(n.id)}
                onMouseLeave={() => setActiveNode(null)}
              >
                {/* Outer halo */}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={isHovered ? "7" : "5"}
                  fill={n.color}
                  fillOpacity={isHovered ? "0.22" : "0.12"}
                  className="transition-all duration-300"
                />
                {/* Core node */}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r="3.2"
                  fill="#FFFDF8"
                  stroke={n.color}
                  strokeWidth="1.5"
                />
                {/* Label */}
                <text
                  x={n.x}
                  y={n.y > 50 ? n.y + 7.5 : n.y - 5.5}
                  textAnchor="middle"
                  className="font-sans text-[3.2px] font-semibold fill-ink pointer-events-none"
                >
                  {n.label}
                </text>
                <text
                  x={n.x}
                  y={n.y > 50 ? n.y + 11 : n.y - 2.5}
                  textAnchor="middle"
                  className="font-mono text-[2.4px] fill-secondary pointer-events-none"
                >
                  {n.skill}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Floating tooltip preview */}
        <div className="absolute bottom-3 left-3 right-3 sm:right-auto sm:max-w-xs bg-surface/90 backdrop-blur-sm border border-border p-3 rounded-lg shadow-paper text-xs">
          <div className="flex items-center gap-1.5 font-semibold text-ink mb-1">
            <Sparkles className="w-3.5 h-3.5 text-teal-brand" />
            {activeNode ? `Focusing: ${getNode(activeNode)?.label}` : "Hover any node to inspect capabilities"}
          </div>
          <p className="text-[11px] text-secondary">
            {activeNode 
              ? `Demonstrates how ${getNode(activeNode)?.skill} links into surrounding teams to guarantee end-to-end hackathon execution.`
              : "Individual proficiencies are evaluated separately from evidence, ensuring beginners and cross-domain peers are paired fairly."}
          </p>
        </div>
      </div>
    </div>
  );
}
