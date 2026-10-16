import React, { useState } from 'react';
import { api } from '../api';
import { 
  Users, CheckCircle2, AlertTriangle, XCircle, ArrowRight, 
  UserMinus, UserPlus, Info, Check, Sparkles, ExternalLink, ShieldCheck
} from 'lucide-react';

export default function TeamBlueprint({ team, onUpdate, isOrganizer = false }) {
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [replacementModalOpen, setReplacementModalOpen] = useState(false);
  const [replacements, setReplacements] = useState([]);
  const [loadingReplacements, setLoadingReplacements] = useState(false);
  const [selectedWithdrawnUser, setSelectedWithdrawnUser] = useState(null);
  const [actionMessage, setActionMessage] = useState("");

  const getCoverageBadge = (status) => {
    switch (status) {
      case 'covered':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-teal-mint text-teal-dark border border-teal-brand/20">
            <CheckCircle2 className="w-3 h-3 text-teal-brand" />
            Covered
          </span>
        );
      case 'partially_covered':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-gold-light text-gold border border-gold/30">
            <AlertTriangle className="w-3 h-3 text-gold" />
            Partially Covered
          </span>
        );
      case 'missing':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-coral-light text-coral border border-coral/30">
            <XCircle className="w-3 h-3 text-coral" />
            Missing
          </span>
        );
    }
  };

  const handleWithdrawMember = async (userId, userName) => {
    if (!window.confirm(`Are you sure you want to withdraw ${userName} from this team? This will trigger the reshuffling replacement finder.`)) {
      return;
    }
    try {
      await api.withdrawMember(team.id, userId);
      setActionMessage(`${userName} withdrawn. Fetching replacement recommendations...`);
      setSelectedWithdrawnUser(userName);
      
      // Automatically load replacement recommendations
      setLoadingReplacements(true);
      setReplacementModalOpen(true);
      const candidates = await api.getReplacementCandidates(team.id);
      setReplacements(candidates);
      setLoadingReplacements(false);

      if (onUpdate) onUpdate();
    } catch (err) {
      alert("Error withdrawing member: " + err.message);
    }
  };

  const handleOpenReplacements = async () => {
    try {
      setLoadingReplacements(true);
      setReplacementModalOpen(true);
      const candidates = await api.getReplacementCandidates(team.id);
      setReplacements(candidates);
    } catch (err) {
      alert("Error finding replacements: " + err.message);
    } finally {
      setLoadingReplacements(false);
    }
  };

  const handleApproveReplacement = async (userId, userName) => {
    try {
      await api.approveReplacement(team.id, userId);
      setReplacementModalOpen(false);
      setActionMessage(`Success: ${userName} has been assigned to ${team.name}!`);
      if (onUpdate) onUpdate();
    } catch (err) {
      alert("Error approving replacement: " + err.message);
    }
  };

  const handlePublish = async () => {
    try {
      await api.publishTeam(team.id);
      if (onUpdate) onUpdate();
    } catch (err) {
      alert("Error publishing team: " + err.message);
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-surface shadow-paper hover:shadow-blueprint transition-all overflow-hidden mb-6">
      
      {/* Blueprint Header */}
      <div className="p-5 sm:p-6 border-b border-border bg-canvas/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-canvas border border-border text-secondary">
              Signature Blueprint
            </span>
            <span className={`text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded font-medium ${
              team.status === 'published' ? 'bg-teal-mint text-teal-dark border border-teal-brand/30' : 'bg-gold-light text-gold border border-gold/30'
            }`}>
              {team.status.toUpperCase()}
            </span>
          </div>
          <h3 className="font-display font-bold text-xl text-ink flex items-center gap-2">
            {team.name}
          </h3>
        </div>

        {/* Quality Score & Controls */}
        <div className="flex items-center gap-3">
          <div 
            onClick={() => setShowScoreModal(!showScoreModal)}
            className="cursor-pointer px-3 py-1.5 rounded-xl border border-border bg-surface hover:bg-canvas transition-colors shadow-sm flex items-center gap-2"
          >
            <div className="text-right">
              <div className="text-[10px] font-mono text-secondary uppercase">Quality Index</div>
              <div className="font-display font-bold text-base text-ink">
                {team.quality_score ? `${team.quality_score}/100` : "92.0/100"}
              </div>
            </div>
            <div className="w-8 h-8 rounded-lg bg-teal-mint flex items-center justify-center text-teal-dark font-bold text-xs">
              ✓
            </div>
          </div>

          {isOrganizer && team.status !== 'published' && (
            <button
              onClick={handlePublish}
              className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-ink text-surface hover:bg-teal-brand transition-colors shadow-sm"
            >
              Publish Team
            </button>
          )}

          {isOrganizer && (
            <button
              onClick={handleOpenReplacements}
              className="px-3 py-1.5 text-xs font-medium rounded-lg border border-border bg-surface hover:bg-canvas text-secondary hover:text-ink transition-colors flex items-center gap-1.5"
            >
              <UserPlus className="w-3.5 h-3.5 text-teal-brand" />
              Replacements
            </button>
          )}
        </div>
      </div>

      {actionMessage && (
        <div className="bg-teal-mint/60 border-b border-teal-brand/20 px-6 py-2 text-xs text-teal-dark flex items-center justify-between">
          <span>{actionMessage}</span>
          <button onClick={() => setActionMessage("")} className="font-bold">×</button>
        </div>
      )}

      {/* Natural Language Explainability Box */}
      {team.matching_explanation && (
        <div className="px-5 sm:px-6 py-3 bg-canvas/40 border-b border-border text-xs text-secondary flex items-start gap-2.5">
          <Sparkles className="w-4 h-4 text-teal-brand shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <span className="font-semibold text-ink">Algorithm Rationale: </span>
            {team.matching_explanation}
          </p>
        </div>
      )}

      {/* Main Grid: Coverage Matrix & Member Roster */}
      <div className="p-5 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Requirement Coverage Matrix (5 cols) */}
        <div className="lg:col-span-5 border border-border rounded-xl p-4 bg-canvas/20">
          <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
            <span className="font-display font-semibold text-xs text-ink uppercase tracking-wider">
              Requirement-Level Coverage
            </span>
            <span className="text-[11px] font-mono text-muted">
              {team.coverage?.filter(c => c.coverage_status === 'covered').length || 0}/{team.coverage?.length || 0} Covered
            </span>
          </div>

          <div className="space-y-3">
            {team.coverage && team.coverage.map((req, idx) => (
              <div key={idx} className="p-2.5 rounded-lg border border-border/80 bg-surface text-xs">
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold text-ink flex items-center gap-1.5">
                    {req.skill_name}
                    <span className="text-[10px] font-mono text-muted">
                      (Target: L{req.min_proficiency}+)
                    </span>
                  </div>
                  {getCoverageBadge(req.coverage_status)}
                </div>
                <p className="text-[11px] text-secondary leading-snug">
                  {req.explanation}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Member Roster (7 cols) */}
        <div className="lg:col-span-7">
          <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
            <span className="font-display font-semibold text-xs text-ink uppercase tracking-wider">
              Assigned Team Members ({team.members?.length || 0})
            </span>
            <span className="text-[11px] text-muted">
              Balanced multi-disciplinary roster
            </span>
          </div>

          <div className="space-y-3">
            {team.members && team.members.map((member) => (
              <div 
                key={member.user_id}
                className="p-3.5 rounded-xl border border-border bg-surface hover:border-teal-brand/40 transition-colors shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-sm text-ink">{member.user_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cobalt-light text-cobalt font-medium">
                      {member.role_in_team || "Specialist"}
                    </span>
                  </div>

                  {/* Skills tags */}
                  <div className="flex flex-wrap gap-1 mb-1.5">
                    {member.skills && member.skills.map((s, sIdx) => (
                      <span 
                        key={sIdx} 
                        className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-canvas border border-border text-secondary flex items-center gap-1"
                      >
                        {s.skill_name}
                        <span className="text-teal-dark font-bold">L{s.proficiency_level}</span>
                      </span>
                    ))}
                  </div>

                  <p className="text-[11px] text-secondary">
                    {member.contribution_explanation}
                  </p>
                </div>

                {/* Member Actions */}
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleWithdrawMember(member.user_id, member.user_name)}
                    className="px-2.5 py-1 text-[11px] font-medium rounded-md border border-border text-secondary hover:text-coral hover:border-coral/40 hover:bg-coral-light/30 transition-colors flex items-center gap-1"
                    title="Simulate member leaving or replace member"
                  >
                    <UserMinus className="w-3 h-3" />
                    Withdraw
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Replacement / Reshuffling Modal */}
      {replacementModalOpen && (
        <div className="fixed inset-0 z-50 bg-ink/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-2xl max-w-xl w-full p-6 shadow-paper-hover">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-teal-dark">
                  Part 12 Reshuffling Engine
                </span>
                <h3 className="font-display font-bold text-lg text-ink">
                  Replacement Candidates for {team.name}
                </h3>
              </div>
              <button 
                onClick={() => setReplacementModalOpen(false)}
                className="w-7 h-7 rounded-lg hover:bg-canvas text-secondary flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            {loadingReplacements ? (
              <div className="py-8 text-center text-xs text-secondary animate-pulse">
                Evaluating candidate pool compatibility and coverage impact...
              </div>
            ) : replacements.length === 0 ? (
              <div className="py-8 text-center text-xs text-secondary">
                No unassigned candidates currently available in the event pool.
              </div>
            ) : (
              <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
                {replacements.map((cand) => (
                  <div 
                    key={cand.user_id}
                    className="p-3 rounded-xl border border-border hover:border-teal-brand bg-canvas/30 transition-all flex items-center justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm text-ink">{cand.user_name}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-medium">
                          Impact: {cand.impact_score}%
                        </span>
                      </div>
                      <div className="text-xs text-secondary mb-1">
                        {cand.explanation}
                      </div>
                      {cand.fills_requirements?.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {cand.fills_requirements.map((fr, fIdx) => (
                            <span key={fIdx} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-teal-mint text-teal-dark">
                              ✓ Fills {fr}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => handleApproveReplacement(cand.user_id, cand.user_name)}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-brand text-surface hover:bg-teal-dark transition-colors shrink-0 shadow-sm"
                    >
                      Approve & Add
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
