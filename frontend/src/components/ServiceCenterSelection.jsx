import React, { useState, useEffect } from 'react'
import { serviceCenterService } from '../services/api'

const ServiceCenterSelection = ({ onSelect, selectedCenterId }) => {
  const [serviceCenters, setServiceCenters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

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
        // Auto-select first center if none selected
        if (!selectedCenterId && response.service_centers && response.service_centers.length > 0) {
          onSelect(response.service_centers[0].center_id)
        }
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

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading service centers...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    )
  }

  if (serviceCenters.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">No service centers available.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Service Center</h2>
      <div className="space-y-3">
        {serviceCenters.map((center) => (
          <div
            key={center.center_id}
            onClick={() => onSelect(center.center_id)}
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
              selectedCenterId === center.center_id
                ? 'border-primary-600 bg-primary-50'
                : 'border-gray-200 hover:border-primary-300'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{center.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{center.address}</p>
                <p className="text-sm text-gray-500 mt-1">Phone: {center.phone}</p>
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
              <div className="mt-2 pt-2 border-t border-primary-200">
                <p className="text-sm text-primary-700">✓ Selected</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ServiceCenterSelection

