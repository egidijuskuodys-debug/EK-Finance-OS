import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { getContributionPlan } from '../api/contributionPlan'
import type { ContributionPlan } from '../types/contributionPlan'
import type { PortfolioTarget } from '../types/portfolioTarget'


interface ContributionPlanPanelProps {
  targets: PortfolioTarget[]
}


function labelDimension(value: string) {
  return value === 'asset_type'
    ? 'By asset type'
    : 'By broker'
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


function ContributionPlanPanel({
  targets,
}: ContributionPlanPanelProps) {
  const [amount, setAmount] = useState('1000')
  const [planAmount, setPlanAmount] = useState(1000)
  const [data, setData] =
    useState<ContributionPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadPlan() {
      try {
        setLoading(true)
        setError(null)

        const result = await getContributionPlan(
          planAmount,
        )

        if (active) {
          setData(result)
        }
      } catch (loadError) {
        if (active) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Failed to load contribution plan.',
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadPlan()

    return () => {
      active = false
    }
  }, [planAmount, targets])

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const numericAmount = Number(amount)

    if (
      Number.isNaN(numericAmount)
      || numericAmount <= 0
    ) {
      setError(
        'Contribution amount must be greater than zero.',
      )
      return
    }

    setPlanAmount(numericAmount)
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            New contribution plan
          </h3>
          <p className="panel-subtitle">
            Allocate new money toward underweight targets
            without selling existing investments
          </p>
        </div>
      </div>

      <form
        className="contribution-form"
        onSubmit={handleSubmit}
      >
        <label>
          Contribution amount
          <input
            type="number"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            min="0.01"
            step="0.01"
            required
          />
        </label>

        <button
          className="target-primary-button"
          type="submit"
          disabled={loading}
        >
          {loading ? 'Calculating...' : 'Calculate plan'}
        </button>
      </form>

      {error && (
        <div className="target-error" role="alert">
          {error}
        </div>
      )}

      {data && !error && (
        <>
          <div className="contribution-summary">
            <div>
              <span>New contribution</span>
              <strong>
                {formatCurrency(
                  data.contribution_amount,
                  data.base_currency,
                )}
              </strong>
            </div>

            <div>
              <span>Portfolio after contribution</span>
              <strong>
                {formatCurrency(
                  data.future_portfolio_value,
                  data.base_currency,
                )}
              </strong>
            </div>
          </div>

          <p className="contribution-note">
            Asset type and broker are two views of the same
            contribution. Do not add their totals together.
          </p>

          <div className="contribution-groups">
            {data.groups.map((group) => (
              <article
                className="contribution-group"
                key={group.dimension}
              >
                <div className="panel-header">
                  <div>
                    <h4 className="panel-title">
                      {labelDimension(group.dimension)}
                    </h4>
                    <p className="panel-subtitle">
                      Suggested allocation of{' '}
                      {formatCurrency(
                        group.allocated_amount,
                        data.base_currency,
                      )}
                    </p>
                  </div>
                </div>

                <div className="table-scroll">
                  <table className="positions-table">
                    <thead>
                      <tr>
                        <th>Target</th>
                        <th className="number">
                          Invest now
                        </th>
                        <th className="number">
                          Future share
                        </th>
                        <th className="number">
                          Goal
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {group.allocations.map((item) => (
                        <tr key={item.target_key}>
                          <td>
                            <span className="ticker">
                              {item.target_key}
                            </span>
                          </td>

                          <td className="number">
                            <strong
                              className={
                                item.suggested_amount > 0
                                  ? 'rebalance-positive'
                                  : ''
                              }
                            >
                              {formatCurrency(
                                item.suggested_amount,
                                data.base_currency,
                              )}
                            </strong>
                          </td>

                          <td className="number">
                            {item.future_percentage.toFixed(1)}%
                          </td>

                          <td className="number">
                            {item.target_percentage.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  )
}


export default ContributionPlanPanel
