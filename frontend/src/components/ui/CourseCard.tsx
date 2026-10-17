import React, { useState } from 'react'
import { 
  BookOpen, 
  Clock, 
  Users, 
  ChevronDown, 
  ChevronUp, 
  Plus,
  Check,
  AlertCircle,
  Target
} from 'lucide-react'

interface Course {
  course_code: string
  course_name: string
  description: string
  credit_hours: number
  prerequisites: string[]
  department: string
  skills_taught: string[]
  relevance_score: number
  priority: 'high' | 'medium' | 'low'
  explanation: string
  semester_recommendation?: string
}

interface CourseCardProps {
  course: Course
  isSelected?: boolean
  onSelect?: (course: Course) => void
  onAddToPlan?: (course: Course) => void
  isInPlan?: boolean
  showActions?: boolean
  className?: string
}

const CourseCard: React.FC<CourseCardProps> = ({
  course,
  isSelected = false,
  onSelect,
  onAddToPlan,
  isInPlan = false,
  showActions = true,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  // Handle both backend field names (title vs course_name, etc.)
  const courseName = (course as any).title || course.course_name || 'Untitled Course'
  const creditHours = (course as any).semester_credit_hours || course.credit_hours || 3
  const skillsTaught = (course as any).skills_addressed || course.skills_taught || []
  const prerequisites = course.prerequisites || []
  
  // Default to 'low' priority if not specified (for courses from catalog vs recommendations)
  const priority = course.priority || 'low'

  const priorityConfig = {
    high: {
      color: 'text-error-600',
      bgColor: 'bg-error-50',
      borderColor: 'border-error-200',
      label: 'High Priority',
      icon: AlertCircle
    },
    medium: {
      color: 'text-warning-600',
      bgColor: 'bg-warning-50',
      borderColor: 'border-warning-200',
      label: 'Medium Priority',
      icon: Target
    },
    low: {
      color: 'text-success-600',
      bgColor: 'bg-success-50',
      borderColor: 'border-success-200',
      label: 'Low Priority',
      icon: BookOpen
    }
  }

  const config = priorityConfig[priority as 'high' | 'medium' | 'low']
  const PriorityIcon = config.icon

  const handleAddToPlan = () => {
    onAddToPlan?.(course)
  }

  // Backend returns relevance_score as 0-10, convert to 0-100 percentage
  const relevancePercentage = Math.round((course.relevance_score || 0) * 10)

  const handleCardClick = () => {
    // Only allow card click to select if showActions is false
    // Otherwise, selection should only happen via the button
    if (!showActions && onSelect) {
      onSelect(course)
    }
  }

  return (
    <div 
      className={`
        card-interactive 
        ${isSelected ? 'card-selected' : ''} 
        ${className}
        transition-all duration-300
      `}
      onClick={handleCardClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm font-mono text-secondary-500 bg-secondary-100 px-2 py-1 rounded">
              {course.course_code || 'N/A'}
            </span>
            {/* Only show priority badge for recommended courses */}
            {course.priority && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.color} ${config.borderColor} border`}>
                <PriorityIcon className="h-3 w-3" />
                <span>{config.label}</span>
              </div>
            )}
          </div>
          <h3 className="text-lg font-semibold text-secondary-900 mb-1 line-clamp-2">
            {courseName}
          </h3>
          <p className="text-sm text-secondary-600 mb-2">
            {course.department || (course as any).prefix || 'UTD Course'}
          </p>
        </div>

        {/* Relevance Score */}
        <div className="flex flex-col items-center ml-4">
          <div className="relative w-12 h-12">
            <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#e2e8f0"
                strokeWidth="2"
              />
              <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#ea580c"
                strokeWidth="2"
                strokeDasharray={`${relevancePercentage}, 100`}
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-semibold text-secondary-700">
                {relevancePercentage}%
              </span>
            </div>
          </div>
          <span className="text-xs text-secondary-500 mt-1">Match</span>
        </div>
      </div>

      {/* Course Details */}
      <div className="space-y-3">
        {/* Quick Info */}
        <div className="flex items-center space-x-4 text-sm text-secondary-600">
          <div className="flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>{creditHours} credits</span>
          </div>
          {course.semester_recommendation && (
            <div className="flex items-center space-x-1">
              <Users className="h-4 w-4" />
              <span>{course.semester_recommendation}</span>
            </div>
          )}
        </div>

        {/* Skills Taught */}
        {skillsTaught && skillsTaught.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-secondary-700 mb-2">Skills You'll Learn:</h4>
            <div className="flex flex-wrap gap-1">
              {skillsTaught.slice(0, isExpanded ? undefined : 3).map((skill: string, index: number) => (
                <span 
                  key={index}
                  className="badge-primary text-xs"
                >
                  {skill}
                </span>
              ))}
              {!isExpanded && skillsTaught.length > 3 && (
                <span className="text-xs text-secondary-500">
                  +{skillsTaught.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Explanation - only show for recommended courses */}
        {course.explanation && (
          <div className="bg-primary-50 p-3 rounded-lg">
            <h4 className="text-sm font-medium text-primary-800 mb-1">Why This Course?</h4>
            <p className="text-sm text-primary-700">
              {course.explanation}
            </p>
          </div>
        )}

        {/* Expandable Content */}
        {isExpanded && (
          <div className="space-y-3 animate-slide-up">
            {/* Full Description */}
            <div>
              <h4 className="text-sm font-medium text-secondary-700 mb-1">Course Description:</h4>
              <p className="text-sm text-secondary-600">
                {course.description}
              </p>
            </div>

            {/* Prerequisites */}
            {prerequisites && prerequisites.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-secondary-700 mb-2">Prerequisites:</h4>
                <div className="space-y-1">
                  {(Array.isArray(prerequisites) ? prerequisites : [prerequisites]).map((prereq: string, index: number) => (
                    <div key={index} className="flex items-center space-x-2 text-sm text-secondary-600">
                      <div className="w-1.5 h-1.5 bg-secondary-400 rounded-full"></div>
                      <span>{prereq}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      {showActions && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-secondary-100">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsExpanded(!isExpanded)
            }}
            className="btn-ghost btn-sm flex items-center space-x-1"
          >
            <span>{isExpanded ? 'Show Less' : 'Show More'}</span>
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation()
              handleAddToPlan()
            }}
            disabled={isInPlan}
            className={`btn-sm transition-all duration-200 flex items-center ${
              isInPlan 
                ? 'btn-success cursor-not-allowed opacity-75' 
                : 'btn-primary'
            }`}
          >
            {isInPlan ? (
              <>
                <Check className="h-4 w-4 mr-1.5" />
                <span>Added to Plan</span>
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-1.5" />
                <span>Add to Plan</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

export default CourseCard
