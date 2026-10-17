import React from 'react'
import { Brain, Zap, Target, Lightbulb } from 'lucide-react'

interface LoadingStateProps {
  stage: 'analyzing' | 'matching' | 'generating' | 'finalizing'
  message?: string
  progress?: number
  className?: string
}

const LoadingState: React.FC<LoadingStateProps> = ({ 
  stage, 
  message, 
  progress = 0, 
  className = '' 
}) => {
  const stages = {
    analyzing: {
      icon: Brain,
      title: 'Analyzing Your Profile',
      description: 'Our AI is understanding your career goals and current skills',
      color: 'text-primary-600',
      bgColor: 'bg-primary-100',
    },
    matching: {
      icon: Target,
      title: 'Matching Job Market Data',
      description: 'Scanning real-time job postings and market trends',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    generating: {
      icon: Lightbulb,
      title: 'Generating Recommendations',
      description: 'Creating personalized course and project suggestions',
      color: 'text-success-600',
      bgColor: 'bg-success-100',
    },
    finalizing: {
      icon: Zap,
      title: 'Finalizing Your Roadmap',
      description: 'Putting together your complete career guidance plan',
      color: 'text-warning-600',
      bgColor: 'bg-warning-100',
    },
  }

  const currentStage = stages[stage]
  const Icon = currentStage.icon

  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      {/* Animated Icon */}
      <div className={`relative mb-6`}>
        <div className={`w-16 h-16 ${currentStage.bgColor} rounded-full flex items-center justify-center animate-pulse-slow`}>
          <Icon className={`h-8 w-8 ${currentStage.color}`} />
        </div>
        
        {/* Rotating Border */}
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary-600 animate-spin"></div>
      </div>

      {/* Stage Information */}
      <div className="text-center max-w-md">
        <h3 className="text-xl font-semibold text-secondary-900 mb-2">
          {currentStage.title}
        </h3>
        <p className="text-secondary-600 mb-4">
          {message || currentStage.description}
        </p>

        {/* Progress Bar */}
        {progress > 0 && (
          <div className="w-full max-w-xs mx-auto mb-4">
            <div className="flex justify-between text-sm text-secondary-500 mb-1">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Loading Dots */}
        <div className="flex justify-center space-x-1">
          <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>

      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-5">
        <div className="absolute -top-4 -right-4 w-24 h-24 bg-primary-600 rounded-full animate-pulse"></div>
        <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-secondary-600 rounded-full animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/4 w-8 h-8 bg-success-600 rounded-full animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
    </div>
  )
}

export default LoadingState
