import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { serviceCenterService } from '../services/api'
import ServiceCenterBookings from './ServiceCenterBookings'
import ServiceCenterOngoing from './ServiceCenterOngoing'
import ServiceCenterTechnicians from './ServiceCenterTechnicians'

const ServiceCenterDashboard = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [selectedCenterId, setSelectedCenterId] = useState(
    location.state?.centerId || localStorage.getItem('selectedServiceCenterId')
  )
  const [workloadStats, setWorkloadStats] = useState({
    scheduledToday: 0,
    inProgress: 0,
    completedToday: 0,
    technicianAvailability: 0,
    workloadDistribution: []
  })
  const [preDiagnosedCases, setPreDiagnosedCases] = useState([])
  const [reviewStats, setReviewStats] = useState({
    averageRating: 0,
    totalFeedbacks: 0,
    feedback: [],
  })
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')

  useEffect(() => {
    if (!selectedCenterId) {
      // Redirect to selection if no center selected
      navigate('/', { replace: true })
      return
    }
    
    if (activeTab === 'dashboard') {
      loadWorkloadData()
    }
  }, [selectedCenterId, activeTab])

  const loadWorkloadData = async () => {
    if (!selectedCenterId) return
    
    setLoading(true)
    try {
      const [workloadResponse, preDiagnosedResponse, feedbackResponse] = await Promise.all([
        serviceCenterService.getServiceCenterWorkload(selectedCenterId),
        serviceCenterService.getPreDiagnosedCases(selectedCenterId),
        serviceCenterService.getServiceCenterFeedback(selectedCenterId),
      ])
      
      if (workloadResponse.status === 'success') {
        setWorkloadStats({
          scheduledToday: workloadResponse.workload.scheduled_today || 0,
          inProgress: workloadResponse.workload.in_progress || 0,
          completedToday: workloadResponse.workload.completed_today || 0,
          technicianAvailability: workloadResponse.workload.available_technicians || 0,
          workloadDistribution: workloadResponse.workload.workload_distribution || []
        })
      }
      
      if (preDiagnosedResponse.status === 'success') {
        setPreDiagnosedCases(preDiagnosedResponse.pre_diagnosed_cases || [])
      }

      if (feedbackResponse.status === 'success') {
        setReviewStats({
          averageRating: feedbackResponse.average_rating || 0,
          totalFeedbacks: feedbackResponse.total_feedbacks || 0,
          feedback: feedbackResponse.feedback || [],
        })
      }
    } catch (error) {
      console.error('Error loading workload data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChangeCenter = () => {
    localStorage.removeItem('selectedServiceCenterId')
    setSelectedCenterId(null)
    navigate('/', { replace: true })
  }

  if (!selectedCenterId) {
    return null // Will redirect
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Dashboard</h1>
          <p className="text-gray-600 mt-1">Center ID: {selectedCenterId}</p>
        </div>
        <button
          onClick={handleChangeCenter}
          className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
        >
          Change Service Center
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                activeTab === 'dashboard'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('bookings')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                activeTab === 'bookings'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Bookings
            </button>
            <button
              onClick={() => setActiveTab('ongoing')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                activeTab === 'ongoing'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Ongoing Bookings
            </button>
            <button
              onClick={() => setActiveTab('technicians')}
              className={`px-6 py-4 text-sm font-medium border-b-2 ${
                activeTab === 'technicians'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Technicians
            </button>
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && (
        <>
          {/* Daily Workload Dashboard */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Scheduled Today</p>
              <p className="text-3xl font-semibold text-gray-900">{workloadStats.scheduledToday}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">In Progress</p>
              <p className="text-3xl font-semibold text-blue-600">{workloadStats.inProgress}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Completed Today</p>
              <p className="text-3xl font-semibold text-green-600">{workloadStats.completedToday}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Available Technicians</p>
              <p className="text-3xl font-semibold text-gray-900">{workloadStats.technicianAvailability}</p>
            </div>
          </div>

          {/* Workload Distribution */}
          {workloadStats.workloadDistribution && workloadStats.workloadDistribution.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Workload Distribution</h2>
              <div className="space-y-3">
                {workloadStats.workloadDistribution.map((tech) => (
                  <div key={tech.technician_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <div>
                        <p className="font-medium text-gray-900">{tech.technician_name || tech.technician_id}</p>
                        <p className="text-sm text-gray-500">
                          {tech.current_assignments} / {tech.max_capacity} assignments
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-700">{tech.utilization_percent}% utilized</p>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          tech.status === 'available' ? 'bg-green-100 text-green-800' :
                          tech.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {tech.status}
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          tech.utilization_percent < 50 ? 'bg-green-500' :
                          tech.utilization_percent < 80 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(tech.utilization_percent, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alerts / Priority Jobs - High-Risk Vehicles Arriving Today */}
          {preDiagnosedCases.filter(c => {
            const scheduledDate = new Date(c.scheduled_date)
            const today = new Date()
            return scheduledDate.toDateString() === today.toDateString() && 
                   (c.health_score < 50 || c.risk_score > 0.65)
          }).length > 0 && (
            <div className="bg-white rounded-lg shadow border-2 border-red-300">
              <div className="p-6 border-b bg-red-50">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <span className="mr-2 text-2xl">🚨</span>
                  Priority Jobs - High-Risk Vehicles Arriving Today
                </h2>
                <p className="text-sm text-gray-600 mt-1">Critical cases requiring immediate attention</p>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  {preDiagnosedCases
                    .filter(c => {
                      const scheduledDate = new Date(c.scheduled_date)
                      const today = new Date()
                      return scheduledDate.toDateString() === today.toDateString() && 
                             (c.health_score < 50 || c.risk_score > 0.65)
                    })
                    .map((case_item) => (
                      <div key={case_item.appointment_id} className="border-2 border-red-300 rounded-lg p-4 bg-red-50">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-bold text-red-900">
                              {case_item.vehicle_name || case_item.vin}
                              {case_item.plate_number && (
                                <span className="text-red-700 ml-2">({case_item.plate_number})</span>
                              )}
                            </p>
                            <p className="text-sm text-red-700 mt-1">
                              Scheduled: {new Date(case_item.scheduled_date).toLocaleString()}
                            </p>
                            <p className="text-sm font-medium text-red-900 mt-2">
                              {case_item.predicted_issue || 'Critical issue detected'}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="px-3 py-1 bg-red-600 text-white text-xs rounded-full font-bold">
                              CRITICAL
                            </span>
                            <p className="text-xs text-red-700 mt-2">
                              Health: {case_item.health_score?.toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* Pre-Diagnosed Service Cases */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b bg-blue-50">
              <h2 className="text-xl font-semibold text-gray-900">Pre-Diagnosed Service Cases</h2>
              <p className="text-sm text-gray-600 mt-1">Predicted issues before vehicles arrive - helps technicians prepare tools & parts</p>
            </div>
            <div className="p-6">
              {preDiagnosedCases.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No upcoming appointments with pre-diagnosed cases
                </div>
              ) : (
                <div className="space-y-4">
                  {preDiagnosedCases.slice(0, 10).map((case_item) => (
                    <div key={case_item.appointment_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-semibold text-gray-900">
                            {case_item.vehicle_name || case_item.vin}
                            {case_item.plate_number && (
                              <span className="text-gray-500 ml-2">({case_item.plate_number})</span>
                            )}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            Scheduled: {new Date(case_item.scheduled_date).toLocaleString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            case_item.health_score < 50 ? 'bg-red-100 text-red-800' :
                            case_item.health_score < 70 ? 'bg-orange-100 text-orange-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            Health: {case_item.health_score?.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Predicted Issue:</p>
                        <p className="text-sm text-gray-900 bg-yellow-50 p-2 rounded">
                          {case_item.predicted_issue || 'General maintenance required'}
                        </p>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">Recommended Tools:</p>
                          <div className="flex flex-wrap gap-1">
                            {case_item.recommended_tools?.map((tool, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                {tool}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">Recommended Parts:</p>
                          <div className="flex flex-wrap gap-1">
                            {case_item.recommended_parts?.map((part, idx) => (
                              <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                {part}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      {case_item.technician_name && (
                        <p className="text-xs text-gray-600">
                          Assigned Technician: <span className="font-medium">{case_item.technician_name}</span>
                          {case_item.technician_specialization && case_item.technician_specialization.length > 0 && (
                            <span className="text-gray-500 ml-2">
                              ({case_item.technician_specialization.join(', ')})
                            </span>
                          )}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setActiveTab('bookings')}
                className="bg-primary-50 border-2 border-primary-200 rounded-lg p-4 text-left hover:bg-primary-100 transition-colors"
              >
                <h3 className="font-semibold text-gray-900 mb-1">View All Bookings</h3>
                <p className="text-sm text-gray-600">See all scheduled appointments</p>
              </button>
              <button
                onClick={() => setActiveTab('ongoing')}
                className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 text-left hover:bg-yellow-100 transition-colors"
              >
                <h3 className="font-semibold text-gray-900 mb-1">Manage Ongoing Services</h3>
                <p className="text-sm text-gray-600">Update service status</p>
              </button>
              <button
                onClick={() => setActiveTab('technicians')}
                className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 text-left hover:bg-blue-100 transition-colors"
              >
                <h3 className="font-semibold text-gray-900 mb-1">View Technicians</h3>
                <p className="text-sm text-gray-600">See technician details and availability</p>
              </button>
            </div>
          </div>
        </>
      )}

      {activeTab === 'bookings' && (
        <ServiceCenterBookings />
      )}

      {activeTab === 'ongoing' && (
        <ServiceCenterOngoing />
      )}

      {activeTab === 'technicians' && (
        <ServiceCenterTechnicians />
      )}
    </div>
  )
}

export default ServiceCenterDashboard
