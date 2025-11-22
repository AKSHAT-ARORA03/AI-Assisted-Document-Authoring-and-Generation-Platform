import React from 'react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggle = ({ size = 'medium', showLabel = false }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleTheme();
    }
  };

  return (
    <div className={`theme-toggle-wrapper ${size}`}>
      {showLabel && (
        <span className="theme-toggle-label">
          {isDark ? 'Dark Mode' : 'Light Mode'}
        </span>
      )}
      
      <button
        className={`theme-toggle ${theme}-mode`}
        onClick={toggleTheme}
        onKeyDown={handleKeyPress}
        aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
        title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
        role="switch"
        aria-checked={isDark}
      >
        <div className="theme-toggle-track">
          <div className="theme-toggle-thumb">
            <span className="theme-icon">
              {isDark ? '🌙' : '☀️'}
            </span>
          </div>
        </div>
      </button>
    </div>
  );
};

export default ThemeToggle;