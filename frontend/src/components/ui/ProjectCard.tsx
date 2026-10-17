import React, { useState } from 'react'
import { 
  Code, 
  Clock, 
  Star, 
  Target, 
  ChevronDown, 
  ChevronUp,
  Plus,
  Check,
  ExternalLink,
  GitBranch,
  Zap
} from 'lucide-react'

interface Project {
  title: string
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimated_time: string
  skills_practiced: string[]
  portfolio_impact: string
  technologies: string[]
  deliverables: string[]
  learning_outcomes: string[]
  resources?: string[]
}

interface ProjectCardProps {
  project: Project
  onAddToRoadmap?: (project: Project) => void
  isInRoadmap?: boolean
  className?: string
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onAddToRoadmap,
  isInRoadmap = false,
  className = ''
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const difficultyConfig = {
    beginner: {
      color: 'text-success-600',
      bgColor: 'bg-success-50',
      borderColor: 'border-success-200',
      label: 'Beginner',
      stars: 1
    },
    intermediate: {
      color: 'text-warning-600',
      bgColor: 'bg-warning-50',
      borderColor: 'border-warning-200',
      label: 'Intermediate',
      stars: 2
    },
    advanced: {
      color: 'text-error-600',
      bgColor: 'bg-error-50',
      borderColor: 'border-error-200',
      label: 'Advanced',
      stars: 3
    }
  }

  const config = difficultyConfig[project.difficulty]

  const handleAddToRoadmap = () => {
    onAddToRoadmap?.(project)
  }

  const renderStars = (count: number) => {
    return Array.from({ length: 3 }, (_, i) => (
      <Star 
        key={i} 
        className={`h-3 w-3 ${i < count ? config.color : 'text-secondary-300'}`}
        fill={i < count ? 'currentColor' : 'none'}
      />
    ))
  }

  return (
    <div className={`card hover:shadow-lg transition-all duration-200 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.color} ${config.borderColor} border`}>
              <div className="flex space-x-0.5">
                {renderStars(config.stars)}
              </div>
              <span>{config.label}</span>
            </div>
            <div className="flex items-center space-x-1 text-xs text-secondary-500 bg-secondary-100 px-2 py-1 rounded-full">
              <Clock className="h-3 w-3" />
              <span>{project.estimated_time}</span>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-secondary-900 mb-2 line-clamp-2">
            {project.title}
          </h3>
        </div>

        <div className="ml-4">
          <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <Code className="h-6 w-6 text-primary-600" />
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-secondary-600 mb-4 line-clamp-3">
        {project.description}
      </p>

      {/* Skills Practiced */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-secondary-700 mb-2">Skills You'll Practice:</h4>
        <div className="flex flex-wrap gap-1">
          {project.skills_practiced.slice(0, isExpanded ? undefined : 3).map((skill, index) => (
            <span 
              key={index}
              className="badge-primary text-xs"
            >
              {skill}
            </span>
          ))}
          {!isExpanded && project.skills_practiced.length > 3 && (
            <span className="text-xs text-secondary-500">
              +{project.skills_practiced.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Portfolio Impact */}
      <div className="bg-primary-50 p-3 rounded-lg mb-4">
        <div className="flex items-start space-x-2">
          <Target className="h-4 w-4 text-primary-600 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-medium text-primary-800 mb-1">Portfolio Impact</h4>
            <p className="text-sm text-primary-700">
              {project.portfolio_impact}
            </p>
          </div>
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="space-y-4 animate-slide-up">
          {/* Technologies */}
          {project.technologies && project.technologies.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-secondary-700 mb-2 flex items-center">
                <Zap className="h-4 w-4 mr-1" />
                Technologies Used:
              </h4>
              <div className="flex flex-wrap gap-1">
                {project.technologies.map((tech, index) => (
                  <span 
                    key={index}
                    className="badge-secondary text-xs"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Deliverables */}
          {project.deliverables && project.deliverables.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-secondary-700 mb-2 flex items-center">
                <GitBranch className="h-4 w-4 mr-1" />
                What You'll Build:
              </h4>
              <ul className="space-y-1">
                {project.deliverables.map((deliverable, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm text-secondary-600">
                    <div className="w-1.5 h-1.5 bg-primary-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span>{deliverable}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Learning Outcomes */}
          {project.learning_outcomes && project.learning_outcomes.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-secondary-700 mb-2 flex items-center">
                <Target className="h-4 w-4 mr-1" />
                Learning Outcomes:
              </h4>
              <ul className="space-y-1">
                {project.learning_outcomes.map((outcome, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm text-secondary-600">
                    <Check className="h-4 w-4 text-success-600 mt-0.5 flex-shrink-0" />
                    <span>{outcome}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Resources */}
          {project.resources && project.resources.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-secondary-700 mb-2 flex items-center">
                <ExternalLink className="h-4 w-4 mr-1" />
                Helpful Resources:
              </h4>
              <ul className="space-y-1">
                {project.resources.map((resource, index) => (
                  <li key={index} className="text-sm">
                    <a 
                      href={resource} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-700 underline"
                    >
                      {resource}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-secondary-100">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="btn-ghost btn-sm flex items-center space-x-1"
        >
          <span>{isExpanded ? 'Show Less' : 'Show Details'}</span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>

        <button
          onClick={handleAddToRoadmap}
          disabled={isInRoadmap}
          className={`btn-sm transition-all duration-200 flex items-center ${
            isInRoadmap 
              ? 'btn-success cursor-not-allowed opacity-75' 
              : 'btn-primary'
          }`}
        >
          {isInRoadmap ? (
            <>
              <Check className="h-4 w-4 mr-1.5" />
              <span>Added to Roadmap</span>
            </>
          ) : (
            <>
              <Plus className="h-4 w-4 mr-1.5" />
              <span>Add to Roadmap</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default ProjectCard
