export default function SimulationsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Digital Twin Simulations</h1>
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4">Run Simulation Before Override</h2>
        <p className="text-gray-600 mb-4">
          Test manual overrides with 5-second predictive simulation
        </p>
        <button className="btn-primary">Run New Simulation</button>
      </div>
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Recent Simulations</h2>
        <p className="text-gray-600">View simulation history and predictions</p>
      </div>
    </div>
  )
}
