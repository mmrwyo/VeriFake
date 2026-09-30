# Upload the corrected VeriFake package

Repository: https://github.com/mmrwyo/VeriFake

Download VeriFake_CSDE_3824_Corrected_Package.zip into Downloads. The commands below upload every file in its prepared VeriFake repository folder. They do not run experiments or upload unrelated Downloads files.

## macOS or Linux Terminal

Use new destination folder names if these already exist.

```sh
cd ~/Downloads
unzip -q VeriFake_CSDE_3824_Corrected_Package.zip -d VeriFake_corrected_files
unzip -q VeriFake_corrected_files/VeriFake.zip -d VeriFake_corrected_files/repository
git clone https://github.com/mmrwyo/VeriFake.git VeriFake_corrected_upload
rsync -av --exclude='.git/' VeriFake_corrected_files/repository/VeriFake/ VeriFake_corrected_upload/
cd VeriFake_corrected_upload
git add .
git diff --cached --stat
git commit -m "Add corrected IEEE CSDE 2026 VeriFake package"
git push -u origin HEAD:main
```

Cloning first preserves existing history. An empty-repository warning is normal on a first upload. Authenticate using your GitHub credentials manager or token, never by adding credentials to a file. If Git says there is nothing to commit, proceed to the push. If the push is rejected, inspect the error and reconcile the remote changes without force-pushing.

## Check the upload

```sh
git status
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

The last two commit hashes should agree. Check README.md, manuscript/, results/tables/, results/figures/ and data/README.md on GitHub.

The repository contains code, all 84 saved prediction files, 39 tuning records, result tables, figures, manuscript sources and PDF, reviewer responses, source/checksum documentation, and handoff notes. Raw news CSVs, fitted model binaries, credentials and unrelated local files are excluded. No code license has been assigned. The upload commands do not rerun training, inference, bootstrap analysis or statistical tests.
