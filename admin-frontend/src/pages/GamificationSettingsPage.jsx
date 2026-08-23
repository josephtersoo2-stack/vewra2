import React, { useState, useEffect } from 'react';
import {
  Trophy,
  Flame,
  Gift,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Coins,
  Calendar,
  Sparkles,
  Zap,
  Info,
} from 'lucide-react';
import { adminApi } from '../api/adminApi';
import { Badge } from '../components/ui/Badge';

export function GamificationSettingsPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [settings, setSettings] = useState({
    day_1_coins: 5,
    day_2_coins: 10,
    day_3_coins: 15,
    day_4_coins: 20,
    day_5_coins: 30,
    day_6_coins: 40,
    day_7_coins: 50,
    mystery_box_day: 7,
    streak_reset_days: 1,
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const data = await adminApi.getStreakSettings();
      if (data) {
        setSettings({
          day_1_coins: Number(data.day_1_coins) || 5,
          day_2_coins: Number(data.day_2_coins) || 10,
          day_3_coins: Number(data.day_3_coins) || 15,
          day_4_coins: Number(data.day_4_coins) || 20,
          day_5_coins: Number(data.day_5_coins) || 30,
          day_6_coins: Number(data.day_6_coins) || 40,
          day_7_coins: Number(data.day_7_coins) || 50,
          mystery_box_day: Number(data.mystery_box_day) || 7,
          streak_reset_days: Number(data.streak_reset_days) || 1,
        });
      }
    } catch (err) {
      console.error('Failed to load gamification settings:', err);
      setErrorMessage('Failed to load gamification settings from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    const num = Math.max(0, parseInt(value, 10) || 0);
    setSettings((prev) => ({
      ...prev,
      [field]: num,
    }));
    setSaveSuccess(false);
  };

  const handleSave = async (e) => {
    if (e) e.preventDefault();
    setSaving(true);
    setErrorMessage('');
    setSaveSuccess(false);

    try {
      const payload = {
        day_1_coins: settings.day_1_coins,
        day_2_coins: settings.day_2_coins,
        day_3_coins: settings.day_3_coins,
        day_4_coins: settings.day_4_coins,
        day_5_coins: settings.day_5_coins,
        day_6_coins: settings.day_6_coins,
        day_7_coins: settings.day_7_coins,
        mystery_box_day: settings.mystery_box_day,
        streak_reset_days: settings.streak_reset_days,
      };

      const updated = await adminApi.updateStreakSettings(payload);
      if (updated) {
        setSettings({
          day_1_coins: Number(updated.day_1_coins),
          day_2_coins: Number(updated.day_2_coins),
          day_3_coins: Number(updated.day_3_coins),
          day_4_coins: Number(updated.day_4_coins),
          day_5_coins: Number(updated.day_5_coins),
          day_6_coins: Number(updated.day_6_coins),
          day_7_coins: Number(updated.day_7_coins),
          mystery_box_day: Number(updated.mystery_box_day),
          streak_reset_days: Number(updated.streak_reset_days),
        });
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 4000);
      }
    } catch (err) {
      console.error('Failed to update streak settings:', err);
      setErrorMessage(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          'Failed to save gamification settings. Please verify inputs.'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setSettings({
      day_1_coins: 5,
      day_2_coins: 10,
      day_3_coins: 15,
      day_4_coins: 20,
      day_5_coins: 30,
      day_6_coins: 40,
      day_7_coins: 50,
      mystery_box_day: 7,
      streak_reset_days: 1,
    });
    setSaveSuccess(false);
  };

  const totalCycleCoins =
    (settings.day_1_coins || 0) +
    (settings.day_2_coins || 0) +
    (settings.day_3_coins || 0) +
    (settings.day_4_coins || 0) +
    (settings.day_5_coins || 0) +
    (settings.day_6_coins || 0) +
    (settings.day_7_coins || 0);

  if (loading) {
    return (
      <div style={{ padding: '48px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            border: '3px solid var(--border-subtle)',
            borderTopColor: 'var(--primary)',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Loading Gamification Settings...</p>
      </div>
    );
  }

  const daysConfig = [
    { key: 'day_1_coins', day: 1, label: 'Day 1' },
    { key: 'day_2_coins', day: 2, label: 'Day 2' },
    { key: 'day_3_coins', day: 3, label: 'Day 3' },
    { key: 'day_4_coins', day: 4, label: 'Day 4' },
    { key: 'day_5_coins', day: 5, label: 'Day 5' },
    { key: 'day_6_coins', day: 6, label: 'Day 6' },
    { key: 'day_7_coins', day: 7, label: 'Day 7 (Grand Prize)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: 'var(--primary-light)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
              }}
            >
              <Trophy size={20} />
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)' }}>
              Gamification & Daily Streak
            </h1>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Phase 1.1: Configure daily login calendar rewards, mystery box triggers, and reset rules in real time.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            type="button"
            onClick={handleResetDefaults}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 16px',
              borderRadius: 'var(--btn-radius)',
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-secondary)',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={14} />
            <span>Reset Defaults</span>
          </button>

          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 22px',
              borderRadius: 'var(--btn-radius)',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              fontSize: '14px',
              fontWeight: '700',
              cursor: saving ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px var(--primary-glow)',
            }}
          >
            <Save size={16} />
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>

      {/* Success Notification */}
      {saveSuccess && (
        <div
          style={{
            padding: '14px 18px',
            borderRadius: 'var(--btn-radius)',
            backgroundColor: 'var(--badge-emerald-bg)',
            color: 'var(--badge-emerald-text)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '14px',
            fontWeight: '600',
          }}
        >
          <CheckCircle2 size={18} />
          <span>Gamification settings saved successfully! All user streak calculations are now live.</span>
        </div>
      )}

      {/* Error Notification */}
      {errorMessage && (
        <div
          style={{
            padding: '14px 18px',
            borderRadius: 'var(--btn-radius)',
            backgroundColor: 'var(--badge-rose-bg)',
            color: 'var(--badge-rose-text)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '14px',
            fontWeight: '600',
          }}
        >
          <AlertCircle size={18} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: 'var(--badge-amber-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--badge-amber-text)',
            }}
          >
            <Coins size={24} />
          </div>
          <div>
            <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: '600', textTransform: 'uppercase' }}>
              Full 7-Day Cycle Pool
            </p>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '2px' }}>
              +{totalCycleCoins} <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>Coins</span>
            </h3>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: 'var(--badge-indigo-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--badge-indigo-text)',
            }}
          >
            <Gift size={24} />
          </div>
          <div>
            <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: '600', textTransform: 'uppercase' }}>
              Mystery Box Trigger
            </p>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '2px' }}>
              Day {settings.mystery_box_day}
            </h3>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '12px',
              backgroundColor: 'var(--badge-rose-bg)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--badge-rose-text)',
            }}
          >
            <Flame size={24} />
          </div>
          <div>
            <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: '600', textTransform: 'uppercase' }}>
              Reset Threshold
            </p>
            <h3 style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', marginTop: '2px' }}>
              {settings.streak_reset_days} {settings.streak_reset_days === 1 ? 'Missed Day' : 'Missed Days'}
            </h3>
          </div>
        </div>
      </div>

      {/* Main Configuration Card: 7-Day Rewards */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>
              7-Day Daily Login Coin Schedule
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Specify the exact coin amount credited to user wallets for each consecutive day logged in.
            </p>
          </div>
          <Badge variant="indigo" size="md">
            <Calendar size={14} /> 7-Day Dynamic Calendar
          </Badge>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
          {daysConfig.map((item) => {
            const isMysteryDay = item.day === settings.mystery_box_day;
            const currentCoins = settings[item.key];

            return (
              <div
                key={item.key}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--input-radius)',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: isMysteryDay ? '2px solid var(--primary)' : '1px solid var(--border-card)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {isMysteryDay && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '8px',
                      right: '8px',
                    }}
                  >
                    <Badge variant="indigo" size="xs">
                      🎁 Mystery Box
                    </Badge>
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '8px',
                      backgroundColor: 'var(--primary-light)',
                      color: 'var(--primary)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: '800',
                      fontSize: '12px',
                    }}
                  >
                    D{item.day}
                  </div>
                  <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                    {item.label}
                  </span>
                </div>

                <div>
                  <label
                    style={{
                      display: 'block',
                      fontSize: '11px',
                      fontWeight: '600',
                      color: 'var(--text-tertiary)',
                      textTransform: 'uppercase',
                      marginBottom: '6px',
                    }}
                  >
                    Reward Coins
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="number"
                      min="0"
                      max="10000"
                      value={currentCoins}
                      onChange={(e) => handleInputChange(item.key, e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        borderRadius: 'var(--input-radius)',
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-card)',
                        color: 'var(--text-primary)',
                        fontSize: '15px',
                        fontWeight: '700',
                      }}
                    />
                    <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: '600' }}>c</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Rules & Triggers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
        {/* Mystery Box & Reset Rules */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Sparkles size={20} style={{ color: 'var(--primary)' }} />
            <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)' }}>
              Triggers & Reset Thresholds
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '700',
                  color: 'var(--text-primary)',
                  marginBottom: '4px',
                }}
              >
                Mystery Box Trigger Day
              </label>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                Which day in the consecutive 7-day cycle unlocks the Mystery Box bonus on top of coin rewards.
              </p>
              <select
                value={settings.mystery_box_day}
                onChange={(e) => handleInputChange('mystery_box_day', e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--input-radius)',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-card)',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  fontWeight: '600',
                }}
              >
                {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                  <option key={d} value={d}>
                    Day {d} {d === 7 ? '(Recommended Grand Prize)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '700',
                  color: 'var(--text-primary)',
                  marginBottom: '4px',
                }}
              >
                Streak Reset Threshold (Missed Days)
              </label>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                How many missed consecutive days causes a user's streak to reset back to Day 1 (default: 1 day).
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="number"
                  min="1"
                  max="14"
                  value={settings.streak_reset_days}
                  onChange={(e) => handleInputChange('streak_reset_days', e.target.value)}
                  style={{
                    width: '120px',
                    padding: '10px 14px',
                    borderRadius: 'var(--input-radius)',
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-card)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                    fontWeight: '700',
                  }}
                />
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {settings.streak_reset_days === 1 ? 'day missed before reset' : 'days missed before reset'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Live Mobile UI Preview */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <Zap size={20} style={{ color: 'var(--accent-amber)' }} />
            <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)' }}>
              Live Mobile App Calendar Preview
            </h3>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Real-time preview of how the daily streak calendar displays to users in the mobile app.
          </p>

          <div
            style={{
              padding: '16px',
              borderRadius: 'var(--input-radius)',
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border-card)',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                🔥 7-Day Login Streak
              </span>
              <Badge variant="amber" size="xs">
                +{totalCycleCoins} Total Coins
              </Badge>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '6px' }}>
              {daysConfig.map((item) => {
                const isMystery = item.day === settings.mystery_box_day;
                return (
                  <div
                    key={item.day}
                    style={{
                      padding: '8px 4px',
                      borderRadius: '8px',
                      backgroundColor: item.day === 1 ? 'var(--primary-light)' : 'var(--bg-secondary)',
                      border: item.day === 1 ? '1px solid var(--primary)' : '1px solid var(--border-card)',
                      textAlign: 'center',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <span style={{ fontSize: '10px', fontWeight: '600', color: 'var(--text-tertiary)' }}>
                      D{item.day}
                    </span>
                    <span style={{ fontSize: '14px' }}>{isMystery ? '🎁' : '🪙'}</span>
                    <span style={{ fontSize: '11px', fontWeight: '800', color: 'var(--text-primary)' }}>
                      +{settings[item.key]}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GamificationSettingsPage;
