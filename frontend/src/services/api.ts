import axios from 'axios'

// Use environment variable for API URL
// In production (CloudFront), VITE_API_URL will be empty to use relative paths
// In development, it should point to local backend or be empty to use proxy
const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : ''

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Don't send credentials for CORS requests unless needed
  withCredentials: false,
})

export interface QuickStartProfile {
  career_goal: string
  current_skills?: string[]
  academic_year?: string
  location?: string
}

export interface ComprehensiveProfile {
  career_goal: string
  alternative_careers?: string[]
  preferred_location?: string
  remote_work_interest?: boolean
  academic_year?: string
  major?: string
  minor?: string
  gpa?: number
  current_skills?: string[]
  target_skills?: string[]
  skill_level?: string
  completed_courses?: string[]
  courses_in_progress?: string[]
  preferred_departments?: string[]
  salary_expectations?: string
  company_size_preference?: string
  industry_interests?: string[]
  learning_style?: string
  time_commitment?: string
  project_preferences?: string[]
  graduation_timeline?: string
  career_timeline?: string
  internship_interest?: boolean
  special_circumstances?: string
  previous_experience?: string
  portfolio_items?: string[]
}

export interface OnboardingOptions {
  career_goals: string[]
  skills: string[]
  departments: string[]
  industries: string[]
  academic_years: string[]
  experience_levels: string[]
  learning_styles: string[]
  time_commitments: string[]
  company_sizes: string[]
}

export const careerGuidanceAPI = {
  // Get onboarding options
  getOnboardingOptions: async (): Promise<OnboardingOptions> => {
    const response = await api.get('/api/onboarding/options')
    return response.data
  },

  // Quick start career guidance
  quickStart: async (profile: QuickStartProfile) => {
    const response = await api.post('/api/onboarding/quick-start', profile)
    return response.data
  },

  // Comprehensive career guidance
  comprehensiveGuidance: async (profile: ComprehensiveProfile) => {
    const response = await api.post('/api/onboarding/comprehensive', profile)
    return response.data
  },

  // Suggest career goals
  suggestCareers: async (major: string, interests: string[] = []) => {
    const response = await api.post('/api/onboarding/suggest-careers', null, {
      params: { major, interests }
    })
    return response.data
  },

  // Validate profile
  validateProfile: async (profile: ComprehensiveProfile) => {
    const response = await api.post('/api/onboarding/validate-profile', profile)
    return response.data
  },

  // Get smart questions
  getSmartQuestions: async (career_goal: string) => {
    const response = await api.get(`/api/onboarding/smart-questions/${career_goal}`)
    return response.data
  },

  // Legacy endpoints for backward compatibility
  getCareerAdvice: async (request: any) => {
    const response = await api.post('/api/career-guidance', request)
    return response.data
  },

  getJobMarketAnalysis: async (request: any) => {
    const response = await api.post('/job-market', request)
    return response.data
  },

  searchCourses: async (request: any) => {
    const response = await api.post('/course-search', request)
    return response.data
  },

  getAllCourses: async () => {
    const response = await api.get('/api/courses/all')
    return response.data
  },

  getProjectRecommendations: async (request: any) => {
    const response = await api.post('/api/project-recommendations', request)
    return response.data
  }
}

export default api
