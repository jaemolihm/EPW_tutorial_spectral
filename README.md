# EPW School 2026 — Spectral Function Tutorial

Hands-on materials for the EPW School 2026 session on Wannier function
perturbation theory (WFPT) and electron/phonon spectral functions
(Quantum ESPRESSO + EPW).

## Layout

- `document/` — LaTeX source of the handout (`main.tex`, `settings.tex`).
- `code/` — input files for the four exercises (`exerciseN/`), plus `run.sh`.
- `gen_appendix.py` — regenerates the Python-scripts appendix in `main.tex`.
- `Makefile` — builds and distributes the handout + code.
- `tutorial.pdf` — versioned snapshot of the handout.
- `workspace/` — gitignored scratch area (symlinks to `code/`) for running locally.

## Building (`make`)

- `make pdf` — build the handout (`pdflatex` ×2) → `Thu.5.Lihm.pdf`.
- `make tar` — package `code/` → `Thu.5.Lihm.tar`.
- `make push` — upload both artifacts to the shared Google Drive (rclone).
- `make` — `pdf` + `tar` + `push`.
- `make clean` — remove the built artifacts.

(`make frontera` scps the tar to Frontera; run manually, needs 2FA.)

## Regenerating the appendix (`gen_appendix.py`)

The handout's "Python post-processing scripts" appendix is generated from the
actual scripts in `code/`. After editing any of those scripts, run:

```
python3 gen_appendix.py   # rewrites the appendix in document/main.tex
make pdf                  # rebuild the PDF
```

It is idempotent (re-running replaces the appendix, never duplicates it). Edit
the `SCRIPTS` list in `gen_appendix.py` to add or reorder scripts.
