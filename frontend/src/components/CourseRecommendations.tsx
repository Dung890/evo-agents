import React from 'react'
import { BookOpen, Star, Clock, CheckCircle } from 'lucide-react'

interface CourseRecommendationsProps {
  courses: any[]
  curriculumComparison?: any
}

const CourseRecommendations: React.FC<CourseRecommendationsProps> = ({ courses, curriculumComparison }) => {
  if (!courses || courses.length === 0) {
    return (
      <div className="card text-center py-8">
        <BookOpen className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Course Recommendations</h3>
        <p className="text-secondary-600">
          We couldn't find specific course recommendations for your career goal.
          Try providing more details about your current skills and interests.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Course Cards */}
      <div className="grid md:grid-cols-2 gap-6">
        {courses.map((course, index) => (
          <div key={index} className="card">
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-semibold text-secondary-900">
                {course.course_code || course.title}
              </h3>
              {course.relevance_score && (
                <div className="flex items-center text-yellow-600">
                  <Star className="h-4 w-4 mr-1" />
                  <span className="text-sm font-medium">{course.relevance_score}/10</span>
                </div>
              )}
            </div>
            
            <p className="text-secondary-700 mb-4">{course.description}</p>
            
            {course.skills_addressed && course.skills_addressed.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-secondary-800 mb-2">Skills Addressed:</h4>
                <div className="flex flex-wrap gap-2">
                  {course.skills_addressed.slice(0, 5).map((skill: string, skillIndex: number) => (
                    <span
                      key={skillIndex}
                      className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            <div className="flex items-center justify-between text-sm text-secondary-600">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                <span>{course.semester_credit_hours || '3'} credits</span>
              </div>
              {course.priority && (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  course.priority === 'critical' ? 'bg-red-100 text-red-700' :
                  course.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                  course.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {course.priority} priority
                </span>
              )}
            </div>
            
            {course.explanation && (
              <div className="mt-3 p-3 bg-secondary-50 rounded-lg">
                <p className="text-sm text-secondary-700">{course.explanation}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Curriculum Comparison */}
      {curriculumComparison && (
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
            <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
            Curriculum Alignment Analysis
          </h3>
          
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-800 mb-2">Coverage Summary</h4>
              <p className="text-green-700 text-sm">
                {curriculumComparison.summary}
              </p>
            </div>
            
            {curriculumComparison.coverage_percentage && (
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-secondary-700">Job Market Alignment</span>
                <div className="flex items-center">
                  <div className="w-32 bg-secondary-200 rounded-full h-2 mr-3">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${curriculumComparison.coverage_percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-secondary-700">
                    {curriculumComparison.coverage_percentage}%
                  </span>
                </div>
              </div>
            )}
            
            {curriculumComparison.gap_recommendations && (
              <div>
                <h4 className="font-medium text-secondary-800 mb-2">Recommendations</h4>
                <ul className="space-y-1">
                  {curriculumComparison.gap_recommendations.map((rec: string, index: number) => (
                    <li key={index} className="text-sm text-secondary-600 flex items-start">
                      <span className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default CourseRecommendations
