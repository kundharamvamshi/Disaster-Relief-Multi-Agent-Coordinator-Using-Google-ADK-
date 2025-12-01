import React from "react";

export default function PlanView({ plan }) {
  if (!plan) {
    return <div className="text-sm text-slate-500">No plan selected</div>;
  }

  return (
    <div>
      <div className="mb-2 text-sm text-slate-600">Risk: {(plan.risk ?? 0).toFixed(2)}</div>

      <div className="mb-3">
        <h3 className="font-semibold">Tasks</h3>
        {(!plan.tasks || plan.tasks.length === 0) && <div className="text-sm text-slate-500">No tasks generated</div>}
        <ul className="list-disc pl-5">
          {plan.tasks && plan.tasks.map((t, i) => (
            <li key={i} className="text-sm py-1">
              <div className="font-medium">{t.task || "task"}</div>
              <div className="text-xs text-slate-600">{t.details || JSON.stringify(t)}</div>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-2">
        <h3 className="font-semibold">Assignment</h3>
        {!plan.assignment && <div className="text-sm text-slate-500">No assignment</div>}
        {plan.assignment && (
          <pre className="text-xs bg-slate-50 p-2 rounded overflow-auto">{JSON.stringify(plan.assignment, null, 2)}</pre>
        )}
      </div>
    </div>
  );
}
