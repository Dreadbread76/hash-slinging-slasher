"""Overnight high-yield multi-pass solver across Black Ops 4 and Cold War.

Runs for up to 16 hours, alternating games, generating high-yield candidate sets:
- All-boundary uncarried endings (general & sound across depths 2, 3, 4, 1, 5)
- Heads with slashes and measured alphabets
- Length 4 tails
- Sound SAB uncarried sets
- Auto-deriving closures (material->image, channels, final byte)
- Auto-submitting after every single job
"""

import datetime
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

LOG_FILE = ROOT / "logs" / "overnight_suite.log"


def log(msg: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)


def run_cmd(cmd, cwd=ROOT, check=False, timeout=None):
    log(f"Executing: {' '.join(str(c) for c in cmd)}")
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        for out_line in res.stdout.splitlines()[-15:]:
            log(f"  > {out_line}")
        return res.returncode, res.stdout
    except Exception as e:
        log(f"Command error: {e}")
        return -1, str(e)


def post_pass_actions():
    """Run derive_closure and submit immediately."""
    log("Running post-pass derivation closure...")
    run_cmd([sys.executable, str(ROOT / "scripts" / "derive_closure.py")], timeout=600)
    log("Submitting findings to community...")
    submit_bin = ROOT / "bin" / "windows" / "submit.exe"
    if submit_bin.exists():
        run_cmd([str(submit_bin)], timeout=300)


def job_allboundary_general(game: str, segments: int, top: int = 100000):
    log(f"--- [JOB] All-boundary General: Game={game}, Segments={segments}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "uncarried_endings_allboundary_20260823-134935.py"
    plan_file = ROOT / "plans" / "ab_uncarried.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    code, _ = run_cmd([sys.executable, str(script), "--segments", str(segments), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"uncarried {segments}-segment endings over all-boundary cores",
                "--script",
                "contrib/uncarried_endings_allboundary_20260823-134935.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_allboundary_sound(game: str, segments: int, top: int = 60000):
    log(f"--- [JOB] All-boundary Sound: Game={game}, Segments={segments}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "uncarried_endings_allboundary_20260823-134935.py"
    plan_file = ROOT / "plans" / "ab_sound_uncarried.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    code, _ = run_cmd([sys.executable, str(script), "--sound-pass", "--segments", str(segments), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        flags = [
            str(confirm_bin),
            str(plan_file),
            "--game",
            game,
            "--anyway",
            "--label",
            f"sound, uncarried {segments}-segment endings over all-boundary cores",
            "--script",
            "contrib/uncarried_endings_allboundary_20260823-134935.py",
        ]
        if game == "BLKOPS04":
            flags.append("--no-fold")
        run_cmd(flags, timeout=7200)
        post_pass_actions()


def job_heads_slash(game: str, length: int = 4):
    log(f"--- [JOB] Heads Slash: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "contributed" / "heads_slash_20260824-025001.py"
    plan_file = ROOT / "plans" / f"heads_slash{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    code, _ = run_cmd([sys.executable, str(script), "--length", str(length), "--write-plan", str(plan_file)], timeout=600)
    if code == 0 and plan_file.exists():
        run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"heads of length {length}, slash-bearing beginnings",
                "--script",
                "contrib/heads_slash_20260824-025001.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_heads_measured(game: str, length: int = 3):
    log(f"--- [JOB] Heads Measured Alphabet: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "contributed" / "heads_measured_alphabet_20260823-204820.py"
    plan_file = ROOT / "plans" / f"heads_meas{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    code, _ = run_cmd([sys.executable, str(script), "--length", str(length), "--write-plan", str(plan_file)], timeout=600)
    if code == 0 and plan_file.exists():
        run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"heads of length {length}, head-measured alphabet",
                "--script",
                "contrib/heads_measured_alphabet_20260823-204820.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_tails(game: str, length: int = 4):
    log(f"--- [JOB] Tails: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "tails.py"
    plan_file = ROOT / "plans" / f"tails{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"

    code, _ = run_cmd([sys.executable, str(script), "--length", str(length), "--write-plan", str(plan_file)], timeout=600)
    if code == 0 and plan_file.exists():
        run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"tails of length {length}",
            ],
            timeout=7200,
        )
        post_pass_actions()


def main():
    log("=== STARTING 16-HOUR OVERNIGHT RECOVERY SUITE ===")
    start_time = time.time()
    max_duration_sec = 16 * 3600  # 16 hours

    # 1. Initial preflight sync
    start_bin = ROOT / "bin" / "windows" / "start.exe"
    if start_bin.exists():
        log("Running preflight sync...")
        run_cmd([str(start_bin)], timeout=300)

    # Initial closure run
    post_pass_actions()

    iteration = 1
    while time.time() - start_time < max_duration_sec:
        log(f"================ ROUND {iteration} ================")

        # Run primary high yield generators
        # 1. BO4 & CW allboundary uncarried endings at key depths
        for segments in [2, 3, 4, 1, 5]:
            job_allboundary_general("BLKOPS04", segments=segments)
            job_allboundary_general("BLKOPSCW", segments=segments)
            if time.time() - start_time >= max_duration_sec:
                break

        # 2. Sound allboundary uncarried
        for segments in [2, 3, 1]:
            job_allboundary_sound("BLKOPS04", segments=segments)
            job_allboundary_sound("BLKOPSCW", segments=segments)
            if time.time() - start_time >= max_duration_sec:
                break

        # 3. Heads slash
        job_heads_slash("BLKOPS04", length=4)
        job_heads_slash("BLKOPSCW", length=4)

        # 4. Heads measured alphabet
        job_heads_measured("BLKOPS04", length=3)
        job_heads_measured("BLKOPSCW", length=3)

        # 5. Tails length 4
        job_tails("BLKOPS04", length=4)
        job_tails("BLKOPSCW", length=4)

        iteration += 1

    log("=== OVERNIGHT SUITE FINISHED ===")
    post_pass_actions()


if __name__ == "__main__":
    main()
