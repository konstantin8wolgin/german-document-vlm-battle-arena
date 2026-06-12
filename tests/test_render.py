import subprocess

from docarena.render import render_pdf


def test_render_pdf_uses_pdftoppm_and_records_hashes(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "rendered"

    def fake_run(cmd, check, capture_output, text):
        assert cmd[:2] == ["pdftoppm", "-png"]
        prefix = cmd[-1]
        page = tmp_path / "rendered" / "doc-1.png"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_bytes(b"png-bytes")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    rendered = render_pdf(pdf, out_dir, pages=[1], dpi=180)

    assert rendered.renderer == "pdftoppm"
    assert rendered.pages[0].image_path.name == "doc-1.png"
    assert rendered.pages[0].sha256


def test_render_pdf_falls_back_to_mutool_when_pdftoppm_fails(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "rendered"
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd[0])
        if cmd[0] == "pdftoppm":
            raise subprocess.CalledProcessError(1, cmd, stderr="missing")
        page = tmp_path / "rendered" / "doc-1.png"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_bytes(b"png-bytes")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    rendered = render_pdf(pdf, out_dir, pages=[1], dpi=180)

    assert calls == ["pdftoppm", "mutool"]
    assert rendered.renderer == "mutool"


def test_render_pdf_finds_zero_padded_pdftoppm_outputs(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    out_dir = tmp_path / "rendered"

    def fake_run(cmd, check, capture_output, text):
        (tmp_path / "rendered" / "doc-01.png").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "rendered" / "doc-01.png").write_bytes(b"png-1")
        (tmp_path / "rendered" / "doc-02.png").write_bytes(b"png-2")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    rendered = render_pdf(pdf, out_dir, pages=[1, 2], dpi=180)

    assert [page.image_path.name for page in rendered.pages] == ["doc-01.png", "doc-02.png"]
