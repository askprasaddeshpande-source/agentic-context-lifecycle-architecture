import unittest
from ace_wsa_r2b.acceptance import run_acceptance
class Acceptance(unittest.TestCase):
    def test_all(self):
        c=run_acceptance()
        self.assertFalse({k:v for k,v in c.items() if not v})
