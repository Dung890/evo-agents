# UTD Career Guidance AI System

## Product revamp: start here

See [the two-person delivery plan](docs/TEAM_PLAN.md) for workstreams, ownership,
dependencies and first tasks. The new [planning contract](docs/PLANNING_CONTRACT.md)
has an isolated synthetic demo: `python -m src.planning.demo` and regression checks:
`python -m unittest discover -s tests -v`. This foundation is not yet connected to
the existing web application. The legacy feature descriptions below are not a
production-readiness assessment.

An autonomous agentic AI system for personalized career guidance using AWS Bedrock, real-time job market data, and UTD course catalog integration.

## 🚀 Features

- **AI-Powered Career Matching**: Personalized course recommendations based on career goals
- **Real-Time Job Market Analysis**: LinkedIn job scraping with skill extraction and salary insights
- **Project Recommendations**: LLM-generated project ideas for portfolio building
- **Streamlined User Experience**: Quick Start (30s) or Comprehensive (5min) onboarding
- **UTD Course Integration**: 2,470+ courses with intelligent matching
- **Learning Path Planning**: Semester-by-semester progression with prerequisites

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Career Matching Agent**: Orchestrates all agents and provides comprehensive guidance
- **Job Market Intelligence Agent**: LinkedIn scraping with anti-bot measures
- **Course Catalog Agent**: UTD course database with 2,470+ courses
- **Project Advisor Agent**: LLM-powered project recommendations
- **AWS Bedrock Integration**: Claude 3.5 Sonnet for intelligent analysis

### Frontend (React + TypeScript + TailwindCSS)
- **Modern UI**: Beautiful, responsive design with TailwindCSS
- **Real-time Integration**: Seamless API communication
- **Progressive Enhancement**: Quick Start → Comprehensive profiles
- **Interactive Components**: Course cards, job insights, project recommendations

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS Account with Bedrock access
- Chrome/Chromium browser (for LinkedIn scraping)

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-2

# Start the server
python start_server.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Usage

### Quick Start (30 seconds)
1. Visit http://localhost:3000
2. Enter your career goal (e.g., "Data Scientist")
3. Optionally add current skills
4. Get instant personalized guidance

### Comprehensive Profile (5 minutes)
1. Choose "Comprehensive Profile"
2. Fill in detailed information:
   - Career goals and target skills
   - Academic year and experience level
   - Industry interests and learning style
   - Company preferences and certifications
3. Get highly personalized recommendations

## 📊 What You Get

### Course Recommendations
- 6 personalized courses based on career goals
- Skill mapping and explanations
- Prerequisites and credit hours
- Priority-based recommendations

### Project Ideas
- 3 portfolio-worthy projects
- Difficulty levels and timelines
- Skills practiced and portfolio impact
- Real-world applicability

### Job Market Insights
- Real LinkedIn job data
- Salary information and trends
- Hot skills and market analysis
- Location-specific insights

### Learning Paths
- Semester-by-semester progression
- Prerequisites and credit hours
- Milestone tracking
- Estimated completion time

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/onboarding/quick-start` - Quick career guidance
- `POST /api/onboarding/comprehensive` - Detailed career guidance
- `POST /api/project-recommendations` - Project recommendations
- `GET /api/onboarding/options` - Available options for forms

### Analysis Endpoints
- `POST /job-market` - Job market analysis
- `POST /course-search` - Course search
- `GET /api/agents/status` - System status

### Authentication
- `POST /auth/linkedin` - LinkedIn authentication
- `GET /auth/status` - Authentication status
- `POST /auth/logout` - Clear session

## 🧠 AI Agents

### Career Matching Agent (Orchestrator)
- Coordinates all other agents
- Analyzes job requirements vs. coursework
- Generates personalized recommendations
- Creates learning paths and curriculum comparisons

### Job Market Intelligence Agent
- LinkedIn job scraping with Selenium
- Skill extraction and frequency analysis
- Salary data processing
- Market trend identification

### Course Catalog Agent
- UTD course database management
- Course search and filtering
- Prerequisites and credit hour tracking
- Department and keyword matching

### Project Advisor Agent
- LLM-powered project generation
- Difficulty and timeline estimation
- Skills mapping and portfolio impact
- Real-world applicability assessment

## 🔒 Security & Performance

- **LinkedIn Authentication**: Secure session management
- **Anti-bot Measures**: Stealth scraping with delays and user agents
- **Caching**: Intelligent caching for performance
- **Error Handling**: Robust fallback systems
- **Rate Limiting**: Respectful scraping practices

## 📈 Performance Metrics

- **Response Time**: < 2 seconds for quick start
- **Course Database**: 2,470+ UTD courses
- **Job Market Data**: Real-time LinkedIn scraping
- **AI Integration**: AWS Bedrock Claude 3.5 Sonnet
- **Frontend**: React with TypeScript and TailwindCSS

## 🚀 Deployment

### Local Development
```bash
# Backend
python start_server.py

# Frontend
cd frontend && npm run dev
```

### Production
- Backend: Deploy to AWS EC2/ECS with proper environment variables
- Frontend: Deploy to Vercel or AWS Amplify
- Database: Consider DynamoDB for production data storage

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the API documentation at http://127.0.0.1:8000/docs
2. Review the system status at http://127.0.0.1:8000/api/agents/status
3. Check logs for detailed error information

---

**Built with ❤️ for UTD students by the Career Guidance AI Team**
