import React from 'react';
import WeaveCanvas from '../components/WeaveCanvas';
import { 
  Users, Sparkles, ShieldCheck, ArrowRight, CheckCircle2, 
  Cpu, Compass, Award, RefreshCw, Layers
} from 'lucide-react';

export default function LandingPage({ onSelectDemoRole, onNavigate }) {
  return (
    <div className="space-y-12 pb-16">
      
      {/* Hero Section */}
      <section className="text-center pt-8 sm:pt-12 max-w-4xl mx-auto px-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-mint border border-teal-brand/20 text-teal-dark text-xs font-mono font-medium mb-4">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-brand animate-ping" />
          PROJECT CODENAME: LIVING WEAVE
        </div>

        <h1 className="font-display font-bold text-4xl sm:text-5xl lg:text-6xl text-ink tracking-tight leading-[1.15] mb-6">
          Form Balanced, Complementary Hackathon Teams with <span className="text-teal-brand underline decoration-teal-mint decoration-wavy decoration-2">Explainable Precision</span>.
        </h1>

        <p className="text-secondary text-base sm:text-lg max-w-2xl mx-auto mb-8 leading-relaxed">
          Traditional hackathons assign participants randomly or rely on superficial headcounts. 
          TeamWeave analyzes requirement-level capability coverage, availability, and distinct proficiencies to weave resilient teams.
        </p>

        {/* Demo Call-to-Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={() => onSelectDemoRole("organizer@teamweave.dev", "organizer")}
            className="px-6 py-3 rounded-xl bg-ink text-surface hover:bg-teal-brand font-semibold text-sm transition-all shadow-paper hover:shadow-paper-hover flex items-center gap-2 group"
          >
            <Cpu className="w-4 h-4 text-teal-mint" />
            Launch as Organizer (Dr. Aarav Patel)
            <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </button>

          <button
            onClick={() => onSelectDemoRole("maya@teamweave.dev", "profile")}
            className="px-6 py-3 rounded-xl bg-surface border border-border hover:border-teal-brand text-ink font-semibold text-sm transition-all shadow-paper hover:shadow-paper-hover flex items-center gap-2"
          >
            <Users className="w-4 h-4 text-cobalt" />
            Explore as Participant (Maya Sharma)
          </button>
        </div>
      </section>

      {/* Signature Motif Canvas */}
      <section className="max-w-6xl mx-auto px-4">
        <WeaveCanvas />
      </section>

      {/* Architectural Value Pillars (Part 2 & Part 3) */}
      <section className="max-w-6xl mx-auto px-4 pt-6">
        <div className="text-center mb-8">
          <span className="text-[11px] font-mono uppercase tracking-widest text-muted">
            Engine Architecture
          </span>
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            Engineered for Fairness & Technical Rigor
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper hover:shadow-paper-hover transition-all">
            <div className="w-10 h-10 rounded-xl bg-teal-mint flex items-center justify-center text-teal-dark mb-4">
              <CheckCircle2 className="w-5 h-5 text-teal-brand" />
            </div>
            <h3 className="font-display font-semibold text-lg text-ink mb-2">
              Requirement-Level Coverage
            </h3>
            <p className="text-secondary text-xs sm:text-sm leading-relaxed">
              Every team is evaluated for specific skill targets (e.g. React L2+, Python L2+). No double-counting, and a missing critical skill remains visibly flagged.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper hover:shadow-paper-hover transition-all">
            <div className="w-10 h-10 rounded-xl bg-cobalt-light flex items-center justify-center text-cobalt mb-4">
              <ShieldCheck className="w-5 h-5 text-cobalt" />
            </div>
            <h3 className="font-display font-semibold text-lg text-ink mb-2">
              Ability vs. Evidence Separation
            </h3>
            <p className="text-secondary text-xs sm:text-sm leading-relaxed">
              We separate declared proficiency from GitHub or portfolio links. Beginners without public repos are not artificially penalized in foundational roles.
            </p>
          </div>

          <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper hover:shadow-paper-hover transition-all">
            <div className="w-10 h-10 rounded-xl bg-gold-light flex items-center justify-center text-gold mb-4">
              <RefreshCw className="w-5 h-5 text-gold" />
            </div>
            <h3 className="font-display font-semibold text-lg text-ink mb-2">
              Resilient Reshuffling
            </h3>
            <p className="text-secondary text-xs sm:text-sm leading-relaxed">
              When a team member withdraws, TeamWeave quantifies the lost capability and surfaces ranked replacement candidates with explainable impact scores.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
}
