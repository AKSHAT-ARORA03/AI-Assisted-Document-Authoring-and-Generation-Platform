import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },

  devLogin: async () => {
    const response = await api.post('/auth/dev-login');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/auth/profile', profileData);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/auth/stats');
    return response.data;
  },

  getActivities: async () => {
    const response = await api.get('/auth/activities');
    return response.data;
  },

  getPreferences: async () => {
    const response = await api.get('/auth/preferences');
    return response.data;
  },

  updatePreferences: async (preferences) => {
    const response = await api.put('/auth/preferences', preferences);
    return response.data;
  },

  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// Projects API
export const projectsAPI = {
  getProjects: async (params = {}) => {
    const response = await api.get('/projects', { params });
    return response.data;
  },

  getProject: async (id) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  createProject: async (projectData) => {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  updateProject: async (id, projectData) => {
    const response = await api.put(`/projects/${id}`, projectData);
    return response.data;
  },

  deleteProject: async (id) => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  }
};

// Generation API
export const generationAPI = {
  generateOutline: async (projectId, numSections = 5) => {
    const response = await api.post(`/generation/outline/${projectId}`, {}, {
      params: { num_sections: numSections }
    });
    return response.data;
  },

  generateSectionContent: async (projectId, sectionId, customPrompt = null) => {
    const response = await api.post(`/generation/section/${projectId}/${sectionId}`, {
      custom_prompt: customPrompt
    });
    return response.data;
  },

  generateSlideContent: async (projectId, slideId, customPrompt = null) => {
    const response = await api.post(`/generation/slide/${projectId}/${slideId}`, {
      custom_prompt: customPrompt
    });
    return response.data;
  },

  generateAllSections: async (projectId) => {
    const response = await api.post(`/generation/all-sections/${projectId}`);
    return response.data;
  }
};

// Refinement API
export const refinementAPI = {
  refineContent: async (projectId, sectionId, prompt) => {
    const response = await api.post(`/refinement/refine/${projectId}/${sectionId}`, {
      prompt
    });
    return response.data;
  },

  acceptRefinement: async (projectId, sectionId) => {
    const response = await api.post(`/refinement/accept/${projectId}/${sectionId}`);
    return response.data;
  },

  submitFeedback: async (projectId, sectionId, feedback) => {
    const response = await api.post(`/refinement/feedback/${projectId}/${sectionId}`, feedback);
    return response.data;
  },

  getRefinementHistory: async (projectId, sectionId) => {
    const response = await api.get(`/refinement/history/${projectId}/${sectionId}`);
    return response.data;
  }
};

// Export API
export const exportAPI = {
  exportDocument: async (projectId) => {
    const response = await api.get(`/export/${projectId}`, {
      responseType: 'blob'
    });
    return response;
  },

  previewDocument: async (projectId) => {
    const response = await api.get(`/export/${projectId}/preview`);
    return response.data;
  }
};

export default api;