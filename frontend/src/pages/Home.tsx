import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCareerGuidance } from '../context/CareerGuidanceContext'
import { careerGuidanceAPI, OnboardingOptions } from '../services/api'
import QuickStartForm from '../components/QuickStartForm'
import ComprehensiveForm from '../components/ComprehensiveForm'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import LoadingState from '../components/ui/LoadingState'
import ProgressTracker from '../components/ui/ProgressTracker'
import { Brain, Target, Lightbulb, Zap, TrendingUp } from 'lucide-react'

const Home: React.FC = () => {
  const navigate = useNavigate()
  const { setUserProfile, setGuidanceResult, setLoading, setError, loading, error } = useCareerGuidance()
  const [onboardingOptions, setOnboardingOptions] = useState<OnboardingOptions | null>(null)
  const [formType, setFormType] = useState<'quick' | 'comprehensive'>('quick')
  const [loadingStage, setLoadingStage] = useState<'analyzing' | 'matching' | 'generating' | 'finalizing'>('analyzing')
  const [progress, setProgress] = useState(0)

  const progressSteps = [
    {
      id: 'input',
      title: 'Your Input',
      description: 'Tell us about your career goals',
      status: 'completed' as const,
      estimatedTime: '30 seconds'
    },
    {
      id: 'analysis',
      title: 'AI Analysis',
      description: 'Processing your profile with AI',
      status: loading ? 'current' as const : 'pending' as const,
      estimatedTime: '1-2 minutes'
    },
    {
      id: 'recommendations',
      title: 'Recommendations',
      description: 'Generating personalized guidance',
      status: 'pending' as const,
      estimatedTime: '30 seconds'
    },
    {
      id: 'results',
      title: 'Your Roadmap',
      description: 'Complete career guidance plan',
      status: 'pending' as const,
      estimatedTime: 'Ready!'
    }
  ]

  useEffect(() => {
    loadOnboardingOptions()
  }, [])

  const loadOnboardingOptions = async () => {
    try {
      const options = await careerGuidanceAPI.getOnboardingOptions()
      setOnboardingOptions(options)
    } catch (err) {
      setError('Failed to load form options')
    }
  }

  const handleQuickStart = async (profile: any) => {
    setLoading(true)
    setError(null)
    setProgress(0)
    
    try {
      // Simulate progress stages
      setLoadingStage('analyzing')
      setProgress(25)
      
      await new Promise(resolve => setTimeout(resolve, 800))
      setLoadingStage('matching')
      setProgress(50)
      
      await new Promise(resolve => setTimeout(resolve, 600))
      setLoadingStage('generating')
      setProgress(75)
      
      const result = await careerGuidanceAPI.quickStart(profile)
      
      setLoadingStage('finalizing')
      setProgress(100)
      
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setUserProfile(profile)
      setGuidanceResult(result)
      navigate('/results')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get career guidance')
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const handleComprehensive = async (profile: any) => {
    setLoading(true)
    setError(null)
    setProgress(0)
    
    try {
      // Simulate progress stages with longer times for comprehensive
      setLoadingStage('analyzing')
      setProgress(20)
      
      await new Promise(resolve => setTimeout(resolve, 1200))
      setLoadingStage('matching')
      setProgress(45)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      setLoadingStage('generating')
      setProgress(70)
      
      const result = await careerGuidanceAPI.comprehensiveGuidance(profile)
      
      setLoadingStage('finalizing')
      setProgress(100)
      
      await new Promise(resolve => setTimeout(resolve, 800))
      
      setUserProfile(profile)
      setGuidanceResult(result)
      navigate('/results')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get career guidance')
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  if (!onboardingOptions) {
    return <LoadingSpinner message="Loading form options..." />
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <ProgressTracker 
          steps={progressSteps} 
          currentStep="analysis" 
          className="mb-8"
        />
        <LoadingState 
          stage={loadingStage} 
          progress={progress}
          className="min-h-96"
        />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="inline-flex items-center space-x-2 bg-primary-100 text-primary-800 px-4 py-2 rounded-full text-sm font-medium mb-6">
          <Brain className="h-4 w-4" />
          <span>Powered by AI Agents & Real Job Market Data</span>
        </div>
        
        <h1 className="text-5xl md:text-6xl font-bold text-secondary-900 mb-6">
          Your <span className="text-gradient">Career GPS</span>
        </h1>
        <p className="text-xl text-secondary-600 mb-8 max-w-3xl mx-auto leading-relaxed">
          Transform career planning from guesswork into science. Get personalized course recommendations, 
          job market insights, and project ideas based on real-time data and AI analysis.
        </p>
        
        {/* Stats */}
        <div className="flex flex-wrap justify-center gap-8 mb-12">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">2,470+</div>
            <div className="text-sm text-secondary-500">UTD Courses</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">Real-time</div>
            <div className="text-sm text-secondary-500">Job Market Data</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">4 AI</div>
            <div className="text-sm text-secondary-500">Specialized Agents</div>
          </div>
        </div>
        
        {/* Form Type Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-xl p-1 shadow-md border border-secondary-200 flex gap-1">
            <button
              onClick={() => setFormType('quick')}
              className={`px-8 py-3 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 whitespace-nowrap ${
                formType === 'quick'
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'text-secondary-600 hover:text-primary-600 hover:bg-primary-50'
              }`}
            >
              <Zap className="h-4 w-4 flex-shrink-0" />
              <span className="font-medium">Quick Start</span>
              <span className="text-sm opacity-75">(30s)</span>
            </button>
            <button
              onClick={() => setFormType('comprehensive')}
              className={`px-8 py-3 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 whitespace-nowrap ${
                formType === 'comprehensive'
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'text-secondary-600 hover:text-primary-600 hover:bg-primary-50'
              }`}
            >
              <Target className="h-4 w-4 flex-shrink-0" />
              <span className="font-medium">Comprehensive</span>
              <span className="text-sm opacity-75">(5min)</span>
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && <ErrorMessage message={error} />}

      {/* Forms */}
      <div className="mb-16">
        {formType === 'quick' ? (
          <QuickStartForm
            options={onboardingOptions}
            onSubmit={handleQuickStart}
            loading={loading}
          />
        ) : (
          <ComprehensiveForm
            options={onboardingOptions}
            onSubmit={handleComprehensive}
            loading={loading}
          />
        )}
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="card text-center hover:shadow-lg transition-all duration-200">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mx-auto mb-6">
            <Target className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-3">
            Personalized Recommendations
          </h3>
          <p className="text-secondary-600 leading-relaxed">
            AI-powered course suggestions tailored to your career goals, current skills, and job market demands
          </p>
        </div>

        <div className="card text-center hover:shadow-lg transition-all duration-200">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-6">
            <TrendingUp className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-3">
            Real Job Market Data
          </h3>
          <p className="text-secondary-600 leading-relaxed">
            Live insights from LinkedIn job postings, salary data, and trending skills in your target location
          </p>
        </div>

        <div className="card text-center hover:shadow-lg transition-all duration-200">
          <div className="w-16 h-16 bg-gradient-to-br from-success-500 to-success-600 rounded-xl flex items-center justify-center mx-auto mb-6">
            <Lightbulb className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-3">
            Portfolio Projects
          </h3>
          <p className="text-secondary-600 leading-relaxed">
            Practical project ideas with difficulty levels, timelines, and portfolio impact assessments
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-gradient-to-br from-secondary-50 to-primary-50 rounded-2xl p-8 md:p-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-secondary-900 mb-4">How It Works</h2>
          <p className="text-secondary-600 max-w-2xl mx-auto">
            Our AI agents work together to analyze your profile and provide comprehensive career guidance
          </p>
        </div>
        
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
              1
            </div>
            <h4 className="font-semibold text-secondary-900 mb-2">Share Your Goals</h4>
            <p className="text-sm text-secondary-600">Tell us about your career aspirations and current skills</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
              2
            </div>
            <h4 className="font-semibold text-secondary-900 mb-2">AI Analysis</h4>
            <p className="text-sm text-secondary-600">Our agents analyze job market data and course catalogs</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
              3
            </div>
            <h4 className="font-semibold text-secondary-900 mb-2">Generate Plan</h4>
            <p className="text-sm text-secondary-600">Receive personalized recommendations and learning paths</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
              4
            </div>
            <h4 className="font-semibold text-secondary-900 mb-2">Take Action</h4>
            <p className="text-sm text-secondary-600">Follow your roadmap to achieve your career goals</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
