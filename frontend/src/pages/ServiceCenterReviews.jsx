import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { serviceCenterService } from '../services/api'

const ServiceCenterReviews = () => {
  const location = useLocation()
  const centerId = location.state?.centerId || localStorage.getItem('selectedServiceCenterId')
  const [stats, setStats] = useState({
    averageRating: 0,
    totalFeedbacks: 0,
    feedback: [],
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (centerId) {
      loadReviews()
    } else {
      setLoading(false)
    }
  }, [centerId])

  const loadReviews = async () => {
    setLoading(true)
    try {
      const response = await serviceCenterService.getServiceCenterFeedback(centerId)
      if (response.status === 'success') {
        setStats({
          averageRating: response.average_rating || 0,
          totalFeedbacks: response.total_feedbacks || 0,
          feedback: response.feedback || [],
        })
      }
    } catch (error) {
      console.error('Error loading reviews:', error)
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
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50 flex items-center">
            <svg className="w-8 h-8 mr-3 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            Customer Reviews
          </h1>
          <p className="text-gray-600 dark:text-slate-400 mt-1">Center ID: {centerId}</p>
        </div>
        <button
          onClick={loadReviews}
          className="bg-gradient-to-r from-primary-600 to-indigo-600 text-white px-5 py-2.5 rounded-xl hover:from-primary-700 hover:to-indigo-700 shadow-lg shadow-primary-500/50 hover:shadow-xl transition-all transform hover:scale-105 active:scale-95 font-semibold flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>Refresh</span>
        </button>
      </div>

      <div className="enhanced-card p-6 flex items-center justify-between bg-gradient-to-r from-yellow-50 via-amber-50 to-orange-50 dark:from-yellow-900/30 dark:via-amber-900/30 dark:to-orange-900/30 border-2 border-yellow-200 dark:border-yellow-800/50">
        <div className="flex items-center space-x-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center shadow-lg">
            <span className="text-4xl font-bold text-white">
              {stats.totalFeedbacks > 0 ? stats.averageRating.toFixed(1) : '—'}
            </span>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider">Average Rating</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-slate-50 mt-1">
              {stats.totalFeedbacks > 0 ? `${stats.averageRating.toFixed(1)} / 5.0` : 'No ratings yet'}
            </p>
            <div className="flex items-center mt-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <svg
                  key={star}
                  className={`w-5 h-5 ${
                    star <= Math.round(stats.averageRating)
                      ? 'text-yellow-400'
                      : 'text-gray-300 dark:text-slate-600'
                  }`}
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold text-gray-600 dark:text-slate-400 uppercase tracking-wider">Total Reviews</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-slate-50 mt-1">{stats.totalFeedbacks}</p>
          <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">Customer feedback</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-slate-400">Loading reviews...</p>
        </div>
      ) : stats.totalFeedbacks === 0 ? (
        <div className="enhanced-card p-12 text-center">
          <svg className="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
          <p className="text-gray-600 dark:text-slate-400 font-medium">No reviews yet for this service center.</p>
          <p className="text-sm text-gray-500 dark:text-slate-500 mt-2">Reviews will appear here after customers rate their service.</p>
        </div>
      ) : (
        <div className="enhanced-card overflow-hidden">
          <div className="divide-y divide-gray-200 dark:divide-slate-700">
            {stats.feedback.map((fb) => (
              <div key={fb.feedback_id} className="p-6 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="flex items-center">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <svg
                            key={star}
                            className={`w-5 h-5 ${
                              star <= fb.rating
                                ? 'text-yellow-400'
                                : 'text-gray-300 dark:text-slate-600'
                            }`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <span className="text-xs font-semibold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-2 py-1 rounded">
                        Appointment #{fb.appointment_id}
                      </span>
                    </div>
                    {fb.comments && (
                      <p className="text-sm text-gray-700 dark:text-slate-300 mt-2 leading-relaxed">{fb.comments}</p>
                    )}
                    <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500 dark:text-slate-400">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        VIN: {fb.vin}
                      </span>
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        {fb.customer_id}
                      </span>
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-xs text-gray-500 dark:text-slate-400 flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {new Date(fb.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-[10px] text-gray-400 dark:text-slate-500 mt-1">
                      {new Date(fb.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ServiceCenterReviews


