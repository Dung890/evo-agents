import React, { createContext, useContext, useState, ReactNode } from 'react'

export interface UserProfile {
  career_goal: string
  current_skills: string[]
  target_skills: string[]
  academic_year: string
  location: string
  completed_courses: string[]
  skill_level: string
}

export interface CareerGuidanceResult {
  success: boolean
  career_goal: string
  location: string
  job_insights: string[]
  market_insights: any
  curriculum_comparison: any
  skill_analysis: any
  course_recommendations: any[]
  project_recommendations?: any[]
  learning_path: any
  projects: any[]
  summary: any
  quick_start?: boolean
  profile_completeness?: string
  personalization_level?: string
}

interface CareerGuidanceContextType {
  userProfile: UserProfile | null
  setUserProfile: (profile: UserProfile) => void
  guidanceResult: CareerGuidanceResult | null
  setGuidanceResult: (result: CareerGuidanceResult) => void
  loading: boolean
  setLoading: (loading: boolean) => void
  error: string | null
  setError: (error: string | null) => void
}

const CareerGuidanceContext = createContext<CareerGuidanceContextType | undefined>(undefined)

export const useCareerGuidance = () => {
  const context = useContext(CareerGuidanceContext)
  if (context === undefined) {
    throw new Error('useCareerGuidance must be used within a CareerGuidanceProvider')
  }
  return context
}

interface CareerGuidanceProviderProps {
  children: ReactNode
}

export const CareerGuidanceProvider: React.FC<CareerGuidanceProviderProps> = ({ children }) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [guidanceResult, setGuidanceResult] = useState<CareerGuidanceResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const value = {
    userProfile,
    setUserProfile,
    guidanceResult,
    setGuidanceResult,
    loading,
    setLoading,
    error,
    setError
  }

  return (
    <CareerGuidanceContext.Provider value={value}>
      {children}
    </CareerGuidanceContext.Provider>
  )
}
