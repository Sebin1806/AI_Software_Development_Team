import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onOpenAuth }) {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="brand">
        ⚡ AI Software Development Team
      </div>
      <div>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
              👤 {user.username} ({user.email})
            </span>
            <button className="btn btn-secondary" onClick={logout}>
              Logout
            </button>
          </div>
        ) : (
          <button className="btn btn-primary" onClick={onOpenAuth}>
            Sign In / Register
          </button>
        )}
      </div>
    </nav>
  );
}
