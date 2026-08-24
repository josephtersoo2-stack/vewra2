import React, { useState, useEffect } from 'react';
import {
  Zap,
  Award,
  Sparkles,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Clock,
  CheckSquare,
  Flame,
  PieChart,
  Users,
  Calculator,
  ShieldAlert,
} from 'lucide-react';
import { adminApi } from '../api/adminApi';
import { Badge } from '../components/ui/Badge';

export function XPSettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [settings, setSettings] = useState({
    xp_per_minute_watched: 10,
    xp_for_completing_task: 50,
    xp_for_daily_streak: 15,
    xp_for_daily_spin: 15,
    xp_for_referral: 100,
  });

  const [simLevel, setSimLevel] = useState(10);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const data = await adminApi.getXPSettings();
      if (data) {
        setSettings({
          xp_per_minute_watched: Number(data.xp_per_minute_watched) || 10,
          xp_for_completing_task: Number(data.xp_for_completing_task) || 50,
          xp_for_daily_streak: Number(data.xp_for_daily_streak) || 15,
          xp_for_daily_spin: Number(data.xp_for_daily_spin) || 15,
          xp_for_referral: Number(data.xp_for_referral) || 100,
        });
      }
    } catch (err) {
      console.error('Failed to load XP settings:', err);
      setErrorMessage('Unable to load XP settings from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    const num = Math.max(0, parseInt(value, 10) || 0);
    setSettings((prev) => ({ ...prev, [field]: num }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveSuccess(false);
    setErrorMessage('');
    try {
      await adminApi.updateXPSettings(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error('Failed to save XP settings:', err);
      setErrorMessage(err?.response?.data?.detail || 'Failed to save settings. Please verify inputs.');
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setSettings({
      xp_per_minute_watched: 10,
      xp_for_completing_task: 50,
      xp_for_daily_streak: 15,
      xp_for_daily_spin: 15,
      xp_for_referral: 100,
    });
  };

  // Level formula: required_xp = (level ** 2) * 20
  const calculateXPForLevel = (lvl) => (lvl ** 2) * 20;

  const milestones = [
    { level: 1, xp: 0, title: 'Newbie', perk: 'Baseline access to video earning tasks' },
    { level: 5, xp: 500, title: 'Apprentice', perk: 'Unlock: Basic Badge Showcase Slot' },
    { level: 10, xp: 2000, title: 'Coin Collector', perk: 'Unlock: Coin Shop & Discount Vouchers' },
    { level: 20, xp: 8000, title: 'Squad Commander', perk: 'Unlock: Guild Creation & Squad Bonuses' },
    { level: 30, xp: 18000, title: 'Elite Viewer', perk: 'Unlock: High-Yield Premium Tasks' },
    { level: 50, xp: 50000, title: 'Master Curator', perk: 'Unlock: Creator Analytics Dashboard' },
    { level: 75, xp: 112500, title: 'Vewra Legend', perk: 'Unlock: 2nd Showcase Slot & VIP Flair' },
    { level: 100, xp: 200000, title: 'Prestige Immortal', perk: 'Unlock: Prestige Reset & Crown Frame' },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-slate-900/40 border border-indigo-500/20 rounded-2xl p-6 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Zap className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">XP & Leveling Engine</h1>
            <Badge variant="indigo">Phase 1.3 Active</Badge>
          </div>
          <p className="text-sm text-slate-400">
            Configure dynamic platform action XP rewards, live formula progression, and account tier ladder.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleResetDefaults}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
          >
            <RotateCcw className="w-4 h-4" />
            Reset Defaults
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold shadow-lg shadow-indigo-500/25 transition disabled:opacity-50"
          >
            {saving ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* Alerts */}
      {saveSuccess && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 animate-fadeIn">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm font-medium">XP Settings saved successfully! Changes are applied instantly.</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 animate-fadeIn">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm font-medium">{errorMessage}</span>
        </div>
      )}

      {/* XP Action Reward Configuration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Watch Time XP */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden group hover:border-indigo-500/40 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Clock className="w-5 h-5" />
            </div>
            <Badge variant="blue">Watch Time</Badge>
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">XP per Minute Watched</h3>
          <p className="text-xs text-slate-400 mb-6">
            Awarded for every 60 seconds of verified video playback.
          </p>
          <div className="relative">
            <input
              type="number"
              min="1"
              max="500"
              value={settings.xp_per_minute_watched}
              onChange={(e) => handleChange('xp_per_minute_watched', e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-lg font-bold text-white focus:outline-none focus:border-indigo-500 transition"
            />
            <span className="absolute right-4 top-3.5 text-xs font-semibold text-slate-400">XP / MIN</span>
          </div>
        </div>

        {/* Task Completion Bonus */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden group hover:border-emerald-500/40 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckSquare className="w-5 h-5" />
            </div>
            <Badge variant="emerald">Bonus XP</Badge>
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Task Completion Bonus</h3>
          <p className="text-xs text-slate-400 mb-6">
            Bonus XP awarded when a user completes a video task requirement.
          </p>
          <div className="relative">
            <input
              type="number"
              min="0"
              max="1000"
              value={settings.xp_for_completing_task}
              onChange={(e) => handleChange('xp_for_completing_task', e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-lg font-bold text-white focus:outline-none focus:border-emerald-500 transition"
            />
            <span className="absolute right-4 top-3.5 text-xs font-semibold text-slate-400">XP / TASK</span>
          </div>
        </div>

        {/* Daily Streak XP */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden group hover:border-amber-500/40 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Flame className="w-5 h-5" />
            </div>
            <Badge variant="amber">Daily Streak</Badge>
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Daily Streak Login XP</h3>
          <p className="text-xs text-slate-400 mb-6">
            XP rewarded each day when a user claims their daily login streak bonus.
          </p>
          <div className="relative">
            <input
              type="number"
              min="0"
              max="500"
              value={settings.xp_for_daily_streak}
              onChange={(e) => handleChange('xp_for_daily_streak', e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-lg font-bold text-white focus:outline-none focus:border-amber-500 transition"
            />
            <span className="absolute right-4 top-3.5 text-xs font-semibold text-slate-400">XP / CLAIM</span>
          </div>
        </div>

        {/* Daily Spin Wheel XP */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden group hover:border-purple-500/40 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <PieChart className="w-5 h-5" />
            </div>
            <Badge variant="purple">Spin Wheel</Badge>
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Daily Spin Wheel XP</h3>
          <p className="text-xs text-slate-400 mb-6">
            XP awarded upon spinning the Lucky Wheel.
          </p>
          <div className="relative">
            <input
              type="number"
              min="0"
              max="500"
              value={settings.xp_for_daily_spin}
              onChange={(e) => handleChange('xp_for_daily_spin', e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-lg font-bold text-white focus:outline-none focus:border-purple-500 transition"
            />
            <span className="absolute right-4 top-3.5 text-xs font-semibold text-slate-400">XP / SPIN</span>
          </div>
        </div>

        {/* Referral XP */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm relative overflow-hidden group hover:border-pink-500/40 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
              <Users className="w-5 h-5" />
            </div>
            <Badge variant="pink">Referral</Badge>
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Referral Signup XP</h3>
          <p className="text-xs text-slate-400 mb-6">
            XP awarded to referrer when an invited user joins and earns.
          </p>
          <div className="relative">
            <input
              type="number"
              min="0"
              max="2000"
              value={settings.xp_for_referral}
              onChange={(e) => handleChange('xp_for_referral', e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-lg font-bold text-white focus:outline-none focus:border-pink-500 transition"
            />
            <span className="absolute right-4 top-3.5 text-xs font-semibold text-slate-400">XP / REF</span>
          </div>
        </div>

        {/* Progression Formula Card */}
        <div className="bg-gradient-to-br from-indigo-950/60 via-purple-950/40 to-slate-950/80 border border-indigo-500/30 rounded-2xl p-6 backdrop-blur-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 mb-2">
              <Calculator className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-wider">Level Equation</span>
            </div>
            <h4 className="text-lg font-bold text-white mb-1 font-mono">
              XP_req(L) = L² × 20
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Quadratic progression curve guarantees early levels are fast and engaging, while prestige levels remain rare and prestigious.
            </p>
          </div>
          <div className="bg-black/40 rounded-xl p-3 border border-indigo-500/20">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Max Account Level:</span>
              <span className="font-bold text-indigo-300">Level 101</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Level Calculator & Milestone Ladder */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-indigo-400" />
              Level Progression Calculator & Milestones
            </h2>
            <p className="text-sm text-slate-400">
              Preview XP requirements and milestone unlock thresholds across levels 1–101.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400">Test Level:</span>
            <input
              type="number"
              min="1"
              max="101"
              value={simLevel}
              onChange={(e) => setSimLevel(Math.min(101, Math.max(1, parseInt(e.target.value, 10) || 1)))}
              className="w-16 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-sm font-bold text-indigo-400 text-center focus:outline-none"
            />
            <span className="text-xs font-mono font-bold text-white">
              = {calculateXPForLevel(simLevel).toLocaleString()} XP
            </span>
          </div>
        </div>

        {/* Milestone Cards Ladder */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {milestones.map((m) => {
            const isReached = simLevel >= m.level;
            return (
              <div
                key={m.level}
                className={`p-4 rounded-xl border transition ${
                  isReached
                    ? 'bg-indigo-950/40 border-indigo-500/40 text-white'
                    : 'bg-slate-950/40 border-slate-800/80 text-slate-400 opacity-70'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                    Level {m.level}
                  </span>
                  <span className="text-xs font-semibold text-slate-400">
                    {m.xp.toLocaleString()} XP
                  </span>
                </div>
                <div className="text-sm font-bold text-slate-200 mb-1">{m.title}</div>
                <div className="text-xs text-slate-400 leading-snug">{m.perk}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
