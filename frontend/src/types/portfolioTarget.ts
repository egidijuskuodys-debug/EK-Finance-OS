export interface PortfolioTarget {
  id: number
  dimension: string
  target_key: string
  target_percentage: number
}

export interface PortfolioTargetInput {
  dimension: string
  target_key: string
  target_percentage: number
}

export interface PortfolioTargetUpdate {
  dimension?: string
  target_key?: string
  target_percentage?: number
}
