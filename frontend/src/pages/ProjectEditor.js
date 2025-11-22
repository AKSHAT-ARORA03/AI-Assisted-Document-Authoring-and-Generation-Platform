import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Sparkles, 
  ThumbsUp, 
  ThumbsDown,
  MessageSquare,
  History,
  RefreshCw,
  Save
} from 'lucide-react';
import { 
  projectsAPI, 
  generationAPI, 
  refinementAPI, 
  exportAPI 
} from '../services/api';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';

const ProjectEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState({});
  const [refinementPrompts, setRefinementPrompts] = useState({});
  const [refinementResults, setRefinementResults] = useState({});
  const [comments, setComments] = useState({});

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      const projectData = await projectsAPI.getProject(id);
      setProject(projectData);
    } catch (error) {
      toast.error('Error loading project');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async (itemId, isSlide = false) => {
    setGenerating({ ...generating, [itemId]: true });
    
    try {
      let result;
      if (isSlide) {
        result = await generationAPI.generateSlideContent(project.id, itemId);
      } else {
        result = await generationAPI.generateSectionContent(project.id, itemId);
      }
      
      // Update project state
      const updatedProject = { ...project };
      const items = isSlide ? updatedProject.slides : updatedProject.sections;
      const itemIndex = items.findIndex(item => item.id === itemId);
      
      if (itemIndex !== -1) {
        items[itemIndex].content = result.content;
        items[itemIndex].generated_at = result.generated_at;
        setProject(updatedProject);
      }
      
      toast.success('Content generated successfully!');
    } catch (error) {
      toast.error('Error generating content');
      console.error(error);
    } finally {
      setGenerating({ ...generating, [itemId]: false });
    }
  };

  const generateAllContent = async () => {
    try {
      toast.loading('Generating all content...');
      const result = await generationAPI.generateAllSections(project.id);
      
      // Update project state
      const updatedProject = { ...project };
      if (project.document_type === 'docx') {
        updatedProject.sections = result.sections;
      } else {
        updatedProject.slides = result.slides;
      }
      updatedProject.status = 'completed';
      setProject(updatedProject);
      
      toast.dismiss();
      toast.success('All content generated successfully!');
    } catch (error) {
      toast.dismiss();
      toast.error('Error generating all content');
      console.error(error);
    }
  };

  const refineContent = async (itemId) => {
    const prompt = refinementPrompts[itemId];
    if (!prompt?.trim()) {
      toast.error('Please enter a refinement prompt');
      return;
    }

    try {
      const result = await refinementAPI.refineContent(project.id, itemId, prompt);
      setRefinementResults({ ...refinementResults, [itemId]: result });
      setRefinementPrompts({ ...refinementPrompts, [itemId]: '' });
      toast.success('Content refined successfully!');
    } catch (error) {
      toast.error('Error refining content');
      console.error(error);
    }
  };

  const acceptRefinement = async (itemId) => {
    try {
      await refinementAPI.acceptRefinement(project.id, itemId);
      
      // Update project state
      const updatedProject = { ...project };
      const items = project.document_type === 'docx' ? updatedProject.sections : updatedProject.slides;
      const itemIndex = items.findIndex(item => item.id === itemId);
      
      if (itemIndex !== -1) {
        items[itemIndex].content = refinementResults[itemId].refined_content;
      }
      
      setProject(updatedProject);
      setRefinementResults({ ...refinementResults, [itemId]: null });
      toast.success('Refinement accepted!');
    } catch (error) {
      toast.error('Error accepting refinement');
    }
  };

  const rejectRefinement = (itemId) => {
    setRefinementResults({ ...refinementResults, [itemId]: null });
    toast.success('Refinement rejected');
  };

  const submitFeedback = async (itemId, liked) => {
    try {
      await refinementAPI.submitFeedback(project.id, itemId, {
        liked,
        comment: comments[itemId] || ''
      });
      setComments({ ...comments, [itemId]: '' });
      toast.success('Feedback submitted!');
    } catch (error) {
      toast.error('Error submitting feedback');
    }
  };

  const exportDocument = async () => {
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
      toast.success('Document downloaded successfully!');
    } catch (error) {
      toast.dismiss();
      toast.error('Error downloading document');
      console.error(error);
    }
  };

  const renderContent = (item, isSlide = false) => {
    const itemId = item.id;
    const content = item.content;
    const hasRefinement = refinementResults[itemId];

    return (
      <div className="space-y-4">
        {/* Content display */}
        <div className="bg-secondary-50 rounded-lg p-4">
          {content ? (
            isSlide ? (
              <ul className="list-disc pl-6 space-y-2">
                {(Array.isArray(content) ? content : [content]).map((bullet, idx) => (
                  <li key={idx} className="text-secondary-700">{bullet}</li>
                ))}
              </ul>
            ) : (
              <p className="text-secondary-700 whitespace-pre-wrap">{content}</p>
            )
          ) : (
            <div className="text-center py-8">
              <p className="text-secondary-500 mb-4">No content generated yet</p>
              <button
                onClick={() => generateContent(itemId, isSlide)}
                disabled={generating[itemId]}
                className="btn-primary inline-flex items-center space-x-2"
              >
                {generating[itemId] ? (
                  <>
                    <LoadingSpinner size="small" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    <span>Generate Content</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Refinement result */}
        {hasRefinement && (
          <div className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-yellow-800">Refined Content</h4>
              <div className="flex space-x-2">
                <button
                  onClick={() => acceptRefinement(itemId)}
                  className="text-green-600 hover:text-green-700 text-sm font-medium"
                >
                  Accept
                </button>
                <button
                  onClick={() => rejectRefinement(itemId)}
                  className="text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  Reject
                </button>
              </div>
            </div>
            
            <div className="bg-white rounded p-3">
              {isSlide ? (
                <ul className="list-disc pl-6 space-y-2">
                  {(Array.isArray(hasRefinement.refined_content) 
                    ? hasRefinement.refined_content 
                    : hasRefinement.refined_content.split('\n').filter(Boolean)
                  ).map((bullet, idx) => (
                    <li key={idx} className="text-secondary-700">{bullet}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-secondary-700 whitespace-pre-wrap">
                  {hasRefinement.refined_content}
                </p>
              )}
            </div>
          </div>
        )}

        {content && (
          <div className="space-y-4">
            {/* Refinement input */}
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Enter refinement instructions (e.g., 'Make it more formal', 'Shorten to 100 words')"
                value={refinementPrompts[itemId] || ''}
                onChange={(e) => setRefinementPrompts({
                  ...refinementPrompts,
                  [itemId]: e.target.value
                })}
                className="flex-1 input-field"
              />
              <button
                onClick={() => refineContent(itemId)}
                className="btn-outline flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refine</span>
              </button>
            </div>

            {/* Feedback */}
            <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-secondary-600">How is this content?</span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => submitFeedback(itemId, true)}
                    className="flex items-center space-x-1 text-green-600 hover:text-green-700"
                  >
                    <ThumbsUp className="h-4 w-4" />
                    <span className="text-sm">Good</span>
                  </button>
                  <button
                    onClick={() => submitFeedback(itemId, false)}
                    className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                  >
                    <ThumbsDown className="h-4 w-4" />
                    <span className="text-sm">Needs work</span>
                  </button>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Add a comment..."
                  value={comments[itemId] || ''}
                  onChange={(e) => setComments({
                    ...comments,
                    [itemId]: e.target.value
                  })}
                  className="px-3 py-1 border border-secondary-300 rounded text-sm"
                />
                <button
                  onClick={() => submitFeedback(itemId, null)}
                  className="text-primary-600 hover:text-primary-700"
                >
                  <MessageSquare className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <p className="text-red-600">Project not found</p>
        </div>
      </div>
    );
  }

  const items = project.document_type === 'docx' ? project.sections || [] : project.slides || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-start space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-secondary-600 hover:text-secondary-900"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Dashboard
          </button>
          
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">{project.title}</h1>
            <p className="text-secondary-600 mt-1">{project.topic}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={generateAllContent}
            className="btn-outline flex items-center space-x-2"
          >
            <Sparkles className="h-5 w-5" />
            <span>Generate All</span>
          </button>
          
          <button
            onClick={exportDocument}
            className="btn-primary flex items-center space-x-2"
          >
            <Download className="h-5 w-5" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Content sections/slides */}
      <div className="space-y-8">
        {items.map((item, index) => (
          <div key={item.id} className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">
                {project.document_type === 'docx' ? 'Section' : 'Slide'} {index + 1}: {item.title}
              </h2>
              
              {item.content && (
                <div className="flex items-center space-x-2 text-sm text-secondary-500">
                  <History className="h-4 w-4" />
                  <span>
                    Generated {item.generated_at ? new Date(item.generated_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              )}
            </div>
            
            {renderContent(item, project.document_type === 'pptx')}
          </div>
        ))}
      </div>

      {items.length === 0 && (
        <div className="text-center py-12">
          <p className="text-secondary-500 mb-4">No content structure found</p>
          <button
            onClick={() => navigate(`/projects/new`)}
            className="btn-primary"
          >
            Configure Structure
          </button>
        </div>
      )}
    </div>
  );
};

export default ProjectEditor;