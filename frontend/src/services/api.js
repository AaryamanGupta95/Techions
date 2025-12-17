import axios from 'axios'

// Use env override for dev; fall back to local backend
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth service
export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },
  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
}

// Vehicle service
export const vehicleService = {
  getTelemetry: async (vin) => {
    const response = await api.get(`/telemetry/${vin}`)
    return response.data
  },
  ingestTelemetry: async (data) => {
    const response = await api.post('/telemetry/ingest', data)
    return response.data
  },
  getVehicle: async (vin) => {
    const response = await api.get(`/vehicles/${vin}`)
    return response.data
  },
  getCustomerVehicles: async (customerId) => {
    const response = await api.get(`/vehicles/customer/${customerId}`)
    return response.data
  },
  createVehicle: async (vehicleData) => {
    const response = await api.post('/vehicles', vehicleData)
    return response.data
  },
}

// Prediction service
export const predictionService = {
  predict: async (data) => {
    const response = await api.post('/predictions/predict', data)
    return response.data
  },
}

// Scheduling service
export const schedulingService = {
  schedule: async (data) => {
    const response = await api.post('/scheduling/schedule', data)
    return response.data
  },
  reschedule: async (data) => {
    const response = await api.post('/scheduling/reschedule', data)
    return response.data
  },
  cancel: async (data) => {
    const response = await api.post('/scheduling/cancel', data)
    return response.data
  },
  getAvailability: async () => {
    const response = await api.get('/scheduling/availability')
    return response.data
  },
  getAppointments: async (customerId) => {
    const response = await api.get(`/scheduling/appointments/${customerId}`)
    return response.data
  },
}

// Service Center service
export const serviceCenterService = {
  getServiceCenters: async () => {
    const response = await api.get('/service-centers')
    return response.data
  },
  getServiceCenterAppointments: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/appointments`)
    return response.data
  },
  getServiceCenterTechnicians: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/technicians`)
    return response.data
  },
  getServiceCenterWorkload: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/workload`)
    return response.data
  },
  updateAppointmentStatus: async (appointmentId, status) => {
    const response = await api.put(`/appointments/${appointmentId}/status`, { status })
    return response.data
  },
  getOngoingBookings: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/ongoing-bookings`)
    return response.data
  },
  getPreDiagnosedCases: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/pre-diagnosed-cases`)
    return response.data
  },
  getServiceCenterFeedback: async (centerId) => {
    const response = await api.get(`/service-centers/${centerId}/feedback`)
    return response.data
  },
}

// Engagement service
export const engagementService = {
  sendAlert: async (data) => {
    const response = await api.post('/engagement/send-alert', data)
    return response.data
  },
  chat: async (data) => {
    const response = await api.post('/engagement/chat', data)
    return response.data
  },
}

// Feedback service
export const feedbackService = {
  submit: async (data) => {
    const response = await api.post('/feedback/submit', data)
    return response.data
  },
  getSummary: async (vin, serviceCenterId) => {
    const response = await api.get('/feedback/summary', {
      params: { vin, service_center_id: serviceCenterId },
    })
    return response.data
  },
}

// Manufacturing service
export const manufacturingService = {
  generateInsights: async (manufacturer) => {
    const response = await api.post('/manufacturing/generate-insights', null, {
      params: { manufacturer },
    })
    return response.data
  },
  getInsights: async (manufacturer) => {
    const response = await api.get('/manufacturing/insights', {
      params: { manufacturer },
    })
    return response.data
  },
  getPatterns: async (manufacturer) => {
    const response = await api.get('/manufacturing/patterns', {
      params: { manufacturer },
    })
    return response.data
  },
}

// Security service
export const securityService = {
  analyze: async () => {
    const response = await api.post('/security/analyze')
    return response.data
  },
  getEvents: async () => {
    const response = await api.get('/security/events')
    return response.data
  },
  checkAgent: async (agentName) => {
    const response = await api.get(`/security/agent/${agentName}`)
    return response.data
  },
}

// Workflow service
export const workflowService = {
  execute: async (data) => {
    const response = await api.post('/workflow/execute', data)
    return response.data
  },
}

// Notification service (AI-controlled alerts)
export const notificationService = {
  checkAndCreate: async (customerId) => {
    const response = await api.post(`/notifications/check-and-create`, {
      customer_id: customerId
    })
    return response.data
  },
  getCustomerNotifications: async (customerId, notificationType = null) => {
    const url = notificationType 
      ? `/notifications/customer/${customerId}?notification_type=${notificationType}`
      : `/notifications/customer/${customerId}`
    const response = await api.get(url)
    return response.data
  },
}

export default api

