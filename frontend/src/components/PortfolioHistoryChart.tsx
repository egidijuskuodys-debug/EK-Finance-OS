import {
  useEffect,
  useState,
} from 'react'

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getPortfolioHistory,
} from '../api/analytics'

import type {
  PortfolioHistoryPoint,
} from '../api/analytics'


type PortfolioHistoryChartProps = {
  currency: string
}


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat(
    'lt-LT',
    {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    },
  ).format(value)
}


function formatDate(
  value: string,
) {
  return new Intl.DateTimeFormat(
    'lt-LT',
    {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    },
  ).format(
    new Date(`${value}T00:00:00`),
  )
}


function formatAxisDate(
  value: string,
) {
  return new Intl.DateTimeFormat(
    'lt-LT',
    {
      year: '2-digit',
      month: 'short',
    },
  ).format(
    new Date(`${value}T00:00:00`),
  )
}


function PortfolioHistoryChart({
  currency,
}: PortfolioHistoryChartProps) {
  const [
    data,
    setData,
  ] = useState<
    PortfolioHistoryPoint[]
  >([])

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)


  useEffect(() => {
    async function loadHistory() {
      try {
        const history = (
          await getPortfolioHistory()
        )

        setData(history)
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load portfolio history.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadHistory()
  }, [])


  if (loading) {
    return (
      <div
        className="loading-state"
        style={{
          minHeight: 360,
        }}
      >
        Loading portfolio history...
      </div>
    )
  }


  if (error !== null) {
    return (
      <div
        className="error-state"
        style={{
          minHeight: 360,
        }}
      >
        {error}
      </div>
    )
  }


  if (data.length === 0) {
    return (
      <div
        className="empty-state"
        style={{
          minHeight: 360,
        }}
      >
        Portfolio history is not
        available.
      </div>
    )
  }


  return (
    <div
      style={{
        width: '100%',
        height: 360,
      }}
    >
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 10,
            left: 10,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient
              id="portfolioValueGradient"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="5%"
                stopColor="currentColor"
                stopOpacity={0.25}
              />

              <stop
                offset="95%"
                stopColor="currentColor"
                stopOpacity={0}
              />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey="date"
            tickFormatter={
              formatAxisDate
            }
            minTickGap={40}
          />

          <YAxis
            tickFormatter={
              (value: number) => (
                formatCurrency(
                  value,
                  currency,
                )
              )
            }
            width={90}
          />

          <Tooltip
            labelFormatter={
              (label) => (
                formatDate(
                  String(label),
                )
              )
            }
            formatter={
              (
                value,
                name,
              ) => {
                if (
                  name === 'value_eur'
                ) {
                  return [
                    formatCurrency(
                      Number(value),
                      currency,
                    ),
                    'Portfolio value',
                  ]
                }

                return [
                  String(value),
                  String(name),
                ]
              }
            }
          />

          <Area
            type="monotone"
            dataKey="value_eur"
            stroke="currentColor"
            fill={
              'url(#portfolioValueGradient)'
            }
            strokeWidth={2}
            dot={false}
            activeDot={{
              r: 4,
            }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}


export default PortfolioHistoryChart