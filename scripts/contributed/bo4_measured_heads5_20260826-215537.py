import runpy, os

# Execute the contributed generator with its repository root corrected for this staging path.
src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "contributed", "measured_heads_20260825-043818.py")
ns = runpy.run_path(src)
root = os.path.dirname(os.path.dirname(__file__))
ns["REPO"] = root
ns["load"].__globals__["REPO"] = root
ns["main"]()
