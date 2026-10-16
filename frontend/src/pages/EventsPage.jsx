import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Calendar, Users, MapPin, CheckCircle2, Clock, 
  ArrowRight, Sparkles 
} from 'lucide-react';

export default function EventsPage({ currentUser, onNavigateToOrganizer }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joinModalEvent, setJoinModalEvent] = useState(null);
  const [rolePreference, setRolePreference] = useState("Frontend Engineer");
  const [goals, setGoals] = useState("Build an innovative AI-assisted web application");
  const [joinedSuccess, setJoinedSuccess] = useState(false);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const evs = await api.listEvents();
      setEvents(evs);
    } catch (err) {
      console.error("Error loading events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handleJoin = async (e) => {
    e.preventDefault();
    if (!joinModalEvent) return;
    try {
      await api.joinEvent(joinModalEvent.id, {
        preferred_role: rolePreference,
        event_goals: goals,
        availability: JSON.stringify(["weekend_full", "weekday_evening"])
      });
      setJoinedSuccess(true);
      setTimeout(() => {
        setJoinedSuccess(false);
        setJoinModalEvent(null);
        loadEvents();
      }, 1500);
    } catch (err) {
      alert("Error joining event: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-sm text-secondary animate-pulse">
        Loading active hackathons and challenges...
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-medium border border-teal-brand/20">
            Hackathons & Events
          </span>
        </div>
        <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
          Active Collaboration Events
        </h1>
        <p className="text-secondary text-xs sm:text-sm">
          Discover hackathons, join participant pools, and let the Living Weave engine match you into a complementary team.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {events.map((ev) => (
          <div key={ev.id} className="p-6 rounded-2xl border border-border bg-surface shadow-paper hover:shadow-paper-hover transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-semibold">
                  {ev.category.toUpperCase()}
                </span>
                <span className="text-xs font-mono text-muted">
                  Status: {ev.status}
                </span>
              </div>

              <h2 className="font-display font-bold text-xl text-ink mb-2">
                {ev.name}
              </h2>
              <p className="text-secondary text-xs sm:text-sm leading-relaxed mb-4">
                {ev.description}
              </p>

              <div className="space-y-2 border-t border-border pt-4 text-xs text-secondary">
                <div className="flex items-center gap-2">
                  <Users className="w-3.5 h-3.5 text-teal-brand" />
                  <span>
                    <strong>{ev.participant_count}</strong> Registered Participants
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-cobalt" />
                  <span>Team Size: <strong>{ev.min_team_size} - {ev.max_team_size}</strong> members</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-3.5 h-3.5 text-coral" />
                  <span>Mode: <strong className="capitalize">{ev.participation_mode}</strong></span>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-border flex items-center justify-between gap-3">
              {currentUser?.role === 'organizer' ? (
                <button
                  onClick={onNavigateToOrganizer}
                  className="w-full py-2.5 rounded-xl bg-ink text-surface hover:bg-teal-brand font-semibold text-xs transition-colors flex items-center justify-center gap-2 shadow-sm"
                >
                  Manage in Organizer Studio
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              ) : (
                <button
                  onClick={() => setJoinModalEvent(ev)}
                  className="w-full py-2.5 rounded-xl bg-teal-brand hover:bg-teal-dark text-surface font-semibold text-xs transition-colors flex items-center justify-center gap-2 shadow-sm"
                >
                  Join Participant Pool
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Join Event Modal */}
      {joinModalEvent && (
        <div className="fixed inset-0 z-50 bg-ink/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-2xl max-w-md w-full p-6 shadow-paper-hover">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <h3 className="font-display font-bold text-lg text-ink">
                Join {joinModalEvent.name}
              </h3>
              <button 
                onClick={() => setJoinModalEvent(null)}
                className="w-7 h-7 rounded-lg hover:bg-canvas text-secondary flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            {joinedSuccess ? (
              <div className="py-8 text-center text-xs text-teal-dark font-semibold flex flex-col items-center gap-2">
                <CheckCircle2 className="w-8 h-8 text-teal-brand" />
                Successfully registered! Your declared capabilities are now eligible for team weaving.
              </div>
            ) : (
              <form onSubmit={handleJoin} className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-ink block mb-1">
                    Preferred Hackathon Contribution Role
                  </label>
                  <input
                    type="text"
                    value={rolePreference}
                    onChange={(e) => setRolePreference(e.target.value)}
                    required
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-canvas text-ink"
                    placeholder="e.g. Frontend Engineer, Product Designer, AI Specialist"
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-ink block mb-1">
                    Hackathon Goal / Ambition
                  </label>
                  <textarea
                    rows={3}
                    value={goals}
                    onChange={(e) => setGoals(e.target.value)}
                    required
                    className="w-full text-xs p-2.5 rounded-lg border border-border bg-canvas text-ink"
                    placeholder="e.g. Build an explainable AI product and learn modern design systems"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-teal-brand hover:bg-teal-dark text-surface font-semibold text-xs transition-colors shadow-sm"
                >
                  Confirm Registration
                </button>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
