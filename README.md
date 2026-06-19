# barrnap-rna-toolkit

A suite of Python command-line tools for compiling, summarising, and extracting RNA annotations produced by **barrnap** across collections of MAGs (Metagenome-Assembled Genomes).

[![CI](https://github.com/Pedrolleao/barrnap-rna-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Pedrolleao/barrnap-rna-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Tools

| Tool | Description |
|------|-------------|
| **compile_barrnap** | Compile all barrnap GFF outputs from a folder into annotation tables and per-MAG statistics. Optional flags activate detailed tRNA and rRNA breakdowns. |
| **extract_rrna_seqs** | Extract rRNA sequences from MAG FASTA files using the annotation table produced by `compile_barrnap`. Writes one FASTA file per rRNA type with fully traceable sequence headers. |
| **run_barrnap_pipeline** | Wrapper that runs `compile_barrnap` and `extract_rrna_seqs` sequentially in a single command. |

---

## Installation

```bash
git clone https://github.com/Pedrolleao/barrnap-rna-toolkit.git
cd barrnap-rna-toolkit/scripts
```

No installation required. All scripts use the Python standard library only (Python 3.6+).

---

## Quick start

**Compile all barrnap GFF outputs into tables:**
```bash
python3 scripts/compile_barrnap.py gff_folder/ --output-prefix my_run --trna --rrna
```

**Extract rRNA sequences from MAG FASTA files:**
```bash
python3 scripts/extract_rrna_seqs.py my_run_table.tsv fna_folder/ --output-dir rrna_seqs/
```

**Run the full pipeline in one command:**
```bash
python3 scripts/run_barrnap_pipeline.py gff_folder/ fna_folder/ --output-dir results/
```

---

## Documentation

Each tool has its own detailed README:

- **compile_barrnap** — [`scripts/README_compile_barrnap.md`](scripts/README_compile_barrnap.md)
- **extract_rrna_seqs** — [`scripts/README_extract_rrna_seqs.md`](scripts/README_extract_rrna_seqs.md)
- **run_barrnap_pipeline** — [`scripts/README_run_barrnap_pipeline.md`](scripts/README_run_barrnap_pipeline.md)

---

## Requirements

- Python 3.6 or newer
- No external dependencies (standard library only)
- barrnap GFF output files as input (produced by [barrnap](https://github.com/tseemann/barrnap))

---

## License

MIT — see [LICENSE](LICENSE).
