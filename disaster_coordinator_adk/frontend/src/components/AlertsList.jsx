import React from "react";

export default function AlertsList({alerts, onPlan}){
  if(!alerts || alerts.length===0) return <p className="text-sm text-slate-500">No alerts yet</p>;
  return (
    <ul className="space-y-3">
      {alerts.map(a => (
        <li key={a.id} className="p-3 border rounded">
          <div className="flex justify-between items-start">
            <div>
              <div className="font-medium">{a.type} — {a.location}</div>
              <div className="text-xs text-slate-500">conf: {a.confidence} · {new Date(a.time).toLocaleString()}</div>
            </div>
            <div className="flex flex-col items-end">
              <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm" onClick={()=>onPlan(a.id)}>Plan</button>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
