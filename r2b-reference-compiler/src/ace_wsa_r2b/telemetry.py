from datetime import datetime,timezone
from uuid import uuid4
class Telemetry:
    def __init__(self,mission_id):self.mission_id=mission_id;self.events=[]
    def emit(self,event_type,payload):
        self.events.append({"event_version":"r2b.1","event_id":f"EVT-{uuid4()}",
            "timestamp":datetime.now(timezone.utc).isoformat(),"mission_id":self.mission_id,
            "event_type":event_type,"payload":payload})
