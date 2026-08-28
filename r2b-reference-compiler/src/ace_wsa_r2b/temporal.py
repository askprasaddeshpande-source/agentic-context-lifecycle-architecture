from dataclasses import replace
from datetime import datetime,timezone
from .models import TemporalState

def _parse(x):
    if not x:return None
    d=datetime.fromisoformat(x.replace("Z","+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

class TemporalResolver:
    def resolve(self,c,mission_time=None):
        t=c.temporal
        if t.superseded_by:
            return replace(c,temporal=replace(t,state=TemporalState.SUPERSEDED))
        if t.state in {TemporalState.SUPERSEDED,TemporalState.CONFLICTING}: return c
        if mission_time:
            now=_parse(mission_time); vf=_parse(t.valid_from); vt=_parse(t.valid_to)
            if vf and now and now<vf:return replace(c,temporal=replace(t,state=TemporalState.HISTORICAL))
            if vt and now and now>=vt:return replace(c,temporal=replace(t,state=TemporalState.HISTORICAL))
        return c
