# EPW School 2026 — Spectral Function Tutorial

Hands-on tutorial materials for the EPW School 2026 session on Wannier
function perturbation theory (WFPT) and phonon spectral functions, built on
Quantum ESPRESSO and EPW. Carried over from the 2024 tutorial (commit 7ccad8a
"Add files from 2024 tutorial") and being updated for 2026.

## Layout

- `code/` — input files for the hands-on exercises, organized per exercise.
  - `exercise1/` — diamond AHC / WFPT band-structure renormalization.
  - `exercise2/` — MgB$_2$ electron spectral function.
  - `exercise3/` — MgB$_2$ phonon spectral function.
  - `run.sh` — example SLURM batch script (Stampede3, `pw.x` + `ph.x`).
  - Each exercise directory holds the QE/EPW inputs (`scf.in`, `nscf.in`,
    `ph.in`, `pp.in`, `epw*.in`, `ahc.in`, …), pseudopotentials (`*.UPF`),
    and any helper scripts (`plot.py`).
- `document/` — LaTeX source of the tutorial handout.
  - `main.tex` — main LaTeX file for the handout (compile this).
  - `settings.tex` — shared preamble (packages, page geometry, fancyhdr,
    `\program` and `\action` macros). Document-specific macros (`\Eq`,
    `\mb`, `\todo`, `\qnu`) live in `main.tex`, not here, so `settings.tex`
    can be kept in sync with the school-wide template.
  - Built PDF is `main.pdf`.

## Building the handout

The handout uses `pdflatex` (no bibliography backend currently configured;
references are inline `\href`/`\footnote`). From `document/`:

```
pdflatex main.tex
pdflatex main.tex   # second pass for \pageref{LastPage}
```

LaTeX build artifacts (`*.aux`, `*.log`, `*.out`, etc.) and `document/main.pdf`
itself are gitignored. To version a specific PDF (e.g., the distributed
handout), copy it to a tracked path outside `document/` rather than
un-ignoring the build output.

## Debugging workspace

`workspace/` mirrors `code/` with every input file symlinked to its counterpart
in `code/`. It is gitignored, so output files, scratch data, and QE `*.save`
directories produced during a run never pollute the tracked tree.

To run an exercise locally, work from the corresponding `workspace/exerciseN/`
directory. New files created there (stdout logs, `*.save/`, `*.xml`, …) stay
untracked. The symlinked input files resolve to `code/exerciseN/*`, so edits to
inputs should be made in `code/`, not in `workspace/`.

If `workspace/` is ever missing or out of sync with `code/`, recreate it:

```bash
find code -type d | sed 's|^code|workspace|' | xargs mkdir -p
find code -type f | while read f; do
  rel="${f#code/}"
  ln -sf "$(pwd)/$f" "workspace/$rel"
done
```

## Running the exercises

`code/run.sh` targets Stampede3 (SLURM, `ibrun`, `-A DMR23030`, `skx`
partition) and points at a fixed QE build path
(`/work2/.../EPWSchool2024/q-e`). Update the partition, account, and
`PATHQE` for the target cluster before submitting.

Typical exercise flow: `pw.x` (scf) → `ph.x` → `pw.x` (nscf) → `pp.x` →
`epw.x` (and/or `ahc.x`). See each exercise's input files for the exact
order; the handout (`main.tex`) is the authoritative walkthrough.

## Editing conventions

- Keep `settings.tex` as the single source of shared LaTeX macros — don't
  duplicate them into the main file.
- When adding a new exercise, mirror the existing pattern: one directory
  under `code/`, self-contained inputs, optional `plot.py`.
- Pseudopotentials (`*.UPF`) are tracked in-tree so the tutorial is
  reproducible without external downloads.

## Commit messages

Keep commit messages to a single short line unless the user explicitly
asks for a longer body. No multi-line summaries, no bullet lists.

After every commit, push to origin immediately (`git push`).
