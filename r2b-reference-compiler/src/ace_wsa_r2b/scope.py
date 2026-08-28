from .models import ContextCandidate, MissionRequest

class ScopePolicy:
    @staticmethod
    def allowed(c:ContextCandidate,m:MissionRequest):
        s,e=c.scope,m.environment
        if s.shareable: return True,None
        if s.project_id and e.project_id and s.project_id!=e.project_id: return False,"WRONG_SCOPE"
        if s.system and e.system and s.system!=e.system: return False,"WRONG_ENVIRONMENT"
        if s.client and e.client and s.client!=e.client: return False,"WRONG_ENVIRONMENT"
        return True,None
