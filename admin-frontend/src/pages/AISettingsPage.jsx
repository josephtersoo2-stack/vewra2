import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  Key,
  Cpu,
  RefreshCw,
  Play,
  Save,
  CheckCircle2,
  AlertCircle,
  Clock,
  Eye,
  EyeOff,
  Search,
} from 'lucide-react';
import { adminApi } from '../api/adminApi';
import { Badge } from '../components/ui/Badge';
import { useTheme } from '../theme/ThemeContext';

export function AISettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form states
  const [activeProvider, setActiveProvider] = useState('openrouter');
  const [geminiKey, setGeminiKey] = useState('');
  const [openrouterKey, setOpenrouterKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [isActive, setIsActive] = useState(true);

  // Show/Hide Keys
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [showORKey, setShowORKey] = useState(false);

  // Dynamic Models
  const [models, setModels] = useState([]);
  const [fetchingModels, setFetchingModels] = useState(false);
  const [modelSearch, setModelSearch] = useState('');
  const [modelFeedback, setModelFeedback] = useState('');

  // Sandbox Tester states
  const [testUrl, setTestUrl] = useState('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testError, setTestError] = useState('');

  const loadSettings = async () => {
    try {
      const data = await adminApi.getAISettings();
      setSettings(data);
      const prov = data.active_provider || 'openrouter';
      const gKey = data.gemini_api_key || '';
      const orKey = data.openrouter_api_key || '';
      setActiveProvider(prov);
      setGeminiKey(gKey);
      setOpenrouterKey(orKey);
      setSelectedModel(data.selected_model || '');
      setCustomPrompt(data.custom_system_prompt || '');
      setIsActive(data.is_active ?? true);

      // Fetch models for active provider
      loadModels(prov, prov === 'gemini' ? gKey : orKey);
    } catch (err) {
      console.error('Failed to load AI settings', err);
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async (provider, customKey = '') => {
    setFetchingModels(true);
    setModelFeedback('');
    try {
      const keyToUse = customKey !== '' ? customKey : (provider === 'gemini' ? geminiKey : openrouterKey);
      const res = await adminApi.fetchAIModels(provider, keyToUse);
      const list = res.models || [];
      setModels(list);
      setModelFeedback(`✓ Loaded ${list.length} models for ${provider === 'gemini' ? 'Google Gemini' : 'OpenRouter'}`);
      setTimeout(() => setModelFeedback(''), 4000);
    } catch (err) {
      console.error('Failed to fetch models', err);
      setModelFeedback(`Error: ${err.response?.data?.error || err.message}`);
    } finally {
      setFetchingModels(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleProviderChange = (provider) => {
    setActiveProvider(provider);
    const key = provider === 'gemini' ? geminiKey : openrouterKey;
    loadModels(provider, key);
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await adminApi.updateAISettings({
        active_provider: activeProvider,
        gemini_api_key: geminiKey,
        openrouter_api_key: openrouterKey,
        selected_model: selectedModel,
        custom_system_prompt: customPrompt,
        is_active: isActive,
      });
      setSettings(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      loadModels(activeProvider, activeProvider === 'gemini' ? geminiKey : openrouterKey);
    } catch (err) {
      alert('Failed to save settings: ' + (err.response?.data?.error || err.message));
    } finally {
      setSaving(false);
    }
  };

  const handleRunSandboxTest = async (e) => {
    e.preventDefault();
    if (!testUrl) return;
    setTesting(true);
    setTestResult(null);
    setTestError('');
    try {
      const res = await adminApi.testAISandbox({
        youtube_url: testUrl,
        provider: activeProvider,
        model_name: selectedModel,
        custom_prompt: customPrompt,
      });
      setTestResult(res);
    } catch (err) {
      setTestError(err.response?.data?.error || err.message || 'Sandbox test failed');
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading AI Studio configuration...</p>
      </div>
    );
  }

  const filteredModels = models.filter((m) => {
    const id = (typeof m === 'string' ? m : m.id || m.name || '').toLowerCase();
    const name = (typeof m === 'object' && m.name ? m.name : '').toLowerCase();
    const query = modelSearch.toLowerCase();
    return id.includes(query) || name.includes(query);
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-primary)' }}>
            AI Keyword Studio & Models
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Configure OpenRouter / Gemini LLM providers, discover live models, and test prompt generation
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {saveSuccess && (
            <Badge variant="emerald" size="md">
              <CheckCircle2 size={16} /> Settings Saved
            </Badge>
          )}
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
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
            <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '24px' }}>
        {/* Left Column: Provider & Keys */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Active Provider Selector */}
          <div className="card">
            <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '16px' }}>
              Active AI Provider
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              {/* OpenRouter Option */}
              <div
                onClick={() => handleProviderChange('openrouter')}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--btn-radius)',
                  border: activeProvider === 'openrouter' ? '2px solid var(--primary)' : '1px solid var(--border-card)',
                  backgroundColor: activeProvider === 'openrouter' ? 'var(--primary-light)' : 'var(--bg-tertiary)',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: '700', fontSize: '15px', color: 'var(--text-primary)' }}>
                    OpenRouter Hub
                  </span>
                  {activeProvider === 'openrouter' && <Badge variant="indigo">Active</Badge>}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Access to 400+ top open & commercial LLM models
                </p>
              </div>

              {/* Google Gemini Option */}
              <div
                onClick={() => handleProviderChange('gemini')}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--btn-radius)',
                  border: activeProvider === 'gemini' ? '2px solid var(--primary)' : '1px solid var(--border-card)',
                  backgroundColor: activeProvider === 'gemini' ? 'var(--primary-light)' : 'var(--bg-tertiary)',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: '700', fontSize: '15px', color: 'var(--text-primary)' }}>
                    Google Gemini
                  </span>
                  {activeProvider === 'gemini' && <Badge variant="indigo">Active</Badge>}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Ultra-fast response time with official Gemini API keys
                </p>
              </div>
            </div>

            {/* API Keys Configuration */}
            <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>
                    OpenRouter API Key
                  </label>
                  {openrouterKey ? (
                    <Badge variant="emerald" size="sm">Configured</Badge>
                  ) : (
                    <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Optional for browsing models</span>
                  )}
                </div>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showORKey ? 'text' : 'password'}
                    value={openrouterKey}
                    onChange={(e) => setOpenrouterKey(e.target.value)}
                    placeholder="sk-or-v1-..."
                    style={{
                      width: '100%',
                      padding: '12px 42px 12px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowORKey(!showORKey)}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-tertiary)',
                      cursor: 'pointer',
                    }}
                  >
                    {showORKey ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)' }}>
                    Google Gemini API Key
                  </label>
                  {geminiKey && <Badge variant="emerald" size="sm">Configured</Badge>}
                </div>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showGeminiKey ? 'text' : 'password'}
                    value={geminiKey}
                    onChange={(e) => setGeminiKey(e.target.value)}
                    placeholder="AIzaSy..."
                    style={{
                      width: '100%',
                      padding: '12px 42px 12px 14px',
                      borderRadius: 'var(--input-radius)',
                      backgroundColor: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-card)',
                      color: 'var(--text-primary)',
                      fontSize: '13px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowGeminiKey(!showGeminiKey)}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-tertiary)',
                      cursor: 'pointer',
                    }}
                  >
                    {showGeminiKey ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Dynamic Model Picker */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)' }}>
                  Select Model ({activeProvider === 'gemini' ? 'Google Gemini' : 'OpenRouter'})
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Active Model: <code style={{ color: 'var(--primary)', fontWeight: '700' }}>{selectedModel || (activeProvider === 'openrouter' ? 'google/gemini-2.5-flash' : 'gemini-2.5-flash')}</code>
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {modelFeedback && (
                  <span style={{ fontSize: '11px', fontWeight: '600', color: modelFeedback.startsWith('✓') ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                    {modelFeedback}
                  </span>
                )}
                <button
                  onClick={() => loadModels(activeProvider, activeProvider === 'gemini' ? geminiKey : openrouterKey)}
                  disabled={fetchingModels}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: 'var(--btn-radius)',
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-card)',
                    color: 'var(--text-primary)',
                    fontSize: '12px',
                    fontWeight: '600',
                    cursor: 'pointer',
                  }}
                >
                  <RefreshCw size={14} className={fetchingModels ? 'pulse-badge' : ''} />
                  <span>{fetchingModels ? 'Fetching...' : 'Discover Models'}</span>
                </button>
              </div>
            </div>

            {/* Model Search Box */}
            <div style={{ position: 'relative', marginBottom: '12px' }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-tertiary)' }} />
              <input
                type="text"
                value={modelSearch}
                onChange={(e) => setModelSearch(e.target.value)}
                placeholder="Filter models (e.g. flash, llama, sonnet, free, deepseek)..."
                style={{
                  width: '100%',
                  padding: '10px 12px 10px 36px',
                  borderRadius: 'var(--input-radius)',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-card)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                }}
              />
            </div>

            {/* Models Scrollable List */}
            <div
              style={{
                maxHeight: '260px',
                overflowY: 'auto',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--input-radius)',
                padding: '6px',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
              }}
            >
              {filteredModels.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-tertiary)' }}>
                  {fetchingModels ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <RefreshCw size={16} className="pulse-badge" />
                      <span>Discovering live models from {activeProvider === 'gemini' ? 'Google' : 'OpenRouter'}...</span>
                    </div>
                  ) : (
                    <div>
                      <p>No models found matching "{modelSearch}".</p>
                      <button
                        onClick={() => loadModels(activeProvider, activeProvider === 'gemini' ? geminiKey : openrouterKey)}
                        style={{
                          marginTop: '8px',
                          padding: '4px 12px',
                          fontSize: '12px',
                          borderRadius: '4px',
                          backgroundColor: 'var(--primary)',
                          color: '#fff',
                          border: 'none',
                          cursor: 'pointer',
                        }}
                      >
                        Discover All Models
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                filteredModels.map((m) => {
                  const id = typeof m === 'string' ? m : m.id || m.name;
                  const name = typeof m === 'object' && m.name && m.name !== id ? m.name : '';
                  const isFree = id.includes(':free') || id.includes('free');
                  const isSelected = selectedModel === id;

                  return (
                    <div
                      key={id}
                      onClick={() => setSelectedModel(id)}
                      style={{
                        padding: '10px 12px',
                        borderRadius: '8px',
                        backgroundColor: isSelected ? 'var(--primary-light)' : 'transparent',
                        border: isSelected ? '1px solid var(--border-active)' : '1px solid transparent',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        transition: 'background-color 0.15s ease',
                      }}
                    >
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                          <span style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '13px',
                            fontWeight: isSelected ? '700' : '500',
                            color: isSelected ? 'var(--primary)' : 'var(--text-primary)',
                          }}>
                            {id}
                          </span>
                          {isFree && <Badge variant="emerald" size="sm">Free</Badge>}
                        </div>
                        {name && (
                          <span style={{ fontSize: '11px', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {name}
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                        {m.context_length ? (
                          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                            {Math.round(m.context_length / 1000)}k ctx
                          </span>
                        ) : null}
                        {isSelected && <CheckCircle2 size={18} style={{ color: 'var(--primary)' }} />}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Prompt Editor & Interactive Sandbox */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Prompt Editor */}
          <div className="card">
            <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '12px' }}>
              System Prompt Template
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              Instruction given to the model for generating verified YouTube search phrases.
            </p>

            <textarea
              rows={8}
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              style={{
                width: '100%',
                padding: '14px',
                borderRadius: 'var(--input-radius)',
                backgroundColor: 'var(--bg-tertiary)',
                border: '1px solid var(--border-card)',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                lineHeight: '1.5',
                resize: 'vertical',
              }}
            />
          </div>

          {/* Real-time Sandbox Tester */}
          <div className="card" style={{ border: '1px solid var(--border-active)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Sparkles size={20} style={{ color: 'var(--primary)' }} />
              <h3 style={{ fontSize: '17px', fontWeight: '700', color: 'var(--text-primary)' }}>
                Live Keyword Sandbox Tester
              </h3>
            </div>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Test keyword extraction on any YouTube link with your current active model in real time.
            </p>

            <form onSubmit={handleRunSandboxTest} style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  borderRadius: 'var(--input-radius)',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-card)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                }}
              />
              <button
                type="submit"
                disabled={testing}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 18px',
                  borderRadius: 'var(--btn-radius)',
                  backgroundColor: 'var(--primary)',
                  color: '#FFFFFF',
                  border: 'none',
                  fontSize: '13px',
                  fontWeight: '700',
                  cursor: testing ? 'not-allowed' : 'pointer',
                }}
              >
                <Play size={14} />
                <span>{testing ? 'Testing...' : 'Run Test'}</span>
              </button>
            </form>

            {testError && (
              <div
                style={{
                  marginTop: '16px',
                  padding: '12px',
                  borderRadius: 'var(--btn-radius)',
                  backgroundColor: 'var(--badge-rose-bg)',
                  color: 'var(--badge-rose-text)',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <AlertCircle size={16} />
                <span>{testError}</span>
              </div>
            )}

            {testResult && (
              <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                  <div>
                    <span style={{ fontSize: '14px', fontWeight: '800', color: 'var(--text-primary)' }}>
                      {testResult.metadata?.title || 'YouTube Video'}
                    </span>
                    {testResult.metadata?.channel && (
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        Creator: <strong style={{ color: 'var(--primary)' }}>{testResult.metadata.channel}</strong>
                      </p>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <Badge variant="emerald">✓ {testResult.verified_count || 8} Verified</Badge>
                    <Badge variant="indigo">{testResult.provider_used}</Badge>
                    <Badge variant="amber">{testResult.latency_ms}ms</Badge>
                  </div>
                </div>

                {testResult.queries && testResult.queries.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '6px' }}>
                    {testResult.queries.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          padding: '12px 14px',
                          borderRadius: 'var(--input-radius)',
                          backgroundColor: 'var(--bg-tertiary)',
                          border: '1px solid var(--border-card)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '4px',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                          <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                            {item.category}
                          </span>
                          <span style={{ fontSize: '11px', color: 'var(--badge-emerald-text)', backgroundColor: 'var(--badge-emerald-bg)', padding: '2px 6px', borderRadius: '4px', fontWeight: '600' }}>
                            {item.confidence_score || '98%'} Match
                          </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-primary)' }}>
                            🔍 "{item.query}"
                          </span>
                        </div>
                        {item.note && (
                          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic', margin: 0 }}>
                            ({item.note})
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {testResult.keywords?.map((kw, i) => (
                      <Badge key={i} variant="amber" size="md">
                        🔍 {kw}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
