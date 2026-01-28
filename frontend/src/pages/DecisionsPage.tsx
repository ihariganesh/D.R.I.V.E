export default function DecisionsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">AI Decisions (XAI Dashboard)</h1>
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Explainable AI</h2>
        <p className="text-gray-600 mb-4">
          View AI decisions with detailed explanations showing WHAT the AI decided and WHY
        </p>
        <div className="bg-primary-50 p-4 rounded-lg">
          <p className="font-medium">Example Decision:</p>
          <p className="text-sm mt-2">
            "Speed reduced to 40 km/h because Camera 4 detected debris 500m ahead. 
            High pedestrian activity observed."
          </p>
        </div>
      </div>
    </div>
  )
}
