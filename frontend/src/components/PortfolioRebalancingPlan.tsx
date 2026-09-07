import { useEffect, useState } from 'react'

import { getPortfolioRebalancing } from '../api/rebalancing'
import type { PortfolioRebalancing } from '../types/rebalancing'
import type { PortfolioTarget } from '../types/portfolioTarget'


interface PortfolioRebalancingPlanProps {
  targets: PortfolioTarget[]
}


function labelDimension(value: string) {
  return value === 'asset_type'
    ? 'Asset type'
    : 'Broker'
}


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat('en-IE', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}


function PortfolioRebalancingPlan({
  targets,
}: PortfolioRebalancingPlanProps) {
  const [data, setData] =
    useState<PortfolioRebalancing | null>(null)
  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadRebalancing() {
      try {
        setError(null)
        const result =
          await getPortfolioRebalancing()

        if (active) {
          setData(result)
        }
      } catch (loadError) {
        if (active) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Failed to load rebalancing plan.',
          )
        }
      }
    }

    void loadRebalancing()

    return () => {
      active = false
    }
  }, [targets])

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Rebalancing plan
          </h3>
          <p className="panel-subtitle">
            Amount needed to reach each allocation target
          </p>
        </div>

        {data && (
          <div className="base-currency-badge">
            {formatCurrency(
              data.portfolio_value,
              data.base_currency,
            )}
          </div>
        )}
      </div>

      {error ? (
        <div className="target-error" role="alert">
          {error}
        </div>
      ) : !data ? (
        <p className="target-empty">
          Loading rebalancing plan...
        </p>
      ) : data.items.length === 0 ? (
        <p className="target-empty">
          Add portfolio targets to create a plan.
        </p>
      ) : (
        <div className="table-scroll">
          <table className="positions-table">
            <thead>
              <tr>
                <th>Dimension</th>
                <th>Target</th>
                <th className="number">Current</th>
                <th className="number">Goal</th>
                <th className="number">Difference</th>
                <th className="number">Action</th>
              </tr>
            </thead>

            <tbody>
              {data.items.map((item) => (
                <tr
                  key={`${item.dimension}-${item.target_key}`}
                >
                  <td>
                    {labelDimension(item.dimension)}
                  </td>

                  <td>
                    <span className="ticker">
                      {item.target_key}
                    </span>
                  </td>

                  <td className="number">
                    {formatCurrency(
                      item.current_value,
                      item.currency,
                    )}
                    <div className="kpi-subvalue">
                      {item.current_percentage.toFixed(1)}%
                    </div>
                  </td>

                  <td className="number">
                    {formatCurrency(
                      item.target_value,
                      item.currency,
                    )}
                    <div className="kpi-subvalue">
                      {item.target_percentage.toFixed(1)}%
                    </div>
                  </td>

                  <td className="number">
                    <span
                      className={
                        item.difference >= 0
                          ? 'rebalance-positive'
                          : 'rebalance-negative'
                      }
                    >
                      {item.difference > 0 ? '+' : ''}
                      {formatCurrency(
                        item.difference,
                        item.currency,
                      )}
                    </span>
                  </td>

                  <td className="number">
                    <span
                      className={
                        `rebalance-badge ${
                          item.action.toLowerCase()
                        }`
                      }
                    >
                      {item.action}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}


export default PortfolioRebalancingPlan
