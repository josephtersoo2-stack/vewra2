import React, { useState, useEffect } from 'react';
import {
  Award,
  Plus,
  Search,
  Filter,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Edit2,
  Trash2,
  Eye,
  EyeOff,
  Sparkles,
  Shield,
  Clock,
  Coins,
  Flame,
  Users,
  Compass,
  Trophy,
} from 'lucide-react';
import { adminApi } from '../api/adminApi';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';

export function BadgesManagementPage() {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Modal State for Add / Edit
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalBadge, setModalBadge] = useState(null);

  const categories = [
    { key: 'all', label: 'All Badges' },
    { key: 'onboarding', label: 'Onboarding' },
    { key: 'watch', label: 'Watch & Retention' },
    { key: 'social', label: 'Social & Referral' },
    { key: 'earning', label: 'Earning & Economy' },
    { key: 'special', label: 'Special & Milestones' },
  ];

  useEffect(() => {
    fetchBadges();
  }, []);

  const fetchBadges = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      let data = await adminApi.getBadges();
      if (!data || data.length === 0) {
        // Seed defaults if empty
        const seedRes = await adminApi.seedDefaultBadges();
        data = seedRes.badges || [];
      }
      setBadges(data);
    } catch (err) {
      console.error('Failed to load badges:', err);
      setErrorMessage('Unable to load badges from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenEdit = (badge) => {
    setModalBadge({ ...badge });
    setIsModalOpen(true);
  };

  const handleOpenCreate = () => {
    setModalBadge({
      key: '',
      name: '',
      description: '',
      category: 'watch',
      icon_url: '',
      is_hidden: false,
      target_bronze: 10,
      target_silver: 50,
      target_gold: 250,
      target_diamond: 1000,
    });
    setIsModalOpen(true);
  };

  const handleSaveModal = async () => {
    if (!modalBadge.key || !modalBadge.name) {
      alert('Key and Name are required.');
      return;
    }

    setSaving(true);
    try {
      if (modalBadge.id) {
        // Update
        const updated = await adminApi.updateBadge(modalBadge.id, modalBadge);
        setBadges((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
      } else {
        // Create
        const created = await adminApi.createBadge(modalBadge);
        setBadges((prev) => [...prev, created]);
      }
      setIsModalOpen(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save badge:', err);
      alert(err?.response?.data?.detail || 'Failed to save badge.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteBadge = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete badge "${name}"?`)) return;
    try {
      await adminApi.deleteBadge(id);
      setBadges((prev) => prev.filter((b) => b.id !== id));
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to delete badge:', err);
      alert('Failed to delete badge.');
    }
  };

  const handleSeedDefaults = async () => {
    if (!window.confirm('Reset/seed default badges system?')) return;
    setLoading(true);
    try {
      const res = await adminApi.seedDefaultBadges();
      if (res?.badges) {
        setBadges(res.badges);
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Failed to seed badges:', err);
      alert('Failed to seed default badges.');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryBadgeVariant = (cat) => {
    switch (cat) {
      case 'onboarding':
        return 'emerald';
      case 'watch':
        return 'blue';
      case 'social':
        return 'purple';
      case 'earning':
        return 'amber';
      case 'special':
        return 'rose';
      default:
        return 'slate';
    }
  };

  const filteredBadges = badges.filter((b) => {
    const matchesCat = selectedCategory === 'all' || b.category === selectedCategory;
    const matchesSearch =
      b.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-purple-900/40 via-indigo-900/30 to-slate-900/40 border border-purple-500/20 rounded-2xl p-6 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Award className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Badges & Achievements</h1>
            <Badge variant="purple">{badges.length} Badges Configured</Badge>
          </div>
          <p className="text-sm text-slate-400">
            Configure multi-tier achievement thresholds (Bronze, Silver, Gold, Diamond) across platform actions.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSeedDefaults}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
          >
            <RotateCcw className="w-4 h-4" />
            Seed Defaults
          </button>
          <button
            onClick={handleOpenCreate}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-lg shadow-purple-500/25 transition"
          >
            <Plus className="w-4 h-4" />
            New Badge
          </button>
        </div>
      </div>

      {/* Alerts */}
      {saveSuccess && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 animate-fadeIn">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm font-medium">Badge changes saved successfully!</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 animate-fadeIn">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span className="text-sm font-medium">{errorMessage}</span>
        </div>
      )}

      {/* Search & Category Filter Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Category Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat.key}
              onClick={() => setSelectedCategory(cat.key)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
                selectedCategory === cat.key
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/20'
                  : 'bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search badges..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-purple-500 transition"
          />
        </div>
      </div>

      {/* Badges Table */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl overflow-hidden backdrop-blur-sm shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="py-4 px-6">Badge Details</th>
                <th className="py-4 px-4">Category</th>
                <th className="py-4 px-4 text-center">
                  <span className="px-2 py-1 rounded bg-amber-900/30 text-amber-300 border border-amber-500/30">
                    🥉 Bronze
                  </span>
                </th>
                <th className="py-4 px-4 text-center">
                  <span className="px-2 py-1 rounded bg-slate-800/80 text-slate-200 border border-slate-600/30">
                    🥈 Silver
                  </span>
                </th>
                <th className="py-4 px-4 text-center">
                  <span className="px-2 py-1 rounded bg-yellow-900/30 text-yellow-300 border border-yellow-500/30">
                    🥇 Gold
                  </span>
                </th>
                <th className="py-4 px-4 text-center">
                  <span className="px-2 py-1 rounded bg-cyan-900/30 text-cyan-300 border border-cyan-500/30">
                    💎 Diamond
                  </span>
                </th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60">
              {filteredBadges.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-12 text-slate-500">
                    No badges match your filter criteria.
                  </td>
                </tr>
              ) : (
                filteredBadges.map((badge) => (
                  <tr key={badge.id} className="hover:bg-slate-800/30 transition group">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                          <Trophy className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-white group-hover:text-purple-300 transition">
                            {badge.name}
                          </div>
                          <div className="text-xs text-slate-400 font-mono">{badge.key}</div>
                          <div className="text-xs text-slate-400 mt-0.5 line-clamp-1">
                            {badge.description}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="py-4 px-4">
                      <Badge variant={getCategoryBadgeVariant(badge.category)}>
                        {badge.category}
                      </Badge>
                    </td>

                    <td className="py-4 px-4 text-center font-mono font-bold text-amber-300">
                      {badge.target_bronze}
                    </td>

                    <td className="py-4 px-4 text-center font-mono font-bold text-slate-200">
                      {badge.target_silver}
                    </td>

                    <td className="py-4 px-4 text-center font-mono font-bold text-yellow-300">
                      {badge.target_gold}
                    </td>

                    <td className="py-4 px-4 text-center font-mono font-bold text-cyan-300">
                      {badge.target_diamond}
                    </td>

                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleOpenEdit(badge)}
                          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                          title="Edit thresholds"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteBadge(badge.id, badge.name)}
                          className="p-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 transition"
                          title="Delete badge"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit / Create Modal */}
      {isModalOpen && modalBadge && (
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={modalBadge.id ? `Edit Badge: ${modalBadge.name}` : 'Create New Badge'}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Badge Name</label>
                <input
                  type="text"
                  value={modalBadge.name}
                  onChange={(e) => setModalBadge({ ...modalBadge, name: e.target.value })}
                  placeholder="e.g. Master Marathoner"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Unique Key</label>
                <input
                  type="text"
                  value={modalBadge.key}
                  onChange={(e) => setModalBadge({ ...modalBadge, key: e.target.value })}
                  placeholder="e.g. master_marathoner"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Category</label>
              <select
                value={modalBadge.category}
                onChange={(e) => setModalBadge({ ...modalBadge, category: e.target.value })}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
              >
                <option value="onboarding">Onboarding</option>
                <option value="watch">Watch & Retention</option>
                <option value="social">Social & Referral</option>
                <option value="earning">Earning & Economy</option>
                <option value="special">Special & Milestones</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Description</label>
              <textarea
                value={modalBadge.description}
                onChange={(e) => setModalBadge({ ...modalBadge, description: e.target.value })}
                rows="2"
                placeholder="Explain what the user must achieve..."
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
              />
            </div>

            {/* Thresholds Matrix */}
            <div className="border-t border-slate-800 pt-4">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                Tier Target Thresholds
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-xs font-medium text-amber-400 mb-1">🥉 Bronze</label>
                  <input
                    type="number"
                    value={modalBadge.target_bronze}
                    onChange={(e) =>
                      setModalBadge({ ...modalBadge, target_bronze: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">🥈 Silver</label>
                  <input
                    type="number"
                    value={modalBadge.target_silver}
                    onChange={(e) =>
                      setModalBadge({ ...modalBadge, target_silver: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-yellow-400 mb-1">🥇 Gold</label>
                  <input
                    type="number"
                    value={modalBadge.target_gold}
                    onChange={(e) =>
                      setModalBadge({ ...modalBadge, target_gold: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-cyan-400 mb-1">💎 Diamond</label>
                  <input
                    type="number"
                    value={modalBadge.target_diamond}
                    onChange={(e) =>
                      setModalBadge({ ...modalBadge, target_diamond: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 text-sm font-medium hover:bg-slate-700 transition"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveModal}
                disabled={saving}
                className="px-6 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold transition"
              >
                {saving ? 'Saving...' : 'Save Badge'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
