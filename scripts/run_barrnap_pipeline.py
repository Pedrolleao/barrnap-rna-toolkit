#!/usr/bin/env python3
"""
run_barrnap_pipeline.py
-----------------------
Wrapper that runs the full barrnap post-processing pipeline:

  Step 1 — compile_barrnap.py
      Compiles all barrnap GFF outputs in a folder into summary tables.
      Always runs with --trna and --rrna flags.
      The output prefix defaults to the name of the GFF folder.

  Step 2 — extract_rrna_seqs.py  (only if <fna_folder> is supplied)
      Extracts rRNA sequences from the original MAG FASTA files using the
      annotation table produced in step 1.

Usage:
    python run_barrnap_pipeline.py <gff_folder> [fna_folder] [--output-dir DIR]

Arguments:
    gff_folder        Folder containing barrnap .gff output files.
    fna_folder        (optional) Folder containing the original MAG .fna files.
                      Required for the sequence-extraction step. If omitted,
                      the pipeline stops after the table-compilation step.
    --output-dir DIR  Directory for all output files (default: current directory).
    --output-prefix   Override the output-file prefix (default: basename of
                      gff_folder).

Outputs (always):
    <prefix>_table.tsv          - Full annotation table.
    <prefix>_stats.tsv          - Per-MAG RNA type count statistics.
    <prefix>_tRNA_table.tsv     - tRNA-only table with split Info columns.
    <prefix>_tRNA_aa_pct.tsv    - Per-MAG amino acid % coverage + total tRNA count.
    <prefix>_rRNA_table.tsv     - rRNA-only table with split Info columns.
    <prefix>_rRNA_types_pct.tsv - Per-MAG rRNA type % coverage + total rRNA count.

Outputs (only when fna_folder is supplied):
    <output_dir>/<rRNA_type>.fasta  - One FASTA per rRNA type (e.g. 16S_rRNA.fasta).
"""

import os
import sys
import argparse
import subprocess


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _script_dir():
    """Return the directory that contains this wrapper script."""
    return os.path.dirname(os.path.realpath(__file__))


def _find_sibling(name):
    """Return the absolute path to a script in the same directory as this file."""
    path = os.path.join(_script_dir(), name)
    if not os.path.isfile(path):
        print(f"ERROR: Cannot find '{name}' in {_script_dir()}", file=sys.stderr)
        sys.exit(1)
    return path


def _run(cmd, step_label):
    """Run a subprocess command, streaming output, and exit on failure."""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  {step_label}", file=sys.stderr)
    print(f"  Command: {' '.join(cmd)}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(
            f"\nERROR: {step_label} exited with code {result.returncode}.",
            file=sys.stderr,
        )
        sys.exit(result.returncode)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run the full barrnap post-processing pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "gff_folder",
        help="Folder containing barrnap .gff output files.",
    )
    parser.add_argument(
        "fna_folder",
        nargs="?",
        default=None,
        help=(
            "Folder containing the original MAG .fna files. "
            "Required for the rRNA sequence-extraction step. "
            "If omitted, the pipeline stops after table compilation."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for all output files (default: current directory).",
    )
    parser.add_argument(
        "--output-prefix",
        default=None,
        help=(
            "Prefix for output files. "
            "Defaults to the basename of gff_folder."
        ),
    )
    args = parser.parse_args()

    # ── Validate inputs ──────────────────────────────────────────────────────
    gff_folder = args.gff_folder.rstrip("/")
    if not os.path.isdir(gff_folder):
        print(f"ERROR: '{gff_folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    if args.fna_folder is not None:
        fna_folder = args.fna_folder.rstrip("/")
        if not os.path.isdir(fna_folder):
            print(f"ERROR: '{fna_folder}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)
    else:
        fna_folder = None

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    prefix_name = args.output_prefix or os.path.basename(os.path.abspath(gff_folder))
    prefix_path = os.path.join(output_dir, prefix_name)

    # ── Locate sibling scripts ───────────────────────────────────────────────
    compile_script  = _find_sibling("compile_barrnap.py")
    extract_script  = _find_sibling("extract_rrna_seqs.py")

    # ── Step 1: compile_barrnap.py ───────────────────────────────────────────
    compile_cmd = [
        sys.executable, compile_script,
        gff_folder,
        "--output-prefix", prefix_path,
        "--trna",
        "--rrna",
    ]
    _run(compile_cmd, "Step 1 — compile_barrnap.py")

    table_path = f"{prefix_path}_table.tsv"
    if not os.path.isfile(table_path):
        print(f"ERROR: Expected output '{table_path}' not found.", file=sys.stderr)
        sys.exit(1)

    # ── Step 2: extract_rrna_seqs.py (optional) ──────────────────────────────
    if fna_folder is None:
        print(
            "\nNo fna_folder supplied — skipping rRNA sequence extraction.",
            file=sys.stderr,
        )
        print(
            "To extract sequences, re-run with the path to the .fna folder as the "
            "second argument.",
            file=sys.stderr,
        )
    else:
        extract_cmd = [
            sys.executable, extract_script,
            table_path,
            fna_folder,
            "--output-dir", output_dir,
        ]
        _run(extract_cmd, "Step 2 — extract_rrna_seqs.py")

    print(f"\nPipeline complete. Outputs are in: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
