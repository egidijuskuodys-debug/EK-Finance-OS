import {
  useState,
} from "react"

import {
  getFinancialPlan,
} from "../api/financialPlan"

import type {
  FinancialPlanResponse,
} from "../types/financialPlan"


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat(
    "lt-LT",
    {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(value)
}


export default function FinancialPlanPanel() {
  const [
    monthlyBudget,
    setMonthlyBudget,
  ] = useState(1000)

  const [
    mortgageShare,
    setMortgageShare,
  ] = useState(20)

  const [
    expectedReturn,
    setExpectedReturn,
  ] = useState(7)

  const [
    plan,
    setPlan,
  ] = useState<FinancialPlanResponse | null>(
    null,
  )

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  )


  async function calculatePlan() {
    setLoading(true)
    setError(null)

    try {
      const result =
        await getFinancialPlan({
          monthly_budget: monthlyBudget,
          mortgage_share_percent:
            mortgageShare,
          expected_etf_return_percent:
            expectedReturn,
          projection_years: [
            1,
            5,
            10,
          ],
        })

      setPlan(result)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          "Nepavyko apskaičiuoti plano.",
        )
      }
    } finally {
      setLoading(false)
    }
  }


  return (
    <section
      className="panel"
      style={{
        marginTop: "28px",
      }}
    >
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Finansinis planas
          </h3>

          <p className="panel-subtitle">
            Mėnesio biudžeto paskirstymo tarp
            investavimo ir papildomo paskolos
            grąžinimo scenarijus.
          </p>
        </div>
      </div>

      <div
        className="target-form"
        style={{
          gridTemplateColumns:
            "repeat(3, minmax(0, 1fr)) auto",
          marginBottom: "24px",
        }}
      >
        <label>
          Mėnesio biudžetas (€)

          <input
            type="number"
            min="1"
            step="50"
            value={monthlyBudget}
            onChange={(event) =>
              setMonthlyBudget(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Papildomai paskolai (%)

          <input
            type="number"
            min="0"
            max="100"
            step="5"
            value={mortgageShare}
            onChange={(event) =>
              setMortgageShare(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Tikėtina ETF grąža (%)

          <input
            type="number"
            min="0"
            max="100"
            step="0.5"
            value={expectedReturn}
            onChange={(event) =>
              setExpectedReturn(
                Number(event.target.value),
              )
            }
          />
        </label>

        <button
          className="target-primary-button"
          type="button"
          onClick={calculatePlan}
          disabled={loading}
        >
          {loading
            ? "Skaičiuojama..."
            : "Apskaičiuoti"}
        </button>
      </div>

      {error && (
        <div className="target-error">
          {error}
        </div>
      )}

      {plan && (
        <>
          <div className="kpi-grid">
            <article className="kpi-card">
              <div className="kpi-label">
                Investavimui / mėn.
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  plan.monthly_investment_amount,
                  plan.base_currency,
                )}
              </div>

              <div className="kpi-subvalue">
                {
                  plan.investment_share_percent
                }
                % mėnesio biudžeto
              </div>
            </article>

            <article className="kpi-card">
              <div className="kpi-label">
                Papildomai paskolai / mėn.
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  plan.monthly_mortgage_amount,
                  plan.base_currency,
                )}
              </div>

              <div className="kpi-subvalue">
                {
                  plan.mortgage_share_percent
                }
                % mėnesio biudžeto
              </div>
            </article>

            <article className="kpi-card">
              <div className="kpi-label">
                Investavimui / metus
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  plan.annual_investment_amount,
                  plan.base_currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Pagal pasirinktą mėnesio planą
              </div>
            </article>

            <article className="kpi-card">
              <div className="kpi-label">
                Dabartinis portfelis
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  plan.current_investment_wealth,
                  plan.base_currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Naudojama kaip prognozės pradžia
              </div>
            </article>
          </div>

          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Investicijų prognozė
              </h3>

              <p className="panel-subtitle">
                Pagal pasirinktą{" "}
                {
                  plan.expected_etf_return_percent
                }
                % metinę ETF grąžą.
              </p>
            </div>
          </div>

          <div className="table-scroll">
            <table className="positions-table">
              <thead>
                <tr>
                  <th>
                    Laikotarpis
                  </th>

                  <th className="number">
                    Papildomai investuota
                  </th>

                  <th className="number">
                    Investicijų augimas
                  </th>

                  <th className="number">
                    Prognozuojama vertė
                  </th>
                </tr>
              </thead>

              <tbody>
                {plan.projections.map(
                  (projection) => (
                    <tr
                      key={
                        projection.years
                      }
                    >
                      <td>
                        <strong>
                          {
                            projection.years
                          }{" "}
                          m.
                        </strong>
                      </td>

                      <td className="number">
                        {formatCurrency(
                          projection
                            .additional_invested,
                          plan.base_currency,
                        )}
                      </td>

                      <td className="number positive">
                        {formatCurrency(
                          projection
                            .estimated_growth,
                          plan.base_currency,
                        )}
                      </td>

                      <td className="number">
                        <strong>
                          {formatCurrency(
                            projection
                              .projected_investment_value,
                            plan.base_currency,
                          )}
                        </strong>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>

          <div
            className="contribution-note"
            style={{
              marginTop: "20px",
              marginBottom: 0,
            }}
          >
            Prognozė yra scenarijus pagal
            pasirinktą metinę ETF grąžą.
            Faktinė investicijų grąža gali
            būti didesnė arba mažesnė.
          </div>
        </>
      )}
    </section>
  )
}