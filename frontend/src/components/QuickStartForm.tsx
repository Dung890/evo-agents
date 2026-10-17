import React, { useState } from 'react'
import { OnboardingOptions } from '../services/api'
import { ArrowRight, Sparkles } from 'lucide-react'

interface QuickStartFormProps {
  options: OnboardingOptions
  onSubmit: (profile: any) => void
  loading: boolean
}

const QuickStartForm: React.FC<QuickStartFormProps> = ({ options, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    career_goal: '',
    current_skills: [] as string[],
    academic_year: 'sophomore',
    location: 'Dallas, TX'
  })

  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [customCareer, setCustomCareer] = useState('')
  const [customSkill, setCustomSkill] = useState('')
  const [showCustomCareer, setShowCustomCareer] = useState(false)

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSkillToggle = (skill: string) => {
    setSelectedSkills(prev => {
      const newSkills = prev.includes(skill)
        ? prev.filter(s => s !== skill)
        : [...prev, skill]
      
      setFormData(prev => ({ ...prev, current_skills: newSkills }))
      return newSkills
    })
  }

  const handleAddCustomSkill = () => {
    if (customSkill.trim() && !selectedSkills.includes(customSkill.trim())) {
      const newSkills = [...selectedSkills, customSkill.trim()]
      setSelectedSkills(newSkills)
      setFormData(prev => ({ ...prev, current_skills: newSkills }))
      setCustomSkill('')
    }
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="flex items-center mb-6">
        <Sparkles className="h-6 w-6 text-primary-600 mr-3" />
        <h2 className="text-2xl font-bold text-secondary-900">Quick Start</h2>
        <span className="ml-auto text-sm text-secondary-500">30 seconds</span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Career Goal */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            What career do you want to pursue? *
          </label>
          <select
            value={showCustomCareer ? 'custom' : formData.career_goal}
            onChange={(e) => handleCareerChange(e.target.value)}
            className="input-field"
            required={!showCustomCareer}
          >
            <option value="">Select your career goal</option>
            {options.career_goals.map(goal => (
              <option key={goal} value={goal}>{goal}</option>
            ))}
            <option value="custom">✏️ Other (type below)</option>
          </select>
          
          {showCustomCareer && (
            <div className="mt-3 flex gap-2">
              <input
                type="text"
                value={customCareer}
                onChange={(e) => setCustomCareer(e.target.value)}
                onBlur={handleCustomCareerSubmit}
                onKeyPress={(e) => e.key === 'Enter' && handleCustomCareerSubmit()}
                className="input-field flex-1"
                placeholder="Enter your career goal"
                autoFocus
                required
              />
            </div>
          )}
          {showCustomCareer && formData.career_goal && (
            <p className="text-sm text-success-600 mt-2">
              ✓ Career goal set: {formData.career_goal}
            </p>
          )}
        </div>

        {/* Current Skills */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            What skills do you already have? (Optional)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
            {options.skills.slice(0, 12).map(skill => (
              <button
                key={skill}
                type="button"
                onClick={() => handleSkillToggle(skill)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  selectedSkills.includes(skill)
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
                value={customSkill}
                onChange={(e) => setCustomSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomSkill())}
                className="input-field flex-1 text-sm"
                placeholder="e.g., React, Python, SQL"
              />
              <button
                type="button"
                onClick={handleAddCustomSkill}
                disabled={!customSkill.trim()}
                className="btn-outline btn-sm whitespace-nowrap disabled:opacity-50"
              >
                Add Skill
              </button>
            </div>
          </div>
          
          {selectedSkills.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {selectedSkills.map(skill => (
                <span
                  key={skill}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-100 text-primary-700"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => handleSkillToggle(skill)}
                    className="ml-1 hover:text-primary-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Academic Year */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            What year are you?
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

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Where do you want to work?
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleInputChange('location', e.target.value)}
            className="input-field"
            placeholder="e.g., Dallas, TX"
          />
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
              <span>Get My Career Guidance</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </form>

      <div className="mt-6 p-4 bg-primary-50 rounded-lg">
        <h4 className="font-medium text-primary-800 mb-2">What you'll get:</h4>
        <ul className="text-sm text-primary-700 space-y-1">
          <li>• Personalized course recommendations</li>
          <li>• Job market insights for your career</li>
          <li>• Project ideas to build your portfolio</li>
          <li>• Learning path tailored to your goals</li>
        </ul>
      </div>
    </div>
  )
}

export default QuickStartForm
