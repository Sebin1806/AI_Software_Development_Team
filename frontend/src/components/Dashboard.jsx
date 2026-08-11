import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import CreateProjectModal from './CreateProjectModal';

export default function Dashboard({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
    } catch (err) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleProjectCreated = (newProj) => {
    setProjects([newProj, ...projects]);
  };

  const handleDeleteProject = async (e, projectId) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this project?')) return;
    try {
      await api.deleteProject(projectId);
      setProjects(projects.filter(p => p.id !== projectId));
    } catch (err) {
      alert(err.message || 'Failed to delete project');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2>Your Software Projects</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Manage and run 12-agent software development workflows
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)}>
          + New Software Project
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#ef4444', padding: '0.75rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <h3>No projects yet</h3>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem', marginBottom: '1.5rem' }}>Create your first project to start the 12-agent software development workflow.</p>
          <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)}>+ Create Project</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="glass-panel"
              onClick={() => onSelectProject(proj)}
              style={{
                padding: '1.5rem',
                cursor: 'pointer',
                transition: 'transform 0.2s, border-color 0.2s',
                display: 'flex',
                flexDirection: 'column',
                justify: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h3 style={{ fontSize: '1.1rem' }}>{proj.name}</h3>
                  <span className="badge badge-running">{proj.status}</span>
                </div>
                <p style={{ color: '#94a3b8', fontSize: '0.88rem', lineClamp: 3, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {proj.description || 'No description provided.'}
                </p>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  Created: {new Date(proj.created_at).toLocaleDateString()}
                </span>
                <button className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', color: '#ef4444' }} onClick={(e) => handleDeleteProject(e, proj.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <CreateProjectModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onProjectCreated={handleProjectCreated}
      />
    </div>
  );
}
