export interface ProjectionMilestone {
  years: number
  projected_value: number
  total_contributions: number
  investment_growth: number
}

export interface YearlyProjection {
  year: number
  value: number
}

export interface PortfolioProjection {
  currency: string
  starting_value: number
  monthly_contribution: number
  annual_return_percent: number
  milestones: ProjectionMilestone[]
  yearly_projection: YearlyProjection[]
}