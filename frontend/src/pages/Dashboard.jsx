import React from 'react'
import { useAuth } from '../services/AuthContext'
import { useNavigate } from 'react-router-dom'
import CustomerDashboard from './CustomerDashboard'
import ServiceCenterSelection from './ServiceCenterSelection'
import ManufacturingDashboard from './ManufacturingDashboard'
import SystemDashboard from './SystemDashboard'

const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  
  // Route to role-specific dashboard
  if (user?.role === 'customer') {
    return <CustomerDashboard />
  } else if (user?.role === 'service_center') {
    // Always show selection page - don't remember previous selection
    // Clear any stored selection on login
    localStorage.removeItem('selectedServiceCenterId')
    return <ServiceCenterSelection />
  } else if (user?.role === 'manufacturing') {
    return <ManufacturingDashboard />
  } else if (user?.role === 'admin') {
    return <SystemDashboard />
  }
  
  return <CustomerDashboard /> // Default fallback
  const [stats, setStats] = useState({
    vehicles_monitored: 0,
    active_alerts: 0,
    scheduled_services: 0,
    health_score: 0,
  })
  const [recentAlerts, setRecentAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [demoVin] = useState('DEMO_VIN_001')
  const [demoCustomerId] = useState('CUST_001')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Simulate dashboard data
      setStats({
        vehicles_monitored: 150,
        active_alerts: 12,
        scheduled_services: 8,
        health_score: 85,
      })
      
      setRecentAlerts([
        { id: 1, vin: 'VIN001', message: 'High temperature detected', risk: 'high', time: '2 hours ago' },
        { id: 2, vin: 'VIN002', message: 'Oil pressure low', risk: 'medium', time: '5 hours ago' },
        { id: 3, vin: 'VIN003', message: 'Battery voltage low', risk: 'medium', time: '1 day ago' },
      ])
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const triggerWorkflow = async () => {
    try {
      const result = await workflowService.execute({
        workflow: 'monitor_and_predict',
        vin: demoVin,
        customer_id: demoCustomerId,
      })
      alert('Workflow executed successfully! Check the console for details.')
      console.log('Workflow result:', result)
    } catch (error) {
      console.error('Error executing workflow:', error)
      alert('Error executing workflow')
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Dashboard</h1>
        <button
          onClick={triggerWorkflow}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          Run Monitoring Workflow
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
              <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Vehicles Monitored</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.vehicles_monitored}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-red-100 rounded-md p-3">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Alerts</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.active_alerts}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Scheduled Services</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.scheduled_services}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
              <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg Health Score</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.health_score}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Alerts and Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Recent Alerts</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentAlerts.map((alert) => (
                <div key={alert.id} className="border-l-4 border-red-500 pl-4 py-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{alert.vin}</p>
                      <p className="text-sm text-gray-600">{alert.message}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      alert.risk === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {alert.risk}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow" style={{ height: '500px' }}>
          <Chat vin={demoVin} customerId={demoCustomerId} />
        </div>
      </div>
    </div>
  )
}

export default Dashboard

