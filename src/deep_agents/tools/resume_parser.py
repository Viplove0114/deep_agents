"""
Deep Agents — Resume Parser Tool.

Extracts clean text from uploaded resume files across multiple formats
(PDF, DOCX, TXT, Markdown), then provides the raw content alongside a
structured schema so the LLM can intelligently parse it into a
``ResumeProfile``.

Supported Formats
-----------------
* ``.pdf``  — via ``pymupdf`` (fitz), industry-standard for speed & layout
* ``.docx`` — via ``python-docx``, preserves semantic paragraph structure
* ``.txt``  — plain-text read
* ``.md``   — plain-text read (Markdown)

Design Rationale
----------------
The tool handles *file format conversion* (binary → text) only.
The *intelligent extraction* of structured fields (name, skills, etc.)
is delegated to the LLM, which is far better at understanding context
than regex or rule-based parsers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
#  Structured Resume Schema
# ---------------------------------------------------------------------------


class ExperienceEntry(BaseModel):
    """A single work experience entry."""

    company: str = Field(default="", description="Company or organisation name.")
    title: str = Field(default="", description="Job title or role.")
    dates: str = Field(default="", description="Employment period (e.g. 'Jan 2023 – Present').")
    location: str = Field(default="", description="City, state, or 'Remote'.")
    bullets: list[str] = Field(
        default_factory=list,
        description="Achievement bullet points for this role.",
    )


class EducationEntry(BaseModel):
    """A single education entry."""

    institution: str = Field(default="", description="University or school name.")
    degree: str = Field(default="", description="Degree earned (e.g. 'B.Tech in CSE').")
    dates: str = Field(default="", description="Attendance period.")
    gpa: str = Field(default="", description="GPA or percentage, if mentioned.")


class ProjectEntry(BaseModel):
    """A single project entry."""

    name: str = Field(default="", description="Project name.")
    description: str = Field(default="", description="Brief description of the project.")
    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies and frameworks used.",
    )
    link: str = Field(default="", description="URL to the project (GitHub, live demo, etc.).")


class ResumeProfile(BaseModel):
    """Structured representation of a parsed resume.

    This schema is the canonical output format for resume parsing.
    All downstream subagents (JD Analyzer, Resume Tailor, Quality Judge)
    consume and produce data conforming to this structure.
    """

    name: str = Field(default="", description="Candidate's full name.")
    email: str = Field(default="", description="Contact email address.")
    phone: str = Field(default="", description="Contact phone number.")
    location: str = Field(default="", description="City, State or Country.")
    linkedin: str = Field(default="", description="LinkedIn profile URL.")
    github: str = Field(default="", description="GitHub profile URL.")
    portfolio: str = Field(default="", description="Personal website or portfolio URL.")
    summary: str = Field(
        default="",
        description="Professional summary or objective statement.",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Technical and soft skills.",
    )
    experience: list[ExperienceEntry] = Field(
        default_factory=list,
        description="Work experience entries in reverse-chronological order.",
    )
    education: list[EducationEntry] = Field(
        default_factory=list,
        description="Education entries.",
    )
    projects: list[ProjectEntry] = Field(
        default_factory=list,
        description="Notable projects.",
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Professional certifications.",
    )
    raw_text: str = Field(
        default="",
        description="Original raw text extracted from the resume file.",
    )


# ---------------------------------------------------------------------------
#  File Format Extractors
# ---------------------------------------------------------------------------


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz).

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the PDF file.

    Returns
    -------
    str
        Extracted text content, pages separated by double newlines.
    """
    import io

    # Try pypdf first (pure Python — no DLL issues on Windows)
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
        return "\n\n".join(pages)
    except ImportError:
        pass

    # Fallback to pymupdf (faster but needs C libs)
    try:
        import fitz  # pymupdf

        pages = []
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text = page.get_text("text")
                if text.strip():
                    pages.append(text.strip())
        return "\n\n".join(pages)
    except ImportError:
        raise ImportError(
            "No PDF reader available. Install one of:\n"
            "  pip install pypdf       (recommended, pure Python)\n"
            "  pip install pymupdf     (faster, needs C libs)"
        )


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the DOCX file.

    Returns
    -------
    str
        Extracted text content, paragraphs separated by newlines.
    """
    import io

    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs: list[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def _extract_text_from_plain(file_bytes: bytes) -> str:
    """Extract text from a plain-text or Markdown file.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the text file.

    Returns
    -------
    str
        Decoded text content.
    """
    # Try UTF-8 first, fall back to latin-1 for resilience
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


# Map of supported extensions → extractor functions
_EXTRACTORS: dict[str, Any] = {
    ".pdf": _extract_text_from_pdf,
    ".docx": _extract_text_from_docx,
    ".txt": _extract_text_from_plain,
    ".md": _extract_text_from_plain,
}

SUPPORTED_EXTENSIONS: tuple[str, ...] = tuple(_EXTRACTORS.keys())


# ---------------------------------------------------------------------------
#  Public API — Tool Factory
# ---------------------------------------------------------------------------


def parse_resume_file(file_bytes: bytes, filename: str) -> str:
    """Parse a resume file and return extracted text with structuring instructions.

    This is the main entry-point called by the Streamlit UI or agent tools.
    It handles format detection, text extraction, and returns the raw text
    alongside a schema description so the LLM can structure the content.

    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of the uploaded file.
    filename : str
        Original filename (used to detect format via extension).

    Returns
    -------
    str
        Extracted text with instructions for LLM-based structuring.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    """
    ext = Path(filename).suffix.lower()

    if ext not in _EXTRACTORS:
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    extractor = _EXTRACTORS[ext]
    raw_text = extractor(file_bytes)

    if not raw_text.strip():
        return (
            f"WARNING: No text could be extracted from '{filename}'. "
            "The file may be image-based (scanned). "
            "Please re-upload a text-based PDF or paste your resume as plain text."
        )

    word_count = len(raw_text.split())
    line_count = len(raw_text.strip().splitlines())

    return (
        f"RESUME PARSED SUCCESSFULLY\n"
        f"File: {filename} | Format: {ext} | Words: {word_count} | Lines: {line_count}\n"
        f"{'=' * 60}\n\n"
        f"{raw_text}\n\n"
        f"{'=' * 60}\n"
        f"INSTRUCTIONS: Extract the following structured fields from the resume above:\n"
        f"- name, email, phone, location, linkedin, github, portfolio\n"
        f"- summary (professional summary / objective)\n"
        f"- skills[] (all technical and soft skills)\n"
        f"- experience[] (each with: company, title, dates, location, bullets[])\n"
        f"- education[] (each with: institution, degree, dates, gpa)\n"
        f"- projects[] (each with: name, description, technologies[], link)\n"
        f"- certifications[]\n\n"
        f"IMPORTANT: Only extract information that is EXPLICITLY present in the text. "
        f"Do NOT infer, assume, or fabricate any details.\n"
        f"Save the structured result to /profile/master_resume.json using write_file."
    )


def create_resume_parser_tool() -> callable:
    """Create and return a resume parsing function for use as a deep-agent tool.

    The returned function accepts raw text (for paste-in-chat mode) and
    returns it with structuring instructions. For file-based parsing,
    use ``parse_resume_file()`` directly from the Streamlit UI layer.

    Returns
    -------
    callable
        A ``parse_resume(raw_text)`` function ready for agent tool registration.
    """

    def parse_resume(raw_text: str) -> str:
        """Parse raw resume text and return it with structured extraction instructions.

        Use this when the user pastes their resume directly in the chat
        rather than uploading a file.

        Parameters
        ----------
        raw_text : str
            The raw resume text content (pasted by the user).

        Returns
        -------
        str
            The resume text with extraction instructions for structuring.
        """
        if not raw_text.strip():
            return "ERROR: Empty resume text provided. Please paste your resume content."

        word_count = len(raw_text.split())

        return (
            f"RESUME TEXT RECEIVED\n"
            f"Words: {word_count}\n"
            f"{'=' * 60}\n\n"
            f"{raw_text}\n\n"
            f"{'=' * 60}\n"
            f"INSTRUCTIONS: Extract the following structured fields from the resume above:\n"
            f"- name, email, phone, location, linkedin, github, portfolio\n"
            f"- summary (professional summary / objective)\n"
            f"- skills[] (all technical and soft skills)\n"
            f"- experience[] (each with: company, title, dates, location, bullets[])\n"
            f"- education[] (each with: institution, degree, dates, gpa)\n"
            f"- projects[] (each with: name, description, technologies[], link)\n"
            f"- certifications[]\n\n"
            f"IMPORTANT: Only extract information that is EXPLICITLY present in the text. "
            f"Do NOT infer, assume, or fabricate any details.\n"
            f"Save the structured result to /profile/master_resume.json using write_file."
        )

    return parse_resume
