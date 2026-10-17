import React from 'react'
import { Check, Clock } from 'lucide-react'

interface ProgressStep {
  id: string
  title: string
  description: string
  status: 'completed' | 'current' | 'pending'
  estimatedTime?: string
}

interface ProgressTrackerProps {
  steps: ProgressStep[]
  currentStep: string
  className?: string
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ 
  steps, 
  currentStep, 
  className = '' 
}) => {
  const currentStepIndex = steps.findIndex(step => step.id === currentStep)

  return (
    <div className={`w-full ${className}`}>
      {/* Mobile Progress Bar */}
      <div className="md:hidden mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-secondary-700">
            Step {currentStepIndex + 1} of {steps.length}
          </span>
          <span className="text-sm text-secondary-500">
            {Math.round(((currentStepIndex + 1) / steps.length) * 100)}%
          </span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
          />
        </div>
        <div className="mt-2">
          <h3 className="font-medium text-secondary-900">
            {steps[currentStepIndex]?.title}
          </h3>
          <p className="text-sm text-secondary-600">
            {steps[currentStepIndex]?.description}
          </p>
        </div>
      </div>

      {/* Desktop Step Indicator */}
      <div className="hidden md:block">
        <nav aria-label="Progress">
          <ol className="flex items-center justify-between">
            {steps.map((step, stepIdx) => (
              <li key={step.id} className="relative flex-1 flex flex-col items-center">
                {/* Connector Line */}
                {stepIdx !== steps.length - 1 && (
                  <div className="absolute top-4 left-1/2 w-full h-0.5" aria-hidden="true">
                    <div className={`h-full ${
                      step.status === 'completed' ? 'bg-primary-600' : 'bg-secondary-200'
                    }`} />
                  </div>
                )}

                {/* Step Circle */}
                <div className="relative z-10 flex items-center justify-center mb-2">
                  {step.status === 'completed' ? (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 hover:bg-primary-700 transition-colors">
                      <Check className="h-5 w-5 text-white" aria-hidden="true" />
                    </div>
                  ) : step.status === 'current' ? (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-primary-600 bg-white">
                      <div className="h-2.5 w-2.5 rounded-full bg-primary-600 animate-pulse" />
                    </div>
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-secondary-300 bg-white group-hover:border-secondary-400 transition-colors">
                      <div className="h-2.5 w-2.5 rounded-full bg-transparent group-hover:bg-secondary-300 transition-colors" />
                    </div>
                  )}
                </div>

                {/* Step Content */}
                <div className="text-center px-2">
                  <div className={`text-sm font-medium ${
                    step.status === 'current' ? 'text-primary-600 font-semibold' : 
                    step.status === 'completed' ? 'text-secondary-700' : 'text-secondary-500'
                  }`}>
                    {step.title}
                  </div>
                  <div className={`text-xs mt-1 ${
                    step.status === 'current' ? 'text-secondary-600' : 'text-secondary-500'
                  }`}>
                    {step.description}
                  </div>
                  {step.estimatedTime && step.status === 'current' && (
                    <div className="flex items-center justify-center mt-1 text-xs text-secondary-500">
                      <Clock className="h-3 w-3 mr-1" />
                      {step.estimatedTime}
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </nav>
      </div>
    </div>
  )
}

export default ProgressTracker
