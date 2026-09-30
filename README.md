# VeriFake

Code, recorded results, and manuscript materials for:

VeriFake: A TF-IDF and Ensemble Learning Framework for Web-Based Fake News Detection

Accepted manuscript, IEEE CSDE 2026, paper ieee-csde_3824. The paper compares thirteen established classifiers with TF-IDF features, training-only selection, author-disjoint evaluation, bidirectional dataset transfer, and input ablations.

Project repository: https://github.com/mmrwyo/VeriFake

## Contents

- repair_verifake.py and verifake_text.py: scientific source matching the completed run's SHA-256 hashes.
- verifake_arcc.slurm: portable ARCC launcher adapted from the original job. Supply the account/partition and activate a compatible environment before use.
- requirements.txt: recorded package versions, not a newly tested installation environment.
- previous_results/: historical input records required for diagnostic comparisons. Do not use these as the manuscript's final results.
- results/tables/: final model comparisons, transfer, input ablation, confidence intervals and paired-test tables.
- results/predictions/: all 84 saved compressed prediction files.
- results/checkpoints/: 39 tuning/settings JSON records, without model binaries.
- results/figures/: the three manuscript figures, including editable SVG for Figure 1.
- results/: run identity, environment, data audit, split manifests and completion/provenance records.
- render_saved_results.py: redraws result figures using existing tables and prediction scores; it does not train classifiers.
- data/: recorded source URLs and exact input checksums. Raw news articles are not redistributed.
- manuscript/: corrected six-page IEEE conference PDF, editable source, reviewer response, reference audit and formatting checks.
- GITHUB_UPLOAD.md: upload commands that preserve remote history.

## Recorded results

Completed ARCC job 20840138 supplies the reported numbers. CV-selected LinearSVC achieves 98.15% random accuracy, 96.80% known-author-disjoint accuracy, 71.49% Kaggle-to-ISOT accuracy, and 58.47% ISOT-to-Kaggle accuracy. The model predicts dataset labels; it does not verify claims using external evidence.

## Reproduction

No experiment was rerun during the camera-ready update. Ask the project owner before any training, inference, statistical rerun or cluster submission.

After approval, obtain train.csv, Fake.csv and True.csv using data/README.md and verify data/input_sha256.json. The completed run used Python 3.11.16 and the listed versions. From this folder, the documented command is:

```sh
python repair_verifake.py --data data --previous previous_results --output verifake_repair_results --workers 8
```

For ARCC, activate the environment and submit verifake_arcc.slurm with your allocation's account and partition. The adapted launcher and a fresh installation have not been executed or validated during this preparation.

## Data and availability

The collections originate from Kaggle Fake News and ISOT, acquired through the mirrors recorded in data/README.md. ChatGPT assistance does not make the underlying articles synthetic. Consult the source terms before redistributing data. Trained weights, Django deployment files, raw article CSVs and account credentials are not included. The code has no newly assigned license in this package.

## Assistance disclosure

OpenAI ChatGPT assisted with code preparation, figure scripts and manuscript wording. Numerical results come from the recorded experiment. Authors remain responsible for the final content.

## Conference format correction

The current paper uses the supplied unchanged IEEE conference class and the finalized SignLink author-block and header/footer layout. Figure 1 follows the supplied four-panel grayscale style with VeriFake processes. The paper retains 22 references. External PDF eXpress, screening and portal-author checks remain outstanding; see VeriFake_VALIDATION_NOTES.md.
