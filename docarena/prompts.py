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
    "important_info_v2": (
        "You are a careful German document extraction engine for category: {category}.\n\n"
        "Task: extract the most important visible information from the supplied rendered page images. "
        "Return exactly one valid JSON object and no markdown.\n\n"
        "Output schema:\n"
        "{{\n"
        '  "document_type": "specific German document type",\n'
        '  "involved_names": [{{"name": "...", "role_or_context": "..."}}],\n'
        '  "dates": [{{"value": "...", "meaning": "..."}}],\n'
        '  "numbers": [{{"value": "...", "meaning": "..."}}],\n'
        '  "required_fields": {{"field_name": "visible value or null"}},\n'
        '  "optional_fields": {{"field_name": "visible value or null"}},\n'
        '  "full_document_summary": "2-4 concise German sentences covering purpose, parties, obligations/actions, amounts/IDs/dates if visible",\n'
        '  "evidence_notes": [{{"field": "...", "evidence": "short quote or visual location from the image"}}]\n'
        "}}\n\n"
        "Category focus:\n"
        "- rechnungen: seller/buyer, invoice number/date, tax IDs, IBAN, line items, net/gross/VAT amounts, payment terms, Kleinunternehmer wording.\n"
        "- bank_finanzen: account/mandate/reference IDs, IBAN/BIC, SEPA/EBICS terms, customer data, signatures, required actions.\n"
        "- behoerdenpost: sender/recipient, file/reference numbers, decision type, legal remedy, deadlines, requested action.\n"
        "- formulare: applicant/person data fields, benefit period, income/housing/social-insurance fields, attachments, signatures.\n"
        "- medizin: form number/version, patient/provider fields, medical service/context, instructions, billing/printing rules.\n"
        "- steuer: taxpayer/agent fields, tax year, certificate/annex type, amounts, legal basis, declaration/signature requirements.\n"
        "- versicherung: product type, covered risks, exclusions, duties, claim/reporting rules, limits/deductibles.\n"
        "- vertraege: parties, contract type, obligations, payment, term, termination, liability, jurisdiction/applicable law.\n\n"
        "Rules:\n"
        "- Include only information visible in the rendered images.\n"
        "- Preserve German wording for names, identifiers, amounts, dates, clauses, and form labels.\n"
        "- Use null for expected but not visible values; do not invent.\n"
        "- Prefer exact numbers/dates over paraphrases.\n"
        "- Keep arrays short but complete for important information.\n"
        "- The response must be parseable JSON."
    ),
}

IMAGE_ONLY_RULE = (
    "Use only the rendered page images supplied in this request. "
    "Do not use OCR, PDF text layers, extracted text, external lookup, or hidden metadata. "
)


def prompt_for(variant: str, category: str) -> str:
    template = PROMPT_VARIANTS[variant]
    return IMAGE_ONLY_RULE + template.format(category=category)
