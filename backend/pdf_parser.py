import re
import json
import fitz  # PyMuPDF


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from all pages of a PDF file."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def detect_bank(text: str) -> str:
    """Detect which bank the extract is from based on keywords."""
    text_lower = text.lower()

    if "banca transilvania" in text_lower or "bancatransilvania" in text_lower:
        return "BT"
    elif "ing bank" in text_lower:
        return "ING"
    elif "revolut" in text_lower:
        return "Revolut"
    elif "bcr" in text_lower or "banca comerciala romana" in text_lower:
        return "BCR"
    elif "brd" in text_lower:
        return "BRD"
    elif "raiffeisen" in text_lower:
        return "Raiffeisen"
    else:
        return "Unknown"


def parse_bt_transactions(text: str) -> list[dict]:
    """
    Parse transactions from Banca Transilvania extract.
    Uses regex for BT's known format: DD.MM.YYYY | description | amount RON
    """
    transactions = []
    pattern = r"(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+([-+]?\d+[\.,]\d{2})\s*RON"
    matches = re.finditer(pattern, text, re.MULTILINE)

    for match in matches:
        date, description, amount = match.groups()
        amount = float(amount.replace(",", "."))
        transactions.append({
            "date": date,
            "description": description.strip(),
            "amount": amount,
            "currency": "RON"
        })

    return transactions


def parse_with_claude(text: str, bank: str, claude_client) -> list[dict]:
    message = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": f"""Extract all bank transactions from the following {bank} bank statement text.

                            Return ONLY a JSON array, no explanation, no markdown. Each transaction must have:
                            - date (DD.MM.YYYY format)
                            - description (merchant or transaction description)
                            - amount (negative for expenses, positive for income)
                            - currency (RON, EUR, USD etc.)

                            Bank statement text:
                            {text[:50000]}

                            Example format:
                            [{{"date": "05.01.2024", "description": "Kaufland", "amount": -150.00, "currency": "RON"}}]"""
            }
        ]
    )

    # Debug: print raw response
    raw = message.content[0].text

    try:
        # Strip markdown backticks if present
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip()
        return json.loads(clean)
    except Exception as e:
        print(f"JSON parse error: {e}")
        return []


def parse_transactions_from_pdf(file_bytes: bytes, claude_client) -> dict:
    """
    Main entry point: extracts and parses transactions from any PDF bank statement.
    Uses Claude for all banks — regex as future optimization for known formats.
    """
    # Extract raw text from PDF
    text = extract_text_from_pdf(file_bytes)

    # Detect bank
    bank = detect_bank(text)

    # Use Claude for all banks (robust fallback for any format)
    transactions = parse_with_claude(text, bank, claude_client)
    parser_used = "claude"

    return {
        "bank": bank,
        "parser_used": parser_used,
        "transactions": transactions
    }