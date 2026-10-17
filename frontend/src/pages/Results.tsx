import React, { useState } from 'react'
import { useCareerGuidance } from '../context/CareerGuidanceContext'
import { useNavigate } from 'react-router-dom'
import CourseCard from '../components/ui/CourseCard'
import ProjectCard from '../components/ui/ProjectCard'
import { careerGuidanceAPI } from '../services/api'
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  BookOpen, 
  Briefcase, 
  Code, 
  TrendingUp,
  Target,
  Calendar,
  CheckCircle,
  Star,
  Clock,
  Plus,
  Trash2,
  GripVertical,
  Search,
  X
} from 'lucide-react'

const Results: React.FC = () => {
  const navigate = useNavigate()
  const { userProfile, guidanceResult } = useCareerGuidance()
  const [activeTab, setActiveTab] = useState<'overview' | 'courses' | 'jobs' | 'projects' | 'roadmap'>('overview')
  const [selectedCourses, setSelectedCourses] = useState<any[]>([])
  const [selectedProjects, setSelectedProjects] = useState<any[]>([])
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null)
  
  // Semester planning state
  interface Semester {
    id: string
    name: string
    season: 'Fall' | 'Spring' | 'Summer'
    year: number
    courses: any[]
  }
  
  const [semesters, setSemesters] = useState<Semester[]>([
    { id: '1', name: 'Fall 2024', season: 'Fall', year: 2024, courses: [] },
    { id: '2', name: 'Spring 2025', season: 'Spring', year: 2025, courses: [] }
  ])
  const [draggedCourse, setDraggedCourse] = useState<any>(null)
  const [draggedFromSemester, setDraggedFromSemester] = useState<string | null>(null)
  
  // All courses state
  const [showAllCourses, setShowAllCourses] = useState(false)
  const [courseSearchQuery, setCourseSearchQuery] = useState('')
  const [allCourses, setAllCourses] = useState<any[]>([])
  const [loadingAllCourses, setLoadingAllCourses] = useState(false)

  if (!guidanceResult || !userProfile) {
    return (
      <div className="max-w-4xl mx-auto text-center py-16">
        <div className="bg-warning-50 border border-warning-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-warning-800 mb-2">No Results Found</h2>
          <p className="text-warning-700 mb-4">
            It looks like you haven't completed the career guidance process yet.
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Start Career Guidance
          </button>
        </div>
      </div>
    )
  }

  // Helper function to get unique course identifier
  const getCourseId = (course: any): string => {
    // Use course_code if it's not empty, otherwise fall back to other identifiers
    const id = (course.course_code && course.course_code.trim()) || 
               (course.id && course.id.trim()) || 
               course.title || 
               course.course_name || 
               JSON.stringify(course)
    return id
  }

  // Helper function to check if course is in plan
  const isCourseInPlan = (course: any): boolean => {
    const courseId = getCourseId(course)
    return selectedCourses.some(c => getCourseId(c) === courseId)
  }

  const showToast = (message: string, type: 'success' | 'info' | 'error' = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const handleCourseSelect = (course: any) => {
    const courseId = getCourseId(course)
    const isAdding = !selectedCourses.find(c => getCourseId(c) === courseId)
    
    setSelectedCourses(prev => {
      const found = prev.find(c => getCourseId(c) === courseId)
      
      if (found) {
        // Remove from selection
        return prev.filter(c => getCourseId(c) !== courseId)
      } else {
        // Add to selection
        return [...prev, course]
      }
    })
    
    if (isAdding) {
      showToast(`✓ ${course.title || course.course_name} added to your plan!`)
    }
  }

  const handleProjectSelect = (project: any) => {
    const isAdding = !selectedProjects.find(p => p.title === project.title)
    setSelectedProjects(prev => 
      prev.find(p => p.title === project.title)
        ? prev.filter(p => p.title !== project.title)
        : [...prev, project]
    )
    if (isAdding) {
      showToast(`✓ ${project.title} added to your roadmap!`)
    }
  }

  const handleShare = async () => {
    const shareData = {
      title: 'My Career Roadmap - UTD Career Guidance',
      text: `My personalized career roadmap for ${guidanceResult.career_goal}`,
      url: window.location.href
    }

    try {
      if (navigator.share) {
        await navigator.share(shareData)
        showToast('✓ Shared successfully!')
      } else {
        // Fallback: Copy link to clipboard
        await navigator.clipboard.writeText(window.location.href)
        showToast('✓ Link copied to clipboard!', 'info')
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        console.error('Error sharing:', error)
        showToast('Failed to share. Please try again.', 'error')
      }
    }
  }

  const handleExportPDF = () => {
    // Create a simple text summary for now
    const summary = `
=== UTD Career Guidance Report ===
Career Goal: ${guidanceResult.career_goal}
Location: ${guidanceResult.location}

=== Course Recommendations ===
${guidanceResult.course_recommendations?.map((course: any, index: number) => 
  `${index + 1}. ${course.title} (${course.course_code})
   Priority: ${course.priority}
   Skills: ${course.skills_addressed?.join(', ') || 'N/A'}
   Explanation: ${course.explanation}
`).join('\n') || 'No courses available'}

=== Project Recommendations ===
${guidanceResult.project_recommendations?.map((project: any, index: number) => 
  `${index + 1}. ${project.title}
   Difficulty: ${project.difficulty}
   Duration: ${project.duration_weeks} weeks
   Skills: ${project.skills_practiced?.join(', ') || 'N/A'}
`).join('\n') || 'No projects available'}

=== Learning Path ===
Total Semesters: ${guidanceResult.learning_path?.total_semesters || 'N/A'}
Total Credits: ${guidanceResult.learning_path?.total_credit_hours || 'N/A'}
Completion: ${guidanceResult.learning_path?.completion_timeline || 'N/A'}

Generated on: ${new Date().toLocaleDateString()}
    `.trim()

    // Create a blob and download
    const blob = new Blob([summary], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `career-roadmap-${guidanceResult.career_goal?.replace(/\s+/g, '-').toLowerCase()}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    showToast('✓ Report downloaded successfully!')
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Target },
    { id: 'courses', label: 'Courses', icon: BookOpen },
    { id: 'jobs', label: 'Job Market', icon: Briefcase },
    { id: 'projects', label: 'Projects', icon: Code },
    { id: 'roadmap', label: 'Roadmap', icon: Calendar }
  ]

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-secondary-900 mb-4">
          Your Career Roadmap
        </h1>
        <p className="text-xl text-secondary-600 mb-6">
          Personalized guidance for becoming a {guidanceResult.career_goal}
        </p>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
          <div className="bg-primary-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-primary-600">
              {guidanceResult.course_recommendations?.length || 0}
            </div>
            <div className="text-sm text-primary-700">Recommended Courses</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-blue-600">
              {guidanceResult.project_recommendations?.length || 0}
            </div>
            <div className="text-sm text-blue-700">Project Ideas</div>
          </div>
          <div className="bg-success-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-success-600">
              {guidanceResult.skill_analysis?.current_coverage || '0%'}
            </div>
            <div className="text-sm text-success-700">Skill Coverage</div>
          </div>
          <div className="bg-warning-50 rounded-lg p-4">
            <div className="text-2xl font-bold text-warning-600">
              {guidanceResult.learning_path?.completion_timeline || 'N/A'}
            </div>
            <div className="text-sm text-warning-700">Est. Completion</div>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Skill Analysis */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-success-600" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900">Skill Analysis</h3>
          </div>
          
          {guidanceResult.skill_analysis && (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary-600">Current Coverage</span>
                  <span className="font-medium">{guidanceResult.skill_analysis.current_coverage}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${parseFloat(guidanceResult.skill_analysis.current_coverage) || 0}%` }}
                  />
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-secondary-700 mb-2">Skills to Develop:</h4>
                <div className="flex flex-wrap gap-1">
                  {guidanceResult.skill_analysis.missing_skills?.slice(0, 5).map((skill: string, index: number) => (
                    <span key={index} className="badge-warning text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Job Market Insights */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Briefcase className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900">Job Market</h3>
          </div>
          
          {guidanceResult.job_insights && (
            <div className="space-y-3">
              {guidanceResult.job_insights.slice(0, 3).map((insight: string, index: number) => (
                <div key={index} className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-secondary-600">{insight}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Top Recommendations Preview */}
      <div className="space-y-6">
        <h3 className="text-2xl font-semibold text-secondary-900">Top Recommendations</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          {/* Top Course */}
          {guidanceResult.course_recommendations?.[0] && (
            <div>
              <h4 className="text-lg font-medium text-secondary-800 mb-3 flex items-center">
                <BookOpen className="h-5 w-5 mr-2 text-primary-600" />
                Priority Course
              </h4>
              <CourseCard
                course={guidanceResult.course_recommendations[0]}
                onAddToPlan={handleCourseSelect}
                isInPlan={guidanceResult.course_recommendations[0] ? isCourseInPlan(guidanceResult.course_recommendations[0]) : false}
                showActions={false}
              />
            </div>
          )}

          {/* Top Project */}
          {guidanceResult.project_recommendations?.[0] && (
            <div>
              <h4 className="text-lg font-medium text-secondary-800 mb-3 flex items-center">
                <Code className="h-5 w-5 mr-2 text-success-600" />
                Recommended Project
              </h4>
              <ProjectCard
                project={guidanceResult.project_recommendations[0]}
                onAddToRoadmap={handleProjectSelect}
                isInRoadmap={selectedProjects.some(p => p.title === guidanceResult.project_recommendations?.[0]?.title)}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )

  const renderCourses = () => {
    // Load all courses function
    const loadAllCourses = async () => {
      if (allCourses.length > 0) {
        setShowAllCourses(true)
        return
      }
      
      setLoadingAllCourses(true)
      try {
        // Call the backend API to get all courses
        console.log('Fetching all courses from API...')
        const response = await careerGuidanceAPI.getAllCourses()
        console.log('API Response:', response)
        
        if (response.success && response.courses) {
          setAllCourses(response.courses)
          setShowAllCourses(true)
          showToast(`Loaded ${response.total_courses} courses`, 'success')
        } else {
          console.error('Invalid response format:', response)
          throw new Error(response.error || 'Failed to load courses')
        }
      } catch (error: any) {
        console.error('Error loading all courses:', error)
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to load all courses'
        showToast(errorMessage, 'error')
      } finally {
        setLoadingAllCourses(false)
      }
    }
    
    // Filter courses based on search query
    const getFilteredCourses = () => {
      const coursesToFilter = showAllCourses ? allCourses : (guidanceResult.course_recommendations || [])
      
      if (!courseSearchQuery.trim()) {
        return coursesToFilter
      }
      
      const query = courseSearchQuery.toLowerCase()
      return coursesToFilter.filter((course: any) => {
        const courseName = (course.title || course.course_name || '').toLowerCase()
        const courseCode = (course.course_code || course.code || '').toLowerCase()
        const department = (course.department || '').toLowerCase()
        
        return courseName.includes(query) || 
               courseCode.includes(query) || 
               department.includes(query)
      })
    }
    
    const filteredCourses = getFilteredCourses()
    const displayTitle = showAllCourses ? 'All Available Courses' : 'Course Recommendations'
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-secondary-900">{displayTitle}</h2>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-secondary-500">
              {selectedCourses.length} selected
            </div>
            {!showAllCourses && (
              <button
                onClick={loadAllCourses}
                disabled={loadingAllCourses}
                className="btn-outline btn-sm flex items-center space-x-2"
              >
                <BookOpen className="h-4 w-4" />
                <span>{loadingAllCourses ? 'Loading...' : 'Browse All Courses'}</span>
              </button>
            )}
            {showAllCourses && (
              <button
                onClick={() => {
                  setShowAllCourses(false)
                  setCourseSearchQuery('')
                }}
                className="btn-outline btn-sm flex items-center space-x-2"
              >
                <X className="h-4 w-4" />
                <span>Show Recommendations Only</span>
              </button>
            )}
          </div>
        </div>
        
        {/* Search Bar */}
        {(showAllCourses || guidanceResult.course_recommendations.length > 5) && (
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-secondary-400" />
            </div>
            <input
              type="text"
              value={courseSearchQuery}
              onChange={(e) => setCourseSearchQuery(e.target.value)}
              placeholder="Search by course name, code, or department..."
              className="input-field pl-10 pr-10"
            />
            {courseSearchQuery && (
              <button
                onClick={() => setCourseSearchQuery('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <X className="h-5 w-5 text-secondary-400 hover:text-secondary-600" />
              </button>
            )}
          </div>
        )}
        
        {/* Course Count */}
        {courseSearchQuery && (
          <div className="text-sm text-secondary-600">
            Found {filteredCourses.length} course{filteredCourses.length !== 1 ? 's' : ''}
          </div>
        )}
        
        {filteredCourses.length > 0 ? (
          <div className="grid gap-6">
            {filteredCourses.map((course: any, index: number) => (
              <CourseCard
                key={index}
                course={course}
                isSelected={isCourseInPlan(course)}
                onAddToPlan={handleCourseSelect}
                isInPlan={isCourseInPlan(course)}
              />
            ))}
          </div>
        ) : courseSearchQuery ? (
          <div className="card text-center py-12">
            <div className="text-secondary-400 mb-4">
              <Search className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-secondary-700 mb-2">
              No Courses Found
            </h3>
            <p className="text-secondary-600">
              Try adjusting your search query or browse all courses
            </p>
            <button
              onClick={() => setCourseSearchQuery('')}
              className="btn-secondary btn-sm mt-4"
            >
              Clear Search
            </button>
          </div>
        ) : (
          <div className="card text-center py-12">
            <div className="text-secondary-400 mb-4">
              <BookOpen className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-secondary-700 mb-2">
              No Course Recommendations Available
            </h3>
            <p className="text-secondary-600">
              Course recommendations will be generated based on your career goals and skills.
            </p>
          </div>
        )}
      </div>
    )
  }

  const renderJobs = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-secondary-900">Job Market Insights</h2>
      
      {/* Market Summary */}
      {guidanceResult.market_insights && (
        <div className="card bg-gradient-to-r from-blue-50 to-primary-50">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Market Summary</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {guidanceResult.market_insights.total_opportunities || 'N/A'}
              </div>
              <div className="text-sm text-blue-700">Available Jobs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-600">
                ${guidanceResult.market_insights.salary_insights?.average?.toLocaleString() || 'N/A'}
              </div>
              <div className="text-sm text-success-700">Average Salary</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {guidanceResult.market_insights.market_health || 'Healthy'}
              </div>
              <div className="text-sm text-primary-700">Market Health</div>
            </div>
          </div>
          
          {/* Market Summary Text */}
          {guidanceResult.market_insights.market_summary && (
            <div className="mt-4 pt-4 border-t border-blue-100">
              <p className="text-sm text-secondary-700">{guidanceResult.market_insights.market_summary}</p>
            </div>
          )}
        </div>
      )}

      {/* Hot Skills */}
      {guidanceResult.market_insights?.hot_skills && guidanceResult.market_insights.hot_skills.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">🔥 In-Demand Skills</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {guidanceResult.market_insights.hot_skills.slice(0, 10).map((skillInfo: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <span className="font-medium text-secondary-900">{skillInfo.skill}</span>
                <span className="text-sm text-secondary-600">
                  {skillInfo.frequency} {skillInfo.frequency === 1 ? 'job' : 'jobs'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Emerging vs Established Skills */}
      {(guidanceResult.market_insights?.emerging_skills || guidanceResult.market_insights?.established_skills) && (
        <div className="grid md:grid-cols-2 gap-6">
          {guidanceResult.market_insights.emerging_skills && guidanceResult.market_insights.emerging_skills.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">🚀 Emerging Skills</h3>
              <div className="space-y-2">
                {guidanceResult.market_insights.emerging_skills.map((skill: string, index: number) => (
                  <div key={index} className="badge-success">
                    {skill}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {guidanceResult.market_insights.established_skills && guidanceResult.market_insights.established_skills.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">📚 Established Skills</h3>
              <div className="space-y-2">
                {guidanceResult.market_insights.established_skills.map((skill: string, index: number) => (
                  <div key={index} className="badge-primary">
                    {skill}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )

  const renderProjects = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-secondary-900">Project Recommendations</h2>
        <div className="text-sm text-secondary-500">
          {selectedProjects.length} of {guidanceResult.project_recommendations?.length || 0} selected
        </div>
      </div>
      
      {guidanceResult.project_recommendations && guidanceResult.project_recommendations.length > 0 ? (
        <div className="grid gap-6">
          {guidanceResult.project_recommendations.map((project: any, index: number) => (
            <ProjectCard
              key={index}
              project={project}
              onAddToRoadmap={handleProjectSelect}
              isInRoadmap={selectedProjects.some(p => p.title === project.title)}
            />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <div className="text-secondary-400 mb-4">
            <Code className="h-16 w-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-secondary-700 mb-2">
            No Project Recommendations Yet
          </h3>
          <p className="text-secondary-600">
            Project recommendations will be generated based on your course selections and career goals.
          </p>
        </div>
      )}
    </div>
  )

  // Semester management functions
  const addNewSemester = () => {
    let nextSeason: 'Fall' | 'Spring' | 'Summer'
    let nextYear: number
    
    if (semesters.length === 0) {
      // If no semesters exist, start with Fall of current year
      nextSeason = 'Fall'
      nextYear = 2024
    } else {
      const lastSemester = semesters[semesters.length - 1]
      nextYear = lastSemester.year
      
      if (lastSemester.season === 'Fall') {
        nextSeason = 'Spring'
        nextYear += 1
      } else if (lastSemester.season === 'Spring') {
        nextSeason = 'Summer'
      } else {
        nextSeason = 'Fall'
      }
    }
    
    const newSemester: Semester = {
      id: Date.now().toString(),
      name: `${nextSeason} ${nextYear}`,
      season: nextSeason,
      year: nextYear,
      courses: []
    }
    
    setSemesters([...semesters, newSemester])
    showToast(`✓ ${newSemester.name} added`, 'success')
  }
  
  const removeSemester = (semesterId: string) => {
    const semester = semesters.find(s => s.id === semesterId)
    if (!semester) return
    
    // Move courses back to unassigned
    if (semester.courses.length > 0) {
      showToast(`${semester.courses.length} course(s) moved to unassigned`, 'info')
    }
    
    setSemesters(semesters.filter(s => s.id !== semesterId))
  }
  
  const getSemesterCredits = (semester: Semester) => {
    return semester.courses.reduce((total, course) => {
      const credits = Number((course as any).semester_credit_hours || course.credit_hours || 3)
      return total + credits
    }, 0)
  }
  
  const getUnassignedCourses = () => {
    const assignedCourseIds = new Set(
      semesters.flatMap(sem => sem.courses.map(c => getCourseId(c)))
    )
    return selectedCourses.filter(course => !assignedCourseIds.has(getCourseId(course)))
  }
  
  const handleDragStart = (course: any, fromSemesterId: string | null) => {
    setDraggedCourse(course)
    setDraggedFromSemester(fromSemesterId)
  }
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }
  
  const handleDrop = (toSemesterId: string) => {
    if (!draggedCourse) return
    
    // Don't do anything if dropping in the same semester
    if (draggedFromSemester === toSemesterId) {
      setDraggedCourse(null)
      setDraggedFromSemester(null)
      return
    }
    
    // Check if course already exists in destination semester
    const destinationSemester = semesters.find(sem => sem.id === toSemesterId)
    const courseAlreadyInDestination = destinationSemester?.courses.some(
      c => getCourseId(c) === getCourseId(draggedCourse)
    )
    
    if (courseAlreadyInDestination) {
      showToast('Course is already in this semester', 'error')
      setDraggedCourse(null)
      setDraggedFromSemester(null)
      return
    }
    
    // Update semesters in a single operation
    setSemesters(semesters.map(sem => {
      // Remove from source semester
      if (draggedFromSemester && sem.id === draggedFromSemester) {
        return {
          ...sem,
          courses: sem.courses.filter(c => getCourseId(c) !== getCourseId(draggedCourse))
        }
      }
      // Add to destination semester
      if (sem.id === toSemesterId) {
        return {
          ...sem,
          courses: [...sem.courses, draggedCourse]
        }
      }
      return sem
    }))
    
    setDraggedCourse(null)
    setDraggedFromSemester(null)
  }
  
  const removeCourseFromSemester = (semesterId: string, course: any) => {
    setSemesters(semesters.map(sem => {
      if (sem.id === semesterId) {
        return {
          ...sem,
          courses: sem.courses.filter(c => getCourseId(c) !== getCourseId(course))
        }
      }
      return sem
    }))
    showToast(`Course moved to unassigned`, 'info')
  }

  const renderRoadmap = () => {
    const unassignedCourses = getUnassignedCourses()
    // Only count credits from courses assigned to semesters
    const totalCredits = semesters.reduce((sum, sem) => sum + getSemesterCredits(sem), 0)

    const handleRemoveCourse = (course: any) => {
      handleCourseSelect(course) // This toggles the course
      showToast(`✗ ${course.title || course.course_name} removed from plan`, 'info')
    }

    const handleRemoveProject = (project: any) => {
      handleProjectSelect(project) // This toggles the project
      showToast(`✗ ${project.title} removed from roadmap`, 'info')
    }

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-secondary-900">My Learning Roadmap</h2>
          <button
            onClick={() => {
              setSelectedCourses([])
              setSelectedProjects([])
              showToast('Roadmap cleared', 'info')
            }}
            className="btn-outline btn-sm"
          >
            Clear All
          </button>
        </div>

        {/* Summary */}
        <div className="card bg-gradient-to-r from-primary-50 to-success-50">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Roadmap Summary</h3>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {semesters.length}
              </div>
              <div className="text-sm text-primary-700">Semesters</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-600">
                {selectedCourses.length}
              </div>
              <div className="text-sm text-success-700">Courses</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {totalCredits}
              </div>
              <div className="text-sm text-blue-700">Total Credits</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-warning-600">
                {selectedProjects.length}
              </div>
              <div className="text-sm text-warning-700">Projects</div>
            </div>
          </div>
        </div>

        {/* Empty State */}
        {selectedCourses.length === 0 && selectedProjects.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-secondary-400 mb-4">
              <Calendar className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-secondary-700 mb-2">
              Your Roadmap is Empty
            </h3>
            <p className="text-secondary-600 mb-4">
              Add courses and projects from the recommendations to build your personalized learning roadmap.
            </p>
            <div className="flex justify-center space-x-4">
              <button onClick={() => setActiveTab('courses')} className="btn-primary btn-sm">
                Browse Courses
              </button>
              <button onClick={() => setActiveTab('projects')} className="btn-secondary btn-sm">
                Browse Projects
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Unassigned Courses */}
            {unassignedCourses.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-secondary-900">Unassigned Courses</h3>
                  <span className="text-sm text-secondary-500">{unassignedCourses.length} course(s)</span>
                </div>
                <div className="card bg-secondary-50 border-2 border-dashed border-secondary-300">
                  <p className="text-sm text-secondary-600 mb-3">Drag courses to assign them to a semester</p>
                  <div className="space-y-2">
                    {unassignedCourses.map((course: any, index: number) => {
                      const courseName = course.title || course.course_name || 'Untitled Course'
                      const courseCode = course.course_code || course.code || 'N/A'
                      const credits = Number((course as any).semester_credit_hours || course.credit_hours || 3)
                      
                      return (
                        <div
                          key={index}
                          draggable
                          onDragStart={() => handleDragStart(course, null)}
                          className="flex items-center justify-between p-3 bg-white rounded-lg hover:shadow-md transition-all cursor-move border border-secondary-200"
                        >
                          <div className="flex items-center space-x-3 flex-1">
                            <GripVertical className="h-4 w-4 text-secondary-400" />
                            <BookOpen className="h-5 w-5 text-primary-600 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-secondary-900">{courseName}</div>
                              <div className="text-sm text-secondary-600">{courseCode}</div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span className="text-sm text-secondary-600">{credits} cr</span>
                            <button
                              onClick={() => handleRemoveCourse(course)}
                              className="p-1.5 text-error-600 hover:bg-error-50 rounded"
                              title="Remove from plan"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
            
            {/* Semester Breakdown */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-secondary-900">Semester Plan</h3>
                <button onClick={addNewSemester} className="btn-primary btn-sm flex items-center space-x-2">
                  <Plus className="h-4 w-4" />
                  <span>Add Semester</span>
                </button>
              </div>
              
              {semesters.map((semester) => {
                const semCredits = getSemesterCredits(semester)
                const isOverloaded = semCredits > 18
                const isNearMax = semCredits > 12 && semCredits <= 18
                
                return (
                  <div 
                    key={semester.id} 
                    className="card"
                    onDragOver={handleDragOver}
                    onDrop={() => handleDrop(semester.id)}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h4 className="text-lg font-medium text-secondary-900">
                            {semester.name}
                          </h4>
                          <button
                            onClick={() => removeSemester(semester.id)}
                            className="p-1 text-error-600 hover:bg-error-50 rounded"
                            title="Remove semester"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                        <p className="text-sm text-secondary-600 mt-1">
                          {semester.courses.length} course{semester.courses.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                          isOverloaded 
                            ? 'bg-error-100 text-error-700 border border-error-300' 
                            : isNearMax
                            ? 'bg-warning-100 text-warning-700 border border-warning-300'
                            : 'bg-success-100 text-success-700 border border-success-300'
                        }`}>
                          {semCredits} / 12-18 credits
                        </span>
                      </div>
                    </div>
                    
                    {semester.courses.length === 0 ? (
                      <div className="p-8 border-2 border-dashed border-secondary-300 rounded-lg text-center bg-secondary-50">
                        <BookOpen className="h-8 w-8 mx-auto text-secondary-400 mb-2" />
                        <p className="text-sm text-secondary-500">Drop courses here to add to {semester.name}</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {semester.courses.map((course: any, courseIndex: number) => {
                          const courseName = course.title || course.course_name || 'Untitled Course'
                          const courseCode = course.course_code || course.code || 'N/A'
                          const credits = Number((course as any).semester_credit_hours || course.credit_hours || 3)
                          const skillsTaught = (course as any).skills_addressed || course.skills_taught || []
                          
                          return (
                            <div
                              key={courseIndex}
                              draggable
                              onDragStart={() => handleDragStart(course, semester.id)}
                              className="flex items-start justify-between p-3 bg-secondary-50 rounded-lg hover:bg-secondary-100 transition-colors group cursor-move"
                            >
                              <div className="flex items-start space-x-3 flex-1">
                                <GripVertical className="h-4 w-4 text-secondary-400 mt-1" />
                                <BookOpen className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                  <div className="font-medium text-secondary-900">
                                    {courseName}
                                  </div>
                                  <div className="text-sm text-secondary-600">
                                    {courseCode} • {credits} credit{credits !== 1 ? 's' : ''}
                                  </div>
                                  {skillsTaught.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1">
                                      {skillsTaught.slice(0, 3).map((skill: string, skillIdx: number) => (
                                        <span key={skillIdx} className="text-xs badge-primary">
                                          {skill}
                                        </span>
                                      ))}
                                      {skillsTaught.length > 3 && (
                                        <span className="text-xs text-secondary-500">
                                          +{skillsTaught.length - 3} more
                                        </span>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <button
                                onClick={() => removeCourseFromSemester(semester.id, course)}
                                className="ml-4 p-2 text-error-600 hover:bg-error-50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                                title="Remove from semester"
                              >
                                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          )
                        })}
                      </div>
                    )}
                    
                    {/* Credit limit warning */}
                    {isOverloaded && (
                      <div className="mt-3 p-3 bg-error-50 border border-error-200 rounded-lg">
                        <p className="text-sm text-error-700">
                          ⚠️ Warning: This semester exceeds the recommended 18 credit maximum. Consider redistributing courses.
                        </p>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Projects Section */}
            {selectedProjects.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-secondary-900">Portfolio Projects</h3>
                <div className="card">
                  <div className="space-y-3">
                    {selectedProjects.map((project: any, index: number) => (
                      <div key={index} className="flex items-start justify-between p-3 bg-secondary-50 rounded-lg hover:bg-secondary-100 transition-colors group">
                        <div className="flex items-start space-x-3 flex-1">
                          <Code className="h-5 w-5 text-success-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-secondary-900">
                              {project.title}
                            </div>
                            <div className="text-sm text-secondary-600 mt-1">
                              {project.description}
                            </div>
                            <div className="flex items-center space-x-4 mt-2 text-xs text-secondary-500">
                              <span className={`px-2 py-0.5 rounded-full ${
                                project.difficulty === 'beginner' ? 'bg-success-100 text-success-700' :
                                project.difficulty === 'intermediate' ? 'bg-warning-100 text-warning-700' :
                                'bg-error-100 text-error-700'
                              }`}>
                                {project.difficulty}
                              </span>
                              <span className="flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {project.estimated_time}
                              </span>
                            </div>
                            {project.skills_practiced && project.skills_practiced.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {project.skills_practiced.slice(0, 4).map((skill: string, skillIdx: number) => (
                                  <span key={skillIdx} className="text-xs badge-success">
                                    {skill}
                                  </span>
                                ))}
                                {project.skills_practiced.length > 4 && (
                                  <span className="text-xs text-secondary-500">
                                    +{project.skills_practiced.length - 4} more
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveProject(project)}
                          className="ml-4 p-2 text-error-600 hover:bg-error-50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Remove from roadmap"
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview()
      case 'courses':
        return renderCourses()
      case 'jobs':
        return renderJobs()
      case 'projects':
        return renderProjects()
      case 'roadmap':
        return renderRoadmap()
      default:
        return renderOverview()
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={() => navigate('/')}
          className="btn-ghost flex items-center space-x-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Home</span>
        </button>

        <div className="flex items-center space-x-3">
          <button 
            onClick={handleShare}
            className="btn-outline btn-sm flex items-center space-x-2"
          >
            <Share2 className="h-4 w-4" />
            <span>Share</span>
          </button>
          <button 
            onClick={handleExportPDF}
            className="btn-primary btn-sm flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-secondary-200 mb-8">
        <nav className="flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in">
        {renderTabContent()}
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
          <div className={`
            px-6 py-4 rounded-lg shadow-lg flex items-center space-x-3
            ${toast.type === 'success' ? 'bg-success-600 text-white' : 
              toast.type === 'error' ? 'bg-error-600 text-white' : 
              'bg-primary-600 text-white'}
          `}>
            {toast.type === 'success' && <CheckCircle className="h-5 w-5" />}
            {toast.type === 'error' && <Star className="h-5 w-5" />}
            {toast.type === 'info' && <Star className="h-5 w-5" />}
            <span className="font-medium">{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default Results