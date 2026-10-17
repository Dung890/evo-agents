import React from 'react'
import { Target, TrendingUp, AlertCircle } from 'lucide-react'

interface SkillAnalysisProps {
  skillAnalysis: any
}

const SkillAnalysis: React.FC<SkillAnalysisProps> = ({ skillAnalysis }) => {
  if (!skillAnalysis) {
    return (
      <div className="card text-center py-8">
        <Target className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Skill Analysis Available</h3>
        <p className="text-secondary-600">
          Skill analysis will be available once you complete your profile.
        </p>
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Current Coverage */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
          Current Skill Coverage
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-secondary-700">Overall Coverage</span>
            <span className="text-lg font-bold text-green-600">{skillAnalysis.current_coverage}</span>
          </div>
          
          {skillAnalysis.skills_to_develop && (
            <div>
              <h4 className="font-medium text-secondary-800 mb-2">Skills to Develop</h4>
              <div className="flex flex-wrap gap-2">
                {skillAnalysis.skills_to_develop.slice(0, 6).map((skill: string, index: number) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Missing Skills */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
          <AlertCircle className="h-5 w-5 mr-2 text-orange-600" />
          Missing Skills
        </h3>
        
        <div className="space-y-3">
          {skillAnalysis.missing_skills && skillAnalysis.missing_skills.length > 0 ? (
            skillAnalysis.missing_skills.slice(0, 5).map((skill: string, index: number) => (
              <div key={index} className="flex items-center">
                <div className="w-2 h-2 bg-orange-500 rounded-full mr-3 flex-shrink-0"></div>
                <span className="text-secondary-700">{skill}</span>
              </div>
            ))
          ) : (
            <p className="text-secondary-600 text-sm">No missing skills identified</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default SkillAnalysis
