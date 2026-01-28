import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  CameraIcon, 
  ExclamationTriangleIcon,
  TruckIcon,
  CpuChipIcon,
  BeakerIcon,
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline'

interface LayoutProps {
  children: ReactNode
  onLogout: () => void
}

export default function Layout({ children, onLogout }: LayoutProps) {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Cameras', href: '/cameras', icon: CameraIcon },
    { name: 'Events', href: '/events', icon: ExclamationTriangleIcon },
    { name: 'Emergency', href: '/emergency', icon: TruckIcon },
    { name: 'AI Decisions', href: '/decisions', icon: CpuChipIcon },
    { name: 'Simulations', href: '/simulations', icon: BeakerIcon },
  ]

  const handleLogout = () => {
    localStorage.removeItem('token')
    onLogout()
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-primary-900 text-white">
        <div className="flex items-center justify-center h-16 bg-primary-800">
          <h1 className="text-2xl font-bold">D.R.I.V.E</h1>
        </div>
        
        <nav className="mt-8">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-800 text-white border-l-4 border-white'
                    : 'text-primary-100 hover:bg-primary-800'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            )
          })}
        </nav>
        
        <div className="absolute bottom-0 w-full p-4">
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-6 py-3 text-sm font-medium text-primary-100 hover:bg-primary-800 transition-colors rounded-lg"
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="ml-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
