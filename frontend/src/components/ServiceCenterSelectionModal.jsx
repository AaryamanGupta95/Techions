import React, { useState, useEffect } from 'react'
import { schedulingService, feedbackService } from '../services/api'

const ServiceCenterSelectionModal = ({ isOpen, onClose, vehicle, onSuccess, isReschedule = false, appointmentId = null }) => {
  const [serviceCenters, setServiceCenters] = useState([])
  const [selectedCenter, setSelectedCenter] = useState(null)
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedTime, setSelectedTime] = useState('10:00')
  const [loading, setLoading] = useState(false)
  const [scheduling, setScheduling] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadServiceCenters()
      // Set default date to tomorrow
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      setSelectedDate(tomorrow.toISOString().split('T')[0])
      setSelectedTime('10:00')
    }
  }, [isOpen])

  const loadServiceCenters = async () => {
    setLoading(true)
    setError('')
    try {
      // Always fetch from MongoDB - no demo data
      const response = await schedulingService.getAvailability()
      
      if (!response || response.status !== 'success') {
        throw new Error('Failed to fetch service centers')
      }
      
      let centers = response.availability || []

      // Filter centers based on vehicle manufacturer (Hero/Mahindra alignment)
      if (vehicle && vehicle.manufacturer) {
        const manufacturer = vehicle.manufacturer.toLowerCase()
        if (manufacturer.includes('hero')) {
          centers = centers.filter((center) =>
            (center.name || '').toLowerCase().includes('hero')
          )
        } else if (manufacturer.includes('mahindra')) {
          centers = centers.filter((center) =>
            (center.name || '').toLowerCase().includes('mahindra')
          )
        }
      }
      
      // If no centers returned, show error
      if (centers.length === 0) {
        setError('No service centers found in the system. Please contact support or try again later.')
        setServiceCenters([])
        return
      }
      
      // Filter to show only centers with available slots (but keep at least 3 if all are full)
      const availableCenters = centers.filter(center => (center.available_slots || 0) > 0)
      
      const centersToUse = availableCenters.length === 0 ? centers.slice(0, 3) : availableCenters

      // Attach rating information for each center
      const centersWithRatings = await Promise.all(
        centersToUse.map(async (center) => {
          try {
            const summary = await feedbackService.getSummary(undefined, center.center_id)
            const avg = summary.summary?.average_rating || 0
            const total = summary.summary?.total_feedbacks || 0
            return { ...center, average_rating: avg, total_feedbacks: total }
          } catch (err) {
            console.error('Error loading rating for center', center.center_id, err)
            return { ...center, average_rating: 0, total_feedbacks: 0 }
          }
        })
      )

      if (availableCenters.length === 0) {
        setError('All service centers are currently at full capacity. You can still select a center, but availability may be limited.')
      } else {
        setError('')
      }

      setServiceCenters(centersWithRatings)
    } catch (error) {
      console.error('Error loading service centers:', error)
      setError('Failed to load service centers. Please refresh the page and try again.')
      setServiceCenters([])
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmBooking = async () => {
    if (!selectedCenter) {
      setError('Please select a service center')
      return
    }

    if (!selectedDate) {
      setError('Please select a date')
      return
    }

    if (!selectedTime) {
      setError('Please select a time')
      return
    }

    setScheduling(true)
    setError('')

    try {
      const customerId = vehicle.customer_id || 'CUST_001'
      
      // Combine date and time into ISO string
      const scheduledDateTime = new Date(`${selectedDate}T${selectedTime}:00`)
      
      let result
      if (isReschedule && appointmentId) {
        // For reschedule, cancel old appointment and create new one
        result = await schedulingService.reschedule({
          appointment_id: appointmentId,
          customer_id: customerId,
          vin: vehicle.vin,
          service_center_id: selectedCenter.center_id,
          scheduled_date: scheduledDateTime.toISOString(),
          service_type: 'predictive',
          priority: 'medium',
          risk_score: 0.6
        })
      } else {
        result = await schedulingService.schedule({
          customer_id: customerId,
          vin: vehicle.vin,
          service_center_id: selectedCenter.center_id,
          scheduled_date: scheduledDateTime.toISOString(),
          service_type: 'predictive',
          priority: 'medium',
          risk_score: 0.6
        })
      }
      
      // Call onSuccess with the result
      if (onSuccess && result) {
        await onSuccess(result)
      }
      
      // Close modal after success
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || err.message || `Failed to ${isReschedule ? 'reschedule' : 'schedule'} service. Please try again.`)
    } finally {
      setScheduling(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {isReschedule ? 'Reschedule Service' : 'Select Service Center'}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {isReschedule ? 'Reschedule' : 'Book'} service for {vehicle?.vehicle_name || vehicle?.model} ({vehicle?.plate_number})
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading service centers...</p>
            </div>
          ) : serviceCenters.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-2">No service centers with available slots at the moment.</p>
              <p className="text-sm text-gray-500">Please try again later.</p>
            </div>
          ) : (
            <>
              {/* Date and Time Selection */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-700 mb-4">Select Date & Time</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Date
                    </label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      max={(() => {
                        const max = new Date()
                        max.setDate(max.getDate() + 20)
                        return max.toISOString().split('T')[0]
                      })()}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Time
                    </label>
                    <input
                      type="time"
                      value={selectedTime}
                      onChange={(e) => setSelectedTime(e.target.value)}
                      min="09:00"
                      max="18:00"
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">Service hours: 9:00 AM - 6:00 PM</p>
                  </div>
                </div>
              </div>

              {/* Service Center Selection */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Select Service Center</h3>
                <div className="space-y-3">
                  {serviceCenters.map((center) => (
                    <div
                      key={center.center_id}
                      onClick={() => setSelectedCenter(center)}
                      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                        selectedCenter?.center_id === center.center_id
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
                            center.available_slots > 5
                              ? 'bg-green-100 text-green-800'
                              : center.available_slots > 2
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {center.available_slots} slots available
                          </div>
                          <p className="text-xs text-gray-500 mt-1">Capacity: {center.capacity}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            Rating:{' '}
                            {center.average_rating && center.total_feedbacks > 0
                              ? `${center.average_rating.toFixed(1)} / 5 (${center.total_feedbacks} reviews)`
                              : 'No reviews yet'}
                          </p>
                        </div>
                      </div>
                      {selectedCenter?.center_id === center.center_id && (
                        <div className="mt-2 pt-2 border-t border-primary-200">
                          <p className="text-sm text-primary-700">✓ Selected</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmBooking}
                  disabled={!selectedCenter || !selectedDate || !selectedTime || scheduling}
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {scheduling ? (isReschedule ? 'Rescheduling...' : 'Scheduling...') : (isReschedule ? 'Confirm Reschedule' : 'Confirm Booking')}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ServiceCenterSelectionModal

