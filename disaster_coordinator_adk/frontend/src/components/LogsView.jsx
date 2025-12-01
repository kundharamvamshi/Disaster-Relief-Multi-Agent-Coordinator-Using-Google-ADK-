// src/components/LogsView.jsx
/*eslint-disable*/
import React, { useEffect, useState, startTransition } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function LogsView() {
  const [logs, setLogs] = useState([]);

  async function fetchLogsOnce(isMounted) {
    try {
      const res = await fetch(`${API_BASE}/api/logs`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      // Only update state if component is still mounted
      if (isMounted()) {
        // Mark as low-priority update to avoid render cascade warnings
        startTransition(() => {
          setLogs(json.logs || []);
        });
      }
    } catch (e) {
      // swallow errors and optionally log
      // console.error("fetchLogs error", e);
      if (isMounted()) {
        startTransition(() => setLogs([]));
      }
    }
  }

  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;

    // initial fetch (async)
    fetchLogsOnce(isMounted);

    // poll every 5s
    const id = setInterval(() => {
      fetchLogsOnce(isMounted);
    }, 5000);

    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="max-h-48 overflow-auto">
      {logs.length === 0 && <div className="text-sm text-slate-500">No logs yet</div>}
      <ul className="text-xs">
        {logs.map((l, i) => (
          <li key={i} className="py-1 border-b">
            {JSON.stringify(l)}
          </li>
        ))}
      </ul>
    </div>
  );
}
