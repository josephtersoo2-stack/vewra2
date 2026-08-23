import React, { useState, useEffect } from 'react';
import {
  PieChart,
  RotateCcw,
  Plus,
  Edit2,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Coins,
  Sparkles,
  Play,
  X,
  Save,
  Check,
} from 'lucide-react';
import { adminApi } from '../api/adminApi';
import { Badge } from '../components/ui/Badge';

const PRESET_COLORS = [
  '#4F46E5', '#6366F1', '#8B5CF6', '#EC4899', '#F43F5E',
  '#EF4444', '#F59E0B', '#10B981', '#06B6D4', '#3B82F6',
  '#A855F7', '#EAB308', '#14B8A6', '#D946EF'
];

export function SpinWheelSettingsPage() {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Modal State for Add / Edit
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSegment, setEditingSegment] = useState(null);
  const [formData, setFormData] = useState({
    label: '',
    reward_coins: 10,
    weight: 10,
    color: '#6366F1',
    order: 1,
    is_active: true,
  });

  // Wheel Animation Preview
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinRotation, setSpinRotation] = useState(0);
  const [simulatedWin, setSimulatedWin] = useState(null);

  useEffect(() => {
    fetchSegments();
  }, []);

  const fetchSegments = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const data = await adminApi.getSpinWheelSegments();
      const list = Array.isArray(data) ? data : data.results || [];
      // Sort by order
      list.sort((a, b) => a.order - b.order);
      setSegments(list);
    } catch (err) {
      console.error('Failed to load spin wheel segments:', err);
      setErrorMessage('Failed to load spin wheel segments from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetDefaults = async () => {
    if (!window.confirm('Reset all wheel segments to the standard 12-segment default configuration?')) {
      return;
    }
    setActionLoading(true);
    setErrorMessage('');
    try {
      const res = await adminApi.resetSpinWheelDefaults();
      const list = res.segments || (Array.isArray(res) ? res : []);
      list.sort((a, b) => a.order - b.order);
      setSegments(list);
      showSuccess('Wheel segments reset to default 12-segment configuration successfully!');
    } catch (err) {
      console.error('Failed to reset defaults:', err);
      setErrorMessage('Failed to reset default segments.');
    } finally {
      setActionLoading(false);
    }
  };

  const openAddModal = () => {
    setEditingSegment(null);
    setFormData({
      label: '',
      reward_coins: 20,
      weight: 10,
      color: PRESET_COLORS[segments.length % PRESET_COLORS.length] || '#6366F1',
      order: segments.length + 1,
      is_active: true,
    });
    setModalOpen(true);
  };

  const openEditModal = (seg) => {
    setEditingSegment(seg);
    setFormData({
      label: seg.label,
      reward_coins: seg.reward_coins,
      weight: seg.weight,
      color: seg.color || '#6366F1',
      order: seg.order,
      is_active: seg.is_active,
    });
    setModalOpen(true);
  };

  const handleSaveSegment = async (e) => {
    e.preventDefault();
    if (!formData.label.trim()) {
      setErrorMessage('Label is required.');
      return;
    }

    setActionLoading(true);
    setErrorMessage('');

    try {
      if (editingSegment) {
        // Update existing
        const updated = await adminApi.updateSpinWheelSegment(editingSegment.id, formData);
        setSegments((prev) =>
          prev.map((s) => (s.id === editingSegment.id ? updated : s)).sort((a, b) => a.order - b.order)
        );
        showSuccess(`Segment "${updated.label}" updated successfully!`);
      } else {
        // Create new
        const created = await adminApi.createSpinWheelSegment(formData);
        setSegments((prev) => [...prev, created].sort((a, b) => a.order - b.order));
        showSuccess(`New segment "${created.label}" added successfully!`);
      }
      setModalOpen(false);
    } catch (err) {
      console.error('Failed to save segment:', err);
      setErrorMessage(err.response?.data?.detail || 'Failed to save segment details.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteSegment = async (seg) => {
    if (!window.confirm(`Delete segment "${seg.label}"?`)) {
      return;
    }
    setActionLoading(true);
    try {
      await adminApi.deleteSpinWheelSegment(seg.id);
      setSegments((prev) => prev.filter((s) => s.id !== seg.id));
      showSuccess(`Segment "${seg.label}" deleted.`);
    } catch (err) {
      console.error('Failed to delete segment:', err);
      setErrorMessage('Failed to delete segment.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleToggleActive = async (seg) => {
    try {
      const updated = await adminApi.patchSpinWheelSegment(seg.id, { is_active: !seg.is_active });
      setSegments((prev) => prev.map((s) => (s.id === seg.id ? updated : s)));
    } catch (err) {
      console.error('Failed to toggle segment status:', err);
      setErrorMessage('Failed to update segment active state.');
    }
  };

  const showSuccess = (msg) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(''), 4000);
  };

  // Test spin preview simulation
  const handleTestSpin = () => {
    if (isSpinning || segments.length === 0) return;
    setIsSpinning(true);
    setSimulatedWin(null);

    const activeSegs = segments.filter((s) => s.is_active);
    if (activeSegs.length === 0) {
      setIsSpinning(false);
      return;
    }

    // Weighted random selection
    const weights = activeSegs.map((s) => Math.max(1, s.weight));
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    let rand = Math.random() * totalWeight;
    let selected = activeSegs[0];
    for (let i = 0; i < activeSegs.length; i++) {
      if (rand < weights[i]) {
        selected = activeSegs[i];
        break;
      }
      rand -= weights[i];
    }

    // Calculate rotation angle
    const extraRounds = 5 * 360;
    const newRot = spinRotation + extraRounds + Math.floor(Math.random() * 360);
    setSpinRotation(newRot);

    setTimeout(() => {
      setIsSpinning(false);
      setSimulatedWin(selected);
    }, 3000);
  };

  // Compute conic gradient for wheel preview
  const activeSegments = segments.filter((s) => s.is_active);
  const totalWeight = activeSegments.reduce((sum, s) => sum + (s.weight || 0), 0) || 1;

  let currentDeg = 0;
  const gradientStops = activeSegments.map((s) => {
    const sliceDeg = (s.weight / totalWeight) * 360;
    const stop = `${s.color} ${currentDeg}deg ${currentDeg + sliceDeg}deg`;
    currentDeg += sliceDeg;
    return stop;
  });
  const conicGradientStyle = gradientStops.length > 0
    ? `conic-gradient(${gradientStops.join(', ')})`
    : 'conic-gradient(#6366F1 0deg 360deg)';

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
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Loading Spin Wheel Segments...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Header */}
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
              <PieChart size={20} />
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: '800', color: 'var(--text-primary)' }}>
              Daily Spin Wheel Configuration
            </h1>
          </div>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Phase 1.2: Manage dynamic wheel segments, reward payouts, colors, and weighted probability RNG.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            type="button"
            onClick={handleResetDefaults}
            disabled={actionLoading}
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
              cursor: actionLoading ? 'not-allowed' : 'pointer',
            }}
          >
            <RotateCcw size={14} />
            <span>Reset to Default 12-Segment Wheel</span>
          </button>

          <button
            type="button"
            onClick={openAddModal}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 18px',
              borderRadius: 'var(--btn-radius)',
              backgroundColor: 'var(--primary)',
              color: '#FFFFFF',
              border: 'none',
              fontSize: '14px',
              fontWeight: '700',
              cursor: 'pointer',
              boxShadow: '0 4px 12px var(--primary-glow)',
            }}
          >
            <Plus size={16} />
            <span>Add New Segment</span>
          </button>
        </div>
      </div>

      {/* Notifications */}
      {successMessage && (
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
          <span>{successMessage}</span>
        </div>
      )}

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

      {/* Interactive Wheel Preview + Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
        {/* Visual Wheel Simulator */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', position: 'relative' }}>
          <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)' }}>
              Live Wheel Preview
            </h3>
            <Badge variant="indigo">
              {activeSegments.length} Active Segments
            </Badge>
          </div>

          {/* Wheel Pointer */}
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: '12px solid transparent',
              borderRight: '12px solid transparent',
              borderTop: '20px solid #EF4444',
              marginBottom: '-10px',
              zIndex: 10,
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.4))',
            }}
          />

          {/* Wheel Container */}
          <div
            style={{
              width: '240px',
              height: '240px',
              borderRadius: '50%',
              background: conicGradientStyle,
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3), inset 0 0 0 8px rgba(255, 255, 255, 0.15)',
              transform: `rotate(${spinRotation}deg)`,
              transition: isSpinning ? 'transform 3s cubic-bezier(0.15, 0.85, 0.35, 1.05)' : 'none',
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '4px solid #FFFFFF',
            }}
          >
            {/* Center Cap */}
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                backgroundColor: 'var(--bg-secondary)',
                border: '3px solid #FFFFFF',
                boxShadow: '0 4px 10px rgba(0, 0, 0, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
                fontWeight: '800',
                fontSize: '18px',
              }}
            >
              🎰
            </div>
          </div>

          <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <button
              type="button"
              onClick={handleTestSpin}
              disabled={isSpinning}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 22px',
                borderRadius: 'var(--btn-radius)',
                backgroundColor: isSpinning ? 'var(--bg-tertiary)' : 'var(--accent-amber)',
                color: '#1E293B',
                border: 'none',
                fontSize: '13px',
                fontWeight: '800',
                cursor: isSpinning ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
              }}
            >
              <Play size={14} />
              <span>{isSpinning ? 'Spinning...' : 'Simulate Test Spin'}</span>
            </button>

            {simulatedWin && (
              <div
                style={{
                  padding: '8px 14px',
                  borderRadius: 'var(--input-radius)',
                  backgroundColor: 'var(--badge-emerald-bg)',
                  color: 'var(--badge-emerald-text)',
                  fontSize: '13px',
                  fontWeight: '700',
                }}
              >
                🎉 Landed on: <strong>{simulatedWin.label}</strong> (+{simulatedWin.reward_coins} Coins)
              </div>
            )}
          </div>
        </div>

        {/* Probability & Economy Summary */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>
              Wheel Probability Calibration
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Weights determine the relative likelihood of landing on each slice. The engine runs a server-side RNG with these exact weight distributions.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Total Weight Sum:</span>
                <strong style={{ color: 'var(--text-primary)' }}>{totalWeight} pts (100%)</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Active Slices:</span>
                <strong style={{ color: 'var(--text-primary)' }}>{activeSegments.length} / {segments.length}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Max Jackpot Reward:</span>
                <strong style={{ color: 'var(--accent-amber)' }}>
                  {Math.max(...segments.map((s) => s.reward_coins || 0), 0)} Coins
                </strong>
              </div>
            </div>
          </div>

          <div
            style={{
              padding: '14px',
              borderRadius: 'var(--input-radius)',
              backgroundColor: 'var(--bg-tertiary)',
              border: '1px solid var(--border-card)',
              fontSize: '12px',
              color: 'var(--text-secondary)',
              marginTop: '16px',
            }}
          >
            💡 <strong>Anti-Cheat Guarantee:</strong> Mobile clients only request a spin trigger. Randomness, prize selection, and wallet credits are executed 100% atomically on the backend server.
          </div>
        </div>
      </div>

      {/* Segments Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>
              Configured Wheel Segments ({segments.length})
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Click edit to modify reward coins, weights, display order, or slice colors.
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-tertiary)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700', width: '60px' }}>#</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700', width: '80px' }}>Color</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700' }}>Segment Label</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700' }}>Reward Coins</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700' }}>Weight (Odds)</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700' }}>Status</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-tertiary)', fontWeight: '700', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {segments.map((seg, idx) => {
                const probPercent = totalWeight > 0 ? ((seg.weight / totalWeight) * 100).toFixed(1) : 0;
                return (
                  <tr
                    key={seg.id || idx}
                    style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      opacity: seg.is_active ? 1 : 0.5,
                      backgroundColor: idx % 2 === 0 ? 'transparent' : 'var(--bg-secondary)',
                    }}
                  >
                    <td style={{ padding: '14px 16px', fontWeight: '800', color: 'var(--text-primary)' }}>
                      {seg.order || idx + 1}
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div
                          style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '6px',
                            backgroundColor: seg.color || '#6366F1',
                            border: '1px solid rgba(255,255,255,0.2)',
                          }}
                        />
                        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>
                          {seg.color}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px', fontWeight: '700', color: 'var(--text-primary)' }}>
                      {seg.label}
                    </td>
                    <td style={{ padding: '14px 16px', fontWeight: '800', color: 'var(--accent-amber)' }}>
                      +{seg.reward_coins} <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Coins</span>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>{seg.weight} pts</span>
                        <Badge variant="indigo" size="xs">
                          {probPercent}%
                        </Badge>
                      </div>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <button
                        type="button"
                        onClick={() => handleToggleActive(seg)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          padding: 0,
                        }}
                      >
                        {seg.is_active ? (
                          <Badge variant="emerald" size="sm">Active</Badge>
                        ) : (
                          <Badge variant="rose" size="sm">Disabled</Badge>
                        )}
                      </button>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                        <button
                          type="button"
                          onClick={() => openEditModal(seg)}
                          style={{
                            padding: '6px 10px',
                            borderRadius: '6px',
                            backgroundColor: 'var(--bg-tertiary)',
                            border: '1px solid var(--border-card)',
                            color: 'var(--text-primary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '12px',
                          }}
                        >
                          <Edit2 size={13} />
                          <span>Edit</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDeleteSegment(seg)}
                          style={{
                            padding: '6px 10px',
                            borderRadius: '6px',
                            backgroundColor: 'var(--badge-rose-bg)',
                            border: '1px solid rgba(244,63,94,0.3)',
                            color: 'var(--badge-rose-text)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '12px',
                          }}
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add / Edit Modal */}
      {modalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '16px',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '480px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--card-radius)',
              border: '1px solid var(--border-card)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                padding: '18px 24px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <h3 style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-primary)' }}>
                {editingSegment ? 'Edit Wheel Segment' : 'Add Wheel Segment'}
              </h3>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSaveSegment} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Segment Label
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 50 Coins, 1000 Coins Jackpot"
                  value={formData.label}
                  onChange={(e) => setFormData({ ...formData, label: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 'var(--input-radius)',
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-card)',
                    color: 'var(--text-primary)',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Reward Coins
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100000"
                    required
                    value={formData.reward_coins}
                    onChange={(e) => setFormData({ ...formData, reward_coins: parseInt(e.target.value, 10) || 0 })}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '14px',
                      fontWeight: '700',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Weight (Probability)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    required
                    value={formData.weight}
                    onChange={(e) => setFormData({ ...formData, weight: parseInt(e.target.value, 10) || 1 })}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '14px',
                      fontWeight: '700',
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Wheel Order (#)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="24"
                    required
                    value={formData.order}
                    onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value, 10) || 1 })}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '14px',
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '12px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Color Hex
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '14px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  />
                </div>
              </div>

              {/* Quick Color Picker */}
              <div>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: 'var(--text-tertiary)', marginBottom: '8px' }}>
                  Quick Color Palette
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {PRESET_COLORS.map((c) => (
                    <button
                      key={c}
                      type="button"
                      onClick={() => setFormData({ ...formData, color: c })}
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        backgroundColor: c,
                        border: formData.color === c ? '2px solid #FFFFFF' : '1px solid transparent',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {formData.color === c && <Check size={14} color="#FFFFFF" />}
                    </button>
                  ))}
                </div>
              </div>

              {/* Active Toggle */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
                <input
                  type="checkbox"
                  id="seg_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                />
                <label htmlFor="seg_active" style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', cursor: 'pointer' }}>
                  Enable this segment on the live wheel
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '12px' }}>
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  style={{
                    padding: '10px 16px',
                    borderRadius: 'var(--btn-radius)',
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-card)',
                    color: 'var(--text-secondary)',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  style={{
                    padding: '10px 20px',
                    borderRadius: 'var(--btn-radius)',
                    backgroundColor: 'var(--primary)',
                    color: '#FFFFFF',
                    border: 'none',
                    fontWeight: '700',
                    cursor: actionLoading ? 'not-allowed' : 'pointer',
                  }}
                >
                  {actionLoading ? 'Saving...' : editingSegment ? 'Update Segment' : 'Add Segment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default SpinWheelSettingsPage;
