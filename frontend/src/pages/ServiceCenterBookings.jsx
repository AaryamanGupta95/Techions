import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { serviceCenterService } from '../services/api'

const ServiceCenterBookings = () => {
  const location = useLocation()
  const centerId = location.state?.centerId || localStorage.getItem('selectedServiceCenterId')
  const [appointments, setAppointments] = useState([])
  const [filteredAppointments, setFilteredAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [dateFilter, setDateFilter] = useState({
    from: '',
    to: ''
  })

  useEffect(() => {
    if (centerId) {
      loadAppointments()
    }
  }, [centerId])

  const loadAppointments = async () => {
    setLoading(true)
    try {
      const response = await serviceCenterService.getServiceCenterAppointments(centerId)
      if (response.status === 'success') {
        const allAppointments = response.appointments || []
        setAppointments(allAppointments)
        // Apply current date filter or show all
        if (dateFilter.from || dateFilter.to) {
          applyDateFilter(allAppointments, dateFilter)
        } else {
          setFilteredAppointments(allAppointments)
        }
      }
    } catch (error) {
      console.error('Error loading appointments:', error)
    } finally {
      setLoading(false)
    }
  }

  const applyDateFilter = (appts, filter) => {
    if (!filter.from && !filter.to) {
      setFilteredAppointments(appts)
      return
    }

    const filtered = appts.filter(apt => {
      const aptDate = new Date(apt.scheduled_date)
      aptDate.setHours(0, 0, 0, 0)

      if (filter.from && filter.to) {
        const fromDate = new Date(filter.from)
        fromDate.setHours(0, 0, 0, 0)
        const toDate = new Date(filter.to)
        toDate.setHours(23, 59, 59, 999)
        return aptDate >= fromDate && aptDate <= toDate
      } else if (filter.from) {
        const fromDate = new Date(filter.from)
        fromDate.setHours(0, 0, 0, 0)
        return aptDate >= fromDate
      } else if (filter.to) {
        const toDate = new Date(filter.to)
        toDate.setHours(23, 59, 59, 999)
        return aptDate <= toDate
      }
      return true
    })

    setFilteredAppointments(filtered)
  }

  const handleDateFilterChange = (field, value) => {
    const newFilter = { ...dateFilter, [field]: value }
    setDateFilter(newFilter)
    applyDateFilter(appointments, newFilter)
  }

  const clearDateFilter = () => {
    const emptyFilter = { from: '', to: '' }
    setDateFilter(emptyFilter)
    setFilteredAppointments(appointments)
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
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">All Bookings</h1>
          <p className="text-gray-600 dark:text-slate-300 mt-1">Center ID: {centerId}</p>
        </div>
        <button
          onClick={loadAppointments}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          Refresh
        </button>
      </div>

      {/* Date Filter */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">From Date:</label>
            <input
              type="date"
              value={dateFilter.from}
              onChange={(e) => handleDateFilterChange('from', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">To Date:</label>
            <input
              type="date"
              value={dateFilter.to}
              onChange={(e) => handleDateFilterChange('to', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          {(dateFilter.from || dateFilter.to) && (
            <button
              onClick={clearDateFilter}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 text-sm"
            >
              Clear Filter
            </button>
          )}
          {(dateFilter.from || dateFilter.to) && (
            <span className="text-sm text-gray-600">
              Showing {filteredAppointments.length} of {appointments.length} appointments
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading bookings...</p>
        </div>
      ) : appointments.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">No bookings found.</p>
        </div>
      ) : filteredAppointments.length === 0 && (dateFilter.from || dateFilter.to) ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">No bookings found for the selected date range.</p>
          <button
            onClick={clearDateFilter}
            className="mt-4 text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Clear filter to see all bookings
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appointment ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scheduled Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Predicted Issue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Health Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technician</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(filteredAppointments.length > 0 ? filteredAppointments : appointments).map((apt) => (
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
                      {new Date(apt.scheduled_date).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="max-w-xs">
                        <p className="font-medium text-gray-900">{apt.predicted_issue || 'General maintenance'}</p>
                        {apt.failure_risk && (
                          <p className="text-xs text-gray-500 mt-1">Risk: {(apt.failure_risk * 100).toFixed(0)}%</p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {apt.health_score !== undefined ? (
                        <span className={`font-medium ${
                          apt.health_score < 50 ? 'text-red-600' :
                          apt.health_score < 70 ? 'text-orange-600' :
                          'text-green-600'
                        }`}>
                          {apt.health_score.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        apt.priority === 'critical' ? 'bg-red-100 text-red-800' :
                        apt.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {apt.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {apt.technician_name ? (
                        <span className="font-medium">{apt.technician_name}</span>
                      ) : apt.technician_id ? (
                        <span className="font-medium">{apt.technician_id}</span>
                      ) : (
                        <span className="text-gray-400">Not assigned</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        apt.status === 'completed' ? 'bg-green-100 text-green-800' :
                        apt.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {apt.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {apt.status === 'scheduled' && (
                        <button
                          onClick={async () => {
                            try {
                              await serviceCenterService.updateAppointmentStatus(apt.appointment_id, 'in_progress')
                              await loadAppointments()
                            } catch (error) {
                              console.error('Error updating status:', error)
                              alert('Failed to start service. Please try again.')
                            }
                          }}
                          className="text-primary-600 hover:text-primary-700 font-medium"
                        >
                          Start Service
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default ServiceCenterBookings

