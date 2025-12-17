import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { serviceCenterService } from '../services/api'

const ServiceCenterTechnicians = () => {
  const location = useLocation()
  const centerId = location.state?.centerId || localStorage.getItem('selectedServiceCenterId')
  const [technicians, setTechnicians] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedTechnician, setSelectedTechnician] = useState(null)
  const [technicianHistory, setTechnicianHistory] = useState([])

  useEffect(() => {
    if (centerId) {
      loadTechnicians()
    }
  }, [centerId])

  const loadTechnicians = async () => {
    setLoading(true)
    try {
      const response = await serviceCenterService.getServiceCenterTechnicians(centerId)
      if (response.status === 'success') {
        setTechnicians(response.technicians || [])
      }
    } catch (error) {
      console.error('Error loading technicians:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!centerId) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please select a service center first</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Technician Details</h1>
          <p className="text-gray-600 dark:text-slate-300 mt-1">Center ID: {centerId}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600 dark:text-slate-300">
            Total: {technicians.length} | Available: {technicians.filter(t => t.status === 'available' && t.current_assignments < t.max_capacity).length}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading technicians...</p>
        </div>
      ) : technicians.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">No technicians found for this service center.</p>
        </div>
      ) : selectedTechnician ? (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">{selectedTechnician.name}</h2>
              <p className="text-sm text-gray-600 mt-1">ID: {selectedTechnician.technician_id}</p>
            </div>
            <button
              onClick={() => setSelectedTechnician(null)}
              className="text-gray-600 hover:text-gray-900 px-4 py-2 border rounded-lg"
            >
              ← Back to List
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Basic Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Age:</span>
                  <span className="font-medium">{selectedTechnician.age || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Contact:</span>
                  <span className="font-medium">{selectedTechnician.contact_number || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    selectedTechnician.status === 'available' ? 'bg-green-100 text-green-800' :
                    selectedTechnician.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {selectedTechnician.status}
                  </span>
                </div>
              </div>
            </div>

            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Performance Metrics</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Vehicles Repaired (Last Month):</span>
                  <span className="font-medium text-green-600">{selectedTechnician.vehicles_repaired_last_month || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Current Load:</span>
                  <span className="font-medium">{selectedTechnician.current_assignments} / {selectedTechnician.max_capacity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Utilization:</span>
                  <span className="font-medium">
                    {Math.round((selectedTechnician.current_assignments / selectedTechnician.max_capacity) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {selectedTechnician.specialization && selectedTechnician.specialization.length > 0 && (
            <div className="border rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Expertise Areas</h3>
              <div className="flex flex-wrap gap-2">
                {selectedTechnician.specialization.map((spec, idx) => (
                  <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {spec}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Past Jobs (Last 30 Days)</h3>
            {technicianHistory.length === 0 ? (
              <p className="text-sm text-gray-500">No completed jobs in the last 30 days</p>
            ) : (
              <div className="space-y-2">
                {technicianHistory.map((job, idx) => (
                  <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded text-sm">
                    <div>
                      <p className="font-medium text-gray-900">{job.vehicle_name || job.vin}</p>
                      <p className="text-xs text-gray-600">{new Date(job.completed_date).toLocaleDateString()}</p>
                    </div>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Completed</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {technicians.map((tech) => (
            <div 
              key={tech.technician_id} 
              className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedTechnician(tech)}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{tech.name}</h3>
                  <p className="text-sm text-gray-600">ID: {tech.technician_id}</p>
                </div>
                <span className={`px-3 py-1 text-xs rounded-full ${
                  tech.status === 'available' ? 'bg-green-100 text-green-800' :
                  tech.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {tech.status}
                </span>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Age:</span>
                  <span className="font-medium text-gray-900">{tech.age || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Contact Number:</span>
                  <span className="font-medium text-gray-900">{tech.contact_number || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Vehicles Repaired (Last Month):</span>
                  <span className="font-medium text-green-600">{tech.vehicles_repaired_last_month || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Current Load:</span>
                  <span className="font-medium">{tech.current_assignments} / {tech.max_capacity}</span>
                </div>
              </div>
              
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      tech.current_assignments >= tech.max_capacity ? 'bg-red-600' :
                      tech.current_assignments > tech.max_capacity * 0.7 ? 'bg-yellow-600' :
                      'bg-green-600'
                    }`}
                    style={{ width: `${Math.min(100, (tech.current_assignments / tech.max_capacity) * 100)}%` }}
                  ></div>
                </div>
              </div>
              
              {tech.specialization && tech.specialization.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-medium text-gray-700 mb-2">Specializations:</p>
                  <div className="flex flex-wrap gap-2">
                    {tech.specialization.map((spec, idx) => (
                      <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {spec}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ServiceCenterTechnicians

