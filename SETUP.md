# UTD Career Guidance AI System - Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd aws-agetic-ai
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `aws-agetic-ai` directory:

```env
# AWS Bedrock Configuration (Optional - system uses fallback if not configured)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-2
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# LinkedIn Credentials (Optional - for real job scraping)
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password

# RapidAPI (Optional - not currently used)
RAPIDAPI_KEY=your_rapidapi_key
```

**Note**: The system works with fallback mechanisms if credentials are not provided.

### 3. Download ChromeDriver (for LinkedIn scraping)

- Download ChromeDriver from: https://chromedriver.chromium.org/
- Place `chromedriver.exe` in the `bin/` directory or system PATH
- Ensure Chrome browser is installed

### 4. Run the Server

```bash
# From the aws-agetic-ai directory
uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

Or use the startup script:

```bash
python start_server.py
```

### 5. Access the API

The API will be available at: `http://127.0.0.1:8000`

- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## Main Endpoints

### 1. Career Guidance (Primary Endpoint)

```bash
POST /api/career-guidance
```

**Request Body:**
```json
{
  "query": "I want to become a Data Scientist",
  "location": "Dallas, TX"
}
```

**Response:**
- Career goal analysis
- Job market insights (skills, salaries)
- Personalized course recommendations
- Learning path (semester-by-semester)

### 2. Job Market Analysis

```bash
POST /job-market
```

**Request Body:**
```json
{
  "job_title": "Data Scientist",
  "location": "Dallas, TX",
  "limit": 5
}
```

### 3. Course Search

```bash
POST /course-search
```

**Request Body:**
```json
{
  "query": "machine learning"
}
```

## System Architecture

### Components

1. **Career Matching Agent**: Coordinates career guidance and course recommendations
2. **Job Market Agent**: Scrapes and analyzes job market data
3. **Course Catalog Agent**: Manages UTD course database
4. **LinkedIn Scraper**: Real-time job data collection (Selenium-based)

### Data

- **Course Database**: `data/utd_courses.json` (70 courses across 18 departments)
- **Job Cache**: `data/job_cache/` (cached job market data)
- **LinkedIn Session**: `data/linkedin_session.json` (authentication cache)

## Features

### ✅ Implemented

- ✅ Career-specific course recommendations
- ✅ Job market analysis with skills and salaries
- ✅ Real-time LinkedIn job scraping
- ✅ Intelligent fallback system (works without AWS/LinkedIn credentials)
- ✅ 12+ career path patterns supported
- ✅ 70 UTD courses (CS, Business, Science, Engineering)
- ✅ Caching system for performance

### Career Paths Supported

- Financial Analyst, Investment Analyst
- Data Scientist, Data Engineer
- Software Engineer, DevOps Engineer
- Neuroscientist
- Marketing Analyst
- Business Analyst
- Operations Manager
- Management Consultant
- And more...

## Development

### Project Structure

```
aws-agetic-ai/
├── src/
│   ├── agents/           # AI Agents
│   │   ├── career_matching_agent/
│   │   ├── job_market_agent/
│   │   ├── course_catalog_agent/
│   │   └── orchestrator.py
│   ├── api/             # FastAPI application
│   ├── auth/            # LinkedIn authentication
│   ├── config/          # Configuration
│   ├── core/           
│   │   ├── aws/         # AWS Bedrock service
│   │   └── llm/         # LLM service for recommendations
│   └── scrapers/        # Web scrapers
├── data/                # Course data and caches
├── requirements.txt
└── .env                # Environment variables
```

### Running Tests

The system includes built-in fallback mechanisms, so you can test without credentials:

```bash
# Test the API
curl http://127.0.0.1:8000/health

# Test career guidance
curl -X POST http://127.0.0.1:8000/api/career-guidance \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to become a Financial Analyst", "location": "Dallas, TX"}'
```

## Troubleshooting

### ModuleNotFoundError: No module named 'src'

Make sure you're running uvicorn from the `aws-agetic-ai` directory:

```bash
cd aws-agetic-ai
uvicorn src.api.app:app --reload
```

### LinkedIn Scraping Not Working

1. Ensure ChromeDriver is installed and in PATH
2. Check Chrome browser version matches ChromeDriver version
3. Verify LinkedIn credentials in `.env` file
4. Note: The system works with mock data if LinkedIn scraping fails

### AWS Bedrock Errors

The system uses intelligent fallback for course recommendations. AWS Bedrock is optional.

## Performance

- **Course Recommendations**: < 1 second (using fallback system)
- **Job Market Analysis**: 2-5 seconds (with caching)
- **LinkedIn Scraping**: Disabled by default for performance
- **Total Response Time**: ~1-3 seconds typical

## Notes

- The system is optimized for performance with mock data fallbacks
- LinkedIn scraping is available but not required
- AWS Bedrock integration is optional
- All major features work without external dependencies

