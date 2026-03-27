# extract_rrna_seqs.py

A Python script to extract **rRNA sequences** from MAG FASTA files using the coordinates in a barrnap annotation table produced by `compile_barrnap.py`. One FASTA file is written per rRNA type, with fully traceable sequence headers.

---

## Requirements

- Python 3.6+
- No external dependencies (standard library only)

---

## Input

### Required files

The script takes two inputs: the `*_table.tsv` produced by `compile_barrnap.py` and a folder of the original MAG `.fna` files used to run barrnap.

```
input_folder/
├── GCA_000986845.1_ASM98684v1_genomic.fna
├── GCA_001563325.2_ASM156332v2_genomic.fna
├── GCA_001563335.2_ASM156333v2_genomic.fna
└── ...
```

The MAG identifiers in the table must match the base names of the `.fna` files (the filename without the `.fna` extension). The script first tries an exact match and falls back to a prefix match if no exact file is found.

### Annotation table format

The `*_table.tsv` file is the tab-separated table produced by `compile_barrnap.py` (the `--rrna` flag is **not** required; the base table is sufficient). The columns used by this script are:

| Column   | Field    | Example                                                              |
|----------|----------|----------------------------------------------------------------------|
| 1        | MAG      | `GCA_000986845.1_ASM98684v1_genomic`                                 |
| 2        | Scaffold | `JYIM01000321.1`                                                     |
| 3        | RNA_type | `rRNA` (only rows where this equals `rRNA` are processed)            |
| 4        | Start    | `1`                                                                  |
| 5        | Stop     | `1179`                                                               |
| 6        | Strand   | `+` or `-`                                                           |
| 7        | Info     | `Name=16S_rRNA;Alias=SSU_rRNA_archaea;Dbxref=Rfam:RF01959;product=16S ribosomal RNA` |

Example input table (`arch_barrnap_table.tsv`, rRNA rows only):

```
MAG                                     Scaffold         RNA_type  Start  Stop   Strand  Info
GCA_000986845.1_ASM98684v1_genomic      JYIM01000321.1   rRNA      1      1179   +       Name=16S_rRNA;Alias=SSU_rRNA_archaea;Dbxref=Rfam:RF01959;product=16S ribosomal RNA
GCA_000986845.1_ASM98684v1_genomic      JYIM01000373.1   rRNA      477    3826   +       Name=23S_rRNA;Alias=LSU_rRNA_archaea;Dbxref=Rfam:RF02540;product=23S ribosomal RNA
GCA_000986845.1_ASM98684v1_genomic      JYIM01000373.1   rRNA      487    643    +       Name=5.8S_rRNA;Alias=5_8S_rRNA;Dbxref=Rfam:RF00002;product=5.8S ribosomal RNA
```

### FASTA file format

Each `.fna` file is a standard multi-contig FASTA file. The scaffold identifier used for coordinate lookup is the first whitespace-delimited token on the header line.

Example:

```
>JYIM01000321.1 MAG: Candidatus Lokiarchaeum sp. GC14_75 isolate GC14_75 ...
ATGCTAGCTAGCTAGCATCGATCGATCGATCGATCGATCGTAGCTAGCTAGCATCG...
>JYIM01000373.1 MAG: Candidatus Lokiarchaeum sp. GC14_75 isolate GC14_75 ...
GCTAGCTAGCTAGCTAGCTAGCATCGATCGATCGATCGATCGATCGTAGCTAGCTA...
```

---

## Usage

```bash
python3 extract_rrna_seqs.py <table.tsv> <fna_folder> [--output-dir DIR]
```

### Arguments

| Argument       | Required | Default | Description                                                    |
|----------------|----------|---------|----------------------------------------------------------------|
| `table`        | Yes      | —       | Barrnap annotation table (`*_table.tsv` from `compile_barrnap.py`) |
| `fna_folder`   | Yes      | —       | Folder containing the original MAG `.fna` files               |
| `--output-dir` | No       | `.`     | Directory for output FASTA files (default: current directory) |

### Examples

**Basic run** — extract rRNA sequences to the current directory:
```bash
python3 extract_rrna_seqs.py arch_barrnap_table.tsv ../fna/
```

**Write output to a dedicated folder:**
```bash
python3 extract_rrna_seqs.py arch_barrnap_table.tsv ../fna/ --output-dir rrna_seqs_arch/
```

---

## Output

One FASTA file is created per rRNA type found in the annotation table. The filename matches the rRNA type name as it appears in the `Name=` field of the GFF3 attributes (e.g. `16S_rRNA.fasta`).

```
output_dir/
├── 16S_rRNA.fasta
├── 23S_rRNA.fasta
├── 5.8S_rRNA.fasta
└── 5S_rRNA.fasta
```

### Sequence header format

Each sequence header encodes five fields separated by `#`, with no key prefixes:

```
>MAG#scaffold#start-stop#strand#rRNA_type
```

| Field      | Description                                          | Example                                   |
|------------|------------------------------------------------------|-------------------------------------------|
| MAG        | MAG identifier (from the annotation table)           | `GCA_000986845.1_ASM98684v1_genomic`      |
| scaffold   | Contig/scaffold name                                 | `JYIM01000321.1`                          |
| start-stop | GFF3 coordinates (1-based, fully inclusive)          | `1-1179`                                  |
| strand     | Strand the feature is encoded on                     | `+`                                       |
| rRNA_type  | rRNA subunit name from the `Name=` attribute         | `16S_rRNA`                                |

**Example headers:**

```
>GCA_000986845.1_ASM98684v1_genomic#JYIM01000321.1#1-1179#+#16S_rRNA
>GCA_000986845.1_ASM98684v1_genomic#JYIM01000373.1#477-3826#+#23S_rRNA
>GCA_001563325.2_ASM156332v2_genomic#JBHLON010000003#441-560#+#5S_rRNA
```

### FASTA format

Sequences are written on a single (unwrapped) line — no line-length limit is applied.

**Example output (`16S_rRNA.fasta`):**

```
>GCA_000986845.1_ASM98684v1_genomic#JYIM01000321.1#1-1179#+#16S_rRNA
ATGCTAGCTAGCTAGCATCGATCGATCGATCGATCGATCGTAGCTAGCTAGCATCGATCGATCGATCGATCGTAGCTAGC...
>GCA_001563325.2_ASM156332v2_genomic#JBHLON010000004#1-1197#+#16S_rRNA
GCTAGCTAGCTAGCTAGCTAGCATCGATCGATCGATCGATCGATCGTAGCTAGCTAGCTAGCTAGCATCGATCGATCGAT...
```

### Strand handling

Sequences on the minus strand (`-`) are automatically reverse-complemented before writing. IUPAC ambiguity codes (`R`, `Y`, `K`, `M`, `S`, `W`, `B`, `D`, `H`, `V`, `N`) are handled correctly.

---

## Output file summary

| File              | Description                                      |
|-------------------|--------------------------------------------------|
| `16S_rRNA.fasta`  | All 16S rRNA sequences across all MAGs           |
| `23S_rRNA.fasta`  | All 23S rRNA sequences across all MAGs           |
| `5S_rRNA.fasta`   | All 5S rRNA sequences across all MAGs            |
| `5.8S_rRNA.fasta` | All 5.8S rRNA sequences across all MAGs          |
| `*.fasta`         | One file per rRNA type found in the input table  |

> The files generated depend on the rRNA types present in the annotation table. Only types with at least one annotation produce an output file.

---

## Notes

- The script prints a **progress log** to stderr listing each MAG processed, the number of rRNA records it carries, and any warnings about missing `.fna` files or scaffolds not found in the assembly.
- A **summary** is printed to stderr on completion reporting the total number of sequences extracted and the count of any skipped records.
- GFF3 coordinates are **1-based and fully inclusive**. The script converts them to the correct 0-based Python slice internally (`seq[start-1:stop]`).
- The MAG identifier is always taken from the annotation table, not derived from the `.fna` filename — ensuring the header exactly matches the source of the annotation.
- Only rows with `RNA_type == rRNA` in the annotation table are processed; tRNA, ncRNA, and tmRNA rows are ignored.
