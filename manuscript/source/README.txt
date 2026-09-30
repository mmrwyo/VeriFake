VeriFake IEEE CSDE 2026 conference source
Paper ID: ieee-csde_3824

Uses the unchanged IEEEtran.cls from the supplied IEEE_Conference_Template.zip, identical to the class in SignLink_IEEE_CSDE_3826_Manuscript.zip. Conference mode, standard 10-point body, US Letter, two columns. Eight individual author blocks follow the latest supplied VeriFake author order and affiliations, arranged in three rows. Only the supplied corresponding-author email is included.

From this directory, use:
latexmk -pdf -interaction=nonstopmode -halt-on-error ieee-csde_3824_Paper.tex

Alternatively run pdflatex three times, or until cross-references and the remembered header position stabilize. The bibliography is embedded; BibTeX is unnecessary. Standard TeX Live packages are required: cite, amsmath, amssymb, graphicx, booktabs, array, url, enumitem, tikz, etoolbox, hyperref, and fontenc.

Expected output: exactly six pages including 22 references, three figures, five tables, five equations, and Algorithm 1. No body font, margin or line-spacing reductions were made. Figure 1 matches the supplied SignLink four-panel grayscale style using actual VeriFake processes. Editable SVG and high-resolution PNG are included.

Document compilation is permitted; ask the project owner before any experimental code rerun. Match authors to the accepted portal record and obtain the required IEEE PDF eXpress pass and screening reports before submission. These external checks have not been performed here.
