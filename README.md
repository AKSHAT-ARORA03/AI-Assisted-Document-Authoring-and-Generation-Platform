# AI-Assisted Document Authoring Platform

A modern, full-stack application that leverages artificial intelligence to help users create, edit, and export professional documents with ease. Built with React and FastAPI, featuring dark/light theme support, real-time editing, and seamless document export capabilities.

## 🚀 Features

### Core Functionality
- **AI-Powered Document Generation**: Create documents using advanced AI models (Google Gemini)
- **Real-time Document Editing**: Interactive document editor with live preview
- **Multi-format Export**: Export documents to PDF, DOCX, and PPTX formats
- **Project Management**: Organize and manage multiple document projects
- **User Profiles**: Personalized user experience with profile management

### User Experience
- **Responsive Design**: Mobile-first, fully responsive interface
- **Dark/Light Theme**: Toggle between themes with persistent preference
- **Professional UI**: Modern, clean interface with intuitive navigation
- **Real-time Feedback**: Instant loading states and error handling

### Technical Features
- **Universal User Support**: Flexible authentication with guest and registered users
- **RESTful API**: Well-structured backend with comprehensive endpoints
- **Database Integration**: MongoDB Atlas for scalable data persistence
- **Secure Authentication**: JWT-based authentication with proper validation
- **Error Handling**: Comprehensive error handling and user feedback

## 🛠️ Technology Stack

### Frontend
- **React 18**: Modern JavaScript framework with hooks and context
- **React Router DOM**: Client-side routing and navigation
- **CSS3**: Custom styling with CSS variables for dynamic theming
- **Fetch API**: Native HTTP client for API communication

### Backend
- **FastAPI**: Modern Python web framework with automatic documentation
- **Python 3.9+**: Core programming language
- **MongoDB Atlas**: Cloud NoSQL database with global clusters
- **Uvicorn**: High-performance ASGI server
- **Pydantic**: Data validation and settings management

### AI Integration
- **Google Gemini AI**: Advanced language model for document generation
- **Multiple Model Support**: Fallback mechanisms for reliability
- **Content Refinement**: AI-powered content improvement

### Document Processing
- **python-docx**: Microsoft Word document generation
- **python-pptx**: PowerPoint presentation creation
- **ReportLab**: PDF generation capabilities

## 📋 Prerequisites

Before running this application, ensure you have:

- **Python 3.9 or higher**
- **Node.js 16 or higher**
- **npm or yarn package manager**
- **MongoDB Atlas account** (free tier available)
- **Google AI API key** (Gemini Pro)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-assisted-document-authoring.git
cd ai-assisted-document-authoring
```

### 2. Environment Setup

#### Backend Environment
Create a `.env` file in the `backend/` directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_document_db?retryWrites=true&w=majority
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/ai_document_db?retryWrites=true&w=majority

# AI Service Configuration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
GEMINI_API_KEY=your_google_ai_api_key_here

# Authentication Settings
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
FRONTEND_URL=http://localhost:3000
```

#### Frontend Environment
Create a `.env` file in the `frontend/` directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 3. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory (new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📚 Usage Guide

### Getting Started
1. **Launch the Application**: Access http://localhost:3000
2. **Welcome Screen**: Review the professional landing page
3. **Authentication**: Register a new account or use guest mode
4. **Dashboard Access**: Navigate to your personalized dashboard

### Creating Documents
1. **New Project**: Click "Create New Project" from the dashboard
2. **Project Configuration**: Set up document type and structure
3. **AI Generation**: Use AI-powered content generation
4. **Content Refinement**: Polish and customize your document
5. **Export Options**: Download in preferred format (PDF, DOCX, PPTX)

### Profile Management
- **Theme Preference**: Toggle between dark and light modes
- **Personal Information**: Update profile details and preferences
- **Project History**: View and manage document projects
- **Settings**: Customize application behavior

### Advanced Features
- **Document Templates**: Use pre-built templates for common document types
- **AI Content Refinement**: Improve existing content with AI assistance
- **Collaborative Features**: Share and collaborate on projects
- **Export Customization**: Advanced export options and formatting

## 🏗️ Project Structure

```
ai-assisted-document-authoring/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Application entry point & CORS setup
│   │   ├── models/            # Database models
│   │   │   ├── user.py        # User data models
│   │   │   └── project.py     # Project data models
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── projects.py    # Project CRUD operations
│   │   │   ├── profile.py     # User profile management
│   │   │   ├── generation.py  # AI document generation
│   │   │   ├── refinement.py  # Document content refinement
│   │   │   └── export.py      # Document export functionality
│   │   ├── services/          # Business logic layer
│   │   │   ├── ai_service.py  # Google Gemini integration
│   │   │   └── document_service.py  # Document processing
│   │   └── utils/             # Utility functions
│   │       ├── auth.py        # JWT authentication utilities
│   │       ├── database.py    # MongoDB connection
│   │       └── memory_store.py # In-memory data management
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend application
│   ├── public/
│   │   ├── index.html        # HTML template
│   │   └── manifest.json     # PWA configuration
│   ├── src/
│   │   ├── App.js            # Main application component
│   │   ├── index.js          # React application entry point
│   │   ├── index.css         # Global styles
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Header.js     # Navigation header
│   │   │   ├── LoadingSpinner.js  # Loading indicators
│   │   │   ├── ProtectedRoute.js  # Route protection
│   │   │   └── ThemeToggle.js     # Dark/light theme switch
│   │   ├── pages/            # Page components
│   │   │   ├── Home.js       # Landing page
│   │   │   ├── Dashboard.js  # User dashboard
│   │   │   ├── Profile.js    # Profile management
│   │   │   ├── Login.js      # Authentication
│   │   │   ├── Register.js   # User registration
│   │   │   ├── ProjectEditor.js  # Document editor
│   │   │   └── NewProject.js     # Project creation
│   │   ├── context/          # React contexts
│   │   │   ├── AuthContext.js    # Authentication state
│   │   │   └── ThemeContext.js   # Theme management
│   │   ├── services/         # API communication
│   │   │   ├── api.js        # API client
│   │   │   └── authService.js    # Authentication service
│   │   └── styles/
│   │       └── theme.css     # Theme definitions
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── postcss.config.js     # PostCSS configuration
├── .gitignore               # Git ignore rules
└── README.md               # Project documentation
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration with validation
- `POST /auth/login` - User authentication and token generation
- `GET /auth/me` - Get current authenticated user information
- `POST /auth/logout` - User logout and token invalidation

### Projects
- `GET /projects/` - List all user projects with pagination
- `POST /projects/` - Create new project with validation
- `GET /projects/{id}` - Get specific project details
- `PUT /projects/{id}` - Update project information
- `DELETE /projects/{id}` - Delete project and associated data

### Profile Management
- `GET /profile/` - Get user profile information
- `PUT /profile/` - Update user profile with validation
- `GET /profile/preferences` - Get user preferences
- `PUT /profile/preferences` - Update user preferences

### AI Document Generation
- `POST /generation/generate` - Generate document content using AI
- `POST /generation/sections` - Generate specific sections
- `GET /generation/templates` - Get available document templates

### Content Refinement
- `POST /refinement/refine` - Refine document sections
- `POST /refinement/improve` - Improve content quality
- `POST /refinement/suggestions` - Get improvement suggestions

### Document Export
- `POST /export/pdf` - Export document to PDF format
- `POST /export/docx` - Export to Microsoft Word format
- `POST /export/pptx` - Export to PowerPoint presentation
- `GET /export/status/{id}` - Check export job status

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Token Expiration**: Configurable token expiration times
- **Role-based Access**: User role and permission management

### Data Protection
- **Input Validation**: Comprehensive Pydantic model validation
- **SQL Injection Prevention**: MongoDB query parameterization
- **XSS Protection**: Input sanitization and output encoding
- **CORS Configuration**: Secure cross-origin resource sharing

### Infrastructure Security
- **Environment Variables**: Sensitive data stored securely
- **HTTPS Support**: SSL/TLS encryption for production
- **Rate Limiting**: API endpoint protection against abuse
- **Error Handling**: Secure error responses without data leakage

## 🚀 Deployment

### Production Environment Setup

#### Backend Deployment (Railway/Heroku/DigitalOcean)
1. **Environment Configuration**: Set production environment variables
2. **Database Setup**: Configure MongoDB Atlas production cluster
3. **Security**: Enable HTTPS and configure secure headers
4. **Monitoring**: Set up logging and error tracking

```bash
# Production start command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Frontend Deployment (Netlify/Vercel)
1. **Build Optimization**: Create production build
2. **Environment Variables**: Configure production API endpoints
3. **CDN Configuration**: Set up content delivery network
4. **Analytics**: Implement usage analytics

```bash
# Production build
npm run build
```

### Docker Deployment
Create `docker-compose.yml` for containerized deployment:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=${MONGODB_URI}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Test Coverage
- **Backend**: Unit tests for API endpoints and business logic
- **Frontend**: Component tests and integration tests
- **E2E**: End-to-end testing with Playwright/Cypress

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Follow Code Standards**: Use ESLint/Prettier for frontend, Black for backend
4. **Write Tests**: Include appropriate test coverage
5. **Commit Changes**: `git commit -m 'Add amazing feature'`
6. **Push Branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**: Provide detailed description

### Development Guidelines
- **Code Style**: Follow established formatting standards
- **Documentation**: Update documentation for new features
- **Testing**: Maintain test coverage above 80%
- **Security**: Follow security best practices

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.9+

# Verify dependencies
pip install -r requirements.txt

# Check environment variables
echo $MONGODB_URI
echo $GEMINI_API_KEY
```

#### Frontend Build Fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 16+
```

#### Database Connection Issues
- Verify MongoDB Atlas connection string format
- Check IP whitelist settings in MongoDB Atlas console
- Ensure network connectivity and firewall settings
- Validate username/password credentials

#### AI Service Errors
- Verify Google AI API key is valid and active
- Check API quota and billing status
- Monitor API usage limits
- Review network connectivity

#### Theme/Styling Issues
- Clear browser cache and local storage
- Check CSS variable definitions
- Verify theme context provider setup
- Review responsive design breakpoints

## 📊 Performance Optimization

### Backend Optimization
- **Database Indexing**: Optimize MongoDB queries
- **Caching**: Implement Redis for frequent operations
- **Connection Pooling**: Optimize database connections
- **API Pagination**: Implement efficient data pagination

### Frontend Optimization
- **Code Splitting**: Lazy load components and routes
- **Bundle Analysis**: Optimize webpack bundle size
- **Image Optimization**: Compress and optimize images
- **Performance Monitoring**: Track Core Web Vitals

## 📞 Support & Documentation

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **API Documentation**: http://localhost:8000/docs
- **Code Comments**: Comprehensive inline documentation
- **Wiki**: Additional guides and tutorials

### Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **MongoDB Atlas**: https://www.mongodb.com/atlas
- **Google AI Platform**: https://ai.google.dev/

## 🔮 Roadmap & Future Enhancements

### Short Term (Next Sprint)
- [ ] Real-time collaboration features
- [ ] Advanced document templates
- [ ] Enhanced AI model integration
- [ ] Mobile app development

### Medium Term (3-6 months)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Third-party integrations
- [ ] Enterprise features

### Long Term (6+ months)
- [ ] AI model fine-tuning
- [ ] Advanced document workflows
- [ ] White-label solutions
- [ ] API monetization

---

**Built with ❤️ using React and FastAPI**

*This project demonstrates modern full-stack development practices with AI integration, suitable for educational purposes, portfolio projects, and production deployment.*

## 🏆 Achievement Highlights

- ✅ **Full-Stack Architecture**: Complete separation of concerns
- ✅ **AI Integration**: Advanced language model implementation
- ✅ **Responsive Design**: Mobile-first development approach
- ✅ **Security Best Practices**: JWT authentication and data protection
- ✅ **Professional UI/UX**: Modern design principles and accessibility
- ✅ **Scalable Database**: Cloud-native MongoDB implementation
- ✅ **Production Ready**: Deployment-ready configuration and documentation