import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { serviceCenterService } from '../services/api'

const ServiceCenterSelection = () => {
  const [serviceCenters, setServiceCenters] = useState([])
  const [selectedCenterId, setSelectedCenterId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadServiceCenters()
  }, [])

  const loadServiceCenters = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await serviceCenterService.getServiceCenters()
      if (response.status === 'success') {
        setServiceCenters(response.service_centers || [])
      } else {
        setError('Failed to load service centers')
      }
    } catch (err) {
      console.error('Error loading service centers:', err)
      setError('Failed to load service centers. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (centerId) => {
    setSelectedCenterId(centerId)
  }

  const handleContinue = () => {
    if (selectedCenterId) {
      // Store selected center in localStorage (for current session only)
      localStorage.setItem('selectedServiceCenterId', selectedCenterId)
      // Navigate to service center dashboard (not main dashboard)
      navigate('/service-center', { state: { centerId: selectedCenterId }, replace: true })
    } else {
      setError('Please select a service center')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading service centers...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50 mb-2">Select Service Center</h1>
          <p className="text-gray-600 dark:text-slate-300">Please select the service center you want to manage</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {serviceCenters.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600">No service centers available.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {serviceCenters.map((center) => (
                <div
                  key={center.center_id}
                  onClick={() => handleSelect(center.center_id)}
                  className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${
                    selectedCenterId === center.center_id
                      ? 'border-primary-600 bg-primary-50 shadow-lg'
                      : 'border-gray-200 hover:border-primary-300 bg-white dark:bg-slate-900'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-2">{center.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-slate-300 mb-1">{center.address}</p>
                      <p className="text-sm text-gray-500 dark:text-slate-400">Phone: {center.phone}</p>
                      <p className="text-sm text-gray-500">Email: {center.email}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                        (center.capacity - center.current_load) > 5
                          ? 'bg-green-100 text-green-800'
                          : (center.capacity - center.current_load) > 2
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {center.capacity - center.current_load} slots available
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Capacity: {center.capacity}</p>
                    </div>
                  </div>
                  {selectedCenterId === center.center_id && (
                    <div className="mt-4 pt-4 border-t border-primary-200">
                      <p className="text-sm text-primary-700 font-medium">✓ Selected</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="text-center">
              <button
                onClick={handleContinue}
                disabled={!selectedCenterId}
                className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-lg font-semibold"
              >
                Continue to Dashboard
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default ServiceCenterSelection

