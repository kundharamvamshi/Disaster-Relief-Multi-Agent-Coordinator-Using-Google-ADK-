// src/components/RiskBadge.jsx
import React from "react";

export default function RiskBadge({ risk }) {
  if (risk == null) return null;
  const r = Number(risk);
  const color = r >= 0.85 ? "bg-red-600" : r >= 0.6 ? "bg-amber-500" : r >= 0.35 ? "bg-green-600" : "bg-blue-600";
  const label = r >= 0.85 ? "Critical" : r >= 0.6 ? "High" : r >= 0.35 ? "Medium" : "Low";
  return (
    <span className={`text-white px-2 py-1 text-xs rounded ${color}`}>
      {label} ({(r * 100).toFixed(0)}%)
    </span>
  );
}
