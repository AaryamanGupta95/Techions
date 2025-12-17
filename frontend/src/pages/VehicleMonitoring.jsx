import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { vehicleService, predictionService } from '../services/api'
import { useAuth } from '../services/AuthContext'

const VehicleMonitoring = () => {
  const { user } = useAuth()
  const [vehicles, setVehicles] = useState([])
  const [selectedVehicle, setSelectedVehicle] = useState(null)
  const [telemetry, setTelemetry] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadCustomerVehicles()
  }, [])

  useEffect(() => {
    if (selectedVehicle) {
      // Clear previous prediction when switching vehicles
      setPrediction(null)
      setTelemetry([])
      loadTelemetry()
    }
  }, [selectedVehicle])

  const loadCustomerVehicles = async () => {
    setLoading(true)
    try {
      // Map username "customer" to customer_id "CUST_001" for compatibility
      const rawCustomerId = user?.customer_id || user?.username || 'CUST_001'
      const customerId = rawCustomerId === 'customer' ? 'CUST_001' : rawCustomerId
      const response = await vehicleService.getCustomerVehicles(customerId)
      let vehiclesList = response.vehicles || []
      
      // If no vehicles, show demo data for prototype
      if (vehiclesList.length === 0) {
        vehiclesList = getDemoVehicles(customerId)
        setVehicles(vehiclesList)
      } else {
        setVehicles(vehiclesList)
      }
      
      // Auto-select first vehicle if available
      if (vehiclesList.length > 0 && !selectedVehicle) {
        setSelectedVehicle(vehiclesList[0])
      }
    } catch (error) {
      console.error('Error loading vehicles:', error)
      // Show demo data on error for prototype
      const rawCustomerId = user?.customer_id || user?.username || 'CUST_001'
      const customerId = rawCustomerId === 'customer' ? 'CUST_001' : rawCustomerId
      const demoVehicles = getDemoVehicles(customerId)
      setVehicles(demoVehicles)
      if (demoVehicles.length > 0) {
        setSelectedVehicle(demoVehicles[0])
      }
    } finally {
      setLoading(false)
    }
  }

  const getDemoVehicles = (customerId) => {
    return [
      {
        vin: 'VIN001',
        vehicle_name: 'My Hero Bike',
        plate_number: 'MH-12-AB-1234',
        model: 'Hero Splendor',
        manufacturer: 'Hero',
        year: 2023,
        customer_id: customerId
      },
      {
        vin: 'VIN002',
        vehicle_name: 'Family Car',
        plate_number: 'MH-12-CD-5678',
        model: 'Mahindra XUV300',
        manufacturer: 'Mahindra',
        year: 2022,
        customer_id: customerId
      }
    ]
  }

  const loadTelemetry = async () => {
    if (!selectedVehicle) return
    
    setLoading(true)
    try {
      const response = await vehicleService.getTelemetry(selectedVehicle.vin)
      let telemetryData = response.telemetry || []
      
      // Backend already sorts by timestamp descending, but ensure consistency
      // Sort by timestamp descending (most recent first) to ensure consistency
      telemetryData.sort((a, b) => {
        const dateA = new Date(a.timestamp || a.created_at || 0)
        const dateB = new Date(b.timestamp || b.created_at || 0)
        return dateB - dateA
      })
      
      // If no telemetry data, generate sample data
      if (telemetryData.length === 0) {
        telemetryData = generateSampleTelemetry(selectedVehicle.vin)
        setTelemetry(telemetryData)
      } else {
        setTelemetry(telemetryData)
      }
    } catch (error) {
      console.error('Error loading telemetry:', error)
      // Generate sample data on error
      const sampleData = generateSampleTelemetry(selectedVehicle.vin)
      setTelemetry(sampleData)
    } finally {
      setLoading(false)
    }
  }

  // Helper function to get latest health score - EXACTLY matches CustomerDashboard logic
  const getLatestHealthScore = (vin) => {
    if (!vin || telemetry.length === 0) {
      // Generate sample health using same logic as CustomerDashboard
      const vinNumber = vin?.match(/\d+/)?.[0] || '001'
      let baseHealth
      if (vinNumber === '001' || vin?.includes('VIN001')) {
        baseHealth = 48.0
      } else if (vinNumber === '002' || vin?.includes('VIN002')) {
        baseHealth = 72.0
      } else {
        baseHealth = 82.0
      }
      // Use VIN as seed for consistent variation (same as CustomerDashboard)
      const vinSeed = vin?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0
      const variation = (vinSeed % 7) - 3  // -3 to +3 variation
      const healthScore = Math.max(30, Math.min(100, baseHealth + variation))
      return Math.round(healthScore * 10) / 10
    }
    // Get the most recent telemetry record (already sorted descending)
    const latest = telemetry[0]
    // If health_score exists, use it; otherwise generate sample
    if (latest.health_score !== undefined && latest.health_score !== null) {
      return latest.health_score
    }
    // Fallback to sample generation if health_score is missing
    const vinNumber = vin?.match(/\d+/)?.[0] || '001'
    let baseHealth
    if (vinNumber === '001' || vin?.includes('VIN001')) {
      baseHealth = 48.0
    } else if (vinNumber === '002' || vin?.includes('VIN002')) {
      baseHealth = 72.0
    } else {
      baseHealth = 82.0
    }
    const vinSeed = vin?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0
    const variation = (vinSeed % 7) - 3
    const healthScore = Math.max(30, Math.min(100, baseHealth + variation))
    return Math.round(healthScore * 10) / 10
  }

  const generateSampleTelemetry = (vin) => {
    // Don't generate random data - this should only be used as last resort
    // The backend should provide consistent data from MongoDB
    const now = new Date()
    const data = []
    
    // Use VIN to determine consistent base health (same as backend)
    // Extract number from VIN to determine health level
    const vinNumber = vin.match(/\d+/)?.[0] || '001'
    let baseHealth
    if (vinNumber === '001' || vin.includes('VIN001')) {
      baseHealth = 48.0  // Low health for first vehicle
    } else if (vinNumber === '002' || vin.includes('VIN002')) {
      baseHealth = 72.0  // Medium health for second vehicle
    } else {
      baseHealth = 82.0  // Good health for others
    }
    
    // Use VIN as seed for consistent but unique data per vehicle
    const vinSeed = vin.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
    
    for (let i = 0; i < 20; i++) {
      const timestamp = new Date(now.getTime() - i * 60000) // Every minute
      
      // Small consistent variation based on VIN seed (not random)
      const variation = ((vinSeed + i) % 7) - 3  // -3 to +3 variation
      const healthScore = Math.max(30, Math.min(100, baseHealth + variation))
      
      // Generate telemetry that correlates with health (consistent per VIN)
      let engineTemp, oilPressure, batteryVoltage, vibrationLevel, errorCodes, anomalyDetected, predictionRisk
      
      if (healthScore < 50) {
        // Low health vehicle characteristics
        engineTemp = 95 + ((vinSeed + i) % 8)  // 95-102
        oilPressure = 28 + ((vinSeed + i) % 5)  // 28-32
        batteryVoltage = 11.9 + ((vinSeed + i) % 3) * 0.1  // 11.9-12.1
        vibrationLevel = 0.85 + ((vinSeed + i) % 2) * 0.1  // 0.85-0.95
        errorCodes = ['P0300', 'P0171']
        anomalyDetected = true
        predictionRisk = 0.65 + ((vinSeed + i) % 10) * 0.01  // 0.65-0.74
      } else if (healthScore < 70) {
        // Medium health vehicle characteristics
        engineTemp = 88 + ((vinSeed + i) % 6)  // 88-93
        oilPressure = 32 + ((vinSeed + i) % 6)  // 32-37
        batteryVoltage = 12.2 + ((vinSeed + i) % 3) * 0.1  // 12.2-12.4
        vibrationLevel = 0.65 + ((vinSeed + i) % 2) * 0.1  // 0.65-0.75
        errorCodes = []
        anomalyDetected = (vinSeed + i) % 3 === 0  // Occasional anomalies
        predictionRisk = 0.35 + ((vinSeed + i) % 10) * 0.01  // 0.35-0.44
      } else {
        // Good health vehicle characteristics
        engineTemp = 85 + ((vinSeed + i) % 5)  // 85-89
        oilPressure = 38 + ((vinSeed + i) % 5)  // 38-42
        batteryVoltage = 12.6 + ((vinSeed + i) % 2) * 0.1  // 12.6-12.7
        vibrationLevel = 0.55 + ((vinSeed + i) % 2) * 0.05  // 0.55-0.60
        errorCodes = []
        anomalyDetected = false
        predictionRisk = 0.15 + ((vinSeed + i) % 5) * 0.01  // 0.15-0.19
      }
      
      data.push({
        vin: vin,
        timestamp: timestamp.toISOString(),
        engine_temperature: Math.round(engineTemp * 10) / 10,
        oil_pressure: Math.round(oilPressure * 10) / 10,
        vibration_level: Math.round(vibrationLevel * 100) / 100,
        battery_voltage: Math.round(batteryVoltage * 100) / 100,
        speed: 40 + ((vinSeed + i) % 30),  // Different speeds per vehicle
        mileage: 15000 + i * 10,
        health_score: Math.round(healthScore * 10) / 10,
        prediction_risk: Math.round(predictionRisk * 1000) / 1000,
        error_codes: errorCodes,
        anomaly_detected: anomalyDetected
      })
    }
    return data.reverse()
  }

  const runPrediction = async () => {
    if (!selectedVehicle) {
      alert('Please select a vehicle first')
      return
    }
    
    setLoading(true)
    setPrediction(null)
    
    try {
      // First ensure we have telemetry data
      if (telemetry.length === 0) {
        await loadTelemetry()
      }
      
      // Run prediction - ensure we have telemetry data
      if (telemetry.length === 0) {
        throw new Error('No telemetry data available for prediction')
      }
      
      // Run prediction API call
      const response = await predictionService.predict({ vin: selectedVehicle.vin })
      
      // Check if response is valid
      if (response && response.status === 'success') {
        setPrediction({
          risk_score: response.risk_score || 0,
          recommendation: response.recommendation || 'Analysis complete',
          predicted_failure_window: response.predicted_failure_window || 'No immediate risk detected',
          health_score: response.health_score
        })
      } else if (response && response.risk_score !== undefined) {
        // Handle case where response doesn't have status but has risk_score
        setPrediction({
          risk_score: response.risk_score || 0,
          recommendation: response.recommendation || 'Analysis complete',
          predicted_failure_window: response.predicted_failure_window || 'No immediate risk detected',
          health_score: response.health_score
        })
      } else {
        throw new Error('Invalid prediction response')
      }
    } catch (error) {
      console.error('Error running prediction:', error)
      // Create fallback prediction based on telemetry data
      const latestTelemetry = telemetry[0] || {}
      const healthScore = latestTelemetry.health_score || 75
      
      // Calculate risk based on health score (inverse relationship)
      let riskScore = 0
      if (healthScore < 40) {
        riskScore = 0.75
      } else if (healthScore < 60) {
        riskScore = 0.6
      } else if (healthScore < 70) {
        riskScore = 0.4
      } else if (healthScore < 80) {
        riskScore = 0.25
      } else {
        riskScore = 0.1
      }
      
      // Also consider other telemetry factors
      if (latestTelemetry.engine_temperature > 100) riskScore += 0.15
      if (latestTelemetry.oil_pressure < 30) riskScore += 0.15
      if (latestTelemetry.battery_voltage < 12.0) riskScore += 0.1
      if (latestTelemetry.anomaly_detected) riskScore += 0.1
      
      riskScore = Math.min(1.0, riskScore)
      
      setPrediction({
        risk_score: riskScore,
        recommendation: riskScore > 0.6 
          ? 'High risk detected. Immediate service recommended within 3-5 days.'
          : riskScore > 0.4
          ? 'Moderate risk detected. Schedule service within 7-10 days.'
          : riskScore > 0.3
          ? 'Low risk detected. Schedule preventive maintenance within 14-21 days.'
          : 'Vehicle is in good condition. Regular maintenance recommended.',
        predicted_failure_window: riskScore > 0.6 
          ? '3-5 days'
          : riskScore > 0.4
          ? '7-14 days'
          : riskScore > 0.3
          ? '30-60 days'
          : 'No immediate risk detected',
        health_score: healthScore
      })
    } finally {
      setLoading(false)
    }
  }

  const chartData = telemetry.slice(0, 20).map((t) => ({
    time: new Date(t.timestamp).toLocaleTimeString(),
    temp: t.engine_temperature,
    pressure: t.oil_pressure,
    vibration: t.vibration_level,
    voltage: t.battery_voltage,
    health: t.health_score,
  }))

  const latestTelemetry = telemetry[0] || {}

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Vehicle Monitoring</h1>

      {/* Vehicle Selection Dropdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Vehicle</h2>
        {vehicles.length === 0 ? (
          <p className="text-gray-500">No vehicles found. Please add a vehicle from the Dashboard.</p>
        ) : (
          <select
            value={selectedVehicle?.vin || ''}
            onChange={(e) => {
              const vehicle = vehicles.find(v => v.vin === e.target.value)
              setSelectedVehicle(vehicle || null)
            }}
            className="w-full md:w-1/2 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">-- Select a vehicle --</option>
            {vehicles.map((vehicle) => (
              <option key={vehicle.vin} value={vehicle.vin}>
                {vehicle.vehicle_name || vehicle.model} ({vehicle.plate_number})
              </option>
            ))}
          </select>
        )}
      </div>

      {selectedVehicle && (
        <>
          {/* Vehicle Info Header */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedVehicle.vehicle_name || selectedVehicle.model}
                </h2>
                <p className="text-gray-600">Plate Number: {selectedVehicle.plate_number}</p>
                <p className="text-sm text-gray-500">{selectedVehicle.model} • {selectedVehicle.manufacturer} • {selectedVehicle.year}</p>
              </div>
              <button
                onClick={runPrediction}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Analyzing...' : 'Run Health Analysis'}
              </button>
            </div>
          </div>

          {/* Current Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Engine Temperature</p>
              <p className="text-2xl font-semibold text-gray-900">
                {latestTelemetry.engine_temperature?.toFixed(1) || 'N/A'}°C
              </p>
              <p className={`text-sm mt-2 ${latestTelemetry.engine_temperature > 100 ? 'text-red-600' : 'text-green-600'}`}>
                {latestTelemetry.engine_temperature > 100 ? 'High' : 'Normal'}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Oil Pressure</p>
              <p className="text-2xl font-semibold text-gray-900">
                {latestTelemetry.oil_pressure?.toFixed(1) || 'N/A'} PSI
              </p>
              <p className={`text-sm mt-2 ${latestTelemetry.oil_pressure < 30 ? 'text-red-600' : 'text-green-600'}`}>
                {latestTelemetry.oil_pressure < 30 ? 'Low' : 'Normal'}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Health Score</p>
              {(() => {
                const healthScore = getLatestHealthScore(selectedVehicle?.vin)
                return (
                  <>
                    <p className="text-2xl font-semibold text-gray-900">
                      {healthScore.toFixed(1)}%
                    </p>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          healthScore > 80 ? 'bg-green-600' :
                          healthScore > 60 ? 'bg-yellow-600' : 'bg-red-600'
                        }`}
                        style={{ width: `${healthScore}%` }}
                      ></div>
                    </div>
                  </>
                )
              })()}
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-500">Failure Risk</p>
              <p className="text-2xl font-semibold text-gray-900">
                {prediction?.risk_score !== undefined 
                  ? (prediction.risk_score * 100).toFixed(1) 
                  : latestTelemetry.prediction_risk !== undefined
                  ? (latestTelemetry.prediction_risk * 100).toFixed(1) 
                  : '--'}%
              </p>
              <p className={`text-sm mt-2 ${
                (prediction?.risk_score !== undefined ? prediction.risk_score : latestTelemetry.prediction_risk || 0) > 0.7 ? 'text-red-600' :
                (prediction?.risk_score !== undefined ? prediction.risk_score : latestTelemetry.prediction_risk || 0) > 0.5 ? 'text-yellow-600' : 
                (prediction?.risk_score !== undefined ? prediction.risk_score : latestTelemetry.prediction_risk || 0) > 0.3 ? 'text-orange-600' : 'text-green-600'
              }`}>
                {prediction?.recommendation || (prediction === null ? 'Click "Run Health Analysis" to check' : 'Analysis pending')}
              </p>
            </div>
          </div>

          {/* Prediction Result */}
          {prediction && prediction.risk_score !== undefined && (
            <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${
              prediction.risk_score > 0.7 ? 'border-red-500' :
              prediction.risk_score > 0.5 ? 'border-yellow-500' : 
              prediction.risk_score > 0.3 ? 'border-orange-500' : 'border-green-500'
            }`}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Health Analysis Result</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Risk Score</p>
                  <p className={`text-3xl font-bold ${
                    prediction.risk_score > 0.7 ? 'text-red-600' :
                    prediction.risk_score > 0.5 ? 'text-yellow-600' : 
                    prediction.risk_score > 0.3 ? 'text-orange-600' : 'text-green-600'
                  }`}>
                    {(prediction.risk_score * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-sm text-gray-500">Recommendation</p>
                  <p className="text-lg font-medium text-gray-900">{prediction.recommendation}</p>
                </div>
                {prediction.predicted_failure_window && (
                  <div className="md:col-span-3">
                    <p className="text-sm text-gray-500">Predicted Failure Window</p>
                    <p className="text-lg font-medium text-gray-900">{prediction.predicted_failure_window}</p>
                  </div>
                )}
                {prediction.health_score !== undefined && (
                  <div>
                    <p className="text-sm text-gray-500">Current Health Score</p>
                    <p className="text-2xl font-semibold text-gray-900">{prediction.health_score.toFixed(1)}%</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Charts */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Telemetry Trends</h2>
            {telemetry.length > 0 ? (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="temp" stroke="#ef4444" name="Engine Temp (°C)" />
                  <Line yAxisId="left" type="monotone" dataKey="pressure" stroke="#3b82f6" name="Oil Pressure (PSI)" />
                  <Line yAxisId="right" type="monotone" dataKey="vibration" stroke="#f59e0b" name="Vibration" />
                  <Line yAxisId="right" type="monotone" dataKey="voltage" stroke="#10b981" name="Battery (V)" />
                  <Line yAxisId="right" type="monotone" dataKey="health" stroke="#8b5cf6" name="Health Score" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-gray-500 py-8">No telemetry data available</p>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default VehicleMonitoring
