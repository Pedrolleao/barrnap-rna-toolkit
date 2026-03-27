# run_barrnap_pipeline.py

A Python wrapper that runs the full barrnap post-processing pipeline in a single command. It sequentially executes `compile_barrnap.py` (table compilation) and, when a FASTA folder is supplied, `extract_rrna_seqs.py` (rRNA sequence extraction). Both sibling scripts must be present in the same directory as this wrapper.

---

## Requirements

- Python 3.6+
- No external dependencies (standard library only)
- `compile_barrnap.py` and `extract_rrna_seqs.py` must be in the same directory as this script

---

## Pipeline steps

| Step | Script | Triggered by |
|------|--------|--------------|
| 1 | `compile_barrnap.py` | always |
| 2 | `extract_rrna_seqs.py` | only when `fna_folder` is supplied |

---

## Input

### Required

| Argument | Description |
|----------|-------------|
| `gff_folder` | Folder containing barrnap `.gff` output files (one per MAG) |

### Optional

| Argument | Description |
|----------|-------------|
| `fna_folder` | Folder containing the original MAG `.fna` files. Required for the rRNA sequence-extraction step (Step 2). If omitted, the pipeline stops after table compilation. |

### Folder structure example

```
gff_folder/
├── GCA_000986845.1_ASM98684v1_genomic.fna-barrnap.gff
├── GCA_001563325.2_ASM156332v2_genomic.fna-barrnap.gff
└── ...

fna_folder/
├── GCA_000986845.1_ASM98684v1_genomic.fna
├── GCA_001563325.2_ASM156332v2_genomic.fna
└── ...
```

The MAG identifiers in the GFF filenames must match the base names of the `.fna` files (filename without the `.fna` extension). See the `extract_rrna_seqs.py` README for matching details.

---

## Usage

```bash
python3 run_barrnap_pipeline.py <gff_folder> [fna_folder] [--output-dir DIR] [--output-prefix PREFIX]
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `gff_folder` | Yes | — | Folder containing barrnap `.gff` output files |
| `fna_folder` | No | — | Folder containing the original MAG `.fna` files |
| `--output-dir` | No | `.` (current directory) | Directory for all output files |
| `--output-prefix` | No | basename of `gff_folder` | Prefix for the compiled output files |

### Examples

**Step 1 only** — compile tables (no sequence extraction):
```bash
python3 run_barrnap_pipeline.py arch_barrnap/
```

**Full pipeline** — compile tables and extract rRNA sequences:
```bash
python3 run_barrnap_pipeline.py arch_barrnap/ arch_fna/
```

**Write all outputs to a dedicated folder:**
```bash
python3 run_barrnap_pipeline.py arch_barrnap/ arch_fna/ --output-dir results/
```

**Override the output-file prefix:**
```bash
python3 run_barrnap_pipeline.py arch_barrnap/ arch_fna/ --output-dir results/ --output-prefix asgard_arch
```

---

## Outputs

### Step 1 — `compile_barrnap.py` outputs *(always generated)*

All files are tab-separated (`.tsv`) and written to `--output-dir`. The filename prefix defaults to the basename of `gff_folder` (e.g. folder `arch_barrnap/` → prefix `arch_barrnap`).

| File | Description |
|------|-------------|
| `<prefix>_table.tsv` | Full annotation table — all RNA annotations across all MAGs |
| `<prefix>_stats.tsv` | Per-MAG RNA type count statistics |
| `<prefix>_tRNA_table.tsv` | tRNA-only table with Info field split into individual columns |
| `<prefix>_tRNA_aa_pct.tsv` | Per-MAG amino acid % coverage + total tRNA count |
| `<prefix>_rRNA_table.tsv` | rRNA-only table with Info field split into individual columns |
| `<prefix>_rRNA_types_pct.tsv` | Per-MAG rRNA subunit type % coverage + total rRNA count |

> `--trna` and `--rrna` are always passed to `compile_barrnap.py` by this wrapper, so all six files above are always produced.

See the `compile_barrnap.py` README for full column descriptions and example output.

### Step 2 — `extract_rrna_seqs.py` outputs *(only when `fna_folder` is supplied)*

One FASTA file per rRNA type, written to `--output-dir`.

| File | Description |
|------|-------------|
| `16S_rRNA.fasta` | All 16S rRNA sequences across all MAGs |
| `23S_rRNA.fasta` | All 23S rRNA sequences across all MAGs |
| `5S_rRNA.fasta` | All 5S rRNA sequences across all MAGs |
| `*.fasta` | One file per rRNA type found in the annotation table |

Sequence headers follow the format:

```
>MAG#scaffold#start-stop#strand#rRNA_type
```

Example:
```
>GCA_000986845.1_ASM98684v1_genomic#JYIM01000321.1#1-1179#+#16S_rRNA
```

Sequences on the minus strand are automatically reverse-complemented. See the `extract_rrna_seqs.py` README for full details.

---

## Output file summary

```
output_dir/
├── <prefix>_table.tsv           ← Step 1 (always)
├── <prefix>_stats.tsv           ← Step 1 (always)
├── <prefix>_tRNA_table.tsv      ← Step 1 (always)
├── <prefix>_tRNA_aa_pct.tsv     ← Step 1 (always)
├── <prefix>_rRNA_table.tsv      ← Step 1 (always)
├── <prefix>_rRNA_types_pct.tsv  ← Step 1 (always)
├── 16S_rRNA.fasta               ← Step 2 (only with fna_folder)
├── 23S_rRNA.fasta               ← Step 2 (only with fna_folder)
└── ...
```

---

## Notes

- The wrapper locates `compile_barrnap.py` and `extract_rrna_seqs.py` relative to its own location, so it can be called from any working directory.
- Each step's command is printed to stderr before execution, making the pipeline easy to reproduce manually if needed.
- If `fna_folder` is omitted, a message is printed to stderr explaining how to re-run with sequence extraction enabled. No error is raised.
- The `<prefix>_table.tsv` produced in Step 1 is passed directly to Step 2 — no manual file handling is required between steps.
