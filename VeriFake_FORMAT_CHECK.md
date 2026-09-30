# VeriFake conference format comparison

Checked against the actual supplied IEEE_Conference_Template.zip and finalized SignLink_IEEE_CSDE_3826_Manuscript.zip on 30 September 2026.

| Element | Corrected VeriFake implementation |
| --- | --- |
| Class | Unchanged IEEEtran.cls, byte-identical to both supplied references |
| Mode | documentclass conference; default US Letter, standard 10-point body, two columns |
| Authors | Eight individual IEEEauthorblockN and IEEEauthorblockA blocks, in accepted-list order as last supplied; rows of three, three, and two |
| Affiliations | Original VeriFake affiliations retained; no SignLink authors or affiliations copied |
| Header | SignLink top-right first-page TikZ placement and exact CSDE 2026 wording |
| Copyright | SignLink IEEEpubid first-page left-column footer, 979-8-3195-4477-3/26/$31.00 ©2026 IEEE |
| Sections | IEEE automatic numbering and standard heading styles |
| Figure 1 | Four connected grayscale panels, gray title bands and restrained shadow; VeriFake processes only |
| Pagination | Exactly six pages, including 22 references |
| Manuscript ZIP | Flat root containing IEEEtran.cls, main TeX, required table input, README and figures/ |
| Repository ZIP | VeriFake/ root with code, requirements, results/tables, results/figures, saved prediction evidence, data provenance and manuscript/ |

The preceding VeriFake source already selected conference mode. The visible mismatch was its shared author/affiliation block and independently implemented header/footer. These are now aligned with the finalized SignLink source. The class, body size, margins, and line spacing were not compressed to fit. Repeated prose was shortened to accommodate individual author blocks.

The supplied SignLink.zip is a research repository, whereas SignLink_IEEE_CSDE_3826_Manuscript.zip is the manuscript-source example. The VeriFake repository follows its code/results organization, with prediction and tuning records appropriate to VeriFake. SignLink CNN files, private .git history, and unrelated model results are not copied.

## Page map

1: title, eight author blocks, abstract, keywords, Introduction, start of Related Work.
2: remainder of Related Work, data cleaning, protocols, Table I, start of text representation.
3: Figure 1, Table II, model formulations and settings, start of evaluation measures.
4: Algorithm 1, metrics, implementation and GitHub URL, Table III, start of primary results.
5: Figure 2, Tables IV and V, primary-result continuation, transfer and ablation, start of discussion.
6: Figure 3, discussion continuation, conclusion, assistance disclosure, all 22 references.

## Author source boundary

The latest supplied eight-author list was preserved. The portal screenshot itself has not been recovered, so exact portal matching remains an author-side check. No new author was introduced during this revision.
