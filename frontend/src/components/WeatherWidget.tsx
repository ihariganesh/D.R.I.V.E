import {
    CloudIcon,
    SunIcon,
    CloudArrowDownIcon,
    ExclamationCircleIcon
} from '@heroicons/react/24/outline'

interface WeatherData {
    city: string
    condition: string
    temperature: number
    humidity: number
    visibility: number
    precipitation: number
    wind_speed: number
    timestamp: string
}

interface WeatherWidgetProps {
    weather: WeatherData | null
}

export default function WeatherWidget({ weather }: WeatherWidgetProps) {
    if (!weather) return null

    const getIcon = (condition: string) => {
        switch (condition.toLowerCase()) {
            case 'clear':
                return <SunIcon className="w-8 h-8 text-yellow-500" />
            case 'rain':
            case 'heavy_rain':
                return <CloudArrowDownIcon className="w-8 h-8 text-blue-500" />
            case 'cloudy':
                return <CloudIcon className="w-8 h-8 text-gray-500" />
            default:
                return <ExclamationCircleIcon className="w-8 h-8 text-orange-500" />
        }
    }

    const getImpactColor = (condition: string) => {
        switch (condition.toLowerCase()) {
            case 'clear': return 'text-success-500'
            case 'rain': return 'text-warning-500'
            case 'heavy_rain':
            case 'fog': return 'text-danger-500'
            default: return 'text-gray-500'
        }
    }

    return (
        <div className="card glass-morphism overflow-hidden relative">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-lg font-semibold text-gray-900">{weather.city}</h3>
                    <p className="text-sm text-gray-500 capitalize">{weather.condition}</p>
                </div>
                <div className="bg-white/50 p-2 rounded-xl backdrop-blur-sm shadow-inner">
                    {getIcon(weather.condition)}
                </div>
            </div>

            <div className="mt-6 flex items-baseline">
                <span className="text-4xl font-bold text-gray-900">{Math.round(weather.temperature)}°</span>
                <span className="text-gray-500 ml-1 text-lg">C</span>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="bg-white/30 p-2 rounded-lg backdrop-blur-xs">
                    <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Visibility</p>
                    <p className="text-sm font-semibold">{(weather.visibility / 1000).toFixed(1)} km</p>
                </div>
                <div className="bg-white/30 p-2 rounded-lg backdrop-blur-xs">
                    <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Precipitation</p>
                    <p className="text-sm font-semibold">{weather.precipitation} mm</p>
                </div>
                <div className="bg-white/30 p-2 rounded-lg backdrop-blur-xs">
                    <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Wind</p>
                    <p className="text-sm font-semibold">{weather.wind_speed.toFixed(1)} km/h</p>
                </div>
                <div className="bg-white/30 p-2 rounded-lg backdrop-blur-xs">
                    <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Humidity</p>
                    <p className="text-sm font-semibold">{weather.humidity}%</p>
                </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                <span className="text-xs text-gray-500 font-medium">Traffic Impact</span>
                <span className={`text-xs font-bold uppercase tracking-widest ${getImpactColor(weather.condition)}`}>
                    {weather.condition === 'clear' ? 'Minimal' : weather.condition === 'rain' ? 'Moderate' : 'High'}
                </span>
            </div>
        </div>
    )
}
