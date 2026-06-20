from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .utils import read_png_dimensions, sha256_file


@dataclass(frozen=True)
class RenderedPage:
    page_number: int
    image_path: Path
    width: int | None
    height: int | None
    sha256: str


@dataclass(frozen=True)
class RenderedDocument:
    doc_id: str
    source_pdf: Path
    renderer: str
    dpi: int
    pages: list[RenderedPage]
    category: str = "document"


def _run_pdftoppm(pdf: Path, out_dir: Path, pages: list[int], dpi: int) -> None:
    first, last = min(pages), max(pages)
    prefix = out_dir / pdf.stem
    cmd = ["pdftoppm", "-png", "-r", str(dpi), "-f", str(first), "-l", str(last), str(pdf), str(prefix)]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _run_mutool(pdf: Path, out_dir: Path, pages: list[int], dpi: int) -> None:
    page_spec = ",".join(str(page) for page in pages)
    output = out_dir / f"{pdf.stem}-%d.png"
    cmd = ["mutool", "draw", "-r", str(dpi), "-o", str(output), str(pdf), page_spec]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def render_pdf(
    pdf_path: str | Path,
    out_dir: str | Path,
    pages: list[int],
    dpi: int = 200,
    doc_id: str | None = None,
    category: str = "document",
) -> RenderedDocument:
    pdf = Path(pdf_path)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_id = doc_id or pdf.stem

    renderer = "pdftoppm"
    try:
        _run_pdftoppm(pdf, output_dir, pages, dpi)
    except (FileNotFoundError, subprocess.CalledProcessError):
        renderer = "mutool"
        _run_mutool(pdf, output_dir, pages, dpi)

    rendered_pages: list[RenderedPage] = []
    for page in pages:
        candidates = [
            output_dir / f"{pdf.stem}-{page}.png",
            output_dir / f"{pdf.stem}-{page:02d}.png",
            output_dir / f"{pdf.stem}-{page:03d}.png",
            output_dir / f"{pdf.stem}-{len(rendered_pages) + 1}.png",
            output_dir / f"{pdf.stem}-{len(rendered_pages) + 1:02d}.png",
            output_dir / f"{pdf.stem}-{len(rendered_pages) + 1:03d}.png",
        ]
        image_path = next((candidate for candidate in candidates if candidate.exists()), None)
        if image_path is None:
            raise FileNotFoundError(f"renderer did not produce an image for page {page} of {pdf}")
        width, height = read_png_dimensions(image_path)
        rendered_pages.append(
            RenderedPage(
                page_number=page,
                image_path=image_path,
                width=width,
                height=height,
                sha256=sha256_file(image_path),
            )
        )
    return RenderedDocument(doc_id=doc_id, source_pdf=pdf, renderer=renderer, dpi=dpi, pages=rendered_pages, category=category)


def write_rendered_manifest(rendered: list[RenderedDocument], path: str | Path) -> Path:
    target = Path(path)
    target.write_text(
        json.dumps(
            [
                {
                    **asdict(doc),
                    "source_pdf": str(doc.source_pdf),
                    "pages": [{**asdict(page), "image_path": str(page.image_path)} for page in doc.pages],
                }
                for doc in rendered
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target
