const BASE_URL = '/api';

export function getAuthHeader() {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {})
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (response.status === 204) {
    return true;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || `Request failed with status ${response.status}`);
  }

  return data;
}

export const api = {
  // Auth
  register: (username, email, password) => request('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) }),
  login: (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  getProfile: () => request('/auth/profile'),

  // Projects
  getProjects: () => request('/projects'),
  getProject: (id) => request(`/projects/${id}`),
  createProject: (name, description) => request('/projects', { method: 'POST', body: JSON.stringify({ name, description }) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),

  // Orchestrator & Tasks
  startTask: (projectId, userPrompt) => request('/orchestrator/start', { method: 'POST', body: JSON.stringify({ project_id: projectId, user_prompt: userPrompt }) }),
  getTaskStatus: (taskId) => request(`/orchestrator/status/${taskId}`),
  getTaskResults: (taskId) => request(`/orchestrator/results/${taskId}`),
  cancelTask: (taskId) => request(`/orchestrator/cancel/${taskId}`, { method: 'POST' }),

  // Artifacts
  getProjectArtifacts: (projectId) => request(`/projects/${projectId}/artifacts`),
  getArtifact: (projectId, artifactId) => request(`/projects/${projectId}/artifacts/${artifactId}`),
  getArtifactDownloadUrl: (projectId, artifactId) => `/api/projects/${projectId}/artifacts/${artifactId}/download`
};
