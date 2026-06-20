from docarena.prompts import prompt_for


def test_important_info_v2_prompt_has_image_only_rule_schema_and_category_focus():
    prompt = prompt_for("important_info_v2", "rechnungen")

    assert "Use only the rendered page images" in prompt
    assert "Do not use OCR" in prompt
    assert '"required_fields"' in prompt
    assert '"evidence_notes"' in prompt
    assert "seller/buyer" in prompt
    assert "Use null for expected but not visible values" in prompt
