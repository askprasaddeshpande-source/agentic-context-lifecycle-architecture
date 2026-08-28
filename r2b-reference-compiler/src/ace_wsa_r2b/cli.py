import argparse,json
from pathlib import Path
from .compiler import ContextCompiler
from .fixtures import helios_mission,helios_candidates
from .contracts import mission_from_dict,candidate_from_dict

def main():
    p=argparse.ArgumentParser(prog="ace-context");s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("helios");c=s.add_parser("compile");c.add_argument("mission");c.add_argument("candidates")
    a=p.parse_args();cc=ContextCompiler()
    if a.cmd=="helios":r=cc.compile(helios_mission(),helios_candidates(),mode="SHADOW")
    else:
        m=mission_from_dict(json.loads(Path(a.mission).read_text(encoding="utf-8")))
        cs=[candidate_from_dict(x) for x in json.loads(Path(a.candidates).read_text(encoding="utf-8"))]
        r=cc.compile(m,cs,mode="SHADOW")
    payload={"status":r.status.value,"blocking_conditions":r.blocking_conditions,
             "context":r.context.to_dict() if r.context else None,"telemetry":r.telemetry}
    print(json.dumps(payload,indent=2))
