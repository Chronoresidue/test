import React, { useState } from 'react';
import { api, setToken } from '../api';
import { 
  Users, Award, Sparkles, UserCheck, ShieldCheck, 
  RefreshCw, LogOut, ChevronDown, Check, Compass, Cpu
} from 'lucide-react';

export default function Navbar({ currentUser, onUserChange, activeTab, setActiveTab }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const demoAccounts = [
    { email: "organizer@teamweave.dev", name: "Dr. Aarav Patel", role: "organizer", label: "Organizer View" },
    { email: "maya@teamweave.dev", name: "Maya Sharma", role: "participant", label: "Frontend Specialist" },
    { email: "rohan@teamweave.dev", name: "Rohan Deshmukh", role: "participant", label: "Backend Specialist" },
    { email: "priya@teamweave.dev", name: "Priya Nair", role: "participant", label: "AI/ML Researcher" },
    { email: "ananya@teamweave.dev", name: "Ananya Sen", role: "participant", label: "UI/UX Designer" },
  ];

  const handleSwitchUser = async (email) => {
    try {
      setLoadingDemo(true);
      const res = await api.login({ email, password: "password123" });
      setToken(res.access_token);
      onUserChange(res.user);
      setDropdownOpen(false);
    } catch (err) {
      alert("Failed to switch demo user: " + err.message);
    } finally {
      setLoadingDemo(false);
    }
  };

  const handleResetSeed = async () => {
    try {
      setLoadingDemo(true);
      await api.seedDemo();
      alert("Demonstration database reset and seeded successfully!");
      // Switch back to organizer
      handleSwitchUser("organizer@teamweave.dev");
    } catch (err) {
      alert("Seed note: " + err.message);
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-surface/95 backdrop-blur-md border-b border-border shadow-paper">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand & Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab("landing")}>
            <div className="relative w-9 h-9 rounded-lg bg-ink flex items-center justify-center shadow-md">
              {/* Signature Living Weave SVG Emblem */}
              <svg className="w-6 h-6" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="13" stroke="#17A982" strokeWidth="1.5" strokeDasharray="3 3" opacity="0.6" />
                <path d="M9 16 C9 10, 23 10, 23 16 C23 22, 9 22, 9 16 Z" stroke="#17A982" strokeWidth="2.2" strokeLinecap="round" />
                <path d="M16 9 C22 9, 22 23, 16 23 C10 23, 10 9, 16 9 Z" stroke="#536FF1" strokeWidth="2" strokeLinecap="round" opacity="0.85" />
                <circle cx="16" cy="16" r="2.5" fill="#FFFDF8" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display font-bold text-xl tracking-tight text-ink">
                  TeamWeave
                </span>
                <span className="text-[10px] font-mono uppercase tracking-widest px-1.5 py-0.5 rounded bg-teal-mint text-teal-dark font-medium border border-teal-brand/20">
                  Living Weave
                </span>
              </div>
              <p className="text-[11px] text-secondary hidden sm:block">Intelligent Skill-Based Team Formation</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActiveTab("events")}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                activeTab === "events" ? "bg-canvas text-ink font-semibold border border-border" : "text-secondary hover:text-ink hover:bg-canvas/60"
              }`}
            >
              Events
            </button>

            {currentUser?.role === "organizer" && (
              <button
                onClick={() => setActiveTab("organizer")}
                className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1.5 transition-colors ${
                  activeTab === "organizer" ? "bg-teal-mint text-teal-dark font-semibold border border-teal-brand/30" : "text-secondary hover:text-ink hover:bg-canvas/60"
                }`}
              >
                <Cpu className="w-3.5 h-3.5 text-teal-brand" />
                Organizer Studio
              </button>
            )}

            {currentUser && (
              <>
                <button
                  onClick={() => setActiveTab("profile")}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    activeTab === "profile" ? "bg-canvas text-ink font-semibold border border-border" : "text-secondary hover:text-ink hover:bg-canvas/60"
                  }`}
                >
                  My Skills & Evidence
                </button>

                <button
                  onClick={() => setActiveTab("gamification")}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1 transition-colors ${
                    activeTab === "gamification" ? "bg-canvas text-ink font-semibold border border-border" : "text-secondary hover:text-ink hover:bg-canvas/60"
                  }`}
                >
                  <Award className="w-3.5 h-3.5 text-gold" />
                  Daily Challenge
                </button>

                <button
                  onClick={() => setActiveTab("myteam")}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1 transition-colors ${
                    activeTab === "myteam" ? "bg-canvas text-ink font-semibold border border-border" : "text-secondary hover:text-ink hover:bg-canvas/60"
                  }`}
                >
                  <Users className="w-3.5 h-3.5 text-cobalt" />
                  My Team Blueprint
                </button>
              </>
            )}
          </nav>

          {/* Quick Demo Switcher & Profile Dropdown */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-canvas hover:bg-surface text-ink text-xs transition-all shadow-sm"
              >
                <div className={`w-2 h-2 rounded-full ${currentUser?.role === 'organizer' ? 'bg-teal-brand ring-2 ring-teal-mint' : 'bg-cobalt ring-2 ring-cobalt-light'}`} />
                <span className="font-medium max-w-[120px] truncate">
                  {currentUser ? currentUser.full_name : "Select Demo Persona"}
                </span>
                <span className="text-[10px] px-1 rounded bg-border text-secondary uppercase font-mono">
                  {currentUser?.role || "Guest"}
                </span>
                <ChevronDown className="w-3.5 h-3.5 text-muted" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-xl border border-border bg-surface p-2 shadow-paper-hover z-50">
                  <div className="px-2 py-1.5 text-[10px] font-mono uppercase tracking-wider text-muted border-b border-border mb-1">
                    Quick Persona Switcher (Instant Demo)
                  </div>
                  {demoAccounts.map((acc) => {
                    const isSelected = currentUser?.email === acc.email;
                    return (
                      <button
                        key={acc.email}
                        onClick={() => handleSwitchUser(acc.email)}
                        className={`w-full text-left px-2.5 py-2 rounded-lg text-xs flex items-center justify-between transition-colors ${
                          isSelected ? "bg-teal-mint/60 text-teal-dark font-medium" : "hover:bg-canvas text-ink"
                        }`}
                      >
                        <div>
                          <div className="font-medium">{acc.name}</div>
                          <div className="text-[10px] text-muted">{acc.label}</div>
                        </div>
                        {isSelected && <Check className="w-3.5 h-3.5 text-teal-brand" />}
                      </button>
                    );
                  })}
                  
                  <div className="border-t border-border mt-1 pt-1">
                    <button
                      onClick={handleResetSeed}
                      disabled={loadingDemo}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-2 text-secondary hover:text-ink hover:bg-canvas transition-colors"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${loadingDemo ? 'animate-spin' : ''}`} />
                      Reset Demo Dataset
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
