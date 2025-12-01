import React, {useState, useEffect} from "react";
import AlertsList from "./components/AlertsList";
import PlanView from "./components/PlanView";
import LogsView from "./components/LogsView";
import MapView from "./components/MapView";
import RiskBadge from "./components/RiskBadge";



const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function computeUiRisk(alert) {
  // small heuristic to show in UI quickly
  if (!alert) return 0.2;
  const conf = Number(alert.confidence || 0.5);
  // sample heuristic: severity score from payload if present
  const severity = alert.payload?.severity === "high" ? 0.9 : alert.payload?.severity === "medium" ? 0.6 : 0.3;
  return Math.min(1, conf * severity);
}


function App(){
  const [alerts, setAlerts] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  async function pollAlerts(){
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/poll_alerts`);
      const arr = await res.json();
      setAlerts(arr || []);
    } catch(e) {
      console.error(e);
      setAlerts([]);
    } finally { setLoading(false); }
  }

  async function createPlan(alertId){
  setLoading(true);
  try {
    const url = `${API_BASE}/api/plan/${alertId}`;
    console.log("[DEBUG] createPlan POST", url);
    const res = await fetch(url, { method: "POST" });
    console.log("[DEBUG] createPlan status", res.status, res.statusText);
    const text = await res.text();
    let plan;
    try { plan = JSON.parse(text); } catch(e) {
      console.error("[DEBUG] createPlan parse failed:", e, "raw:", text);
      plan = null;
    }
    if (!plan) {
      // show user-friendly message
      alert("Plan creation failed — no plan returned. Check backend logs.");
      setSelectedPlan(null);
      return;
    }
    console.log("[DEBUG] createPlan response plan:", plan);
    setSelectedPlan(plan);
    // refresh incidents list (optional)
    await pollAlerts();
  } catch(e) {
    console.error("createPlan failed:", e);
    alert("Plan request failed: " + (e.message || e));
  } finally {
    setLoading(false);
  }
}


  useEffect(()=> { pollAlerts(); }, []);

   return (
  <div className="min-h-screen bg-slate-50 p-6">
    <header className="max-w-7xl mx-auto mb-6">
      <h1 className="text-3xl font-bold">Disaster Relief Coordinator — Demo</h1>
      <p className="text-sm text-slate-600">Live alerts, risk scoring, and plans</p>
    </header>

    <main className="max-w-7xl mx-auto grid grid-cols-4 gap-6">

      {/* Left column: map */}
      <div className="col-span-2 bg-white p-4 rounded shadow">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Map</h2>
          <div>
            <button onClick={pollAlerts} className="text-sm text-blue-600 mr-3">
              {loading ? "..." : "Refresh"}
            </button>
          </div>
        </div>
        <MapView incidents={alerts} onSelect={(inc)=>createPlan(inc.id)} />
      </div>

      {/* Middle column: alerts (scrollable) */}
      <div className="col-span-1 bg-white p-4 rounded shadow flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Alerts</h2>
          <div className="text-xs text-slate-500">Total: {alerts.length}</div>
        </div>

        {/* Scrollable alerts list */}
        <div className="overflow-y-auto pr-2" style={{ maxHeight: "calc(100vh - 240px)" }}>
          <div className="space-y-3">
            {alerts.map(a => (
              <div key={a.id} className="p-3 border rounded flex justify-between items-start">
                <div>
                  <div className="font-medium">{a.type} — {a.location}</div>
                  <div className="text-xs text-slate-500">
                    conf: {a.confidence} · {new Date(a.time).toLocaleString()}
                  </div>
                  <div className="mt-2">
                    <RiskBadge risk={a._ui_risk ?? computeUiRisk(a)} />
                  </div>
                </div>
                <div>
                  <button
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm"
                    onClick={() => createPlan(a.id)}
                  >
                    Plan
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right column: plan & logs */}
      <div className="col-span-1 bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-3">Plan</h2>
        <PlanView plan={selectedPlan} />
        <hr className="my-3" />
        <h3 className="font-semibold">Logs</h3>
        <LogsView />
      </div>

    </main>
  </div>
);

}

export default App;
