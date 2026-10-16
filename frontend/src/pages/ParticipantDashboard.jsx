import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  UserCheck, Plus, Trash2, ExternalLink, ShieldCheck, 
  Sparkles, CheckCircle2, MessageSquare, Star, ArrowRight
} from 'lucide-react';

export default function ParticipantDashboard({ currentUser, onUserUpdate }) {
  const [skills, setSkills] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add Skill state
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [selectedLevel, setSelectedLevel] = useState(2);

  // Add Evidence state
  const [evTitle, setEvTitle] = useState("");
  const [evUrl, setEvUrl] = useState("");
  const [evDesc, setEvDesc] = useState("");
  const [evSkillId, setEvSkillId] = useState("");
  const [evKind, setEvKind] = useState("project");

  // Feedback form state
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackComments, setFeedbackComments] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [mySkills, cat, myEv] = await Promise.all([
        api.getMySkills(),
        api.getSkillsCatalog(),
        api.getMyEvidence(),
      ]);
      setSkills(mySkills);
      setCatalog(cat);
      setEvidenceList(myEv);
      if (cat.length > 0 && !selectedSkillId) {
        setSelectedSkillId(cat[0].id);
      }
    } catch (err) {
      console.error("Error loading participant data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentUser]);

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!selectedSkillId) return;
    try {
      await api.addOrUpdateSkill({
        skill_id: parseInt(selectedSkillId),
        proficiency_level: parseInt(selectedLevel)
      });
      loadData();
    } catch (err) {
      alert("Error saving skill: " + err.message);
    }
  };

  const handleRemoveSkill = async (skillId) => {
    try {
      await api.removeSkill(skillId);
      loadData();
    } catch (err) {
      alert("Error removing skill: " + err.message);
    }
  };

  const handleAddEvidence = async (e) => {
    e.preventDefault();
    if (!evTitle) return;
    try {
      await api.addEvidence({
        title: evTitle,
        url: evUrl || null,
        description: evDesc || null,
        skill_id: evSkillId ? parseInt(evSkillId) : null,
        evidence_kind: evKind
      });
      setEvTitle("");
      setEvUrl("");
      setEvDesc("");
      loadData();
    } catch (err) {
      alert("Error adding evidence: " + err.message);
    }
  };

  const handleDeleteEvidence = async (evId) => {
    try {
      await api.removeEvidence(evId);
      loadData();
    } catch (err) {
      alert("Error removing evidence: " + err.message);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    try {
      await api.submitFeedback({
        event_id: 1,
        communication_rating: feedbackRating,
        collaboration_rating: feedbackRating,
        responsibility_rating: feedbackRating,
        distribution_rating: feedbackRating,
        overall_rating: feedbackRating,
        comments: feedbackComments
      });
      setFeedbackSubmitted(true);
    } catch (err) {
      alert("Error submitting feedback: " + err.message);
    }
  };

  const getLevelLabel = (lvl) => {
    switch (lvl) {
      case 1: return "L1 — Exploring (Curious / Fundamentals)";
      case 2: return "L2 — Developing (Can build with guidance)";
      case 3: return "L3 — Independent (Reliable autonomous execution)";
      case 4: return "L4 — Advanced (Architecture & Mentorship)";
      default: return `Level ${lvl}`;
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-sm text-secondary animate-pulse">
        Loading profile and capability matrix...
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Participant Profile Banner */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-cobalt-light text-cobalt font-medium">
              Participant Profile
            </span>
            <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-canvas border border-border text-secondary">
              Role: {currentUser?.preferred_roles || 'Software Builder'}
            </span>
          </div>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            {currentUser?.full_name}
          </h1>
          <p className="text-secondary text-xs sm:text-sm max-w-xl mt-1">
            {currentUser?.bio || "Passionate participant ready to build innovative hackathon solutions."}
          </p>
          <div className="text-[11px] font-mono text-muted mt-2">
            Interests: {currentUser?.interests || "Web, Cloud, AI"}
          </div>
        </div>

        <div className="p-4 rounded-xl border border-border bg-canvas/30 text-xs sm:max-w-xs">
          <div className="flex items-center gap-1.5 font-semibold text-ink mb-1">
            <ShieldCheck className="w-4 h-4 text-teal-brand" />
            Fair Skill Representation
          </div>
          <p className="text-[11px] text-secondary leading-snug">
            TeamWeave separates declared ability from repository evidence. You are matched based on capability and learning readiness, not commit counts.
          </p>
        </div>
      </div>

      {/* Grid: 4-Level Skills Matrix & Evidence Vault */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Col: 4-Level Skills (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          <div className="p-5 rounded-2xl border border-border bg-surface shadow-paper">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div>
                <h2 className="font-display font-bold text-base text-ink">
                  Declared Capabilities ({skills.length})
                </h2>
                <p className="text-[11px] text-secondary">
                  Four-tier proficiency model calibrated for honest collaboration.
                </p>
              </div>
            </div>

            {/* List Skills */}
            <div className="space-y-2.5 mb-6">
              {skills.length === 0 ? (
                <div className="text-center py-6 text-xs text-muted">
                  No skills declared yet. Add your first skill below!
                </div>
              ) : (
                skills.map((s) => (
                  <div key={s.id} className="p-3 rounded-xl border border-border bg-canvas/30 text-xs flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-ink flex items-center gap-2">
                        <span>{s.skill_name}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-bold">
                          L{s.proficiency_level}
                        </span>
                        {s.verified && (
                          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-surface border border-teal-brand text-teal-dark">
                            Evidence Linked
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-secondary mt-0.5">
                        {getLevelLabel(s.proficiency_level)}
                      </div>
                    </div>

                    <button
                      onClick={() => handleRemoveSkill(s.skill_id)}
                      className="w-7 h-7 rounded-lg text-muted hover:text-coral hover:bg-coral-light/40 flex items-center justify-center transition-colors"
                      title="Remove skill"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Add Skill Form */}
            <form onSubmit={handleAddSkill} className="border-t border-border pt-4 space-y-3">
              <span className="font-display font-semibold text-xs text-ink uppercase tracking-wider block">
                Add or Update Capability
              </span>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">Select Skill</label>
                  <select
                    value={selectedSkillId}
                    onChange={(e) => setSelectedSkillId(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    {catalog.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.category})</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">Proficiency Level</label>
                  <select
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    <option value="1">L1 — Exploring</option>
                    <option value="2">L2 — Developing</option>
                    <option value="3">L3 — Independent</option>
                    <option value="4">L4 — Advanced</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2 rounded-lg bg-surface border border-border hover:border-teal-brand text-ink text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Plus className="w-3.5 h-3.5 text-teal-brand" />
                Declare Proficiency
              </button>
            </form>

          </div>
        </div>

        {/* Right Col: Evidence Vault (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          <div className="p-5 rounded-2xl border border-border bg-surface shadow-paper">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div>
                <h2 className="font-display font-bold text-base text-ink">
                  Evidence Vault ({evidenceList.length})
                </h2>
                <p className="text-[11px] text-secondary">
                  Optional project repos, Figma links, or writing supporting your declarations.
                </p>
              </div>
            </div>

            {/* List Evidence */}
            <div className="space-y-2.5 mb-6">
              {evidenceList.length === 0 ? (
                <div className="text-center py-6 text-xs text-muted">
                  No evidence linked yet. Add a project link or paper!
                </div>
              ) : (
                evidenceList.map((ev) => (
                  <div key={ev.id} className="p-3 rounded-xl border border-border bg-canvas/30 text-xs flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold text-ink flex items-center gap-2">
                        <span>{ev.title}</span>
                        <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-canvas border border-border text-secondary">
                          {ev.evidence_kind}
                        </span>
                      </div>
                      {ev.description && (
                        <div className="text-[11px] text-secondary mt-0.5">
                          {ev.description}
                        </div>
                      )}
                      {ev.url && (
                        <a 
                          href={ev.url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="text-[10px] font-mono text-teal-dark hover:underline flex items-center gap-1 mt-1"
                        >
                          <ExternalLink className="w-2.5 h-2.5" />
                          {ev.url}
                        </a>
                      )}
                    </div>

                    <button
                      onClick={() => handleDeleteEvidence(ev.id)}
                      className="w-7 h-7 rounded-lg text-muted hover:text-coral hover:bg-coral-light/40 flex items-center justify-center transition-colors"
                      title="Remove evidence"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Add Evidence Form */}
            <form onSubmit={handleAddEvidence} className="border-t border-border pt-4 space-y-3">
              <span className="font-display font-semibold text-xs text-ink uppercase tracking-wider block">
                Link Project Proof / Artifact
              </span>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <input
                    type="text"
                    placeholder="Title (e.g. Design Token Library)"
                    value={evTitle}
                    onChange={(e) => setEvTitle(e.target.value)}
                    required
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink placeholder:text-muted"
                  />
                </div>

                <div>
                  <select
                    value={evKind}
                    onChange={(e) => setEvKind(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    <option value="project">Project / App</option>
                    <option value="portfolio">Figma / Portfolio</option>
                    <option value="certificate">Certification</option>
                    <option value="research">Research Paper</option>
                  </select>
                </div>
              </div>

              <div>
                <input
                  type="url"
                  placeholder="URL (e.g. https://github.com/username/project)"
                  value={evUrl}
                  onChange={(e) => setEvUrl(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink placeholder:text-muted"
                />
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Short description (e.g. Built 50+ reusable components)"
                  value={evDesc}
                  onChange={(e) => setEvDesc(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink placeholder:text-muted"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 rounded-lg bg-surface border border-border hover:border-teal-brand text-ink text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Plus className="w-3.5 h-3.5 text-teal-brand" />
                Store Evidence Artifact
              </button>
            </form>

          </div>
        </div>

      </div>

      {/* Part 14: Post-Event Collaboration Feedback */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper">
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="w-4 h-4 text-teal-brand" />
          <h2 className="font-display font-bold text-lg text-ink">
            Post-Event Collaboration Review (Part 14)
          </h2>
        </div>
        <p className="text-secondary text-xs sm:text-sm max-w-xl mb-4">
          Provide anonymous constructive feedback on team communication, task distribution, and collaborative dynamics.
        </p>

        {feedbackSubmitted ? (
          <div className="p-4 rounded-xl bg-teal-mint/60 border border-teal-brand/30 text-teal-dark text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-brand" />
            Thank you! Your feedback has been recorded to improve future team formation runs.
          </div>
        ) : (
          <form onSubmit={handleSubmitFeedback} className="space-y-4 max-w-xl">
            <div>
              <label className="text-xs font-medium text-ink block mb-1.5">
                Overall Collaboration & Team Synergy Rating: {feedbackRating} / 5
              </label>
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFeedbackRating(star)}
                    className={`w-9 h-9 rounded-lg flex items-center justify-center border transition-all ${
                      star <= feedbackRating 
                        ? 'bg-gold-light border-gold text-gold font-bold shadow-sm' 
                        : 'bg-canvas border-border text-muted hover:border-secondary'
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-ink block mb-1.5">
                Notes on task distribution or team balance:
              </label>
              <textarea
                rows={3}
                value={feedbackComments}
                onChange={(e) => setFeedbackComments(e.target.value)}
                placeholder="The team had a strong frontend and backend weave. Having a dedicated designer helped us polish the pitch."
                className="w-full text-xs p-3 rounded-xl border border-border bg-canvas text-ink placeholder:text-muted"
              />
            </div>

            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-ink text-surface hover:bg-teal-brand font-semibold text-xs transition-colors shadow-sm"
            >
              Submit Anonymous Review
            </button>
          </form>
        )}
      </div>

    </div>
  );
}
