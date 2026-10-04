import {
  useEffect,
  useState,
} from "react"

import {
  getFinancialIndependence,
} from "../api/financialIndependence"

import type {
  FinancialIndependence,
} from "../types/financialIndependence"


function formatCurrency(
  value: number,
  currency: string,
) {
  return new Intl.NumberFormat(
    "lt-LT",
    {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    },
  ).format(value)
}


function formatCurrencyDetailed(
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


function FinancialIndependencePanel() {
  const [
    data,
    setData,
  ] = useState<
    FinancialIndependence | null
  >(null)

  const [
    monthlyIncomeTarget,
    setMonthlyIncomeTarget,
  ] = useState(1000)

  const [
    withdrawalRate,
    setWithdrawalRate,
  ] = useState(4)

  const [
    monthlyContribution,
    setMonthlyContribution,
  ] = useState(1000)

  const [
    annualReturn,
    setAnnualReturn,
  ] = useState(7)

  const [
    propertyGrowth,
    setPropertyGrowth,
  ] = useState(2)

  const [
    currentAge,
    setCurrentAge,
  ] = useState(45)

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")


  async function loadProjection() {
    try {
      setLoading(true)
      setError("")

      const result =
        await getFinancialIndependence(
          monthlyIncomeTarget,
          withdrawalRate,
          monthlyContribution,
          annualReturn,
          propertyGrowth,
          currentAge,
        )

      setData(result)
    } catch {
      setError(
        "Nepavyko apskaičiuoti FI prognozės.",
      )
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    void loadProjection()
  }, [])


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">
            Finansinė nepriklausomybė
          </h2>

          <p className="panel-subtitle">
            Investicijų portfelis ir NT
            grynasis cash flow vertinami
            atskirai, o jų pajamos
            sujungiamos į bendrą FI tikslą.
          </p>
        </div>
      </div>

      <div className="target-form">
        <label>
          Mėnesio pajamų tikslas
          <input
            type="number"
            min="1"
            step="50"
            value={monthlyIncomeTarget}
            onChange={(event) =>
              setMonthlyIncomeTarget(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Išėmimo norma (%)
          <input
            type="number"
            min="0.1"
            max="100"
            step="0.1"
            value={withdrawalRate}
            onChange={(event) =>
              setWithdrawalRate(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Mėnesio investicija
          <input
            type="number"
            min="0"
            step="50"
            value={monthlyContribution}
            onChange={(event) =>
              setMonthlyContribution(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Investicijų grąža (%)
          <input
            type="number"
            step="0.1"
            value={annualReturn}
            onChange={(event) =>
              setAnnualReturn(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          NT vertės augimas (%)
          <input
            type="number"
            step="0.1"
            value={propertyGrowth}
            onChange={(event) =>
              setPropertyGrowth(
                Number(event.target.value),
              )
            }
          />
        </label>

        <label>
          Dabartinis amžius
          <input
            type="number"
            min="0"
            max="120"
            step="1"
            value={currentAge}
            onChange={(event) =>
              setCurrentAge(
                Number(event.target.value),
              )
            }
          />
        </label>
      </div>

      <button
        className="target-primary-button"
        type="button"
        onClick={() => {
          void loadProjection()
        }}
        disabled={loading}
      >
        {loading
          ? "Skaičiuojama..."
          : "Apskaičiuoti FI tikslą"}
      </button>

      {error && (
        <p className="contribution-note">
          {error}
        </p>
      )}

      {data && (
        <>
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-label">
                Reikalingas FI kapitalas
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  data.required_capital,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Investicijoms, įvertinus
                NT cash flow
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                Dabartinis FI kapitalas
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  data.current_fi_capital,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Investicinis portfelis
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                Investicijų pajamos
              </div>

              <div className="kpi-value">
                {formatCurrencyDetailed(
                  data
                    .investment_monthly_passive_income,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Per mėnesį pagal{" "}
                {data.withdrawal_rate_percent} %
                taisyklę
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                NT cash flow
              </div>

              <div className="kpi-value">
                {formatCurrencyDetailed(
                  data.rental_monthly_cash_flow,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Nuoma − išlaidos − paskolos
                įmokos
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                Bendros pasyvios pajamos
              </div>

              <div className="kpi-value">
                {formatCurrencyDetailed(
                  data
                    .current_monthly_passive_income,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Investicijos + NT cash flow
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                FI progresas
              </div>

              <div className="kpi-value">
                {data.progress_percent.toFixed(
                  2,
                )} %
              </div>

              <div className="kpi-subvalue">
                Pagal reikalingą
                investicinį kapitalą
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                Prognozuojamas FI tikslas
              </div>

              <div className="kpi-value">
                {data.years_to_goal !== null
                  ? `${data.years_to_goal} metų`
                  : "Neprognozuojama"}
              </div>

              <div className="kpi-subvalue">
                {data.projected_age_at_goal
                  !== null
                  ? `${data.projected_age_at_goal} metų amžiaus`
                  : "Per prognozės laikotarpį nepasiekiamas"}
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                NT nuosavas kapitalas
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  data
                    .current_real_estate_equity,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Įtrauktas į net worth,
                bet ne į FI kapitalą
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-label">
                Bendras grynasis turtas
              </div>

              <div className="kpi-value">
                {formatCurrency(
                  data.current_net_worth,
                  data.currency,
                )}
              </div>

              <div className="kpi-subvalue">
                Investicijos + NT equity
              </div>
            </div>
          </div>

          <div className="allocation-list">
            <div className="allocation-row">
              <div>
                <strong>
                  FI progresas
                </strong>

                <span>
                  {formatCurrency(
                    data.current_fi_capital,
                    data.currency,
                  )}
                  {" / "}
                  {formatCurrency(
                    data.required_capital,
                    data.currency,
                  )}
                </span>
              </div>

              <div className="allocation-track">
                <div
                  className="allocation-fill"
                  style={{
                    width: `${
                      Math.min(
                        data.progress_percent,
                        100,
                      )
                    }%`,
                  }}
                />
              </div>
            </div>
          </div>

          <p className="contribution-note">
            Iš tavo{" "}
            {formatCurrencyDetailed(
              data.monthly_income_target,
              data.currency,
            )}{" "}
            mėnesio FI tikslo NT šiuo
            metu padengia{" "}
            {formatCurrencyDetailed(
              data.rental_monthly_cash_flow,
              data.currency,
            )}
            , todėl investicijos turi
            generuoti{" "}
            {formatCurrencyDetailed(
              data.investment_income_target,
              data.currency,
            )}{" "}
            per mėnesį.
          </p>

          <div className="positions-table">
            <table>
              <thead>
                <tr>
                  <th>Laikotarpis</th>
                  <th>FI kapitalas</th>
                  <th>NT equity</th>
                  <th>Net worth</th>
                  <th>
                    Investicijų pajamos
                  </th>
                  <th>NT cash flow</th>
                  <th>
                    Bendros pasyvios pajamos
                  </th>
                  <th>Būsena</th>
                </tr>
              </thead>

              <tbody>
                {data.yearly_projection.map(
                  (point) => (
                    <tr key={point.year}>
                      <td>
                        {point.year === 0
                          ? "Dabar"
                          : `${point.year} m.`}
                      </td>

                      <td>
                        {formatCurrency(
                          point.investment_value,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {formatCurrency(
                          point
                            .real_estate_equity,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {formatCurrency(
                          point.net_worth,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {formatCurrencyDetailed(
                          point
                            .investment_monthly_passive_income,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {formatCurrencyDetailed(
                          point
                            .rental_monthly_cash_flow,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {formatCurrencyDetailed(
                          point
                            .monthly_passive_income,
                          data.currency,
                        )}
                      </td>

                      <td>
                        {point.target_reached
                          ? "Tikslas pasiektas"
                          : "Dar nepasiektas"}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>

          <p className="contribution-note">
            4 % išėmimo taisyklė taikoma
            tik investiciniam portfeliui.
            NT nuosavas kapitalas yra
            bendro grynojo turto dalis,
            tačiau FI pajamoms naudojamas
            tik realus NT cash flow:
            nuoma minus NT išlaidos ir
            paskolos įmokos.
          </p>
        </>
      )}
    </section>
  )
}


export default FinancialIndependencePanel