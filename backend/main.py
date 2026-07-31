import json
import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pdf_parser import parse_csv_transactions, parse_transactions_from_pdf

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize the FastAPI app
app = FastAPI(
    title="Finance Dashboard API",
    description="Personal finance dashboard with AI transaction categorization",
    version="0.1.0"
)

# CORS middleware: allows the frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint: used to verify the API is running
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}
    
# Categorization endpoint: uses Claude to categorize a list of transactions
@app.post("/categorize")
async def categorize_transactions(transactions: list[dict]):
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")

    # Format transactions as a readable list for Claude
    transactions_text = "\n".join(
        [f"- {t.get('date', 'N/A')} | {t.get('description', 'N/A')} | {t.get('amount', 'N/A')} {t.get('currency', '')}"
         for t in transactions]
    )

    # Ask Claude to categorize each transaction
    message = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""Categorize each of the following bank transactions into one of these categories:
                            Food & Groceries, Transport, Entertainment, Utilities, Healthcare, Shopping, Income, Savings, Mortgage, Other.
                            Transactions:
                            {transactions_text}

                            Respond ONLY with a JSON array, no explanation, no markdown. Example format:
                            [{{"description": "Kaufland", "category": "Food & Groceries"}}]"""
            }
        ]
    )

    # Parse Claude's response
    try:
        categories = json.loads(message.content[0].text)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not parse Claude's response")

    # Merge categories back into original transactions
    for i, transaction in enumerate(transactions):
        if i < len(categories):
            transaction["category"] = categories[i].get("category", "Other")

    return {"categorized_transactions": transactions}

# Smart upload endpoint: auto-detects CSV or PDF, parses and categorizes transactions
@app.post("/upload")
async def smart_upload(file: UploadFile = File(...)):
    filename = file.filename.lower()

    # Validate file type
    if not filename.endswith(".csv") and not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only CSV or PDF files are accepted")

    contents = await file.read()

    # 1) Parse based on file type
    if filename.endswith(".csv"):
        try:
            transactions = parse_csv_transactions(contents)
            bank = "N/A"
            parser_used = "pandas"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e!s}")
    else:
        try:
            result = parse_transactions_from_pdf(contents, claude)
            transactions = result["transactions"]
            bank = result["bank"]
            parser_used = result["parser_used"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not parse PDF: {e!s}")

    if not transactions:
        return {
            "filename": file.filename,
            "bank": bank,
            "parser_used": parser_used,
            "rows": 0,
            "transactions": []
        }

    # 2) Auto-categorize transactions
    categorized = await categorize_transactions(transactions)

    return {
        "filename": file.filename,
        "bank": bank,
        "parser_used": parser_used,
        "rows": len(categorized["categorized_transactions"]),
        "transactions": categorized["categorized_transactions"]
    }