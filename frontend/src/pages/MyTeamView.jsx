import React, { useState, useEffect } from 'react';
import { api } from '../api';
import TeamBlueprint from '../components/TeamBlueprint';
import { Users, AlertCircle, Sparkles, Layers } from 'lucide-react';

export default function MyTeamView({ currentUser }) {
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadMyTeam = async () => {
    try {
      setLoading(true);
      const allTeams = await api.getEventTeams(1);
      // Find the team where current user is a member
      const myTeam = allTeams.find(t => 
        t.members && t.members.some(m => m.user_id === currentUser?.id)
      );
      setTeam(myTeam || null);
    } catch (err) {
      console.error("Error loading my team:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMyTeam();
  }, [currentUser]);

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-sm text-secondary animate-pulse">
        Fetching your assigned team blueprint...
      </div>
    );
  }

  if (!team) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="p-10 rounded-2xl border border-dashed border-border bg-surface shadow-paper">
          <Layers className="w-12 h-12 text-muted mx-auto mb-4" />
          <h2 className="font-display font-bold text-xl text-ink mb-2">
            Team Not Assigned Yet
          </h2>
          <p className="text-secondary text-xs sm:text-sm max-w-md mx-auto mb-6">
            The organizer has not published teams yet or is currently balancing the candidate pool. 
            Check back shortly or visit the Organizer Studio to trigger the matching run!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-medium border border-teal-brand/20">
            Assigned Hackathon Roster
          </span>
        </div>
        <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
          My Collaboration Blueprint
        </h1>
        <p className="text-secondary text-xs sm:text-sm">
          Here is how your capabilities weave into your teammates' proficiencies to achieve complete project coverage.
        </p>
      </div>

      <TeamBlueprint
        team={team}
        onUpdate={loadMyTeam}
        isOrganizer={currentUser?.role === 'organizer'}
      />
    </div>
  );
}
