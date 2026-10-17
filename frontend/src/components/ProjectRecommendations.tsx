import React from 'react'
import { Lightbulb, Clock, Target, Star } from 'lucide-react'

interface ProjectRecommendationsProps {
  projects: any[]
}

const ProjectRecommendations: React.FC<ProjectRecommendationsProps> = ({ projects }) => {
  if (!projects || projects.length === 0) {
    return (
      <div className="card text-center py-8">
        <Lightbulb className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Project Recommendations</h3>
        <p className="text-secondary-600">
          Project recommendations will be generated based on your career goals and skills.
        </p>
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {projects.map((project, index) => (
        <div key={index} className="card">
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-secondary-900">
              {project.title}
            </h3>
            <div className="flex items-center space-x-2">
              {project.difficulty && (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  project.difficulty === 'advanced' ? 'bg-red-100 text-red-700' :
                  project.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {project.difficulty}
                </span>
              )}
              {project.duration_weeks && (
                <div className="flex items-center text-sm text-secondary-600">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>{project.duration_weeks} weeks</span>
                </div>
              )}
            </div>
          </div>
          
          <p className="text-secondary-700 mb-4">{project.description}</p>
          
          {project.skills_practiced && project.skills_practiced.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-secondary-800 mb-2 flex items-center">
                <Target className="h-4 w-4 mr-1" />
                Skills Practiced
              </h4>
              <div className="flex flex-wrap gap-2">
                {project.skills_practiced.map((skill: string, skillIndex: number) => (
                  <span
                    key={skillIndex}
                    className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {project.key_features && project.key_features.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-secondary-800 mb-2">Key Features</h4>
              <ul className="space-y-1">
                {project.key_features.map((feature: string, featureIndex: number) => (
                  <li key={featureIndex} className="text-sm text-secondary-600 flex items-start">
                    <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {project.portfolio_impact && (
            <div className="p-3 bg-green-50 rounded-lg">
              <h4 className="text-sm font-medium text-green-800 mb-1 flex items-center">
                <Star className="h-4 w-4 mr-1" />
                Portfolio Impact
              </h4>
              <p className="text-sm text-green-700">{project.portfolio_impact}</p>
            </div>
          )}
          
          {project.why_valuable && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
              <h4 className="text-sm font-medium text-blue-800 mb-1">Why This Project is Valuable</h4>
              <p className="text-sm text-blue-700">{project.why_valuable}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default ProjectRecommendations
