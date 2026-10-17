import React from 'react'
import { BookOpen, Calendar, ArrowRight } from 'lucide-react'

interface LearningPathProps {
  learningPath: any
}

const LearningPath: React.FC<LearningPathProps> = ({ learningPath }) => {
  if (!learningPath || !learningPath.semesters) {
    return (
      <div className="card text-center py-8">
        <BookOpen className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Learning Path Available</h3>
        <p className="text-secondary-600">
          Learning path will be generated based on your course recommendations.
        </p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-secondary-900 mb-6 flex items-center">
        <Calendar className="h-5 w-5 mr-2 text-primary-600" />
        Recommended Learning Path
      </h3>
      
      <div className="space-y-6">
        {learningPath.semesters.map((semester: any, index: number) => (
          <div key={index} className="border-l-4 border-primary-200 pl-6">
            <div className="flex items-center mb-3">
              <h4 className="text-lg font-semibold text-secondary-900">
                {semester.semester_name}
              </h4>
              {semester.priority && (
                <span className={`ml-3 px-2 py-1 rounded-full text-xs font-medium ${
                  semester.priority === 'critical' ? 'bg-red-100 text-red-700' :
                  semester.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {semester.priority} priority
                </span>
              )}
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              {semester.courses.map((course: any, courseIndex: number) => (
                <div key={courseIndex} className="bg-secondary-50 rounded-lg p-4">
                  <h5 className="font-medium text-secondary-900 mb-1">
                    {course.course_code || course.title}
                  </h5>
                  <p className="text-sm text-secondary-600 mb-2">{course.description}</p>
                  
                  {course.skills_addressed && course.skills_addressed.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {course.skills_addressed.slice(0, 3).map((skill: string, skillIndex: number) => (
                        <span
                          key={skillIndex}
                          className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {index < learningPath.semesters.length - 1 && (
              <div className="flex items-center justify-center mt-4">
                <ArrowRight className="h-4 w-4 text-secondary-400" />
              </div>
            )}
          </div>
        ))}
      </div>
      
      {learningPath.estimated_completion && (
        <div className="mt-6 p-4 bg-primary-50 rounded-lg">
          <p className="text-primary-800 font-medium">
            Estimated Completion: {learningPath.estimated_completion}
          </p>
        </div>
      )}
    </div>
  )
}

export default LearningPath
