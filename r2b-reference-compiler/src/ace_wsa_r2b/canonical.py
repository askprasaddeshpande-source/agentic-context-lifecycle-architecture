import json,hashlib
def canonical_json(x):return json.dumps(x,sort_keys=True,separators=(",",":"),default=str)
def stable_hash(x):return "sha256:"+hashlib.sha256(canonical_json(x).encode()).hexdigest()
