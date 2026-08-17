#!/usr/bin/env bash
#
# assemble.sh — copy the local run outputs and task files into this repo,
# sorted into tasks/ and data/, then report what landed where.
#
# Usage:
#   ./assemble.sh "/Users/amikeda/Desktop/Welfare tests"
#
# Safe to re-run: it never overwrites an existing destination file, it
# reports collisions instead. (That is the provenance rule from docs/DATA.md:
# a new repetition is a new file, never an overwrite.)

set -euo pipefail

SRC="${1:-}"
if [[ -z "$SRC" ]]; then
  echo "usage: $0 /path/to/'Welfare tests'" >&2
  exit 1
fi
if [[ ! -d "$SRC" ]]; then
  echo "error: source folder not found: $SRC" >&2
  exit 1
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$REPO/data" "$REPO/tasks"

copied=0; skipped=0; collided=0

copy_one() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [[ -e "$dest" ]]; then
    if cmp -s "$src" "$dest"; then
      skipped=$((skipped+1))
    else
      echo "  COLLISION (different content, not overwritten):"
      echo "    have: $dest"
      echo "    new : $src"
      collided=$((collided+1))
    fi
  else
    cp "$src" "$dest"
    copied=$((copied+1))
  fi
}

echo "Source: $SRC"
echo "Repo:   $REPO"
echo

# --- task files: any .txt that looks like a user-turn script ---
echo "== tasks =="
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  copy_one "$f" "$REPO/tasks/$rel"
done < <(find "$SRC" -type f -name '*.txt' -print0)

# --- run outputs: JSON envelopes and NPZ archives ---
echo "== data =="
while IFS= read -r -d '' f; do
  rel="${f#"$SRC"/}"
  copy_one "$f" "$REPO/data/$rel"
done < <(find "$SRC" -type f \( -name '*.json' -o -name '*.npz' \) -print0)

# --- notebooks found locally (kept separate; the canonical ones are committed) ---
echo "== notebooks found locally (not copied automatically) =="
find "$SRC" -type f -name '*.ipynb' -print | sed 's/^/  /' || true

echo
echo "copied:    $copied"
echo "identical: $skipped (already present, unchanged)"
echo "collisions:$collided (same name, different content — resolve by hand)"
echo

# --- inventory ---
echo "== inventory =="
echo "task files: $(find "$REPO/tasks" -type f -name '*.txt' | wc -l | tr -d ' ')"
echo "JSON runs:  $(find "$REPO/data" -type f -name '*.json' | wc -l | tr -d ' ')"
echo "NPZ files:  $(find "$REPO/data" -type f -name '*.npz'  | wc -l | tr -d ' ')"
npz_size=$(find "$REPO/data" -type f -name '*.npz' -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
echo "NPZ total:  ${npz_size}"
echo
echo "If NPZ total is over ~1 GB, use Git LFS (git lfs install) or host the"
echo "archives separately — see docs/DATA.md."
