import {
  useEffect,
  useState,
} from 'react'

import {
  getPortfolioHealth,
} from '../api/analytics'

import type {
  PortfolioHealth,
} from '../api/analytics'


function PortfolioHealthPanel() {
  const [
    health,
    setHealth,
  ] = useState<
    PortfolioHealth | null
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
    async function loadHealth() {
      try {
        const data = (
          await getPortfolioHealth()
        )

        setHealth(data)
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load portfolio health.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadHealth()
  }, [])


  if (loading) {
    return (
      <section className="panel">
        <p>
          Loading portfolio health...
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
    health === null
  ) {
    return null
  }


  const components = [
    {
      name: 'Position diversification',
      data:
        health
          .components
          .position_diversification,
    },
    {
      name: 'HHI diversification',
      data:
        health
          .components
          .hhi_diversification,
    },
    {
      name: 'Broker diversification',
      data:
        health
          .components
          .broker_diversification,
    },
    {
      name: 'Currency diversification',
      data:
        health
          .components
          .currency_diversification,
    },
    {
      name: 'Asset type diversification',
      data:
        health
          .components
          .asset_type_diversification,
    },
  ]


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Portfolio health
          </h3>

          <p className="panel-subtitle">
            Diversification and concentration score
          </p>
        </div>

        <div className="base-currency-badge">
          {health.label}
        </div>
      </div>


      <section className="kpi-grid">
        <article className="kpi-card">
          <div className="kpi-label">
            Health score
          </div>

          <div className="kpi-value">
            {health.score.toFixed(0)}
            /{health.max_score}
          </div>

          <div className="kpi-subvalue">
            {health.label}
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Strengths
          </div>

          <div className="kpi-value">
            {health.strengths.length}
          </div>

          <div className="kpi-subvalue">
            Positive portfolio signals
          </div>
        </article>


        <article className="kpi-card">
          <div className="kpi-label">
            Watch items
          </div>

          <div className="kpi-value">
            {health.watch_items.length}
          </div>

          <div className="kpi-subvalue">
            Areas requiring attention
          </div>
        </article>
      </section>


      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Score components
              </h3>

              <p className="panel-subtitle">
                Contribution to total score
              </p>
            </div>
          </div>

          <div className="allocation-list">
            {
              components.map(
                (item) => {
                  const percentage = (
                    item.data.max_score > 0
                      ? (
                          item.data.score
                          / item.data.max_score
                        ) * 100
                      : 0
                  )

                  return (
                    <div
                      className="allocation-row"
                      key={item.name}
                    >
                      <div className="allocation-name">
                        {item.name}
                      </div>

                      <div className="allocation-track">
                        <div
                          className="allocation-fill"
                          style={{
                            width:
                              `${percentage}%`,
                          }}
                        />
                      </div>

                      <div className="allocation-percentage">
                        {
                          item.data.score.toFixed(
                            0,
                          )
                        }
                        /
                        {
                          item.data.max_score
                        }
                      </div>
                    </div>
                  )
                },
              )
            }
          </div>
        </div>


        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Health insights
              </h3>

              <p className="panel-subtitle">
                Strengths and items to monitor
              </p>
            </div>
          </div>


          <h3>
            Strengths
          </h3>

          <ul>
            {
              health.strengths.map(
                (item) => (
                  <li key={item}>
                    {item}
                  </li>
                ),
              )
            }
          </ul>


          <h3>
            Watch items
          </h3>

          <ul>
            {
              health.watch_items.map(
                (item) => (
                  <li key={item}>
                    {item}
                  </li>
                ),
              )
            }
          </ul>
        </div>
      </div>
    </section>
  )
}


export default PortfolioHealthPanel