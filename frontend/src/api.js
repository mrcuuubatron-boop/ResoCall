/**
 * api.js — тонкий HTTP-клиент к ResoCall API.
 * Базовый URL можно переопределить через localStorage('resocall_api_url').
 */
const API_BASE = localStorage.getItem('resocall_api_url') || 'http://localhost:8000/api/v1';

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || 'Ошибка API');
  }
  return response.json();
}

const api = {
  // Agents
  getAgents: () => apiFetch('/agents/'),
  createAgent: (data) => apiFetch('/agents/', { method: 'POST', body: JSON.stringify(data) }),
  getAgent: (id) => apiFetch(`/agents/${id}`),

  // Calls
  getCalls: () => apiFetch('/calls/'),
  createCall: (data) => apiFetch('/calls/', { method: 'POST', body: JSON.stringify(data) }),
  getCall: (id) => apiFetch(`/calls/${id}`),

  // Analysis
  getAnalyses: () => apiFetch('/analysis/'),
  runAnalysis: (callId) => apiFetch(`/analysis/${callId}`, { method: 'POST' }),
  getAnalysis: (callId) => apiFetch(`/analysis/${callId}`),
};
