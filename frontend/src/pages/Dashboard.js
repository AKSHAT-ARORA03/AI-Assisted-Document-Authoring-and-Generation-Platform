import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  FileText, 
  Presentation, 
  Calendar,
  MoreVertical,
  Edit,
  Trash2,
  Download
} from 'lucide-react';
import { projectsAPI, exportAPI } from '../services/api';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const [menuOpen, setMenuOpen] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const projectsData = await projectsAPI.getProjects({
        search: searchTerm,
        document_type: filter !== 'all' ? filter : undefined
      });
      setProjects(projectsData);
    } catch (error) {
      toast.error('Error fetching projects');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setLoading(true);
    fetchProjects();
  };

  const handleDelete = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectsAPI.deleteProject(projectId);
        setProjects(projects.filter(p => p.id !== projectId));
        toast.success('Project deleted successfully');
      } catch (error) {
        toast.error('Error deleting project');
      }
    }
    setMenuOpen(null);
  };

  const handleExport = async (project) => {
    try {
      toast.loading('Preparing document for download...');
      const response = await exportAPI.exportDocument(project.id);
      
      // Create download link
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const filename = `${project.title}.${project.document_type}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.dismiss();
      toast.success('Document downloaded successfully');
    } catch (error) {
      toast.dismiss();
      toast.error('Error downloading document');
      console.error(error);
    }
    setMenuOpen(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'generating':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">Your Projects</h1>
        <p className="text-secondary-600 mt-2">
          Manage and create professional documents with AI assistance
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        {/* Search and filter */}
        <div className="flex flex-col sm:flex-row gap-4 flex-1 max-w-lg">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="input-field pl-10"
            />
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-field min-w-32"
          >
            <option value="all">All Types</option>
            <option value="docx">Word Docs</option>
            <option value="pptx">PowerPoint</option>
          </select>
        </div>

        {/* New project button */}
        <Link
          to="/projects/new"
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-5 w-5" />
          <span>New Project</span>
        </Link>
      </div>

      {/* Projects grid */}
      {projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="card hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/projects/${project.id}/edit`)}
            >
              {/* Project header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {project.document_type === 'docx' ? (
                    <FileText className="h-8 w-8 text-blue-600" />
                  ) : (
                    <Presentation className="h-8 w-8 text-orange-600" />
                  )}
                  <div>
                    <h3 className="text-lg font-semibold text-secondary-900 line-clamp-1">
                      {project.title}
                    </h3>
                    <p className="text-sm text-secondary-500">
                      {project.document_type === 'docx' ? 'Word Document' : 'PowerPoint'}
                    </p>
                  </div>
                </div>
                
                {/* Menu */}
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setMenuOpen(menuOpen === project.id ? null : project.id);
                    }}
                    className="p-1 rounded-full hover:bg-secondary-100 transition-colors"
                  >
                    <MoreVertical className="h-5 w-5 text-secondary-400" />
                  </button>
                  
                  {menuOpen === project.id && (
                    <div className="absolute right-0 top-8 bg-white shadow-lg rounded-lg border border-secondary-200 py-1 z-10 min-w-40">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/projects/${project.id}/edit`);
                        }}
                        className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExport(project);
                        }}
                        className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
                      >
                        <Download className="h-4 w-4" />
                        <span>Download</span>
                      </button>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(project.id);
                        }}
                        className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Project details */}
              <p className="text-secondary-600 text-sm mb-4 line-clamp-2">
                {project.topic}
              </p>

              {/* Status and date */}
              <div className="flex items-center justify-between">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </span>
                
                <div className="flex items-center space-x-1 text-xs text-secondary-500">
                  <Calendar className="h-4 w-4" />
                  <span>{formatDate(project.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        // Empty state
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            No projects yet
          </h3>
          <p className="text-secondary-500 mb-6">
            Get started by creating your first AI-powered document
          </p>
          <Link
            to="/projects/new"
            className="btn-primary inline-flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>Create Your First Project</span>
          </Link>
        </div>
      )}
    </div>
  );
};

export default Dashboard;