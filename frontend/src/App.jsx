import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import OrganizerStudio from './pages/OrganizerStudio';
import ParticipantDashboard from './pages/ParticipantDashboard';
import GamificationHub from './pages/GamificationHub';
import MyTeamView from './pages/MyTeamView';
import EventsPage from './pages/EventsPage';
import { api, setToken, getToken } from './api';
import { Compass, Sparkles, Heart } from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState("landing");
  const [loading, setLoading] = useState(true);

  // Initialize with demo user if no token exists
  useEffect(() => {
    async function initUser() {
      try {
        setLoading(true);
        if (!getToken()) {
          // Auto login as default organizer for frictionless hackathon judge experience
          const res = await api.login({ email: "organizer@teamweave.dev", password: "password123" });
          setToken(res.access_token);
          setCurrentUser(res.user);
        } else {
          try {
            const me = await api.getMe();
            setCurrentUser(me);
          } catch (e) {
            // Token expired or invalid, re-login demo user
            const res = await api.login({ email: "organizer@teamweave.dev", password: "password123" });
            setToken(res.access_token);
            setCurrentUser(res.user);
          }
        }
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setLoading(false);
      }
    }
    initUser();
  }, []);

  const handleSelectDemoRole = async (email, targetTab) => {
    try {
      setLoading(true);
      const res = await api.login({ email, password: "password123" });
      setToken(res.access_token);
      setCurrentUser(res.user);
      setActiveTab(targetTab);
    } catch (err) {
      alert("Error switching demo role: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col font-sans selection:bg-teal-mint selection:text-ink">
      
      {/* Signature Living Weave Navigation Bar */}
      <Navbar
        currentUser={currentUser}
        onUserChange={setCurrentUser}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {loading ? (
          <div className="max-w-4xl mx-auto px-4 py-20 text-center text-sm text-secondary animate-pulse">
            Connecting to Living Weave Engine...
          </div>
        ) : (
          <>
            {activeTab === "landing" && (
              <LandingPage
                onSelectDemoRole={handleSelectDemoRole}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === "events" && (
              <EventsPage
                currentUser={currentUser}
                onNavigateToOrganizer={() => setActiveTab("organizer")}
              />
            )}

            {activeTab === "organizer" && (
              <OrganizerStudio eventId={1} />
            )}

            {activeTab === "profile" && (
              <ParticipantDashboard
                currentUser={currentUser}
                onUserUpdate={setCurrentUser}
              />
            )}

            {activeTab === "gamification" && (
              <GamificationHub currentUser={currentUser} />
            )}

            {activeTab === "myteam" && (
              <MyTeamView currentUser={currentUser} />
            )}
          </>
        )}
      </main>

      {/* Footer with Editorial Typography */}
      <footer className="border-t border-border bg-surface py-8 text-xs text-secondary mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-ink">TeamWeave</span>
            <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-teal-mint text-teal-dark border border-teal-brand/20">
              Living Weave 2026
            </span>
            <span className="text-muted">·</span>
            <span className="text-[11px] text-muted">Python FastAPI + React + Vite + Tailwind CSS</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-secondary">Explainable Matchmaking</span>
            <span>·</span>
            <span className="text-secondary">4-Level Capability Matrix</span>
            <span>·</span>
            <span className="text-secondary">Resilient Reshuffling</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
