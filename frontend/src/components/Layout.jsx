import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../services/AuthContext'
import { useTheme } from '../services/ThemeContext'

const Layout = ({ children }) => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-transparent text-slate-900 dark:text-slate-100">
      {/* Top Navigation - clean, professional */}
      <nav className="sticky top-0 z-40 bg-white/95 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-base sm:text-lg font-semibold tracking-tight text-slate-900 dark:text-slate-50">
                  Connected Intelligence Hub
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {/* Dashboard - Only show for customers (admin has separate System dashboard) */}
                {user?.role === 'customer' && (
                  <Link
                    to="/"
                    className={`${
                      isActive('/')
                        ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                        : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    Dashboard
                  </Link>
                )}
                {/* Vehicle Monitoring & Service History - Customers only */}
                {user?.role === 'customer' && (
                  <>
                    <Link
                      to="/monitoring"
                      className={`${
                        isActive('/monitoring')
                          ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                          : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      Vehicle Monitoring
                    </Link>
                    <Link
                      to="/service-history"
                      className={`${
                        isActive('/service-history')
                          ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                          : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      Service History
                    </Link>
                  </>
                )}
                {user?.role === 'service_center' && (
                  <>
                    <Link
                      to="/service-center"
                      className={`${
                        isActive('/service-center') ||
                        isActive('/service-center/bookings') ||
                        isActive('/service-center/ongoing') ||
                        isActive('/service-center/technicians')
                          ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                          : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/service-center/reviews"
                      className={`${
                        isActive('/service-center/reviews')
                          ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                          : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      Reviews
                    </Link>
                  </>
                )}
                {(user?.role === 'manufacturing' || user?.role === 'admin') && (
                  <Link
                    to="/manufacturing"
                    className={`${
                      isActive('/manufacturing')
                        ? 'border-primary-500 text-slate-900 dark:text-slate-50'
                        : 'border-transparent text-gray-500 dark:text-slate-400 hover:border-gray-300 hover:text-gray-800 dark:hover:text-slate-100'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    Manufacturing Insights
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Simple theme toggle */}
              <button
                onClick={toggleTheme}
                className="inline-flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
              >
                {theme === 'dark' ? (
                  <>
                    <span className="text-amber-300 text-base">☾</span>
                    <span>Dark</span>
                  </>
                ) : (
                  <>
                    <span className="text-sky-500 text-base">☀</span>
                    <span>Light</span>
                  </>
                )}
              </button>

              <div className="hidden md:flex flex-col items-end mr-2">
                <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">{user?.username}</span>
                <span className="text-[11px] uppercase text-slate-400 dark:text-slate-500">{user?.role}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 space-y-6">
        {children}
      </main>
    </div>
  )
}

export default Layout

