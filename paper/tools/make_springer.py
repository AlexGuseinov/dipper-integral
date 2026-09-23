"""Generate the Springer Nature (sn-jnl) submission version from paper.tex.

The body text is taken verbatim from paper.tex; only the front matter, theorem
set-up, declarations, appendix environment and bibliography style change.
Output: springer/main.tex, springer/refs.bib and the figure PDFs (flat folder,
as required by the journal). sn-jnl.cls and sn-mathphys-num.bst from the official
Springer Nature LaTeX template must be placed in springer/ to compile.
"""
import re, shutil, os

SRC = "paper.tex"
OUT = "springer"
s = open(SRC).read()

body = s[s.index(r"\end{abstract}") + len(r"\end{abstract}"):s.index(r"\end{document}")]
abstract = s[s.index(r"\begin{abstract}") + len(r"\begin{abstract}"):s.index(r"\end{abstract}")].strip()
m = re.search(r"\\noindent\\textbf\{Keywords:\}\s*(.*)\n", body)
keywords = m.group(1).strip().replace(";", ",")
body = body.replace(m.group(0), "")

# data availability -> declarations; \appendix -> appendices environment
da0 = body.index(r"\section*{Data and code availability}")
da1 = body.index(r"\appendix")
data_text = body[da0 + len(r"\section*{Data and code availability}"):da1].strip()
app = body[da1 + len(r"\appendix"):body.index(r"\bibliographystyle")].strip()
body = body[:da0]

MSC = "94A60, 94D10, 68P25"

declarations = r"""
\backmatter

\section*{Declarations}

\bmhead{Funding}
The authors did not receive support from any organization for the submitted work.

\bmhead{Competing interests}
The authors have no competing interests to declare that are relevant to the content of this article. The cipher analysed here, Dipper, was proposed by the authors in earlier work~\cite{dipper2026}; this article evaluates it and corrects two statements of its specification.

\bmhead{Data and code availability}
""" + data_text + r"""

\bmhead{Ethics approval and consent to participate}
Not applicable.

\bmhead{Author contributions}
Ali Huseynli: conceptualization, methodology, software, formal analysis, investigation, writing -- original draft. Yadigar Imamverdiyev: supervision, validation, writing -- review and editing. Jalal Alizadeh: supervision, validation, writing -- review and editing. All authors read and approved the final manuscript.
"""

preamble = r"""\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}

\usepackage{graphicx}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{amsthm}
\usepackage[title]{appendix}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{textcomp}
\usepackage{manyfoot}% required by sn-jnl.cls (footnote hook at begin document), as in the template
\usepackage{url}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta}

\theoremstyle{thmstyleone}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}
\newtheorem{corollary}{Corollary}
\theoremstyle{thmstylethree}
\newtheorem{definition}{Definition}
\theoremstyle{thmstyletwo}
\newtheorem{example}{Example}
\newtheorem{remark}{Remark}

\newcommand{\modadd}{\boxplus}
\newcommand{\Ftwo}{\mathbb{F}_2}
\newcommand{\intval}{\operatorname{val}}
\newcommand{\hw}{\operatorname{wt}}
\newcommand{\MPEL}{\textsf{MP-EL}}
\newcommand{\MPC}{\textsf{MP-circuit}}
\newcommand{\BDP}{\textsf{BDP}}
\newcommand{\repo}{\url{https://github.com/AlexGuseinov/dipper-integral}}
%%NUMBERS%%

\raggedbottom
\setlength{\emergencystretch}{3em}

\begin{document}

\title[Certified Integral Properties of Dipper]{Certified Integral Properties of the Dipper Block Cipher: Monomial-Trail Analysis and the Role of the Half-State Modular Addition}

\author*[1]{\fnm{Ali} \sur{Huseynli}}\email{ali.huseynli@student.aztu.edu.az}
\author[1]{\fnm{Yadigar} \sur{Imamverdiyev}}\email{yadigar.imamverdiyev@aztu.edu.az}
\author[1]{\fnm{Jalal} \sur{Alizadeh}}\email{jalal.alizadeh@aztu.edu.az}

\affil*[1]{\orgdiv{Department of Cybersecurity, Faculty of Information Technologies and Telecommunications}, \orgname{Azerbaijan Technical University}, \orgaddress{\city{Baku}, \postcode{AZ1073}, \country{Azerbaijan}}}

"""

front = (r"\abstract{" + abstract + "}\n\n" + r"\keywords{" + keywords + "}\n\n" +
         r"\pacs[MSC Classification]{" + MSC + "}\n\n" + r"\maketitle" + "\n")

tail = ("\n" + declarations + "\n\\begin{appendices}\n\n" + app + "\n\n\\end{appendices}\n\n"
        + "\\bibliography{refs}\n\n\\end{document}\n")

numbers = "".join(l + "\n" for l in s.splitlines() if re.match(r"\\newcommand\{\\N[A-Z]+\}", l))
preamble = preamble.replace("%%NUMBERS%%\n", numbers)
doc = preamble + front + body.rstrip() + "\n" + tail
# rename generic macros to avoid clashes with the journal class
for old, new in ((r"\add", r"\modadd"), (r"\F", r"\Ftwo"), (r"\val", r"\intval"), (r"\wt", r"\hw")):
    pre, post = doc.split(r"\begin{document}", 1)
    post = re.sub(re.escape(old) + r"(?![A-Za-z])", lambda _: new, post)
    doc = pre + r"\begin{document}" + post

# appendix test-vector tables: 32 hex digits need a smaller font at the journal text width
doc = doc.replace(r"\begin{center}\small", r"\begin{center}\footnotesize")
# no adjustbox around tables: sn-jnl wraps every table in threeparttable, which needs the
# tabular as its direct content; all tables fit the text width (checked with sn-jnl.cls)
# a long inline formula in the proof of Lemma addret: set it as a display
doc = doc.replace(r"characterisation, $(x\modadd y)^w=\sum_{\intval(a')+\intval(b')=\intval(w)}x^{a'}y^{b'}$. Multiplying",
                  r"characterisation, \[(x\modadd y)^w=\sum_{\intval(a')+\intval(b')=\intval(w)}x^{a'}y^{b'}.\] Multiplying")

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "main.tex"), "w").write(doc)
for f in ("refs.bib", "fig_degree.pdf", "fig_ablation.pdf"):
    shutil.copy(f, os.path.join(OUT, f))
used = set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", doc))
missing = [f for f in used if not os.path.exists(os.path.join(OUT, f))]
print("abstract words:", len(abstract.split()), "| keywords:", len(keywords.split(",")),
      "| figures:", sorted(used), "| missing:", missing)
