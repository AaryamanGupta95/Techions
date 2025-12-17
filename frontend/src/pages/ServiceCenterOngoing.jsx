import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { serviceCenterService } from '../services/api'

const ServiceCenterOngoing = () => {
  const location = useLocation()
  const centerId = location.state?.centerId || localStorage.getItem('selectedServiceCenterId')
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (centerId) {
      loadOngoingBookings()
    }
  }, [centerId])

  const loadOngoingBookings = async () => {
    setLoading(true)
    try {
      // Get both ongoing bookings and scheduled appointments that can be started
      const [ongoingResponse, bookingsResponse] = await Promise.all([
        serviceCenterService.getOngoingBookings(centerId),
        serviceCenterService.getServiceCenterAppointments(centerId)
      ])
      
      // Combine in_progress, completed, and scheduled appointments
      const ongoing = ongoingResponse.status === 'success' ? ongoingResponse.appointments || [] : []
      const scheduled = bookingsResponse.status === 'success' 
        ? (bookingsResponse.appointments || []).filter(apt => apt.status === 'scheduled')
        : []
      
      // Combine and sort by date
      const allAppointments = [...ongoing, ...scheduled].sort((a, b) => {
        return new Date(a.scheduled_date) - new Date(b.scheduled_date)
      })
      
      setAppointments(allAppointments)
    } catch (error) {
      console.error('Error loading ongoing bookings:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateServiceStatus = async (appointmentId, newStatus) => {
    try {
      const response = await serviceCenterService.updateAppointmentStatus(appointmentId, newStatus)
      if (response.status === 'success') {
        // Reload data to get updated status
        await loadOngoingBookings()
        alert(`Service status updated to ${newStatus} successfully!`)
      }
    } catch (error) {
      console.error('Error updating status:', error)
      alert('Failed to update status. Please try again.')
    }
  }

  if (!centerId) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please select a service center first</p>
      </div>
    )
  }

  const scheduledAppointments = appointments.filter(apt => apt.status === 'scheduled')
  const inProgressAppointments = appointments.filter(apt => apt.status === 'in_progress')
  const completedAppointments = appointments.filter(apt => apt.status === 'completed')

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Ongoing Bookings</h1>
          <p className="text-gray-600 dark:text-slate-300 mt-1">Center ID: {centerId}</p>
        </div>
        <button
          onClick={loadOngoingBookings}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading ongoing bookings...</p>
        </div>
      ) : (
        <>
          {/* Scheduled Section - Can Start */}
          {scheduledAppointments.length > 0 && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b bg-blue-50">
                <h2 className="text-xl font-semibold text-gray-900">Scheduled - Ready to Start ({scheduledAppointments.length})</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appointment ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technician</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {scheduledAppointments.map((apt) => (
                      <tr key={apt.appointment_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {apt.appointment_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div>
                            <p className="font-medium">{apt.vehicle_name || apt.vin}</p>
                            {apt.plate_number && (
                              <p className="text-xs text-gray-400">{apt.plate_number}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.customer_name || apt.customer_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.technician_name || apt.technician_id || 'Not assigned'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(apt.scheduled_date).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => updateServiceStatus(apt.appointment_id, 'in_progress')}
                            className="text-primary-600 hover:text-primary-700 font-medium"
                          >
                            Start Service
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* In Progress Section */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b bg-yellow-50">
              <h2 className="text-xl font-semibold text-gray-900">In Progress ({inProgressAppointments.length})</h2>
            </div>
            <div className="overflow-x-auto">
              {inProgressAppointments.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No appointments in progress
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appointment ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technician</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {inProgressAppointments.map((apt) => (
                      <tr key={apt.appointment_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {apt.appointment_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div>
                            <p className="font-medium">{apt.vehicle_name || apt.vin}</p>
                            {apt.plate_number && (
                              <p className="text-xs text-gray-400">{apt.plate_number}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.customer_name || apt.customer_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.technician_name || apt.technician_id || 'Not assigned'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(apt.scheduled_date).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => updateServiceStatus(apt.appointment_id, 'completed')}
                            className="text-green-600 hover:text-green-700 font-medium"
                          >
                            Mark Complete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Completed Section */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b bg-green-50">
              <h2 className="text-xl font-semibold text-gray-900">Completed ({completedAppointments.length})</h2>
            </div>
            <div className="overflow-x-auto">
              {completedAppointments.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No completed appointments
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appointment ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technician</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completed Time</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {completedAppointments.map((apt) => (
                      <tr key={apt.appointment_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {apt.appointment_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div>
                            <p className="font-medium">{apt.vehicle_name || apt.vin}</p>
                            {apt.plate_number && (
                              <p className="text-xs text-gray-400">{apt.plate_number}</p>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.customer_name || apt.customer_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.technician_name || apt.technician_id || 'Not assigned'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.updated_at ? new Date(apt.updated_at).toLocaleString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ServiceCenterOngoing

