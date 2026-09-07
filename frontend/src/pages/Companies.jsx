import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

import {
  hasPermission,
} from '../utils/permissions'

import CompanyFormModal from '../components/CompanyFormModal'

import {
  createCompany,
  deleteCompany,
  getCompanies,
  updateCompany,
} from '../services/api'


function Companies({
  user,
}) {
  const { t } = useTranslation()

  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState(null)

  const [deletingCompanyId, setDeletingCompanyId] =
    useState(null)


  useEffect(() => {
    async function loadCompanies() {
      try {
        const data = await getCompanies()
        setCompanies(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadCompanies()
  }, [])


  function handleOpenCreateModal() {
    setSelectedCompany(null)
    setIsModalOpen(true)
  }


  function handleOpenEditModal(company) {
    setSelectedCompany(company)
    setIsModalOpen(true)
  }


  function handleCloseModal() {
    setIsModalOpen(false)
    setSelectedCompany(null)
  }


  async function handleSubmitCompany(formData) {
    if (selectedCompany) {
      const updatedCompany = await updateCompany(
        selectedCompany.id,
        formData
      )

      setCompanies((currentCompanies) =>
        currentCompanies.map((company) =>
          company.id === updatedCompany.id
            ? updatedCompany
            : company
        )
      )
    } else {
      const newCompany = await createCompany(formData)

      setCompanies((currentCompanies) => [
        ...currentCompanies,
        newCompany,
      ])
    }

    handleCloseModal()
  }


  async function handleDeleteCompany(company) {
    const confirmed = window.confirm(
      t(
        'companies.deleteConfirmation',
        {
          name: company.name,
        }
      )
    )

    if (!confirmed) {
      return
    }

    try {
      setDeletingCompanyId(company.id)

      await deleteCompany(company.id)

      setCompanies((currentCompanies) =>
        currentCompanies.filter(
          (item) => item.id !== company.id
        )
      )
    } catch (err) {
      window.alert(err.message)
    } finally {
      setDeletingCompanyId(null)
    }
  }


  if (loading) {
    return (
      <div className="companies-page">
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>
            {t('companies.loadingTitle')}
          </h2>

          <p>
            {t('companies.loadingDescription')}
          </p>
        </div>
      </div>
    )
  }


  if (error) {
    return (
      <div className="companies-page">
        <div className="page-state page-state--error">
          <div className="error-icon">
            !
          </div>

          <h2>
            {t('companies.loadError')}
          </h2>

          <p>
            {error}
          </p>
        </div>
      </div>
    )
  }


  const canEditCompany = hasPermission(
    user,
    'companies.change_company'
  )

  const canDeleteCompany = hasPermission(
    user,
    'companies.delete_company'
  )

  const canManageCompanies =
    canEditCompany || canDeleteCompany


  return (
    <div className="companies-page">
      <header className="companies-header">
        <div>
          <h1>
            {t('companies.title')}
          </h1>

          <p>
            {t('companies.description')}
          </p>
        </div>

        {hasPermission(
          user,
          'companies.add_company'
        ) && (
          <button
            type="button"
            className="primary-button"
            onClick={handleOpenCreateModal}
          >
            {t('companies.addCompany')}
          </button>
        )}
      </header>


      {companies.length === 0 ? (
        <div className="empty-state">
          {t('companies.empty')}
        </div>
      ) : (
        <div className="companies-table-wrapper">
          <table className="companies-table">
            <thead>
              <tr>
                <th>
                  {t('companies.company')}
                </th>

                <th>
                  {t('companies.nationalId')}
                </th>

                <th>
                  {t('companies.companyType')}
                </th>

                {canManageCompanies && (
                  <th>
                    {t('companies.actions')}
                  </th>
                )}
              </tr>
            </thead>

            <tbody>
              {companies.map((company) => (
                <tr key={company.id}>
                  <td>
                    {company.name}
                  </td>

                  <td>
                    {company.national_id}
                  </td>

                  <td>
                    <span className="company-type-badge">
                      {
                        company.company_type === 'PRODUCTION'
                          ? t('companies.production')
                          : t('companies.commercial')
                      }
                    </span>
                  </td>

                  {canManageCompanies && (
                    <td>
                      <div className="table-actions">
                        {canEditCompany && (
                          <button
                            type="button"
                            className="table-action-button"
                            onClick={() =>
                              handleOpenEditModal(company)
                            }
                          >
                            {t('common.edit')}
                          </button>
                        )}

                        {canDeleteCompany && (
                          <button
                            type="button"
                            className="table-action-button table-action-button--danger"
                            onClick={() =>
                              handleDeleteCompany(company)
                            }
                            disabled={
                              deletingCompanyId === company.id
                            }
                          >
                            {
                              deletingCompanyId === company.id
                                ? t('companies.deleting')
                                : t('common.delete')
                            }
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}


      {isModalOpen && (
        <CompanyFormModal
          company={selectedCompany}
          onClose={handleCloseModal}
          onSubmit={handleSubmitCompany}
        />
      )}
    </div>
  )
}


export default Companies