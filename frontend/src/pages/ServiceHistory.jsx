import React, { useState, useEffect } from 'react'
import { schedulingService, vehicleService } from '../services/api'
import { useAuth } from '../services/AuthContext'

const ServiceHistory = () => {
  const { user } = useAuth()
  const [serviceHistory, setServiceHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const rawCustomerId = user?.customer_id || user?.username || 'CUST_001'
  const customerId = rawCustomerId === 'customer' ? 'CUST_001' : rawCustomerId

  useEffect(() => {
    loadServiceHistory()
  }, [])

  const loadServiceHistory = async () => {
    setLoading(true)
    try {
      // Get all appointments (including completed ones)
      const appointmentsResponse = await schedulingService.getAppointments(customerId)
      const allAppointments = appointmentsResponse.appointments || []
      
      // Filter to only completed appointments and sort by date (newest first)
      const completedServices = allAppointments
        .filter(apt => apt.status === 'completed')
        .sort((a, b) => new Date(b.updated_at || b.scheduled_date) - new Date(a.updated_at || a.scheduled_date))
      
      // Get vehicle info for each service
      const servicesWithDetails = await Promise.all(
        completedServices.map(async (apt) => {
          try {
            const vehicleResponse = await vehicleService.getVehicle(apt.vin)
            return {
              ...apt,
              vehicle_name: vehicleResponse.vehicle?.vehicle_name || vehicleResponse.vehicle?.model || apt.vin,
              plate_number: vehicleResponse.vehicle?.plate_number || ''
            }
          } catch (error) {
            return {
              ...apt,
              vehicle_name: apt.vin,
              plate_number: ''
            }
          }
        })
      )
      
      setServiceHistory(servicesWithDetails)
    } catch (error) {
      console.error('Error loading service history:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Service History</h1>
        <button
          onClick={loadServiceHistory}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading service history...</p>
        </div>
      ) : serviceHistory.length === 0 ? (
        <div className="enhanced-card p-12 text-center">
          <svg className="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-gray-600 dark:text-slate-400 font-medium">No service history available.</p>
          <p className="text-sm text-gray-500 dark:text-slate-500 mt-2">Completed services will appear here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {serviceHistory.map((service) => (
            <div key={service.appointment_id} className="enhanced-card p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-slate-50 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    {service.vehicle_name}
                    {service.plate_number && (
                      <span className="text-gray-500 dark:text-slate-400 ml-2 font-normal">({service.plate_number})</span>
                    )}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-slate-400 mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Service Date: {new Date(service.updated_at || service.scheduled_date).toLocaleDateString()}
                  </p>
                </div>
                <span className="px-3 py-1 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/40 dark:to-emerald-900/40 text-green-800 dark:text-green-300 text-sm rounded-full font-semibold border border-green-200 dark:border-green-800">
                  ✓ Completed
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 dark:bg-slate-800/50 p-3 rounded-lg">
                  <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-1">Appointment ID</p>
                  <p className="text-sm font-mono text-gray-900 dark:text-slate-100">{service.appointment_id}</p>
                </div>
                <div className="bg-gray-50 dark:bg-slate-800/50 p-3 rounded-lg">
                  <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-1">Service Type</p>
                  <p className="text-sm text-gray-900 dark:text-slate-100 capitalize font-medium">{service.service_type || 'General'}</p>
                </div>
                {service.service_center_id && (
                  <div className="bg-gray-50 dark:bg-slate-800/50 p-3 rounded-lg">
                    <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-1">Service Center</p>
                    <p className="text-sm text-gray-900 dark:text-slate-100 font-medium">{service.service_center_id}</p>
                  </div>
                )}
                {service.technician_id && (
                  <div className="bg-gray-50 dark:bg-slate-800/50 p-3 rounded-lg">
                    <p className="text-xs font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider mb-1">Technician</p>
                    <p className="text-sm text-gray-900 dark:text-slate-100 font-medium">{service.technician_id}</p>
                  </div>
                )}
              </div>

              {service.description && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-medium text-gray-700 mb-2">Service Description</p>
                  <p className="text-sm text-gray-600">{service.description}</p>
                </div>
              )}

              {service.predicted_issue && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-sm font-medium text-gray-700 mb-2">Issue Resolved</p>
                  <p className="text-sm text-gray-600">{service.predicted_issue}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ServiceHistory

