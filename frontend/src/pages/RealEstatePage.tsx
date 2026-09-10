import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'

import {
  getRealEstateProperties,
  getRealEstateSummary,
  updateRealEstateProperty,
} from '../api/realEstate'
import RealEstateProjectionPanel from '../components/RealEstateProjectionPanel'
import type {
  RealEstateProperty,
  RealEstateSummary,
} from '../types/realEstate'


interface EditFormState {
  current_value: string
  loan_balance: string
  interest_rate: string
  monthly_payment: string
  monthly_rent: string
  monthly_expenses: string
}


interface MetricCardProps {
  label: string
  value: string
  subvalue: string
  valueClass?: string
}


const emptyEditForm: EditFormState = {
  current_value: '',
  loan_balance: '',
  interest_rate: '',
  monthly_payment: '',
  monthly_rent: '',
  monthly_expenses: '',
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


function getValueClass(
  value: number,
) {
  if (value > 0) {
    return 'positive'
  }

  if (value < 0) {
    return 'negative'
  }

  return ''
}


function MetricCard({
  label,
  value,
  subvalue,
  valueClass = '',
}: MetricCardProps) {
  return (
    <article className="kpi-card">
      <div className="kpi-label">
        {label}
      </div>

      <div
        className={
          `kpi-value ${valueClass}`
        }
      >
        {value}
      </div>

      <div className="kpi-subvalue">
        {subvalue}
      </div>
    </article>
  )
}


function RealEstatePage() {
  const [
    properties,
    setProperties,
  ] = useState<
    RealEstateProperty[]
  >([])

  const [
    summary,
    setSummary,
  ] = useState<
    RealEstateSummary | null
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

  const [
    editingPropertyId,
    setEditingPropertyId,
  ] = useState<
    number | null
  >(null)

  const [
    editForm,
    setEditForm,
  ] = useState<EditFormState>(
    emptyEditForm,
  )

  const [
    saving,
    setSaving,
  ] = useState(false)

  const [
    actionError,
    setActionError,
  ] = useState<
    string | null
  >(null)


  const loadRealEstate = useCallback(
    async () => {
      const [
        propertyData,
        summaryData,
      ] = await Promise.all([
        getRealEstateProperties(),
        getRealEstateSummary(),
      ])

      setProperties(
        propertyData,
      )

      setSummary(
        summaryData,
      )
    },
    [],
  )


  useEffect(() => {
    async function loadPage() {
      try {
        await loadRealEstate()
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(
            error.message,
          )
        } else {
          setError(
            'Failed to load real estate.',
          )
        }
      } finally {
        setLoading(false)
      }
    }

    loadPage()
  }, [loadRealEstate])


  function startEditing(
    property: RealEstateProperty,
  ) {
    setEditingPropertyId(
      property.id,
    )

    setEditForm({
      current_value: String(
        property.current_value,
      ),
      loan_balance: String(
        property.loan_balance,
      ),
      interest_rate: (
        property.interest_rate
        !== null
          ? String(
              property.interest_rate,
            )
          : ''
      ),
      monthly_payment: String(
        property.monthly_payment,
      ),
      monthly_rent: String(
        property.monthly_rent,
      ),
      monthly_expenses: String(
        property.monthly_expenses,
      ),
    })

    setActionError(null)
  }


  function cancelEditing() {
    setEditingPropertyId(null)

    setEditForm(
      emptyEditForm,
    )

    setActionError(null)
  }


  function updateFormField(
    field: keyof EditFormState,
    value: string,
  ) {
    setEditForm(
      (
        currentForm,
      ) => ({
        ...currentForm,
        [field]: value,
      }),
    )
  }


  async function saveProperty(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (
      editingPropertyId === null
    ) {
      return
    }

    const currentValue = Number(
      editForm.current_value,
    )

    const loanBalance = Number(
      editForm.loan_balance,
    )

    const monthlyPayment = Number(
      editForm.monthly_payment,
    )

    const monthlyRent = Number(
      editForm.monthly_rent,
    )

    const monthlyExpenses = Number(
      editForm.monthly_expenses,
    )

    const interestRate = (
      editForm.interest_rate.trim()
        ? Number(
            editForm.interest_rate,
          )
        : null
    )

    const numericValues = [
      currentValue,
      loanBalance,
      monthlyPayment,
      monthlyRent,
      monthlyExpenses,
    ]

    if (
      numericValues.some(
        (
          value,
        ) => (
          !Number.isFinite(value)
          || value < 0
        ),
      )
      || (
        interestRate !== null
        && (
          !Number.isFinite(
            interestRate,
          )
          || interestRate < 0
        )
      )
    ) {
      setActionError(
        'Enter valid non-negative numbers.',
      )

      return
    }

    setSaving(true)
    setActionError(null)

    try {
      await updateRealEstateProperty(
        editingPropertyId,
        {
          current_value: currentValue,
          loan_balance: loanBalance,
          interest_rate: interestRate,
          monthly_payment: monthlyPayment,
          monthly_rent: monthlyRent,
          monthly_expenses: monthlyExpenses,
        },
      )

      await loadRealEstate()

      cancelEditing()
    } catch (error) {
      if (
        error instanceof Error
      ) {
        setActionError(
          error.message,
        )
      } else {
        setActionError(
          'Failed to update property.',
        )
      }
    } finally {
      setSaving(false)
    }
  }


  if (loading) {
    return (
      <div className="loading-state">
        <h1>
          Real estate
        </h1>

        <p>
          Loading real estate...
        </p>
      </div>
    )
  }


  if (
    error !== null
    || summary === null
  ) {
    return (
      <div className="error-state">
        <h1>
          Real estate
        </h1>

        <p>
          {
            error
            ?? 'No real estate data available.'
          }
        </p>
      </div>
    )
  }


  return (
    <main>
      <section className="dashboard-heading">
        <div>
          <h1>
            Real estate
          </h1>

          <p>
            Property, mortgage and
            rental overview
          </p>
        </div>

        <div className="base-currency-badge">
          Base currency:{' '}
          {summary.currency}
        </div>
      </section>


      <section className="kpi-grid">
        <MetricCard
          label="Property value"
          value={
            formatCurrency(
              summary.total_current_value,
              summary.currency,
            )
          }
          subvalue={
            `${summary.properties_count} properties`
          }
        />

        <MetricCard
          label="Mortgage balance"
          value={
            formatCurrency(
              summary.total_loan_balance,
              summary.currency,
            )
          }
          subvalue="Outstanding debt"
        />

        <MetricCard
          label="Property equity"
          value={
            formatCurrency(
              summary.total_equity,
              summary.currency,
            )
          }
          subvalue="Value minus mortgage"
          valueClass={
            getValueClass(
              summary.total_equity,
            )
          }
        />

        <MetricCard
          label="Monthly rent"
          value={
            formatCurrency(
              summary.total_monthly_rent,
              summary.currency,
            )
          }
          subvalue="Gross rental income"
        />

        <MetricCard
          label="Monthly cash flow"
          value={
            formatCurrency(
              summary
                .total_monthly_cash_flow,
              summary.currency,
            )
          }
          subvalue="After mortgage and expenses"
          valueClass={
            getValueClass(
              summary
                .total_monthly_cash_flow,
            )
          }
        />

        <MetricCard
          label="Annual cash flow"
          value={
            formatCurrency(
              summary
                .total_annual_cash_flow,
              summary.currency,
            )
          }
          subvalue="Net cash flow per year"
          valueClass={
            getValueClass(
              summary
                .total_annual_cash_flow,
            )
          }
        />
      </section>


      {
        properties.length === 0
          ? (
              <section className="panel">
                <div className="empty-state">
                  <h3>
                    No properties
                  </h3>

                  <p>
                    Add your first real
                    estate property.
                  </p>
                </div>
              </section>
            )
          : properties.map(
              (
                property,
              ) => (
                <section
                  className="panel"
                  key={property.id}
                >
                  <div className="panel-header">
                    <div>
                      <h3 className="panel-title">
                        {property.name}
                      </h3>

                      <p className="panel-subtitle">
                        {
                          property.address
                          ?? property.property_type
                        }
                      </p>
                    </div>

                    <div className="target-actions">
                      <span className="base-currency-badge">
                        {property.currency}
                      </span>

                      {
                        editingPropertyId
                        !== property.id
                          ? (
                              <button
                                className="target-secondary-button"
                                type="button"
                                onClick={
                                  () => (
                                    startEditing(
                                      property,
                                    )
                                  )
                                }
                              >
                                Edit property
                              </button>
                            )
                          : null
                      }
                    </div>
                  </div>


                  {
                    editingPropertyId
                    === property.id
                      ? (
                          <form
                            className="target-form"
                            onSubmit={
                              saveProperty
                            }
                          >
                            <label>
                              Current value
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                required
                                value={
                                  editForm
                                    .current_value
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'current_value',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <label>
                              Mortgage balance
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                required
                                value={
                                  editForm
                                    .loan_balance
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'loan_balance',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <label>
                              Interest rate (%)
                              <input
                                type="number"
                                min="0"
                                step="0.001"
                                value={
                                  editForm
                                    .interest_rate
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'interest_rate',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <label>
                              Monthly payment
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                required
                                value={
                                  editForm
                                    .monthly_payment
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'monthly_payment',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <label>
                              Monthly rent
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                required
                                value={
                                  editForm
                                    .monthly_rent
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'monthly_rent',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <label>
                              Monthly expenses
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                required
                                value={
                                  editForm
                                    .monthly_expenses
                                }
                                onChange={
                                  (
                                    event,
                                  ) => (
                                    updateFormField(
                                      'monthly_expenses',
                                      event.target.value,
                                    )
                                  )
                                }
                              />
                            </label>

                            <div className="target-actions">
                              <button
                                className="target-secondary-button"
                                type="button"
                                disabled={saving}
                                onClick={
                                  cancelEditing
                                }
                              >
                                Cancel
                              </button>

                              <button
                                className="target-primary-button"
                                type="submit"
                                disabled={saving}
                              >
                                {
                                  saving
                                    ? 'Saving...'
                                    : 'Save changes'
                                }
                              </button>
                            </div>

                            {
                              actionError
                                ? (
                                    <p className="negative">
                                      {actionError}
                                    </p>
                                  )
                                : null
                            }
                          </form>
                        )
                      : null
                  }


                  <section className="kpi-grid">
                    <MetricCard
                      label="Current value"
                      value={
                        formatCurrency(
                          property.current_value,
                          property.currency,
                        )
                      }
                      subvalue={
                        (
                          'Purchase price: '
                          + formatCurrency(
                            property.purchase_price,
                            property.currency,
                          )
                        )
                      }
                    />

                    <MetricCard
                      label="Equity"
                      value={
                        formatCurrency(
                          property.equity,
                          property.currency,
                        )
                      }
                      subvalue={
                        (
                          'Down payment: '
                          + formatCurrency(
                            property.down_payment,
                            property.currency,
                          )
                        )
                      }
                      valueClass={
                        getValueClass(
                          property.equity,
                        )
                      }
                    />

                    <MetricCard
                      label="Mortgage"
                      value={
                        formatCurrency(
                          property.loan_balance,
                          property.currency,
                        )
                      }
                      subvalue={
                        (
                          'LTV: '
                          + formatPercent(
                            property.loan_to_value,
                          )
                        )
                      }
                    />

                    <MetricCard
                      label="Interest rate"
                      value={
                        property.interest_rate
                        !== null
                          ? formatPercent(
                              property.interest_rate,
                            )
                          : '\u2014'
                      }
                      subvalue={
                        (
                          'Monthly payment: '
                          + formatCurrency(
                            property.monthly_payment,
                            property.currency,
                          )
                        )
                      }
                    />

                    <MetricCard
                      label="Gross yield"
                      value={
                        formatPercent(
                          property
                            .gross_rental_yield,
                        )
                      }
                      subvalue={
                        (
                          'Annual rent divided '
                          + 'by value'
                        )
                      }
                    />

                    <MetricCard
                      label="Net yield"
                      value={
                        formatPercent(
                          property
                            .net_rental_yield,
                        )
                      }
                      subvalue={
                        'After property expenses'
                      }
                    />
                  </section>


                  <div className="table-scroll">
                    <table className="positions-table">
                      <thead>
                        <tr>
                          <th>
                            Metric
                          </th>

                          <th className="number">
                            Monthly
                          </th>

                          <th className="number">
                            Annual
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        <tr>
                          <td>
                            Rental income
                          </td>

                          <td className="number positive">
                            {
                              formatCurrency(
                                property.monthly_rent,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number positive">
                            {
                              formatCurrency(
                                property.annual_rent,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Mortgage payments
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .monthly_payment,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .annual_loan_payments,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Property expenses
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .monthly_expenses,
                                property.currency,
                              )
                            }
                          </td>

                          <td className="number negative">
                            {
                              formatCurrency(
                                -property
                                  .annual_expenses,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>

                        <tr>
                          <td>
                            Net cash flow
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  property
                                    .monthly_cash_flow,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                property
                                  .monthly_cash_flow,
                                property.currency,
                              )
                            }
                          </td>

                          <td
                            className={
                              `number ${
                                getValueClass(
                                  property
                                    .annual_cash_flow,
                                )
                              }`
                            }
                          >
                            {
                              formatCurrency(
                                property
                                  .annual_cash_flow,
                                property.currency,
                              )
                            }
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </section>
              ),
            )
      }
            {
        properties.map(
          (
            property,
          ) => (
            <RealEstateProjectionPanel
              key={
                `projection-${property.id}`
              }
              propertyId={property.id}
              propertyName={property.name}
              currency={property.currency}
            />
          ),
        )
      }
    </main>
  )
}


export default RealEstatePage