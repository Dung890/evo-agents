import React, { useState } from 'react'
import { 
  DollarSign, 
  MapPin, 
  Users, 
  Calendar,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Briefcase
} from 'lucide-react'

interface JobInsight {
  title: string
  company: string
  location: string
  salary_range?: string
  posted_date?: string
  job_type: string
  experience_level: string
  skills_required: string[]
  description: string
  url?: string
  match_score?: number
}

interface JobInsightCardProps {
  job: JobInsight
  className?: string
  showFullDetails?: boolean
}

const JobInsightCard: React.FC<JobInsightCardProps> = ({
  job,
  className = '',
  showFullDetails = false
}) => {
  const [isExpanded, setIsExpanded] = useState(showFullDetails)

  const matchPercentage = job.match_score ? Math.round(job.match_score * 100) : 0

  const getExperienceLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'entry':
      case 'junior':
        return 'bg-success-100 text-success-800 border-success-200'
      case 'mid':
      case 'mid-level':
        return 'bg-warning-100 text-warning-800 border-warning-200'
      case 'senior':
      case 'lead':
        return 'bg-error-100 text-error-800 border-error-200'
      default:
        return 'bg-secondary-100 text-secondary-800 border-secondary-200'
    }
  }

  const getJobTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'full-time':
        return 'bg-primary-100 text-primary-800 border-primary-200'
      case 'part-time':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'contract':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'internship':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-secondary-100 text-secondary-800 border-secondary-200'
    }
  }

  return (
    <div className={`card hover:shadow-lg transition-all duration-200 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-secondary-900 mb-1 line-clamp-2">
            {job.title}
          </h3>
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-primary-600 font-medium">{job.company}</span>
            <div className="flex items-center text-secondary-500 text-sm">
              <MapPin className="h-4 w-4 mr-1" />
              {job.location}
            </div>
          </div>
        </div>

        {/* Match Score */}
        {job.match_score && (
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
                  stroke="#22c55e"
                  strokeWidth="2"
                  strokeDasharray={`${matchPercentage}, 100`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-semibold text-secondary-700">
                  {matchPercentage}%
                </span>
              </div>
            </div>
            <span className="text-xs text-secondary-500 mt-1">Match</span>
          </div>
        )}
      </div>

      {/* Job Details */}
      <div className="space-y-3">
        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          <span className={`badge-base border ${getJobTypeColor(job.job_type)}`}>
            <Briefcase className="h-3 w-3 mr-1" />
            {job.job_type}
          </span>
          <span className={`badge-base border ${getExperienceLevelColor(job.experience_level)}`}>
            <Users className="h-3 w-3 mr-1" />
            {job.experience_level}
          </span>
          {job.posted_date && (
            <span className="badge-secondary">
              <Calendar className="h-3 w-3 mr-1" />
              {job.posted_date}
            </span>
          )}
        </div>

        {/* Salary */}
        {job.salary_range && (
          <div className="flex items-center space-x-2 text-success-700 bg-success-50 p-2 rounded-lg">
            <DollarSign className="h-4 w-4" />
            <span className="font-medium">{job.salary_range}</span>
          </div>
        )}

        {/* Skills Required */}
        {job.skills_required && job.skills_required.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-secondary-700 mb-2">Required Skills:</h4>
            <div className="flex flex-wrap gap-1">
              {job.skills_required.slice(0, isExpanded ? undefined : 4).map((skill, index) => (
                <span 
                  key={index}
                  className="badge-primary text-xs"
                >
                  {skill}
                </span>
              ))}
              {!isExpanded && job.skills_required.length > 4 && (
                <span className="text-xs text-secondary-500">
                  +{job.skills_required.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Expandable Description */}
        {isExpanded && job.description && (
          <div className="animate-slide-up">
            <h4 className="text-sm font-medium text-secondary-700 mb-2">Job Description:</h4>
            <p className="text-sm text-secondary-600 leading-relaxed">
              {job.description.length > 300 
                ? `${job.description.substring(0, 300)}...` 
                : job.description
              }
            </p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-secondary-100">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="btn-ghost btn-sm flex items-center space-x-1"
        >
          <span>{isExpanded ? 'Show Less' : 'Show More'}</span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>

        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary btn-sm flex items-center space-x-1"
          >
            <span>View Job</span>
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </div>
    </div>
  )
}

export default JobInsightCard
