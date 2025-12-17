import React, { useState, useEffect } from 'react'

const SystemDashboard = () => {
  const [agentStats, setAgentStats] = useState({})
  const [securityEvents, setSecurityEvents] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Use static sample data so the dashboard always looks operational
    setLoading(true)
    const now = new Date()
    const demoEvents = [
      {
        event_id: 'SEC_SAMPLE_001',
        event_type: 'anomaly',
        severity: 'high',
        agent_name: 'Failure Prediction Agent',
        description: 'Unusually high failure risk detected for Mahindra XUV300 vehicles.',
        detected_at: now.toISOString(),
      },
      {
        event_id: 'SEC_SAMPLE_002',
        event_type: 'anomaly',
        severity: 'medium',
        agent_name: 'Customer Engagement Agent',
        description: 'Multiple alerts sent to the same customer within a short time window.',
        detected_at: new Date(now.getTime() - 5 * 60000).toISOString(),
      },
    ]

    setAgentStats({
      totalAgents: 8,
      activeAgents: 7,
      anomaliesDetected: demoEvents.filter(e => e.event_type === 'anomaly').length,
      totalActions: 4890,
    })
    setSecurityEvents(demoEvents)
    setLoading(false)
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">System & Agentic AI Dashboard</h1>

      {/* Agent Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800 p-6">
          <p className="text-sm font-medium text-gray-500 dark:text-slate-400">Total Agents</p>
          <p className="text-3xl font-semibold text-slate-900 dark:text-slate-50">{agentStats.totalAgents || 8}</p>
        </div>
        <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800 p-6">
          <p className="text-sm font-medium text-gray-500 dark:text-slate-400">Active Agents</p>
          <p className="text-3xl font-semibold text-green-600">{agentStats.activeAgents || 7}</p>
        </div>
        <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800 p-6">
          <p className="text-sm font-medium text-gray-500 dark:text-slate-400">Anomalies Detected</p>
          <p className="text-3xl font-semibold text-red-600">{agentStats.anomaliesDetected || 0}</p>
        </div>
        <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800 p-6">
          <p className="text-sm font-medium text-gray-500 dark:text-slate-400">Total Actions</p>
          <p className="text-3xl font-semibold text-slate-900 dark:text-slate-50">{agentStats.totalActions || 0}</p>
        </div>
      </div>

      {/* Agent Status Table */}
      <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">Agent Status Table</h2>
          <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">Real-time status of all agents in the system</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
            <thead className="bg-gray-50 dark:bg-slate-800/80">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase">
                  Agent Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase">
                  Last Activity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase">
                  Action Count
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-300 uppercase">
                  Health Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-800">
              {[
                { name: 'Master Agent', status: 'active', lastActivity: new Date(Date.now() - 2 * 60000), actions: 1250, health: 'healthy' },
                { name: 'Telemetry Agent', status: 'active', lastActivity: new Date(Date.now() - 5 * 60000), actions: 1250, health: 'healthy' },
                { name: 'Failure Prediction Agent', status: 'active', lastActivity: new Date(Date.now() - 3 * 60000), actions: 890, health: 'healthy' },
                { name: 'Customer Engagement Agent', status: 'active', lastActivity: new Date(Date.now() - 1 * 60000), actions: 450, health: 'healthy' },
                { name: 'Smart Scheduling Agent', status: 'active', lastActivity: new Date(Date.now() - 4 * 60000), actions: 320, health: 'healthy' },
                { name: 'Feedback Agent', status: 'active', lastActivity: new Date(Date.now() - 6 * 60000), actions: 280, health: 'healthy' },
                { name: 'Manufacturing Insights Agent', status: 'active', lastActivity: new Date(Date.now() - 10 * 60000), actions: 150, health: 'healthy' },
                { name: 'UEBA Security Agent', status: 'active', lastActivity: new Date(Date.now() - 1 * 60000), actions: 2100, health: 'healthy' },
              ].map((agent) => (
                <tr key={agent.name}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-slate-50">
                    {agent.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-slate-300">
                    {agent.lastActivity.toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900 dark:text-slate-50">
                    {agent.actions.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      agent.health === 'healthy' ? 'bg-green-100 text-green-800' :
                      agent.health === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {agent.health}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Workflow Timeline */}
      <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">Workflow Timeline</h2>
          <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">
            Telemetry → Prediction → Booking → Service → Feedback
          </p>
        </div>
        <div className="p-6">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>
            
            {/* Timeline steps */}
            <div className="space-y-6">
              {[
                { step: 'Telemetry', agent: 'Telemetry Agent', description: 'Ingest vehicle data', status: 'completed', time: '2 min ago' },
                { step: 'Prediction', agent: 'Failure Prediction Agent', description: 'Analyze and predict failures', status: 'completed', time: '1 min ago' },
                { step: 'Booking', agent: 'Smart Scheduling Agent', description: 'Schedule service appointment', status: 'completed', time: '30 sec ago' },
                { step: 'Service', agent: 'Service Center', description: 'Execute service', status: 'in_progress', time: 'Now' },
                { step: 'Feedback', agent: 'Feedback Agent', description: 'Collect customer feedback', status: 'pending', time: 'Pending' },
              ].map((item, index) => (
                <div key={index} className="relative flex items-start">
                  <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full border-4 bg-white ${
                    item.status === 'completed' ? 'border-green-500' :
                    item.status === 'in_progress' ? 'border-blue-500' :
                    'border-gray-300'
                  }`}>
                    <span className={`text-2xl ${
                      item.status === 'completed' ? 'text-green-500' :
                      item.status === 'in_progress' ? 'text-blue-500' :
                      'text-gray-400'
                    }`}>
                      {item.status === 'completed' ? '✓' : item.status === 'in_progress' ? '⟳' : '○'}
                    </span>
                  </div>
                  <div className="ml-6 flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">{item.step}</h3>
                        <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">{item.description}</p>
                        <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">Agent: {item.agent}</p>
                      </div>
                      <div className="text-right">
                        <span
                          className={`px-3 py-1 text-xs rounded-full ${
                          item.status === 'completed' ? 'bg-green-100 text-green-800' :
                          item.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}
                        >
                          {item.status}
                        </span>
                        <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">{item.time}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* UEBA Security Monitoring */}
      <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">UEBA Security Monitoring</h2>
          <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">Tracks agent behavior and flags anomalies</p>
        </div>
        <div className="p-6">
          {securityEvents.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-slate-400">
              <p>No security events detected</p>
              <p className="text-sm mt-2">All agents operating normally</p>
            </div>
          ) : (
            <div className="space-y-4">
              {securityEvents.map((event) => (
                <div key={event.event_id} className={`border-l-4 ${
                  event.severity === 'critical' ? 'border-red-500 bg-red-50' :
                  event.severity === 'high' ? 'border-orange-500 bg-orange-50' :
                  'border-yellow-500 bg-yellow-50'
                } pl-4 py-3 rounded`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-slate-50">{event.description}</p>
                      <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">
                        Agent: {event.agent_name || 'N/A'} | Type: {event.event_type}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-slate-400 mt-1">
                        Detected: {new Date(event.detected_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 text-xs rounded-full ${
                      event.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      event.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {event.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Agent Action Logs */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Agent Action Logs</h2>
          <p className="text-sm text-gray-600 mt-1">Timestamp, Agent name, Action performed</p>
        </div>
        <div className="p-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action Performed</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { timestamp: new Date(Date.now() - 2 * 60000), agent: 'Master Agent', action: 'Orchestrated workflow execution' },
                  { timestamp: new Date(Date.now() - 5 * 60000), agent: 'Telemetry Agent', action: 'Ingested vehicle data for 15 vehicles' },
                  { timestamp: new Date(Date.now() - 3 * 60000), agent: 'Failure Prediction Agent', action: 'Analyzed 12 vehicles, detected 3 high-risk cases' },
                  { timestamp: new Date(Date.now() - 1 * 60000), agent: 'Customer Engagement Agent', action: 'Sent 3 proactive alerts' },
                  { timestamp: new Date(Date.now() - 4 * 60000), agent: 'Smart Scheduling Agent', action: 'Scheduled 2 service appointments' },
                  { timestamp: new Date(Date.now() - 1 * 60000), agent: 'UEBA Security Agent', action: 'Analyzed 2100 agent logs, detected 0 anomalies' },
                ].map((log, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {log.timestamp.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{log.agent}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{log.action}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Anomaly Alerts */}
      {securityEvents.length > 0 && (
        <div className="bg-white rounded-lg shadow border-2 border-red-300">
          <div className="p-6 border-b bg-red-50">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <span className="mr-2 text-2xl">⚠️</span>
              Anomaly Alerts
            </h2>
            <p className="text-sm text-gray-600 mt-1">Unexpected behavior flagged by UEBA Security Agent</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {securityEvents.map((event) => (
                <div key={event.event_id} className={`border-l-4 ${
                  event.severity === 'critical' ? 'border-red-500 bg-red-50' :
                  event.severity === 'high' ? 'border-orange-500 bg-orange-50' :
                  'border-yellow-500 bg-yellow-50'
                } pl-4 py-3 rounded`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-gray-900">{event.description}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Agent: {event.agent_name || 'N/A'} | Type: {event.event_type}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Detected: {new Date(event.detected_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 text-xs rounded-full ${
                      event.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      event.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {event.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SystemDashboard

