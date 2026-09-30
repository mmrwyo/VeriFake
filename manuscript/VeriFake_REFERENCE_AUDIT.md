# VeriFake reference and link audit

Checked 30 September 2026. The revised manuscript contains 22 references, nine more than the preceding version. New entries are [3], [5], [6], [7], [9], [11], [12], [13], and [22]. All 22 are cited in the manuscript in first-citation order. DOI strings and previously unlinked JMLR entries are clickable in the PDF.

Publication identity and live link access are different checks. Publication/documentation records support 21 entries. The original Kaggle competition attribution is supported by the supplied experiment provenance, but its live page could not be independently retrieved. Some correct publisher DOI links were inaccessible to the checking service; accessible primary alternatives are recorded below. No guarantee of universal or permanent link access is made.

The added references support the survey context, dataset distinctions, recent LLM work, leakage safeguards, and MCC. Their published scores are not presented as matched experimental baselines. LIAR, FakeNewsNet, FEVER and TripleFact were not evaluated in the VeriFake experiment.

## [1] Kishi et al., 2026

Purpose: Dataset and annotation bias.

Link: https://aclanthology.org/2026.eacl-srw.47/

Check: ACL record opened; title, authors, year, pages and DOI match.

## [2] Verhoeven et al., 2026

Purpose: Generalization across multiple axes.

Link: https://aclanthology.org/2026.cl-2.6/

Check: ACL journal record opened; 52(2), 619-675 and DOI match. Direct DOI fetch was restricted.

## [3] Zhou and Zafarani, 2020

Purpose: Knowledge, style, propagation and source taxonomy.

Link: https://doi.org/10.1145/3395046

Check: ACM access restricted. Author preprint https://arxiv.org/abs/1812.00315 and institutional record https://experts.boisestate.edu/en/publications/a-survey-of-fake-news-fundamental-theories-detection-methods-and-/ opened; article 109 and publication details verified.

## [4] Ahmed et al., 2018

Purpose: N-gram classification and ISOT attribution.

Link: https://onlinelibrary.wiley.com/doi/abs/10.1002/spy2.9

Check: Publisher record opened; title, authors, year, e9 and DOI match.

## [5] Wang, 2017

Purpose: LIAR short-statement benchmark.

Link: https://aclanthology.org/P17-2067/

Check: ACL record opened; title, author, year, 422-426 and DOI match.

## [6] Shu et al., 2020

Purpose: FakeNewsNet news and social context.

Link: https://journals.sagepub.com/doi/10.1089/big.2020.0062

Check: Publisher record opened; author-hosted publication PDF https://suhangwang.ist.psu.edu/publications/FakeNewsNet.pdf also opened; 8(3), 171-188 and DOI match.

## [7] Thorne et al., 2018

Purpose: FEVER evidence-based claim verification.

Link: https://aclanthology.org/N18-1074/

Check: ACL record opened; four authors, 809-819 and DOI match.

## [8] Liu et al., 2024

Purpose: TELLER cognition and decision framework.

Link: https://aclanthology.org/2024.findings-acl.919/

Check: ACL record opened; four authors, 15556-15583 and DOI match.

## [9] Ma et al., 2024

Purpose: LLM-enhanced topic and entity semantics.

Link: https://aclanthology.org/2024.emnlp-main.31/

Check: ACL record opened; six authors, 508-521 and DOI match.

## [10] Wei et al., 2025

Purpose: Dual-granularity cross-domain training.

Link: https://aclanthology.org/2025.coling-main.631/

Check: ACL record opened; five authors, 9407-9417 and URL match.

## [11] Su et al., 2024

Purpose: Human-written and machine-generated news mixtures.

Link: https://aclanthology.org/2024.findings-naacl.95/

Check: ACL record opened; three authors, 1473-1490 and DOI match.

## [12] Xu and Yan, 2025

Purpose: TripleFact and benchmark contamination.

Link: https://aclanthology.org/2025.acl-long.431/

Check: ACL record opened; two authors, 8808-8823 and DOI match.

## [13] Kapoor and Narayanan, 2023

Purpose: Leakage and reproducibility.

Link: https://doi.org/10.1016/j.patter.2023.100804

Check: Publisher-indexed record confirms Patterns 4(9), 100804. Direct DOI/ScienceDirect access restricted and PMC presented a browser challenge. The author preprint https://arxiv.org/abs/2207.07048 opened; it is the earlier 2022 version, not substituted for the 2023 citation.

## [14] Kaggle, Fake News

Purpose: Original primary collection attribution.

Link: https://www.kaggle.com/competitions/fake-news

Check: Live competition page could not be retrieved, including the older /c/fake-news path. Retained as the original source recorded in the supplied notebook and experiment provenance. Do not describe this link as currently verified accessible.

## [15] ISOT Research Lab

Purpose: Dataset source documentation.

Link: https://onlineacademiccommunity.uvic.ca/isot/datasets/

Check: University of Victoria page opened; dataset attribution verified.

## [16] Pedregosa et al., 2011

Purpose: scikit-learn implementation.

Link: https://jmlr.org/papers/v12/pedregosa11a.html

Check: JMLR record opened; title, year, volume 12 and pages 2825-2830 match. Clickable link added.

## [17] scikit-learn developers

Purpose: TF-IDF implementation details.

Link: https://scikit-learn.org/stable/modules/feature_extraction.html

Check: Official documentation opened; page identifies version 1.9.1 at this check. The stable URL can change version over time.

## [18] Fan et al., 2008

Purpose: LIBLINEAR.

Link: https://jmlr.org/papers/v9/fan08a.html

Check: JMLR record opened; authors, volume 9 and 1871-1874 match. Clickable link added.

## [19] Breiman, 2001

Purpose: Random forests.

Link: https://link.springer.com/article/10.1023/A:1010933404324

Check: Publisher record opened; title, author, year, volume 45, 5-32 and DOI match.

## [20] scikit-learn developers

Purpose: MLP objective and implementation.

Link: https://scikit-learn.org/stable/modules/neural_networks_supervised.html

Check: Official documentation opened; page identifies version 1.9.1 at this check. The stable URL can change version over time.

## [21] Chen and Guestrin, 2016

Purpose: XGBoost.

Link: https://doi.org/10.1145/2939672.2939785

Check: Direct ACM/DOI fetch restricted. Author paper https://arxiv.org/abs/1603.02754 opened and identifies the same work and publication DOI. Citation retained.

## [22] Chicco and Jurman, 2020

Purpose: MCC metric rationale.

Link: https://link.springer.com/article/10.1186/s12864-019-6413-7

Check: Open-access publisher record opened; authors, year, volume 21, article 6 and DOI match.

## Dataset acquisition links

The recorded Hugging Face mirrors are listed in data/README.md in the repository package, with SHA-256 checksums from the completed run. These URLs establish the recorded acquisition path; the checking service could not retrieve the Kaggle mirror pages during this revision. No new download or hash verification of raw CSV files was performed. The original recorded hashes are preserved.

## Validation scope

The audit checks reference identity, relevance, metadata, link targets, and in-text use. It does not reproduce any cited study, guarantee absence of later corrections, certify external similarity screening, or replace IEEE PDF eXpress approval. No experimental rerun was performed.
