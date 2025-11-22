import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

const Profile = () => {
  const { user, updateUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    bio: '',
    company: '',
    title: '',
    location: ''
  });
  const [stats, setStats] = useState({
    totalProjects: 0,
    documentsCreated: 0,
    timesSaved: 0,
    joinDate: ''
  });
  const [activities, setActivities] = useState([]);
  const [preferences, setPreferences] = useState({
    notifications: true,
    emailUpdates: false,
    autoSave: true,
    defaultFormat: 'word'
  });

  useEffect(() => {
    if (user) {
      // Load real profile data from backend
      loadProfileData();
      fetchUserStats();
      fetchUserActivities();
      fetchUserPreferences();
    }
  }, [user]);

  const loadProfileData = async () => {
    try {
      const profile = await authAPI.getProfile();
      setProfileData({
        name: profile.name || user?.name || '',
        email: profile.email || user?.email || '',
        bio: profile.bio || '',
        company: profile.company || '',
        title: profile.title || '',
        location: profile.location || ''
      });
    } catch (error) {
      console.error('Error loading profile:', error);
      // If API fails, try to use user data from context
      setProfileData({
        name: user?.name || user?.full_name || '',
        email: user?.email || '',
        bio: '',
        company: '',
        title: '',
        location: ''
      });
    }
  };

  const fetchUserStats = async () => {
    try {
      const response = await authAPI.getStats();
      setStats(response);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const fetchUserActivities = async () => {
    try {
      const response = await authAPI.getActivities();
      setActivities(response);
    } catch (error) {
      console.error('Error fetching user activities:', error);
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const response = await authAPI.getPreferences();
      setPreferences(response);
    } catch (error) {
      console.error('Error fetching user preferences:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveProfile = async () => {
    try {
      // Call backend API directly to save profile
      const updatedProfile = await authAPI.updateProfile(profileData);
      
      // Update the user context if the auth context has an update method
      if (updateUserProfile) {
        await updateUserProfile(profileData);
      }
      
      setIsEditing(false);
      alert('Profile updated successfully!');
      
      // Reload profile data to ensure it's saved and update the header
      await loadProfileData();
      
      // Force a page refresh to update all components
      window.location.reload();
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile. Please try again.');
    }
  };

  const handleSavePreferences = async () => {
    try {
      await authAPI.updatePreferences(preferences);
      alert('Preferences saved successfully!');
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Error saving preferences. Please try again.');
    }
  };

  const renderOverviewTab = () => (
    <div className="profile-overview">
      <div className="profile-stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <div className="stat-number">{stats.totalProjects}</div>
            <div className="stat-label">Total Projects</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📄</div>
          <div className="stat-content">
            <div className="stat-number">{stats.documentsCreated}</div>
            <div className="stat-label">Documents Created</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <div className="stat-number">{stats.timesSaved}h</div>
            <div className="stat-label">Time Saved</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-number">{stats.joinDate ? new Date(stats.joinDate).toLocaleDateString() : 'Recent'}</div>
            <div className="stat-label">Member Since</div>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {activities && activities.length > 0 ? (
            activities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  {activity.type === 'project_created' ? '📁' : 
                   activity.type === 'document_exported' ? '📄' : 
                   activity.type === 'content_generated' ? '✨' : '📝'}
                </div>
                <div className="activity-content">
                  <div className="activity-title">{activity.title}</div>
                  <div className="activity-time">
                    {activity.timestamp ? new Date(activity.timestamp).toLocaleDateString() : 'Recently'}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="activity-item">
              <div className="activity-icon">🎉</div>
              <div className="activity-content">
                <div className="activity-title">Welcome to AI Document Platform!</div>
                <div className="activity-time">Start creating your first project</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderPersonalInfoTab = () => (
    <div className="profile-personal-info">
      <div className="profile-form">
        <div className="form-header">
          <h3>Personal Information</h3>
          {!isEditing ? (
            <button className="btn-secondary" onClick={() => setIsEditing(true)}>
              Edit Profile
            </button>
          ) : (
            <div className="edit-buttons">
              <button className="btn-secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleSaveProfile}>
                Save Changes
              </button>
            </div>
          )}
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={profileData.name}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={profileData.email}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="company">Company</label>
            <input
              type="text"
              id="company"
              name="company"
              value={profileData.company}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="title">Job Title</label>
            <input
              type="text"
              id="title"
              name="title"
              value={profileData.title}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">Location</label>
            <input
              type="text"
              id="location"
              name="location"
              value={profileData.location}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-input"
            />
          </div>

          <div className="form-group full-width">
            <label htmlFor="bio">Bio</label>
            <textarea
              id="bio"
              name="bio"
              value={profileData.bio}
              onChange={handleInputChange}
              disabled={!isEditing}
              className="form-textarea"
              placeholder="Tell us about yourself..."
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderPreferencesTab = () => (
    <div className="profile-preferences">
      <div className="preferences-sections">
        <div className="preference-section">
          <h3>Notifications</h3>
          <div className="preference-item">
            <div className="preference-info">
              <span>In-app Notifications</span>
              <small>Receive notifications within the application</small>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.notifications}
                onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          
          <div className="preference-item">
            <div className="preference-info">
              <span>Email Updates</span>
              <small>Receive updates and news via email</small>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.emailUpdates}
                onChange={(e) => handlePreferenceChange('emailUpdates', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div className="preference-section">
          <h3>Editor Settings</h3>
          <div className="preference-item">
            <div className="preference-info">
              <span>Auto-save Documents</span>
              <small>Automatically save your work as you type</small>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.autoSave}
                onChange={(e) => handlePreferenceChange('autoSave', e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="preference-item">
            <div className="preference-info">
              <span>Default Export Format</span>
              <small>Default format for document exports</small>
            </div>
            <select
              value={preferences.defaultFormat}
              onChange={(e) => handlePreferenceChange('defaultFormat', e.target.value)}
              className="preference-select"
            >
              <option value="word">Microsoft Word (.docx)</option>
              <option value="powerpoint">PowerPoint (.pptx)</option>
              <option value="pdf">PDF (.pdf)</option>
            </select>
          </div>
        </div>

        <div className="preference-actions">
          <button className="btn-primary" onClick={handleSavePreferences}>
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="profile-security">
      <div className="security-sections">
        <div className="security-section">
          <h3>Password & Security</h3>
          <div className="security-item">
            <div className="security-info">
              <span>Change Password</span>
              <small>Update your account password</small>
            </div>
            <button className="btn-secondary">Change Password</button>
          </div>

          <div className="security-item">
            <div className="security-info">
              <span>Two-Factor Authentication</span>
              <small>Add an extra layer of security to your account</small>
            </div>
            <button className="btn-secondary">Enable 2FA</button>
          </div>
        </div>

        <div className="security-section">
          <h3>Account Data</h3>
          <div className="security-item">
            <div className="security-info">
              <span>Download Your Data</span>
              <small>Get a copy of your account information and projects</small>
            </div>
            <button className="btn-secondary">Download Data</button>
          </div>

          <div className="security-item danger">
            <div className="security-info">
              <span>Delete Account</span>
              <small>Permanently delete your account and all data</small>
            </div>
            <button className="btn-danger">Delete Account</button>
          </div>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'personal', label: 'Personal Info', icon: '👤' },
    { id: 'preferences', label: 'Preferences', icon: '⚙️' },
    { id: 'security', label: 'Security', icon: '🔒' }
  ];

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">
            {profileData.name ? profileData.name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="profile-info">
            <h1>{profileData.name || 'User'}</h1>
            <p className="profile-email">{profileData.email}</p>
            {profileData.title && profileData.company && (
              <p className="profile-role">{profileData.title} at {profileData.company}</p>
            )}
          </div>
        </div>

        <div className="profile-content">
          <div className="profile-tabs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="tab-icon">{tab.icon}</span>
                <span className="tab-label">{tab.label}</span>
              </button>
            ))}
          </div>

          <div className="profile-tab-content">
            {activeTab === 'overview' && renderOverviewTab()}
            {activeTab === 'personal' && renderPersonalInfoTab()}
            {activeTab === 'preferences' && renderPreferencesTab()}
            {activeTab === 'security' && renderSecurityTab()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;