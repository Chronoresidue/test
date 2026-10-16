import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Award, Flame, CheckCircle2, XCircle, Sparkles, 
  ShieldCheck, HelpCircle, ArrowRight
} from 'lucide-react';

export default function GamificationHub({ currentUser }) {
  const [challenge, setChallenge] = useState(null);
  const [streak, setStreak] = useState(null);
  const [badges, setBadges] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadGamification = async () => {
    try {
      setLoading(true);
      const [ch, st, bd] = await Promise.all([
        api.getDailyChallenge(),
        api.getStreak(),
        api.getBadges(),
      ]);
      setChallenge(ch);
      setStreak(st);
      setBadges(bd);
    } catch (err) {
      console.error("Error loading challenge:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGamification();
  }, [currentUser]);

  const handleSubmitChallenge = async () => {
    if (selectedIndex === null) return;
    try {
      setSubmitting(true);
      const res = await api.submitDailyChallenge(selectedIndex);
      setResult(res);
      // Reload streak and badges
      const [st, bd] = await Promise.all([api.getStreak(), api.getBadges()]);
      setStreak(st);
      setBadges(bd);
    } catch (err) {
      alert("Error submitting challenge: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-sm text-secondary animate-pulse">
        Loading today's skill challenge and streak data...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header & Honest Gamification Note */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-gold-light text-gold font-medium">
              Daily Challenge & Streaks
            </span>
            <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-canvas border border-border text-secondary">
              Part 13 System
            </span>
          </div>
          <h1 className="font-display font-bold text-2xl sm:text-3xl text-ink">
            Skill Growth & Honest Engagement
          </h1>
          <p className="text-secondary text-xs sm:text-sm max-w-xl mt-1">
            Build steady practice habits. TeamWeave rewards active participation honestly without falsely equating streaks with technical superiority.
          </p>
        </div>

        {/* Streak Counter Card */}
        <div className="p-4 rounded-xl border border-border bg-canvas/40 flex items-center gap-4 shrink-0 shadow-sm">
          <div className="w-12 h-12 rounded-xl bg-gold-light flex items-center justify-center text-gold">
            <Flame className="w-7 h-7 text-gold animate-bounce" />
          </div>
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-secondary">Current Streak</div>
            <div className="font-display font-bold text-2xl text-ink">
              {streak?.current_streak || 0} <span className="text-sm font-sans font-normal text-muted">days</span>
            </div>
            <div className="text-[10px] text-muted">
              Longest: {streak?.longest_streak || 0} days · Total: {streak?.total_completions || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Daily Challenge Card */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper space-y-6">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-teal-brand" />
            <span className="font-display font-semibold text-sm text-ink">
              Today's Daily Challenge
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-teal-mint text-teal-dark font-medium">
              Category: {challenge?.skill_category}
            </span>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-canvas border border-border text-secondary">
              Difficulty: {challenge?.difficulty}
            </span>
          </div>
        </div>

        {/* Question */}
        <div className="font-display font-bold text-lg text-ink leading-snug">
          {challenge?.question}
        </div>

        {/* Options */}
        <div className="space-y-3">
          {challenge?.options && challenge.options.map((opt, idx) => {
            const isSelected = selectedIndex === idx;
            let btnStyle = "border-border bg-canvas/30 text-ink hover:border-teal-brand/40 hover:bg-canvas";
            
            if (result) {
              if (idx === result.correct_index) {
                btnStyle = "border-teal-brand bg-teal-mint/70 text-teal-dark font-semibold";
              } else if (isSelected && !result.is_correct) {
                btnStyle = "border-coral bg-coral-light/70 text-coral font-semibold";
              }
            } else if (isSelected) {
              btnStyle = "border-teal-brand bg-teal-mint/30 text-teal-dark font-semibold ring-1 ring-teal-brand";
            }

            return (
              <button
                key={idx}
                disabled={result !== null || challenge?.already_completed}
                onClick={() => setSelectedIndex(idx)}
                className={`w-full text-left p-3.5 rounded-xl border text-xs sm:text-sm transition-all flex items-center justify-between gap-3 ${btnStyle}`}
              >
                <span>{opt}</span>
                {result && idx === result.correct_index && (
                  <CheckCircle2 className="w-4 h-4 text-teal-brand shrink-0" />
                )}
                {result && isSelected && !result.is_correct && (
                  <XCircle className="w-4 h-4 text-coral shrink-0" />
                )}
              </button>
            );
          })}
        </div>

        {/* Submit or Result Explanation */}
        {!result && !challenge?.already_completed ? (
          <div className="pt-2 flex justify-end">
            <button
              onClick={handleSubmitChallenge}
              disabled={selectedIndex === null || submitting}
              className="px-6 py-2.5 rounded-xl bg-teal-brand hover:bg-teal-dark text-surface text-xs font-semibold transition-colors disabled:opacity-50 shadow-sm flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {submitting ? "Evaluating..." : "Submit Answer"}
            </button>
          </div>
        ) : (
          <div className="p-4 rounded-xl border border-border bg-canvas/40 text-xs text-secondary space-y-1">
            <div className="font-semibold text-ink flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-teal-brand" />
              {result?.is_correct ? "Correct Answer! Streak incremented." : "Knowledge Explanation:"}
            </div>
            <p className="leading-relaxed">
              {result?.explanation || "Challenge completed for today. Check back tomorrow for the next capability quiz!"}
            </p>
          </div>
        )}
      </div>

      {/* Honest Badges Showcase */}
      <div className="p-6 rounded-2xl border border-border bg-surface shadow-paper space-y-4">
        <div>
          <h2 className="font-display font-bold text-lg text-ink">
            Milestone Badges ({badges.filter(b => b.earned_at).length} / {badges.length} Unlocked)
          </h2>
          <p className="text-secondary text-xs">
            Earned through honest consistency and skill declarations.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {badges.map((b) => {
            const isEarned = Boolean(b.earned_at);
            return (
              <div 
                key={b.id}
                className={`p-4 rounded-xl border transition-all text-xs flex flex-col justify-between ${
                  isEarned 
                    ? 'border-teal-brand/40 bg-teal-mint/20 shadow-sm' 
                    : 'border-border bg-canvas/20 opacity-60'
                }`}
              >
                <div>
                  <div className="w-8 h-8 rounded-lg bg-surface border border-border flex items-center justify-center mb-3">
                    <Award className={`w-4 h-4 ${isEarned ? 'text-teal-brand' : 'text-muted'}`} />
                  </div>
                  <div className="font-semibold text-ink text-sm mb-1">{b.name}</div>
                  <div className="text-[11px] text-secondary leading-snug">{b.description}</div>
                </div>

                <div className="mt-4 pt-2 border-t border-border/60 text-[10px] font-mono">
                  {isEarned ? (
                    <span className="text-teal-dark font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-teal-brand" />
                      Unlocked
                    </span>
                  ) : (
                    <span className="text-muted">In Progress</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
