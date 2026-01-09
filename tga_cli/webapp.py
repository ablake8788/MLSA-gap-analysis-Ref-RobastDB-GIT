####### webapp.py
## Add a web entrypoint (FastAPI “runner”)

import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="TGA Runner")

class RunRequest(BaseModel):
    args: list[str] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(req: RunRequest):
    # Run the existing CLI module in-process as a subprocess
    # so it behaves like your current CLI behavior.
    cmd = ["python", "-m", "tga_cli"] + req.args

    # Ensure output dir exists (App Service writeable path is /home)
    output_dir = os.environ.get("OUTPUT_DIR", "/home/site/wwwroot/reports")
    os.makedirs(output_dir, exist_ok=True)

    env = os.environ.copy()
    env["OUTPUT_DIR"] = output_dir

    p = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if p.returncode != 0:
        raise HTTPException(status_code=500, detail={
            "returncode": p.returncode,
            "stdout": p.stdout[-4000:],
            "stderr": p.stderr[-4000:]
        })

    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-4000:],
        "stderr": p.stderr[-4000:]
    }
