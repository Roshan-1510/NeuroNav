# NeuroNav 🧠

**AI-Powered Personalized Learning Roadmap Generator Based on Brain Types**

NeuroNav creates personalized learning paths using VARK assessment (Visual, Auditory, Reading/Writing, Kinesthetic) and AI-powered content generation to optimize learning experiences for individual cognitive preferences.

## ✨ Key Features

- **🧠 VARK Brain Type Assessment**: 10-question quiz to identify learning preferences
- **🤖 AI-Powered Roadmaps**: Uses Meta Llama 3.3 8B Instruct via OpenRouter API
- **📚 Personalized Content**: Learning resources tailored to brain types
- **📊 Progress Tracking**: Real-time dashboard with completion metrics
- **🎯 Smart Learning Tips**: Brain-type specific study strategies
- **🔄 Dynamic Updates**: Auto-refreshing dashboard and progress sync
- **✏️ Roadmap Management**: Add, edit, delete steps and entire roadmaps
- **🎨 Modern UI**: Clean, responsive design with Tailwind CSS

## 🛠 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: JWT tokens
- **AI Integration**: OpenRouter API (Meta Llama 3.3 8B Instruct)
- **Environment**: Python 3.10+

### Frontend  
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **Routing**: React Router
- **State Management**: React hooks + Context

### AI & APIs
- **AI Provider**: OpenRouter (https://openrouter.ai)
- **Model**: Meta Llama 3.3 8B Instruct
- **Features**: Brain-type specific prompting, JSON response parsing, fallback handling

## 🎯 Key Features

### 🧠 AI-Powered Personalization
- **Brain Type Assessment**: 4-question quiz determines learning style (Visual, Auditory, Reading/Writing, Kinesthetic)
- **Meta Llama 3.3 8B Integration**: Advanced AI generates personalized roadmaps based on user preferences
- **Adaptive Content**: Roadmaps tailored to individual learning patterns and career goals

### 📚 Learning Management
- **Custom Roadmaps**: AI-generated learning paths for various tech topics
- **Progress Tracking**: Step-by-step completion monitoring with visual indicators
- **Step Management**: Add, edit, delete, and reorder learning steps
- **Content Variety**: Mix of tutorials, projects, articles, and practical exercises

### 🛠️ Full CRUD Operations
- **Roadmap Management**: Create, read, update, delete roadmaps
- **Step Management**: Granular control over individual learning steps
- **User Progress**: Track completion status across all roadmaps
- **Data Persistence**: Secure MongoDB storage with user authentication

### 🔐 Security & Authentication
- **JWT Authentication**: Secure login/register system
- **Protected Routes**: API endpoints secured with token verification
- **User Sessions**: Persistent login state management
- **Password Security**: Secure password hashing and validation

## 🏗️ Architecture

### Backend (Flask + MongoDB)
```
backend/
├── app.py              # Main Flask application
├── routes/
│   ├── auth.py         # User authentication endpoints
│   ├── roadmaps.py     # Roadmap CRUD operations
│   ├── progress.py     # Progress tracking
│   └── quiz.py         # Brain type assessment
├── models/
│   └── database.py     # MongoDB connection & models
└── requirements.txt    # Python dependencies
```

### Frontend (React + TypeScript)
```
src/
├── components/         # Reusable UI components
├── pages/             # Application routes/pages
├── lib/
│   ├── api.ts         # API client functions
│   └── utils.ts       # Utility functions
├── types/             # TypeScript type definitions
└── hooks/             # Custom React hooks
```

## 🚀 Setup Instructions

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm  
- **MongoDB** (local installation or MongoDB Atlas)
- **OpenRouter API Key** (for AI features)

### 🔧 Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install flask flask-cors flask-jwt-extended pymongo python-dotenv requests
   ```

4. **Environment Configuration:**
   Create `.env` file in backend directory:
   ```env
   # OpenRouter AI Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # MongoDB Configuration  
   MONGO_URI=mongodb://localhost:27017/neuronav
   
   # JWT Configuration
   JWT_SECRET_KEY=your_secure_random_string_here
   ```

5. **Start the Flask server:**
   ```bash
   python app.py
   ```
   Server runs on `http://localhost:5000`

### 🎨 Frontend Setup

1. **Navigate to project root:**
   ```bash
   cd ..  # if in backend directory
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

### 🗄️ Database Setup

**Option 1: Local MongoDB**
- Install MongoDB Community Edition
- Start MongoDB service
- Database will be created automatically

**Option 2: MongoDB Atlas (Cloud)**
- Create free account at mongodb.com
- Create cluster and get connection string
- Update `MONGO_URI` in `.env` file

## 📁 Project Structure

```
NeuroNav/
├── backend/                 # Flask API server
│   ├── routes/
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── roadmaps.py     # Roadmap CRUD operations
│   │   ├── progress.py     # Progress tracking
│   │   └── quiz.py         # Brain type quiz
│   ├── models/
│   │   └── database.py     # MongoDB connection
│   ├── app.py              # Main Flask application
│   └── .env                # Environment variables
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── pages/             # Application pages
│   ├── lib/               # API & utilities
│   └── types/             # TypeScript definitions
├── public/                # Static assets
└── package.json           # Node.js dependencies
```

## 🔗 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/user` - Get current user

### Quiz & Assessment
- `POST /quiz/submit` - Submit brain type quiz
- `GET /quiz/results` - Get user's brain type

### Roadmaps
- `GET /roadmaps` - Get user's roadmaps
- `POST /roadmaps` - Create new roadmap
- `GET /roadmaps/{id}` - Get specific roadmap
- `PUT /roadmaps/{id}` - Update roadmap
- `DELETE /roadmaps/{id}` - Delete roadmap
- `POST /roadmaps/{id}/steps` - Add step to roadmap
- `DELETE /roadmaps/{id}/steps/{num}` - Delete specific step

### Progress
- `GET /progress/summary` - Get user progress summary
- `POST /progress/update` - Update step completion

## 🚀 Deployment

### Environment Variables
Create `.env` file with:
```env
OPENROUTER_API_KEY=your_openrouter_key
MONGO_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_secure_random_string
```

### Production Setup
1. Set up MongoDB Atlas or production MongoDB instance
2. Deploy backend to cloud service (Heroku, DigitalOcean, etc.)
3. Build frontend: `npm run build`
4. Deploy frontend to static hosting (Vercel, Netlify, etc.)
5. Update API base URL in frontend configuration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request


**Built with ❤️ for personalized learning experiences**
8. Run analysis script (`python analysis/engagement_analysis.py`)
9. Run smoke test (`python tests/smoke_test.py`)
10. Show results in dashboard and analysis folder

*All steps can be completed in under 10 minutes for exam/demo.*
