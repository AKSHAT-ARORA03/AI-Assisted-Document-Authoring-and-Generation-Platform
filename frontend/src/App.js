import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { ClerkProvider } from '@clerk/clerk-react';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import NewProject from './pages/NewProject';
import ProjectEditor from './pages/ProjectEditor';
import Profile from './pages/Profile';
import './styles/theme.css';

const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

// Check if we have a valid Clerk key
const isClerkEnabled = clerkPubKey && 
  clerkPubKey !== 'your-clerk-publishable-key-here' && 
  clerkPubKey.startsWith('pk_');

function AppContent() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <Router>
          <div style={{ 
            minHeight: '100vh', 
            background: 'var(--bg-primary)',
            color: 'var(--text-primary)'
          }}>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Header />
                  <Dashboard />
                </ProtectedRoute>
              } />
              
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Header />
                  <Profile />
                </ProtectedRoute>
              } />
              
              <Route path="/projects/new" element={
                <ProtectedRoute>
                  <Header />
                  <NewProject />
                </ProtectedRoute>
              } />
              
              <Route path="/projects/:id/edit" element={
                <ProtectedRoute>
                  <Header />
                  <ProjectEditor />
                </ProtectedRoute>
              } />
              
              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            
            {/* Toast notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  boxShadow: 'var(--shadow-lg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                },
                success: {
                  iconTheme: {
                    primary: 'var(--success-color)',
                    secondary: 'var(--bg-primary)',
                  },
                },
                error: {
                  iconTheme: {
                    primary: 'var(--danger-color)',
                    secondary: 'var(--bg-primary)',
                  },
                },
              }}
            />
          </div>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

function App() {
  // Only use ClerkProvider if we have a valid key
  if (isClerkEnabled) {
    return (
      <ClerkProvider publishableKey={clerkPubKey}>
        <AppContent />
      </ClerkProvider>
    );
  }

  // Fall back to JWT-only authentication
  return <AppContent />;
}

export default App;