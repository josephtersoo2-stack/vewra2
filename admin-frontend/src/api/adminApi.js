import { apiClient } from './client';

export const adminApi = {
  // Auth
  login: async (username, password) => {
    const res = await apiClient.post('/auth/login/', { username, password });
    return res.data;
  },

  // Dashboard KPIs & Trends
  getDashboardStats: async (params = {}) => {
    const res = await apiClient.get('/admin/stats/', { params });
    return res.data;
  },

  // Video Tasks
  getVideoTasks: async () => {
    const res = await apiClient.get('/admin/tasks/');
    return res.data;
  },
  createVideoTask: async (data) => {
    const res = await apiClient.post('/admin/tasks/', data);
    return res.data;
  },
  updateVideoTask: async (id, data) => {
    const res = await apiClient.patch(`/admin/tasks/${id}/`, data);
    return res.data;
  },
  deleteVideoTask: async (id) => {
    const res = await apiClient.delete(`/admin/tasks/${id}/`);
    return res.data;
  },
  regenerateKeywords: async (id) => {
    const res = await apiClient.post(`/admin/tasks/${id}/regenerate-keywords/`);
    return res.data;
  },
  fetchYouTubeMeta: async (url) => {
    const res = await apiClient.post('/admin/tasks/fetch-youtube-meta/', { youtube_url: url });
    return res.data;
  },

  // AI Settings & Sandbox
  getAISettings: async () => {
    const res = await apiClient.get('/admin/ai-settings/');
    return res.data;
  },
  updateAISettings: async (data) => {
    const res = await apiClient.patch('/admin/ai-settings/', data);
    return res.data;
  },
  fetchAIModels: async (provider, apiKey = '') => {
    const params = { provider };
    if (apiKey) params.api_key = apiKey;
    const res = await apiClient.get('/admin/ai-settings/fetch-models/', { params });
    return res.data;
  },
  testAISandbox: async (data) => {
    const res = await apiClient.post('/admin/ai-settings/test-sandbox/', data);
    return res.data;
  },

  // Watch Sessions & Telemetry
  getWatchSessions: async (params = {}) => {
    const res = await apiClient.get('/admin/watch-sessions/', { params });
    return res.data;
  },
  getLiveWatchSessions: async () => {
    const res = await apiClient.get('/admin/watch-sessions/live/');
    return res.data;
  },
  getVideoTelemetry: async (params = {}) => {
    const res = await apiClient.get('/admin/watch-sessions/video-telemetry/', { params });
    return res.data;
  },
  getVideoViewers: async (videoTaskId) => {
    const res = await apiClient.get('/admin/watch-sessions/video-viewers/', {
      params: { video_task_id: videoTaskId },
    });
    return res.data;
  },

  // Users
  getUsers: async (params = {}) => {
    const res = await apiClient.get('/admin/users/', { params });
    return res.data;
  },
  adjustUserBalance: async (id, data) => {
    const res = await apiClient.post(`/admin/users/${id}/adjust-balance/`, data);
    return res.data;
  },
  toggleUserStatus: async (id) => {
    const res = await apiClient.post(`/admin/users/${id}/toggle-status/`);
    return res.data;
  },

  // Financial Ledger
  getWalletTransactions: async (params = {}) => {
    const res = await apiClient.get('/admin/wallet-transactions/', { params });
    return res.data;
  },

  // Gamification & Daily Streak Settings
  getStreakSettings: async () => {
    const res = await apiClient.get('/admin/gamification-settings/');
    return res.data;
  },
  updateStreakSettings: async (data) => {
    const res = await apiClient.put('/admin/gamification-settings/', data);
    return res.data;
  },

  // Daily Spin Wheel Configuration
  getSpinWheelSegments: async () => {
    const res = await apiClient.get('/admin/spin-wheel-segments/');
    return res.data;
  },
  createSpinWheelSegment: async (data) => {
    const res = await apiClient.post('/admin/spin-wheel-segments/', data);
    return res.data;
  },
  updateSpinWheelSegment: async (id, data) => {
    const res = await apiClient.put(`/admin/spin-wheel-segments/${id}/`, data);
    return res.data;
  },
  patchSpinWheelSegment: async (id, data) => {
    const res = await apiClient.patch(`/admin/spin-wheel-segments/${id}/`, data);
    return res.data;
  },
  deleteSpinWheelSegment: async (id) => {
    const res = await apiClient.delete(`/admin/spin-wheel-segments/${id}/`);
    return res.data;
  },
  resetSpinWheelDefaults: async () => {
    const res = await apiClient.post('/admin/spin-wheel-segments/reset_defaults/');
    return res.data;
  },

  // Tokens & Security
  getTokens: async () => {
    const res = await apiClient.get('/admin/tokens/');
    return res.data;
  },
  blacklistToken: async (tokenId) => {
    const res = await apiClient.post('/admin/tokens/', { token_id: tokenId });
    return res.data;
  },
};

// Phase 1.2: Spin wheel API client functions registered.
