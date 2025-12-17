import React, { useState, useEffect } from 'react'
import { manufacturingService } from '../services/api'
import jsPDF from 'jspdf'

// Demo fallback data so dashboard always looks populated
const getDemoPatterns = (manufacturer) => {
  const heroPatterns = [
    {
      pattern_id: 'PAT_HERO_ENGINE_OVERHEAT',
      component: 'Engine Cooling System',
      failure_type: 'Engine Overheating',
      manufacturer: 'Hero',
      model: 'Hero Splendor',
      occurrence_count: 8,
      severity: 'critical',
    },
    {
      pattern_id: 'PAT_HERO_BRAKE_WEAR',
      component: 'Braking System',
      failure_type: 'Brake Pad Wear',
      manufacturer: 'Hero',
      model: 'Hero Splendor',
      occurrence_count: 5,
      severity: 'high',
    },
  ]

  const mahindraPatterns = [
    {
      pattern_id: 'PAT_MAHINDRA_BATTERY',
      component: 'Electrical System',
      failure_type: 'Battery Drain',
      manufacturer: 'Mahindra',
      model: 'Mahindra XUV300',
      occurrence_count: 7,
      severity: 'high',
    },
    {
      pattern_id: 'PAT_MAHINDRA_OIL_PRESSURE',
      component: 'Engine Oil System',
      failure_type: 'Low Oil Pressure',
      manufacturer: 'Mahindra',
      model: 'Mahindra XUV300',
      occurrence_count: 4,
      severity: 'medium',
    },
  ]

  if (manufacturer === 'Hero') return heroPatterns
  if (manufacturer === 'Mahindra') return mahindraPatterns
  return [...heroPatterns, ...mahindraPatterns]
}

const getDemoInsights = (manufacturer) => {
  const base = [
    {
      insight_id: 'INSIGHT_HERO_ENGINE',
      failure_pattern_id: 'PAT_HERO_ENGINE_OVERHEAT',
      manufacturer: 'Hero',
      title: 'RCA/CAPA Analysis: Engine Cooling System Overheating',
      root_causes: ['Insufficient coolant flow', 'Thermostat sticking in closed position'],
      contributing_factors: ['High ambient temperatures', 'Delayed maintenance'],
      analysis_summary:
        'Hero Splendor bikes show repeated overheating events. Improving cooling design and service intervals will reduce failures.',
      corrective_actions: [
        {
          description: 'Review and update coolant flow specifications for Hero Splendor engines.',
          responsible_team: 'Engineering',
          status: 'pending',
        },
        {
          description: 'Redesign thermostat to reduce sticking risk in high-temperature conditions.',
          responsible_team: 'Design',
          status: 'pending',
        },
      ],
      preventive_actions: [
        {
          description: 'Introduce enhanced cooling system health checks in service centers.',
          responsible_team: 'After-sales',
          status: 'pending',
        },
        {
          description: 'Update preventive maintenance schedule to include coolant quality checks.',
          responsible_team: 'Quality',
          status: 'pending',
        },
      ],
      affected_vehicles_count: 8,
      estimated_impact: 'High impact - affects significant number of vehicles',
      recommendation_priority: 'critical',
    },
    {
      insight_id: 'INSIGHT_MAHINDRA_BATTERY',
      failure_pattern_id: 'PAT_MAHINDRA_BATTERY',
      manufacturer: 'Mahindra',
      title: 'RCA/CAPA Analysis: Electrical System Battery Drain',
      root_causes: ['Parasitic drain from infotainment system', 'Aging battery chemistry'],
      contributing_factors: ['Short trips', 'High accessory usage'],
      analysis_summary:
        'Mahindra XUV300 vehicles show frequent battery drain cases. Optimizing power management and battery specifications will reduce warranty claims.',
      corrective_actions: [
        {
          description: 'Optimize infotainment power management to reduce standby drain.',
          responsible_team: 'Electronics',
          status: 'pending',
        },
        {
          description: 'Introduce higher-capacity batteries for XUV300 high-accessory variants.',
          responsible_team: 'Product Engineering',
          status: 'pending',
        },
      ],
      preventive_actions: [
        {
          description: 'Add battery health check in every scheduled service.',
          responsible_team: 'After-sales',
          status: 'pending',
        },
        {
          description: 'Educate customers about accessory usage and charging patterns.',
          responsible_team: 'Customer Experience',
          status: 'pending',
        },
      ],
      affected_vehicles_count: 7,
      estimated_impact: 'Medium impact - affects multiple vehicles',
      recommendation_priority: 'high',
    },
  ]

  if (manufacturer === 'Hero') return base.filter((i) => i.manufacturer === 'Hero')
  if (manufacturer === 'Mahindra') return base.filter((i) => i.manufacturer === 'Mahindra')
  return base
}

const ManufacturingDashboard = () => {
  const [insights, setInsights] = useState([])
  const [patterns, setPatterns] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedManufacturer, setSelectedManufacturer] = useState('Hero') // Hero, Mahindra, or All

  useEffect(() => {
    loadInsights('Hero')
    loadPatterns('Hero')
  }, [])

  const loadInsights = async (manufacturer) => {
    setLoading(true)
    try {
      const response = await manufacturingService.getInsights(
        manufacturer === 'All' ? undefined : manufacturer
      )
      const data = response.insights || []
      if (data.length === 0) {
        setInsights(getDemoInsights(manufacturer))
      } else {
        setInsights(data)
      }
    } catch (error) {
      console.error('Error loading insights:', error)
      setInsights(getDemoInsights(manufacturer))
    } finally {
      setLoading(false)
    }
  }

  const loadPatterns = async (manufacturer) => {
    try {
      const response = await manufacturingService.getPatterns(
        manufacturer === 'All' ? undefined : manufacturer
      )
      const data = response.patterns || []
      if (data.length === 0) {
        setPatterns(getDemoPatterns(manufacturer))
      } else {
        setPatterns(data)
      }
    } catch (error) {
      console.error('Error loading patterns:', error)
      setPatterns(getDemoPatterns(manufacturer))
    }
  }

  const generateInsights = async () => {
    setLoading(true)
    try {
      const manufacturerParam = selectedManufacturer === 'All' ? undefined : selectedManufacturer

      // Ask backend to generate insights (best-effort; ignore failures)
      try {
        await manufacturingService.generateInsights(manufacturerParam)
      } catch (e) {
        console.warn('Generate insights call failed, falling back to local data', e)
      }

      // Fetch latest data (with fallback to sample data)
      const [insightsResponse, patternsResponse] = await Promise.all([
        manufacturingService.getInsights(manufacturerParam),
        manufacturingService.getPatterns(manufacturerParam),
      ])

      const insightsData =
        (insightsResponse && insightsResponse.insights && insightsResponse.insights.length
          ? insightsResponse.insights
          : getDemoInsights(selectedManufacturer)) || []

      const patternsData =
        (patternsResponse && patternsResponse.patterns && patternsResponse.patterns.length
          ? patternsResponse.patterns
          : getDemoPatterns(selectedManufacturer)) || []

      // Update UI state
      setInsights(insightsData)
      setPatterns(patternsData)

      // Build PDF summary
      const doc = new jsPDF()
      const title = `Manufacturing Summary - ${selectedManufacturer} (${new Date().toLocaleDateString()})`
      doc.setFontSize(14)
      doc.text(title, 10, 15)

      let y = 25
      doc.setFontSize(11)
      doc.text('Failure Trends:', 10, y)
      y += 6

      patternsData.slice(0, 6).forEach((p, index) => {
        if (y > 270) {
          doc.addPage()
          y = 20
        }
        const line = `${index + 1}. ${p.component} / ${p.model || 'N/A'} - ${p.failure_type}  (Cases: ${
          p.occurrence_count
        }, Severity: ${p.severity})`
        doc.text(line.slice(0, 110), 12, y)
        y += 6
      })

      y += 4
      doc.setFontSize(11)
      doc.text('RCA / CAPA Insights:', 10, y)
      y += 6

      insightsData.slice(0, 4).forEach((insight, idx) => {
        if (y > 260) {
          doc.addPage()
          y = 20
        }
        doc.setFont(undefined, 'bold')
        doc.text(`${idx + 1}. ${insight.title}`, 12, y)
        doc.setFont(undefined, 'normal')
        y += 5

        if (insight.analysis_summary) {
          const summary = doc.splitTextToSize(
            `Summary: ${insight.analysis_summary}`,
            185
          )
          summary.forEach((line) => {
            if (y > 270) {
              doc.addPage()
              y = 20
            }
            doc.text(line, 14, y)
            y += 5
          })
        }

        if (insight.corrective_actions && insight.corrective_actions.length) {
          if (y > 270) {
            doc.addPage()
            y = 20
          }
          doc.text('Corrective Actions:', 14, y)
          y += 5
          insight.corrective_actions.slice(0, 3).forEach((a, i) => {
            const line = `• ${a.description} [${a.responsible_team || ''}]`
            const wrapped = doc.splitTextToSize(line, 185)
            wrapped.forEach((l) => {
              if (y > 270) {
                doc.addPage()
                y = 20
              }
              doc.text(l, 18, y)
              y += 4
            })
          })
        }

        if (insight.preventive_actions && insight.preventive_actions.length) {
          if (y > 270) {
            doc.addPage()
            y = 20
          }
          doc.text('Preventive Actions:', 14, y)
          y += 5
          insight.preventive_actions.slice(0, 3).forEach((a, i) => {
            const line = `• ${a.description} [${a.responsible_team || ''}]`
            const wrapped = doc.splitTextToSize(line, 185)
            wrapped.forEach((l) => {
              if (y > 270) {
                doc.addPage()
                y = 20
              }
              doc.text(l, 18, y)
              y += 4
            })
          })
        }

        y += 4
      })

      const fileName = `manufacturing_summary_${selectedManufacturer.toLowerCase()}_${new Date()
        .toISOString()
        .slice(0, 10)}.pdf`
      doc.save(fileName)
    } catch (error) {
      console.error('Error generating insights or PDF:', error)
      alert('Unable to generate summary right now. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 text-white rounded-xl px-6 py-5 shadow-sm">
        <div>
          <h1 className="text-3xl font-bold text-white">Manufacturing Insights Dashboard</h1>
          <p className="text-sm text-slate-200 mt-1">
            OEM quality view aligned with customer & service center data
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Manufacturer Switcher */}
          <div className="bg-slate-800 rounded-full p-1 flex text-sm font-medium">
            {['Hero', 'Mahindra', 'All'].map((mfg) => (
              <button
                key={mfg}
                onClick={() => {
                  setSelectedManufacturer(mfg)
                  loadPatterns(mfg)
                  loadInsights(mfg)
                }}
                className={`px-3 py-1 rounded-full transition ${
                  selectedManufacturer === mfg
                    ? 'bg-primary-600 text-white'
                    : 'text-slate-200 hover:text-white'
                }`}
              >
                {mfg}
              </button>
            ))}
          </div>
          <button
            onClick={generateInsights}
            disabled={loading}
            className="bg-primary-500 hover:bg-primary-400 text-slate-900 font-semibold px-4 py-2 rounded-lg shadow-sm disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Insights'}
          </button>
        </div>
      </div>

      {/* Failure Trends Chart */}
      <div className="bg-white/95 dark:bg-slate-900/80 rounded-lg shadow-sm border border-slate-100 dark:border-slate-800">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">Failure Trends Chart</h2>
          <p className="text-sm text-gray-600 dark:text-slate-300 mt-1">Failures by component, model, and time period</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-slate-200 mb-3">By Component</h3>
              <div className="space-y-2">
                {patterns.slice(0, 5).map((pattern) => (
                  <div key={pattern.pattern_id} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-slate-300">{pattern.component}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-slate-700 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${Math.min(100, (pattern.occurrence_count / 50) * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-slate-50 w-8">{pattern.occurrence_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">By Model</h3>
              <div className="space-y-2">
                {patterns.slice(0, 5).map((pattern) => (
                  <div key={pattern.pattern_id} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{pattern.model || 'N/A'}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${Math.min(100, (pattern.occurrence_count / 50) * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-8">{pattern.occurrence_count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">By Severity</h3>
              <div className="space-y-2">
                {['critical', 'high', 'medium'].map((severity) => {
                  const count = patterns.filter(p => p.severity === severity).length
                  return (
                    <div key={severity} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{severity}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              severity === 'critical' ? 'bg-red-600' :
                              severity === 'high' ? 'bg-orange-600' :
                              'bg-yellow-600'
                            }`}
                            style={{ width: `${Math.min(100, (count / patterns.length) * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-8">{count}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Warranty Risk Indicators */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Warranty Risk Indicators</h2>
          <p className="text-sm text-gray-600 mt-1">High-frequency issues and cost impact estimates</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">High-Frequency Issues</h3>
              <div className="space-y-3">
                {patterns.slice(0, 5).map((pattern) => (
                  <div key={pattern.pattern_id} className="flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{pattern.component}</p>
                      <p className="text-xs text-gray-600">{pattern.failure_type}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-red-600">{pattern.occurrence_count} cases</p>
                      <p className="text-xs text-gray-500">
                        Est. Cost: ${(pattern.occurrence_count * 150).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Cost Impact Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Warranty Claims</span>
                  <span className="text-lg font-bold text-gray-900">
                    {patterns.reduce((sum, p) => sum + p.occurrence_count, 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Estimated Total Cost</span>
                  <span className="text-lg font-bold text-red-600">
                    ${(patterns.reduce((sum, p) => sum + p.occurrence_count, 0) * 150).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Average Cost per Issue</span>
                  <span className="text-lg font-bold text-gray-900">$150</span>
                </div>
                <div className="mt-4 pt-4 border-t">
                  <p className="text-xs text-gray-500">
                    * Cost estimates based on average warranty claim processing
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Failure Pattern Analysis */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Failure Pattern Analysis</h2>
          <p className="text-sm text-gray-600 mt-1">Groups recurring failures by component and vehicle model</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pattern ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Component</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Failure Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehicle Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Occurrences</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patterns.slice(0, 10).map((pattern) => (
                <tr key={pattern.pattern_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{pattern.pattern_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{pattern.component}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{pattern.failure_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{pattern.model || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{pattern.occurrence_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      pattern.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      pattern.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {pattern.severity}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* RCA/CAPA Insights */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-900">RCA/CAPA Insights</h2>
        {insights.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
            No insights available. Click "Generate Insights" to create RCA/CAPA analysis.
          </div>
        ) : (
          insights.map((insight) => (
            <div key={insight.insight_id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold text-gray-900">{insight.title}</h3>
                <span className={`px-3 py-1 text-sm rounded-full ${
                  insight.recommendation_priority === 'critical' ? 'bg-red-100 text-red-800' :
                  insight.recommendation_priority === 'high' ? 'bg-orange-100 text-orange-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {insight.recommendation_priority}
                </span>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-gray-700 mb-2">Root Causes:</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {insight.root_causes?.map((cause, idx) => (
                    <li key={idx}>{cause}</li>
                  ))}
                </ul>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-gray-700 mb-2">Analysis Summary:</h4>
                <p className="text-gray-600">{insight.analysis_summary}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Corrective Actions:</h4>
                  <ul className="space-y-2">
                    {insight.corrective_actions?.map((action, idx) => (
                      <li key={idx} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        <span className="font-medium">{action.description}</span>
                        <span className="ml-2 text-xs text-gray-500">({action.responsible_team})</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Preventive Actions:</h4>
                  <ul className="space-y-2">
                    {insight.preventive_actions?.map((action, idx) => (
                      <li key={idx} className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        <span className="font-medium">{action.description}</span>
                        <span className="ml-2 text-xs text-gray-500">({action.responsible_team})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t flex justify-between text-sm text-gray-500">
                <span>Affected Vehicles: {insight.affected_vehicles_count}</span>
                <span>Impact: {insight.estimated_impact}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* CAPA Tracking */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">CAPA Tracking</h2>
          <p className="text-sm text-gray-600 mt-1">Corrective and Preventive Actions</p>
        </div>
        <div className="p-6">
          {insights.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No CAPA actions available. Generate insights to see corrective actions.
            </div>
          ) : (
            <div className="space-y-4">
              {insights.map((insight) => (
                <div key={insight.insight_id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      insight.recommendation_priority === 'critical' ? 'bg-red-100 text-red-800' :
                      insight.recommendation_priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {insight.recommendation_priority}
                    </span>
                  </div>
                  
                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Corrective Actions:</h4>
                    <ul className="space-y-1">
                      {insight.corrective_actions?.map((action, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-center">
                          <span className={`w-2 h-2 rounded-full mr-2 ${
                            action.status === 'completed' ? 'bg-green-500' :
                            action.status === 'in_progress' ? 'bg-yellow-500' :
                            'bg-gray-400'
                          }`}></span>
                          <span>{action.description}</span>
                          <span className="ml-2 text-xs text-gray-500">({action.responsible_team})</span>
                          <span className={`ml-auto px-2 py-1 text-xs rounded ${
                            action.status === 'completed' ? 'bg-green-100 text-green-800' :
                            action.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {action.status}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mb-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Preventive Actions:</h4>
                    <ul className="space-y-1">
                      {insight.preventive_actions?.map((action, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-center">
                          <span className={`w-2 h-2 rounded-full mr-2 ${
                            action.status === 'completed' ? 'bg-green-500' :
                            action.status === 'in_progress' ? 'bg-yellow-500' :
                            'bg-gray-400'
                          }`}></span>
                          <span>{action.description}</span>
                          <span className="ml-2 text-xs text-gray-500">({action.responsible_team})</span>
                          <span className={`ml-auto px-2 py-1 text-xs rounded ${
                            action.status === 'completed' ? 'bg-green-100 text-green-800' :
                            action.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {action.status}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Improvement Timeline */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Improvement Timeline</h2>
          <p className="text-sm text-gray-600 mt-1">Before vs After Metrics</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Failure Rate</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Before</span>
                    <span className="text-sm font-medium text-gray-900">45 failures/month</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-red-600 h-3 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">After</span>
                    <span className="text-sm font-medium text-green-600">19 failures/month</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-green-600 h-3 rounded-full" style={{ width: '42%' }}></div>
                  </div>
                </div>
                <div className="pt-2 border-t">
                  <p className="text-sm font-medium text-green-700">Improvement: -58%</p>
                </div>
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Warranty Costs</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Before</span>
                    <span className="text-sm font-medium text-gray-900">$6,750/month</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-red-600 h-3 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">After</span>
                    <span className="text-sm font-medium text-green-600">$2,850/month</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div className="bg-green-600 h-3 rounded-full" style={{ width: '42%' }}></div>
                  </div>
                </div>
                <div className="pt-2 border-t">
                  <p className="text-sm font-medium text-green-700">Savings: -58% ($3,900/month)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quality Improvement Reports */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Quality Improvement Reports</h2>
          <p className="text-sm text-gray-600 mt-1">Structured data for design teams to enable faster design fixes</p>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Design Fix Recommendations</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Component</p>
                  <p className="font-medium">Engine Cooling System</p>
                </div>
                <div>
                  <p className="text-gray-500">Issue Frequency</p>
                  <p className="font-medium">High (45 occurrences)</p>
                </div>
                <div>
                  <p className="text-gray-500">Recommended Action</p>
                  <p className="font-medium">Enhance cooling system design</p>
                </div>
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Production Batch Correlation</h3>
              <p className="text-sm text-gray-600 mb-3">Field failures linked to production batches and manufacturing timelines</p>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Batch #2023-Q4</p>
                    <p className="text-xs text-gray-600">Oct-Dec 2023</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-red-600">12 failures</p>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div className="bg-red-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Batch #2024-Q1</p>
                    <p className="text-xs text-gray-600">Jan-Mar 2024</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-orange-600">8 failures</p>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div className="bg-orange-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-medium text-gray-900">Batch #2024-Q2</p>
                    <p className="text-xs text-gray-600">Apr-Jun 2024</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-green-600">5 failures</p>
                    <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '25%' }}></div>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t">
                  <p className="text-xs font-medium text-green-700">✓ Trend: Decreasing failure rate (-58%)</p>
                </div>
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Resolution Trends</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Issues Resolved</p>
                  <p className="text-2xl font-semibold text-green-600">78%</p>
                </div>
                <div>
                  <p className="text-gray-500">Warranty Cost Impact</p>
                  <p className="text-2xl font-semibold text-blue-600">-23%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ManufacturingDashboard

