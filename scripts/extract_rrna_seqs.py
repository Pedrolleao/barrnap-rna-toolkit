#!/usr/bin/env python3
"""
extract_rrna_seqs.py
--------------------
Extract rRNA sequences from MAG FASTA files using the coordinates in the
barrnap annotation table produced by compile_barrnap.py.

One FASTA file is created per rRNA type (e.g. 16S_rRNA.fasta, 23S_rRNA.fasta).
Each sequence header contains the MAG name, scaffold, coordinates, strand,
rRNA type, alias, Rfam accession, and product description so every sequence
is fully traceable.

Usage:
    python extract_rrna_seqs.py <table.tsv> <fna_folder> [--output-dir DIR]

Arguments:
    table        The *_table.tsv produced by compile_barrnap.py.
    fna_folder   Folder containing the original MAG .fna files.
    --output-dir Directory for output FASTA files (default: current directory).
"""

import os
import sys
import argparse
from collections import defaultdict


# ─── Sequence utilities ────────────────────────────────────────────────────────

_COMPLEMENT = str.maketrans("ACGTacgtNnRrYyKkMmSsWwBbDdHhVv",
                             "TGCAtgcaNnYyRrMmKkSsWwVvHhDdBb")

def reverse_complement(seq):
    return seq.translate(_COMPLEMENT)[::-1]


def format_fasta(header, seq):
    """Return a FASTA-format string with the sequence on a single line."""
    return f"{header}\n{seq}"


# ─── Parsing helpers ───────────────────────────────────────────────────────────

def parse_gff_info(info):
    """Split a GFF9 Info string into a key→value dict."""
    fields = {}
    for part in info.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            fields[k.strip()] = v.strip()
    return fields


def read_rrna_records(table_path):
    """
    Read the barrnap table and return rRNA records grouped by MAG.

    Returns:
        dict: {mag_name: [record_dict, ...]}
    """
    mag_records = defaultdict(list)

    with open(table_path) as fh:
        fh.readline()  # skip header
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7:
                continue
            mag, scaffold, rna_type, start, stop, strand, info = parts[:7]
            if rna_type != "rRNA":
                continue
            try:
                mag_records[mag].append({
                    "mag":      mag,
                    "scaffold": scaffold,
                    "start":    int(start),
                    "stop":     int(stop),
                    "strand":   strand,
                    "info":     info,
                })
            except ValueError:
                # Skip rows with non-integer coordinates
                continue

    return mag_records


def find_fna_file(fna_folder, mag_name):
    """
    Locate the .fna file for a given MAG name.
    Tries an exact match first, then a prefix match as fallback.
    """
    exact = os.path.join(fna_folder, mag_name + ".fna")
    if os.path.isfile(exact):
        return exact
    for fn in sorted(os.listdir(fna_folder)):
        if fn.startswith(mag_name) and fn.endswith(".fna"):
            return os.path.join(fna_folder, fn)
    return None


def parse_fasta(fna_path):
    """
    Parse a (possibly multi-contig) FASTA file.

    Returns:
        dict: {scaffold_id: sequence_string}
        Scaffold ID is the first whitespace-delimited token on the header line.
    """
    sequences = {}
    current_id = None
    buf = []

    with open(fna_path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if current_id is not None:
                    sequences[current_id] = "".join(buf)
                current_id = line[1:].split()[0]
                buf = []
            else:
                buf.append(line)

    if current_id is not None:
        sequences[current_id] = "".join(buf)

    return sequences


# ─── FASTA header builder ──────────────────────────────────────────────────────

def build_header(rec, info_fields):
    """
    Construct a concise FASTA header for one rRNA sequence.

    Format:
      >MAG#scaffold#start-stop#strand#rRNA_type
    Fields are separated by '#'; no key= prefixes.
    """
    rrna_name = info_fields.get("Name", "unknown_rRNA")

    return (
        f">{rec['mag']}"
        f"#{rec['scaffold']}"
        f"#{rec['start']}-{rec['stop']}"
        f"#{rec['strand']}"
        f"#{rrna_name}"
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract rRNA sequences from MAG FASTA files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "table",
        help="Barrnap annotation table (*_table.tsv from compile_barrnap.py).",
    )
    parser.add_argument(
        "fna_folder",
        help="Folder containing the original MAG .fna files.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for output FASTA files (default: current directory).",
    )
    args = parser.parse_args()

    # ── Validate inputs ──
    if not os.path.isfile(args.table):
        print(f"ERROR: Table file not found: '{args.table}'", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.fna_folder):
        print(f"ERROR: FNA folder not found: '{args.fna_folder}'", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    # ── Read rRNA records ──
    print("Reading annotation table...", file=sys.stderr)
    mag_records = read_rrna_records(args.table)

    if not mag_records:
        print("No rRNA records found in the table. Exiting.", file=sys.stderr)
        sys.exit(0)

    total_mags   = len(mag_records)
    total_records = sum(len(v) for v in mag_records.values())
    print(f"Found {total_records} rRNA annotations across {total_mags} MAGs.",
          file=sys.stderr)

    # ── Extract sequences ──
    # rrna_sequences: {rRNA_type: [(header, seq), ...]}
    rrna_sequences  = defaultdict(list)
    n_extracted     = 0
    n_missing_fna   = 0
    n_missing_scaf  = 0

    for i, (mag, records) in enumerate(sorted(mag_records.items()), 1):

        fna_path = find_fna_file(args.fna_folder, mag)
        if fna_path is None:
            print(f"  [{i}/{total_mags}] WARNING: no .fna found for '{mag}'"
                  f" — skipping {len(records)} record(s)", file=sys.stderr)
            n_missing_fna += len(records)
            continue

        print(f"  [{i}/{total_mags}] {os.path.basename(fna_path)}"
              f"  ({len(records)} rRNA record(s))", file=sys.stderr)

        scaffolds = parse_fasta(fna_path)

        for rec in records:
            scaffold = rec["scaffold"]

            if scaffold not in scaffolds:
                print(f"    WARNING: scaffold '{scaffold}' not found in"
                      f" {os.path.basename(fna_path)} — skipping", file=sys.stderr)
                n_missing_scaf += 1
                continue

            # GFF coordinates are 1-based, fully inclusive
            full_seq = scaffolds[scaffold]
            subseq   = full_seq[rec["start"] - 1 : rec["stop"]]

            if rec["strand"] == "-":
                subseq = reverse_complement(subseq)

            info_fields = parse_gff_info(rec["info"])
            rrna_type   = info_fields.get("Name", "unknown_rRNA")
            header      = build_header(rec, info_fields)

            rrna_sequences[rrna_type].append((header, subseq))
            n_extracted += 1

    # ── Write output FASTA files ──
    print(f"\nWriting FASTA files to '{args.output_dir}'...", file=sys.stderr)

    for rrna_type, entries in sorted(rrna_sequences.items()):
        out_path = os.path.join(args.output_dir, f"{rrna_type}.fasta")
        with open(out_path, "w") as fh:
            for j, (header, seq) in enumerate(entries):
                if j > 0:
                    fh.write("\n")
                fh.write(format_fasta(header, seq) + "\n")
        print(f"  {rrna_type}.fasta  —  {len(entries)} sequences", file=sys.stderr)

    # ── Summary ──
    print(f"\n{'─'*50}", file=sys.stderr)
    print(f"Sequences extracted:  {n_extracted}", file=sys.stderr)
    if n_missing_fna:
        print(f"Skipped (no .fna):    {n_missing_fna}", file=sys.stderr)
    if n_missing_scaf:
        print(f"Skipped (no scaffold):{n_missing_scaf}", file=sys.stderr)


if __name__ == "__main__":
    main()
