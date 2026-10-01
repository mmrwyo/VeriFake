# VeriFake

Code and recorded results for fake news classification using TF-IDF and thirteen established classifiers.

Repository: https://github.com/mmrwyo/VeriFake

## Contents

- repair_verifake.py: experiment pipeline matching the completed run.
- verifake_text.py: text normalization and export support matching the completed run.
- verifake_arcc.slurm: adapted cluster launcher.
- render_saved_results.py: confusion-matrix and ROC plotting from saved outputs.
- requirements.txt: package versions recorded in the completed run.
- data/: input source URLs and SHA-256 checksums.
- results/tables/: classifier metrics, transfer results, ablations, intervals and paired comparisons.
- results/figures/: confusion matrices and ROC curves in PNG and vector PDF formats.
- results/predictions/: all 84 saved compressed prediction files and their available metadata.
- results/checkpoints/: 39 tuning records and corresponding CV tables, without model binaries.
- results/environment.json: recorded environment details.
- results/: completion records, run identity, split manifests and data audits.
- previous_results/: historical results used by the experiment's diagnostic comparison.
- SHA256SUMS.txt: file-integrity checksums for this package.

## Recorded experiment

Completed ARCC job 20840138 supplies these results. LinearSVC was selected by training cross-validation MCC. Accuracy is 98.15 percent on the random Kaggle test, 96.80 percent on the known-author-disjoint test, 71.49 percent from Kaggle to ISOT, and 58.47 percent in reverse. The system predicts dataset labels from text and does not verify claims against external evidence.

## Reproduction

Ask the project owner before running experiments, inference, statistical analysis or cluster jobs. No experimental code was rerun during this repository cleanup.

The original inputs are train.csv, Fake.csv and True.csv. Obtain them using data/README.md and match data/input_sha256.json before reproduction. Raw CSVs and fitted model binaries are not included. The recorded run used Python 3.11.16 and the package versions in requirements.txt; a fresh environment has not been tested here.

After approval, the experiment command from this directory is:

```sh
python repair_verifake.py --data data --previous previous_results --output verifake_repair_results --workers 8
```

The previous_results folder name is retained because the launcher and diagnostic command use that path. The portable launcher requires your allocation's account, partition and compatible environment. The plotting script uses the retained tables and prediction files.

## Data sources

The underlying news collections are Kaggle Fake News and the University of Victoria ISOT Fake News Dataset. Recorded acquisition mirrors and input hashes are in data/. ChatGPT assistance with acquisition and code does not mean the source articles were synthetic. Check the original data terms before redistribution. No code license has been assigned in this package.
