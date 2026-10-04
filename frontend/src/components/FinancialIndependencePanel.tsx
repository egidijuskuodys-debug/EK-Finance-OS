import {
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  getFinancialIndependence,
} from '../api/financialIndependence'
import type {
  FinancialIndependence,
} from '../types/financialIndependence'


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


function formatPercent(
  value: number,
) {
  return `${value.toFixed(2)}%`
}


function FinancialIndependencePanel() {
  const [
    projection,
    setProjection,
  ] = useState<
    FinancialIndependence | null
  >(null)

  const [
    monthlyIncomeTarget,
    setMonthlyIncomeTarget,
  ] = useState('1000')

  const [
    withdrawalRate,
    setWithdrawalRate,
  ] = useState('4')

  const [
    monthlyContribution,
    setMonthlyContribution,
  ] = useState('1000')

  const [
    annualReturn,
    setAnnualReturn,
  ] = useState('7')

  const [
    propertyGrowth,
    setPropertyGrowth,
  ] = useState('2')

  const [
    currentAge,
    setCurrentAge,
  ] = useState('45')

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


  async function loadProjection(
    incomeTarget: number,
    rate: number,
    contribution: number,
    returnPercent: number,
    growthPercent: number,
    age: number,
  ) {
    setLoading(true)
    setError(null)

    try {
      const data = (
        await getFinancialIndependence(
          incomeTarget,
          rate,
          contribution,
          returnPercent,
          growthPercent,
          age,
        )
      )

      setProjection(data)
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setError(
          error.message,
        )
      } else {
        setError(
          (
            'Nepavyko įkelti finansinės '
            + 'nepriklausomybės prognozės.'
          ),
        )
      }
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadProjection(
      1000,
      4,
      1000,
      7,
      2,
      45,
    )
  }, [])


  function calculateProjection(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const incomeTarget = Number(
      monthlyIncomeTarget,
    )

    const rate = Number(
      withdrawalRate,
    )

    const contribution = Number(
      monthlyContribution,
    )

    const returnPercent = Number(
      annualReturn,
    )

    const growthPercent = Number(
      propertyGrowth,
    )

    const age = Number(
      currentAge,
    )

    if (
      !Number.isFinite(incomeTarget)
      || incomeTarget <= 0
      || !Number.isFinite(rate)
      || rate <= 0
      || rate > 100
      || !Number.isFinite(contribution)
      || contribution < 0
      || !Number.isFinite(returnPercent)
      || returnPercent <= -100
      || returnPercent > 100
      || !Number.isFinite(growthPercent)
      || growthPercent <= -100
      || growthPercent > 100
      || !Number.isInteger(age)
      || age < 0
      || age > 120
    ) {
      setError(
        'Įveskite tinkamas prognozės reikšmes.',
      )

      return
    }

    loadProjection(
      incomeTarget,
      rate,
      contribution,
      returnPercent,
      growthPercent,
      age,
    )
  }


  const milestoneYears = new Set([
    0,
    5,
    10,
    15,
  ])

  const milestonePoints = (
    projection?.yearly_projection.filter(
      (
        point,
      ) => (
        milestoneYears.has(
          point.year,
        )
        || point.year
        === projection.years_to_goal
      ),
    )
    ?? []
  )


  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h3 className="panel-title">
            Finansinė nepriklausomybė
          </h3>

          <p className="panel-subtitle">
            Prognozė, kada investicinis kapitalas
            gali pasiekti tavo pasyvių pajamų tikslą
          </p>
        </div>
      </div>


      <form
        className="target-form"
        onSubmit={calculateProjection}
      >
        <label>
          Mėnesio pajamų tikslas
          <input
            type="number"
            min="1"
            step="50"
            value={monthlyIncomeTarget}
            onChange={
              (
                event,
              ) => (
                setMonthlyIncomeTarget(
                  event.target.value,
                )
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
            onChange={
              (
                event,
              ) => (
                setWithdrawalRate(
                  event.target.value,
                )
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
            onChange={
              (
                event,
              ) => (
                setMonthlyContribution(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          Investicijų grąža (%)
          <input
            type="number"
            min="-99"
            max="100"
            step="0.1"
            value={annualReturn}
            onChange={
              (
                event,
              ) => (
                setAnnualReturn(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <label>
          NT vertės augimas (%)
          <input
            type="number"
            min="-99"
            max="100"
            step="0.1"
            value={propertyGrowth}
            onChange={
              (
                event,
              ) => (
                setPropertyGrowth(
                  event.target.value,
                )
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
            onChange={
              (
                event,
              ) => (
                setCurrentAge(
                  event.target.value,
                )
              )
            }
          />
        </label>

        <button
          className="target-primary-button"
          type="submit"
          disabled={loading}
        >
          {
            loading
              ? 'Skaičiuojama...'
              : 'Apskaičiuoti FI tikslą'
          }
        </button>
      </form>


      {
        error
          ? (
              <p className="negative">
                {error}
              </p>
            )
          : null
      }


      {
        projection !== null
          ? (
              <>
                <section className="kpi-grid">
                  <article className="kpi-card">
                    <div className="kpi-label">
                      Reikalingas FI kapitalas
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .required_capital,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        formatCurrency(
                          projection
                            .monthly_income_target,
                          projection.currency,
                        )
                      } per mėnesį
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      Dabartinis FI kapitalas
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .current_fi_capital,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Investicinis portfelis
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      Dabartinės pasyvios pajamos
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .current_monthly_passive_income,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Taikant {
                        formatPercent(
                          projection
                            .withdrawal_rate_percent,
                        )
                      } išėmimo normą
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      FI progresas
                    </div>

                    <div className="kpi-value positive">
                      {
                        formatPercent(
                          projection
                            .progress_percent,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Trūksta:{' '}
                      {
                        formatCurrency(
                          projection
                            .remaining_gap,
                          projection.currency,
                        )
                      }
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      Prognozuojamas FI tikslas
                    </div>

                    <div className="kpi-value positive">
                      {
                        projection.years_to_goal
                        !== null
                          ? (
                              `${projection
                                .years_to_goal} metų`
                            )
                          : 'Už prognozės ribų'
                      }
                    </div>

                    <div className="kpi-subvalue">
                      {
                        projection
                          .projected_age_at_goal
                        !== null
                          ? (
                              `${projection
                                .projected_age_at_goal} metų amžiaus`
                            )
                          : (
                              'Tikslas nepasiekiamas '
                              + 'per 15 metų'
                            )
                      }
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      NT nuosavas kapitalas
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .current_real_estate_equity,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Neįtraukiamas į 4 % FI kapitalą
                    </div>
                  </article>


                  <article className="kpi-card">
                    <div className="kpi-label">
                      Bendras grynasis turtas
                    </div>

                    <div className="kpi-value">
                      {
                        formatCurrency(
                          projection
                            .current_net_worth,
                          projection.currency,
                        )
                      }
                    </div>

                    <div className="kpi-subvalue">
                      Investicijos + NT equity
                    </div>
                  </article>
                </section>


                <div className="allocation-list">
                  <div className="allocation-row">
                    <div className="allocation-name">
                      FI progresas
                    </div>

                    <div className="allocation-track">
                      <div
                        className="allocation-fill"
                        style={{
                          width: (
                            `${projection
                              .progress_percent}%`
                          ),
                        }}
                      />
                    </div>

                    <div className="allocation-percentage">
                      {
                        formatPercent(
                          projection
                            .progress_percent,
                        )
                      }
                    </div>
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
                          FI kapitalas
                        </th>

                        <th className="number">
                          NT equity
                        </th>

                        <th className="number">
                          Net worth
                        </th>

                        <th className="number">
                          Pasyvios pajamos / mėn.
                        </th>

                        <th>
                          Būsena
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {
                        milestonePoints.map(
                          (
                            point,
                          ) => (
                            <tr key={point.year}>
                              <td>
                                {
                                  point.year
                                  === 0
                                    ? 'Šiandien'
                                    : `${point.year} metų`
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .investment_value,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .real_estate_equity,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point.net_worth,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td className="number">
                                {
                                  formatCurrency(
                                    point
                                      .monthly_passive_income,
                                    projection.currency,
                                  )
                                }
                              </td>

                              <td
                                className={
                                  point.target_reached
                                    ? 'positive'
                                    : ''
                                }
                              >
                                {
                                  point.target_reached
                                    ? 'FI tikslas pasiektas'
                                    : 'Kapitalas kaupiamas'
                                }
                              </td>
                            </tr>
                          ),
                        )
                      }
                    </tbody>
                  </table>
                </div>


                <p className="contribution-note">
                  FI skaičiavime 4 % išėmimo norma
                  taikoma investiciniam portfeliui.
                  NT nuosavas kapitalas rodomas kaip
                  bendro grynojo turto dalis, tačiau
                  nėra laikomas likvidžiu FI kapitalu.
                  Nuomos pajamos šiame skaičiavime
                  kol kas neįtraukiamos.
                </p>
              </>
            )
          : null
      }
    </section>
  )
}


export default FinancialIndependencePanel