import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleGetStarted = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
  };

  const handleLearnMore = () => {
    document.getElementById('features-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  const features = [
    {
      icon: '🤖',
      title: 'Intelligent Content Generation',
      description: 'AI creates complete documents from simple prompts with advanced language models.'
    },
    {
      icon: '📄',
      title: 'Multi-Format Export',
      description: 'Professional Word and PowerPoint output ready for immediate use.'
    },
    {
      icon: '✨',
      title: 'Smart Content Refinement',
      description: 'AI-powered editing and improvement suggestions for perfect documents.'
    },
    {
      icon: '📋',
      title: 'Instant Document Structure',
      description: 'Auto-generated outlines and organization for any topic or purpose.'
    },
    {
      icon: '⚡',
      title: 'Real-Time Collaboration',
      description: 'Live editing and feedback integration for seamless teamwork.'
    },
    {
      icon: '🔒',
      title: 'Enterprise-Ready Security',
      description: 'Professional-grade data protection with industry-standard encryption.'
    }
  ];

  const steps = [
    {
      number: '01',
      title: 'Define Your Vision',
      description: 'Enter your topic and select document type (Word or PowerPoint)'
    },
    {
      number: '02',
      title: 'AI Creates Content',
      description: 'Our AI generates professional content with intelligent structure'
    },
    {
      number: '03',
      title: 'Refine and Export',
      description: 'Edit, refine, and export your document in professional formats'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Marketing Manager',
      company: 'TechCorp',
      quote: 'This platform cut my document creation time by 80%. The AI understands exactly what I need.'
    },
    {
      name: 'Dr. Michael Chen',
      role: 'Research Director',
      company: 'Innovation Labs',
      quote: 'The quality of generated content is exceptional. It feels like having a professional writer on my team.'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Business Consultant',
      company: 'Strategy Plus',
      quote: 'My clients are impressed with the professional quality of documents I can create so quickly.'
    }
  ];

  return (
    <div className="home-page">
      {/* Navigation Bar */}
      <nav className="home-navbar">
        <div className="navbar-container">
          {/* Logo and Project Name */}
          <div className="navbar-brand">
            <span className="navbar-logo">📄</span>
            <span className="navbar-title">AI Document Platform</span>
          </div>

          {/* Navigation Buttons */}
          <div className="navbar-buttons">
            {user ? (
              <>
                <button 
                  className="navbar-btn-secondary"
                  onClick={() => navigate('/dashboard')}
                >
                  Dashboard
                </button>
                <button 
                  className="navbar-btn-secondary"
                  onClick={() => navigate('/profile')}
                >
                  Profile
                </button>
              </>
            ) : (
              <>
                <button 
                  className="navbar-btn-secondary"
                  onClick={() => navigate('/login')}
                >
                  Login
                </button>
                <button 
                  className="navbar-btn-primary"
                  onClick={() => navigate('/register')}
                >
                  Register
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Transform Ideas Into Professional Documents with AI
            </h1>
            <p className="hero-subtitle">
              Create stunning Word documents and PowerPoint presentations in minutes, not hours. 
              Let our advanced AI handle the writing while you focus on what matters most.
            </p>
            <div className="hero-buttons">
              <button className="btn-primary" onClick={handleGetStarted}>
                Start Creating Free
              </button>
              <button className="btn-secondary" onClick={handleLearnMore}>
                See How It Works
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-animation">
              <div className="document-preview">
                <div className="document-header">
                  <div className="doc-controls">
                    <span className="doc-dot"></span>
                    <span className="doc-dot"></span>
                    <span className="doc-dot"></span>
                  </div>
                  <span className="doc-title">AI Generated Document</span>
                </div>
                <div className="document-content">
                  <div className="typing-animation">
                    <div className="line"></div>
                    <div className="line"></div>
                    <div className="line short"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features-section" className="features-section">
        <div className="container">
          <div className="section-header">
            <h2>Platform Capabilities</h2>
            <p>Powerful features designed to revolutionize your document creation workflow</p>
          </div>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="container">
          <div className="section-header">
            <h2>Simple 3-Step Workflow</h2>
            <p>From idea to professional document in minutes</p>
          </div>
          <div className="steps-container">
            {steps.map((step, index) => (
              <div key={index} className="step-item">
                <div className="step-number">{step.number}</div>
                <div className="step-content">
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </div>
                {index < steps.length - 1 && <div className="step-connector"></div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="container">
          <div className="benefits-content">
            <div className="benefits-text">
              <h2>Why Choose Our AI Platform?</h2>
              <div className="benefit-list">
                <div className="benefit-item">
                  <span className="benefit-icon">⏰</span>
                  <span>Save 80% of your document creation time</span>
                </div>
                <div className="benefit-item">
                  <span className="benefit-icon">🏆</span>
                  <span>Professional quality output every time</span>
                </div>
                <div className="benefit-item">
                  <span className="benefit-icon">🎯</span>
                  <span>No design or writing skills required</span>
                </div>
                <div className="benefit-item">
                  <span className="benefit-icon">🔄</span>
                  <span>Unlimited revisions and refinements</span>
                </div>
              </div>
            </div>
            <div className="benefits-visual">
              <div className="stats-container">
                <div className="stat-item">
                  <div className="stat-number">10,000+</div>
                  <div className="stat-label">Documents Created</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">500+</div>
                  <div className="stat-label">Happy Users</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">80%</div>
                  <div className="stat-label">Time Saved</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="container">
          <div className="section-header">
            <h2>What Our Users Say</h2>
            <p>Join thousands of professionals who trust our platform</p>
          </div>
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="testimonial-card">
                <div className="testimonial-quote">"{testimonial.quote}"</div>
                <div className="testimonial-author">
                  <div className="author-avatar">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div className="author-info">
                    <div className="author-name">{testimonial.name}</div>
                    <div className="author-role">{testimonial.role}, {testimonial.company}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Create Amazing Documents?</h2>
            <p>Join thousands of professionals already creating with AI</p>
            <button className="btn-primary large" onClick={handleGetStarted}>
              Start Creating Now
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>AI Document Platform</h3>
              <p>Transforming document creation with artificial intelligence.</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#api">API</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li><a href="#about">About</a></li>
                <li><a href="#careers">Careers</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Support</h4>
              <ul>
                <li><a href="#help">Help Center</a></li>
                <li><a href="#privacy">Privacy</a></li>
                <li><a href="#terms">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 AI Document Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;