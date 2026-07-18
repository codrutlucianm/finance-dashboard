import io
import os

import anthropic
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI(
    title="Finance Dashboard API",
    description="Personal finance dashboard with AI transaction categorization",
    version="0.1.0"
)

# CORS middleware: frontend <-> API communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}

# CSV upload endpoint: receives a CSV file and returns parsed transactions
@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    # Validate that the uploaded file is a CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    # Read the file content
    contents = await file.read()

    # Parse CSV into a pandas DataFrame
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {str(e)}")

    # Return basic info about the uploaded file
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }
    
# Categorization endpoint: use Claude to categorize list of transactions
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
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Categorize each of the following bank transactions into one of these categories:
                            Food & Groceries, Transport, Entertainment, Utilities, Healthcare, Shopping, Income, Savings, Other.

                            Transactions:
                            {transactions_text}

                            Respond ONLY with a JSON array, no explanation, no markdown. Example format:
                            [{{"description": "Kaufland", "category": "Food & Groceries"}}]"""
            }
        ]
    )
    
    # Parse Claude's response
    import json
    try:
        categories = json.loads(message.content[0].text)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not parse Claude's response")
    
    # Merge categories back into original transactions
    for i, transaction in enumerate(transactions):
        if i < len(categories):
            transaction["category"] = categories[i].get("category", "Other")
            
    return {"categorized_transactions": transactions}
