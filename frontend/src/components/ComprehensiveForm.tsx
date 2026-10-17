import React, { useState } from 'react'
import { OnboardingOptions } from '../services/api'
import { ArrowRight, User, MapPin, BookOpen, Target } from 'lucide-react'

interface ComprehensiveFormProps {
  options: OnboardingOptions
  onSubmit: (profile: any) => void
  loading: boolean
}

const ComprehensiveForm: React.FC<ComprehensiveFormProps> = ({ options, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    career_goal: '',
    alternative_careers: [] as string[],
    preferred_location: 'Dallas, TX',
    remote_work_interest: true,
    academic_year: 'sophomore',
    major: '',
    current_skills: [] as string[],
    target_skills: [] as string[],
    skill_level: 'intermediate',
    completed_courses: [] as string[],
    industry_interests: [] as string[],
    learning_style: 'hands-on',
    time_commitment: 'moderate',
    internship_interest: true
  })

  // const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  // const [selectedTargetSkills, setSelectedTargetSkills] = useState<string[]>([])
  // const [selectedIndustries, setSelectedIndustries] = useState<string[]>([])
  
  const [customCareer, setCustomCareer] = useState('')
  const [customCurrentSkill, setCustomCurrentSkill] = useState('')
  const [customTargetSkill, setCustomTargetSkill] = useState('')
  const [showCustomCareer, setShowCustomCareer] = useState(false)

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleMultiSelect = (field: string, value: string, current: string[], setter: (skills: string[]) => void) => {
    const newSelection = current.includes(value)
      ? current.filter(item => item !== value)
      : [...current, value]
    
    setter(newSelection)
    setFormData(prev => ({ ...prev, [field]: newSelection }))
  }

  const handleCareerChange = (value: string) => {
    if (value === 'custom') {
      setShowCustomCareer(true)
      setFormData(prev => ({ ...prev, career_goal: '' }))
    } else {
      setShowCustomCareer(false)
      setFormData(prev => ({ ...prev, career_goal: value }))
    }
  }

  const handleCustomCareerSubmit = () => {
    if (customCareer.trim()) {
      setFormData(prev => ({ ...prev, career_goal: customCareer.trim() }))
    }
  }

  const handleAddCustomCurrentSkill = () => {
    if (customCurrentSkill.trim() && !formData.current_skills.includes(customCurrentSkill.trim())) {
      const newSkills = [...formData.current_skills, customCurrentSkill.trim()]
      setFormData(prev => ({ ...prev, current_skills: newSkills }))
      setCustomCurrentSkill('')
    }
  }

  const handleAddCustomTargetSkill = () => {
    if (customTargetSkill.trim() && !formData.target_skills.includes(customTargetSkill.trim())) {
      const newSkills = [...formData.target_skills, customTargetSkill.trim()]
      setFormData(prev => ({ ...prev, target_skills: newSkills }))
      setCustomTargetSkill('')
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="card max-w-4xl mx-auto">
      <div className="flex items-center mb-6">
        <User className="h-6 w-6 text-primary-600 mr-3" />
        <h2 className="text-2xl font-bold text-secondary-900">Comprehensive Profile</h2>
        <span className="ml-auto text-sm text-secondary-500">5 minutes</span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Career Goals Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <Target className="h-5 w-5 mr-2" />
            Career Goals
          </h3>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Primary Career Goal *
            </label>
            <select
              value={showCustomCareer ? 'custom' : formData.career_goal}
              onChange={(e) => handleCareerChange(e.target.value)}
              className="input-field"
              required={!showCustomCareer}
            >
              <option value="">Select your primary career goal</option>
              {options.career_goals.map(goal => (
                <option key={goal} value={goal}>{goal}</option>
              ))}
              <option value="custom">✏️ Other (type below)</option>
            </select>
            
            {showCustomCareer && (
              <div className="mt-3">
                <input
                  type="text"
                  value={customCareer}
                  onChange={(e) => setCustomCareer(e.target.value)}
                  onBlur={handleCustomCareerSubmit}
                  onKeyPress={(e) => e.key === 'Enter' && handleCustomCareerSubmit()}
                  className="input-field"
                  placeholder="Enter your career goal"
                  autoFocus
                  required
                />
                {formData.career_goal && (
                  <p className="text-sm text-success-600 mt-2">
                    ✓ Career goal set: {formData.career_goal}
                  </p>
                )}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Alternative Career Interests (Optional)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {options.career_goals.slice(0, 9).map(goal => (
                <button
                  key={goal}
                  type="button"
                  onClick={() => handleMultiSelect('alternative_careers', goal, formData.alternative_careers, (skills) => setFormData(prev => ({ ...prev, alternative_careers: skills })))}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    formData.alternative_careers.includes(goal)
                      ? 'bg-primary-100 border-primary-300 text-primary-700'
                      : 'bg-white border-secondary-300 text-secondary-700 hover:border-primary-300'
                  }`}
                >
                  {goal}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Location & Preferences */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <MapPin className="h-5 w-5 mr-2" />
            Location & Preferences
          </h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Preferred Location
              </label>
              <input
                type="text"
                value={formData.preferred_location}
                onChange={(e) => handleInputChange('preferred_location', e.target.value)}
                className="input-field"
                placeholder="e.g., Dallas, TX"
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.remote_work_interest}
                  onChange={(e) => handleInputChange('remote_work_interest', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-secondary-700">Open to remote work</span>
              </label>
            </div>
          </div>
        </div>

        {/* Academic Information */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900 flex items-center">
            <BookOpen className="h-5 w-5 mr-2" />
            Academic Information
          </h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Academic Year
              </label>
              <select
                value={formData.academic_year}
                onChange={(e) => handleInputChange('academic_year', e.target.value)}
                className="input-field"
              >
                {options.academic_years.map(year => (
                  <option key={year} value={year}>
                    {year.charAt(0).toUpperCase() + year.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Major/Field of Study
              </label>
              <input
                type="text"
                value={formData.major}
                onChange={(e) => handleInputChange('major', e.target.value)}
                className="input-field"
                placeholder="e.g., Computer Science"
              />
            </div>
          </div>
        </div>

        {/* Skills Assessment */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900">Skills Assessment</h3>
          
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Current Skills
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
              {options.skills.map(skill => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => handleMultiSelect('current_skills', skill, formData.current_skills, (skills) => setFormData(prev => ({ ...prev, current_skills: skills })))}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    formData.current_skills.includes(skill)
                      ? 'bg-primary-100 border-primary-300 text-primary-700'
                      : 'bg-white border-secondary-300 text-secondary-700 hover:border-primary-300'
                  }`}
                >
                  {skill}
                </button>
              ))}
            </div>
            
            {/* Custom Skill Input */}
            <div className="mt-3">
              <label className="text-xs text-secondary-600 mb-1 block">
                If not listed, type below:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customCurrentSkill}
                  onChange={(e) => setCustomCurrentSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomCurrentSkill())}
                  className="input-field flex-1 text-sm"
                  placeholder="e.g., React, Python, SQL"
                />
                <button
                  type="button"
                  onClick={handleAddCustomCurrentSkill}
                  disabled={!customCurrentSkill.trim()}
                  className="btn-outline btn-sm whitespace-nowrap disabled:opacity-50"
                >
                  Add Skill
                </button>
              </div>
            </div>
            
            {formData.current_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {formData.current_skills.map(skill => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-100 text-primary-700"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleMultiSelect('current_skills', skill, formData.current_skills, (skills) => setFormData(prev => ({ ...prev, current_skills: skills })))}
                      className="ml-1 hover:text-primary-900"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Skills You Want to Develop
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
              {options.skills.map(skill => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => handleMultiSelect('target_skills', skill, formData.target_skills, (skills) => setFormData(prev => ({ ...prev, target_skills: skills })))}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    formData.target_skills.includes(skill)
                      ? 'bg-green-100 border-green-300 text-green-700'
                      : 'bg-white border-secondary-300 text-secondary-700 hover:border-green-300'
                  }`}
                >
                  {skill}
                </button>
              ))}
            </div>
            
            {/* Custom Target Skill Input */}
            <div className="mt-3">
              <label className="text-xs text-secondary-600 mb-1 block">
                If not listed, type below:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customTargetSkill}
                  onChange={(e) => setCustomTargetSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTargetSkill())}
                  className="input-field flex-1 text-sm"
                  placeholder="e.g., Machine Learning, AWS, Docker"
                />
                <button
                  type="button"
                  onClick={handleAddCustomTargetSkill}
                  disabled={!customTargetSkill.trim()}
                  className="btn-outline btn-sm whitespace-nowrap disabled:opacity-50"
                >
                  Add Skill
                </button>
              </div>
            </div>
            
            {formData.target_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {formData.target_skills.map(skill => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-700"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => handleMultiSelect('target_skills', skill, formData.target_skills, (skills) => setFormData(prev => ({ ...prev, target_skills: skills })))}
                      className="ml-1 hover:text-green-900"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Overall Skill Level
            </label>
            <select
              value={formData.skill_level}
              onChange={(e) => handleInputChange('skill_level', e.target.value)}
              className="input-field"
            >
              {options.experience_levels.map(level => (
                <option key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Industry Interests */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900">Industry Interests</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {options.industries.map(industry => (
              <button
                key={industry}
                type="button"
                onClick={() => handleMultiSelect('industry_interests', industry, formData.industry_interests, (industries) => setFormData(prev => ({ ...prev, industry_interests: industries })))}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  formData.industry_interests.includes(industry)
                    ? 'bg-blue-100 border-blue-300 text-blue-700'
                    : 'bg-white border-secondary-300 text-secondary-700 hover:border-blue-300'
                }`}
              >
                {industry}
              </button>
            ))}
          </div>
        </div>

        {/* Learning Preferences */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-secondary-900">Learning Preferences</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Learning Style
              </label>
              <select
                value={formData.learning_style}
                onChange={(e) => handleInputChange('learning_style', e.target.value)}
                className="input-field"
              >
                {options.learning_styles.map(style => (
                  <option key={style} value={style}>
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Time Commitment
              </label>
              <select
                value={formData.time_commitment}
                onChange={(e) => handleInputChange('time_commitment', e.target.value)}
                className="input-field"
              >
                {options.time_commitments.map(commitment => (
                  <option key={commitment} value={commitment}>
                    {commitment.charAt(0).toUpperCase() + commitment.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.internship_interest}
                onChange={(e) => handleInputChange('internship_interest', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-secondary-700">Interested in internships</span>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!formData.career_goal || loading}
          className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <>
              <span>Get Comprehensive Career Guidance</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default ComprehensiveForm
