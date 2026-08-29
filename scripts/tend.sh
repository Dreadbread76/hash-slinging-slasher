#!/usr/bin/env bash
#
# Merges submission pull requests as they land, and deletes the branches behind them.
#
#     bash scripts/tend.sh            watch and tend, every 60 seconds
#     bash scripts/tend.sh --once     one pass and stop
#
# ## Why
#
# A grind opens a pull request after every job, so an overnight run leaves dozens. Each is the
# same shape, and reviewing them by eye is a queue rather than a judgement. This does the checking
# a person could not do by eye anyway, and merges what passes.
#
# ## What it will not merge
#
# Anything that is not submission text. A pull request touching `src/`, `bin/`, `data/`,
# `snapshots/`, `.github/` or the markdown at the root changes what every contributor runs, and
# that is a decision for a person. Those are left open and reported.
#
# A pull request carrying a **new or changed** generator is also left alone: a generator is code
# that every agent pulling this repository then runs, so it gets read by a human before it lands.
#
# And nothing merges until its checks have actually run and passed. This is not the same as "no
# check failed": a fork's first pull request has its workflows held at `action_required` until
# somebody approves them, so *no checks at all* is the normal state of a new contributor's first
# submission, and it used to read here as nothing being wrong. It is not nothing being wrong -- it
# is the re-verification in `validate.yml` never having happened, which would leave the names
# taken on the sender's word. Those runs are released automatically, after the file gate above has
# proved the pull request touches nothing but submission text, and the merge waits for the result.
# What is removed automatically is a script copy identical to one already in the library --
# `submit` should no longer send those, but an older client or a stale `contrib/` still can, and
# merging one either duplicates a file or flips its line endings for nothing.
#
# The comparison is by **content**, not by name: a stamp differs on every submission, so names
# cannot tell an update from a duplicate, and those two need opposite treatment.
#
# ## Safety
#
# Every check is read from the GitHub API rather than from a checkout, so nothing in a fork's
# branch is executed here. Branches are deleted only after their tip is proved to be an ancestor
# of `main`, so an unmerged branch cannot be lost.
set -u

cd "$(dirname "$0")/.." || exit 1
mkdir -p logs

REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null \
       || echo "KingslayerKyle/hash-slinging-slasher")
ONCE=0
[ "${1:-}" = "--once" ] && ONCE=1

say() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

# What the checks on a pull request's *current* head say. This is the one thing this script
# did not look at, and the gap was not theoretical: a fork's first pull request has its
# workflows held at `action_required` until somebody approves them, so on the busiest night
# here 100 of 220 open pull requests carried no checks at all. Merging on the file gate alone
# would have taken every one of those on the sender's word -- which is exactly what
# `validate.yml` exists to refuse. The sender already checked the names on their own machine
# with their own build; that is not evidence, and a wrong name entered into the community
# tables is copied outward and is very hard to take back.
#
# PASS only when something actually ran and everything that ran succeeded. NONE is not PASS.
checks_state() {
    gh pr view "$1" --repo "$REPO" --json statusCheckRollup --jq '
        [.statusCheckRollup[]? | (.conclusion // .state // "PENDING")]
        | if length == 0 then "NONE"
          elif any(. == "FAILURE" or . == "ERROR" or . == "TIMED_OUT"
                   or . == "CANCELLED" or . == "ACTION_REQUIRED"
                   or . == "STARTUP_FAILURE") then "FAIL"
          elif any(. == "PENDING" or . == "IN_PROGRESS" or . == "QUEUED"
                   or . == "WAITING" or . == "EXPECTED") then "PENDING"
          else "PASS" end' 2>/dev/null
}

# Release the workflows a fork's pull request has waiting for approval, so the checks this
# script now insists on can actually run. Safe only because it happens *after* the file gate:
# the pull request has already been proved to touch nothing but submission text and the
# contributed library, so it cannot be editing the workflow it is about to run. A fork's
# `pull_request` run gets a read-only token and no secrets either way.
#
# Without this the new gate would deadlock the queue it was added to protect: no checks, so no
# merge, so the pull request waits for ever on a human this script exists to spare.
approve_waiting_runs() {
    local pr="$1" head="$2" id
    for id in $(gh api "repos/$REPO/actions/runs?event=pull_request&head_sha=$head" \
                    --jq '.workflow_runs[]? | select(.status == "action_required"
                          or .conclusion == "action_required") | .id' 2>/dev/null); do
        gh api -X POST "repos/$REPO/actions/runs/$id/approve" >/dev/null 2>&1 \
            && say "#$pr released workflow run $id -- its checks can run now"
    done
}

tend_one() {
    local pr="$1"
    local files branch path name stem here sha candidate

    files=$(gh pr view "$pr" --repo "$REPO" --json files --jq '.files[].path' 2>/dev/null)
    [ -z "$files" ] && return 0

    if printf '%s\n' "$files" | grep -qvE '^(submissions/|scripts/contributed/)'; then
        say "#$pr touches more than submissions -- leaving it for a human"
        return 0
    fi

    branch=$(gh pr view "$pr" --repo "$REPO" --json headRefName --jq .headRefName 2>/dev/null)
    [ -z "$branch" ] && return 0

    # The branch lives in the *fork*, not here. Reading it out of "$REPO" 404s for every
    # fork pull request -- which is all of them -- and the `|| continue` below then skipped
    # the generator check entirely and fell through to the merge. Measured on the queue of
    # 2026-08-29: 37 pull requests carrying 456 contributed scripts, and this gate fired
    # zero times. Every one of them merged with its generator unread.
    head_repo=$(gh pr view "$pr" --repo "$REPO" \
                --json headRepositoryOwner,headRepository \
                --jq '.headRepositoryOwner.login + "/" + .headRepository.name' 2>/dev/null)
    case "$head_repo" in ""|"/"|*/) head_repo="$REPO";; esac

    for path in $(printf '%s\n' "$files" | grep '^scripts/contributed/'); do
        name=$(basename "$path")

        # Split the extension off before stripping the stamp, rather than assuming .py. The stamp
        # sits before the extension, so `${name%.py}` left it in place on a .sh or a .txt: the stem
        # kept both stamp and extension, no library candidate could ever match it, and every such
        # file was reported as a new generator forever. Held rather than merged, so nothing was
        # lost -- but a submission carrying one could not be cleared by this script at all.
        ext="${name##*.}"
        stem=$(echo "${name%.*}" | sed -E 's/_[0-9]{8}-[0-9]{6}$//')

        # Raw content straight from the API: no base64, no line-ending juggling.
        # Fails *closed*. If the script cannot be read then it has not been compared to
        # anything, and merging it would be taking an unread generator on trust -- the one
        # thing this function exists to prevent. So it holds rather than continuing.
        if ! gh api -H "Accept: application/vnd.github.raw" \
                "repos/$head_repo/contents/$path?ref=$branch" > logs/.incoming 2>/dev/null; then
            rm -f logs/.incoming
            say "#$pr could not read $name to check it -- leaving it for a human"
            return 0
        fi

        here=""
        for candidate in scripts/contributed/"$stem"_*."$ext" "scripts/contributed/$stem.$ext" "scripts/$stem.$ext"; do
            [ -f "$candidate" ] || continue
            # --strip-trailing-cr so a CRLF checkout does not read as a different file.
            if diff -q --strip-trailing-cr "$candidate" logs/.incoming >/dev/null 2>&1; then
                here="$candidate"
                break
            fi
        done
        rm -f logs/.incoming

        if [ -z "$here" ]; then
            say "#$pr carries a new or changed generator ($name) -- leaving it for a human"
            return 0
        fi

        sha=$(gh api "repos/$head_repo/contents/$path?ref=$branch" --jq .sha 2>/dev/null)
        [ -z "$sha" ] && { say "#$pr cannot read the sha for $name -- leaving it"; return 0; }

        # Against the fork too. Dropping the duplicate needs write access to that branch,
        # which a fork grants only through "allow edits by maintainers"; where it is refused
        # the pull request is held rather than merged with the duplicate still on it.
        if gh api -X DELETE "repos/$head_repo/contents/$path" \
               -f message="Already in the library as $here" \
               -f sha="$sha" -f branch="$branch" >/dev/null 2>&1; then
            say "#$pr dropped duplicate $name (library has $here)"
        else
            say "#$pr carries duplicate $name and it could not be dropped -- leaving it"
            return 0
        fi
    done

    # Read the head again rather than reusing anything from above: dropping a duplicate
    # generator rewrites the branch, and the checks that matter are the ones on what would
    # actually merge.
    local head state
    head=$(gh pr view "$pr" --repo "$REPO" --json headRefOid --jq .headRefOid 2>/dev/null)
    state=$(checks_state "$pr")

    case "$state" in
        NONE)
            [ -n "$head" ] && approve_waiting_runs "$pr" "$head"
            say "#$pr has no checks yet -- not merging until they have run"
            return 0
            ;;
        PENDING)
            say "#$pr checks still running -- leaving it for the next pass"
            return 0
            ;;
        FAIL)
            say "#$pr checks did not pass -- leaving it for a human"
            return 0
            ;;
        PASS) ;;
        *)
            say "#$pr check state unreadable ('$state') -- leaving it rather than guessing"
            return 0
            ;;
    esac

    if gh pr merge "$pr" --repo "$REPO" --merge >/dev/null 2>&1; then
        say "#$pr merged"
    else
        say "#$pr would not merge -- probably a conflict, leaving it"
    fi
}

prune_branches() {
    local branch sha
    git fetch -q origin --prune 2>/dev/null

    for branch in $(git ls-remote --heads origin 'refs/heads/findings/*' 2>/dev/null \
                    | awk '{print $2}' | sed 's|refs/heads/||'); do
        sha=$(git ls-remote origin "refs/heads/$branch" 2>/dev/null | cut -f1)
        [ -z "$sha" ] && continue

        # Proved to be in main, never assumed. An unmerged branch is somebody's night.
        if git merge-base --is-ancestor "$sha" origin/main 2>/dev/null; then
            git push origin --delete "$branch" >/dev/null 2>&1 && say "deleted branch $branch"
        fi
    done
}

while :; do
    # --limit, because `gh pr list` defaults to 30 and a night leaves far more than that.
    # Without it the queue is only ever drained thirty at a time, and the tail of a big
    # batch looks like it merged when it was never looked at.
    for pr in $(gh pr list --repo "$REPO" --limit 500 --json number --jq '.[].number' 2>/dev/null); do
        tend_one "$pr"
    done

    prune_branches

    [ "$ONCE" = "1" ] && break
    sleep 60
done
