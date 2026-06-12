PROMPT_VARIANTS = {
    "strict_schema": (
        "Extract the German document as JSON only. Include document_type, involved_names, "
        "dates, numbers, required_fields, optional_fields, full_document_summary, and evidence_notes."
    ),
    "evidence_first": (
        "Inspect the rendered pages. First identify visual evidence and context internally, then return "
        "one JSON object with extracted fields and evidence_notes. Do not use OCR text or PDF text layers."
    ),
    "role_specialist": (
        "You are a German document analyst for {category}. Read only the supplied page images and return "
        "a valid JSON extraction with required fields, dates, amounts, IDs, parties, and a concise summary."
    ),
}

IMAGE_ONLY_RULE = (
    "Use only the rendered page images supplied in this request. "
    "Do not use OCR, PDF text layers, extracted text, external lookup, or hidden metadata. "
)


def prompt_for(variant: str, category: str) -> str:
    template = PROMPT_VARIANTS[variant]
    return IMAGE_ONLY_RULE + template.format(category=category)
