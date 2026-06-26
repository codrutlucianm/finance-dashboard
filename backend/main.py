import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io

# FastAPI app initialization
app = FastAPI(
    title="Fnance Dashboard API",
    description="Personal finance dashboard with AI tranzaction categorization",
    version="0.1.0"
)

# FE <-> BE communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint: checks if the API is running
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Finance Dashboard API is running"}

# CSV upload endpoint: receives a CSV file and returns parsed transactions
@app.post("/upload")
async def upload_csv(file: UploadFile =File(...)):
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