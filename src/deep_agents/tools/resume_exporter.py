"""
Deep Agents — Resume Exporter Tool.

Converts a tailored markdown resume into downloadable **PDF** and **DOCX**
files using clean, ATS-optimised templates.

Export Formats
--------------
* **PDF**  — Markdown → HTML → styled PDF via ``weasyprint``.
* **DOCX** — Programmatic Word document via ``python-docx``.

Template Design Rationale
-------------------------
The template follows industry-standard ATS best practices:

* **Single-column** layout — ATS reads left-to-right, top-to-bottom.
  Multi-column layouts cause misread data.
* **Standard fonts** — Calibri (primary), Arial (fallback), 11 pt body.
  These are universally parseable by every ATS (Workday, Greenhouse, Taleo).
* **No graphics / tables / text boxes** — these are the #1 cause of ATS
  parsing failures.
* **A4 page, 1-inch margins** — professional standard.
* **Reverse-chronological** section flow — preferred by both ATS and
  human recruiters.

Deployment
----------
PDF export requires ``weasyprint`` which needs system libraries
(Pango, Cairo). On Streamlit Cloud, add a ``packages.txt`` at the
project root with the required apt packages.
"""

from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
#  ATS Resume CSS Template (for PDF export)
# ---------------------------------------------------------------------------

_RESUME_CSS = """
@page {
    size: A4;
    margin: 2.54cm;   /* 1 inch all sides */
}

body {
    font-family: 'Calibri', 'Arial', 'Helvetica Neue', sans-serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
}

/* --- Name / Title --- */
h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #111111;
    margin: 0 0 4pt 0;
    padding: 0;
    border: none;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
}

/* --- Section Headings --- */
h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #222222;
    margin: 14pt 0 6pt 0;
    padding: 0 0 3pt 0;
    border-bottom: 1.2pt solid #333333;
    text-transform: uppercase;
    letter-spacing: 0.3pt;
}

/* --- Sub-headings (company, degree) --- */
h3 {
    font-size: 11pt;
    font-weight: 600;
    color: #1a1a1a;
    margin: 8pt 0 2pt 0;
    padding: 0;
}

/* --- Paragraphs --- */
p {
    margin: 0 0 4pt 0;
    padding: 0;
    orphans: 3;
    widows: 3;
}

/* --- Contact info line (below name) --- */
p:first-of-type {
    font-size: 10pt;
    color: #444444;
    margin-bottom: 8pt;
}

/* --- Bullet lists --- */
ul {
    margin: 2pt 0 6pt 0;
    padding-left: 18pt;
}

li {
    margin-bottom: 3pt;
    line-height: 1.4;
}

/* --- Bold / Italic --- */
strong {
    font-weight: 600;
}

em {
    font-style: italic;
    color: #555555;
}

/* --- Links (for email, LinkedIn, GitHub) --- */
a {
    color: #1a1a1a;
    text-decoration: none;
}

/* --- Horizontal rules --- */
hr {
    border: none;
    border-top: 0.8pt solid #cccccc;
    margin: 10pt 0;
}

/* --- Inline code (for skills tags) --- */
code {
    font-family: 'Calibri', 'Arial', sans-serif;
    font-size: 10.5pt;
    background: none;
    padding: 0;
}
"""

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
{css}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


# ---------------------------------------------------------------------------
#  PDF Export
# ---------------------------------------------------------------------------


def export_resume_to_pdf(markdown_content: str) -> bytes:
    """Convert a markdown resume to a styled PDF document.

    Parameters
    ----------
    markdown_content : str
        The tailored resume in markdown format.

    Returns
    -------
    bytes
        PDF file content as raw bytes, ready for ``st.download_button``.

    Raises
    ------
    ImportError
        If ``weasyprint`` or ``markdown`` is not installed.
    RuntimeError
        If PDF generation fails (e.g. missing system libraries).
    """
    import markdown as md_lib
    from weasyprint import HTML

    # Convert markdown → HTML
    html_body = md_lib.markdown(
        markdown_content,
        extensions=["extra", "sane_lists"],
    )

    # Wrap in full HTML document with ATS CSS
    full_html = _HTML_TEMPLATE.format(
        css=_RESUME_CSS,
        content=html_body,
    )

    # Generate PDF
    pdf_bytes = HTML(string=full_html).write_pdf()

    return pdf_bytes


# ---------------------------------------------------------------------------
#  DOCX Export
# ---------------------------------------------------------------------------


def _parse_markdown_to_sections(markdown_content: str) -> list[dict[str, Any]]:
    """Parse markdown resume into structured sections for DOCX generation.

    Parameters
    ----------
    markdown_content : str
        Resume content in markdown format.

    Returns
    -------
    list[dict]
        List of section dicts, each with ``type`` (heading1, heading2,
        heading3, paragraph, bullet, hr) and ``text``.
    """
    sections: list[dict[str, Any]] = []

    for line in markdown_content.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        # Headings
        if stripped.startswith("### "):
            sections.append({"type": "heading3", "text": stripped[4:]})
        elif stripped.startswith("## "):
            sections.append({"type": "heading2", "text": stripped[3:]})
        elif stripped.startswith("# "):
            sections.append({"type": "heading1", "text": stripped[2:]})
        # Horizontal rules
        elif stripped in ("---", "***", "___"):
            sections.append({"type": "hr", "text": ""})
        # Bullet points
        elif stripped.startswith(("- ", "* ", "• ")):
            bullet_text = stripped[2:]
            sections.append({"type": "bullet", "text": bullet_text})
        # Regular paragraphs
        else:
            sections.append({"type": "paragraph", "text": stripped})

    return sections


def _clean_markdown_formatting(text: str) -> str:
    """Strip markdown inline formatting (bold, italic, links, code).

    Parameters
    ----------
    text : str
        Text with possible markdown formatting.

    Returns
    -------
    str
        Clean plain text.
    """
    # Remove bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # Remove italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    # Remove inline code: `text`
    text = re.sub(r"`(.+?)`", r"\1", text)
    # Remove links: [text](url) → text
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)

    return text.strip()


def export_resume_to_docx(markdown_content: str) -> bytes:
    """Convert a markdown resume to a formatted DOCX document.

    Uses ``python-docx`` to build a properly styled Word document
    with ATS-friendly formatting. The document uses standard Word
    styles so the user can easily edit it after download.

    Parameters
    ----------
    markdown_content : str
        The tailored resume in markdown format.

    Returns
    -------
    bytes
        DOCX file content as raw bytes, ready for ``st.download_button``.

    Raises
    ------
    ImportError
        If ``python-docx`` is not installed.
    """
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()

    # --- Page margins: 1 inch all sides ---
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # --- Default font ---
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

    paragraph_format = style.paragraph_format
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(3)
    paragraph_format.line_spacing = 1.15

    # --- Parse and build document ---
    sections = _parse_markdown_to_sections(markdown_content)

    for item in sections:
        text = _clean_markdown_formatting(item["text"])
        item_type = item["type"]

        if item_type == "heading1":
            # Name — large, bold, uppercase
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = para.add_run(text.upper())
            run.font.size = Pt(20)
            run.font.bold = True
            run.font.name = "Calibri"
            run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            para.paragraph_format.space_after = Pt(2)

        elif item_type == "heading2":
            # Section heading — bold, uppercase, with bottom border
            para = doc.add_paragraph()
            run = para.add_run(text.upper())
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.name = "Calibri"
            run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
            para.paragraph_format.space_before = Pt(12)
            para.paragraph_format.space_after = Pt(4)
            # Bottom border via XML
            from docx.oxml.ns import qn
            pPr = para._p.get_or_add_pPr()
            pBdr = pPr.makeelement(qn("w:pBdr"), {})
            bottom = pBdr.makeelement(
                qn("w:bottom"),
                {
                    qn("w:val"): "single",
                    qn("w:sz"): "6",
                    qn("w:space"): "1",
                    qn("w:color"): "333333",
                },
            )
            pBdr.append(bottom)
            pPr.append(pBdr)

        elif item_type == "heading3":
            # Sub-heading (company name, degree)
            para = doc.add_paragraph()
            run = para.add_run(text)
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.name = "Calibri"
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
            para.paragraph_format.space_before = Pt(6)
            para.paragraph_format.space_after = Pt(1)

        elif item_type == "bullet":
            # Bullet point
            para = doc.add_paragraph(text, style="List Bullet")
            para.paragraph_format.space_before = Pt(0)
            para.paragraph_format.space_after = Pt(2)
            for run in para.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(11)

        elif item_type == "hr":
            # Thin horizontal line
            para = doc.add_paragraph()
            para.paragraph_format.space_before = Pt(6)
            para.paragraph_format.space_after = Pt(6)
            from docx.oxml.ns import qn
            pPr = para._p.get_or_add_pPr()
            pBdr = pPr.makeelement(qn("w:pBdr"), {})
            bottom = pBdr.makeelement(
                qn("w:bottom"),
                {
                    qn("w:val"): "single",
                    qn("w:sz"): "4",
                    qn("w:space"): "1",
                    qn("w:color"): "CCCCCC",
                },
            )
            pBdr.append(bottom)
            pPr.append(pBdr)

        else:
            # Regular paragraph
            para = doc.add_paragraph(text)
            for run in para.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(11)

    # Write to bytes buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()


# ---------------------------------------------------------------------------
#  Convenience: Export Both Formats
# ---------------------------------------------------------------------------


def export_resume(
    markdown_content: str,
    formats: tuple[str, ...] = ("pdf", "docx"),
) -> dict[str, bytes]:
    """Export a markdown resume to one or more formats.

    Parameters
    ----------
    markdown_content : str
        The tailored resume in markdown format.
    formats : tuple[str, ...]
        Desired output formats. Supports ``"pdf"`` and ``"docx"``.

    Returns
    -------
    dict[str, bytes]
        Mapping of format name → raw file bytes.
        e.g. ``{"pdf": b"...", "docx": b"..."}``

    Raises
    ------
    ValueError
        If an unsupported format is requested.
    """
    _exporters = {
        "pdf": export_resume_to_pdf,
        "docx": export_resume_to_docx,
    }

    results: dict[str, bytes] = {}

    for fmt in formats:
        fmt_lower = fmt.lower()
        if fmt_lower not in _exporters:
            raise ValueError(
                f"Unsupported format '{fmt}'. Supported: {list(_exporters.keys())}"
            )
        results[fmt_lower] = _exporters[fmt_lower](markdown_content)

    return results
