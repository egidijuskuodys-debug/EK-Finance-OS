import {
  useEffect,
  useState,
} from 'react'

import {
  getPortfolioRisk,
} from '../api/analytics'

import type {
  PortfolioRisk,
} from '../api/analytics'


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


function PortfolioRiskPanel() {
  const [
    risk,
    setRisk,
  ] = useState<
    PortfolioRisk | null
  >(null)

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
    async function loadRisk() {
      try {
        const data = (
          await getPortfolioRisk()
        )

        setRisk(data)
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load portfolio risk.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadRisk()
  }, [])


  if (loading) {
    return (
      <section className="panel">
        <p>
          Loading portfolio risk...
        </p>
      </section>
    )
  }


  if (
    error !== null
  ) {
    return (
      <section className="panel">
        <p className="negative">
          {error}
        </p>
      </section>
    )
  }


  if (
    risk === null
  ) {
    return null
  }


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Portfolio risk
          </h3>

          <p className="panel-subtitle">
            Concentration and exposure
            overview
          </p>
        </div>
      </div>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Largest position
          </div>

          <div className="kpi-value">
            {
              risk.largest_position
                ? formatPercent(
                    risk
                      .largest_position
                      .percentage,
                  )
                : '—'
            }
          </div>

          <div className="kpi-subvalue">
            {
              risk.largest_position
                ?.ticker
              ?? 'No position'
            }
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Top 3 concentration
          </div>

          <div className="kpi-value">
            {
              formatPercent(
                risk
                  .concentration
                  .top_3_percentage,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Three largest positions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Top 5 concentration
          </div>

          <div className="kpi-value">
            {
              formatPercent(
                risk
                  .concentration
                  .top_5_percentage,
              )
            }
          </div>

          <div className="kpi-subvalue">
            Five largest positions
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            HHI
          </div>

          <div className="kpi-value">
            {
              risk
                .concentration
                .hhi
                .toFixed(2)
            }
          </div>

          <div className="kpi-subvalue">
            Position concentration index
          </div>
        </article>
      </section>


      <div className="dashboard-grid">
        <div>
          <h3>
            Broker exposure
          </h3>

          <div className="allocation-list">
            {
              risk.by_broker.map(
                (item) => (
                  <div
                    className="allocation-row"
                    key={item.broker}
                  >
                    <div className="allocation-name">
                      {item.broker}
                    </div>

                    <div className="allocation-track">
                      <div
                        className="allocation-fill"
                        style={{
                          width:
                            `${item.percentage}%`,
                        }}
                      />
                    </div>

                    <div className="allocation-percentage">
                      {
                        formatPercent(
                          item.percentage,
                        )
                      }
                    </div>
                  </div>
                ),
              )
            }
          </div>
        </div>


        <div>
          <h3>
            Currency exposure
          </h3>

          <div className="allocation-list">
            {
              risk.by_currency.map(
                (item) => (
                  <div
                    className="allocation-row"
                    key={item.currency}
                  >
                    <div className="allocation-name">
                      {item.currency}
                    </div>

                    <div className="allocation-track">
                      <div
                        className="allocation-fill"
                        style={{
                          width:
                            `${item.percentage}%`,
                        }}
                      />
                    </div>

                    <div className="allocation-percentage">
                      {
                        formatPercent(
                          item.percentage,
                        )
                      }
                    </div>
                  </div>
                ),
              )
            }
          </div>
        </div>
      </div>


      <div className="table-scroll">
        <table className="positions-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Broker</th>
              <th>Type</th>
              <th className="number">
                Value
              </th>
              <th className="number">
                Weight
              </th>
            </tr>
          </thead>

          <tbody>
            {
              risk.top_positions.map(
                (position) => (
                  <tr
                    key={
                      position
                        .investment_id
                    }
                  >
                    <td>
                      <span className="ticker">
                        {position.ticker}
                      </span>
                    </td>

                    <td>
                      {position.broker}
                    </td>

                    <td>
                      <span className="asset-type">
                        {
                          position
                            .asset_type
                        }
                      </span>
                    </td>

                    <td className="number">
                      {
                        formatCurrency(
                          position.value,
                          risk.base_currency,
                        )
                      }
                    </td>

                    <td className="number">
                      {
                        formatPercent(
                          position
                            .percentage,
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
  )
}


export default PortfolioRiskPanel