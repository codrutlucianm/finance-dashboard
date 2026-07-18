import pytest
from pdf_parser import detect_bank, parse_csv_transactions, extract_text_from_pdf


class TestDetectBank:
    def test_detect_bt(self):
        text = "BANCA TRANSILVANIA extras de cont"
        assert detect_bank(text) == "BT"

    def test_detect_bt_lowercase(self):
        text = "banca transilvania"
        assert detect_bank(text) == "BT"

    def test_detect_ing(self):
        text = "ING Bank Romania"
        assert detect_bank(text) == "ING"

    def test_detect_revolut(self):
        text = "Revolut Ltd statement"
        assert detect_bank(text) == "Revolut"

    def test_detect_bcr(self):
        text = "BCR extras de cont"
        assert detect_bank(text) == "BCR"

    def test_detect_brd(self):
        text = "BRD Group Societe Generale"
        assert detect_bank(text) == "BRD"

    def test_detect_raiffeisen(self):
        text = "Raiffeisen Bank Romania"
        assert detect_bank(text) == "Raiffeisen"

    def test_detect_unknown(self):
        text = "Some random text without bank name"
        assert detect_bank(text) == "Unknown"
        
class TestParseCsvTransactions:
    def test_parse_valid_csv(self):
        csv_content = b"date,description,amount,currency\n2026-05-01,Kaufland,-150.00,RON\n2026-05-02,Salary,5000.00,RON\n"
        result = parse_csv_transactions(csv_content)
        assert len(result) == 2
        assert result[0]["description"] == "Kaufland"
        assert result[0]["amount"] == -150.00
        assert result[1]["description"] == "Salary"

    def test_parse_csv_single_row(self):
        csv_content = b"date,description,amount,currency\n2026-05-01,Netflix,-37.00,RON\n"
        result = parse_csv_transactions(csv_content)
        assert len(result) == 1
        assert result[0]["currency"] == "RON"

    def test_parse_csv_empty(self):
        csv_content = b"date,description,amount,currency\n"
        result = parse_csv_transactions(csv_content)
        assert len(result) == 0

    def test_parse_csv_preserves_columns(self):
        csv_content = b"date,description,amount,currency\n2026-05-01,OMV,-300.00,RON\n"
        result = parse_csv_transactions(csv_content)
        assert "date" in result[0]
        assert "description" in result[0]
        assert "amount" in result[0]
        assert "currency" in result[0]