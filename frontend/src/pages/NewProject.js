import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Presentation, ArrowLeft, Sparkles, Plus, Trash2 } from 'lucide-react';
import { projectsAPI, generationAPI } from '../services/api';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const NewProject = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    topic: '',
    description: '',
    document_type: 'docx'
  });
  const [structure, setStructure] = useState([]);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleNext = () => {
    if (step === 1) {
      if (!formData.title.trim() || !formData.topic.trim()) {
        toast.error('Please fill in all required fields');
        return;
      }
    }
    setStep(step + 1);
  };

  const generateAIOutline = async () => {
    setLoading(true);
    try {
      // Create a temporary project to get AI outline
      const tempProject = await projectsAPI.createProject({
        ...formData,
        sections: formData.document_type === 'docx' ? [] : undefined,
        slides: formData.document_type === 'pptx' ? [] : undefined
      });

      const outline = await generationAPI.generateOutline(tempProject.id, 5);
      
      if (formData.document_type === 'docx') {
        setStructure(outline.sections || []);
      } else {
        setStructure(outline.slides || []);
      }
      
      // Clean up temporary project
      await projectsAPI.deleteProject(tempProject.id);
      
      toast.success('AI outline generated successfully!');
    } catch (error) {
      toast.error('Error generating AI outline');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const addSection = () => {
    const newSection = {
      id: Date.now().toString(),
      title: '',
      order: structure.length + 1
    };
    setStructure([...structure, newSection]);
  };

  const updateSection = (id, title) => {
    setStructure(structure.map(item => 
      item.id === id ? { ...item, title } : item
    ));
  };

  const removeSection = (id) => {
    setStructure(structure.filter(item => item.id !== id));
  };

  const moveSection = (index, direction) => {
    const newStructure = [...structure];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (targetIndex >= 0 && targetIndex < newStructure.length) {
      [newStructure[index], newStructure[targetIndex]] = [newStructure[targetIndex], newStructure[index]];
      
      // Update order
      newStructure.forEach((item, idx) => {
        item.order = idx + 1;
      });
      
      setStructure(newStructure);
    }
  };

  const createProject = async () => {
    if (structure.length === 0) {
      toast.error('Please add at least one section/slide');
      return;
    }

    setLoading(true);
    try {
      const projectData = {
        ...formData,
        sections: formData.document_type === 'docx' ? structure : undefined,
        slides: formData.document_type === 'pptx' ? structure : undefined
      };

      const project = await projectsAPI.createProject(projectData);
      toast.success('Project created successfully!');
      navigate(`/projects/${project.id}/edit`);
    } catch (error) {
      toast.error('Error creating project');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-secondary-600 hover:text-secondary-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to Dashboard
        </button>
        
        <h1 className="text-3xl font-bold text-secondary-900">Create New Project</h1>
        <p className="text-secondary-600 mt-2">
          {step === 1 ? 'Choose your document type and provide basic information' :
           'Configure your document structure'}
        </p>
      </div>

      {step === 1 && (
        <div className="space-y-8">
          {/* Document type selection */}
          <div>
            <h2 className="text-xl font-semibold text-secondary-900 mb-4">
              Choose Document Type
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => setFormData({ ...formData, document_type: 'docx' })}
                className={`p-6 rounded-lg border-2 transition-all ${
                  formData.document_type === 'docx'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-secondary-200 hover:border-secondary-300'
                }`}
              >
                <FileText className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-secondary-900">Word Document</h3>
                <p className="text-secondary-600 text-sm">
                  Create professional documents with structured sections
                </p>
              </button>

              <button
                onClick={() => setFormData({ ...formData, document_type: 'pptx' })}
                className={`p-6 rounded-lg border-2 transition-all ${
                  formData.document_type === 'pptx'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-secondary-200 hover:border-secondary-300'
                }`}
              >
                <Presentation className="h-12 w-12 text-orange-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-secondary-900">PowerPoint Presentation</h3>
                <p className="text-secondary-600 text-sm">
                  Create engaging presentations with slide-based content
                </p>
              </button>
            </div>
          </div>

          {/* Project details */}
          <div className="card">
            <h2 className="text-xl font-semibold text-secondary-900 mb-6">
              Project Details
            </h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Project Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Enter a title for your project"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Main Topic *
                </label>
                <input
                  type="text"
                  name="topic"
                  value={formData.topic}
                  onChange={handleInputChange}
                  placeholder="What is your document about?"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  placeholder="Provide additional context or requirements"
                  className="input-field"
                />
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                onClick={handleNext}
                className="btn-primary"
              >
                Continue to Structure
              </button>
            </div>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-8">
          {/* AI outline generation */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">
                Document Structure
              </h2>
              <button
                onClick={generateAIOutline}
                disabled={loading}
                className="btn-outline flex items-center space-x-2"
              >
                <Sparkles className="h-5 w-5" />
                <span>{loading ? 'Generating...' : 'AI Suggest Outline'}</span>
                {loading && <LoadingSpinner size="small" />}
              </button>
            </div>
            
            <p className="text-secondary-600 mb-6">
              Add {formData.document_type === 'docx' ? 'sections' : 'slides'} to your document or let AI suggest an outline based on your topic.
            </p>

            {/* Structure list */}
            <div className="space-y-3 mb-6">
              {structure.map((item, index) => (
                <div
                  key={item.id}
                  className="flex items-center space-x-3 p-3 border border-secondary-200 rounded-lg"
                >
                  <span className="text-sm text-secondary-500 w-6">
                    {index + 1}
                  </span>
                  
                  <input
                    type="text"
                    value={item.title}
                    onChange={(e) => updateSection(item.id, e.target.value)}
                    placeholder={`${formData.document_type === 'docx' ? 'Section' : 'Slide'} title`}
                    className="flex-1 px-3 py-2 border border-secondary-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => moveSection(index, 'up')}
                      disabled={index === 0}
                      className="p-1 text-secondary-400 hover:text-secondary-600 disabled:opacity-30"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => moveSection(index, 'down')}
                      disabled={index === structure.length - 1}
                      className="p-1 text-secondary-400 hover:text-secondary-600 disabled:opacity-30"
                    >
                      ↓
                    </button>
                    <button
                      onClick={() => removeSection(item.id)}
                      className="p-1 text-red-400 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Add section button */}
            <button
              onClick={addSection}
              className="btn-outline flex items-center space-x-2 w-full"
            >
              <Plus className="h-5 w-5" />
              <span>Add {formData.document_type === 'docx' ? 'Section' : 'Slide'}</span>
            </button>

            {/* Navigation */}
            <div className="flex justify-between mt-8 pt-6 border-t border-secondary-200">
              <button
                onClick={() => setStep(1)}
                className="btn-secondary"
              >
                Back
              </button>
              
              <button
                onClick={createProject}
                disabled={loading || structure.length === 0}
                className="btn-primary disabled:opacity-50"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="small" />
                    <span>Creating Project...</span>
                  </div>
                ) : (
                  'Create Project'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewProject;