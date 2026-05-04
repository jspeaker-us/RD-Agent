import json
import platform
import re
from pathlib import Path

from rdagent.core.experiment import FBWorkspace
from rdagent.utils.env import Env


def get_runtime_environment_by_env(env: Env) -> str:
    implementation = FBWorkspace()
    fname = "runtime_info.py"
    implementation.inject_files(**{fname: (Path(__file__).absolute().resolve().parent / "runtime_info.py").read_text()})
    stdout = implementation.execute(env=env, entry=f"python {fname}")
    # Extract JSON from stdout (skip CUDA/container warnings)
    json_match = re.search(r"\{.*\}", stdout, re.DOTALL)
    return json.dumps(json.loads(json_match.group()), indent=2)


def check_runtime_environment(env: Env) -> str:
    implementation = FBWorkspace()
    # 1) Check if strace exists in env
    strace_check_cmd = (
        "python -c \"import shutil, sys; sys.exit(0 if shutil.which('strace') else 1)\""
        if platform.system() == "Windows"
        else "which strace"
    )
    strace_check = implementation.run(env=env, entry=strace_check_cmd)
    if platform.system() == "Windows" and strace_check.exit_code != 0:
        # Native Windows environments do not provide strace; keep the check informative only.
        strace_check = None
    elif strace_check.exit_code != 0:
        raise RuntimeError("`strace` not found in the target environment.")

    # 2) Check if coverage module works in env
    coverage_check = implementation.run(env=env, entry="python -m coverage --version")
    if coverage_check.exit_code != 0:
        raise RuntimeError("`coverage` module not found or not runnable in the target environment.")
