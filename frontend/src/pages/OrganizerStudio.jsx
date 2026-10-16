import React, { useState, useEffect } from 'react';
import { api } from '../api';
import TeamBlueprint from '../components/TeamBlueprint';
import { 
  Cpu, Users, Plus, Trash2, Sparkles, CheckCircle2, 
  RefreshCw, AlertCircle, Layers, ArrowRight, ShieldAlert
} from 'lucide-react';

export default function OrganizerStudio({ eventId = 1 }) {
  const [event, setEvent] = useState(null);
  const [requirements, setRequirements] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [teams, setTeams] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [matchingInProgress, setMatchingInProgress] = useState(false);
  const [matchingSummary, setMatchingSummary] = useState("");

  // New Requirement Form state
  const [newSkillId, setNewSkillId] = useState("");
  const [newPriority, setNewPriority] = useState("required");
  const [newMinProf, setNewMinProf] = useState(2);
  const [newPeopleNeeded, setNewPeopleNeeded] = useState(1);
  const [newExplanation, setNewExplanation] = useState("");

  const loadEventData = async () => {
    try {
      setLoading(true);
      const [ev, reqs, parts, tms, cats] = await Promise.all([
        api.getEvent(eventId),
        api.getEventRequirements(eventId),
        api.getEventParticipants(eventId),
        api.getEventTeams(eventId),
        api.getSkillsCatalog()
      ]);
      setEvent(ev);
      setRequirements(reqs);
      setParticipants(parts);
      setTeams(tms);
      setCatalog(cats);
      if (cats.length > 0 && !newSkillId) {
        setNewSkillId(cats[0].id);
      }
    } catch (err) {
      console.error("Error loading event data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEventData();
  }, [eventId]);

  const handleRunMatching = async () => {
    try {
      setMatchingInProgress(true);
      const result = await api.runMatching(eventId);
      setTeams(result.teams);
      setMatchingSummary(result.summary);
      // Reload event status
      const updatedEv = await api.getEvent(eventId);
      setEvent(updatedEv);
    } catch (err) {
      alert("Error running matching: " + err.message);
    } finally {
      setMatchingInProgress(false);
    }
  };

  const handlePublishAll = async () => {
    try {
      const res = await api.publishAllTeams(eventId);
      alert(`Successfully published all ${res.published_count} teams!`);
      loadEventData();
    } catch (err) {
      alert("Error publishing teams: " + err.message);
    }
  };

  const handleAddRequirement = async (e) => {
    e.preventDefault();
    if (!newSkillId) return;
    try {
      await api.addEventRequirement(eventId, {
        skill_id: parseInt(newSkillId),
        priority: newPriority,
        min_proficiency: parseInt(newMinProf),
        people_needed: parseInt(newPeopleNeeded),
        explanation: newExplanation || "Standard team capability target"
      });
      setNewExplanation("");
      const updatedReqs = await api.getEventRequirements(eventId);
      setRequirements(updatedReqs);
    } catch (err) {
      alert("Error adding requirement: " + err.message);
    }
  };

  const handleDeleteRequirement = async (reqId) => {
    try {
      await api.deleteEventRequirement(eventId, reqId);
      const updatedReqs = await api.getEventRequirements(eventId);
      setRequirements(updatedReqs);
    } catch (err) {
      alert("Error deleting requirement: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-secondary animate-pulse">
        Loading Hackathon Studio and Participant Pool...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Studio Banner */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-medium border border-teal-brand/20">
              Organizer Control Center
            </span>
            <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-canvas border border-border text-secondary">
              Status: {event?.status || 'Open'}
            </span>
          </div>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            {event?.name}
          </h1>
          <p className="text-secondary text-xs sm:text-sm max-w-2xl mt-1">
            {event?.description}
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleRunMatching}
            disabled={matchingInProgress}
            className="px-5 py-2.5 rounded-xl bg-teal-brand hover:bg-teal-dark text-surface font-semibold text-xs sm:text-sm transition-all shadow-paper hover:shadow-paper-hover flex items-center gap-2 disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 ${matchingInProgress ? 'animate-spin' : ''}`} />
            {matchingInProgress ? "Weaving Teams..." : "Weave Teams (Operation B)"}
          </button>

          {teams.length > 0 && (
            <button
              onClick={handlePublishAll}
              className="px-4 py-2.5 rounded-xl bg-ink hover:bg-teal-brand text-surface font-semibold text-xs sm:text-sm transition-all shadow-sm"
            >
              Publish All Teams
            </button>
          )}
        </div>
      </div>

      {matchingSummary && (
        <div className="p-4 rounded-xl border border-teal-brand/30 bg-teal-mint/50 text-teal-dark text-xs sm:text-sm font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-teal-brand shrink-0" />
          <span>{matchingSummary}</span>
        </div>
      )}

      {/* Grid: Requirements Builder & Participant Pool */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Col: Requirements Config (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-5 rounded-2xl border border-border bg-surface shadow-paper">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div>
                <h2 className="font-display font-bold text-base text-ink">
                  Event Skill Requirements
                </h2>
                <p className="text-[11px] text-secondary">
                  Hard and preferred capabilities each formed team must satisfy.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-teal-dark bg-teal-mint px-2 py-0.5 rounded">
                {requirements.length} Configured
              </span>
            </div>

            {/* List Existing Requirements */}
            <div className="space-y-2.5 mb-6">
              {requirements.map((req) => (
                <div key={req.id} className="p-3 rounded-xl border border-border bg-canvas/30 text-xs flex items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2 font-semibold text-ink">
                      <span>{req.skill_name}</span>
                      <span className={`text-[9px] font-mono uppercase px-1.5 py-0.2 rounded font-medium ${
                        req.priority === 'required' ? 'bg-coral-light text-coral' : 'bg-cobalt-light text-cobalt'
                      }`}>
                        {req.priority}
                      </span>
                    </div>
                    <div className="text-[11px] text-secondary mt-0.5">
                      Min Level {req.min_proficiency} · Needed: {req.people_needed} person(s)
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteRequirement(req.id)}
                    className="w-7 h-7 rounded-lg text-muted hover:text-coral hover:bg-coral-light/40 flex items-center justify-center transition-colors"
                    title="Remove requirement"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add New Requirement Form */}
            <form onSubmit={handleAddRequirement} className="border-t border-border pt-4 space-y-3">
              <span className="font-display font-semibold text-xs text-ink uppercase tracking-wider block">
                Add Skill Requirement
              </span>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">Target Skill</label>
                  <select
                    value={newSkillId}
                    onChange={(e) => setNewSkillId(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    {catalog.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.category})</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    <option value="required">Required</option>
                    <option value="preferred">Preferred</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">Min Proficiency</label>
                  <select
                    value={newMinProf}
                    onChange={(e) => setNewMinProf(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  >
                    <option value="1">L1 - Exploring</option>
                    <option value="2">L2 - Developing</option>
                    <option value="3">L3 - Independent</option>
                    <option value="4">L4 - Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-mono text-secondary block mb-1">People Needed</label>
                  <input
                    type="number"
                    min="1"
                    max="3"
                    value={newPeopleNeeded}
                    onChange={(e) => setNewPeopleNeeded(e.target.value)}
                    className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink"
                  />
                </div>
              </div>

              <div>
                <input
                  type="text"
                  placeholder="Optional rationale (e.g. Core component delivery)"
                  value={newExplanation}
                  onChange={(e) => setNewExplanation(e.target.value)}
                  className="w-full text-xs p-2 rounded-lg border border-border bg-canvas text-ink placeholder:text-muted"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 rounded-lg bg-surface border border-border hover:border-teal-brand text-ink text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Plus className="w-3.5 h-3.5 text-teal-brand" />
                Add Requirement Target
              </button>
            </form>

          </div>
        </div>

        {/* Right Col: Registered Participant Pool (7 cols) */}
        <div className="lg:col-span-7">
          <div className="p-5 rounded-2xl border border-border bg-surface shadow-paper">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div>
                <h2 className="font-display font-bold text-base text-ink">
                  Registered Participant Pool ({participants.length})
                </h2>
                <p className="text-[11px] text-secondary">
                  Eligible candidates available for Operation B team formation.
                </p>
              </div>
              <span className="text-xs font-mono text-secondary">
                Min: {event?.min_team_size} · Max: {event?.max_team_size} per team
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[500px] overflow-y-auto pr-1">
              {participants.map((p) => (
                <div key={p.user_id} className="p-3 rounded-xl border border-border bg-canvas/30 text-xs hover:border-teal-brand/40 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-ink">{p.user_name}</span>
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-cobalt-light text-cobalt font-medium">
                      {p.preferred_role || "Generalist"}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {p.skills?.map((s, sIdx) => (
                      <span key={sIdx} className="text-[9px] font-mono px-1 py-0.2 rounded bg-surface border border-border text-secondary">
                        {s.skill_name} <strong className="text-teal-dark">L{s.proficiency_level}</strong>
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>

          </div>
        </div>

      </div>

      {/* Formed Team Blueprints Display */}
      <div className="space-y-6 pt-4 border-t border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display font-bold text-2xl text-ink">
              Formed Team Blueprints ({teams.length})
            </h2>
            <p className="text-secondary text-xs sm:text-sm">
              Each team reflects requirement-level coverage, role diversity, and natural language explainability.
            </p>
          </div>

          {teams.length === 0 && (
            <button
              onClick={handleRunMatching}
              className="px-4 py-2 rounded-xl bg-teal-brand text-surface text-xs font-semibold hover:bg-teal-dark transition-colors shadow-sm"
            >
              Run Intelligent Matching Now
            </button>
          )}
        </div>

        {teams.length === 0 ? (
          <div className="p-12 text-center rounded-2xl border border-dashed border-border bg-canvas/40">
            <Layers className="w-10 h-10 text-muted mx-auto mb-3" />
            <h3 className="font-display font-semibold text-base text-ink mb-1">
              No Teams Formed Yet
            </h3>
            <p className="text-xs text-secondary max-w-md mx-auto mb-4">
              Click "Weave Teams" above to trigger Operation B. The algorithm will optimize requirement coverage and generate full Team Blueprints.
            </p>
            <button
              onClick={handleRunMatching}
              className="px-4 py-2 rounded-lg bg-teal-brand text-surface text-xs font-semibold hover:bg-teal-dark transition-colors"
            >
              Run Matching Engine
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {teams.map((t) => (
              <TeamBlueprint
                key={t.id}
                team={t}
                onUpdate={loadEventData}
                isOrganizer={true}
              />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
