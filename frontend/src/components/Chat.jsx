import React, { useState, useEffect, useRef } from 'react'
import { engagementService, vehicleService, predictionService } from '../services/api'

const Chat = ({ vin, customerId, alerts = [] }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize chat - NO alerts, only welcome message
  useEffect(() => {
    if (!initialized && customerId) {
      // Simple welcome message - chatbot should NOT show alerts
      const botMessage = {
        role: 'bot',
        content: `Hello! I'm your vehicle assistant. I can help you with:\n\n` +
                 `• Vehicle health status\n` +
                 `• Service scheduling\n` +
                 `• Maintenance questions\n` +
                 `• General vehicle information\n\n` +
                 `How can I help you today?`,
        timestamp: new Date()
      }
      setMessages([botMessage])
      setInitialized(true)
    }
  }, [customerId, initialized])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input, timestamp: new Date() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await engagementService.chat({
        message: input,
        customer_id: customerId,
        vin: vin,
      })

      const botMessage = {
        role: 'bot',
        content: response.response,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        role: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Chat Header */}
      <div className="bg-primary-600 text-white p-4 rounded-t-lg">
        <h3 className="font-semibold">Vehicle Assistant</h3>
        <p className="text-sm text-primary-100">Ask me about your vehicle</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Start a conversation about your vehicle</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : msg.isAlert
                  ? 'bg-yellow-50 border-2 border-yellow-300 text-gray-800'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-line">{msg.content}</p>
              <p className={`text-xs mt-1 ${msg.role === 'user' ? 'opacity-70' : 'text-gray-500'}`}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default Chat

