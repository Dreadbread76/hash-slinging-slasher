"""Overnight high-yield multi-pass autonomous recovery suite across Black Ops 4 and Cold War.

Runs autonomously for up to 16 hours, alternating games, generating high-yield candidate sets:
- Preflight sync & readiness refresh (refreshes cod-name-db tables and open PR claims every 2 hours)
- Corpus-mined substitutions, equivalence classes, and indels (mined_axes)
- Sound-specific backwards final-byte solve with game-correct backslashes (sound_final_byte)
- Evidence-backed multi-axis grids: map prefixes & gamemodes, operator voice line speaker grids, head-axis-tail grids
- Two-token & six-token suffix block precedents
- Observed token-boundary, separator, and adjacent-order variants
- Numeric repadding (_1 <-> _01 <-> _001)
- All-boundary uncarried endings (general & sound across depths 2, 3, 4, 1, 5)
- Measured shells (head 6 + tail 6 cross-products)
- Slash-bearing heads & measured-alphabet heads / tails
- Typed borrowed endings across ranked bands (xanim, xmodel, material, image)
- Automatic closure derivation (image siblings, channel completion, final-byte backwards solve)
- Automatic PR submission to GitHub after every single job
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


def run_pipeline(producer_cmd, consumer_cmd, cwd=ROOT, timeout=7200):
    log(f"Pipeline: {' '.join(str(c) for c in producer_cmd)} | {' '.join(str(c) for c in consumer_cmd)}")
    try:
        p1 = subprocess.Popen(producer_cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(consumer_cmd, cwd=str(cwd), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        p1.stdout.close()
        stdout, _ = p2.communicate(timeout=timeout)
        p1.wait(timeout=30)
        for out_line in stdout.splitlines()[-15:]:
            log(f"  > {out_line}")
        return p2.returncode, stdout
    except Exception as e:
        log(f"Pipeline error: {e}")
        return -1, str(e)


def post_pass_actions():
    """Run derive_closure and submit immediately after any finding."""
    log("Running post-pass derivation closure...")
    run_cmd([sys.executable, str(ROOT / "scripts" / "derive_closure.py")], timeout=600)
    log("Submitting findings to community...")
    submit_bin = ROOT / "bin" / "windows" / "submit.exe"
    if submit_bin.exists():
        run_cmd([str(submit_bin)], timeout=300)


def preflight_sync():
    """Run start.exe to refresh hash tables, survey open PRs, and renew the 12-hour lease."""
    start_bin = ROOT / "bin" / "windows" / "start.exe"
    if start_bin.exists():
        log("Running preflight sync & table refresh...")
        run_cmd([str(start_bin)], timeout=300)


# =========================================================================
# JOB DEFINITIONS
# =========================================================================

def job_mined_axes(game: str, top: int = 400, classes: bool = False, indels: bool = False):
    log(f"--- [JOB] Mined Axes: Game={game}, Top={top}, Classes={classes}, Indels={indels} ---")
    script = ROOT / "scripts" / "contributed" / "mined_axes_20260825-113712.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    if classes:
        prod.append("--classes")
    elif indels:
        prod.append("--indels")
    else:
        prod.extend(["--top", str(top)])
    
    label = "corpus-mined substitutions"
    if classes:
        label += " (equivalence classes)"
    elif indels:
        label += " (indels)"
    else:
        label += f" (top {top})"

    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        label,
        "--script",
        "scripts/contributed/mined_axes_20260825-113712.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=2400)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_sound_final_byte(game: str):
    log(f"--- [JOB] Sound Final Byte: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "sound_final_byte_20260825-043818.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script), "--game", game]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "sound final byte solved backwards",
        "--script",
        "scripts/contributed/sound_final_byte_20260825-043818.py",
    ]
    if game == "BLKOPS04":
        cons.append("--no-fold")
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_speaker_grids(game: str):
    log(f"--- [JOB] Speaker Grids: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "speaker_grids_20260822-021342.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "speaker grids across voice lines",
        "--script",
        "scripts/contributed/speaker_grids_20260822-021342.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_map_prefix_mode_grid(game: str):
    log(f"--- [JOB] Map Prefix Mode Grid: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "map_prefix_mode_grid_20260826-044806.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "map prefix and mode grid completion",
        "--script",
        "scripts/contributed/map_prefix_mode_grid_20260826-044806.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_head_axis_tail_grid(game: str, top: int = 15):
    log(f"--- [JOB] Head Axis Tail Grid: Game={game}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "head_axis_tail_grid_20260826-120940.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script), "--top", str(top)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        f"evidence-backed head_axis_tail grids, top {top}",
        "--script",
        "scripts/contributed/head_axis_tail_grid_20260826-120940.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_suffix_block_precedents(game: str):
    log(f"--- [JOB] Suffix Block Precedents: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "suffix_block_precedents_20260826-064355.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "two-token per-suffix precedents",
        "--script",
        "scripts/contributed/suffix_block_precedents_20260826-064355.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_precedents_suffix6(game: str):
    log(f"--- [JOB] Precedents Suffix 6: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "precedents_suffix6_20260826-080521.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "one-token precedents before six-token suffix",
        "--script",
        "scripts/contributed/precedents_suffix6_20260826-080521.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_token_boundaries(game: str):
    log(f"--- [JOB] Token Boundaries: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "token_boundaries_20260826-041334.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "observed token-boundary variants",
        "--script",
        "scripts/contributed/token_boundaries_20260826-041334.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_separator_variants(game: str):
    log(f"--- [JOB] Separator Variants: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "separator_variants_20260826-041334.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "observed separator spelling variants",
        "--script",
        "scripts/contributed/separator_variants_20260826-041334.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_adjacent_token_order(game: str):
    log(f"--- [JOB] Adjacent Token Order: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "adjacent_token_order_20260826-041334.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "adjacent token permutations",
        "--script",
        "scripts/contributed/adjacent_token_order_20260826-041334.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_repad(game: str):
    log(f"--- [JOB] Numeric Repad: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "repad_20260825-045514.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "numeric repadding",
        "--script",
        "scripts/contributed/repad_20260825-045514.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


def job_numbered_grids(game: str):
    log(f"--- [JOB] Numbered Grids: Game={game} ---")
    script = ROOT / "scripts" / "contributed" / "numbered_grids_20260824-155834.py"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_list.exe"
    if not script.exists() or not confirm_bin.exists():
        return
    prod = [sys.executable, str(script)]
    cons = [
        str(confirm_bin),
        "-",
        "--game",
        game,
        "--anyway",
        "--label",
        "numbered families on two axes",
        "--script",
        "scripts/contributed/numbered_grids_20260824-155834.py",
    ]
    code, out = run_pipeline(prod, cons, timeout=1800)
    if "this run added 0" not in out and "this run added" in out:
        post_pass_actions()


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
                "scripts/contributed/uncarried_endings_allboundary_20260823-134935.py",
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
            "scripts/contributed/uncarried_endings_allboundary_20260823-134935.py",
        ]
        if game == "BLKOPS04":
            flags.append("--no-fold")
        run_cmd(flags, timeout=7200)
        post_pass_actions()


def job_measured_shells(game: str, head: int = 6, tail: int = 6, top: int = 800):
    log(f"--- [JOB] Measured Shells: Game={game}, Head={head}, Tail={tail}, Top={top} ---")
    script = ROOT / "scripts" / "contributed" / "measured_shells_20260825-045514.py"
    plan_file = ROOT / "plans" / f"shell_h{head}t{tail}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--head", str(head), "--tail", str(tail), "--top", str(top)], timeout=600)
    if code == 0 and plan_file.exists():
        run_cmd(
            [
                str(confirm_bin),
                str(plan_file),
                "--game",
                game,
                "--anyway",
                "--label",
                f"measured shells, head {head} tail {tail}, top {top}",
                "--script",
                "scripts/contributed/measured_shells_20260825-045514.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_heads_slash(game: str, length: int = 4):
    log(f"--- [JOB] Heads Slash: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "contributed" / "heads_slash_20260824-025001.py"
    plan_file = ROOT / "plans" / f"heads_slash{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

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
                "scripts/contributed/heads_slash_20260824-025001.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_heads_measured(game: str, length: int = 3):
    log(f"--- [JOB] Heads Measured Alphabet: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "contributed" / "heads_measured_alphabet_20260823-204820.py"
    plan_file = ROOT / "plans" / f"heads_meas{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

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
                "scripts/contributed/heads_measured_alphabet_20260823-204820.py",
            ],
            timeout=7200,
        )
        post_pass_actions()


def job_tails(game: str, length: int = 4):
    log(f"--- [JOB] Tails: Game={game}, Length={length} ---")
    script = ROOT / "scripts" / "tails.py"
    plan_file = ROOT / "plans" / f"tails{length}.txt"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not script.exists() or not confirm_bin.exists():
        return

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


def job_typed_borrowed_endings(game: str, ends: int = 5000, ends_skip: int = 0):
    log(f"--- [JOB] Typed Borrowed Endings: Game={game}, Ends={ends}, Skip={ends_skip} ---")
    script = ROOT / "scripts" / "contributed" / "typed_borrowed_endings_20260824-201239.py"
    source_file = ROOT / "borrowed" / "bo3_assetlist.txt"
    if not source_file.exists() or not script.exists():
        log("  > skipped: borrowed/bo3_assetlist.txt not present on this machine")
        return

    plan_prefix = ROOT / "plans" / "tbe"
    confirm_bin = ROOT / "bin" / "windows" / "confirm_plan.exe"
    if not confirm_bin.exists():
        return

    code, _ = run_cmd([sys.executable, str(script), "--write-plans", str(plan_prefix), "--ends", str(ends), "--ends-skip", str(ends_skip)], timeout=600)
    if code == 0:
        for kind in ["xanim", "xmodel", "material", "image"]:
            plan_file = ROOT / "plans" / f"tbe.{kind}.txt"
            if plan_file.exists():
                run_cmd(
                    [
                        str(confirm_bin),
                        str(plan_file),
                        "--game",
                        game,
                        "--anyway",
                        "--label",
                        f"typed borrowed endings ({kind}), ends {ends} skip {ends_skip}",
                        "--script",
                        "scripts/contributed/typed_borrowed_endings_20260824-201239.py",
                    ],
                    timeout=7200,
                )
                post_pass_actions()


def main():
    log("=== STARTING 8-HOUR AUTONOMOUS RECOVERY SUITE ===")
    start_time = time.time()
    max_duration_sec = 8 * 3600  # 8 hours

    # 1. Initial preflight sync
    preflight_sync()
    post_pass_actions()

    iteration = 1
    last_preflight_time = time.time()

    while time.time() - start_time < max_duration_sec:
        log(f"================ ROUND {iteration} ================")

        # Periodically refresh preflight every 2 hours to avoid 12-hr readiness block
        if time.time() - last_preflight_time > 7200:
            preflight_sync()
            last_preflight_time = time.time()

        # -------------------------------------------------------------
        # 1. Sound-Specific Backwards Final-Byte Solve (Highest Yield Sound Pool)
        # -------------------------------------------------------------
        job_sound_final_byte("BLKOPS04")
        job_sound_final_byte("BLKOPSCW")

        # -------------------------------------------------------------
        # 2. Mined Axes, Equivalence Classes & Indels
        # -------------------------------------------------------------
        for top_n in [400, 800]:
            job_mined_axes("BLKOPS04", top=top_n)
            job_mined_axes("BLKOPSCW", top=top_n)
            if time.time() - start_time >= max_duration_sec:
                break

        job_mined_axes("BLKOPS04", classes=True)
        job_mined_axes("BLKOPSCW", classes=True)

        job_mined_axes("BLKOPS04", indels=True)
        job_mined_axes("BLKOPSCW", indels=True)

        # -------------------------------------------------------------
        # 3. Evidence-Backed Multi-Axis Grids (Maps, Speakers, Families)
        # -------------------------------------------------------------
        job_speaker_grids("BLKOPS04")
        job_speaker_grids("BLKOPSCW")

        job_map_prefix_mode_grid("BLKOPS04")
        job_map_prefix_mode_grid("BLKOPSCW")

        job_head_axis_tail_grid("BLKOPS04", top=15)
        job_head_axis_tail_grid("BLKOPSCW", top=15)

        job_numbered_grids("BLKOPS04")
        job_numbered_grids("BLKOPSCW")

        # -------------------------------------------------------------
        # 4. Suffix Block Precedents & Token Boundaries
        # -------------------------------------------------------------
        job_suffix_block_precedents("BLKOPS04")
        job_suffix_block_precedents("BLKOPSCW")

        job_precedents_suffix6("BLKOPS04")
        job_precedents_suffix6("BLKOPSCW")

        job_token_boundaries("BLKOPS04")
        job_token_boundaries("BLKOPSCW")

        job_separator_variants("BLKOPS04")
        job_separator_variants("BLKOPSCW")

        job_adjacent_token_order("BLKOPS04")
        job_adjacent_token_order("BLKOPSCW")

        job_repad("BLKOPS04")
        job_repad("BLKOPSCW")

        # -------------------------------------------------------------
        # 5. All-Boundary Uncarried Endings (General & Sound)
        # -------------------------------------------------------------
        for segments in [2, 3, 4, 1, 5]:
            job_allboundary_general("BLKOPS04", segments=segments)
            job_allboundary_general("BLKOPSCW", segments=segments)
            if time.time() - start_time >= max_duration_sec:
                break

        for segments in [2, 3, 1]:
            job_allboundary_sound("BLKOPS04", segments=segments)
            job_allboundary_sound("BLKOPSCW", segments=segments)
            if time.time() - start_time >= max_duration_sec:
                break

        # -------------------------------------------------------------
        # 6. Measured Shells & Alphabets
        # -------------------------------------------------------------
        job_measured_shells("BLKOPS04", head=6, tail=6, top=800)
        job_measured_shells("BLKOPSCW", head=6, tail=6, top=800)

        job_heads_slash("BLKOPS04", length=4)
        job_heads_slash("BLKOPSCW", length=4)

        job_heads_measured("BLKOPS04", length=3)
        job_heads_measured("BLKOPSCW", length=3)

        job_tails("BLKOPS04", length=4)
        job_tails("BLKOPSCW", length=4)

        # -------------------------------------------------------------
        # 7. Typed Borrowed Endings (Type-Specific Plans)
        # -------------------------------------------------------------
        for ends, ends_skip in [(5000, 0), (5000, 5000), (5000, 10000)]:
            job_typed_borrowed_endings("BLKOPS04", ends=ends, ends_skip=ends_skip)
            job_typed_borrowed_endings("BLKOPSCW", ends=ends, ends_skip=ends_skip)
            if time.time() - start_time >= max_duration_sec:
                break

        iteration += 1

    log("=== OVERNIGHT SUITE COMPLETED (8 HOURS) ===")
    post_pass_actions()


if __name__ == "__main__":
    main()
