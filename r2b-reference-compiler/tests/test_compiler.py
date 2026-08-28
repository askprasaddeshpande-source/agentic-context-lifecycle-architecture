import unittest
from ace_wsa_r2b.compiler import ContextCompiler
from ace_wsa_r2b.fixtures import helios_mission,helios_candidates
from ace_wsa_r2b.models import CompileStatus

class Compiler(unittest.TestCase):
    def test_helios(self):
        r=ContextCompiler().compile(helios_mission(),helios_candidates())
        self.assertEqual(r.status,CompileStatus.COMPILED)
        self.assertEqual(len(r.context.authoritative_state),10)
        self.assertEqual(len(r.context.tools),0)
        self.assertEqual(r.context.provenance_manifest["coverage"]["excluded_count"],3500)
    def test_hash_stable(self):
        cc=ContextCompiler()
        a=cc.compile(helios_mission(),helios_candidates(10))
        b=cc.compile(helios_mission(),helios_candidates(10))
        self.assertEqual(a.context.context_hash,b.context.context_hash)
