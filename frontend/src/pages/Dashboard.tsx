import { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  CameraIcon, 
  ExclamationTriangleIcon, 
  TruckIcon, 
  SignalIcon 
} from '@heroicons/react/24/outline'

interface DashboardStats {
  system_status: string
  active_cameras: number
  active_events: number
  emergency_vehicles_active: number
  green_wave_protocols_active: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    // Refresh every 5 seconds
    const interval = setInterval(fetchDashboardData, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('/api/v1/dashboard/overview', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  const statCards = [
    {
      name: 'Active Cameras',
      value: stats?.active_cameras || 0,
      icon: CameraIcon,
      color: 'bg-primary-500',
    },
    {
      name: 'Active Events',
      value: stats?.active_events || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-warning-500',
    },
    {
      name: 'Emergency Vehicles',
      value: stats?.emergency_vehicles_active || 0,
      icon: TruckIcon,
      color: 'bg-danger-500',
    },
    {
      name: 'Green Wave Active',
      value: stats?.green_wave_protocols_active || 0,
      icon: SignalIcon,
      color: 'bg-success-500',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Traffic Control Dashboard</h1>
        <p className="text-gray-600 mt-2">Real-time monitoring and control</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">{stat.name}</p>
                  <p className="text-3xl font-bold mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">AI Control</span>
              <span className="badge badge-success">Active</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Green Wave Protocol</span>
              <span className="badge badge-success">Enabled</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Digital Twin</span>
              <span className="badge badge-success">Online</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-start">
              <div className="w-2 h-2 bg-success-500 rounded-full mt-1.5 mr-3"></div>
              <div>
                <p className="font-medium">Green Wave activated for AMB001</p>
                <p className="text-gray-500 text-xs">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-2 h-2 bg-warning-500 rounded-full mt-1.5 mr-3"></div>
              <div>
                <p className="font-medium">Speed limit adjusted on Main Street</p>
                <p className="text-gray-500 text-xs">5 minutes ago</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-2 h-2 bg-danger-500 rounded-full mt-1.5 mr-3"></div>
              <div>
                <p className="font-medium">Congestion detected on Brigade Road</p>
                <p className="text-gray-500 text-xs">8 minutes ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
