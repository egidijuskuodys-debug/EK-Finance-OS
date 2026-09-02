export interface Transaction {
  id: number

  investment_id: number

  broker_transaction_id: string | null

  transaction_type: string

  quantity: number
  price: number

  currency: string

  transaction_date: string

  realized_profit: number
}