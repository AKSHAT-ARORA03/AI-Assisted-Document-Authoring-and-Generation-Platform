import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User, FileText, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from './ThemeToggle';
import toast from 'react-hot-toast';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Error logging out');
    }
  };

  return (
    <header style={{ 
      background: 'var(--bg-primary)', 
      borderBottom: '1px solid var(--border-color)',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <FileText style={{ 
              height: '32px', 
              width: '32px', 
              color: 'var(--accent-primary)' 
            }} />
            <span style={{ 
              fontSize: '1.25rem', 
              fontWeight: '700', 
              color: 'var(--text-primary)' 
            }}>
              AI Document Platform
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/dashboard" 
              style={{ 
                color: 'var(--text-secondary)', 
                fontWeight: '500',
                textDecoration: 'none',
                transition: 'color 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--text-primary)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              Dashboard
            </Link>
            <Link 
              to="/projects/new" 
              style={{ 
                color: 'var(--text-secondary)', 
                fontWeight: '500',
                textDecoration: 'none',
                transition: 'color 0.3s ease'
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--text-primary)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
            >
              New Project
            </Link>
          </nav>

          {/* User menu */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle */}
            <ThemeToggle size="small" />
            
            {/* User Info */}
            <div className="flex items-center space-x-2 text-sm">
              <User style={{ 
                height: '20px', 
                width: '20px', 
                color: 'var(--text-tertiary)' 
              }} />
              <span style={{ 
                color: 'var(--text-secondary)', 
                fontWeight: '500' 
              }}>
                {user?.full_name || user?.name || user?.email}
              </span>
            </div>

            {/* Profile Link */}
            <Link
              to="/profile"
              style={{ 
                color: 'var(--text-secondary)',
                textDecoration: 'none',
                transition: 'color 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--text-primary)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              title="Profile Settings"
            >
              <Settings style={{ height: '20px', width: '20px' }} />
              <span className="hidden sm:inline">Profile</span>
            </Link>
            
            {/* Logout Button */}
            <button
              onClick={handleLogout}
              style={{ 
                color: 'var(--text-secondary)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                transition: 'color 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => e.target.style.color = 'var(--text-primary)'}
              onMouseLeave={(e) => e.target.style.color = 'var(--text-secondary)'}
              title="Logout"
            >
              <LogOut style={{ height: '20px', width: '20px' }} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;