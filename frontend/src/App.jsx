import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import Dashboard from './components/Dashboard';
import ProjectDetailView from './components/ProjectDetailView';

function MainLayout() {
  const { user, loading } = useAuth();
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '5rem', color: '#94a3b8' }}>Loading AI Platform...</div>;
  }

  return (
    <div>
      <Navbar onOpenAuth={() => setIsAuthOpen(true)} />
      <main className="container">
        {!user ? (
          <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center', maxWidth: '700px', margin: '3rem auto' }}>
            <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem', background: 'linear-gradient(135deg, #818cf8 0%, #38bdf8 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Autonomous 12-Agent Software Engineering Team
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '2rem', lineHeight: '1.6' }}>
              Submit your software requirements and watch 12 specialized AI agents (Project Manager, Architect, DB Engineer, API Developer, Frontend/Backend Developers, Security Engineer, QA, DevOps) design and build complete applications.
            </p>
            <button className="btn btn-primary" style={{ padding: '0.8rem 2rem', fontSize: '1.05rem' }} onClick={() => setIsAuthOpen(true)}>
              Get Started
            </button>
          </div>
        ) : selectedProject ? (
          <ProjectDetailView project={selectedProject} onBack={() => setSelectedProject(null)} />
        ) : (
          <Dashboard onSelectProject={(proj) => setSelectedProject(proj)} />
        )}
      </main>
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}
