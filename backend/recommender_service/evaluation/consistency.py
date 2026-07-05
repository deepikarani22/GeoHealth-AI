def check_consistency(run_fn, payload):
    r1 = run_fn(payload)
    r2 = run_fn(payload)
    return r1 == r2
