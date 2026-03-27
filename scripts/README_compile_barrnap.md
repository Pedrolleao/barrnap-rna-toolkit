# compile_barrnap.py

A Python script to compile and summarise **barrnap** RNA annotation outputs (GFF3 format) from a folder of MAG (Metagenome-Assembled Genome) files into structured tables. Optional flags activate deeper analyses of tRNA and rRNA content.

---

## Requirements

- Python 3.6+
- No external dependencies (standard library only)

---

## Input

### Folder structure

The script expects a single folder containing one barrnap GFF3 output file per MAG. All files must end with `.gff`.

```
input_folder/
├── GCA_000986845.1_ASM98684v1_genomic.fna-barrnap.gff
├── GCA_001563325.2_ASM156332v2_genomic.fna-barrnap.gff
├── GCA_001563335.2_ASM156333v2_genomic.fna-barrnap.gff
└── ...
```

Both naming conventions produced by barrnap are supported:
- Archaea/Bacteria runs: `<MAG>.fna-barrnap.gff`
- Eukaryote runs: `<MAG>.fna-barrnap_fun.gff`

The MAG identifier is extracted automatically from the filename (everything before `.fna-barrnap`).

### Input file format

Each file is a standard **GFF3** file as produced by barrnap (combining aragorn for tRNA/tmRNA and infernal for rRNA/ncRNA). The columns used by this script are:

| Column | Field      | Example                                      |
|--------|------------|----------------------------------------------|
| 1      | Scaffold   | `JYIM01000011.1`                             |
| 3      | RNA type   | `tRNA`, `rRNA`, `ncRNA`, `tmRNA`, `gene`     |
| 4      | Start      | `8012`                                       |
| 5      | Stop       | `8085`                                       |
| 7      | Strand     | `+` or `-`                                   |
| 9      | Info       | `Name=tRNA-Lys;product=transfer RNA (ctt)`   |

Example input file (`GCA_000986845.1_ASM98684v1_genomic.fna-barrnap.gff`):

```
##gff-version 3
JYIM01000011.1	aragorn:1.2.41	gene			.	-	.	Name=gene;product=transfer-messenger RNA
JYIM01000011.1	aragorn:1.2.41	tRNA	8012	8085	.	-	.	Name=tRNA-Lys;product=transfer RNA (ctt)
JYIM01000054.1	aragorn:1.2.41	gene			.	-	.	Name=gene;product=transfer-messenger RNA
JYIM01000054.1	aragorn:1.2.41	tRNA	14488	14560	.	+	.	Name=tRNA-Ala;product=transfer RNA (ggc)
JYIM01000225.1	infernal:1.1.5	ncRNA	18917	19237	2.9e-18	+	.	Name=RNaseP_arch;Dbxref=Rfam:RF00373;product=Archaeal RNase P
JYIM01000321.1	infernal:1.1.5	rRNA	1	1179	0	+	.	Name=16S_rRNA;Alias=SSU_rRNA_archaea;Dbxref=Rfam:RF01959;product=16S ribosomal RNA
JYIM01000373.1	infernal:1.1.5	rRNA	477	3826	0	+	.	Name=23S_rRNA;Alias=LSU_rRNA_archaea;Dbxref=Rfam:RF02540;product=23S ribosomal RNA
```

> **Note:** Bare `gene` stub rows emitted by aragorn (companion rows without coordinates) are automatically filtered out.

---

## Usage

```bash
python3 compile_barrnap.py <input_folder> [--output-prefix PREFIX] [--trna] [--rrna]
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `input_folder` | Yes | — | Path to folder containing barrnap `.gff` files |
| `--output-prefix` | No | `barrnap_compiled` | Prefix for all output file names |
| `--trna` | No | off | Generate detailed tRNA output files |
| `--rrna` | No | off | Generate detailed rRNA output files |

### Examples

**Basic run** — compile all annotations and generate general statistics:
```bash
python3 compile_barrnap.py arch/ --output-prefix arch_barrnap
```

**With tRNA analysis:**
```bash
python3 compile_barrnap.py arch/ --output-prefix arch_barrnap --trna
```

**With rRNA analysis:**
```bash
python3 compile_barrnap.py arch/ --output-prefix arch_barrnap --rrna
```

**Full run — all outputs at once:**
```bash
python3 compile_barrnap.py arch/ --output-prefix arch_barrnap --trna --rrna
```

---

## Outputs

All outputs are tab-separated (`.tsv`) files. The files generated depend on which flags are used.

---

### 1. `<prefix>_table.tsv` — Full annotation table *(always generated)*

A single table compiling all RNA annotations from all MAGs, with the MAG identifier as the first column.

| Column   | Description |
|----------|-------------|
| MAG      | MAG identifier extracted from the filename |
| Scaffold | Contig/scaffold name |
| RNA_type | Type of RNA feature (`tRNA`, `rRNA`, `ncRNA`, `tmRNA`, `gene`) |
| Start    | Start coordinate |
| Stop     | Stop coordinate |
| Strand   | Strand (`+` or `-`) |
| Info     | Raw GFF9 attributes field |

**Example:**

```
MAG                                     Scaffold         RNA_type  Start  Stop   Strand  Info
GCA_000986845.1_ASM98684v1_genomic      JYIM01000011.1   tRNA      8012   8085   -       Name=tRNA-Lys;product=transfer RNA (ctt)
GCA_000986845.1_ASM98684v1_genomic      JYIM01000054.1   tRNA      14488  14560  +       Name=tRNA-Ala;product=transfer RNA (ggc)
GCA_001563325.2_ASM156332v2_genomic     JBHLON010000003  rRNA      441    560    +       Name=5S_rRNA;Alias=5S_rRNA;Dbxref=Rfam:RF00001;product=5S ribosomal RNA
```

---

### 2. `<prefix>_stats.tsv` — Per-MAG RNA type counts *(always generated)*

One row per MAG with the count of each RNA type detected, plus a total.

| Column  | Description |
|---------|-------------|
| MAG     | MAG identifier |
| ncRNA   | Number of non-coding RNA annotations |
| rRNA    | Number of ribosomal RNA annotations |
| tRNA    | Number of transfer RNA annotations |
| tmRNA   | Number of transfer-messenger RNA annotations |
| Total   | Total RNA features for that MAG |

> Columns are dynamically generated from the data — only RNA types actually present in the dataset will appear.

**Example:**

```
MAG                                     ncRNA  rRNA  tRNA  tmRNA  Total
GCA_000986845.1_ASM98684v1_genomic      1      3     5     0      9
GCA_001563325.2_ASM156332v2_genomic     3      4     15    0      22
GCA_001563335.2_ASM156333v2_genomic     2      2     27    0      31
```

---

### 3. `<prefix>_tRNA_table.tsv` — Detailed tRNA table *(requires `--trna`)*

tRNA-only rows with the Info field parsed and split into individual columns.

| Column     | Description |
|------------|-------------|
| MAG        | MAG identifier |
| Scaffold   | Contig/scaffold name |
| Start      | Start coordinate |
| Stop       | Stop coordinate |
| Strand     | Strand (`+` or `-`) |
| tRNA_name  | Full tRNA name (e.g. `tRNA-Ala`) |
| Amino_acid | Three-letter amino acid code (e.g. `Ala`; `???` if unidentified) |
| Anticodon  | Anticodon sequence (e.g. `ggc`) |
| Product    | Product description (e.g. `transfer RNA (ggc)`) |

**Example:**

```
MAG                                     Scaffold         Start  Stop   Strand  tRNA_name  Amino_acid  Anticodon  Product
GCA_000986845.1_ASM98684v1_genomic      JYIM01000011.1   8012   8085   -       tRNA-Lys   Lys         ctt        transfer RNA (ctt)
GCA_000986845.1_ASM98684v1_genomic      JYIM01000054.1   14488  14560  +       tRNA-Ala   Ala         ggc        transfer RNA (ggc)
GCA_001563325.2_ASM156332v2_genomic     JBHLON010000001  3201   3274   +       tRNA-Arg   Arg         tcg        transfer RNA (tcg)
```

---

### 4. `<prefix>_tRNA_aa_pct.tsv` — Per-MAG amino acid coverage *(requires `--trna`)*

One row per MAG showing, for each amino acid, the **percentage** of the total tRNAs in that MAG that encode it. The last column gives the raw total tRNA count.

**Columns:** `MAG` | `Ala` | `Arg` | `Asn` | `Asp` | `Cys` | `Gln` | `Glu` | `Gly` | `His` | `Ile` | `Leu` | `Lys` | `Met` | `Phe` | `Pro` | `Ser` | `Thr` | `Trp` | `Tyr` | `Val` | `Pyl` | `SeC` | `Stop` | `???` | `Total_tRNA`

- The **20 canonical amino acids** always appear as columns, in alphabetical order.
- **Non-standard types** (`Pyl` = pyrrolysine, `SeC` = selenocysteine, `Stop` = suppressor tRNA, `???` = unidentified) are appended after the 20 canonical ones and are always present as columns even if absent from the dataset.
- Percentages are calculated over **all tRNAs** in that MAG (so each row sums to 100%).

**Example:**

```
MAG                                     Ala    Arg    Asn   Asp   Cys   Gln   ...  Val    Pyl   SeC   Stop  ???   Total_tRNA
GCA_000986845.1_ASM98684v1_genomic      20.00  0.00   0.00  0.00  0.00  0.00  ...  0.00   0.00  0.00  0.00  0.00  5
GCA_001563325.2_ASM156332v2_genomic     0.00   13.33  0.00  0.00  6.67  0.00  ...  6.67   0.00  0.00  0.00  0.00  15
GCA_001563335.2_ASM156333v2_genomic     11.11  14.81  0.00  0.00  3.70  7.41  ...  3.70   0.00  0.00  0.00  0.00  27
```

---

### 5. `<prefix>_rRNA_table.tsv` — Detailed rRNA table *(requires `--rrna`)*

rRNA-only rows with the Info field parsed and split into individual columns.

| Column    | Description |
|-----------|-------------|
| MAG       | MAG identifier |
| Scaffold  | Contig/scaffold name |
| Start     | Start coordinate |
| Stop      | Stop coordinate |
| Length    | Sequence length in bp (`Stop - Start + 1`) |
| Strand    | Strand (`+` or `-`) |
| rRNA_name | rRNA subunit name (e.g. `16S_rRNA`, `5S_rRNA`) |
| Alias     | Rfam alias (e.g. `SSU_rRNA_archaea`) |
| Rfam_ID   | Rfam accession number (e.g. `RF01959`) |
| Product   | Product description (e.g. `16S ribosomal RNA`) |

**Example:**

```
MAG                                     Scaffold         Start  Stop   Length  Strand  rRNA_name   Alias             Rfam_ID  Product
GCA_000986845.1_ASM98684v1_genomic      JYIM01000321.1   1      1179   1179    +       16S_rRNA    SSU_rRNA_archaea  RF01959  16S ribosomal RNA
GCA_000986845.1_ASM98684v1_genomic      JYIM01000373.1   477    3826   3350    +       23S_rRNA    LSU_rRNA_archaea  RF02540  23S ribosomal RNA
GCA_000986845.1_ASM98684v1_genomic      JYIM01000373.1   487    643    157     +       5.8S_rRNA   5_8S_rRNA         RF00002  5.8S ribosomal RNA
```

---

### 6. `<prefix>_rRNA_types_pct.tsv` — Per-MAG rRNA type coverage *(requires `--rrna`)*

One row per MAG showing, for each rRNA subunit type, the **percentage** of the total rRNAs in that MAG belonging to it. The last column gives the raw total rRNA count.

**Columns:** `MAG` | `5S_rRNA` | `5.8S_rRNA` | `16S_rRNA` | `18S_rRNA` | `23S_rRNA` | `28S_rRNA` | `Total_rRNA`

- The **6 known rRNA subunit types** (covering prokaryotic, archaeal, and eukaryotic) always appear as columns, in size order, even if absent from the dataset.
- Any **additional rRNA type** found in the data that is not in the known list is appended alphabetically at the end.
- Percentages are calculated over **all rRNAs** in that MAG (so each row sums to 100%).

**Example:**

```
MAG                                     5S_rRNA  5.8S_rRNA  16S_rRNA  18S_rRNA  23S_rRNA  28S_rRNA  Total_rRNA
GCA_000986845.1_ASM98684v1_genomic      0.00     33.33      33.33     0.00      33.33     0.00      3
GCA_001563325.2_ASM156332v2_genomic     0.00     25.00      75.00     0.00      0.00      0.00      4
GCA_001563335.2_ASM156333v2_genomic     50.00    0.00       50.00     0.00      0.00      0.00      2
```

---

## Output file summary

| File | Flag | Description |
|------|------|-------------|
| `<prefix>_table.tsv` | always | All RNA annotations from all MAGs |
| `<prefix>_stats.tsv` | always | Per-MAG counts by RNA type |
| `<prefix>_tRNA_table.tsv` | `--trna` | tRNA annotations with expanded Info columns |
| `<prefix>_tRNA_aa_pct.tsv` | `--trna` | Per-MAG % of tRNAs per amino acid + total count |
| `<prefix>_rRNA_table.tsv` | `--rrna` | rRNA annotations with expanded Info columns |
| `<prefix>_rRNA_types_pct.tsv` | `--rrna` | Per-MAG % of rRNAs per subunit type + total count |

---

## Notes

- The script prints a **progress log** to stderr as it reads each file, and a **global RNA type summary** to stdout on completion.
- Bare `gene` stub rows produced by aragorn (which lack coordinates) are automatically excluded from all outputs.
- The MAG identifier is always derived from the filename — no metadata file is required.
