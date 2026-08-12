import React, { useState, useEffect } from 'react';
import { api, getAuthHeader } from '../api/client';

export default function ProjectDetailView({ project, onBack }) {
  const [userPrompt, setUserPrompt] = useState('');
  const [activeTask, setActiveTask] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [artifacts, setArtifacts] = useState([]);
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('artifacts'); // 'artifacts', 'review', 'security'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Real-time SSE Progress Streaming & Status Polling
  useEffect(() => {
    let eventSource;
    let timer;

    if (activeTask && (taskStatus?.status === 'pending' || taskStatus?.status === 'running')) {
      // 1. EventSource SSE streaming connection
      try {
        const streamUrl = api.getTaskStreamUrl(activeTask);
        eventSource = new EventSource(streamUrl);

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setTaskStatus(prev => ({
              ...prev,
              ...data
            }));

            if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
              eventSource.close();
              fetchTaskResults(activeTask);
            }
          } catch (e) {
            console.error("SSE parse error", e);
          }
        };

        eventSource.onerror = () => {
          eventSource.close();
        };
      } catch (err) {
        console.error("SSE connection error", err);
      }

      // 2. Backup Polling every 3 seconds
      timer = setInterval(async () => {
        try {
          const statusData = await api.getTaskStatus(activeTask);
          setTaskStatus(statusData);

          if (statusData.status === 'completed' || statusData.status === 'failed' || statusData.status === 'cancelled') {
            clearInterval(timer);
            if (eventSource) eventSource.close();
            fetchTaskResults(activeTask);
          }
        } catch (err) {
          console.error("Status polling error:", err);
        }
      }, 3000);
    }

    return () => {
      if (eventSource) eventSource.close();
      if (timer) clearInterval(timer);
    };
  }, [activeTask, taskStatus?.status]);

  const fetchTaskResults = async (taskId) => {
    try {
      const res = await api.getTaskResults(taskId);
      setResults(res);
      setArtifacts(res.artifacts || []);
      if (res.artifacts && res.artifacts.length > 0) {
        setSelectedArtifact(res.artifacts[0]);
      }
    } catch (err) {
      console.error("Results fetch error:", err);
    }
  };

  const handleStartTask = async (e) => {
    e.preventDefault();
    if (!userPrompt.trim()) return;
    setError('');
    setLoading(true);

    try {
      const taskRes = await api.startTask(project.id, userPrompt);
      setActiveTask(taskRes.task_id);
      setTaskStatus({ status: 'pending', percentage_completed: 0, current_step: 0, total_steps: 12, logs: [] });
      setResults(null);
      setArtifacts([]);
    } catch (err) {
      setError(err.message || 'Failed to start task');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelTask = async () => {
    if (!activeTask) return;
    try {
      await api.cancelTask(activeTask);
      const statusData = await api.getTaskStatus(activeTask);
      setTaskStatus(statusData);
    } catch (err) {
      console.error("Cancel task error:", err);
    }
  };

  const handleCopyCode = (content) => {
    navigator.clipboard.writeText(content);
    alert('Code copied to clipboard!');
  };

  const filteredArtifacts = artifacts.filter(art => {
    if (selectedCategory === 'all') return true;
    return art.category === selectedCategory;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <button className="btn btn-secondary" style={{ marginBottom: '0.75rem' }} onClick={onBack}>
            ← Back to Projects
          </button>
          <h2>{project.name}</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.25rem' }}>{project.description || 'No description provided.'}</p>
        </div>
        {results && (
          <a
            className="btn btn-primary"
            href={api.getProjectZipUrl(project.id)}
            download
            style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            📦 Download Complete Project ZIP
          </a>
        )}
      </div>

      {/* Start Task Form */}
      {(!taskStatus || taskStatus.status === 'completed' || taskStatus.status === 'failed' || taskStatus.status === 'cancelled') && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>🚀 Submit Software Requirements</h3>
          {error && <div style={{ color: '#ef4444', marginBottom: '1rem', fontSize: '0.85rem' }}>{error}</div>}
          <form onSubmit={handleStartTask}>
            <div className="form-group">
              <textarea
                className="form-textarea"
                required
                value={userPrompt}
                onChange={e => setUserPrompt(e.target.value)}
                placeholder="Describe the application requirements in detail (e.g. Build a SaaS task management system with user authentication, PostgreSQL database, REST endpoints, React frontend, and Docker deployment)..."
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Submitting Requirement...' : 'Start 12-Agent Autonomous Workflow'}
            </button>
          </form>
        </div>
      )}

      {/* Workflow Execution Progress */}
      {taskStatus && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3>Workflow Progress (Real-Time SSE)</h3>
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem', alignItems: 'center' }}>
                <span className={`badge badge-${taskStatus.status}`}>{taskStatus.status}</span>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                  Step {taskStatus.current_step || 0} / {taskStatus.total_steps || 12}
                </span>
                {taskStatus.current_agent && (
                  <span style={{ fontSize: '0.85rem', color: '#818cf8', fontWeight: 600 }}>
                    Active Agent: {taskStatus.current_agent}
                  </span>
                )}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {taskStatus.status === 'running' && (
                <button className="btn btn-danger" onClick={handleCancelTask}>
                  Cancel Workflow
                </button>
              )}
              {activeTask && (
                <a className="btn btn-secondary" href={api.getTaskZipUrl(activeTask)} download style={{ textDecoration: 'none' }}>
                  ⚡ Download Task ZIP
                </a>
              )}
            </div>
          </div>

          <div className="progress-bar-container">
            <div className="progress-bar-fill" style={{ width: `${taskStatus.percentage_completed || 0}%` }} />
          </div>
          <div style={{ textAlign: 'right', fontSize: '0.8rem', color: '#94a3b8' }}>
            {taskStatus.percentage_completed || 0}% Completed
          </div>

          {/* Timeline Table */}
          <h4 style={{ marginTop: '1.5rem', marginBottom: '0.75rem' }}>12-Agent Execution Timeline</h4>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: '#94a3b8' }}>
                  <th style={{ padding: '0.5rem' }}>Step</th>
                  <th style={{ padding: '0.5rem' }}>Agent</th>
                  <th style={{ padding: '0.5rem' }}>Status</th>
                  <th style={{ padding: '0.5rem' }}>Retries</th>
                  <th style={{ padding: '0.5rem' }}>Error / Validation Log</th>
                </tr>
              </thead>
              <tbody>
                {(taskStatus.logs || []).map((log, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.5rem' }}>{log.step_number}</td>
                    <td style={{ padding: '0.5rem', fontWeight: 600 }}>{log.agent_name}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span className={`badge badge-${log.status}`}>{log.status}</span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{log.retry_count}</td>
                    <td style={{ padding: '0.5rem', color: '#ef4444' }}>{log.error_message || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Artifacts & Results Section */}
      {results && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>📦 Generated Project Architecture & Files</h3>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            <button className={`btn ${activeTab === 'artifacts' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('artifacts')}>
              Nested Code Files ({artifacts.length})
            </button>
            <button className={`btn ${activeTab === 'review' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('review')}>
              AST Code Review Report
            </button>
            <button className={`btn ${activeTab === 'security' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('security')}>
              OWASP Security Audit
            </button>
          </div>

          {/* Tab 1: Artifact File Browser */}
          {activeTab === 'artifacts' && (
            <div>
              {/* Category Filter Pills */}
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                {['all', 'frontend', 'backend', 'database', 'docs', 'deployment', 'tests'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    style={{
                      padding: '0.3rem 0.8rem',
                      borderRadius: '16px',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      border: '1px solid var(--border-color)',
                      background: selectedCategory === cat ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                      color: 'white',
                      cursor: 'pointer',
                      textTransform: 'capitalize'
                    }}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1rem', minHeight: '420px' }}>
                {/* File List Sidebar */}
                <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '0.75rem', overflowY: 'auto' }}>
                  {filteredArtifacts.map((art) => (
                    <div
                      key={art.id}
                      onClick={() => setSelectedArtifact(art)}
                      style={{
                        padding: '0.6rem 0.8rem',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        marginBottom: '0.4rem',
                        fontSize: '0.85rem',
                        background: selectedArtifact?.id === art.id ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                        borderLeft: selectedArtifact?.id === art.id ? '3px solid var(--primary)' : '3px solid transparent'
                      }}
                    >
                      <div style={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        📂 {art.relative_path || art.file_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                        {art.agent_name} • v{art.version}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Code Preview */}
                {selectedArtifact ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#818cf8' }}>
                        📄 {selectedArtifact.relative_path || selectedArtifact.file_name}
                      </span>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }} onClick={() => handleCopyCode(selectedArtifact.content)}>
                          📋 Copy Code
                        </button>
                        <a
                          className="btn btn-primary"
                          style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', textDecoration: 'none' }}
                          href={api.getArtifactDownloadUrl(project.id, selectedArtifact.id)}
                          download={selectedArtifact.file_name}
                        >
                          ⬇️ Download File
                        </a>
                      </div>
                    </div>
                    <pre className="code-block" style={{ maxHeight: '520px', overflowY: 'auto' }}>
                      <code>{selectedArtifact.content}</code>
                    </pre>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>
                    Select a generated artifact to preview source code
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 2: Code Review Findings */}
          {activeTab === 'review' && (
            <div>
              <h4>AST Code Review & Architecture Audit</h4>
              <ul style={{ marginTop: '0.75rem', paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.9rem' }}>
                {(results.workflow_summary?.code_review_findings || []).map((finding, idx) => (
                  <li key={idx} style={{ marginBottom: '0.5rem' }}>{finding}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Tab 3: Security Audit Report */}
          {activeTab === 'security' && (
            <div>
              <h4>OWASP Security Engineering Audit</h4>
              <ul style={{ marginTop: '0.75rem', paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.9rem' }}>
                {(results.workflow_summary?.security_findings || []).map((finding, idx) => (
                  <li key={idx} style={{ marginBottom: '0.5rem' }}>{finding}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
