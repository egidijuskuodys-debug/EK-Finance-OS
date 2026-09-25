import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  compareMortgageVsInvest,
} from '../api/mortgageVsInvest'
import type {
  MortgageReturnComparison,
  MortgageStrategyOutcome,
  MortgageVsInvestResponse,
} from '../types/mortgageVsInvest'


interface MortgageVsInvestPanelProps {
  propertyId: number
  propertyName: string
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
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(value)
}


function formatPercent(
  value: number,
) {
  return `${value.toFixed(2)}%`
}


function formatDate(
  value: string,
) {
  return new Intl.DateTimeFormat(
    'lt-LT',
    {
      year: 'numeric',
      month: 'short',
    },
  ).format(
    new Date(value),
  )
}


function formatDuration(
  months: number,
) {
  const years = Math.floor(
    months / 12,
  )

  const remainingMonths = (
    months % 12
  )

  if (years === 0) {
    return `${remainingMonths} mo`
  }

  if (remainingMonths === 0) {
    return `${years} yr`
  }

  return (
    `${years} yr `
    + `${remainingMonths} mo`
  )
}


function getStrategyLabel(
  strategy: string,
) {
  if (strategy === 'invest_only') {
    return 'Invest'
  }

  if (strategy === 'repay_first') {
    return 'Repay mortgage'
  }

  if (strategy === 'hybrid') {
    return 'Hybrid'
  }

  return strategy
}


function getOutcomes(
  comparison: MortgageReturnComparison,
) {
  return [
    comparison.invest_only,
    comparison.repay_first,
    comparison.hybrid,
  ]
}


function isWinner(
  comparison: MortgageReturnComparison,
  outcome: MortgageStrategyOutcome,
) {
  return (
    comparison.winner
    === outcome.strategy
  )
}


function MortgageVsInvestPanel({
  propertyId,
  propertyName,
  currency,
}: MortgageVsInvestPanelProps) {
  const [
    monthlyAmount,
    setMonthlyAmount,
  ] = useState('700')

  const [
    hybridPercentage,
    setHybridPercentage,
  ] = useState('50')

  const [
    returnScenarios,
    setReturnScenarios,
  ] = useState(['5', '7', '9'])

  const [
    result,
    setResult,
  ] = useState<
    MortgageVsInvestResponse | null
  >(null)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null)


  async function calculate(
    amount: number,
    percentage: number,
    annualReturns: number[],
  ) {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = (
        await compareMortgageVsInvest(
          propertyId,
          {
            monthly_extra_amount: (
              amount
            ),
            hybrid_mortgage_percentage: (
              percentage
            ),
            annual_investment_returns: (
              annualReturns
            ),
          },
        )
      )

      setResult(response)
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setError(error.message)
      } else {
        setError(
          'Failed to calculate comparison.',
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    calculate(
      700,
      50,
      [5, 7, 9],
    )
  }, [propertyId])


  function submitCalculation(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const amount = Number(
      monthlyAmount,
    )

    const percentage = Number(
      hybridPercentage,
    )

    const annualReturns = (
      returnScenarios.map(Number)
    )

    if (
      !Number.isFinite(amount)
      || amount <= 0
    ) {
      setError(
        'Enter a valid positive '
        + 'monthly amount.',
      )

      return
    }

    if (
      !Number.isFinite(percentage)
      || percentage < 0
      || percentage > 100
    ) {
      setError(
        'Hybrid mortgage share must '
        + 'be between 0 and 100.',
      )

      return
    }

    if (
      returnScenarios.some(
        (value) => value.trim() === '',
      )
      || annualReturns.some(
        (value) => (
          !Number.isFinite(value)
          || value <= -100
          || value > 100
        ),
      )
    ) {
      setError(
        'Enter three annual returns '
        + 'between -100% and 100%.',
      )

      return
    }

    if (
      annualReturns[0] >= annualReturns[1]
      || annualReturns[1] >= annualReturns[2]
    ) {
      setError(
        'Enter returns in ascending order: '
        + 'low, expected, high.',
      )

      return
    }

    calculate(
      amount,
      percentage,
      annualReturns,
    )
  }


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Mortgage vs invest
          </h3>

          <p className="panel-subtitle">
            Compare additional mortgage
            repayments with ETF investing
            for {propertyName}
          </p>
        </div>

        <span className="base-currency-badge">
          {currency}
        </span>
      </div>


      <form
        className="target-form mortgage-compare-form"
        onSubmit={submitCalculation}
      >
        <label className="mortgage-base-field">
          Additional monthly budget
          <input
            type="number"
            min="0.01"
            step="0.01"
            required
            value={monthlyAmount}
            onChange={
              (
                event,
              ) => (
                setMonthlyAmount(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label className="mortgage-base-field">
          Hybrid mortgage share (%)
          <input
            type="number"
            min="0"
            max="100"
            step="1"
            required
            value={hybridPercentage}
            onChange={
              (
                event,
              ) => (
                setHybridPercentage(
                  event.target.value,
                )
              )
            }
          />
        </label>

        {
          returnScenarios.map(
            (value, index) => (
              <label
                className="mortgage-return-field"
                key={index}
              >
                {[
                  'Low',
                  'Expected',
                  'High',
                ][index]} ETF return (%)
                <input
                  type="number"
                  min="-99.99"
                  max="100"
                  step="0.01"
                  required
                  value={value}
                  onChange={(event) => {
                    setReturnScenarios(
                      (current) => current.map(
                        (item, itemIndex) => (
                          itemIndex === index
                            ? event.target.value
                            : item
                        ),
                      ),
                    )
                  }}
                />
              </label>
            ),
          )
        }

        <button
          className="target-primary-button"
          type="submit"
          disabled={loading}
        >
          {
            loading
              ? 'Calculating...'
              : 'Compare strategies'
          }
        </button>
      </form>


      {
        error !== null
          ? (
              <div className="error-state">
                <p>{error}</p>
              </div>
            )
          : null
      }


      {
        result !== null
          ? (
              <>
                <section className="kpi-grid">
                  <article className="kpi-card">
                    <div className="kpi-label">
                      Mortgage balance
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          result
                            .baseline
                            .loan_balance,
                          result.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Current outstanding debt
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Interest rate
                    </div>

                    <div className="kpi-value">
                      {
                        formatPercent(
                          result
                            .baseline
                            .annual_interest_rate,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Current mortgage rate
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Baseline interest
                    </div>

                    <div className="kpi-value negative">
                      {
                        formatCurrency(
                          result
                            .baseline
                            .total_interest,
                          result.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Estimated until loan end
                    </div>
                  </article>

                  <article className="kpi-card">
                    <div className="kpi-label">
                      Comparison horizon
                    </div>

                    <div className="kpi-value">
                      {
                        formatDate(
                          result
                            .comparison_end_date,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        formatDuration(
                          result
                            .baseline
                            .remaining_months,
                        )
                      }
                    </div>
                  </article>
                </section>


                {
                  result.comparisons.map(
                    (
                      comparison,
                    ) => (
                      <section
                        key={
                          comparison
                            .annual_investment_return
                        }
                      >
                        <div className="panel-header">
                          <div>
                            <h4 className="panel-title">
                              {
                                formatPercent(
                                  comparison
                                    .annual_investment_return,
                                )
                              }
                              {' '}investment return
                            </h4>

                            <p className="panel-subtitle">
                              Winner:{' '}
                              {
                                getStrategyLabel(
                                  comparison.winner,
                                )
                              }
                              {' '}by{' '}
                              {
                                formatCurrency(
                                  comparison
                                    .difference_to_second,
                                  result.currency,
                                )
                              }
                            </p>
                          </div>
                        </div>

                        <div className="table-scroll">
                          <table className="positions-table">
                            <thead>
                              <tr>
                                <th>Strategy</th>

                                <th className="number">
                                  Mortgage / mo
                                </th>

                                <th className="number">
                                  Invest / mo
                                </th>

                                <th className="number">
                                  Mortgage free
                                </th>

                                <th className="number">
                                  Interest saved
                                </th>

                                <th className="number">
                                  Value at horizon
                                </th>

                                <th className="number">
                                  Vs invest
                                </th>
                              </tr>
                            </thead>

                            <tbody>
                              {
                                getOutcomes(
                                  comparison,
                                ).map(
                                  (
                                    outcome,
                                  ) => (
                                    <tr
                                      key={
                                        outcome.strategy
                                      }
                                    >
                                      <td>
                                        <span
                                          className={
                                            isWinner(
                                              comparison,
                                              outcome,
                                            )
                                              ? 'positive'
                                              : ''
                                          }
                                        >
                                          {
                                            getStrategyLabel(
                                              outcome
                                                .strategy,
                                            )
                                          }
                                        </span>

                                        {
                                          isWinner(
                                            comparison,
                                            outcome,
                                          )
                                            ? (
                                                <div className="panel-subtitle">
                                                  Best projected result
                                                </div>
                                              )
                                            : null
                                        }
                                      </td>

                                      <td className="number">
                                        {
                                          formatCurrency(
                                            outcome
                                              .mortgage_monthly_amount,
                                            result.currency,
                                          )
                                        }
                                      </td>

                                      <td className="number">
                                        {
                                          formatCurrency(
                                            outcome
                                              .investment_monthly_amount,
                                            result.currency,
                                          )
                                        }
                                      </td>

                                      <td className="number">
                                        {
                                          formatDate(
                                            outcome
                                              .payoff_date,
                                          )
                                        }

                                        <div className="panel-subtitle">
                                          {
                                            formatDuration(
                                              outcome
                                                .payoff_months,
                                            )
                                          }
                                        </div>
                                      </td>

                                      <td className="number positive">
                                        {
                                          formatCurrency(
                                            outcome
                                              .interest_saved,
                                            result.currency,
                                          )
                                        }
                                      </td>

                                      <td
                                        className={
                                          (
                                            'number '
                                            + (
                                              isWinner(
                                                comparison,
                                                outcome,
                                              )
                                                ? 'positive'
                                                : ''
                                            )
                                          )
                                        }
                                      >
                                        {
                                          formatCurrency(
                                            outcome
                                              .investment_value_at_horizon,
                                            result.currency,
                                          )
                                        }
                                      </td>

                                      <td
                                        className={
                                          (
                                            'number '
                                            + (
                                              outcome
                                                .advantage_vs_invest_only
                                              >= 0
                                                ? 'positive'
                                                : 'negative'
                                            )
                                          )
                                        }
                                      >
                                        {
                                          formatCurrency(
                                            outcome
                                              .advantage_vs_invest_only,
                                            result.currency,
                                          )
                                        }
                                      </td>
                                    </tr>
                                  ),
                                )
                              }
                            </tbody>
                          </table>
                        </div>
                      </section>
                    ),
                  )
                }


                <div className="panel-header">
                  <div>
                    <h4 className="panel-title">
                      Assumptions
                    </h4>

                    {
                      result.assumptions.map(
                        (
                          assumption,
                        ) => (
                          <p
                            className="panel-subtitle"
                            key={assumption}
                          >
                            • {assumption}
                          </p>
                        ),
                      )
                    }
                  </div>
                </div>
              </>
            )
          : null
      }
    </section>
  )
}


export default MortgageVsInvestPanel
