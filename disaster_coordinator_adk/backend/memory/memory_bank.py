# backend/memory/memory_bank.py
from typing import List, Dict

class MemoryBank:
    def __init__(self):
        self.incidents: List[Dict] = []
        self.plans: List[Dict] = []
        self.logs: List[Dict] = []

    def write_incident(self, inc: Dict):
        self.incidents.append(inc)
        self.logs.append({"type":"incident", "id": inc.get("id")})

    def write_plan(self, plan: Dict):
        self.plans.append(plan)
        self.logs.append({"type":"plan", "id": plan.get("event_id")})

    def query_by_location(self, location: str):
        return [i for i in self.incidents if i.get("location") == location]
