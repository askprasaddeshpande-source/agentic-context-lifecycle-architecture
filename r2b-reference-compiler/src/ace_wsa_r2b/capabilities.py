class CapabilitySelector:
    def select_tools(self,mission,tools):
        req=set(mission.requested_capabilities);sel=[];exc=[]
        for t in sorted(tools,key=lambda x:x.tool_id):
            reason=None
            if t.capability not in req:reason="TOOL_NOT_REQUIRED"
            elif t.scope_project_id and mission.environment.project_id and t.scope_project_id!=mission.environment.project_id:reason="WRONG_SCOPE"
            elif t.mode.upper()=="WRITE" and not mission.execution.write_allowed:reason="WRITE_NOT_AUTHORIZED"
            elif t.requires_authorization and not mission.execution.write_allowed:reason="WRITE_NOT_AUTHORIZED"
            (exc.append((t,reason)) if reason else sel.append(t))
        return sel,exc

    def select_skills(self,mission,skills):
        req=set(mission.requested_capabilities);sel=[];exc=[]
        for s in sorted(skills,key=lambda x:x.skill_id):
            if s.scope_project_id and mission.environment.project_id and s.scope_project_id!=mission.environment.project_id:
                exc.append((s,"WRONG_SCOPE"))
            elif not req.intersection(s.capabilities):
                exc.append((s,"SKILL_NOT_REQUIRED"))
            else:sel.append(s)
        return sel,exc
