export interface Investment {
  id: number

  broker: string
  asset: string
  ticker: string
  market_ticker: string

  asset_type: string

  quantity: number
  purchase_price: number
  current_price: number

  currency: string

  purchase_date: string | null
}