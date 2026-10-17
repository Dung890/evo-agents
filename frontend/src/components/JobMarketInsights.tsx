import { TrendingUp, DollarSign } from 'lucide-react'

interface JobMarketInsightsProps {
  jobInsights: string[]
  marketInsights: any
}

const JobMarketInsights: React.FC<JobMarketInsightsProps> = ({ jobInsights, marketInsights }) => {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Job Insights */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-primary-600" />
          Job Market Overview
        </h3>
        <div className="space-y-3">
          {jobInsights.map((insight, index) => (
            <div key={index} className="flex items-start">
              <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
              <p className="text-secondary-700">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Market Insights */}
      {marketInsights && (
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
            <DollarSign className="h-5 w-5 mr-2 text-green-600" />
            Market Trends
          </h3>
          
          {marketInsights.hot_skills && (
            <div className="mb-4">
              <h4 className="font-medium text-secondary-800 mb-2">Hot Skills</h4>
              <div className="flex flex-wrap gap-2">
                {marketInsights.hot_skills.slice(0, 6).map((skill: string, index: number) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-green-100 text-green-700 text-sm rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {marketInsights.job_trends && (
            <div className="mb-4">
              <h4 className="font-medium text-secondary-800 mb-2">Job Trends</h4>
              <div className="space-y-2">
                {marketInsights.job_trends.slice(0, 3).map((trend: string, index: number) => (
                  <p key={index} className="text-sm text-secondary-600">• {trend}</p>
                ))}
              </div>
            </div>
          )}

          {marketInsights.market_health && (
            <div>
              <h4 className="font-medium text-secondary-800 mb-2">Market Health</h4>
              <p className="text-sm text-secondary-600">{marketInsights.market_health}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default JobMarketInsights
